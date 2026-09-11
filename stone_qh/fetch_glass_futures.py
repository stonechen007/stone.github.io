#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
玻璃期货主连行情数据抓取脚本
从东方财富网抓取最近10天的玻璃主连期货行情数据
"""

import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import time


def fetch_glass_futures_data(days=10):
    """
    抓取玻璃主连期货行情数据
    
    参数:
        days: 获取最近多少天的数据，默认10天
    
    返回:
        DataFrame: 包含日期、开盘价、收盘价、最高价、最低价、价差等信息
    """
    
    # 东方财富期货数据API
    # FGM代表玻璃主连
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    
    # 计算需要的数据条数（多取一些以防万一）
    count = days + 5
    
    params = {
        'secid': '113.fgm',  # 玻璃主连的代码（尝试小写）
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
        'klt': '101',  # 101代表日K线
        'fqt': '0',    # 不复权
        'beg': '0',    # 开始日期，0表示最早
        'end': '20500101',  # 结束日期
        'lmt': count,  # 获取的数据条数
        'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://quote.eastmoney.com/'
    }
    
    try:
        print("正在获取玻璃主连期货数据...")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # 打印响应以便调试
        print(f"API响应状态: {response.status_code}")
        
        if 'data' not in data or data['data'] is None:
            print(f"未能获取到数据，响应内容: {data}")
            # 尝试备用方案
            return fetch_glass_futures_backup(days)
        
        klines = data['data']['klines']
        
        if not klines:
            print("返回的K线数据为空")
            return fetch_glass_futures_backup(days)
        
        # 解析K线数据
        records = []
        for kline in klines[-days:]:  # 只取最近days天的数据
            parts = kline.split(',')
            date = parts[0]
            open_price = float(parts[1])
            close_price = float(parts[2])
            high_price = float(parts[3])
            low_price = float(parts[4])
            volume = float(parts[5])
            amount = float(parts[6])
            
            # 计算价差
            price_diff = high_price - low_price
            
            records.append({
                '日期': date,
                '开盘价': open_price,
                '收盘价': close_price,
                '最高价': high_price,
                '最低价': low_price,
                '最高最低价差': round(price_diff, 2),
                '成交量': volume,
                '成交额': amount
            })
        
        df = pd.DataFrame(records)
        return df
        
    except requests.RequestException as e:
        print(f"网络请求错误: {e}")
        return fetch_glass_futures_backup(days)
    except (KeyError, IndexError, ValueError) as e:
        print(f"数据解析错误: {e}")
        return fetch_glass_futures_backup(days)


def fetch_glass_futures_backup(days=10):
    """
    备用数据获取方案：从新浪财经API获取
    
    参数:
        days: 获取最近多少天的数据，默认10天
    
    返回:
        DataFrame: 包含日期、开盘价、收盘价、最高价、最低价、价差等信息
    """
    try:
        print("\n尝试使用备用数据源（新浪财经）...")
        
        # 新浪财经期货数据接口
        # FG0代表玻璃主连
        url = "https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var%20_FG0=/GlobalFuturesService.getGlobalFuturesDailyKLine"
        
        params = {
            'symbol': 'FG0',  # 玻璃主连
            '_': str(int(time.time() * 1000))
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://finance.sina.com.cn/'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析JSONP响应
        content = response.text
        # 移除JSONP包装
        json_str = content.split('=(')[1].rsplit(');', 1)[0]
        data = json.loads(json_str)
        
        if not data:
            print("备用数据源也无法获取数据")
            return None
        
        # 解析数据
        records = []
        for item in data[-days:]:  # 只取最近days天的数据
            date = item[0]
            open_price = float(item[1])
            high_price = float(item[2])
            low_price = float(item[3])
            close_price = float(item[4])
            volume = float(item[5]) if len(item) > 5 else 0
            
            # 计算价差
            price_diff = high_price - low_price
            
            records.append({
                '日期': date,
                '开盘价': open_price,
                '收盘价': close_price,
                '最高价': high_price,
                '最低价': low_price,
                '最高最低价差': round(price_diff, 2),
                '成交量': volume,
                '成交额': 0  # 新浪接口可能不提供成交额
            })
        
        df = pd.DataFrame(records)
        print("✓ 成功从备用数据源获取数据")
        return df
        
    except Exception as e:
        print(f"备用数据源获取失败: {e}")
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


def display_data(df):
    """
    在控制台美化显示数据
    
    参数:
        df: DataFrame数据
    """
    if df is not None and not df.empty:
        print("\n" + "="*80)
        print("玻璃主连期货最近10天行情数据")
        print("="*80)
        print(df.to_string(index=False))
        print("="*80)
        
        # 统计信息
        print("\n统计信息:")
        print(f"平均开盘价: {df['开盘价'].mean():.2f}")
        print(f"平均收盘价: {df['收盘价'].mean():.2f}")
        print(f"最高价格: {df['最高价'].max():.2f}")
        print(f"最低价格: {df['最低价'].min():.2f}")
        print(f"平均价差: {df['最高最低价差'].mean():.2f}")
        print(f"最大价差: {df['最高最低价差'].max():.2f} (日期: {df.loc[df['最高最低价差'].idxmax(), '日期']})")
    else:
        print("没有可显示的数据")


def main():
    """
    主函数
    """
    print("="*80)
    print("玻璃期货主连行情数据抓取工具")
    print("数据来源: 东方财富网")
    print("="*80)
    
    # 获取数据
    df = fetch_glass_futures_data(days=10)
    
    if df is not None:
        # 显示数据
        display_data(df)
        
        # 保存到CSV
        save_to_csv(df)
        
        print("\n✓ 数据获取成功!")
    else:
        print("\n✗ 数据获取失败，请检查网络连接或稍后重试")


if __name__ == "__main__":
    main()

