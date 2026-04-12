# AKShare 使用指南

## 1. 安装

```bash
pip install akshare
```

## 2. 主要功能

### 2.1 股票历史数据

```python
import akshare as ak

# 获取A股历史数据
df = ak.stock_zh_a_hist(
    symbol="000001",  # 股票代码
    period="daily",   # 周期: daily, weekly, monthly
    start_date="20240101",
    end_date="20241231",
    adjust="qfq"      # 复权: qfq前复权, hfq后复权, ""不复权
)
print(df)
```

### 2.2 实时行情

```python
# 实时行情
df = ak.stock_zh_a_spot_em()
print(df.head())

# 单个股票实时行情
df = ak.stock_zh_a_spot()
print(df[df['代码'] == '000001'])
```

### 2.3 技术指标

```python
# 需要安装 TA-Lib
# pip install TA-Lib

import talib

# 假设 df 已经有收盘价数据
df['MACD'], df['MACD_SIGNAL'], df['MACD_HIST'] = talib.MACD(df['收盘'])
df['K'], df['D'] = talib.STOCH(df['最高'], df['最低'], df['收盘'])
df['RSI'] = talib.RSI(df['收盘'])
df['MA5'] = talib.MA(df['收盘'], timeperiod=5)
df['MA10'] = talib.MA(df['收盘'], timeperiod=10)
```

### 2.4 指数数据

```python
# 上证指数
df = ak.index_zh_a_hist(symbol="000001")

# 深证成指
df = ak.index_zh_a_hist(symbol="399001")

# 创业板指
df = ak.index_zh_a_hist(symbol="399006")
```

### 2.5 资金流向

```python
# 个股资金流向
df = ak.stock_individual_fund_flow_rank(indicator="今日")

# 板块资金流向
df = ak.stock_sector_fund_flow_rank(symbol="今日", indicator="今日")
```

### 2.6 涨跌停

```python
# 涨停板
df = ak.stock_zt_pool_em(date="20240326")

# 跌停板
df = ak.stock_dt_pool_em(date="20240326")
```

### 2.7 龙虎榜

```python
# 龙虎榜数据
df = ak.stock_lhb_detail_daily_em(date="20240326")
```

### 2.8 财务数据

```python
# 财务报表
df = ak.stock_financial_analysis_indicator(symbol="000001")

# 业绩预告
df = ak.stock_yjbb_em()
```

## 3. 常用股票代码

| 代码 | 名称 |
|------|------|
| 000001 | 平安银行 |
| 000002 | 万科A |
| 600000 | 浦发银行 |
| 600036 | 招商银行 |
| 600519 | 贵州茅台 |
| 000858 | 五粮液 |

## 4. 注意事项

1. **无需API Key**: AKShare 完全免费，不需要注册
2. **数据来源**: 东方财富、新浪财经等公开数据
3. **使用限制**: 请遵守网站使用条款，避免频繁请求
4. **数据延迟**: 免费数据可能有延迟
5. **仅供学习**: 不构成投资建议

## 5. 示例代码

```python
import akshare as ak

# 获取最近100天的数据
df = ak.stock_zh_a_hist(symbol="000001", period="daily")

# 保存到CSV
df.to_csv("stock_data.csv", index=False, encoding='utf-8-sig')

# 计算简单指标
df['MA5'] = df['收盘'].rolling(5).mean()
df['MA10'] = df['收盘'].rolling(10).mean()
df['MA20'] = df['收盘'].rolling(20).mean()

# 金叉死叉
df['金叉'] = (df['MA5'] > df['MA10']) & (df['MA5'].shift(1) <= df['MA10'].shift(1))
df['死叉'] = (df['MA5'] < df['MA10']) & (df['MA5'].shift(1) >= df['MA10'].shift(1))

print(df.tail(10))
```

## 6. 参考文档

- 官方文档: https://akshare.akfamily.xyz/
- GitHub: https://github.com/akfamily/akshare
- 数据接口: https://akshare.akfamily.xyz/data/stock/stock.html
