#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选：最近20天内有涨停，且最新交易日为上涨的股票
- 条件1：近20天至少有一天涨停
- 条件2：最新一个交易日涨跌幅 > 0
数据来源：AkShare（与 filter_rising_stocks.py 一致）
"""

import akshare as ak
import pandas as pd
import time
import argparse
from datetime import datetime, timedelta


def parse_args():
    parser = argparse.ArgumentParser(description="近N天有涨停且最新交易日上涨的股票（AkShare）")
    parser.add_argument("-d", "--days", type=int, default=20, help="涨停查询区间：最近多少个交易日（默认20）")
    parser.add_argument("-n", "--number", type=int, default=None, help="最多扫描股票数量，不填则全市场")
    parser.add_argument("-o", "--output", type=str, default="limit_up_today_up", help="输出文件名前缀（默认 limit_up_today_up）")
    return parser.parse_args()


def get_stock_list():
    """获取A股股票列表（与 filter_rising_stocks.py 一致）"""
    try:
        print("正在获取A股股票列表...")
        stock_info = ak.stock_info_a_code_name()
        print(f"✓ 获取到 {len(stock_info)} 只股票")
        return stock_info
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        return None


def get_stock_daily_data(stock_code, days=30):
    """
    获取单只股票的日线数据（与 filter_rising_stocks.py 一致）
    days: 获取最近多少天的数据
    """
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")
        if df is None or df.empty:
            return None
        df_recent = df.tail(days).copy()
        return df_recent
    except Exception:
        return None


def is_limit_up(symbol, pct_chg, name=""):
    """
    判定单日是否涨停
    symbol: 6位股票代码，如 '000001'、'600000'
    pct_chg: 涨跌幅（百分比数值）
    name: 股票名称，用于判断ST
    """
    if pd.isna(pct_chg):
        return False
    pct = float(pct_chg)
    name = str(name or "")
    symbol = str(symbol or "")
    if "ST" in name.upper():
        return pct >= 4.8
    if symbol.startswith(("60", "00")):
        return pct >= 9.8
    if symbol.startswith(("30", "68")):
        return pct >= 19.8
    return pct >= 9.8


def get_limit_up_and_today_up(days=20, max_stocks=None):
    """筛选：近 days 天有涨停，且最新交易日上涨的股票"""
    print(f"条件：近{days}个交易日内有涨停，且最新交易日上涨\n")

    stock_list = get_stock_list()
    if stock_list is None:
        return pd.DataFrame(), days

    # 兼容列名：code/name 或 代码/名称
    cols = list(stock_list.columns)
    code_col = "code" if "code" in cols else ("代码" if "代码" in cols else cols[0])
    name_col = "name" if "name" in cols else ("名称" if "名称" in cols else cols[1])

    total = len(stock_list) if max_stocks is None else min(max_stocks, len(stock_list))
    fetch_days = min(90, max(30, days + 15))

    limit_up_records = []
    for idx, row in stock_list.head(total).iterrows():
        stock_code = row[code_col]
        stock_name = row[name_col]
        if (idx + 1) % 200 == 0 or idx == 0:
            print(f"  进度: {idx + 1}/{total} ...")
        df = get_stock_daily_data(stock_code, days=fetch_days)
        if df is None or df.empty:
            time.sleep(0.1)
            continue
        # 取最近 days 天的数据用于判断涨停
        recent = df.tail(days)
        has_limit_up = False
        limit_up_date = None
        limit_up_pct = None
        for _, day_row in recent.iterrows():
            pct = day_row.get("涨跌幅") if "涨跌幅" in day_row else day_row.get("change_pct")
            if pct is None:
                continue
            if is_limit_up(stock_code, pct, stock_name):
                has_limit_up = True
                limit_up_date = str(day_row.get("日期", day_row.get("date", "")))[:10]
                limit_up_pct = round(float(pct), 2)
                break
        if not has_limit_up:
            time.sleep(0.1)
            continue
        # 最新交易日是否上涨
        latest = df.iloc[-1]
        latest_pct = latest.get("涨跌幅") if "涨跌幅" in latest else latest.get("change_pct")
        if latest_pct is None:
            time.sleep(0.1)
            continue
        if float(latest_pct) <= 0:
            time.sleep(0.1)
            continue
        latest_date = str(latest.get("日期", latest.get("date", "")))[:10]
        limit_up_records.append({
            "code": stock_code,
            "name": stock_name,
            "limit_up_date": limit_up_date,
            "limit_up_pct": limit_up_pct,
            "latest_date": latest_date,
            "latest_pct_chg": round(float(latest_pct), 2),
        })
        time.sleep(0.1)

    result_df = pd.DataFrame(limit_up_records)
    return result_df, days


if __name__ == "__main__":
    args = parse_args()
    days = args.days
    out_base = args.output
    print(f"输出前缀: {out_base}\n")
    df_result, _ = get_limit_up_and_today_up(days=days, max_stocks=args.number)
    if df_result.empty:
        print("没有同时满足「近20天有涨停」且「最新交易日上涨」的股票。")
    else:
        print(f"\n共 {len(df_result)} 只：\n")
        print(df_result.to_string(index=False))
        csv_file = f"{out_base}.csv"
        df_result.to_csv(csv_file, index=False, encoding="utf-8-sig")
        print(f"\n结果已保存: {csv_file}")
