"""HACK汇编器模块 - 负责将.asm源文件翻译为机器码"""

from __future__ import annotations
from typing import Dict, List, Iterable
import pathlib


# HACK指令集规范中的comp字段编码表
COMP_TABLE: Dict[str, str] = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "A+D": "0000010",  # 与D+A等价
    "D+M": "1000010",
    "M+D": "1000010",  # 与D+M等价
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "A&D": "0000000",  # 与D&A等价
    "D&M": "1000000",
    "M&D": "1000000",  # 与D&M等价
    "D|A": "0010101",
    "A|D": "0010101",  # 与D|A等价
    "D|M": "1010101",
    "M|D": "1010101",  # 与D|M等价
}

# jump字段编码表
JUMP_TABLE: Dict[str, str] = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

# 预定义符号表
PREDEFINED: Dict[str, int] = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
    **{f"R{i}": i for i in range(16)},
}


def clean_line(line: str) -> str:
    """去除空白和注释，返回净化后的指令"""
    no_comment = line.split("//", 1)[0]
    return no_comment.strip()


def parse_dest(dest_field: str) -> str:
    """解析dest字段，返回3位二进制编码 (A D M)"""
    if not dest_field:
        return "000"
    bits = ["0", "0", "0"]  # A, D, M
    for ch in dest_field:
        if ch == "A":
            bits[0] = "1"
        elif ch == "D":
            bits[1] = "1"
        elif ch == "M":
            bits[2] = "1"
        else:
            raise ValueError(f"无效的dest字段: {dest_field}")
    return "".join(bits)


def parse_c_instruction(instruction: str) -> str:
    """将C指令翻译为16位二进制机器码"""
    dest_field = ""
    jump_field = ""
    comp_field = instruction

    if "=" in instruction:
        dest_field, comp_field = instruction.split("=", 1)
    if ";" in comp_field:
        comp_field, jump_field = comp_field.split(";", 1)

    comp_bits = COMP_TABLE.get(comp_field)
    if comp_bits is None:
        raise ValueError(f"未知的comp字段: {comp_field}")
    dest_bits = parse_dest(dest_field)
    jump_bits = JUMP_TABLE.get(jump_field, "000")
    return "111" + comp_bits + dest_bits + jump_bits


def first_pass(lines: Iterable[str]) -> Dict[str, int]:
    """第一遍扫描：收集标签定义，返回符号表"""
    symbols = dict(PREDEFINED)
    current_address = 0
    for line in lines:
        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1]
            symbols[label] = current_address
        else:
            current_address += 1
    return symbols


def second_pass(
    lines: Iterable[str], symbols: Dict[str, int]
) -> tuple[List[str], List[str]]:
    """第二遍扫描：生成机器码，并保留对应的汇编源码"""
    rom_binary: List[str] = []
    rom_source: List[str] = []
    next_variable = 16

    for line in lines:
        if line.startswith("(") and line.endswith(")"):
            continue
        if line.startswith("@"):
            symbol = line[1:]
            if symbol.isdigit():
                address = int(symbol)
            else:
                if symbol not in symbols:
                    symbols[symbol] = next_variable
                    next_variable += 1
                address = symbols[symbol]
            rom_binary.append(f"0{address:015b}")
        else:
            rom_binary.append(parse_c_instruction(line))
        rom_source.append(line)

    return rom_binary, rom_source


def assemble_file(source: pathlib.Path) -> tuple[List[str], List[str]]:
    """
    汇编一个.asm文件，返回(机器码列表, 源码列表)
    
    Args:
        source: .asm源文件路径
        
    Returns:
        (rom_binary, rom_source): 机器码和源码的对应列表
    """
    raw_lines = source.read_text(encoding="utf-8").splitlines()
    lines = [clean_line(line) for line in raw_lines]
    lines = [line for line in lines if line]

    symbols = first_pass(lines)
    machine_code, machine_source = second_pass(lines, symbols)

    return machine_code, machine_source


def save_hack_file(machine_code: List[str], destination: pathlib.Path) -> None:
    """将机器码保存为.hack文件"""
    destination.write_text("\n".join(machine_code) + "\n", encoding="utf-8")
