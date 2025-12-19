"""简单调试 - 检查ODD.EVEN计算"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import assemble_file, HackCPU


test_file = Path(__file__).parent / "test_programs" / "TEST.asm"
machine_code, source_lines = assemble_file(test_file)
cpu = HackCPU(machine_code)

# X=1, Y=4
cpu.set_ram(0, 1)
cpu.set_ram(1, 4)

print("测试: X=1, Y=4 (奇数+偶数)")
print("期望: 1+2+3+4 = 10\n")

# 执行程序
for step in range(500):
    pc_before = cpu.PC
    cpu.step()
    
    # 每执行一条指令后检查R2
    if step % 50 == 0:
        print(f"Step {step}: R2 = {cpu.get_ram(2)}")
    
    if cpu.PC == pc_before and step > 100:
        break

print(f"\n最终: R2 = {cpu.get_ram(2)}")

# 显示所有非零RAM
print("\n非零RAM值:")
for i in range(20):
    val = cpu.get_ram(i)
    if val != 0:
        print(f"  RAM[{i}] = {val}")
