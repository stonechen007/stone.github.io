#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票筛选工具 - 增强版（可调参数）
支持自定义筛选条件
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import argparse


class StockFilter:
    """股票筛选器"""
    
    def __init__(self, days=3, volume_growth=15, max_scan=None):
        """
        初始化
        
        参数:
            days: 连续上涨天数（默认3天）
            volume_growth: 成交量增长阈值（默认15%）
            max_scan: 最多扫描股票数量（None表示全部）
        """
        self.days = days
        self.volume_growth = volume_growth
        self.max_scan = max_scan
        self.qualified_stocks = []
        
    def get_stock_list(self):
        """获取股票列表"""
        try:
            print("正在获取A股股票列表...")
            stock_info = ak.stock_info_a_code_name()
            print(f"✓ 获取到 {len(stock_info)} 只股票")
            return stock_info
        except Exception as e:
            print(f"❌ 获取股票列表失败: {e}")
            return None
    
    def get_stock_data(self, stock_code):
        """获取股票数据"""
        try:
            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")
            if df is None or df.empty:
                return None
            
            # 需要days+1天的数据（用于计算第一天的成交量增长）
            df_recent = df.tail(self.days + 1).copy()
            
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
        except:
            return None
    
    def check_conditions(self, df):
        """检查是否符合条件"""
        if df is None or len(df) < self.days + 1:
            return False, None
        
        recent_data = df.tail(self.days + 1).reset_index(drop=True)
        
        # 检查价格连续上涨
        price_rises = []
        for i in range(1, self.days + 1):
            current_close = recent_data.loc[i, 'close']
            previous_close = recent_data.loc[i-1, 'close']
            price_rises.append(current_close > previous_close)
        
        # 检查成交量增长
        volume_grows = []
        volume_growth_rates = []
        for i in range(1, self.days + 1):
            current_volume = recent_data.loc[i, 'volume']
            previous_volume = recent_data.loc[i-1, 'volume']
            
            if previous_volume > 0:
                growth_rate = ((current_volume - previous_volume) / previous_volume) * 100
                volume_grows.append(growth_rate >= self.volume_growth)
                volume_growth_rates.append(growth_rate)
            else:
                volume_grows.append(False)
                volume_growth_rates.append(0)
        
        # 判断是否符合条件
        meets_conditions = all(price_rises) and all(volume_grows)
        
        if meets_conditions:
            info = {
                'dates': [str(d) for d in recent_data['date'].tail(self.days).tolist()],
                'closes': recent_data['close'].tail(self.days).tolist(),
                'volumes': recent_data['volume'].tail(self.days).tolist(),
                'volume_growth_rates': volume_growth_rates,
                'latest_close': recent_data.loc[self.days, 'close'],
                'total_change': sum([recent_data.loc[i, 'close'] - recent_data.loc[i-1, 'close'] 
                                    for i in range(1, self.days + 1)]),
                'total_change_pct': ((recent_data.loc[self.days, 'close'] - recent_data.loc[0, 'close']) 
                                    / recent_data.loc[0, 'close'] * 100)
            }
            return True, info
        
        return False, None
    
    def filter_stocks(self, stock_list):
        """筛选股票"""
        print("\n" + "=" * 100)
        print("🔍 开始筛选股票...")
        print("=" * 100)
        print(f"筛选条件：")
        print(f"  1. 最近 {self.days} 天连续上涨")
        print(f"  2. 成交量连续 {self.days} 天增长≥{self.volume_growth}%")
        print()
        
        total = len(stock_list) if self.max_scan is None else min(self.max_scan, len(stock_list))
        
        for idx, row in stock_list.head(total).iterrows():
            stock_code = row['code']
            stock_name = row['name']
            
            # 显示进度
            if (idx + 1) % 100 == 0:
                print(f"进度: {idx + 1}/{total} (已找到 {len(self.qualified_stocks)} 只)")
            
            df = self.get_stock_data(stock_code)
            if df is None:
                continue
            
            meets, info = self.check_conditions(df)
            
            if meets:
                self.qualified_stocks.append({
                    'code': stock_code,
                    'name': stock_name,
                    **info
                })
                print(f"✓ 找到: {stock_code} {stock_name} (涨幅{info['total_change_pct']:.2f}%)")
            
            time.sleep(0.1)
        
        print(f"\n✓ 筛选完成，共找到 {len(self.qualified_stocks)} 只符合条件的股票")
        return self.qualified_stocks
    
    def display_results(self):
        """显示结果"""
        if not self.qualified_stocks:
            print("\n❌ 未找到符合条件的股票")
            print("\n💡 建议：")
            print(f"  • 降低成交量增长要求（当前{self.volume_growth}%）")
            print(f"  • 减少连续天数要求（当前{self.days}天）")
            print(f"  • 扩大扫描范围")
            return
        
        print("\n" + "=" * 100)
        print(f"📊 符合条件的股票列表（共 {len(self.qualified_stocks)} 只）")
        print("=" * 100)
        print()
        
        # 按涨幅排序
        sorted_stocks = sorted(self.qualified_stocks, 
                              key=lambda x: x['total_change_pct'], 
                              reverse=True)
        
        for i, stock in enumerate(sorted_stocks, 1):
            print(f"【{i}】{stock['code']} - {stock['name']}")
            print(f"    最新价格: {stock['latest_close']:.2f} 元")
            print(f"    {self.days}日涨幅: {stock['total_change_pct']:.2f}% (累计涨 {stock['total_change']:.2f} 元)")
            
            # 显示日期和收盘价
            dates_str = ' → '.join(stock['dates'])
            closes_str = ' → '.join([f"{c:.2f}" for c in stock['closes']])
            print(f"    日期: {dates_str}")
            print(f"    收盘价: {closes_str}")
            
            # 显示成交量增长
            volume_str = ' → '.join([f"{v:.1f}%" for v in stock['volume_growth_rates']])
            print(f"    成交量增长: {volume_str}")
            print()
    
    def save_results(self, filename='qualified_stocks'):
        """保存结果"""
        if not self.qualified_stocks:
            return
        
        data = []
        for stock in self.qualified_stocks:
            row = {
                '股票代码': stock['code'],
                '股票名称': stock['name'],
                '最新价格': stock['latest_close'],
                f'{self.days}日涨幅(%)': round(stock['total_change_pct'], 2),
                '累计涨幅(元)': round(stock['total_change'], 2),
            }
            
            # 添加每日数据
            for i, (date, close, vol_growth) in enumerate(zip(
                stock['dates'], stock['closes'], stock['volume_growth_rates']), 1):
                row[f'第{i}天日期'] = date
                row[f'第{i}天收盘'] = close
                row[f'第{i}天成交量增长(%)'] = round(vol_growth, 2)
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # 保存CSV
        csv_file = f'{filename}.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"✓ 结果已保存到: {csv_file}")
        
        # 保存Excel
        try:
            excel_file = f'{filename}.xlsx'
            df.to_excel(excel_file, index=False)
            print(f"✓ 结果已保存到: {excel_file}")
        except Exception as e:
            print(f"⚠️  Excel保存失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='股票筛选工具 - 增强版')
    parser.add_argument('-d', '--days', type=int, default=3, 
                       help='连续上涨天数（默认3）')
    parser.add_argument('-v', '--volume', type=float, default=15.0,
                       help='成交量增长阈值百分比（默认15）')
    parser.add_argument('-n', '--number', type=int, default=None,
                       help='扫描股票数量（默认全部）')
    parser.add_argument('-o', '--output', type=str, default='qualified_stocks',
                       help='输出文件名（默认qualified_stocks）')
    
    args = parser.parse_args()
    
    print()
    print("=" * 100)
    print("📈 股票筛选工具 - 增强版（可调参数）")
    print("=" * 100)
    print()
    print("当前设置:")
    print(f"  • 连续上涨天数: {args.days} 天")
    print(f"  • 成交量增长阈值: {args.volume}%")
    print(f"  • 扫描数量: {'全部' if args.number is None else args.number}")
    print(f"  • 输出文件: {args.output}.csv / {args.output}.xlsx")
    print()
    
    # 创建筛选器
    filter = StockFilter(
        days=args.days,
        volume_growth=args.volume,
        max_scan=args.number
    )
    
    # 获取股票列表
    stock_list = filter.get_stock_list()
    if stock_list is None:
        return
    
    # 如果没有指定扫描数量，询问用户
    if args.number is None:
        print("⚠️  未指定扫描数量，将扫描全部股票（可能需要很长时间）")
        try:
            choice = input("继续吗？[y/n] 或输入数量（如500）: ").strip().lower()
            if choice == 'n':
                print("已取消")
                return
            elif choice == 'y':
                pass
            else:
                try:
                    filter.max_scan = int(choice)
                    print(f"✓ 将扫描前 {filter.max_scan} 只股票")
                except:
                    print("输入无效，扫描前50只作为测试")
                    filter.max_scan = 50
        except:
            print("使用默认值：扫描前50只")
            filter.max_scan = 50
    
    # 筛选股票
    filter.filter_stocks(stock_list)
    
    # 显示结果
    filter.display_results()
    
    # 保存结果
    if filter.qualified_stocks:
        filter.save_results(args.output)
    
    print("\n" + "=" * 100)
    print("✅ 程序执行完成！")
    print("=" * 100)
    print()


if __name__ == "__main__":
    main()

