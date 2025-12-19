"""HACK Compiler & Debugger - 核心模块包"""

from .assembler import (
    assemble_file,
    save_hack_file,
    COMP_TABLE,
    JUMP_TABLE,
    PREDEFINED
)
from .cpu import HackCPU, CPUState
from .debugger import Debugger
from .excel_view import ExcelView
from .config import Config, get_config, reload_config

__version__ = "2.0.0"
__all__ = [
    "assemble_file",
    "save_hack_file",
    "HackCPU",
    "CPUState",
    "Debugger",
    "ExcelView",
    "Config",
    "get_config",
    "reload_config",
    "COMP_TABLE",
    "JUMP_TABLE",
    "PREDEFINED"
]
