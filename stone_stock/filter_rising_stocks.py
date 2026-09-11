#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票筛选工具
筛选条件：
1. 最近三天连续上涨
2. 成交量连续三天增长15%以上
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import time


def get_stock_list():
    """获取A股股票列表"""
    try:
        print("正在获取A股股票列表...")
        # 获取沪深A股列表
        stock_info = ak.stock_info_a_code_name()
        print(f"✓ 获取到 {len(stock_info)} 只股票")
        return stock_info
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        return None


def get_stock_daily_data(stock_code, days=5):
    """
    获取单只股票的日线数据
    
    参数:
        stock_code: 股票代码（如 '000001'）
        days: 获取最近多少天的数据
    
    返回:
        DataFrame: 股票日线数据
    """
    try:
        # 获取股票历史数据
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")
        
        if df is None or df.empty:
            return None
        
        # 只取最近days天的数据
        df_recent = df.tail(days).copy()
        
        # 重命名列
        df_recent = df_recent.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
            '涨跌幅': 'change_pct',
            '涨跌额': 'change'
        })
        
        return df_recent
        
    except Exception as e:
        return None


def check_conditions(df):
    """
    检查股票是否符合条件
    
    条件：
    1. 最近三天连续上涨（收盘价）
    2. 成交量连续三天增长15%以上
    
    参数:
        df: 股票日线数据（至少4天，用于计算成交量增长）
    
    返回:
        bool: 是否符合条件
        dict: 详细信息
    """
    if df is None or len(df) < 4:
        return False, None
    
    # 取最近4天的数据（需要计算前一天的成交量增长）
    recent_data = df.tail(4).reset_index(drop=True)
    
    # 检查最近3天是否连续上涨
    price_rises = []
    for i in range(1, 4):  # 最近3天
        current_close = recent_data.loc[i, 'close']
        previous_close = recent_data.loc[i-1, 'close']
        price_rises.append(current_close > previous_close)
    
    # 检查成交量是否连续增长15%以上
    volume_grows = []
    volume_growth_rates = []
    for i in range(1, 4):  # 最近3天
        current_volume = recent_data.loc[i, 'volume']
        previous_volume = recent_data.loc[i-1, 'volume']
        
        if previous_volume > 0:
            growth_rate = ((current_volume - previous_volume) / previous_volume) * 100
            volume_grows.append(growth_rate >= 15)
            volume_growth_rates.append(growth_rate)
        else:
            volume_grows.append(False)
            volume_growth_rates.append(0)
    
    # 判断是否符合条件
    meets_conditions = all(price_rises) and all(volume_grows)
    
    if meets_conditions:
        info = {
            'dates': [str(d) for d in recent_data['date'].tail(3).tolist()],
            'closes': recent_data['close'].tail(3).tolist(),
            'volumes': recent_data['volume'].tail(3).tolist(),
            'volume_growth_rates': volume_growth_rates,
            'latest_close': recent_data.loc[3, 'close'],
            'total_change': sum([recent_data.loc[i, 'close'] - recent_data.loc[i-1, 'close'] 
                                for i in range(1, 4)]),
            'total_change_pct': ((recent_data.loc[3, 'close'] - recent_data.loc[0, 'close']) 
                                / recent_data.loc[0, 'close'] * 100)
        }
        return True, info
    
    return False, None


def filter_stocks(stock_list, max_stocks=None):
    """
    筛选符合条件的股票
    
    参数:
        stock_list: 股票列表DataFrame
        max_stocks: 最多检查多少只股票（None表示全部）
    
    返回:
        list: 符合条件的股票列表
    """
    print("\n" + "=" * 100)
    print("🔍 开始筛选股票...")
    print("=" * 100)
    print(f"筛选条件：")
    print(f"  1. 最近三天连续上涨")
    print(f"  2. 成交量连续三天增长≥15%")
    print()
    
    qualified_stocks = []
    total = len(stock_list) if max_stocks is None else min(max_stocks, len(stock_list))
    
    for idx, row in stock_list.head(total).iterrows():
        stock_code = row['code']
        stock_name = row['name']
        
        # 显示进度
        if (idx + 1) % 100 == 0:
            print(f"进度: {idx + 1}/{total} (已找到 {len(qualified_stocks)} 只符合条件的股票)")
        
        # 获取股票数据
        df = get_stock_daily_data(stock_code, days=5)
        
        if df is None:
            continue
        
        # 检查是否符合条件
        meets, info = check_conditions(df)
        
        if meets:
            qualified_stocks.append({
                'code': stock_code,
                'name': stock_name,
                **info
            })
            print(f"✓ 找到: {stock_code} {stock_name}")
        
        # 延迟，避免请求过快
        time.sleep(0.1)
    
    print(f"\n✓ 筛选完成，共找到 {len(qualified_stocks)} 只符合条件的股票")
    return qualified_stocks


def display_results(stocks):
    """显示筛选结果"""
    if not stocks:
        print("\n❌ 未找到符合条件的股票")
        return
    
    print("\n" + "=" * 100)
    print(f"📊 符合条件的股票列表（共 {len(stocks)} 只）")
    print("=" * 100)
    print()
    
    for i, stock in enumerate(stocks, 1):
        print(f"【{i}】{stock['code']} - {stock['name']}")
        print(f"    最新价格: {stock['latest_close']:.2f} 元")
        print(f"    三日涨幅: {stock['total_change_pct']:.2f}% (累计涨 {stock['total_change']:.2f} 元)")
        print(f"    日期: {stock['dates'][-3]} → {stock['dates'][-2]} → {stock['dates'][-1]}")
        print(f"    收盘价: {stock['closes'][-3]:.2f} → {stock['closes'][-2]:.2f} → {stock['closes'][-1]:.2f}")
        print(f"    成交量增长: {stock['volume_growth_rates'][0]:.1f}% → {stock['volume_growth_rates'][1]:.1f}% → {stock['volume_growth_rates'][2]:.1f}%")
        print()


def save_results(stocks, filename='qualified_stocks.csv'):
    """保存结果到文件"""
    if not stocks:
        return
    
    # 整理数据
    data = []
    for stock in stocks:
        data.append({
            '股票代码': stock['code'],
            '股票名称': stock['name'],
            '最新价格': stock['latest_close'],
            '三日涨幅(%)': round(stock['total_change_pct'], 2),
            '累计涨幅(元)': round(stock['total_change'], 2),
            '第一天日期': stock['dates'][-3],
            '第二天日期': stock['dates'][-2],
            '第三天日期': stock['dates'][-1],
            '第一天收盘': stock['closes'][-3],
            '第二天收盘': stock['closes'][-2],
            '第三天收盘': stock['closes'][-1],
            '第一天成交量增长(%)': round(stock['volume_growth_rates'][0], 2),
            '第二天成交量增长(%)': round(stock['volume_growth_rates'][1], 2),
            '第三天成交量增长(%)': round(stock['volume_growth_rates'][2], 2),
        })
    
    df = pd.DataFrame(data)
    
    # 保存CSV
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✓ 结果已保存到: {filename}")
    
    # 保存Excel
    try:
        excel_filename = filename.replace('.csv', '.xlsx')
        df.to_excel(excel_filename, index=False)
        print(f"✓ 结果已保存到: {excel_filename}")
    except Exception as e:
        print(f"⚠️  Excel保存失败: {e}")


def main():
    """主函数"""
    print()
    print("=" * 100)
    print("📈 股票筛选工具 - 连续上涨且成交量放大")
    print("=" * 100)
    print()
    print("筛选条件:")
    print("  ✓ 最近三天连续上涨")
    print("  ✓ 成交量连续三天增长≥15%")
    print()
    
    # 获取股票列表
    stock_list = get_stock_list()
    
    if stock_list is None:
        print("❌ 无法获取股票列表，程序退出")
        return
    
    print()
    print("⚠️  注意：完整扫描所有股票需要较长时间")
    print("建议先测试少量股票，确认脚本正常后再全量扫描")
    print()
    
    # 询问扫描数量
    try:
        choice = input("请选择扫描模式 [1=测试50只 / 2=扫描500只 / 3=全部股票]: ").strip()
        
        if choice == '1':
            max_stocks = 50
            print(f"\n✓ 将扫描前 {max_stocks} 只股票（测试模式）")
        elif choice == '2':
            max_stocks = 500
            print(f"\n✓ 将扫描前 {max_stocks} 只股票")
        elif choice == '3':
            max_stocks = None
            print(f"\n✓ 将扫描全部 {len(stock_list)} 只股票（这可能需要很长时间）")
        else:
            max_stocks = 50
            print(f"\n⚠️  输入无效，默认扫描前 {max_stocks} 只股票")
    except:
        max_stocks = 50
        print(f"\n⚠️  使用默认值，扫描前 {max_stocks} 只股票")
    
    # 筛选股票
    qualified_stocks = filter_stocks(stock_list, max_stocks=max_stocks)
    
    # 显示结果
    display_results(qualified_stocks)
    
    # 保存结果
    if qualified_stocks:
        save_results(qualified_stocks)
    
    print("\n" + "=" * 100)
    print("✅ 程序执行完成！")
    print("=" * 100)
    print()


if __name__ == "__main__":
    main()

