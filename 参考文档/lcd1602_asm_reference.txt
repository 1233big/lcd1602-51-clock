; ============================================================
; LCD1602 显示 "Claude"   (STC89C52 / 8051, 11.0592MHz 或 12MHz)
;
; 接线:
;   LCD D0~D7 -> P0.0~P0.7
;   RS        -> P2.6
;   RW        -> P2.5
;   E         -> P2.7
;   V0(对比度)-> 电位器中间脚
; 注意: P2.5~P2.7 同时接着 LED6~LED8, 写屏时这三颗灯会闪, 正常现象
;
; 本文件用于阅读/用 Keil 重编;
; lcd1602.hex 由 build_lcd.py 按同一逻辑汇编生成。
; ============================================================

RS      BIT     P2.6
RW      BIT     P2.5
E       BIT     P2.7

        ORG     0000H
        LJMP    MAIN

        ORG     0030H
MAIN:   MOV     SP,#30H
        LCALL   LCD_INIT
        MOV     A,#80H              ; 第 1 行第 1 列
        LCALL   LCD_CMD
        MOV     DPTR,#MSG
        LCALL   LCD_PUTS
        MOV     A,#0C0H             ; 第 2 行第 1 列
        LCALL   LCD_CMD
        MOV     DPTR,#MSG2
        LCALL   LCD_PUTS
HERE:   SJMP    HERE

; ---------------- 初始化 ----------------
LCD_INIT:
        MOV     P0,#0FFH
        CLR     E                   ; 先拉低 E(RW 仍为 1, 不会误写)
        CLR     RS
        CLR     RW
        LCALL   DLY20
        LCALL   DLY20               ; 上电后共约 40ms 再发指令
        MOV     A,#38H              ; 8 位, 两行, 5x8
        LCALL   LCD_CMD
        LCALL   DLY2
        MOV     A,#38H
        LCALL   LCD_CMD
        LCALL   DLY2
        MOV     A,#0CH              ; 开显示, 无光标
        LCALL   LCD_CMD
        LCALL   DLY2
        MOV     A,#01H              ; 清屏
        LCALL   LCD_CMD
        LCALL   DLY2
        MOV     A,#06H              ; 光标右移
        LCALL   LCD_CMD
        LCALL   DLY2
        RET

; ---------------- 写命令 ----------------
LCD_CMD:
        CLR     RS
        SJMP    LCD_WR

; ---------------- 写数据 ----------------
LCD_DAT:
        SETB    RS

LCD_WR: CLR     RW
        MOV     P0,A
        SETB    E
        NOP
        NOP
        NOP
        CLR     E                   ; E 下降沿锁存
        LCALL   DLY
        RET

; ---------------- 写字符串(遇 00H 结束) ----------------
LCD_PUTS:
        CLR     A
        MOVC    A,@A+DPTR
        JZ      PUTS_END
        LCALL   LCD_DAT
        INC     DPTR
        SJMP    LCD_PUTS
PUTS_END:
        RET

; ---------------- 延时 ----------------
DLY:    MOV     R6,#18              ; ~40us
DLY_L:  DJNZ    R6,DLY_L
        RET

DLY2:   MOV     R7,#10              ; ~2ms
D2A:    MOV     R6,#100
D2B:    DJNZ    R6,D2B
        DJNZ    R7,D2A
        RET

DLY20:  MOV     R7,#200             ; ~22ms @11.0592MHz
D20A:   MOV     R6,#100
D20B:   DJNZ    R6,D20B
        DJNZ    R7,D20A
        RET

        ORG     0200H
MSG:    DB      'C','l','a','u','d','e',0

        ORG     0210H
MSG2:   DB      'L','C','D','1','6','0','2',' ','O','K',0

        END
