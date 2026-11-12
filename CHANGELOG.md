# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [1.2.0] - 2026-11-12

### 变更

- 源码移入 `src/`、自检脚本移入 `tools/`、`参考文档/` 改名 `docs/`，根目录只保留 Keil 工程与文档
- `LCD1602.uvproj` 中的文件路径同步改为 `.\src\`，Keil 打开后可直接编译
- CI 工作流与 README 中的路径同步更新

## [1.1.0] - 2026-11-12

### 新增

- `LICENSE`：MIT 许可证，项目转为公开仓库
- `SECURITY.md`：漏洞私密报告渠道与响应时限
- `参考文档/lcd1602_reference.md`：E 脚时序、指令集、C 与汇编逐段对照、延时标定与定时器初值推导
- `.github/workflows/selftest.yml`：push / PR 时自动运行 `build_lcd.py` 自检

### 变更

- `参考文档/lcd1602_asm_reference.txt` 改名为 `参考文档/lcd1602_demo.asm`，文件名标明它是可编译的汇编源码
- `.gitignore` 增加 `.workbuddy/`
- `README` 补充自检脚本输出 `lcd1602.hex` 的说明，更新目录结构与许可证

## [1.0.0] - 2026-11-12

### 新增

- LCD1602 并行驱动：初始化、清屏、光标定位、写字符 / 字符串、定宽补零显示数字
- 基于定时器 0 的电子时钟示例，初值 23:59:55，支持时 / 分 / 秒进位
- `参考文档/lcd1602_asm_reference.txt`：与驱动等价逻辑的汇编对照版
- `build_lcd.py`：8051 编码器 + LCD 总线模拟器，可在无硬件的情况下校验指令序列
