---
name: stock-analysis
description: A股股票技术分析 - 获取实时行情和K线数据，计算均线和技术指标，给出操作建议
summary: "A股股票技术分析 - 多数据源获取K线，计算MA/支撑压力，给出操作建议"
tags: [finance, stock, china-a-share, technical-analysis]
---

# A股股票技术分析

获取A股股票实时行情和K线数据，进行技术分析，给出操作建议。

## 数据源获取顺序（失败切换）

### 1️⃣ 新浪财经API（首选）
```python
def get_sina_kline(code, count=20):
    url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz{code}&scale=240&ma=5,10,20&datalen={count}"
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'}
    # 返回JSON格式K线数据: [{day, open, close, high, low, volume}, ...]
```

### 2️⃣ 腾讯股票API（备选）
```python
def get_kline_data(code, count=20):
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param=sz{code},day,,,{count},qfq"
```

### 3️⃣ 东方财富API（备选）
```python
def get_em_kline(code, count=20):
    url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.{code}&klt=101&fqt=1&beg=20260101&end=20500101&lmt={count}"
```

### 4️⃣ 新浪实时行情（最基本）
```python
def get_stock_data(code):
    url = f"https://hq.sinajs.cn/list=sz{code}"
    # 返回格式: 名称,当前价,昨收,今开,最高,最低,...
    # 解析: fields[3]=当前价, fields[4]=最高, fields[5]=最低, fields[2]=昨收
```

## 分析框架

### 技术指标计算
- **MA均线**: 5日、10日、20日简单移动平均
- **均线排列判断**: 多头(MA5>MA10>MA20) / 空头 / 混乱
- **乖离率**: (当前价 - MA) / MA * 100%
- **日内振幅**: (最高 - 最低) / 昨收 * 100%

### K线形态分析
- 上影线 vs 实体长度 → 上涨遇阻
- 下影线 vs 实体长度 → 下方支撑
- 阴线/阳线判断
- 开盘跳空判断（>2%）

### 支撑压力位
- 第一支撑: MA5附近
- 第二支撑: MA10附近
- 第三支撑: MA20附近
- 压力位: 前期高点、整数关口

## 输出格式模板

```markdown
╔══════════════════════════════════════════════════════════════╗
║           {股票名称}({代码}) 综合分析报告                   ║
║                    数据日期: {日期}                         ║
╚══════════════════════════════════════════════════════════════╝

📊 【今日行情回顾】
   当前价: {价格} 元
   涨跌幅: {涨跌幅}%
   日内振幅: {振幅}%
   成交量: {成交量}万股

📈 【技术面分析】
   ▶ 均线系统
   ├─ MA5:  {值} → 偏离 {百分比}  {✓强势/✗弱势}
   └─ MA10: {值}
   → {均线排列结论}

🎯 【周一操作建议】
   ▶ 支撑位: {支撑1} / {支撑2}
   ▶ 压力位: {压力1} / {压力2}
   
   【具体建议】
   ① 如果周一低开: ...
   ② 如果周一高开: ...

⚠️  免责声明: 以上分析仅供参考，不构成投资建议。
```

## 关键代码片段

### 获取实时行情（最小可用）
```python
import urllib.request

def get_realtime(code):
    url = f"https://hq.sinajs.cn/list=sz{code}"
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'}
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req, timeout=10)
    data = response.read().decode('gbk')
    # 解析: fields[3]=当前价, fields[4]=最高, fields[5]=最低, 等
```

### 计算均线
```python
import pandas as pd
closes = [float(k['close']) for k in kline_data]
close_series = pd.Series(closes)
ma5 = close_series.rolling(5).mean().iloc[-1]
ma10 = close_series.rolling(10).mean().iloc[-1]
ma20 = close_series.rolling(20).mean().iloc[-1]
```

## 注意事项

- 创业板股票代码需要加 `sz` 前缀（如 sz300058）
- 沪市股票需要加 `sh` 前缀（如 sh600000）
- 新浪API返回的是日K线，scale=240表示日线
- 成交额单位需要转换：字段9是万元
- 成功获取数据后立即停止尝试其他数据源
