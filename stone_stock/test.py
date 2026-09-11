import tushare as ts
import pandas as pd
import time
import argparse
from datetime import datetime, timedelta

# ===================== 第一步：配置Tushare（必填） =====================
# 1. 先去Tushare官网注册账号：https://tushare.pro/register
# 2. 获取你的token（个人中心→接口TOKEN），替换下面的字符串
ts.set_token("208ea4bb0edd08b6e491c897ed9c0fa3e1ea2953afc928f7983120d3")
pro = ts.pro_api()

# ===================== 核心参数配置（可由命令行覆盖） =====================
def parse_args():
    parser = argparse.ArgumentParser(description="筛选近N天内有涨停的股票（Tushare）")
    parser.add_argument("-d", "--days", type=int, default=20, help="查询最近多少个自然日（默认20）")
    parser.add_argument("-n", "--number", type=int, default=None, help="最多扫描股票数量，不填则全市场")
    parser.add_argument("-o", "--output", type=str, default="limit_up_stocks", help="输出文件名（不含后缀，默认 limit_up_stocks）")
    return parser.parse_args()

# ===================== 辅助函数：判定是否涨停 =====================
def is_limit_up(row, name=""):
    """
    判定单只股票单日是否涨停
    row: DataFrame的行数据，包含涨跌幅、股票代码等字段
    name: 股票名称，用于判断ST（ST在名称里不在代码里）
    return: True=涨停，False=未涨停
    """
    ts_code = row['ts_code']
    pct_chg = row['pct_chg']  # 涨跌幅（百分比）
    name = str(name)
    
    # 1. ST股（名称含ST）：涨停阈值≈4.8%
    if 'ST' in name.upper():
        return pct_chg >= 4.8
    # 2. 主板（60、00开头）：涨停阈值≈9.8%
    if ts_code.startswith(('60', '00')):
        return pct_chg >= 9.8
    # 3. 创业板（30）、科创板（68）：涨停阈值≈19.8%
    if ts_code.startswith(('30', '68')):
        return pct_chg >= 19.8
    # 其他（如北交所）暂按10%判定
    return pct_chg >= 9.8

# ===================== 核心逻辑：抓取近N天有涨停的股票 =====================
def get_limit_up_stocks(days=20, max_stocks=None):
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

    print("正在获取全市场股票列表...")
    stock_basic = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,industry')
    a_stocks = stock_basic[stock_basic['ts_code'].str.endswith(('SH', 'SZ'))]
    if max_stocks is not None:
        a_stocks = a_stocks.head(max_stocks)
    total = len(a_stocks)

    limit_up_records = []
    for idx, row in a_stocks.iterrows():
        ts_code = row['ts_code']
        name = row['name']
        industry = row.get('industry', '')
        if (idx + 1) % 500 == 0 or idx == 0:
            print(f"  进度: {idx + 1}/{total} ...")
        try:
            df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df is None or df.empty:
                time.sleep(0.2)
                continue
            for _, day_row in df.iterrows():
                if is_limit_up(day_row, name=name):
                    limit_up_records.append({
                        'ts_code': ts_code,
                        'name': name,
                        'industry': industry,
                        'limit_up_date': day_row['trade_date'],
                        'pct_chg': day_row['pct_chg']
                    })
                    break
        except Exception as e:
            pass
        time.sleep(0.2)

    seen = set()
    unique_stocks = []
    for r in limit_up_records:
        if r['ts_code'] not in seen:
            seen.add(r['ts_code'])
            unique_stocks.append(r)

    result_df = pd.DataFrame(unique_stocks)
    return result_df, start_date, end_date, days


# ===================== 主程序 =====================
if __name__ == "__main__":
    args = parse_args()
    days = args.days
    out_base = args.output
    print(f"查询时间范围: 近{days}个自然日，输出前缀: {out_base}\n")
    df_result, start_date, end_date, _ = get_limit_up_stocks(days=days, max_stocks=args.number)
    print(f"实际日期范围: {start_date} ~ {end_date}\n")
    if df_result.empty:
        print(f"近{days}天内没有筛选到有涨停记录的股票。")
    else:
        print(f"\n共筛选出 {len(df_result)} 只近{days}天内有涨停的股票：\n")
        print(df_result.to_string(index=False))
        csv_file = f"{out_base}.csv"
        df_result.to_csv(csv_file, index=False, encoding="utf-8-sig")
        print(f"\n结果已保存到: {csv_file}")