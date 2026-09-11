#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
玻璃期货主连行情数据抓取脚本（AkShare版本）
使用AkShare库获取最近10天的玻璃主连期货行情数据
这是最简单和推荐的方法
"""

try:
    import akshare as ak
except ImportError:
    print("未安装akshare库，请运行以下命令安装:")
    print("pip install akshare")
    exit(1)

import pandas as pd
from datetime import datetime, timedelta


def fetch_glass_futures_data(days=10):
    """
    使用AkShare抓取玻璃主连期货行情数据
    
    参数:
        days: 获取最近多少天的数据，默认10天
    
    返回:
        DataFrame: 包含日期、开盘价、收盘价、最高价、最低价、价差等信息
    """
    
    try:
        print("正在使用AkShare获取玻璃主连期货数据...")
        
        # 获取期货主连数据
        # FG代表玻璃期货
        df = ak.futures_zh_daily_sina(symbol="FG0")
        
        if df is None or df.empty:
            print("未能获取到数据")
            return None
        
        print(f"成功获取到 {len(df)} 条历史数据")
        
        # 只取最近days天的数据
        df_recent = df.tail(days).copy()
        
        # 重命名列以匹配需求
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
        
        # 选择需要的列
        columns_to_keep = ['日期', '开盘价', '收盘价', '最高价', '最低价', '最高最低价差', '成交量']
        
        # 确保所有需要的列都存在
        existing_columns = [col for col in columns_to_keep if col in df_recent.columns]
        df_result = df_recent[existing_columns].copy()
        
        # 重置索引
        df_result.reset_index(drop=True, inplace=True)
        
        return df_result
        
    except Exception as e:
        print(f"数据获取失败: {e}")
        print("\n提示:")
        print("1. 确保已安装akshare库: pip install akshare")
        print("2. 确保网络连接正常")
        print("3. 如果仍然失败，可能是数据源暂时不可用，请稍后再试")
        return None


def fetch_all_futures_varieties():
    """
    获取所有期货品种列表
    """
    try:
        print("\n获取所有期货品种...")
        varieties = ak.futures_display_main_sina()
        print("\n可用的期货品种:")
        print(varieties.to_string())
        return varieties
    except Exception as e:
        print(f"获取期货品种列表失败: {e}")
        return None


def save_to_csv(df, filename='glass_futures_data.csv'):
    """
    将数据保存到CSV文件
    
    参数:
        df: DataFrame数据
        filename: 保存的文件名
    """
    if df is not None and not df.empty:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n数据已保存到文件: {filename}")


def save_to_excel(df, filename='glass_futures_data.xlsx'):
    """
    将数据保存到Excel文件
    
    参数:
        df: DataFrame数据
        filename: 保存的文件名
    """
    if df is not None and not df.empty:
        try:
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"数据已保存到Excel文件: {filename}")
        except Exception as e:
            print(f"保存Excel文件失败: {e}")
            print("提示: 安装openpyxl库以支持Excel: pip install openpyxl")


def display_data(df):
    """
    在控制台美化显示数据
    
    参数:
        df: DataFrame数据
    """
    if df is not None and not df.empty:
        print("\n" + "="*100)
        print("玻璃主连期货最近10天行情数据")
        print("="*100)
        
        # 设置pandas显示选项
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
        print(df.to_string(index=False))
        print("="*100)
        
        # 统计信息
        print("\n📊 统计信息:")
        print(f"   平均开盘价: {df['开盘价'].mean():.2f} 元")
        print(f"   平均收盘价: {df['收盘价'].mean():.2f} 元")
        print(f"   期间最高价: {df['最高价'].max():.2f} 元 (日期: {df.loc[df['最高价'].idxmax(), '日期']})")
        print(f"   期间最低价: {df['最低价'].min():.2f} 元 (日期: {df.loc[df['最低价'].idxmin(), '日期']})")
        print(f"   平均价差: {df['最高最低价差'].mean():.2f} 元")
        print(f"   最大价差: {df['最高最低价差'].max():.2f} 元 (日期: {df.loc[df['最高最低价差'].idxmax(), '日期']})")
        print(f"   最小价差: {df['最高最低价差'].min():.2f} 元 (日期: {df.loc[df['最高最低价差'].idxmin(), '日期']})")
        
        if '成交量' in df.columns:
            print(f"   平均成交量: {df['成交量'].mean():.0f}")
            print(f"   总成交量: {df['成交量'].sum():.0f}")
        
        # 涨跌统计
        df_copy = df.copy()
        df_copy['涨跌'] = df_copy['收盘价'] - df_copy['开盘价']
        up_days = (df_copy['涨跌'] > 0).sum()
        down_days = (df_copy['涨跌'] < 0).sum()
        flat_days = (df_copy['涨跌'] == 0).sum()
        
        print(f"\n📈 涨跌统计:")
        print(f"   上涨天数: {up_days} 天")
        print(f"   下跌天数: {down_days} 天")
        print(f"   平盘天数: {flat_days} 天")
        
        if len(df) >= 2:
            first_close = df.iloc[0]['收盘价']
            last_close = df.iloc[-1]['收盘价']
            period_change = last_close - first_close
            period_change_pct = (period_change / first_close) * 100
            print(f"   区间涨跌: {period_change:+.2f} 元 ({period_change_pct:+.2f}%)")
    else:
        print("没有可显示的数据")


def main():
    """
    主函数
    """
    print("="*100)
    print("🔍 玻璃期货主连行情数据抓取工具 (AkShare版本)")
    print("📊 数据来源: 新浪财经")
    print("="*100)
    
    # 获取数据
    df = fetch_glass_futures_data(days=10)
    
    if df is not None and not df.empty:
        # 显示数据
        display_data(df)
        
        # 保存到CSV
        save_to_csv(df)
        
        # 尝试保存到Excel
        try:
            save_to_excel(df)
        except:
            pass
        
        print("\n✅ 数据获取成功!")
        print("\n💡 提示: 数据已保存，可以使用Excel或其他工具打开CSV文件查看")
    else:
        print("\n❌ 数据获取失败，请检查网络连接或稍后重试")
        print("\n可选操作:")
        print("1. 检查网络连接")
        print("2. 更新akshare库: pip install --upgrade akshare")
        print("3. 尝试使用其他版本的脚本")


if __name__ == "__main__":
    main()

