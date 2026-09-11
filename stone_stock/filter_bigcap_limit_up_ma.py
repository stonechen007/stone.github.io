#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选：总市值>100亿 + 近10日有过涨停 + 均线多头排列（MA5>MA10>MA20）
数据获取与 filter_limit_up_today_up.py 一致：stock_info_a_code_name + stock_zh_a_hist。
大市值列表：同源股票列表 + stock_individual_info_em 逐只取总市值。
"""

import os
import re
import akshare as ak
import pandas as pd
import time
import argparse
from datetime import datetime, timedelta

# Tushare 备用：从环境变量读取，未设置则东方财富失败后提示用户
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")


def parse_args():
    parser = argparse.ArgumentParser(description="大市值+近10日涨停+均线多头排列")
    parser.add_argument("-m", "--min_market_cap", type=float, default=100, help="最低总市值（亿元），默认100")
    parser.add_argument("-d", "--limit_up_days", type=int, default=10, help="涨停查询区间：最近多少个交易日，默认10")
    parser.add_argument("-n", "--number", type=int, default=None, help="大市值阶段最多检查股票数，不填则全市场")
    parser.add_argument("-o", "--output", type=str, default="bigcap_limit_up_ma", help="输出文件名前缀")
    return parser.parse_args()


# ========== 与 filter_limit_up_today_up.py 相同的数据获取方式 ==========

def get_stock_list():
    """获取A股股票列表（与 filter_limit_up_today_up.py 一致）"""
    try:
        print("正在获取A股股票列表...")
        stock_info = ak.stock_info_a_code_name()
        print(f"✓ 获取到 {len(stock_info)} 只股票")
        return stock_info
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        return None


def get_stock_daily_data(stock_code, days=70):
    """获取单只股票日线（与 filter_limit_up_today_up.py 一致）"""
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")
        if df is None or df.empty:
            return None
        return df.tail(days).copy()
    except Exception:
        return None


def get_bigcap_stocks(min_cap_billion=100, max_stocks=None):
    """
    大市值列表：与 filter_limit_up_today_up 同源。
    先 stock_info_a_code_name()，再逐只 stock_individual_info_em 取总市值并筛选。
    """
    stock_list = get_stock_list()
    if stock_list is None:
        return None
    cols = list(stock_list.columns)
    code_col = "code" if "code" in cols else ("代码" if "代码" in cols else cols[0])
    name_col = "name" if "name" in cols else ("名称" if "名称" in cols else cols[1])
    total = len(stock_list) if max_stocks is None else min(max_stocks, len(stock_list))
    big_list = []
    for i, (_, row) in enumerate(stock_list.head(total).iterrows()):
        code = row[code_col]
        name = row[name_col]
        if (i + 1) % 200 == 0 or (i + 1) == total:
            print(f"  获取市值进度: {i + 1}/{total}，已筛出 {len(big_list)} 只>={min_cap_billion}亿")
        try:
            info = ak.stock_individual_info_em(symbol=code)
            if info is None or info.empty:
                time.sleep(0.12)
                continue
            cap_val = None
            key_col, val_col = None, None
            for a, b in [("item", "value"), ("键", "值"), ("项", "值")]:
                if a in info.columns and b in info.columns:
                    key_col, val_col = a, b
                    break
            if key_col is None and len(info.columns) >= 2:
                key_col, val_col = info.columns[0], info.columns[1]
            if key_col is None:
                time.sleep(0.12)
                continue
            cap_row = info[info[key_col].astype(str).str.contains("总市值", na=False)]
            if not cap_row.empty:
                val = cap_row.iloc[0][val_col]
                if isinstance(val, str):
                    s = re.sub(r"[,\s]", "", val).strip()
                    num = re.sub(r"[^\d.]", "", s)
                    cap_val = float(num) if num else None
                    if cap_val is not None and "万" in val and "亿" not in val:
                        cap_val = cap_val / 10000
                else:
                    cap_val = float(val) if pd.notna(val) else None
            if cap_val is not None and cap_val >= min_cap_billion:
                big_list.append({"code": code, "name": name, "total_cap_billion": round(cap_val, 0)})
        except Exception:
            pass
        time.sleep(0.12)
    if not big_list:
        print(f"✓ 总市值>={min_cap_billion}亿的股票 0 只")
        return pd.DataFrame(columns=["code", "name", "total_cap_billion"])
    big = pd.DataFrame(big_list)
    print(f"✓ 总市值>={min_cap_billion}亿的股票共 {len(big)} 只")
    return big


def get_bigcap_stocks_tushare(min_cap_billion=100):
    """
    备用方案：用 Tushare 获取总市值 >= min_cap_billion 亿元的A股。
    需设置环境变量 TUSHARE_TOKEN，或脚本内配置 token。
    daily_basic 中 total_mv 单位为万元，1000亿 = 10000000 万。
    """
    token = TUSHARE_TOKEN or os.environ.get("TUSHARE_TOKEN", "")
    if not token:
        print("❌ 未配置 TUSHARE_TOKEN，无法使用 Tushare 备用。")
        print("   请执行: export TUSHARE_TOKEN=你的token")
        return None
    try:
        import tushare as ts
        ts.set_token(token)
        pro = ts.pro_api()
    except ImportError:
        print("❌ 未安装 tushare，请: pip install tushare")
        return None

    try:
        print("使用 Tushare 获取大市值股票列表...")
        # 最近交易日
        end = datetime.now().strftime("%Y%m%d")
        start = (datetime.now() - timedelta(days=15)).strftime("%Y%m%d")
        cal = pro.trade_cal(exchange="SSE", start_date=start, end_date=end, is_open=1)
        if cal is None or cal.empty:
            trade_date = end
        else:
            trade_date = str(cal.iloc[-1]["cal_date"])
        # 全市场每日指标，含 total_mv（万元）
        df = pro.daily_basic(trade_date=trade_date, fields="ts_code,total_mv")
        if df is None or df.empty:
            print("❌ Tushare 当日指标为空")
            return None
        df["total_mv"] = pd.to_numeric(df["total_mv"], errors="coerce")
        df = df.dropna(subset=["total_mv"])
        # 1000亿 = 10000000 万元
        min_mv_wan = min_cap_billion * 10000
        big = df[df["total_mv"] >= min_mv_wan].copy()
        if big.empty:
            print(f"✓ Tushare 筛选后 总市值>={min_cap_billion}亿 的股票 0 只")
            return pd.DataFrame(columns=["code", "name", "total_cap_billion"])
        # 补全名称：stock_basic
        basic = pro.stock_basic(exchange="", list_status="L", fields="ts_code,name")
        basic = basic[basic["ts_code"].str.endswith(("SH", "SZ"))]
        big = big.merge(basic, on="ts_code", how="left")
        big["code"] = big["ts_code"].str.replace(".SH", "").str.replace(".SZ", "")
        big["total_cap_billion"] = (big["total_mv"] / 10000).round(0)
        big = big[["code", "name", "total_cap_billion"]].drop_duplicates(subset=["code"])
        print(f"✓ 总市值>={min_cap_billion}亿的股票共 {len(big)} 只（Tushare）")
        return big
    except Exception as e:
        print(f"❌ Tushare 获取大市值失败: {e}")
        return None


def is_limit_up(symbol, pct_chg, name=""):
    """判定是否涨停"""
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


def has_limit_up_in_last_n_days(df, symbol, name, n=10):
    """最近 n 个交易日是否有一天涨停。df 为日线，按日期升序，最后一行为最新日"""
    if df is None or len(df) < n:
        return False, None, None
    recent = df.tail(n)
    close_col = "收盘" if "收盘" in df.columns else "close"
    pct_col = "涨跌幅" if "涨跌幅" in df.columns else "change_pct"
    date_col = "日期" if "日期" in df.columns else "date"
    for _, row in recent.iterrows():
        pct = row.get(pct_col)
        if is_limit_up(symbol, pct, name):
            return True, str(row.get(date_col, ""))[:10], round(float(pct), 2) if pct is not None else None
    return False, None, None


def is_ma_bull_aligned(df):
    """
    均线多头排列：最新一日 MA5 > MA10 > MA20。
    df 需至少 20 行，按日期升序。
    """
    if df is None or len(df) < 20:
        return False, {}
    close_col = "收盘" if "收盘" in df.columns else "close"
    closes = df[close_col].astype(float)
    ma5 = closes.rolling(5).mean().iloc[-1]
    ma10 = closes.rolling(10).mean().iloc[-1]
    ma20 = closes.rolling(20).mean().iloc[-1]
    ok = ma5 > ma10 > ma20
    info = {"ma5": round(ma5, 2), "ma10": round(ma10, 2), "ma20": round(ma20, 2)}
    return ok, info


def run_filter(min_cap_billion=100, limit_up_days=10, output_prefix="bigcap_limit_up_ma", max_stocks=None):
    # 与 filter_limit_up_today_up 同源：先股票列表再逐只取市值
    big = get_bigcap_stocks(min_cap_billion, max_stocks=max_stocks)
    if big is None:
        print("尝试 Tushare 备用方案...")
        big = get_bigcap_stocks_tushare(min_cap_billion)
    if big is None or big.empty:
        return pd.DataFrame()

    code_col = [c for c in big.columns if "代码" in c or c == "code"][0]
    name_col = [c for c in big.columns if "名称" in c or c == "name"][0]
    cap_col = [c for c in big.columns if "市值" in c or c == "total_cap_billion"][0]

    results = []
    total = len(big)
    for i, (_, row) in enumerate(big.iterrows()):
        code = row[code_col]
        name = row[name_col]
        cap = row[cap_col]
        if (i + 1) % 50 == 0 or (i + 1) == total:
            print(f"  进度: {i + 1}/{total}，已符合 {len(results)} 只")
        df = get_stock_daily_data(code, days=70)
        if df is None or len(df) < 20:
            time.sleep(0.08)
            continue
        has_lu, lu_date, lu_pct = has_limit_up_in_last_n_days(df, code, name, n=limit_up_days)
        if not has_lu:
            time.sleep(0.08)
            continue
        ok_ma, ma_info = is_ma_bull_aligned(df)
        if not ok_ma:
            time.sleep(0.08)
            continue
        close_col = "收盘" if "收盘" in df.columns else "close"
        date_col = "日期" if "日期" in df.columns else "date"
        latest_close = float(df[close_col].iloc[-1])
        latest_date = str(df[date_col].iloc[-1])[:10]
        results.append({
            "code": code,
            "name": name,
            "total_cap_billion": round(float(cap), 0),
            "limit_up_date": lu_date,
            "limit_up_pct": lu_pct,
            "latest_date": latest_date,
            "latest_close": latest_close,
            "ma5": ma_info["ma5"],
            "ma10": ma_info["ma10"],
            "ma20": ma_info["ma20"],
        })
        time.sleep(0.08)

    return pd.DataFrame(results)


if __name__ == "__main__":
    args = parse_args()
    print(f"条件：总市值>={args.min_market_cap}亿，近{args.limit_up_days}日有过涨停，均线多头排列(MA5>MA10>MA20)\n")
    df_result = run_filter(
        min_cap_billion=args.min_market_cap,
        limit_up_days=args.limit_up_days,
        output_prefix=args.output,
        max_stocks=args.number,
    )
    if df_result.empty:
        print("没有同时满足三项条件的股票。")
    else:
        print(f"\n共 {len(df_result)} 只：\n")
        print(df_result.to_string(index=False))
        csv_file = f"{args.output}.csv"
        df_result.to_csv(csv_file, index=False, encoding="utf-8-sig")
        print(f"\n结果已保存: {csv_file}")
