#!/bin/bash
# 一键修复Homebrew权限问题并安装Python 3.11

set -e  # 遇到错误就停止

echo "========================================================================"
echo "🔧 Homebrew权限修复和Python 3.11安装工具"
echo "========================================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否有sudo权限
echo "📋 步骤1/5: 检查权限..."
if ! sudo -n true 2>/dev/null; then
    echo -e "${YELLOW}需要管理员权限来修复文件权限${NC}"
    echo "请输入您的电脑密码："
    sudo -v
fi

# 保持sudo权限活跃
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

echo -e "${GREEN}✓ 权限检查通过${NC}"
echo ""

# 修复Docker目录权限
echo "📋 步骤2/5: 修复Docker目录权限..."
if [ -d "/usr/local/lib/docker" ]; then
    sudo chown -R $(whoami) /usr/local/lib/docker
    echo -e "${GREEN}✓ Docker目录权限已修复${NC}"
else
    echo -e "${YELLOW}⚠ Docker目录不存在，跳过${NC}"
fi
echo ""

# 修复Homebrew相关目录权限
echo "📋 步骤3/5: 修复Homebrew目录权限..."
for dir in /usr/local/bin /usr/local/lib /usr/local/share /usr/local/Cellar /usr/local/Caskroom; do
    if [ -d "$dir" ]; then
        sudo chown -R $(whoami) "$dir" 2>/dev/null || true
    fi
done
echo -e "${GREEN}✓ Homebrew目录权限已修复${NC}"
echo ""

# 运行brew doctor检查
echo "📋 步骤4/5: 检查Homebrew状态..."
brew doctor || echo -e "${YELLOW}⚠ 有一些警告，但可以继续${NC}"
echo ""

# 安装Python 3.11
echo "📋 步骤5/5: 安装Python 3.11..."
if brew list python@3.11 &>/dev/null; then
    echo -e "${GREEN}✓ Python 3.11已经安装${NC}"
else
    echo "正在安装Python 3.11（这可能需要几分钟）..."
    if brew install python@3.11; then
        echo -e "${GREEN}✓ Python 3.11安装成功${NC}"
    else
        echo -e "${RED}✗ Python 3.11安装失败${NC}"
        echo ""
        echo "备用方案："
        echo "1. 使用pyenv: brew install pyenv && pyenv install 3.11.0"
        echo "2. 下载官方安装包: https://www.python.org/downloads/"
        exit 1
    fi
fi
echo ""

# 检查Python版本
echo "========================================================================"
echo "✅ 修复完成！"
echo "========================================================================"
echo ""
echo "Python版本信息："
python3 --version
echo ""

# 提示安装AkShare
echo "📦 下一步操作："
echo ""
echo "1. 安装AkShare和相关包："
echo "   pip3 install akshare pandas openpyxl"
echo ""
echo "2. 运行脚本获取真实数据："
echo "   cd /Users/shishengchen/promotion/stone.github.io"
echo "   python3 fetch_glass_futures_akshare.py"
echo ""
echo "========================================================================"

# 询问是否立即安装AkShare
read -p "是否现在安装AkShare？(y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在安装AkShare..."
    pip3 install akshare pandas openpyxl
    echo ""
    echo -e "${GREEN}✓ AkShare安装完成！${NC}"
    echo ""
    echo "现在可以运行："
    echo "  cd /Users/shishengchen/promotion/stone.github.io"
    echo "  python3 fetch_glass_futures_akshare.py"
fi

echo ""
echo "🎉 全部完成！"

