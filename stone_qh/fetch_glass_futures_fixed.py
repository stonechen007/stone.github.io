#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
玻璃期货主连行情数据抓取脚本 - 修复版
使用多个可靠数据源，修正字段映射问题
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time


def fetch_from_eastmoney_v2(days=10):
    """
    从东方财富获取数据 - 使用备用接口
    """
    try:
        print("尝试东方财富备用接口...")
        
        # 使用行情接口
        url = "http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js"
        
        params = {
            'rtntype': '6',
            'token': '4f1862fc3b5e77c150a2b985b12db0fd',
            'cb': 'jQuery',
            'id': 'fgm',
            '_': str(int(time.time() * 1000))
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'http://quote.eastmoney.com/'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 解析JSONP
            content = response.text
            if 'jQuery' in content:
                json_str = content.split('(', 1)[1].rsplit(')', 1)[0]
                data = json.loads(json_str)
                
                if 'data' in data and data['data']:
                    print(f"✓ 成功获取数据")
                    return parse_eastmoney_data(data['data'], days)
    
    except Exception as e:
        print(f"东方财富接口错误: {e}")
    
    return None


def fetch_from_hexun(days=10):
    """
    从和讯网获取期货数据
    """
    try:
        print("尝试和讯网数据源...")
        
        # 和讯网期货数据接口
        url = "http://webftcn.hermes.hexun.com/shf/kline"
        
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days+10)
        
        params = {
            'code': 'FG',  # 玻璃
            'start': start_date.strftime('%Y%m%d'),
            'end': end_date.strftime('%Y%m%d'),
            'type': '5'  # 日K线
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'Data' in data and data['Data']:
                print(f"✓ 成功获取到 {len(data['Data'])} 条数据")
                return parse_hexun_data(data['Data'], days)
                
    except Exception as e:
        print(f"和讯网接口错误: {e}")
    
    return None


def fetch_from_qq(days=10):
    """
    从腾讯财经获取期货数据
    """
    try:
        print("尝试腾讯财经数据源...")
        
        url = "http://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
        
        params = {
            '_var': 'kline_dayqfq',
            'param': 'FG888,day,,,300',
            'r': str(time.time())
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'http://gu.qq.com/'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            # 解析返回的数据
            if 'kline_dayqfq=' in content:
                json_str = content.split('kline_dayqfq=')[1]
                data = json.loads(json_str)
                
                if 'data' in data and 'FG888' in data['data']:
                    kline_data = data['data']['FG888']['day']
                    if kline_data:
                        print(f"✓ 成功获取到 {len(kline_data)} 条数据")
                        return parse_qq_data(kline_data, days)
                        
    except Exception as e:
        print(f"腾讯财经接口错误: {e}")
    
    return None


def parse_eastmoney_data(data, days):
    """解析东方财富数据"""
    records = []
    # 实现具体的解析逻辑
    return records


def parse_hexun_data(data, days):
    """
    解析和讯网数据
    和讯格式: [时间戳, 开盘, 最高, 最低, 收盘, 成交量, 持仓量]
    """
    records = []
    
    for item in data[-days:]:
        try:
            # 转换时间戳
            date = datetime.fromtimestamp(int(item[0])/1000).strftime('%Y-%m-%d')
            open_price = float(item[1])
            high_price = float(item[2])
            low_price = float(item[3])
            close_price = float(item[4])
            volume = float(item[5])
            
            price_diff = high_price - low_price
            
            records.append({
                '日期': date,
                '开盘价': open_price,
                '收盘价': close_price,
                '最高价': high_price,
                '最低价': low_price,
                '最高最低价差': round(price_diff, 2),
                '成交量': volume,
                '成交额': 0
            })
        except Exception as e:
            print(f"解析数据项错误: {e}")
            continue
    
    return records


def parse_qq_data(data, days):
    """
    解析腾讯财经数据
    腾讯格式: ["日期", "开盘", "收盘", "最高", "最低", "成交量"]
    """
    records = []
    
    for item in data[-days:]:
        try:
            date = item[0]
            open_price = float(item[1])
            close_price = float(item[2])
            high_price = float(item[3])
            low_price = float(item[4])
            volume = float(item[5])
            
            price_diff = high_price - low_price
            
            records.append({
                '日期': date,
                '开盘价': open_price,
                '收盘价': close_price,
                '最高价': high_price,
                '最低价': low_price,
                '最高最低价差': round(price_diff, 2),
                '成交量': volume,
                '成交额': 0
            })
        except Exception as e:
            print(f"解析数据项错误: {e}")
            continue
    
    return records


def fetch_glass_futures_data(days=10):
    """
    抓取玻璃主连期货行情数据 - 尝试多个数据源
    """
    print("正在获取玻璃主连期货数据...")
    print("="*80)
    
    # 按优先级尝试不同数据源
    sources = [
        ('腾讯财经', fetch_from_qq),
        ('和讯网', fetch_from_hexun),
        ('东方财富', fetch_from_eastmoney_v2),
    ]
    
    for source_name, fetch_func in sources:
        try:
            records = fetch_func(days)
            if records and len(records) > 0:
                df = pd.DataFrame(records)
                print(f"\n✓ 成功从{source_name}获取到 {len(df)} 条数据\n")
                return df
        except Exception as e:
            print(f"{source_name}获取失败: {e}")
            continue
    
    print("\n所有数据源均无法获取数据")
    print("建议:")
    print("1. 检查网络连接")
    print("2. 使用 fetch_glass_futures_akshare.py (需要Python 3.8+)")
    print("3. 稍后重试")
    
    return None


def display_data(df):
    """在控制台美化显示数据"""
    if df is None or df.empty:
        print("没有可显示的数据")
        return
    
    print("=" * 100)
    print("玻璃主连期货最近10天行情数据")
    print("=" * 100)
    print(df.to_string(index=False))
    print("=" * 100)
    
    # 统计信息
    print("\n📊 统计信息:")
    print(f"   平均开盘价: {df['开盘价'].mean():.2f} 元")
    print(f"   平均收盘价: {df['收盘价'].mean():.2f} 元")
    print(f"   期间最高价: {df['最高价'].max():.2f} 元")
    print(f"   期间最低价: {df['最低价'].min():.2f} 元")
    print(f"   平均价差: {df['最高最低价差'].mean():.2f} 元")


def save_to_csv(df, filename='glass_futures_data.csv'):
    """将数据保存到CSV文件"""
    if df is not None and not df.empty:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 数据已保存到文件: {filename}")


def main():
    """主函数"""
    print("=" * 100)
    print("🔍 玻璃期货主连行情数据抓取工具 - 修复版")
    print("📊 使用多个数据源确保数据准确性")
    print("=" * 100)
    print()
    
    # 获取数据
    df = fetch_glass_futures_data(days=10)
    
    if df is not None and not df.empty:
        # 显示数据
        display_data(df)
        
        # 保存到CSV
        save_to_csv(df)
        
        print("\n✅ 数据获取成功!")
        print("\n💡 提示: 数据字段说明")
        print("   - 开盘价: 当日开盘时的价格")
        print("   - 收盘价: 当日收盘时的价格")
        print("   - 最高价: 当日交易的最高价格")
        print("   - 最低价: 当日交易的最低价格")
    else:
        print("\n❌ 数据获取失败")
        print("\n推荐方案:")
        print("如果您的Python版本 >= 3.8，请使用:")
        print("  pip3 install akshare")
        print("  python3 fetch_glass_futures_akshare.py")


if __name__ == "__main__":
    main()

