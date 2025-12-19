"""HACK CPU模拟器 - 模拟HACK计算机的CPU执行"""

from __future__ import annotations
from typing import List, Optional, Set
from dataclasses import dataclass


@dataclass
class CPUState:
    """CPU当前状态快照"""
    A: int = 0  # A寄存器
    D: int = 0  # D寄存器
    PC: int = 0  # 程序计数器
    last_modified: Set[str] = None  # 最近修改的寄存器/内存地址
    
    def __post_init__(self):
        if self.last_modified is None:
            self.last_modified = set()


class HackCPU:
    """HACK CPU模拟器"""
    
    def __init__(self, rom: List[str], ram_size: int = 24577):
        """
        初始化CPU
        
        Args:
            rom: 机器码指令列表（16位二进制字符串）
            ram_size: RAM大小（默认24577，包含屏幕和键盘映射）
        """
        self.rom = rom  # ROM（程序存储器）
        self.ram = [0] * ram_size  # RAM（数据存储器）
        self.A = 0  # A寄存器
        self.D = 0  # D寄存器
        self.PC = 0  # 程序计数器
        self.halted = False  # 是否停机
        self.last_modified: Set[str] = set()  # 上次修改的位置
        
    def reset(self):
        """重置CPU到初始状态"""
        self.ram = [0] * len(self.ram)
        self.A = 0
        self.D = 0
        self.PC = 0
        self.halted = False
        self.last_modified.clear()
        
    def get_state(self) -> CPUState:
        """获取当前CPU状态快照"""
        return CPUState(
            A=self.A,
            D=self.D,
            PC=self.PC,
            last_modified=self.last_modified.copy()
        )
        
    def step(self) -> bool:
        """
        执行一条指令
        
        Returns:
            True表示成功执行，False表示已停机或超出ROM范围
        """
        self.last_modified.clear()
        
        if self.halted or self.PC < 0 or self.PC >= len(self.rom):
            self.halted = True
            return False
            
        instruction = self.rom[self.PC]
        
        # A指令：@value，格式为 0vvvvvvvvvvvvvvv
        if instruction[0] == "0":
            value = int(instruction, 2)
            self.A = value
            self.last_modified.add("A")
            self.PC += 1
            return True
            
        # C指令：dest=comp;jump，格式为 111accccccdddjjj
        # 111 + a(1) + cccccc(6) + ddd(3) + jjj(3)
        a_bit = int(instruction[3])
        comp_bits = instruction[4:10]
        dest_bits = instruction[10:13]
        jump_bits = instruction[13:16]
        
        # 计算comp值
        comp_value = self._compute(comp_bits, a_bit)
        
        # 写入dest
        dest_a, dest_d, dest_m = dest_bits[0] == "1", dest_bits[1] == "1", dest_bits[2] == "1"
        if dest_a:
            self.A = comp_value
            self.last_modified.add("A")
        if dest_d:
            self.D = comp_value
            self.last_modified.add("D")
        if dest_m:
            addr = self.A % len(self.ram)
            self.ram[addr] = comp_value
            self.last_modified.add(f"M[{addr}]")
            
        # 处理jump
        should_jump = self._should_jump(comp_value, jump_bits)
        if should_jump:
            self.PC = self.A
            self.last_modified.add("PC")
        else:
            self.PC += 1
            
        return True
        
    def _compute(self, comp_bits: str, a_bit: int) -> int:
        """根据comp字段和a位计算结果"""
        # a=0时使用A寄存器，a=1时使用M[A]
        am_value = self.ram[self.A % len(self.ram)] if a_bit else self.A
        
        # comp字段解码（6位）
        comp_map = {
            "101010": 0,
            "111111": 1,
            "111010": -1,
            "001100": self.D,
            "110000": am_value,
            "001101": ~self.D,
            "110001": ~am_value,
            "001111": -self.D,
            "110011": -am_value,
            "011111": self.D + 1,
            "110111": am_value + 1,
            "001110": self.D - 1,
            "110010": am_value - 1,
            "000010": self.D + am_value,
            "010011": self.D - am_value,
            "000111": am_value - self.D,
            "000000": self.D & am_value,
            "010101": self.D | am_value,
        }
        
        result = comp_map.get(comp_bits, 0)
        # HACK使用16位有符号整数
        return self._to_signed_16bit(result)
        
    def _should_jump(self, comp_value: int, jump_bits: str) -> bool:
        """判断是否应该跳转"""
        if jump_bits == "000":
            return False
        if jump_bits == "111":  # JMP
            return True
        if jump_bits == "001":  # JGT
            return comp_value > 0
        if jump_bits == "010":  # JEQ
            return comp_value == 0
        if jump_bits == "011":  # JGE
            return comp_value >= 0
        if jump_bits == "100":  # JLT
            return comp_value < 0
        if jump_bits == "101":  # JNE
            return comp_value != 0
        if jump_bits == "110":  # JLE
            return comp_value <= 0
        return False
        
    def _to_signed_16bit(self, value: int) -> int:
        """将整数转换为16位有符号整数范围"""
        # Python的int是任意精度，需要模拟16位有符号整数
        value = value & 0xFFFF  # 保留低16位
        if value >= 0x8000:  # 如果最高位为1，表示负数
            value -= 0x10000
        return value
        
    def set_ram(self, address: int, value: int):
        """设置RAM指定地址的值"""
        if 0 <= address < len(self.ram):
            self.ram[address] = self._to_signed_16bit(value)
            
    def get_ram(self, address: int) -> int:
        """获取RAM指定地址的值"""
        if 0 <= address < len(self.ram):
            return self.ram[address]
        return 0
