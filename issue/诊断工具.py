#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源问题诊断工具
快速检查您的环境和数据源状态
"""

import sys
import subprocess


def check_python_version():
    """检查Python版本"""
    print("\n" + "="*80)
    print("1️⃣  检查Python版本")
    print("="*80)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"当前Python版本: {version_str}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python版本满足要求（>= 3.8）")
        print("💡 可以使用 fetch_glass_futures_akshare.py")
        return True
    elif version.major >= 3 and version.minor >= 7:
        print("⚠️  Python版本为3.7，不支持AkShare")
        print("💡 建议升级到Python 3.8+")
        print("   macOS: brew install python@3.11")
        return False
    else:
        print("❌ Python版本过低")
        print("💡 必须升级到Python 3.8+")
        return False


def check_packages():
    """检查已安装的包"""
    print("\n" + "="*80)
    print("2️⃣  检查已安装的Python包")
    print("="*80)
    
    required_packages = {
        'requests': 'API版本需要',
        'pandas': '所有版本需要',
        'akshare': 'AkShare版本需要（推荐）',
        'selenium': 'Selenium版本需要',
        'openpyxl': 'Excel导出需要'
    }
    
    installed = {}
    
    for package, desc in required_packages.items():
        try:
            __import__(package)
            installed[package] = True
            print(f"✅ {package:15} - 已安装 ({desc})")
        except ImportError:
            installed[package] = False
            print(f"❌ {package:15} - 未安装 ({desc})")
    
    return installed


def check_available_scripts(has_akshare, has_requests, python_ok):
    """检查可用的脚本"""
    print("\n" + "="*80)
    print("3️⃣  可用脚本检查")
    print("="*80)
    
    scripts = []
    
    # 演示版本 - 始终可用
    print("✅ fetch_glass_futures_demo.py")
    print("   - 无需任何依赖")
    print("   - 生成模拟数据（用于演示）")
    print("   - 推荐指数: ⭐⭐⭐")
    scripts.append('demo')
    
    # AkShare版本
    if python_ok and has_akshare:
        print("\n✅ fetch_glass_futures_akshare.py （推荐）")
        print("   - 需要Python 3.8+")
        print("   - 需要akshare包")
        print("   - 获取真实数据")
        print("   - 推荐指数: ⭐⭐⭐⭐⭐")
        scripts.append('akshare')
    else:
        print("\n❌ fetch_glass_futures_akshare.py")
        if not python_ok:
            print("   - ⚠️  需要Python 3.8+（当前版本不满足）")
        if not has_akshare:
            print("   - ⚠️  需要安装: pip3 install akshare")
    
    # API版本
    if has_requests:
        print("\n⚠️  fetch_glass_futures.py")
        print("   - 需要requests包")
        print("   - 支持Python 3.7+")
        print("   - ⚠️  当前数据源不可用")
        print("   - 推荐指数: ⭐⭐")
    else:
        print("\n❌ fetch_glass_futures.py")
        print("   - ⚠️  需要安装: pip3 install requests pandas")
    
    return scripts


def provide_recommendations(python_ok, installed):
    """提供推荐方案"""
    print("\n" + "="*80)
    print("4️⃣  推荐操作方案")
    print("="*80)
    
    if python_ok and installed.get('akshare'):
        print("\n✅ 您的环境配置完善！")
        print("\n推荐操作：")
        print("   python3 fetch_glass_futures_akshare.py")
        print("\n💡 这将获取真实的玻璃期货数据")
        
    elif python_ok and not installed.get('akshare'):
        print("\n⚠️  Python版本满足要求，但缺少AkShare")
        print("\n推荐操作：")
        print("   # 1. 安装AkShare")
        print("   pip3 install akshare pandas openpyxl")
        print("\n   # 2. 运行脚本")
        print("   python3 fetch_glass_futures_akshare.py")
        
    else:
        print("\n⚠️  Python版本过低，需要升级")
        print("\n推荐操作：")
        print("   # 1. 升级Python（macOS）")
        print("   brew install python@3.11")
        print("\n   # 2. 安装AkShare")
        print("   pip3 install akshare pandas openpyxl")
        print("\n   # 3. 运行脚本")
        print("   python3 fetch_glass_futures_akshare.py")
    
    print("\n" + "="*80)
    print("5️⃣  数据源状态说明")
    print("="*80)
    print("\n❌ 免费API数据源当前不可用：")
    print("   - 东方财富API：无法访问")
    print("   - 新浪财经API：被屏蔽")
    print("   - 腾讯财经API：无响应")
    print("\n✅ 可用数据源：")
    print("   - AkShare：稳定可靠（推荐）⭐⭐⭐⭐⭐")
    print("   - 演示数据：模拟数据（仅用于测试）")


def check_demo_vs_real():
    """说明演示版本和真实数据的区别"""
    print("\n" + "="*80)
    print("6️⃣  重要提示：演示数据 vs 真实数据")
    print("="*80)
    
    print("\n⚠️  如果您看到开盘价、收盘价\"不正确\"，请确认：")
    print("\n1. 您运行的是哪个脚本？")
    print("   - fetch_glass_futures_demo.py → 模拟数据（不准确）❌")
    print("   - fetch_glass_futures_akshare.py → 真实数据（准确）✅")
    print("\n2. 演示版本的特点：")
    print("   - 数据是随机生成的")
    print("   - 仅用于展示脚本功能")
    print("   - 不反映真实市场行情")
    print("\n3. 获取真实数据请使用：")
    print("   python3 fetch_glass_futures_akshare.py")


def main():
    """主函数"""
    print("="*80)
    print("🔍 玻璃期货数据抓取 - 环境诊断工具")
    print("="*80)
    print("本工具将帮助您诊断环境配置和数据源问题")
    
    # 检查Python版本
    python_ok = check_python_version()
    
    # 检查已安装的包
    installed = check_packages()
    
    # 检查可用脚本
    available_scripts = check_available_scripts(
        installed.get('akshare', False),
        installed.get('requests', False),
        python_ok
    )
    
    # 提供推荐方案
    provide_recommendations(python_ok, installed)
    
    # 说明演示数据和真实数据的区别
    check_demo_vs_real()
    
    print("\n" + "="*80)
    print("✅ 诊断完成！")
    print("="*80)
    print("\n💡 快速开始：")
    print("   1. 先运行演示版了解功能: python3 fetch_glass_futures_demo.py")
    print("   2. 配置环境后获取真实数据: python3 fetch_glass_futures_akshare.py")
    print("\n📖 详细说明请查看：")
    print("   - 使用说明.md")
    print("   - 数据源问题说明.md")
    print("="*80)


if __name__ == "__main__":
    main()

