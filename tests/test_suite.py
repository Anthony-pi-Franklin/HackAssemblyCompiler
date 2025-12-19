"""HACK编译器和调试器综合测试套件（重构版）"""

import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_utils import (
    load_test_program,
    create_test_cpu,
    create_test_debugger,
    run_until_ram_equals
)
from src import HackCPU, Debugger, ExcelView, get_config


class TestSuite:
    """测试套件类"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.config = get_config()
        
    def run_test(self, test_name: str, test_func):
        """运行单个测试"""
        try:
            print(f"\n{'='*60}")
            print(f"Test: {test_name}")
            print(f"{'='*60}")
            test_func()
            self.passed += 1
            print(f"[PASS] {test_name}")
        except AssertionError as e:
            self.failed += 1
            print(f"[FAIL] {test_name}: {e}")
        except Exception as e:
            self.failed += 1
            print(f"[ERROR] {test_name}: {e}")
            import traceback
            traceback.print_exc()
    
    def test_assembler_basic(self):
        """测试基本汇编功能"""
        machine_code, source_lines = load_test_program("add")
        
        assert len(machine_code) == 10, f"Expected 10 instructions, got {len(machine_code)}"
        assert len(source_lines) == 10, f"Expected 10 source lines, got {len(source_lines)}"
        assert machine_code[0] == "0000000000000000", "First instruction should be @R0"
        
        print(f"  Assembled {len(machine_code)} instructions")
        print(f"  First instruction: {machine_code[0]}")
    
    def test_cpu_addition(self):
        """测试CPU加法运算"""
        cpu, source_lines = create_test_cpu("add")
        
        # 设置输入
        cpu.set_ram(0, 15)  # R0 = 15
        cpu.set_ram(1, 7)   # R1 = 7
        
        # 执行7步完成加法
        for _ in range(7):
            cpu.step()
        
        result = cpu.get_ram(2)
        assert result == 22, f"Expected R2=22, got {result}"
        
        print(f"  R0={cpu.get_ram(0)} + R1={cpu.get_ram(1)} = R2={result}")
    
    def test_counter_program(self):
        """测试计数器程序"""
        cpu, source_lines = create_test_cpu("counter")
        
        # 跟踪变量i (地址16)
        i_values = []
        for step in range(100):
            i_val = cpu.get_ram(16)
            if not i_values or i_val != i_values[-1]:
                i_values.append(i_val)
            
            if not cpu.step():
                break
            
            if i_val == 0 and step > 50:
                break
        
        expected = [0, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        actual = i_values[:12]
        assert actual == expected, f"Expected {expected}, got {actual}"
        
        print(f"  Counter sequence: {actual}")
    
    def test_debugger_breakpoints(self):
        """测试调试器断点功能"""
        debugger, cpu, source_lines = create_test_debugger("register")
        
        # 测试添加断点
        assert debugger.add_breakpoint(5), "Should add breakpoint at address 5"
        assert 5 in debugger.breakpoints, "Breakpoint should be in set"
        
        # 测试单步执行
        success, state = debugger.step()
        assert success, "First step should succeed"
        assert state.PC == 1, f"PC should be 1, got {state.PC}"
        
        # 测试运行到断点
        reason, state = debugger.run_until_breakpoint()
        assert reason == "breakpoint", f"Should stop at breakpoint, got {reason}"
        assert state.PC == 5, f"Should stop at PC=5, got {state.PC}"
        
        # 测试删除断点
        assert debugger.remove_breakpoint(5), "Should remove breakpoint"
        assert 5 not in debugger.breakpoints, "Breakpoint should be removed"
        
        print("  Breakpoint set/remove: OK")
        print("  Step execution: OK")
        print("  Run to breakpoint: OK")
    
    def test_excel_view(self):
        """测试Excel视图生成"""
        debugger, cpu, source_lines = create_test_debugger("register")
        debugger.add_breakpoint(3)
        
        # 创建Excel视图
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        excel_path = output_dir / "test_excel.xlsx"
        
        view = ExcelView(excel_path)
        view.initialize(source_lines, ram_size=16)
        
        # 执行几步
        for _ in range(5):
            cpu.step()
        
        # 更新视图
        view.update(cpu, debugger, ram_view_size=16)
        view.close()
        
        assert excel_path.exists(), "Excel file should be created"
        
        print(f"  Excel view created: {excel_path}")
        print(f"  Contains {len(source_lines)} ROM entries")
    
    def test_register_tracking(self):
        """测试寄存器修改跟踪"""
        cpu, source_lines = create_test_cpu("register")
        
        # Step 1: @5
        cpu.step()
        assert "A" in cpu.last_modified, "A should be modified"
        assert cpu.A == 5, "A should be 5"
        
        # Step 2: D=A
        cpu.step()
        assert "D" in cpu.last_modified, "D should be modified"
        assert cpu.D == 5, "D should be 5"
        
        # Step 3: @R0
        cpu.step()
        assert "A" in cpu.last_modified, "A should be modified"
        assert cpu.A == 0, "A should be 0"
        
        # Step 4: M=D
        cpu.step()
        assert "M[0]" in cpu.last_modified, "M[0] should be modified"
        assert cpu.get_ram(0) == 5, "RAM[0] should be 5"
        
        print("  Register tracking works correctly")
        print(f"  A=5, D=5, RAM[0]=5")
    
    def test_config_loading(self):
        """测试配置加载"""
        config = get_config()
        
        assert config.debugger.ram_view_size == 64, "RAM view size should be 64"
        assert config.excel.color_current_instruction == "FFFF00", "Current color should be yellow"
        assert config.assembler.create_hack_file == True, "Should create hack file by default"
        
        print(f"  Config loaded successfully")
        print(f"  RAM view size: {config.debugger.ram_view_size}")
        print(f"  Excel colors configured")
    
    def run_all(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("HACK Compiler & Debugger - Test Suite (Refactored)")
        print("="*60)
        
        tests = [
            ("Assembler Basic", self.test_assembler_basic),
            ("CPU Addition", self.test_cpu_addition),
            ("Counter Program", self.test_counter_program),
            ("Debugger Breakpoints", self.test_debugger_breakpoints),
            ("Excel View", self.test_excel_view),
            ("Register Tracking", self.test_register_tracking),
            ("Config Loading", self.test_config_loading),
        ]
        
        for name, test_func in tests:
            self.run_test(name, test_func)
        
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        print(f"Total: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        
        if self.failed == 0:
            print("\n[SUCCESS] All tests passed!")
        else:
            print(f"\n[WARNING] {self.failed} test(s) failed")
        
        return self.failed == 0


def main():
    """主测试入口"""
    suite = TestSuite()
    success = suite.run_all()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
