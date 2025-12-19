"""TEST.asm 专项测试"""

import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import assemble_file, HackCPU


def test_test_asm_compilation():
    """测试TEST.asm能否成功编译"""
    print("=" * 60)
    print("测试 TEST.asm 编译")
    print("=" * 60)
    
    test_file = Path(__file__).parent / "test_programs" / "TEST.asm"
    
    try:
        machine_code, source_lines = assemble_file(test_file)
        print(f"✓ 编译成功，共 {len(machine_code)} 条指令")
        print(f"✓ 源代码行数: {len(source_lines)}")
        return True
    except Exception as e:
        print(f"✗ 编译失败: {e}")
        return False


def test_test_asm_execution_simple():
    """测试TEST.asm简单执行（偶数+偶数情况）"""
    print("\n" + "=" * 60)
    print("测试 TEST.asm 执行 - 偶数+偶数")
    print("=" * 60)
    
    test_file = Path(__file__).parent / "test_programs" / "TEST.asm"
    
    machine_code, source_lines = assemble_file(test_file)
    cpu = HackCPU(machine_code)
    
    # 测试用例: X=4, Y=10 (都是偶数)
    # 应该计算从4到10的偶数和: 4+6+8+10 = 28
    cpu.set_ram(0, 4)   # R0 = X = 4
    cpu.set_ram(1, 10)  # R1 = Y = 10
    
    # 运行最多10000步
    max_steps = 10000
    for step in range(max_steps):
        pc_before = cpu.PC
        cpu.step()
        # 检测是否到达STOP标签的无限循环
        if cpu.PC == pc_before and step > 100:
            break
    
    result = cpu.get_ram(2)
    print(f"  X=4, Y=10 (偶数+偶数)")
    print(f"  预期结果: 4+6+8+10 = 28")
    print(f"  实际结果: R2 = {result}")
    print(f"  执行步数: {step + 1}")
    
    if result == 28:
        print("✓ 测试通过")
        return True
    else:
        print(f"✗ 测试失败: 期望28，得到{result}")
        return False


def test_test_asm_odd_even():
    """测试TEST.asm执行 - 奇数+偶数"""
    print("\n" + "=" * 60)
    print("测试 TEST.asm 执行 - 奇数+偶数")
    print("=" * 60)
    
    test_file = Path(__file__).parent / "test_programs" / "TEST.asm"
    
    machine_code, source_lines = assemble_file(test_file)
    cpu = HackCPU(machine_code)
    
    # 测试用例: X=1, Y=4 (奇数+偶数)
    # 应该计算从1到4所有整数和: 1+2+3+4 = 10
    cpu.set_ram(0, 1)   # R0 = X = 1
    cpu.set_ram(1, 4)   # R1 = Y = 4
    
    max_steps = 10000
    for step in range(max_steps):
        pc_before = cpu.PC
        cpu.step()
        if cpu.PC == pc_before and step > 100:
            break
    
    result = cpu.get_ram(2)
    print(f"  X=1, Y=4 (奇数+偶数)")
    print(f"  预期结果: 1+2+3+4 = 10")
    print(f"  实际结果: R2 = {result}")
    print(f"  执行步数: {step + 1}")
    
    if result == 10:
        print("✓ 测试通过")
        return True
    else:
        print(f"✗ 测试失败: 期望10，得到{result}")
        return False


def main():
    """运行所有TEST.asm测试"""
    print("\n" + "=" * 60)
    print("TEST.asm 专项测试套件")
    print("=" * 60 + "\n")
    
    results = []
    
    # 测试1: 编译
    results.append(("编译测试", test_test_asm_compilation()))
    
    # 测试2: 偶数+偶数执行
    results.append(("偶数+偶数执行", test_test_asm_execution_simple()))
    
    # 测试3: 奇数+偶数执行
    results.append(("奇数+偶数执行", test_test_asm_odd_even()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\n总计: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！")
        return 0
    else:
        print("\n[FAILED] 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
