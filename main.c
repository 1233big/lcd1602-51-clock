#include <regx51.h>
#include "lcd1602.h"
unsigned char hour = 23, min = 59, sec = 55, last_sec=0xFF;
unsigned int flag=0;
void Timer0Init(void)		//1毫秒@12.000MHz
{
	TMOD &= 0xF0;              /* 先清定时器0 的模式位 */
  TMOD |= 0x01;
	TL0 = 0x18;		//设置定时初值
	TH0 = 0xFC;		//设置定时初值
	TF0 = 0;		//清除TF0标志
	TR0 = 1;		//定时器0开始计时
	ET0 = 1; 
	EA = 1;
}

void main(void)
{
   /* 初始时间 23:59:55, 方便很快看到进位 */
		Timer0Init();
    LCD_Init();                                    /* 初始化屏幕, 必须最先调用 */
    LCD_WriteStringAt(0, 0, "Clock");              /* 第一行显示标题 */
		
    while (1)
    {
				if(sec!=last_sec){
				last_sec = sec;
				LCD_WriteNumAt(1, 0, hour, 2); LCD_WriteChar(':');   /* 每秒重写整行时间 */
        LCD_WriteNumAt(1, 3, min,  2); LCD_WriteChar(':');
        LCD_WriteNumAt(1, 6, sec,  2);
				}
        
    }
}

void Init0() interrupt 1
{
	
		TL0 = 0x18;		
		TH0 = 0xFC;
		if(flag>=1000)
		{	
        sec++;
				flag=0;
				if (sec >= 60) min++, sec = 0;             /* 满 60 秒 -> 分 +1 */
        if (min >= 60) hour++, min = 0;            /* 满 60 分 -> 时 +1 */
        if (hour >= 24) hour = 0;                  /* 满 24 时 -> 回到 0 点 */
        
		}
		flag++;




}
