# 玻璃期货数据抓取工具

## 功能说明

从东方财富网/新浪财经抓取玻璃主连期货最近10天的行情数据，包括：
- 日期
- 开盘价
- 收盘价
- 最高价
- 最低价
- 最高最低价差
- 成交量
- 成交额

数据来源：[东方财富网 - 玻璃主连](https://quote.eastmoney.com/qihuo/FGM.html)

## 📦 提供的脚本版本

本项目提供了**三个不同版本**的脚本，您可以根据自己的环境选择：

### 1. ⭐ AkShare版本 (推荐)
**文件**: `fetch_glass_futures_akshare.py`
- ✅ **最简单易用**，代码最少
- ✅ 数据稳定可靠
- ❌ **需要Python 3.8或更高版本**
- 🔧 依赖：`akshare`, `pandas`, `openpyxl`

```bash
# 安装依赖
pip install akshare pandas openpyxl

# 运行脚本
python fetch_glass_futures_akshare.py
```

### 2. 🌐 API请求版本
**文件**: `fetch_glass_futures.py`
- ✅ 支持Python 3.7+
- ✅ 无需额外浏览器驱动
- ⚠️ API可能不稳定，有备用数据源
- 🔧 依赖：`requests`, `pandas`

```bash
# 安装依赖
pip install requests pandas

# 运行脚本
python fetch_glass_futures.py
```

### 3. 🤖 Selenium版本
**文件**: `fetch_glass_futures_selenium.py`
- ✅ 模拟真实浏览器访问
- ✅ 可以绕过某些API限制
- ❌ 需要安装Chrome浏览器和ChromeDriver
- ❌ 运行速度较慢
- 🔧 依赖：`selenium`, `pandas`

```bash
# 安装依赖
brew install chromedriver  # macOS
pip install selenium pandas

# 运行脚本
python fetch_glass_futures_selenium.py
```

## 🚀 快速开始

### 检查Python版本

```bash
python --version
# 或
python3 --version
```

### 推荐使用流程

1. **如果Python版本 >= 3.8**：使用AkShare版本（最简单）
2. **如果Python版本 = 3.7**：使用API请求版本
3. **如果前两个都失败**：使用Selenium版本（需要额外配置）

### 一键安装所有依赖

```bash
pip install -r requirements.txt
```

注意：某些依赖可能需要特定Python版本

## 使用方法

### 方法1: 直接运行（推荐）

```bash
# AkShare版本（推荐）
python3 fetch_glass_futures_akshare.py

# API版本
python3 fetch_glass_futures.py

# Selenium版本
python3 fetch_glass_futures_selenium.py
```

### 方法2: 添加执行权限后运行

```bash
chmod +x fetch_glass_futures_akshare.py
./fetch_glass_futures_akshare.py
```

## 输出结果

脚本会：
1. 在控制台显示最近10天的行情数据表格
2. 显示统计信息（平均开盘价、平均收盘价、最高/最低价格、平均价差等）
3. 自动保存数据到 `glass_futures_data.csv` 文件

## 输出示例

```
================================================================================
玻璃主连期货最近10天行情数据
================================================================================
       日期    开盘价    收盘价    最高价    最低价  最高最低价差     成交量        成交额
2024-01-15  1456.00  1462.00  1468.00  1452.00      16.00  125463  1825634000
2024-01-16  1462.00  1459.00  1465.00  1456.00       9.00  108234  1576432000
...
================================================================================

统计信息:
平均开盘价: 1458.50
平均收盘价: 1460.20
最高价格: 1475.00
最低价格: 1445.00
平均价差: 12.50
最大价差: 23.00 (日期: 2024-01-18)
```

## CSV文件格式

生成的CSV文件包含以下列：
- 日期
- 开盘价
- 收盘价
- 最高价
- 最低价
- 最高最低价差
- 成交量
- 成交额

可以使用Excel或其他数据分析工具打开查看。

## 注意事项

1. 需要网络连接才能获取数据
2. 数据来源于东方财富网，如果API变更可能需要更新脚本
3. 默认获取最近10天的数据，可以修改脚本中的 `days` 参数来调整
4. 数据仅供参考，不构成投资建议

## 自定义修改

如果需要获取不同天数的数据，可以修改脚本中的参数：

```python
# 在main()函数中修改days参数
df = fetch_glass_futures_data(days=20)  # 获取最近20天的数据
```

## 故障排除

如果遇到以下问题：

### 1. 网络连接错误
- 检查网络连接
- 确认可以访问东方财富网

### 2. 数据解析错误
- 可能是API格式发生变化
- 查看错误信息并联系维护者

### 3. 依赖包安装失败
```bash
# 使用清华源加速安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 许可证

本工具仅供学习和研究使用。

