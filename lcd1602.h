#ifndef LCD1602_H
#define LCD1602_H

/* ------------------------------------------------------------
 * LCD1602 driver for STC89C52 / 8051 (Keil C51)
 *
 * Wiring: D0-D7 = P0.0-P0.7, RS = P2.6, RW = P2.5, E = P2.7
 *         V0 = pot wiper (contrast)
 *         P2.5-P2.7 are shared with on-board LED6-LED8
 * Coordinates: row = 0/1 (first/second line), col = 0-15
 *
 * Call LCD_Init() once before any other function.
 * ------------------------------------------------------------ */

void LCD_Init(void);
void LCD_Clear(void);
void LCD_SetCursor(unsigned char row, unsigned char col);
void LCD_WriteCmd(unsigned char cmd);
void LCD_WriteData(unsigned char dat);
void LCD_WriteChar(char c);
void LCD_WriteString(const char *str);
void LCD_WriteStringAt(unsigned char row, unsigned char col, const char *str);
void LCD_WriteNum(unsigned int num);
void LCD_WriteNumAt(unsigned char row, unsigned char col, unsigned int num, unsigned char width);
void DelayMs(unsigned int ms);

#endif
