/* ============================================================
 * lcd1602.c  --  LCD1602 驱动实现 (STC89C52 / 8051, Keil C51)
 *
 * 接线: D0~D7 = P0.0~P0.7   RS = P2.6   RW = P2.5   E = P2.7
 * 顺序: 上电先调 LCD_Init(), 之后可自由使用下面各个显示函数
 * ============================================================ */

#include <reg52.h>
#include "lcd1602.h"

sbit LCD_RS = P2 ^ 6;       /* 1 = 写数据, 0 = 写命令 */
sbit LCD_RW = P2 ^ 5;       /* 1 = 读, 0 = 写 */
sbit LCD_E = P2 ^ 7;        /* 使能脚: 拉高准备, 下降沿把数据锁进 LCD */

#define LCD_DATA P0         /* 8 位数据总线, P0 是开漏, 板上需有上拉电阻 */

/* 内部使用: E 拉高后的保持时间, 约 5us (LCD 要求 >450ns) */
static void LCD_Delay5us(void)
{
    volatile unsigned char i = 2;
    while (i--)
        ;
}

/* 内部使用: 每条命令/数据写完后的等待, 约 40us (LCD 要求 37us) */
static void LCD_Delay40us(void)
{
    volatile unsigned char i = 18;
    while (i--)
        ;
}

/*
 * 函数: DelayMs
 * 作用: 毫秒级软件延时, 用于上电等待和普通节奏控制
 * 参数: ms - 延时长度, 单位 ms, 12MHz 下约 1ms/单位
 * 用法: DelayMs(40);   // 等 40ms
 */
void DelayMs(unsigned int ms)
{
    unsigned int i, j;
    for (i = ms; i > 0; i--)
        for (j = 110; j > 0; j--)
            ;
}

/*
 * 函数: LCD_WriteCmd
 * 作用: 向 LCD 写一条指令(RS=0), 如清屏、光标定位、开关显示
 * 参数: cmd - 指令字节, 常用 0x01 清屏 / 0x0C 开显示 / 0x80|地址 定位
 * 用法: LCD_WriteCmd(0x01);
 * 说明: 显示字符请用 LCD_WriteData, 不要用这个
 */
void LCD_WriteCmd(unsigned char cmd)
{
    LCD_RS = 0;
    LCD_RW = 0;
    LCD_DATA = cmd;
    LCD_E = 1;
    LCD_Delay5us();
    LCD_E = 0;
    LCD_Delay40us();
}

/*
 * 函数: LCD_WriteData
 * 作用: 向 LCD 写一个字节数据(RS=1), 显示在当前光标处, 光标自动右移一位
 * 参数: dat - 字符编码, ASCII 字符(如 'A' 的 0x41)或 CGRAM 自定义字符编号 0~7
 * 用法: LCD_WriteData('A');
 */
void LCD_WriteData(unsigned char dat)
{
    LCD_RS = 1;
    LCD_RW = 0;
    LCD_DATA = dat;
    LCD_E = 1;
    LCD_Delay5us();
    LCD_E = 0;
    LCD_Delay40us();
}

/*
 * 函数: LCD_Init
 * 作用: 上电初始化: 等 40ms -> 8位两行 -> 开显示关光标 -> 清屏 -> 光标右移
 * 参数: 无
 * 用法: 程序开头调用一次, 必须在任何显示操作之前
 */
void LCD_Init(void)
{
    LCD_E = 0;
    LCD_RS = 0;
    LCD_RW = 0;
    LCD_DATA = 0xFF;
    DelayMs(40);

    LCD_WriteCmd(0x38);
    DelayMs(2);
    LCD_WriteCmd(0x38);
    DelayMs(2);
    LCD_WriteCmd(0x0C);
    DelayMs(2);
    LCD_WriteCmd(0x01);
    DelayMs(2);
    LCD_WriteCmd(0x06);
    DelayMs(2);
}

/*
 * 函数: LCD_Clear
 * 作用: 清屏, 并把光标移回左上角(第 1 行第 1 列)
 * 参数: 无
 * 用法: LCD_Clear();
 * 说明: 清屏是慢指令, 内部已等 2ms
 */
void LCD_Clear(void)
{
    LCD_WriteCmd(0x01);
    DelayMs(2);
}

/*
 * 函数: LCD_SetCursor
 * 作用: 把光标移到指定行列, 之后写入的字符从这个位置开始
 * 参数: row - 行号, 0 = 第一行, 1 = 第二行
 *       col - 列号, 0~15 (0 = 最左边)
 * 用法: LCD_SetCursor(1, 5);   // 第二行第 6 个字符位置
 */
void LCD_SetCursor(unsigned char row, unsigned char col)
{
    unsigned char addr;

    addr = (row == 0) ? col : (0x40 + col);
    LCD_WriteCmd(0x80 | addr);
}

/*
 * 函数: LCD_WriteChar
 * 作用: 在当前光标处显示一个字符, 光标后移一位
 * 参数: c - ASCII 字符, 如 'A'、'7'、' '
 * 用法: LCD_WriteChar('A');
 * 说明: 和 LCD_WriteData 等价, 只是参数写成字符形式更直观
 */
void LCD_WriteChar(char c)
{
    LCD_WriteData((unsigned char)c);
}

/*
 * 函数: LCD_WriteString
 * 作用: 从当前光标开始连续显示一个字符串
 * 参数: str - 以 '\0' 结尾的字符串指针, 如 "Claude"
 * 用法: LCD_SetCursor(0, 0); LCD_WriteString("Claude");
 */
void LCD_WriteString(const char *str)
{
    while (*str)
    {
        LCD_WriteData((unsigned char)(*str++));
    }
}

/*
 * 函数: LCD_WriteStringAt
 * 作用: 先定位到指定行列, 再显示一个字符串(最常用)
 * 参数: row - 行号, 0 = 第一行, 1 = 第二行
 *       col - 列号, 0~15
 *       str - 要显示的字符串, 如 "LCD1602 OK"
 * 用法: LCD_WriteStringAt(1, 0, "LCD1602 OK");
 */
void LCD_WriteStringAt(unsigned char row, unsigned char col, const char *str)
{
    LCD_SetCursor(row, col);
    LCD_WriteString(str);
}

/*
 * 函数: LCD_WriteNum
 * 作用: 在当前光标处显示一个无符号整数的十进制形式
 * 参数: num - 要显示的数, 范围 0~65535
 * 用法: LCD_WriteNum(1234);   // 显示 "1234"
 * 说明: 不补零也不补空格; 数字位数变少时旧字符不会被擦掉,
 *       刷新计数一类场景请先用空格覆盖或整行重写
 */
void LCD_WriteNum(unsigned int num)
{
    unsigned char buf[5];
    unsigned char i = 0;

    if (num == 0)
    {
        LCD_WriteData('0');
        return;
    }

    while (num > 0)
    {
        buf[i++] = (unsigned char)('0' + num % 10);
        num /= 10;
    }
    while (i > 0)
    {
        LCD_WriteData(buf[--i]);
    }
}

/*
 * 函数: LCD_WriteNumAt
 * 作用: 定位到指定行列, 按固定位数显示无符号数, 位数不足左边自动补 0
 * 参数: row   - 行号, 0 = 第一行, 1 = 第二行
 *       col   - 起始列, 0~15
 *       num   - 要显示的数, 0~65535
 *       width - 显示位数, 1~5 (给 0 按 1 处理, 超过 5 按 5 处理)
 * 用法: LCD_WriteNumAt(1, 6, 7, 2);       // 第二行第 7 列显示 "07"
 *       LCD_WriteNumAt(0, 0, 65535, 5);   // 显示 "65535"
 * 说明: 数值位数比 width 多时只显示低 width 位(高位截掉),
 *       做时间显示时 width 给 2, 请保证传进来的数在 0~99
 */
void LCD_WriteNumAt(unsigned char row, unsigned char col, unsigned int num, unsigned char width)
{
    unsigned char i;
    unsigned int div = 1;

    if (width == 0)
        width = 1;
    if (width > 5)
        width = 5;

    LCD_SetCursor(row, col);

    for (i = 1; i < width; i++)
    {
        div *= 10;
    }

    for (i = 0; i < width; i++)
    {
        LCD_WriteChar((char)('0' + (num / div) % 10));
        div /= 10;
    }
}
