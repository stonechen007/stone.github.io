# Python 3.7 → 3.11 升级指南

## 🎯 目标
将Python从 **3.7.6** 升级到 **3.11**，以便能够安装和使用AkShare获取真实的玻璃期货数据。

## ⚡ 方法1：一键自动升级（推荐）⭐⭐⭐⭐⭐

### 在终端中运行以下命令：

```bash
cd /Users/shishengchen/promotion/stone.github.io
./一键修复.sh
```

**这个脚本会自动完成：**
1. ✅ 修复Homebrew权限问题
2. ✅ 安装Python 3.11
3. ✅ 询问是否安装AkShare
4. ✅ 配置完成后可直接使用

**预计时间：** 10-15分钟（取决于网络速度）

**提示：** 会要求输入您的电脑密码（输入时不显示，输入完按回车）

---

## 🔧 方法2：手动分步升级

如果方法1失败，可以手动执行以下步骤：

### 步骤1：修复Homebrew权限

```bash
cd /Users/shishengchen/promotion/stone.github.io
./快速修复权限.sh
```

### 步骤2：安装Python 3.11

```bash
brew install python@3.11
```

等待安装完成（可能需要5-10分钟）

### 步骤3：验证安装

```bash
python3 --version
# 应该显示：Python 3.11.x
```

如果还是显示3.7，执行：

```bash
# 查找Python 3.11位置
which python3.11

# 创建链接
sudo ln -sf /usr/local/bin/python3.11 /usr/local/bin/python3

# 或者每次使用时明确指定
python3.11 --version
```

### 步骤4：安装AkShare

```bash
pip3 install akshare pandas openpyxl
```

### 步骤5：获取真实数据

```bash
cd /Users/shishengchen/promotion/stone.github.io
python3 fetch_glass_futures_akshare.py
```

---

## 🐍 方法3：使用pyenv（备选方案）

如果Homebrew方式遇到问题，使用pyenv：

### 安装pyenv

```bash
# 修复权限
cd /Users/shishengchen/promotion/stone.github.io
./快速修复权限.sh

# 安装pyenv
brew install pyenv
```

### 配置环境变量

```bash
# 添加到shell配置
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init --path)"' >> ~/.zshrc

# 重新加载配置
source ~/.zshrc
```

### 安装Python 3.11

```bash
# 安装Python 3.11
pyenv install 3.11.0

# 设置为全局默认版本
pyenv global 3.11.0

# 验证版本
python --version
```

### 安装依赖并使用

```bash
pip install akshare pandas openpyxl
cd /Users/shishengchen/promotion/stone.github.io
python fetch_glass_futures_akshare.py
```

---

## 📦 方法4：使用官方安装包

### 下载并安装

1. 访问：https://www.python.org/downloads/macos/
2. 下载 **Python 3.11** for macOS
3. 双击 `.pkg` 文件按提示安装

### 安装后配置

```bash
# 验证版本
python3 --version

# 如果还是3.7，找到新安装的Python
/Library/Frameworks/Python.framework/Versions/3.11/bin/python3 --version

# 创建别名
echo 'alias python3="/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"' >> ~/.zshrc
source ~/.zshrc

# 安装AkShare
pip3 install akshare pandas openpyxl
```

---

## ✅ 验证升级是否成功

### 运行这些命令检查：

```bash
# 1. 检查Python版本
python3 --version
# 期望输出：Python 3.11.x

# 2. 检查AkShare
python3 -c "import akshare; print(f'AkShare版本: {akshare.__version__}')"
# 期望输出：AkShare版本: 1.17.x

# 3. 运行诊断工具
cd /Users/shishengchen/promotion/stone.github.io
python3 诊断工具.py
# 期望看到所有✅

# 4. 获取真实数据
python3 fetch_glass_futures_akshare.py
# 期望看到真实的玻璃期货数据
```

---

## 🆘 常见问题排查

### 问题1：brew install python@3.11 报权限错误

**解决：**
```bash
./快速修复权限.sh
# 然后重试安装
```

### 问题2：安装很慢或卡住

**解决：**
- 耐心等待，Homebrew需要从国外服务器下载
- 或使用方法3（pyenv）或方法4（官方安装包）

### 问题3：python3 --version 还是显示3.7

**解决：**
```bash
# 方案A：明确使用python3.11
python3.11 --version
pip3.11 install akshare pandas openpyxl
python3.11 fetch_glass_futures_akshare.py

# 方案B：修改PATH
echo 'export PATH="/usr/local/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 问题4：pip3 install akshare 失败

**解决：**
```bash
# 使用国内镜像
pip3 install akshare pandas openpyxl -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 🎓 升级前后对比

| 项目 | 升级前 (Python 3.7) | 升级后 (Python 3.11) |
|------|-------------------|---------------------|
| Python版本 | 3.7.6 | 3.11.x |
| AkShare支持 | ❌ 不支持 | ✅ 完全支持 |
| 获取真实数据 | ❌ 无法获取 | ✅ 可以获取 |
| 运行速度 | 基准 | 快25% |
| 安全更新 | ❌ 已停止 | ✅ 持续更新 |

---

## 📋 完整命令清单（复制粘贴）

```bash
# === 一键升级 ===
cd /Users/shishengchen/promotion/stone.github.io
./一键修复.sh

# === 或手动执行 ===
cd /Users/shishengchen/promotion/stone.github.io
./快速修复权限.sh
brew install python@3.11
pip3 install akshare pandas openpyxl
python3 fetch_glass_futures_akshare.py

# === 验证成功 ===
python3 --version
python3 -c "import akshare; print('✓ 成功')"
python3 诊断工具.py
```

---

## 💡 温馨提示

1. **耐心等待**：Python安装可能需要5-15分钟
2. **网络连接**：确保网络畅通
3. **输入密码**：看到提示时输入电脑密码（不会显示）
4. **验证结果**：安装后务必验证版本

---

## 🎉 升级完成后

运行这个命令获取真实的玻璃期货数据：

```bash
cd /Users/shishengchen/promotion/stone.github.io
python3 fetch_glass_futures_akshare.py
```

应该会看到：
- ✅ 真实的日期
- ✅ 真实的开盘价、收盘价
- ✅ 真实的最高价、最低价
- ✅ 真实的成交量、成交额

不再是模拟数据！📈

---

**创建时间**: 2025-11-13  
**目标**: 升级Python 3.7 → 3.11  
**用途**: 安装AkShare获取真实数据  
**状态**: ✅ 完整升级指南


