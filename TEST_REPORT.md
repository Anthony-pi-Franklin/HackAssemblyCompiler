# TEST.asm 测试报告

## 测试日期
2025年12月19日

## 测试文件
`tests/test_programs/TEST.asm` (356行，学号: 20616323 Xiaoyu SHEN)

## 测试结果
✅ **所有测试通过**

## 发现的问题及修正

### 1. 汇编器问题：缺少交换律指令支持

**问题描述**：
- COMP_TABLE中只有 `D+M` 但没有 `M+D`
- TEST.asm使用了 `M+D` 导致编译失败
- 错误信息：`ValueError: 未知的comp字段: M+D`

**修正方案**：
在 [src/assembler.py](src/assembler.py) 的COMP_TABLE中添加交换律等价指令：
- `M+D` (与 `D+M` 等价)
- `A+D` (与 `D+A` 等价)
- `M&D` (与 `D&M` 等价)
- `A&D` (与 `D&A` 等价)
- `M|D` (与 `D|M` 等价)
- `A|D` (与 `D|A` 等价)

**影响**：无副作用，增强了编译器对标准HACK汇编的兼容性

---

### 2. TEST.asm Bug #1：奇偶性检测错误

**问题描述**：
- 奇偶性检测代码错误：`D=D&M` 时D的值为0
- 导致所有情况都被判断为EVEN.EVEN

**原始代码** (第158-169行):
```asm
@0
D=A
@R2
M=D

// check the parity of X
@R0
D=D&M   // ❌ 错误！此时D=0
@R3
M=D
```

**修正后**:
```asm
@0
D=A
@R2
M=D

// check the parity of X
@R0
D=M           // ✅ 先加载R0
@parity_checker
D=D&M         // ✅ 再进行AND操作
@R3
M=D
```

---

### 3. TEST.asm Bug #2：ODD.EVEN循环边界错误

**问题描述**：
- ODD.EVEN部分在累加后才检查循环条件
- 导致多累加一次（例如：期望10，实际得到15）

**原始逻辑**:
```asm
(OE.LOOP)
    M=M+1         // interval++
    D=M
    @R2
    M=M+D         // ❌ 先累加
    @R1
    D=M-D         // ❌ 后检查
@OE.LOOP
D;JGE
```

**执行流程** (X=1, Y=4):
1. interval=1, R2+=1=1, 判断1<=4, 继续
2. interval=2, R2+=2=3, 判断2<=4, 继续
3. interval=3, R2+=3=6, 判断3<=4, 继续
4. interval=4, R2+=4=10, 判断4<=4, 继续
5. interval=5, R2+=5=**15**, 判断5<=4, 退出 ❌

**修正后**:
```asm
(OE.LOOP)
    M=M+1         // interval++
    D=M
    @R1
    D=D-M         // ✅ 先检查
    @SORT
    D;JGT         // ✅ 超出则退出
    
    @interval_value
    D=M
    @R2
    M=M+D         // ✅ 未超出才累加
@OE.LOOP
0;JMP
```

**修正后执行流程**:
1. interval=1, 判断1>4?否, R2+=1=1
2. interval=2, 判断2>4?否, R2+=2=3
3. interval=3, 判断3>4?否, R2+=3=6
4. interval=4, 判断4>4?否, R2+=4=10
5. interval=5, 判断5>4?**是**, 退出 ✅ (R2=10)

---

### 4. 导入问题：相对导入失败

**问题描述**：
- [src/debugger.py](src/debugger.py) 使用了绝对导入 `from cpu import ...`
- 在包结构下运行时失败

**修正**：
```python
# 修正前
from cpu import HackCPU, CPUState

# 修正后
from .cpu import HackCPU, CPUState
```

---

## 测试用例

### 测试1: 编译测试
- **输入**: TEST.asm (613行源代码)
- **输出**: 356条机器码指令
- **结果**: ✅ 编译成功

### 测试2: 偶数+偶数执行
- **输入**: R0=4 (偶数), R1=10 (偶数)
- **预期**: 4+6+8+10 = 28 (偶数序列和)
- **实际**: R2 = 28
- **结果**: ✅ 通过

### 测试3: 奇数+偶数执行
- **输入**: R0=1 (奇数), R1=4 (偶数)
- **预期**: 1+2+3+4 = 10 (完整序列和)
- **实际**: R2 = 10
- **结果**: ✅ 通过

---

## 完整测试套件结果

运行 `tests/test_suite.py`:

```
============================================================
HACK Compiler & Debugger - Test Suite (Refactored)
============================================================

[PASS] Assembler Basic
[PASS] CPU Addition
[PASS] Counter Program
[PASS] Debugger Breakpoints
[PASS] Excel View
[PASS] Register Tracking
[PASS] Config Loading

Total: 7
Passed: 7
Failed: 0

[SUCCESS] All tests passed!
```

---

## 文件变更汇总

### 修改的文件
1. **src/assembler.py** - 添加交换律指令支持 (+6 指令)
2. **src/debugger.py** - 修正相对导入
3. **tests/test_programs/TEST.asm** - 修正2个bug
4. **tests/test_utils.py** - 修正导入路径
5. **tests/test_suite.py** - 修正导入路径

### 新增的文件
1. **tests/test_TEST_asm.py** - TEST.asm专项测试套件
2. **tests/test_programs/minimal_oddeven.asm** - 最小ODD.EVEN测试
3. **tests/simple_debug.py** - 简单调试脚本
4. **tests/debug_test.py** - 详细调试工具

---

## 编译器增强

### 新增COMP指令支持
```python
COMP_TABLE = {
    # 原有28条
    ...
    
    # 新增6条交换律等价指令
    "A+D": "0000010",  # 与D+A等价
    "M+D": "1000010",  # 与D+M等价
    "A&D": "0000000",  # 与D&A等价
    "M&D": "1000000",  # 与D&M等价
    "A|D": "0010101",  # 与D|A等价
    "M|D": "1010101",  # 与D|M等价
}
```

现在支持 **34条COMP指令**（原28条 + 6条交换律）

---

## 总结

1. ✅ TEST.asm成功编译（356条指令）
2. ✅ 修正汇编器以支持交换律指令
3. ✅ 修正TEST.asm中的2个逻辑bug
4. ✅ 所有测试通过（7/7）
5. ✅ 项目结构保持完整性

TEST.asm现在可以正确执行奇偶性判断和算术累加逻辑。
