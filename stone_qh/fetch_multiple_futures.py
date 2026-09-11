#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多品种期货数据抓取工具
获取甲醇、尿素、纯碱的主连期货行情数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime


# 定义期货品种信息
FUTURES_INFO = {
    'MA0': {'name': '甲醇', 'unit': '元/吨'},
    'UR0': {'name': '尿素', 'unit': '元/吨'},
    'SA0': {'name': '纯碱', 'unit': '元/吨'},
}


def fetch_single_futures_data(symbol, days=10):
    """
    获取单个期货品种的数据
    
    参数:
        symbol: 期货代码，如 'MA0', 'UR0', 'SA0'
        days: 获取最近多少天的数据
    
    返回:
        DataFrame: 包含期货数据
    """
    try:
        name = FUTURES_INFO.get(symbol, {}).get('name', symbol)
        print(f"正在获取{name}({symbol})数据...")
        
        # 获取期货主连数据
        df = ak.futures_zh_daily_sina(symbol=symbol)
        
        if df is None or df.empty:
            print(f"❌ 未能获取到{name}数据")
            return None
        
        # 只取最近days天的数据
        df_recent = df.tail(days).copy()
        
        # 重命名列
        df_recent = df_recent.rename(columns={
            'date': '日期',
            'open': '开盘价',
            'close': '收盘价',
            'high': '最高价',
            'low': '最低价',
            'volume': '成交量',
            'hold': '持仓量'
        })
        
        # 计算最高最低价差
        df_recent['最高最低价差'] = (df_recent['最高价'] - df_recent['最低价']).round(2)
        
        # 添加品种信息
        df_recent.insert(0, '品种', name)
        
        # 选择需要的列
        columns = ['品种', '日期', '开盘价', '收盘价', '最高价', '最低价', '最高最低价差', '成交量']
        df_result = df_recent[columns].copy()
        
        # 重置索引
        df_result.reset_index(drop=True, inplace=True)
        
        print(f"✓ 成功获取{name}数据 ({len(df_result)}条)")
        return df_result
        
    except Exception as e:
        name = FUTURES_INFO.get(symbol, {}).get('name', symbol)
        print(f"❌ 获取{name}数据失败: {e}")
        return None


def fetch_multiple_futures_data(symbols=None, days=10):
    """
    获取多个期货品种的数据
    
    参数:
        symbols: 期货代码列表，默认获取所有配置的品种
        days: 获取最近多少天的数据
    
    返回:
        dict: {symbol: DataFrame}
    """
    if symbols is None:
        symbols = list(FUTURES_INFO.keys())
    
    results = {}
    
    for symbol in symbols:
        df = fetch_single_futures_data(symbol, days)
        if df is not None:
            results[symbol] = df
    
    return results


def display_data(data_dict):
    """
    在控制台显示多个品种的数据
    
    参数:
        data_dict: {symbol: DataFrame}
    """
    if not data_dict:
        print("没有可显示的数据")
        return
    
    for symbol, df in data_dict.items():
        name = FUTURES_INFO.get(symbol, {}).get('name', symbol)
        unit = FUTURES_INFO.get(symbol, {}).get('unit', '元')
        
        print("\n" + "=" * 100)
        print(f"{name}主连期货最近10天行情数据 ({symbol})")
        print("=" * 100)
        
        # 显示数据表格
        display_df = df.copy()
        display_df = display_df.drop('品种', axis=1)  # 不显示品种列
        print(display_df.to_string(index=False))
        print("=" * 100)
        
        # 统计信息
        print(f"\n📊 {name}统计信息:")
        print(f"   平均开盘价: {df['开盘价'].mean():.2f} {unit}")
        print(f"   平均收盘价: {df['收盘价'].mean():.2f} {unit}")
        print(f"   期间最高价: {df['最高价'].max():.2f} {unit} (日期: {df.loc[df['最高价'].idxmax(), '日期']})")
        print(f"   期间最低价: {df['最低价'].min():.2f} {unit} (日期: {df.loc[df['最低价'].idxmin(), '日期']})")
        print(f"   平均价差: {df['最高最低价差'].mean():.2f} {unit}")
        print(f"   最大价差: {df['最高最低价差'].max():.2f} {unit} (日期: {df.loc[df['最高最低价差'].idxmax(), '日期']})")
        
        # 涨跌统计
        df_copy = df.copy()
        df_copy['涨跌'] = df_copy['收盘价'] - df_copy['开盘价']
        up_days = (df_copy['涨跌'] > 0).sum()
        down_days = (df_copy['涨跌'] < 0).sum()
        
        if len(df) >= 2:
            first_close = df.iloc[0]['收盘价']
            last_close = df.iloc[-1]['收盘价']
            period_change = last_close - first_close
            period_change_pct = (period_change / first_close) * 100
            
            print(f"\n📈 涨跌统计:")
            print(f"   上涨天数: {up_days} 天")
            print(f"   下跌天数: {down_days} 天")
            print(f"   区间涨跌: {period_change:+.2f} {unit} ({period_change_pct:+.2f}%)")


def save_to_csv(data_dict, prefix='futures_data'):
    """
    保存数据到CSV文件
    
    参数:
        data_dict: {symbol: DataFrame}
        prefix: 文件名前缀
    """
    if not data_dict:
        return
    
    print("\n" + "=" * 100)
    print("💾 保存数据到文件")
    print("=" * 100)
    
    # 为每个品种单独保存
    for symbol, df in data_dict.items():
        name = FUTURES_INFO.get(symbol, {}).get('name', symbol)
        filename = f"{prefix}_{symbol}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✓ {name}数据已保存到: {filename}")
    
    # 合并所有数据到一个文件
    if len(data_dict) > 1:
        combined_df = pd.concat(data_dict.values(), ignore_index=True)
        combined_filename = f"{prefix}_combined.csv"
        combined_df.to_csv(combined_filename, index=False, encoding='utf-8-sig')
        print(f"✓ 合并数据已保存到: {combined_filename}")
    
    # 尝试保存为Excel
    try:
        excel_filename = f"{prefix}_combined.xlsx"
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            for symbol, df in data_dict.items():
                name = FUTURES_INFO.get(symbol, {}).get('name', symbol)
                df.to_excel(writer, sheet_name=name, index=False)
        print(f"✓ Excel文件已保存到: {excel_filename}")
    except Exception as e:
        print(f"⚠️  Excel保存失败: {e}")


def main():
    """主函数"""
    print("=" * 100)
    print("🔍 多品种期货数据抓取工具")
    print("📊 数据来源: 新浪财经")
    print("=" * 100)
    print()
    
    # 显示要获取的品种
    print("📋 将获取以下期货品种数据:")
    for symbol, info in FUTURES_INFO.items():
        print(f"   • {info['name']} ({symbol})")
    print()
    
    # 获取数据
    data_dict = fetch_multiple_futures_data(days=10)
    
    if not data_dict:
        print("\n❌ 未能获取任何数据")
        return
    
    print(f"\n✓ 成功获取 {len(data_dict)} 个品种的数据\n")
    
    # 显示数据
    display_data(data_dict)
    
    # 保存数据
    save_to_csv(data_dict, prefix='futures_data')
    
    print("\n" + "=" * 100)
    print("✅ 数据获取完成！")
    print("=" * 100)
    print("\n💡 提示:")
    print("   - 每个品种的数据已单独保存")
    print("   - 合并数据保存在 futures_data_combined.csv")
    print("   - Excel文件包含所有品种（每个品种一个工作表）")
    print()


if __name__ == "__main__":
    main()

