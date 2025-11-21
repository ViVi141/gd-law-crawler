#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
打包脚本 - 将项目打包成exe可执行文件
"""

import os
import sys
import shutil
import PyInstaller.__main__

def build_exe():
    """构建exe文件"""
    
    # 清理之前的构建文件
    print("清理旧的构建文件...")
    for dir_name in ['build', 'dist', '__pycache__']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  已删除: {dir_name}/")
    
    # 清理spec文件
    spec_file = 'gd-law-crawler.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"  已删除: {spec_file}")
    
    print("\n开始打包...")
    print("=" * 60)
    
    # PyInstaller参数
    # Windows下使用分号分隔，Linux/Mac使用冒号
    separator = ';' if sys.platform == 'win32' else ':'
    
    args = [
        'main.py',                          # 主入口文件
        '--name=gd-law-crawler',           # 生成的exe名称
        '--onefile',                        # 打包成单个exe文件
        '--windowed',                        # Windows下隐藏控制台窗口（GUI模式）
        '--icon=NONE',                      # 图标（如果有的话）
        f'--add-data=config.json.example{separator}.',  # 包含配置文件模板
        '--hidden-import=tkinter',          # 隐藏导入tkinter
        '--hidden-import=tkinter.ttk',      # 隐藏导入ttk
        '--hidden-import=tkinter.scrolledtext',  # 隐藏导入scrolledtext
        '--hidden-import=tkinter.filedialog',    # 隐藏导入filedialog
        '--hidden-import=tkinter.messagebox',    # 隐藏导入messagebox
        '--collect-all=requests',           # 收集requests的所有数据
        '--collect-all=docx',                # 收集python-docx的所有数据
        '--collect-all=pypdf',               # 收集pypdf的所有数据
        '--noconsole',                      # 不显示控制台窗口
        '--clean',                          # 清理临时文件
    ]
    
    # 如果需要命令行模式，可以添加 --console 参数
    # 但这里我们默认使用GUI模式（无控制台）
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 60)
        print("打包完成！")
        print("=" * 60)
        print("\n生成的文件位置:")
        print("  dist/gd-law-crawler.exe")
        print("\n提示:")
        print("  - 首次运行会自动创建 config.json 配置文件")
        print("  - 可以将 dist/gd-law-crawler.exe 复制到任何位置使用")
        print("  - 建议将 exe 和 config.json.example 放在同一目录")
        
    except Exception as e:
        print(f"\n打包失败: {e}")
        print("\n请确保已安装 PyInstaller:")
        print("  pip install pyinstaller")
        sys.exit(1)


if __name__ == "__main__":
    build_exe()

