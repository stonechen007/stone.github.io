# 🚀 快速开始指南

## 📁 已创建的文件

本项目包含以下文件：

### 主要脚本（4个版本）

1. **fetch_glass_futures_demo.py** ⭐ 推荐先运行
   - ✅ 无需任何依赖
   - ✅ 立即可运行
   - ✅ 生成演示数据展示功能
   - 📝 用途：了解脚本功能和输出格式

2. **fetch_glass_futures_akshare.py** ⭐ 最佳选择（获取真实数据）
   - 需要 Python 3.8+
   - 需要安装：`pip install akshare pandas openpyxl`
   - 数据最稳定可靠

3. **fetch_glass_futures.py**
   - 支持 Python 3.7+
   - 需要安装：`pip install requests pandas`
   - 使用API获取数据

4. **fetch_glass_futures_selenium.py**
   - 支持 Python 3.7+
   - 需要安装：`pip install selenium pandas` + ChromeDriver
   - 使用浏览器自动化

### 配置文件

- **requirements.txt** - 依赖包列表
- **README_FUTURES.md** - 详细使用说明
- **QUICKSTART.md** - 本文件

## 🎯 30秒快速体验

```bash
# 1. 进入项目目录
cd /Users/shishengchen/promotion/stone.github.io

# 2. 运行演示版本（无需安装任何依赖）
python3 fetch_glass_futures_demo.py

# 3. 查看生成的文件
# - glass_futures_demo.csv （可用Excel打开）
# - glass_futures_demo.txt （文本格式）
```

## 📊 获取真实数据

### 方案一：使用AkShare（推荐）

```bash
# 1. 检查Python版本（需要3.8+）
python3 --version

# 2. 安装依赖
pip3 install akshare pandas openpyxl

# 3. 运行脚本
python3 fetch_glass_futures_akshare.py

# 4. 查看输出文件
# - glass_futures_data.csv
# - glass_futures_data.xlsx
```

### 方案二：使用API（Python 3.7兼容）

```bash
# 1. 安装依赖
pip3 install requests pandas

# 2. 运行脚本
python3 fetch_glass_futures.py

# 3. 查看输出文件
# - glass_futures_data.csv
```

### 方案三：使用Selenium（最后手段）

```bash
# 1. 安装Chrome浏览器（如果没有）

# 2. 安装ChromeDriver
brew install chromedriver  # macOS
# 或从官网下载：https://chromedriver.chromium.org/

# 3. 安装依赖
pip3 install selenium pandas

# 4. 运行脚本
python3 fetch_glass_futures_selenium.py
```

## 📈 数据说明

脚本会获取玻璃主连期货（FG0）最近10天的以下数据：

| 字段 | 说明 |
|------|------|
| 日期 | 交易日期 |
| 开盘价 | 当日开盘价格（元） |
| 收盘价 | 当日收盘价格（元） |
| 最高价 | 当日最高价格（元） |
| 最低价 | 当日最低价格（元） |
| 最高最低价差 | 当日价格波动幅度（元） |
| 成交量 | 成交量（手） |
| 成交额 | 成交金额（元） |

## 📁 输出文件

运行脚本后会生成以下文件：

- **CSV文件** - 可用Excel、Numbers等表格软件打开
- **Excel文件** - 仅AkShare版本生成
- **TXT文件** - 仅演示版本生成

## ❓ 常见问题

### Q1: Python版本太低怎么办？

```bash
# 查看当前版本
python3 --version

# 如果低于3.8，有两个选择：
# 1. 升级Python（推荐）
brew install python@3.11  # macOS

# 2. 使用API版本脚本（支持Python 3.7）
python3 fetch_glass_futures.py
```

### Q2: 安装依赖失败怎么办？

```bash
# 使用国内镜像加速
pip3 install akshare pandas -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 网络连接失败怎么办？

1. 检查网络连接
2. 尝试使用不同的脚本版本
3. 稍后重试（数据源可能暂时不可用）

### Q4: 如何获取更多天数的数据？

编辑脚本文件，找到这一行：

```python
df = fetch_glass_futures_data(days=10)
```

修改为：

```python
df = fetch_glass_futures_data(days=30)  # 获取30天数据
```

### Q5: 如何定时运行脚本？

在macOS/Linux上可以使用crontab：

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天早上9点运行）
0 9 * * * cd /Users/shishengchen/promotion/stone.github.io && python3 fetch_glass_futures_akshare.py
```

## 💡 使用建议

1. **第一次使用**：先运行演示版本了解功能
2. **日常使用**：推荐使用AkShare版本（数据最稳定）
3. **数据分析**：CSV文件可直接导入Excel进行分析
4. **自动化**：可配合定时任务定期获取数据

## 🔗 相关链接

- [东方财富网 - 玻璃主连](https://quote.eastmoney.com/qihuo/FGM.html)
- [AkShare文档](https://akshare.akfamily.xyz/)
- [Pandas文档](https://pandas.pydata.org/)

## 📞 获取帮助

如果遇到问题：

1. 查看 `README_FUTURES.md` 详细文档
2. 检查Python版本和依赖安装
3. 确认网络连接正常
4. 尝试运行演示版本测试环境

---

**祝使用愉快！** 📈


