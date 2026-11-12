# -*- coding: utf-8 -*-
"""Minimal 8051 encoder + LCD bus simulator for lcd1602.asm.

The simulator models only the instructions this program uses, and latches
P0 on every E falling edge, so the printed log is exactly what the LCD
would receive (RS=0 command / RS=1 data).

Usage:  python -I build_lcd.py
"""
import os

P0 = 0x80
P2 = 0xA0
SP = 0x81
RS_BIT = 0xA6
RW_BIT = 0xA5
E_BIT = 0xA7
BITS = {"RS": RS_BIT, "RW": RW_BIT, "E": E_BIT}

MSG = "Claude"
MSG2 = "LCD1602 OK"
MSG_ADDR = 0x0200
MSG2_ADDR = 0x0210

prog = [
    ("ORG", 0x0000),
    ("LJMP", "MAIN"),
    ("ORG", 0x0030),
    ("LBL", "MAIN"),
    ("MOV_DIR_IMM", SP, 0x30),
    ("LCALL", "LCD_INIT"),
    ("MOV_A_IMM", 0x80),
    ("LCALL", "LCD_CMD"),
    ("MOV_DPTR_IMM", "MSG"),
    ("LCALL", "LCD_PUTS"),
    ("MOV_A_IMM", 0xC0),          # 第 2 行第 1 列
    ("LCALL", "LCD_CMD"),
    ("MOV_DPTR_IMM", "MSG2"),
    ("LCALL", "LCD_PUTS"),
    ("LBL", "HERE"),
    ("SJMP", "HERE"),

    ("LBL", "LCD_INIT"),
    ("MOV_DIR_IMM", P0, 0xFF),
    ("CLR_BIT", "E"),
    ("CLR_BIT", "RS"),
    ("CLR_BIT", "RW"),
    ("LCALL", "DLY20"),
    ("LCALL", "DLY20"),
    ("MOV_A_IMM", 0x38),
    ("LCALL", "LCD_CMD"),
    ("LCALL", "DLY2"),
    ("MOV_A_IMM", 0x38),
    ("LCALL", "LCD_CMD"),
    ("LCALL", "DLY2"),
    ("MOV_A_IMM", 0x0C),
    ("LCALL", "LCD_CMD"),
    ("LCALL", "DLY2"),
    ("MOV_A_IMM", 0x01),
    ("LCALL", "LCD_CMD"),
    ("LCALL", "DLY2"),
    ("MOV_A_IMM", 0x06),
    ("LCALL", "LCD_CMD"),
    ("LCALL", "DLY2"),
    ("RET",),

    ("LBL", "LCD_CMD"),
    ("CLR_BIT", "RS"),
    ("SJMP", "LCD_WR"),

    ("LBL", "LCD_DAT"),
    ("SETB_BIT", "RS"),

    ("LBL", "LCD_WR"),
    ("CLR_BIT", "RW"),
    ("MOV_DIR_A", P0),
    ("SETB_BIT", "E"),
    ("NOP",),
    ("NOP",),
    ("NOP",),
    ("CLR_BIT", "E"),
    ("LCALL", "DLY"),
    ("RET",),

    ("LBL", "LCD_PUTS"),
    ("CLR_A",),
    ("MOVC_A_DPTR",),
    ("JZ", "PUTS_END"),
    ("LCALL", "LCD_DAT"),
    ("INC_DPTR",),
    ("SJMP", "LCD_PUTS"),
    ("LBL", "PUTS_END"),
    ("RET",),

    ("LBL", "DLY"),
    ("MOV_RN_IMM", 6, 18),
    ("LBL", "DLY_L"),
    ("DJNZ", 6, "DLY_L"),
    ("RET",),

    ("LBL", "DLY2"),
    ("MOV_RN_IMM", 7, 10),
    ("LBL", "D2A"),
    ("MOV_RN_IMM", 6, 100),
    ("LBL", "D2B"),
    ("DJNZ", 6, "D2B"),
    ("DJNZ", 7, "D2A"),
    ("RET",),

    ("LBL", "DLY20"),
    ("MOV_RN_IMM", 7, 200),
    ("LBL", "D20A"),
    ("MOV_RN_IMM", 6, 100),
    ("LBL", "D20B"),
    ("DJNZ", 6, "D20B"),
    ("DJNZ", 7, "D20A"),
    ("RET",),

    ("ORG", MSG_ADDR),
    ("LBL", "MSG"),
    ("DB", [ord(c) for c in MSG] + [0]),
    ("ORG", MSG2_ADDR),
    ("LBL", "MSG2"),
    ("DB", [ord(c) for c in MSG2] + [0]),
]

SIZE = {
    "ORG": 0, "LBL": 0,
    "LJMP": 3, "LCALL": 3, "SJMP": 2, "JZ": 2,
    "MOV_DIR_IMM": 3, "MOV_A_IMM": 2, "MOV_RN_IMM": 2, "MOV_DIR_A": 2,
    "MOV_DPTR_IMM": 3, "MOVC_A_DPTR": 1, "CLR_A": 1, "INC_DPTR": 1,
    "SETB_BIT": 2, "CLR_BIT": 2, "NOP": 1, "RET": 1, "DJNZ": 2,
}


def size_of(item):
    if item[0] == "DB":
        return len(item[1])
    return SIZE[item[0]]


def build():
    labels, pc = {}, 0
    for item in prog:
        op = item[0]
        if op == "ORG":
            pc = item[1]
        elif op == "LBL":
            labels[item[1]] = pc
        else:
            pc += size_of(item)

    mem, pc = {}, 0
    for item in prog:
        op = item[0]
        if op == "ORG":
            pc = item[1]
            continue
        if op == "LBL":
            continue
        if op == "DB":
            data = list(item[1])
        elif op == "LJMP":
            a = labels[item[1]]
            data = [0x02, a >> 8, a & 0xFF]
        elif op == "LCALL":
            a = labels[item[1]]
            data = [0x12, a >> 8, a & 0xFF]
        elif op == "SJMP":
            rel = labels[item[1]] - (pc + 2)
            assert -128 <= rel <= 127, "SJMP out of range"
            data = [0x80, rel & 0xFF]
        elif op == "JZ":
            rel = labels[item[1]] - (pc + 2)
            assert -128 <= rel <= 127, "JZ out of range"
            data = [0x60, rel & 0xFF]
        elif op == "MOV_DIR_IMM":
            data = [0x75, item[1], item[2] & 0xFF]
        elif op == "MOV_A_IMM":
            data = [0x74, item[1] & 0xFF]
        elif op == "MOV_RN_IMM":
            data = [0x78 + item[1], item[2] & 0xFF]
        elif op == "MOV_DIR_A":
            data = [0xF5, item[1]]
        elif op == "MOV_DPTR_IMM":
            a = labels[item[1]]
            data = [0x90, a >> 8, a & 0xFF]
        elif op == "MOVC_A_DPTR":
            data = [0x93]
        elif op == "CLR_A":
            data = [0xE4]
        elif op == "INC_DPTR":
            data = [0xA3]
        elif op == "SETB_BIT":
            data = [0xD2, BITS[item[1]]]
        elif op == "CLR_BIT":
            data = [0xC2, BITS[item[1]]]
        elif op == "NOP":
            data = [0x00]
        elif op == "RET":
            data = [0x22]
        elif op == "DJNZ":
            rel = labels[item[2]] - (pc + 2)
            assert -128 <= rel <= 127, "DJNZ out of range"
            data = [0xD8 + item[1], rel & 0xFF]
        else:
            raise SystemExit("unknown mnemonic " + op)
        assert len(data) == size_of(item), op
        for b in data:
            mem[pc] = b
            pc += 1
    return mem, labels


def to_hex(mem, path, width=16):
    addrs = sorted(mem)
    lines, i = [], 0
    while i < len(addrs):
        start = addrs[i]
        chunk, a = [], start
        while i < len(addrs) and addrs[i] == a and len(chunk) < width:
            chunk.append(mem[a])
            a += 1
            i += 1
        rec = [len(chunk), (start >> 8) & 0xFF, start & 0xFF, 0x00] + chunk
        lines.append(":" + "".join("%02X" % b for b in rec) + "%02X" % ((-sum(rec)) & 0xFF))
    lines.append(":00000001FF")
    with open(path, "w", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def simulate(mem, max_steps=2_000_000):
    a, p0, p2, dptr, pc = 0, 0xFF, 0xFF, 0, 0
    reg = [0] * 8
    stack = []
    log = []          # (rs, byte) latched on E falling edge
    steps = 0

    def write_bit(addr, value):
        nonlocal p2
        byte = addr & 0xF8
        bit = addr & 7
        if byte != P2:
            return
        before = (p2 >> bit) & 1
        if value:
            p2 |= (1 << bit)
        else:
            p2 &= ~(1 << bit) & 0xFF
        after = (p2 >> bit) & 1
        if bit == 7 and before == 1 and after == 0:      # E falling edge
            if ((p2 >> 5) & 1) == 0:                      # RW == 0
                log.append(((p2 >> 6) & 1, p0))

    while steps < max_steps:
        steps += 1
        op = mem.get(pc, 0xFF)
        if op == 0x02:
            pc = (mem[pc + 1] << 8) | mem[pc + 2]
        elif op == 0x12:
            stack.append(pc + 3)
            pc = (mem[pc + 1] << 8) | mem[pc + 2]
        elif op == 0x80:
            rel = mem[pc + 1]
            target = (pc + 2 + (rel - 256 if rel > 127 else rel)) & 0xFFFF
            if target == pc and rel == 0xFE:
                return log, steps, True               # SJMP $ -> halt
            pc = target
        elif op == 0x60:                              # JZ
            rel = mem[pc + 1]
            if a == 0:
                pc = (pc + 2 + (rel - 256 if rel > 127 else rel)) & 0xFFFF
            else:
                pc += 2
        elif op == 0x75:                              # MOV direct,#imm
            d = mem[pc + 1]
            if d == P0:
                p0 = mem[pc + 2]
            elif d == P2:
                p2 = mem[pc + 2]
            pc += 3
        elif op == 0x74:
            a = mem[pc + 1]
            pc += 2
        elif 0x78 <= op <= 0x7F:
            reg[op - 0x78] = mem[pc + 1]
            pc += 2
        elif op == 0xF5:
            if mem[pc + 1] == P0:
                p0 = a
            elif mem[pc + 1] == P2:
                p2 = a
            pc += 2
        elif op == 0x90:
            dptr = (mem[pc + 1] << 8) | mem[pc + 2]
            pc += 3
        elif op == 0x93:
            a = mem.get(dptr + a, 0)
            pc += 1
        elif op == 0xE4:
            a = 0
            pc += 1
        elif op == 0xA3:
            dptr = (dptr + 1) & 0xFFFF
            pc += 1
        elif op == 0xD2:
            write_bit(mem[pc + 1], 1)
            pc += 2
        elif op == 0xC2:
            write_bit(mem[pc + 1], 0)
            pc += 2
        elif op == 0x00:
            pc += 1
        elif 0xD8 <= op <= 0xDF:
            n = op - 0xD8
            reg[n] = (reg[n] - 1) & 0xFF
            if reg[n]:
                rel = mem[pc + 1]
                pc = (pc + 2 + (rel - 256 if rel > 127 else rel)) & 0xFFFF
            else:
                pc += 2
        elif op == 0x22:
            pc = stack.pop()
        else:
            raise SystemExit("unexpected opcode 0x%02X at 0x%04X" % (op, pc))
    return log, steps, False


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    mem, labels = build()
    out = os.path.join(here, "lcd1602.hex")
    to_hex(mem, out)

    print("labels:", {k: "0x%04X" % v for k, v in labels.items()})
    print("code bytes:", len(mem), "range 0x%04X-0x%04X" % (min(mem), max(mem)))

    log, steps, halted = simulate(mem)
    cmds = [b for rs, b in log if rs == 0]
    texts, cur = [], ""
    for rs, b in log:
        if rs == 0:
            if cur:
                texts.append(cur)
                cur = ""
        else:
            cur += chr(b)
    if cur:
        texts.append(cur)
    print("E pulses:", len(log), " halted:", halted, " steps:", steps)
    print("commands:", " ".join("%02X" % c for c in cmds))
    print("lines on LCD:", texts)
    print("hex written:", out)

    assert cmds == [0x38, 0x38, 0x0C, 0x01, 0x06, 0x80, 0xC0], cmds
    assert texts == [MSG, MSG2], texts
    print("checks OK")


if __name__ == "__main__":
    main()
