"""调试TEST.asm的ODD.EVEN部分"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import assemble_file, HackCPU


def debug_odd_even():
    """逐步调试奇数+偶数情况"""
    test_file = Path(__file__).parent / "test_programs" / "TEST.asm"
    
    machine_code, source_lines = assemble_file(test_file)
    cpu = HackCPU(machine_code)
    
    # X=1, Y=4
    cpu.set_ram(0, 1)
    cpu.set_ram(1, 4)
    
    # 手动执行到ODD.EVEN部分
    print("开始执行...")
    print(f"初始: R0={cpu.get_ram(0)}, R1={cpu.get_ram(1)}, R2={cpu.get_ram(2)}")
    
    for step in range(100):
        pc = cpu.PC
        instr = source_lines[pc] if pc < len(source_lines) else "???"
        
        # 显示关键变量
        if "interval_value" in instr or "R2" in instr or "OE.LOOP" in instr:
            interval_val = cpu.get_ram(cpu.symbols.get("interval_value", 999)) if hasattr(cpu, 'symbols') else "?"
            r2 = cpu.get_ram(2)
            print(f"Step {step:3d} PC={pc:3d}: {instr:30s} | R2={r2:4d}, interval=?")
        
        pc_before = cpu.PC
        cpu.step()
        
        if cpu.PC == pc_before and step > 50:
            print(f"\n到达STOP循环")
            break
    
    print(f"\n最终结果: R2 = {cpu.get_ram(2)}")
    
    # 显示所有RAM
    print("\nRAM内容:")
    for addr in range(20):
        val = cpu.get_ram(addr)
        if val != 0:
            print(f"  RAM[{addr}] = {val}")


if __name__ == "__main__":
    debug_odd_even()
