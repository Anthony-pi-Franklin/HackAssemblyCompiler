"""HACK编译器和调试器 - 主入口（重构版）"""

from __future__ import annotations
import argparse
import pathlib
import sys

# 添加src目录到路径
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))

from src import (
    assemble_file,
    save_hack_file,
    HackCPU,
    Debugger,
    ExcelView,
    get_config,
    reload_config
)


def cmd_assemble(args):
    """汇编命令：将.asm文件编译为.hack机器码"""
    source = args.source
    if not source.exists():
        print(f"错误：源文件不存在: {source}")
        return 1
    
    # 加载配置
    config = get_config()
    
    try:
        print(f"正在汇编 {source}...")
        machine_code, source_lines = assemble_file(source)
        
        # 确定输出目录
        if args.output_dir:
            output_dir = pathlib.Path(args.output_dir)
        else:
            output_dir = pathlib.Path(config.paths.output)
        output_dir.mkdir(exist_ok=True)
        
        # 保存.hack文件
        if not args.no_hack and config.assembler.create_hack_file:
            if args.output:
                destination = args.output
            else:
                destination = output_dir / source.with_suffix(".hack").name
            save_hack_file(machine_code, destination)
            print(f"已生成机器码: {destination}")
        
        # 保存Excel视图
        excel_enabled = args.excel or config.assembler.create_excel_view
        if excel_enabled:
            if args.excel:
                excel_path = args.excel
            else:
                excel_path = output_dir / source.with_suffix(".xlsx").name
            
            view = ExcelView(excel_path)
            view.initialize(source_lines, ram_size=args.ram_view)
            view.close()
            print(f"已生成Excel视图: {excel_path}")
        
        print(f"汇编完成，共 {len(machine_code)} 条指令")
        return 0
    
    except Exception as e:
        print(f"汇编错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_debug(args):
    """调试命令：交互式调试HACK程序"""
    source = args.source
    if not source.exists():
        print(f"错误：源文件不存在: {source}")
        return 1
    
    # 加载配置
    config = get_config()
    
    try:
        # 汇编程序
        print(f"正在加载程序 {source}...")
        machine_code, source_lines = assemble_file(source)
        print(f"已加载 {len(machine_code)} 条指令")
        
        # 初始化CPU和调试器
        cpu = HackCPU(machine_code)
        debugger = Debugger(cpu, source_lines)
        
        # 确定输出目录
        if args.output_dir:
            output_dir = pathlib.Path(args.output_dir)
        else:
            output_dir = pathlib.Path(config.paths.output)
        output_dir.mkdir(exist_ok=True)
        
        # 初始化Excel视图
        if args.excel:
            excel_path = args.excel
        else:
            excel_path = output_dir / config.debugger.default_excel_file
        
        view = ExcelView(excel_path)
        view.initialize(source_lines, ram_size=args.ram_view)
        
        # 初始更新
        view.update(cpu, debugger, ram_view_size=args.ram_view)
        print(f"Excel视图已创建: {excel_path}")
        
        # 交互式调试循环
        print("\n=== HACK调试器 ===")
        print_help()
        
        while True:
            try:
                cmd = input(f"\n[PC={cpu.PC}] > ").strip().lower()
                
                if not cmd:
                    continue
                
                if cmd in ["q", "quit", "exit"]:
                    print("退出调试器")
                    break
                
                elif cmd in ["h", "help", "?"]:
                    print_help()
                
                elif cmd in ["s", "step"]:
                    success, state = debugger.step()
                    if success:
                        if config.debugger.auto_save_excel:
                            view.update(cpu, debugger, ram_view_size=args.ram_view)
                        print(f"执行: {debugger.get_current_line() or '(无)'}")
                        print(f"寄存器: A={state.A}, D={state.D}, PC={state.PC}")
                    else:
                        print("程序已停止")
                
                elif cmd in ["r", "run"]:
                    print("运行中...")
                    reason, state = debugger.run_until_breakpoint(max_steps=config.debugger.max_steps)
                    view.update(cpu, debugger, ram_view_size=args.ram_view)
                    
                    if reason == "breakpoint":
                        print(f"在断点处停止 (PC={state.PC})")
                    elif reason == "halted":
                        print("程序已结束")
                    elif reason == "max_steps":
                        print("达到最大步数限制")
                    
                    print(f"寄存器: A={state.A}, D={state.D}, PC={state.PC}")
                
                elif cmd.startswith("b "):
                    try:
                        addr = int(cmd.split()[1])
                        if debugger.add_breakpoint(addr):
                            print(f"在地址 {addr} 设置断点")
                            view.update(cpu, debugger, ram_view_size=args.ram_view)
                        else:
                            print(f"无效的地址: {addr}")
                    except (ValueError, IndexError):
                        print("用法: b <地址>")
                
                elif cmd.startswith("d "):
                    try:
                        addr = int(cmd.split()[1])
                        if debugger.remove_breakpoint(addr):
                            print(f"已删除地址 {addr} 的断点")
                            view.update(cpu, debugger, ram_view_size=args.ram_view)
                        else:
                            print(f"地址 {addr} 没有断点")
                    except (ValueError, IndexError):
                        print("用法: d <地址>")
                
                elif cmd == "bc":
                    debugger.clear_breakpoints()
                    print("已清除所有断点")
                    view.update(cpu, debugger, ram_view_size=args.ram_view)
                
                elif cmd == "bl":
                    if debugger.breakpoints:
                        print("断点: " + ", ".join(str(bp) for bp in sorted(debugger.breakpoints)))
                    else:
                        print("无断点")
                
                elif cmd == "reset":
                    debugger.reset()
                    view.update(cpu, debugger, ram_view_size=args.ram_view)
                    print("已重置CPU")
                
                elif cmd == "reg":
                    regs = debugger.get_registers()
                    print(f"A = {regs['A']}")
                    print(f"D = {regs['D']}")
                    print(f"PC = {regs['PC']}")
                
                elif cmd.startswith("m "):
                    try:
                        parts = cmd.split()
                        if len(parts) == 2:
                            addr = int(parts[1])
                            print(f"RAM[{addr}] = {cpu.get_ram(addr)}")
                        elif len(parts) == 3:
                            start = int(parts[1])
                            count = int(parts[2])
                            values = debugger.get_ram_range(start, count)
                            for i, val in enumerate(values):
                                print(f"RAM[{start + i}] = {val}")
                    except (ValueError, IndexError):
                        print("用法: m <地址> [数量]")
                
                elif cmd.startswith("set "):
                    try:
                        parts = cmd.split()
                        addr = int(parts[1])
                        value = int(parts[2])
                        debugger.set_ram_value(addr, value)
                        view.update(cpu, debugger, ram_view_size=args.ram_view)
                        print(f"已设置 RAM[{addr}] = {value}")
                    except (ValueError, IndexError):
                        print("用法: set <地址> <值>")
                
                elif cmd == "config":
                    print("\n当前配置:")
                    print(f"  RAM视图大小: {config.debugger.ram_view_size}")
                    print(f"  最大步数: {config.debugger.max_steps}")
                    print(f"  自动保存Excel: {config.debugger.auto_save_excel}")
                    print(f"  输出目录: {config.paths.output}")
                
                else:
                    print(f"未知命令: {cmd}，输入 h 查看帮助")
            
            except KeyboardInterrupt:
                print("\n使用 'quit' 退出")
                continue
            except Exception as e:
                print(f"错误: {e}")
        
        view.close()
        return 0
    
    except Exception as e:
        print(f"调试器错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


def print_help():
    """打印帮助信息"""
    help_text = """
命令列表:
  s, step       - 单步执行一条指令
  r, run        - 运行直到断点或结束
  b <地址>      - 在指定地址设置断点
  d <地址>      - 删除指定地址的断点
  bc            - 清除所有断点
  bl            - 列出所有断点
  reg           - 查看寄存器值
  m <地址> [数量] - 查看内存（默认1个单元）
  set <地址> <值> - 设置内存值
  reset         - 重置CPU到初始状态
  config        - 显示当前配置
  h, help, ?    - 显示此帮助
  q, quit, exit - 退出调试器

Excel中的颜色:
  黄色 - 当前正在执行的指令
  红色 - 断点
  绿色 - 刚被修改的寄存器/内存值
"""
    print(help_text)


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="HACK汇编器和调试器",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 汇编命令
    asm_parser = subparsers.add_parser("asm", help="汇编.asm文件")
    asm_parser.add_argument("source", type=pathlib.Path, help=".asm源文件")
    asm_parser.add_argument("-o", "--output", type=pathlib.Path, help="输出.hack文件")
    asm_parser.add_argument("--output-dir", type=pathlib.Path, help="输出目录（默认使用config.json中的设置）")
    asm_parser.add_argument("--excel", type=pathlib.Path, help="输出Excel视图")
    asm_parser.add_argument("--ram-view", type=int, default=64, help="Excel中显示的RAM行数")
    asm_parser.add_argument("--no-hack", action="store_true", help="不生成.hack文件")
    
    # 调试命令
    debug_parser = subparsers.add_parser("debug", help="调试.asm程序")
    debug_parser.add_argument("source", type=pathlib.Path, help=".asm源文件")
    debug_parser.add_argument("--output-dir", type=pathlib.Path, help="输出目录（默认使用config.json中的设置）")
    debug_parser.add_argument("--excel", type=pathlib.Path, help="Excel视图文件")
    debug_parser.add_argument("--ram-view", type=int, default=64, help="Excel中显示的RAM行数")
    
    # 配置命令
    config_parser = subparsers.add_parser("config", help="显示或重载配置")
    config_parser.add_argument("--reload", action="store_true", help="重新加载配置文件")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "asm":
        return cmd_assemble(args)
    elif args.command == "debug":
        return cmd_debug(args)
    elif args.command == "config":
        if args.reload:
            reload_config()
            print("配置已重新加载")
        config = get_config()
        print("\n当前配置:")
        print(f"  汇编器:")
        print(f"    输出目录: {config.assembler.default_output_dir}")
        print(f"    创建.hack文件: {config.assembler.create_hack_file}")
        print(f"    创建Excel视图: {config.assembler.create_excel_view}")
        print(f"  调试器:")
        print(f"    默认Excel文件: {config.debugger.default_excel_file}")
        print(f"    RAM视图大小: {config.debugger.ram_view_size}")
        print(f"    最大步数: {config.debugger.max_steps}")
        print(f"  Excel颜色:")
        print(f"    当前指令: #{config.excel.color_current_instruction}")
        print(f"    断点: #{config.excel.color_breakpoint}")
        print(f"    修改值: #{config.excel.color_modified_value}")
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
