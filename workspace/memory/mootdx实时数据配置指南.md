# mootdx 实时数据配置指南

## ⚠️ 重要提示

**mootdx 本身不支持实时数据获取，它只能读取通达信本地数据。**

要配置实时数据，需要配置通达信软件的实时数据源。

---

## 📋 配置步骤

### 步骤1: 安装通达信软件

1. **下载通达信**
   - 官网: https://www.tdx.com.cn/
   - 选择「免费版」或「专业版」

2. **安装通达信**
   ```bash
   # 下载后安装到 /opt/tdx 或其他目录
   # 或者使用 Wine 在 Linux 上运行（需要额外配置）
   ```

### 步骤2: 配置通达信数据源

**如果使用 Windows**:

1. 打开通达信软件
2. 点击「工具」→「选项」
3. 找到「数据源」设置
4. 添加实时数据源（需要数据源账号）

**如果使用 Linux**:

```bash
# 1. 安装 Wine（用于运行 Windows 版通达信）
sudo apt update
sudo apt install wine

# 2. 使用 Wine 安装通达信
wine tdx_setup.exe

# 3. 配置数据源
# 在通达信中配置实时数据源
```

### 步骤3: 配置实时数据更新

1. **打开通达信**
2. **配置数据源**:
   - 点击「数据」→「数据源管理」
   - 添加实时行情数据源（如：通达信官方、第三方数据源）
   - 需要账号密码（有些免费，有些付费）

3. **启用实时更新**:
   - 点击「工具」→「自动交易」
   - 勾选「启用实时行情」
   - 设置更新频率（如：5秒）

### 步骤4: 验证数据

```python
from mootdx.quotes import Quotes

# 创建客户端
client = Quotes.factory(market='std')

# 获取实时数据
bars = client.bars(symbol='600396', frequency=0)  # 0=分时图

print(f"最新数据时间: {bars.index[-1]}")
print(f"最新价格: {bars.iloc[-1]['close']}")
```

---

## 🚨 难点和限制

### 1. 需要通达信软件

**必须安装通达信**，mootdx 只是读取工具，本身没有数据源。

### 2. 需要数据源账号

**实时数据源通常需要账号**:

| 数据源 | 免费版 | 付费版 | 实时性 |
|--------|--------|--------|--------|
| 通达信官方 | ❌ 不支持 | ✅ 支持 | 5-10秒 |
| 东方财富 | ⚠️ 部分免费 | ✅ 支持 | 10-15秒 |
| 第三方数据源 | ❌ 不支持 | ✅ 支持 | 1-3秒 |

### 3. Linux 兼容性问题

**通达信是 Windows 软件**，Linux 上需要：

```bash
# 方案1: Wine
wine 通达信.exe

# 方案2: 虚拟机
# 在 Windows 虚拟机中运行通达信

# 方案3: 远程桌面
# 在 Windows 电脑上运行通达信，Linux 远程访问数据文件
```

---

## 💡 替代方案（推荐）

### 方案1: 直接使用 AKShare（最简单）⭐⭐⭐

```python
import akshare as ak

# 实时行情
df = ak.stock_zh_a_spot_em()
stock = df[df['代码'] == '600396']
print(stock)
```

**优点**:
- ✅ 无需安装其他软件
- ✅ 真正的实时数据
- ✅ 免费

**缺点**:
- ❌ 需要网络连接

### 方案2: 混合使用

```python
# 实时数据 - AKShare
import akshare as ak
realtime = ak.stock_zh_a_spot_em()

# 离线数据 - mootdx
from mootdx.quotes import Quotes
client = Quotes.factory(market='std')
offline = client.bars(symbol='600396', frequency=9)
```

**优点**:
- ✅ 实时数据（AKShare）
- ✅ 离线分析（mootdx）
- ✅ 灵活切换

---

## 🎯 我的建议

**不推荐配置 mootdx 实时数据，原因：**

1. ❌ 需要安装通达信（复杂）
2. ❌ 需要数据源账号（可能付费）
3. ❌ Linux 兼容性差
4. ❌ 配置复杂
5. ✅ AKShare 已经能提供实时数据（免费、简单）

**推荐方案**:

| 需求 | 推荐工具 |
|------|---------|
| 实时数据 | AKShare |
| 离线分析 | mootdx |
| 混合使用 | 两个都装 |

---

## 🔗 相关资源

- 通达信官网: https://www.tdx.com.cn/
- AKShare 文档: https://akshare.akfamily.xyz/
- mootdx 文档: https://www.mootdx.com/

---

**结论**: 配置 mootdx 实时数据非常复杂，**强烈建议直接使用 AKShare**！
