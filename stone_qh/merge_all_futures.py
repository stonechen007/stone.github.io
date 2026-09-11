#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并所有期货品种数据
将玻璃、甲醇、尿素、纯碱的数据合并成一个文件
"""

import pandas as pd
from datetime import datetime


def merge_all_futures():
    """合并所有期货品种数据"""
    print("=" * 100)
    print("🔄 合并所有期货品种数据")
    print("=" * 100)
    print()
    
    all_data = []
    
    # 1. 读取玻璃数据
    try:
        print("📊 读取玻璃数据...")
        glass_df = pd.read_csv('glass_futures_data.csv', encoding='utf-8-sig')
        # 添加品种列
        glass_df.insert(0, '品种', '玻璃')
        print(f"✓ 成功读取玻璃数据: {len(glass_df)} 条")
        all_data.append(glass_df)
    except Exception as e:
        print(f"⚠️  读取玻璃数据失败: {e}")
    
    # 2. 读取甲醇、尿素、纯碱数据
    try:
        print("📊 读取甲醇、尿素、纯碱数据...")
        other_df = pd.read_csv('futures_data_combined.csv', encoding='utf-8-sig')
        print(f"✓ 成功读取其他品种数据: {len(other_df)} 条")
        all_data.append(other_df)
    except Exception as e:
        print(f"⚠️  读取其他品种数据失败: {e}")
    
    if not all_data:
        print("❌ 没有找到任何数据文件")
        return None
    
    # 3. 合并所有数据
    print("\n🔗 合并数据...")
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # 按品种和日期排序
    combined_df = combined_df.sort_values(['品种', '日期']).reset_index(drop=True)
    
    print(f"✓ 合并完成，共 {len(combined_df)} 条数据")
    
    # 4. 统计信息
    print("\n" + "=" * 100)
    print("📊 合并数据统计")
    print("=" * 100)
    
    for variety in combined_df['品种'].unique():
        variety_df = combined_df[combined_df['品种'] == variety]
        count = len(variety_df)
        print(f"   • {variety}: {count} 条数据")
    
    print(f"\n   总计: {len(combined_df)} 条数据")
    
    return combined_df


def display_summary(df):
    """显示数据摘要"""
    print("\n" + "=" * 100)
    print("📈 各品种数据概览（最近10天）")
    print("=" * 100)
    
    for variety in df['品种'].unique():
        variety_df = df[df['品种'] == variety].tail(10)
        
        if len(variety_df) == 0:
            continue
        
        print(f"\n【{variety}】")
        print(f"   数据日期: {variety_df.iloc[0]['日期']} 至 {variety_df.iloc[-1]['日期']}")
        print(f"   价格区间: {variety_df['最低价'].min():.0f} - {variety_df['最高价'].max():.0f} 元")
        print(f"   平均收盘价: {variety_df['收盘价'].mean():.2f} 元")
        
        if len(variety_df) >= 2:
            first_close = variety_df.iloc[0]['收盘价']
            last_close = variety_df.iloc[-1]['收盘价']
            change = last_close - first_close
            change_pct = (change / first_close) * 100
            trend = "⬆️" if change > 0 else "⬇️" if change < 0 else "➡️"
            print(f"   区间涨跌: {change:+.2f} 元 ({change_pct:+.2f}%) {trend}")


def save_files(df, prefix='all_futures'):
    """保存合并后的数据"""
    print("\n" + "=" * 100)
    print("💾 保存合并数据")
    print("=" * 100)
    
    # 保存CSV
    csv_filename = f'{prefix}_combined.csv'
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"✓ CSV文件已保存: {csv_filename}")
    
    # 保存Excel - 所有数据在一个工作表
    try:
        excel_all_filename = f'{prefix}_combined.xlsx'
        df.to_excel(excel_all_filename, index=False, sheet_name='所有品种')
        print(f"✓ Excel文件已保存: {excel_all_filename}")
    except Exception as e:
        print(f"⚠️  Excel保存失败: {e}")
    
    # 保存Excel - 每个品种一个工作表
    try:
        excel_sheets_filename = f'{prefix}_by_variety.xlsx'
        with pd.ExcelWriter(excel_sheets_filename, engine='openpyxl') as writer:
            for variety in df['品种'].unique():
                variety_df = df[df['品种'] == variety].copy()
                # 移除品种列（因为工作表名已经说明了品种）
                variety_df_display = variety_df.drop('品种', axis=1)
                variety_df_display.to_excel(writer, sheet_name=variety, index=False)
        print(f"✓ Excel文件已保存（分工作表）: {excel_sheets_filename}")
    except Exception as e:
        print(f"⚠️  分工作表Excel保存失败: {e}")
    
    print()
    print("📂 生成的文件:")
    print(f"   • {csv_filename} - 所有品种合并（CSV格式）")
    print(f"   • {excel_all_filename} - 所有品种合并（Excel单表）")
    print(f"   • {excel_sheets_filename} - 按品种分工作表（Excel）")


def main():
    """主函数"""
    print()
    print("╔" + "=" * 98 + "╗")
    print("║" + " " * 32 + "四品种期货数据合并工具" + " " * 32 + "║")
    print("║" + " " * 30 + "玻璃 + 甲醇 + 尿素 + 纯碱" + " " * 30 + "║")
    print("╚" + "=" * 98 + "╝")
    print()
    
    # 合并数据
    combined_df = merge_all_futures()
    
    if combined_df is None:
        print("\n❌ 数据合并失败")
        return
    
    # 显示摘要
    display_summary(combined_df)
    
    # 保存文件
    save_files(combined_df)
    
    print("\n" + "=" * 100)
    print("✅ 数据合并完成！")
    print("=" * 100)
    print()
    print("💡 使用建议:")
    print("   • 查看所有数据: open all_futures_combined.xlsx")
    print("   • 按品种对比: open all_futures_by_variety.xlsx")
    print("   • CSV分析: cat all_futures_combined.csv")
    print()


if __name__ == "__main__":
    main()

