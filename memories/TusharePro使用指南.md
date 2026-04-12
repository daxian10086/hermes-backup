# Tushare Pro 使用指南

## 📋 安装状态

✅ Tushare 已安装（版本 1.4.25）
⚠️ 需要配置 Token 才能使用

---

## 🔧 配置步骤

### 步骤1: 注册账号（免费）

1. 访问: https://tushare.pro/
2. 点击右上角「注册」
3. 填写信息完成注册（免费）

### 步骤2: 获取 Token

1. 登录账号
2. 点击右上角「个人中心」
3. 找到「API Token」
4. 复制 Token（一长串字符）

### 步骤3: 配置 Token

编辑配置文件：

```bash
# 方式1: 编辑脚本
nano /workspace/projects/scripts/tushare_pro_test.py

# 找到这一行:
# TUSHARE_TOKEN = "请在这里填写你的Token"

# 替换为:
# TUSHARE_TOKEN = "你复制的Token"
```

或者创建环境变量：

```bash
# 添加到 ~/.bashrc
echo 'export TUSHARE_TOKEN="你的Token"' >> ~/.bashrc
source ~/.bashrc
```

---

## 📊 使用示例

### 基础使用

```python
import tushare as ts

# 设置 Token
ts.set_token('你的Token')

# 创建 Pro API
pro = ts.pro_api()

# 获取日线数据
df = pro.daily(ts_code='600396.SH', start_date='20260101', end_date='20260326')
print(df)
```

### 获取股票列表

```python
# 获取所有上市股票
df = pro.stock_basic(exchange='', list_status='L')
print(df)
```

### 获取实时行情

```python
# 获取多只股票数据
symbols = ['600396.SH', '000001.SZ', '000002.SZ']
df = pro.daily(ts_code=','.join(symbols))
print(df)
```

---

## 🚀 测试脚本

我已经创建了测试脚本，配置完 Token 后运行：

```bash
python3 /workspace/projects/scripts/tushare_pro_test.py
```

**测试内容**:
- ✅ 连接测试
- ✅ 获取股票列表
- ✅ 获取华电辽能数据
- ✅ 获取多只股票数据

---

## 💡 Tushare Pro 优势

| 特性 | Tushare Pro | AKShare |
|------|-------------|---------|
| **稳定性** | ✅ 很稳定 | ⚠️ 中等 |
| **速度** | ✅ 快 | ⚠️ 慢 |
| **数据质量** | ✅ 高 | ✅ 高 |
| **免费额度** | ⚠️ 有限制 | ✅ 完全免费 |
| **文档** | ✅ 完善 | ✅ 完善 |
| **官方支持** | ✅ 有 | ❌ 无 |

---

## 📝 免费额度说明

Tushare Pro 免费账号的限制：

- 每分钟请求次数: 200次
- 每天请求次数: 2000次
- 数据范围: 部分数据需要积分

**对于你的使用场景，免费额度完全够用！**

---

## 🎯 使用建议

### 场景1: 日常数据获取
```python
import tushare as ts

ts.set_token('你的Token')
pro = ts.pro_api()

# 获取历史数据
df = pro.daily(ts_code='600396.SH', start_date='20260101')
```

### 场景2: 批量分析
```python
# 获取股票列表
stock_list = pro.stock_basic(list_status='L')

# 遍历分析
for code in stock_list['ts_code'][:10]:  # 前10只
    df = pro.daily(ts_code=code)
    print(f"{code}: {len(df)} 条数据")
```

### 场景3: 混合使用
```python
# Tushare Pro（稳定数据）
pro_data = pro.daily(ts_code='600396.SH')

# AKShare（实时数据）
import akshare as ak
ak_data = ak.stock_zh_a_spot_em()
```

---

## 📚 参考文档

- 官网: https://tushare.pro/
- 文档: https://tushare.pro/document/1
- API 文档: https://tushare.pro/document/2

---

## ⚡ 快速开始

```bash
# 1. 运行测试脚本（配置 Token 后）
python3 /workspace/projects/scripts/tushare_pro_test.py

# 2. 如果需要配置 Token，编辑脚本
nano /workspace/projects/scripts/tushare_pro_test.py

# 3. 找到这一行并替换
# TUSHARE_TOKEN = "请在这里填写你的Token"
```

---

## 🔗 相关文件

- **测试脚本**: `/workspace/projects/scripts/tushare_pro_test.py`
- **配置说明**: 本文档

---

**配置完 Token 后，Tushare Pro 就可以使用了！** 🎯

需要我帮你配置 Token 吗？还是你自己去注册？
