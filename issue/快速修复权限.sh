#!/bin/bash
# 快速修复Homebrew权限问题

echo "========================================================================"
echo "🔧 快速修复Homebrew权限"
echo "========================================================================"
echo ""
echo "需要输入您的电脑密码..."
echo ""

# 修复Docker目录权限
if [ -d "/usr/local/lib/docker" ]; then
    sudo chown -R $(whoami) /usr/local/lib/docker
    echo "✓ Docker目录权限已修复"
fi

# 修复其他常见目录
sudo chown -R $(whoami) /usr/local/bin 2>/dev/null || true
sudo chown -R $(whoami) /usr/local/lib 2>/dev/null || true
sudo chown -R $(whoami) /usr/local/share 2>/dev/null || true

echo ""
echo "========================================================================"
echo "✅ 权限修复完成！"
echo "========================================================================"
echo ""
echo "现在可以运行："
echo "  brew install python@3.11"
echo ""

