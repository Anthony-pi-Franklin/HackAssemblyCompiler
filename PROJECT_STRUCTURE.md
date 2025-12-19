# HACK Compiler 项目结构说明

## 目录树

```
HACKCompiler/
│
├── src/                          # 核心源代码包
│   ├── __init__.py              # 包初始化，导出公共API
│   ├── assembler.py             # 汇编器模块（194行）
│   ├── cpu.py                   # CPU模拟器模块（200行）
│   ├── debugger.py              # 调试器模块（125行）
│   ├── excel_view.py            # Excel视图模块（180行）
│   └── config.py                # 配置管理模块（130行）
│
├── tests/                        # 测试框架
│   ├── __init__.py              # 测试包初始化
│   ├── test_suite.py            # 综合测试套件（270行）
│   ├── test_utils.py            # 测试工具函数（70行）
│   └── test_programs/           # 测试程序目录
│       ├── add.asm              # 加法测试（11行）
│       ├── counter.asm          # 计数器测试（17行）
│       └── register.asm         # 寄存器测试（19行）
│
├── output/                       # 输出目录（自动创建）
│   ├── *.hack                   # 编译生成的机器码
│   └── *.xlsx                   # Excel视图文件
│
├── config.json                   # 应用配置文件（可编辑）
├── main_new.py                   # 主程序入口（350行）
├── README_v2.md                  # 详细文档
└── PROJECT_STRUCTURE.md          # 本文件
```

## 模块说明

### 核心模块 (src/)

#### 1. assembler.py
**职责**: HACK汇编器
- 两遍扫描汇编
- 符号表管理
- 指令翻译

**主要函数**:
- `assemble_file(source)` - 汇编文件，返回机器码和源码
- `save_hack_file(code, dest)` - 保存机器码到.hack文件
- `clean_line(line)` - 清理注释和空白
- `parse_c_instruction(instr)` - 解析C指令

**导出常量**:
- `COMP_TABLE` - comp字段编码表
- `JUMP_TABLE` - jump字段编码表
- `PREDEFINED` - 预定义符号表

#### 2. cpu.py
**职责**: HACK CPU模拟器
- 指令执行
- 寄存器管理
- 内存访问

**主要类**:
- `CPUState` - CPU状态快照（dataclass）
- `HackCPU` - CPU主类

**HackCPU方法**:
- `step()` - 执行一条指令
- `reset()` - 重置CPU
- `get_state()` - 获取状态快照
- `set_ram(addr, val)` - 设置RAM
- `get_ram(addr)` - 读取RAM

#### 3. debugger.py
**职责**: 交互式调试器
- 断点管理
- 程序控制（单步、运行）
- 状态查看

**主要类**:
- `Debugger` - 调试器主类

**主要方法**:
- `add_breakpoint(addr)` - 添加断点
- `remove_breakpoint(addr)` - 删除断点
- `step()` - 单步执行
- `run_until_breakpoint()` - 运行到断点
- `get_registers()` - 获取寄存器
- `get_ram_range(start, count)` - 获取RAM范围

#### 4. excel_view.py
**职责**: Excel动态可视化
- 实时更新ROM/RAM
- 颜色高亮（当前指令、断点、修改值）
- 工作簿管理

**主要类**:
- `ExcelView` - Excel视图管理器

**主要方法**:
- `initialize(source, ram_size)` - 初始化工作簿
- `update(cpu, debugger, ram_size)` - 更新视图
- `close()` - 关闭工作簿

**颜色方案**:
- 黄色: 当前指令
- 红色: 断点
- 绿色: 修改的值

#### 5. config.py
**职责**: 配置管理
- 加载JSON配置
- 类型安全的配置访问
- 单例模式

**主要类**:
- `Config` - 总配置（dataclass）
- `AssemblerConfig` - 汇编器配置
- `DebuggerConfig` - 调试器配置
- `ExcelConfig` - Excel配置
- `PathsConfig` - 路径配置

**主要函数**:
- `get_config()` - 获取全局配置（单例）
- `reload_config()` - 重新加载配置

### 测试模块 (tests/)

#### 1. test_suite.py
**职责**: 综合测试套件
- 7个测试用例
- 测试结果统计
- 错误处理

**测试类**:
- `TestSuite` - 测试套件主类

**测试方法**:
- `test_assembler_basic()` - 汇编器基础
- `test_cpu_addition()` - CPU加法
- `test_counter_program()` - 计数器程序
- `test_debugger_breakpoints()` - 断点功能
- `test_excel_view()` - Excel视图
- `test_register_tracking()` - 寄存器跟踪
- `test_config_loading()` - 配置加载

#### 2. test_utils.py
**职责**: 测试工具函数
- 简化测试代码
- 提高代码复用

**主要函数**:
- `load_test_program(name)` - 加载测试程序
- `create_test_cpu(name)` - 创建测试CPU
- `create_test_debugger(name)` - 创建测试调试器
- `run_until_ram_equals(cpu, addr, val)` - 运行直到RAM满足条件

#### 3. test_programs/
**职责**: 存放测试用的.asm程序

**程序列表**:
- `add.asm` - 简单加法 (R2 = R0 + R1)
- `counter.asm` - 从10倒数到0
- `register.asm` - 寄存器操作测试

### 主程序 (main_new.py)

**职责**: 统一CLI入口
- 参数解析
- 命令分发
- 交互式调试循环

**命令**:
1. `asm` - 汇编命令
2. `debug` - 调试命令
3. `config` - 配置管理命令

**函数**:
- `cmd_assemble(args)` - 汇编逻辑
- `cmd_debug(args)` - 调试逻辑
- `print_help()` - 打印帮助
- `main()` - 主入口

### 配置文件 (config.json)

**结构**:
```json
{
  "assembler": {...},   # 汇编器配置
  "debugger": {...},    # 调试器配置
  "excel": {...},       # Excel配置
  "paths": {...}        # 路径配置
}
```

## 模块依赖关系

```
main_new.py
    ├── src.assembler
    ├── src.cpu
    ├── src.debugger
    ├── src.excel_view
    │   └── src.config
    └── src.config

tests/test_suite.py
    ├── tests.test_utils
    │   ├── src.assembler
    │   ├── src.cpu
    │   ├── src.debugger
    │   └── src.excel_view
    └── src.config
```

## 数据流

### 汇编流程
```
.asm文件
    ↓
assembler.assemble_file()
    ↓
(machine_code, source_lines)
    ↓
├→ save_hack_file() → .hack文件
└→ ExcelView.initialize() → .xlsx文件
```

### 调试流程
```
.asm文件
    ↓
assembler.assemble_file()
    ↓
HackCPU(machine_code)
    ↓
Debugger(cpu, source)
    ↓
ExcelView.update()
    ↓
交互式命令循环
```

### 配置流程
```
config.json
    ↓
Config.load()
    ↓
get_config() (单例)
    ↓
各模块使用配置
```

## 扩展点

### 1. 添加新的汇编指令
编辑 `src/assembler.py`:
- 更新 `COMP_TABLE`
- 修改 `parse_c_instruction()`

### 2. 添加新的调试命令
编辑 `main_new.py` 的调试循环

### 3. 自定义Excel样式
编辑 `src/excel_view.py`:
- 修改颜色常量
- 更新 `initialize()` 或 `update()`

### 4. 添加新的配置项
1. 编辑 `config.json` 添加字段
2. 编辑 `src/config.py` 添加到对应的dataclass
3. 在需要的模块中使用 `get_config()`

### 5. 添加新的测试
1. 在 `tests/test_programs/` 创建.asm
2. 在 `tests/test_suite.py` 添加测试方法
3. 使用 `test_utils.py` 中的辅助函数

## 代码统计

| 模块 | 代码行数 | 注释率 |
|------|---------|--------|
| src/assembler.py | ~194 | 25% |
| src/cpu.py | ~200 | 30% |
| src/debugger.py | ~125 | 20% |
| src/excel_view.py | ~180 | 25% |
| src/config.py | ~130 | 35% |
| tests/test_suite.py | ~270 | 15% |
| tests/test_utils.py | ~70 | 30% |
| main_new.py | ~350 | 20% |
| **总计** | **~1519** | **25%** |

## 设计原则

1. **单一职责**: 每个模块只负责一个功能域
2. **高内聚低耦合**: 模块内部紧密，模块间松散
3. **配置分离**: 配置与代码分离，便于调整
4. **测试完备**: 每个核心功能都有对应测试
5. **文档齐全**: 每个模块、类、函数都有注释
6. **可扩展性**: 预留扩展点，易于功能增加

## 性能考虑

- CPU模拟器使用整数运算，避免浮点数
- Excel更新按需进行，不是每步都保存
- 配置使用单例模式，避免重复加载
- 测试程序较小，快速执行

## 维护建议

1. 保持测试覆盖率在90%以上
2. 新功能必须添加测试
3. 配置项变更需更新文档
4. 重要修改需运行完整测试套件
5. 遵循现有代码风格和注释规范
