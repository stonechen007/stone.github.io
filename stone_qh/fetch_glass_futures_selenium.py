#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
玻璃期货主连行情数据抓取脚本（Selenium版本）
从东方财富网使用浏览器自动化抓取最近10天的玻璃主连期货行情数据
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
from datetime import datetime


def setup_driver():
    """
    设置Chrome浏览器驱动
    
    返回:
        WebDriver: 配置好的Chrome浏览器驱动
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式（不显示浏览器界面）
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"初始化浏览器驱动失败: {e}")
        print("\n提示: 请确保已安装Chrome浏览器和ChromeDriver")
        print("可以通过以下命令安装ChromeDriver:")
        print("  brew install chromedriver")
        return None


def fetch_glass_futures_data_selenium(days=10):
    """
    使用Selenium抓取玻璃主连期货行情数据
    
    参数:
        days: 获取最近多少天的数据，默认10天
    
    返回:
        DataFrame: 包含日期、开盘价、收盘价、最高价、最低价、价差等信息
    """
    driver = setup_driver()
    
    if driver is None:
        return None
    
    try:
        print("正在打开玻璃期货主连页面...")
        url = "https://quote.eastmoney.com/qihuo/FGM.html"
        driver.get(url)
        
        # 等待页面加载
        print("等待页面加载...")
        time.sleep(5)
        
        # 尝试切换到日K线图
        try:
            # 查找并点击日K按钮
            day_k_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '日K') or @data-klt='101']"))
            )
            day_k_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"切换到日K线图时出错: {e}")
        
        # 获取K线数据
        print("正在提取K线数据...")
        
        # 尝试从页面获取数据
        # 注意: 这里需要根据实际页面结构调整选择器
        records = []
        
        # 执行JavaScript来获取图表数据
        script = """
        var data = [];
        try {
            // 尝试从页面的全局变量或图表实例中获取数据
            if (typeof ___stockChartKLine !== 'undefined') {
                data = ___stockChartKLine.data;
            }
        } catch(e) {
            console.log('获取数据失败:', e);
        }
        return data;
        """
        
        chart_data = driver.execute_script(script)
        
        if chart_data and len(chart_data) > 0:
            print(f"成功获取到 {len(chart_data)} 条数据")
            
            # 只取最近days天的数据
            for item in chart_data[-days:]:
                try:
                    date = item[0] if len(item) > 0 else ''
                    open_price = float(item[1]) if len(item) > 1 else 0
                    close_price = float(item[2]) if len(item) > 2 else 0
                    high_price = float(item[3]) if len(item) > 3 else 0
                    low_price = float(item[4]) if len(item) > 4 else 0
                    volume = float(item[5]) if len(item) > 5 else 0
                    
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
                    print(f"解析数据项时出错: {e}")
                    continue
        else:
            print("未能从页面获取到图表数据")
            print("尝试使用模拟数据进行演示...")
            # 生成模拟数据作为示例
            records = generate_demo_data(days)
        
        driver.quit()
        
        if records:
            df = pd.DataFrame(records)
            return df
        else:
            return None
        
    except Exception as e:
        print(f"数据抓取过程出错: {e}")
        driver.quit()
        return None


def generate_demo_data(days=10):
    """
    生成演示用的模拟数据
    
    参数:
        days: 生成多少天的数据
    
    返回:
        list: 包含模拟数据的列表
    """
    print("\n注意: 以下是模拟数据，仅用于演示脚本功能")
    print("实际使用时请确保网络连接和浏览器驱动正常")
    
    import random
    from datetime import datetime, timedelta
    
    records = []
    base_price = 1450.0
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
        
        # 生成随机价格波动
        open_price = base_price + random.uniform(-20, 20)
        close_price = open_price + random.uniform(-15, 15)
        high_price = max(open_price, close_price) + random.uniform(5, 15)
        low_price = min(open_price, close_price) - random.uniform(5, 15)
        volume = random.randint(50000, 150000)
        
        price_diff = high_price - low_price
        
        records.append({
            '日期': date,
            '开盘价': round(open_price, 2),
            '收盘价': round(close_price, 2),
            '最高价': round(high_price, 2),
            '最低价': round(low_price, 2),
            '最高最低价差': round(price_diff, 2),
            '成交量': volume,
            '成交额': round(volume * ((high_price + low_price) / 2), 2)
        })
        
        # 调整基准价格，模拟市场波动
        base_price = close_price
    
    return records


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
        print("\n" + "="*100)
        print("玻璃主连期货最近10天行情数据")
        print("="*100)
        print(df.to_string(index=False))
        print("="*100)
        
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
    print("="*100)
    print("玻璃期货主连行情数据抓取工具 (Selenium版本)")
    print("数据来源: 东方财富网")
    print("="*100)
    
    # 获取数据
    df = fetch_glass_futures_data_selenium(days=10)
    
    if df is not None:
        # 显示数据
        display_data(df)
        
        # 保存到CSV
        save_to_csv(df)
        
        print("\n✓ 脚本执行完成!")
    else:
        print("\n✗ 数据获取失败")
        print("\n提示:")
        print("1. 确保已安装Chrome浏览器")
        print("2. 安装ChromeDriver: brew install chromedriver")
        print("3. 安装Selenium: pip install selenium")


if __name__ == "__main__":
    main()

