# HACK Compiler & Debugger v2.0

>*注意* 本项目为AI生成，未经过严格的理论论证和人工检查，不能保证完全正确，我只能说大多数情况下它正常运行

一个功能完整、结构清晰的HACK汇编器和交互式调试器，支持Excel动态可视化和JSON配置管理。

## 项目结构

```
HACKCompiler/
├── src/                      # 核心源代码模块
│   ├── __init__.py          # 包初始化，导出公共API
│   ├── assembler.py         # HACK汇编器
│   ├── cpu.py               # HACK CPU模拟器
│   ├── debugger.py          # 交互式调试器
│   ├── excel_view.py        # Excel动态视图
│   └── config.py            # 配置管理模块
├── tests/                    # 测试框架
│   ├── __init__.py          # 测试包初始化
│   ├── test_suite.py        # 综合测试套件
│   ├── test_utils.py        # 测试工具函数
│   └── test_programs/       # 测试程序目录
│       ├── add.asm          # 加法测试程序
│       ├── counter.asm      # 计数器测试程序
│       └── register.asm     # 寄存器测试程序
├── output/                   # 默认输出目录（自动创建）
├── config.json              # 配置文件（可编辑）
├── main_new.py              # 主程序入口
└── README.md                # 本文档
```

## 新特性

### 🎯 模块化架构
- 清晰的目录结构，核心代码和测试分离
- 高代码复用率，模块间依赖清晰
- 支持作为Python包导入使用

### ⚙️ JSON配置系统
- 通过`config.json`自定义所有默认设置
- 支持运行时重载配置
- 独立的配置模块，类型安全

### 🧪 完整测试框架
- 独立的`tests/`目录存放测试代码
- `test_programs/`子目录管理测试程序
- 测试工具模块提供可复用的测试函数

### 📊 增强的Excel视图
- 可配置的颜色方案
- 自动保存选项
- 更好的错误处理

## 配置文件说明

编辑`config.json`自定义默认行为：

```json
{
  "assembler": {
    "default_output_dir": "output",    // 默认输出目录
    "create_hack_file": true,          // 是否默认生成.hack文件
    "create_excel_view": false         // 是否默认生成Excel视图
  },
  "debugger": {
    "default_excel_file": "HACKCompiler.xlsx",  // 默认Excel文件名
    "ram_view_size": 64,                        // 默认RAM显示大小
    "max_steps": 100000,                        // 运行时最大步数
    "auto_save_excel": true                     // 单步执行时自动保存Excel
  },
  "excel": {
    "color_current_instruction": "FFFF00",  // 当前指令颜色（黄色）
    "color_breakpoint": "FF6B6B",           // 断点颜色（红色）
    "color_modified_value": "90EE90"        // 修改值颜色（绿色）
  },
  "paths": {
    "test_programs": "tests/test_programs",  // 测试程序路径
    "output": "output"                       // 输出目录
  }
}
```

## 安装依赖

```bash
pip install openpyxl
```

## 使用方法

### 1. 汇编模式

```bash
python main_new.py asm <source.asm> [选项]

选项:
  -o, --output <file>       指定输出.hack文件
  --output-dir <dir>        指定输出目录（覆盖config.json）
  --excel <file>            生成Excel视图文件
  --ram-view <n>            Excel中显示的RAM行数（默认64）
  --no-hack                 不生成.hack文件
```

示例：
```bash
# 基本汇编（使用config.json中的默认设置）
python main_new.py asm tests/test_programs/add.asm

# 汇编并生成Excel视图到指定目录
python main_new.py asm tests/test_programs/counter.asm --output-dir results --excel results/counter.xlsx

# 只生成Excel，不生成hack文件
python main_new.py asm tests/test_programs/add.asm --excel view.xlsx --no-hack
```

### 2. 调试模式

```bash
python main_new.py debug <source.asm> [选项]

选项:
  --output-dir <dir>        输出目录（默认使用config.json）
  --excel <file>            Excel视图文件
  --ram-view <n>            Excel中显示的RAM行数
```

示例：
```bash
# 启动调试器
python main_new.py debug tests/test_programs/counter.asm

# 使用自定义输出目录
python main_new.py debug tests/test_programs/add.asm --output-dir debug_output
```

### 3. 配置管理

```bash
# 查看当前配置
python main_new.py config

# 重新加载配置文件
python main_new.py config --reload
```

## 调试器命令

| 命令 | 说明 |
|------|------|
| `s`, `step` | 单步执行一条指令 |
| `r`, `run` | 运行直到断点或程序结束 |
| `b <地址>` | 在指定ROM地址设置断点 |
| `d <地址>` | 删除指定地址的断点 |
| `bc` | 清除所有断点 |
| `bl` | 列出所有断点 |
| `reg` | 查看所有寄存器值 |
| `m <地址> [数量]` | 查看内存（默认1个单元） |
| `set <地址> <值>` | 设置内存值 |
| `reset` | 重置CPU到初始状态 |
| `config` | 显示当前配置 |
| `h`, `help`, `?` | 显示帮助 |
| `q`, `quit`, `exit` | 退出调试器 |

## 运行测试

```bash
# 运行完整测试套件
python tests/test_suite.py
```

测试覆盖：
- ✅ 汇编器基本功能
- ✅ CPU指令执行（加法、计数等）
- ✅ 调试器功能（断点、单步等）
- ✅ Excel视图生成
- ✅ 寄存器修改跟踪
- ✅ 配置加载

## 作为Python包使用

```python
from src import assemble_file, HackCPU, Debugger, ExcelView, get_config

# 汇编程序
machine_code, source = assemble_file("program.asm")

# 创建CPU并运行
cpu = HackCPU(machine_code)
cpu.set_ram(0, 10)
for _ in range(100):
    if not cpu.step():
        break

# 使用调试器
debugger = Debugger(cpu, source)
debugger.add_breakpoint(5)
reason, state = debugger.run_until_breakpoint()

# 访问配置
config = get_config()
print(f"RAM视图大小: {config.debugger.ram_view_size}")
```

## Excel视图说明

| 列 | 说明 |
|-------|------|
| ROM_ADDR | ROM地址（指令地址） |
| ASM | 汇编源代码 |
| A, D, PC | 寄存器值（仅当前PC行显示） |
| RAM_ADDR | RAM地址 |
| VALUE | RAM值 |

**颜色编码**（可在config.json中自定义）：
- **黄色** (#FFFF00): 当前正在执行的指令
- **红色** (#FF6B6B): 设置了断点的指令
- **绿色** (#90EE90): 刚被修改的寄存器或内存单元

## 开发指南

### 添加新测试

1. 在`tests/test_programs/`中创建.asm文件
2. 在`tests/test_suite.py`中添加测试方法
3. 使用`test_utils.py`中的辅助函数

```python
def test_my_program(self):
    """测试我的程序"""
    cpu, source = create_test_cpu("my_program")
    # 执行测试...
```

### 修改配置

直接编辑`config.json`，或通过代码：

```python
from src import get_config

config = get_config()
config.debugger.ram_view_size = 128
config.save()  # 保存到config.json
```

### 扩展功能

核心模块位于`src/`目录：
- `assembler.py` - 添加新的汇编指令支持
- `cpu.py` - 修改CPU行为
- `debugger.py` - 添加新的调试命令
- `excel_view.py` - 自定义Excel输出格式
- `config.py` - 添加新的配置选项

## 与旧版本的区别

| 特性 | v1.0 | v2.0（重构版） |
|------|------|----------------|
| 项目结构 | 单目录 | src/, tests/分离 |
| 配置方式 | 硬编码 | config.json |
| 测试 | 单文件 | 完整测试框架 |
| 模块化 | 低 | 高（包结构） |
| 可复用性 | 中 | 高（可作为包导入） |
| 文档 | 基础 | 完整 |

## 迁移指南

从旧版本迁移：
1. 使用`main_new.py`替代`main.py`
2. 测试程序移到`tests/test_programs/`
3. 通过`config.json`设置默认行为
4. 运行`python tests/test_suite.py`确认

## 许可证

本项目仅供学习和教育目的使用。

## 版本历史

- **v2.0** (2025-12-19): 
  - 完全重构项目结构
  - 添加JSON配置系统
  - 建立完整测试框架
  - 提高代码复用率
  - 模块化架构
  
- **v1.0**: 初始版本（基础汇编器和调试器）

## 贡献

欢迎提交Issue和Pull Request！

## 作者

Claude Sonnet 4.5
