"""配置管理模块 - 加载和管理应用程序配置"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class AssemblerConfig:
    """汇编器配置"""
    default_output_dir: str = "output"
    create_hack_file: bool = True
    create_excel_view: bool = False


@dataclass
class DebuggerConfig:
    """调试器配置"""
    default_excel_file: str = "HACKCompiler.xlsx"
    ram_view_size: int = 64
    max_steps: int = 100000
    auto_save_excel: bool = True


@dataclass
class ExcelConfig:
    """Excel视图配置"""
    color_current_instruction: str = "FFFF00"
    color_breakpoint: str = "FF6B6B"
    color_modified_value: str = "90EE90"
    show_headers: bool = True
    auto_adjust_columns: bool = True


@dataclass
class PathsConfig:
    """路径配置"""
    test_programs: str = "tests/test_programs"
    output: str = "output"


@dataclass
class Config:
    """应用程序总配置"""
    assembler: AssemblerConfig = field(default_factory=AssemblerConfig)
    debugger: DebuggerConfig = field(default_factory=DebuggerConfig)
    excel: ExcelConfig = field(default_factory=ExcelConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> Config:
        """
        从JSON文件加载配置
        
        Args:
            config_path: 配置文件路径，默认为config.json
            
        Returns:
            Config实例
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.json"
            
        if not config_path.exists():
            # 返回默认配置
            return cls()
            
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return cls(
                assembler=AssemblerConfig(**data.get("assembler", {})),
                debugger=DebuggerConfig(**data.get("debugger", {})),
                excel=ExcelConfig(**data.get("excel", {})),
                paths=PathsConfig(**data.get("paths", {}))
            )
        except Exception as e:
            print(f"警告: 加载配置文件失败 ({e})，使用默认配置")
            return cls()
    
    def save(self, config_path: Optional[Path] = None) -> None:
        """
        保存配置到JSON文件
        
        Args:
            config_path: 配置文件路径，默认为config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.json"
            
        data = {
            "assembler": self.assembler.__dict__,
            "debugger": self.debugger.__dict__,
            "excel": self.excel.__dict__,
            "paths": self.paths.__dict__
        }
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例（单例模式）"""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config(config_path: Optional[Path] = None) -> Config:
    """重新加载配置"""
    global _config
    _config = Config.load(config_path)
    return _config
