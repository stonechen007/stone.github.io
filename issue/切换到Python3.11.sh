#!/bin/bash
# 切换系统默认Python到3.11

echo "========================================================================"
echo "🐍 切换Python版本到3.11"
echo "========================================================================"
echo ""

# 检查Python 3.11是否安装
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 未安装"
    echo "请先运行: brew install python@3.11"
    exit 1
fi

echo "当前Python版本:"
python3 --version
echo ""

echo "Python 3.11 位置:"
which python3.11
python3.11 --version
echo ""

# 方法1：更新PATH（推荐）
echo "📋 方法1：配置PATH优先级"
echo "----------------------------------------"
# 检查是否已经添加
if grep -q "/usr/local/opt/python@3.11/bin" ~/.zshrc 2>/dev/null; then
    echo "✓ PATH配置已存在"
else
    echo 'export PATH="/usr/local/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
    echo "✓ 已添加到 ~/.zshrc"
fi

# 也添加到~/.bash_profile以防用户使用bash
if grep -q "/usr/local/opt/python@3.11/bin" ~/.bash_profile 2>/dev/null; then
    echo "✓ Bash配置已存在"
else
    echo 'export PATH="/usr/local/opt/python@3.11/bin:$PATH"' >> ~/.bash_profile
    echo "✓ 已添加到 ~/.bash_profile"
fi
echo ""

# 方法2：创建别名
echo "📋 方法2：创建命令别名"
echo "----------------------------------------"
if grep -q "alias python3=" ~/.zshrc 2>/dev/null; then
    echo "✓ 别名已存在"
else
    echo 'alias python3="/usr/local/bin/python3.11"' >> ~/.zshrc
    echo 'alias pip3="/usr/local/bin/pip3.11"' >> ~/.zshrc
    echo "✓ 已添加别名到 ~/.zshrc"
fi
echo ""

# 在当前终端生效
export PATH="/usr/local/opt/python@3.11/bin:$PATH"
alias python3="/usr/local/bin/python3.11"
alias pip3="/usr/local/bin/pip3.11"

echo "========================================================================"
echo "✅ 配置完成！"
echo "========================================================================"
echo ""
echo "在当前终端验证:"
python3 --version
echo ""
echo "⚠️  重要提示："
echo "1. 请 关闭并重新打开 终端窗口"
echo "2. 或者运行: source ~/.zshrc"
echo "3. 然后验证: python3 --version"
echo ""
echo "如果重启终端后还是显示3.7，直接使用 python3.11："
echo "   python3.11 --version"
echo "   pip3.11 install akshare pandas openpyxl"
echo "   python3.11 fetch_glass_futures_akshare.py"
echo ""
echo "========================================================================"

