"""HACK调试器 - 支持断点、单步执行、查看状态等调试功能"""

from __future__ import annotations
from typing import Set, List, Optional
from .cpu import HackCPU, CPUState


class Debugger:
    """HACK程序调试器"""
    
    def __init__(self, cpu: HackCPU, source_lines: List[str]):
        """
        初始化调试器
        
        Args:
            cpu: CPU模拟器实例
            source_lines: 源代码行列表（与ROM对应）
        """
        self.cpu = cpu
        self.source_lines = source_lines
        self.breakpoints: Set[int] = set()  # 断点集合（ROM地址）
        self.running = False
        
    def add_breakpoint(self, address: int) -> bool:
        """
        在指定地址添加断点
        
        Args:
            address: ROM地址
            
        Returns:
            成功返回True
        """
        if 0 <= address < len(self.cpu.rom):
            self.breakpoints.add(address)
            return True
        return False
        
    def remove_breakpoint(self, address: int) -> bool:
        """移除指定地址的断点"""
        if address in self.breakpoints:
            self.breakpoints.discard(address)
            return True
        return False
        
    def clear_breakpoints(self):
        """清除所有断点"""
        self.breakpoints.clear()
        
    def step(self) -> tuple[bool, CPUState]:
        """
        执行一步
        
        Returns:
            (是否成功, CPU状态)
        """
        success = self.cpu.step()
        state = self.cpu.get_state()
        return success, state
        
    def run_until_breakpoint(self, max_steps: int = 100000) -> tuple[str, CPUState]:
        """
        运行直到遇到断点或停机
        
        Args:
            max_steps: 最大执行步数（防止死循环）
            
        Returns:
            (停止原因, CPU状态)
            停止原因可能是: "breakpoint", "halted", "max_steps"
        """
        self.running = True
        steps = 0
        
        while self.running and steps < max_steps:
            # 检查断点
            if self.cpu.PC in self.breakpoints:
                self.running = False
                return "breakpoint", self.cpu.get_state()
                
            # 执行一步
            success = self.cpu.step()
            steps += 1
            
            if not success:
                self.running = False
                return "halted", self.cpu.get_state()
                
        if steps >= max_steps:
            self.running = False
            return "max_steps", self.cpu.get_state()
            
        self.running = False
        return "stopped", self.cpu.get_state()
        
    def stop(self):
        """停止运行"""
        self.running = False
        
    def reset(self):
        """重置CPU和调试器状态"""
        self.cpu.reset()
        self.running = False
        
    def get_current_line(self) -> Optional[str]:
        """获取当前PC指向的源代码行"""
        if 0 <= self.cpu.PC < len(self.source_lines):
            return self.source_lines[self.cpu.PC]
        return None
        
    def get_registers(self) -> dict:
        """获取所有寄存器的值"""
        return {
            "A": self.cpu.A,
            "D": self.cpu.D,
            "PC": self.cpu.PC,
        }
        
    def get_ram_range(self, start: int, count: int) -> List[int]:
        """获取指定范围的RAM内容"""
        result = []
        for addr in range(start, min(start + count, len(self.cpu.ram))):
            result.append(self.cpu.ram[addr])
        return result
        
    def set_ram_value(self, address: int, value: int):
        """设置RAM值（用于调试时手动修改内存）"""
        self.cpu.set_ram(address, value)
