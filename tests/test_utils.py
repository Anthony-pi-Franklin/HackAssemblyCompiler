"""测试工具模块 - 提供测试辅助函数"""

from pathlib import Path
from typing import List, Tuple
import sys

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import assemble_file, HackCPU, Debugger, ExcelView


def load_test_program(program_name: str) -> Tuple[List[str], List[str]]:
    """
    加载测试程序
    
    Args:
        program_name: 程序名称（不带.asm后缀）
        
    Returns:
        (机器码列表, 源码列表)
    """
    test_dir = Path(__file__).parent / "test_programs"
    asm_file = test_dir / f"{program_name}.asm"
    
    if not asm_file.exists():
        raise FileNotFoundError(f"测试程序不存在: {asm_file}")
    
    return assemble_file(asm_file)


def create_test_cpu(program_name: str) -> Tuple[HackCPU, List[str]]:
    """
    创建加载了测试程序的CPU
    
    Args:
        program_name: 程序名称
        
    Returns:
        (CPU实例, 源码列表)
    """
    machine_code, source_lines = load_test_program(program_name)
    cpu = HackCPU(machine_code)
    return cpu, source_lines


def create_test_debugger(program_name: str) -> Tuple[Debugger, HackCPU, List[str]]:
    """
    创建加载了测试程序的调试器
    
    Args:
        program_name: 程序名称
        
    Returns:
        (调试器实例, CPU实例, 源码列表)
    """
    cpu, source_lines = create_test_cpu(program_name)
    debugger = Debugger(cpu, source_lines)
    return debugger, cpu, source_lines


def run_until_ram_equals(cpu: HackCPU, address: int, expected_value: int, max_steps: int = 1000) -> bool:
    """
    运行CPU直到指定RAM地址等于期望值
    
    Args:
        cpu: CPU实例
        address: RAM地址
        expected_value: 期望值
        max_steps: 最大步数
        
    Returns:
        是否成功达到期望值
    """
    for _ in range(max_steps):
        if cpu.get_ram(address) == expected_value:
            return True
        if not cpu.step():
            break
    return cpu.get_ram(address) == expected_value
