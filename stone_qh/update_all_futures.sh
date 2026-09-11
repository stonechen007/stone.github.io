#!/bin/bash
# 一键更新所有期货品种数据

echo "========================================================================"
echo "🔄 更新所有期货品种数据"
echo "========================================================================"
echo ""

# 进入项目目录
cd /Users/shishengchen/promotion/stone.github.io

# 1. 获取玻璃数据
echo "📊 步骤1/3: 获取玻璃数据..."
echo "----------------------------------------"
python3.11 fetch_glass_futures_akshare.py
echo ""

# 2. 获取甲醇、尿素、纯碱数据
echo "📊 步骤2/3: 获取甲醇、尿素、纯碱数据..."
echo "----------------------------------------"
python3.11 fetch_multiple_futures.py
echo ""

# 3. 合并所有数据
echo "📊 步骤3/3: 合并所有数据..."
echo "----------------------------------------"
python3.11 merge_all_futures.py
echo ""

echo "========================================================================"
echo "✅ 所有数据更新完成！"
echo "========================================================================"
echo ""
echo "生成的文件："
echo "  • all_futures_combined.csv - 合并数据（CSV）"
echo "  • all_futures_combined.xlsx - 合并数据（Excel单表）"
echo "  • all_futures_by_variety.xlsx - 按品种分表（推荐）⭐"
echo ""
echo "查看数据："
echo "  open all_futures_by_variety.xlsx"
echo ""

