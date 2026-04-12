---
name: stock-analyze
description: 股票分析Skill - 基于BaoStock的A股数据分析工具。当用户询问股票行情、K线数据、涨停板、龙虎榜、市场情绪、板块分析、个股技术分析、股票代码、行业分类、每日早报，或需要获取A股实时/历史数据时触发。支持获取实时行情、历史K线、涨停池数据、龙虎榜信息、行业分类、市场情绪评分等。
---

# 📈 股票分析 Skill

## 核心数据源

| 数据源 | 用途 | 优先级 | 说明 |
|--------|------|--------|------|
| **腾讯财经** | 实时行情 | ⭐首选 | 盘口、买卖5档、实时价格 |
| **BaoStock** | K线、历史数据 | ⭐首选 | 技术分析、均线计算 |
| **新浪财经** | 实时行情 | 备用 | 辅助验证 |

### 推荐组合：腾讯实时 + BaoStock历史

```python
# 腾讯财经 - 实时行情（盘口、买卖档位）
https://hq.sinajs.cn/list=sz300058

# BaoStock - 历史K线（均线、技术指标）
import baostock as bs
bs.query_history_k_data_plus("sz.300058", ...)
```

## 快速使用

### 1. 安装依赖
```bash
pip install baostock -q
```

### 2. 查询股票信息和K线
```bash
python3 ~/.hermes/skills/finance/stock-analyze/scripts/stock_system.py --mode=info --code=300058
```

### 3. 获取K线数据
```bash
python3 ~/.hermes/skills/finance/stock-analyze/scripts/stock_system.py --mode=kline --code=300058 --days=10
```

### 4. 同步股票信息（行业分类）
```bash
python3 ~/.hermes/skills/finance/stock-analyze/scripts/stock_system.py --mode=sync
```

### 5. 采集涨停池
```bash
python3 ~/.hermes/skills/finance/stock-analyze/scripts/stock_system.py --mode=zt
```

### 6. 生成早报
```bash
python3 ~/.hermes/skills/finance/stock-analyze/scripts/stock_system.py --mode=report
```

## 脚本参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--mode` | 运行模式 | info/kline/zt/report/sync/emotion/lhb |
| `--code` | 股票代码 | 600519/300058 |
| `--days` | K线天数 | 5/10/20 |

## 数据库

- 路径: `~/.hermes/skills/finance/stock-analyze/data/stock_analysis.db`
- 表: zt_pool, lhb_data, emotion_score, stock_kline, stock_info

## 定时任务（Crontab）

```bash
# 16:00 收盘 - 采集涨停池
0 16 * * 1-5 python3 ~/.hermes/skills/finance/stock-analyze/scripts/stock_system.py --mode=zt

# 17:00 龙虎榜
0 17 * * 1-5 python3 ~/.hermes/skills/finance/stock-analyze/scripts/stock_system.py --mode=lhb

# 18:30 情绪评分
30 18 * * 1-5 python3 ~/.hermes/skills/finance/stock-analyze/scripts/stock_system.py --mode=emotion

# 08:30 早报
30 8 * * 1-5 python3 ~/.hermes/skills/finance/stock-analyze/scripts/stock_system.py --mode=report
```

## BaoStock 常用接口

```python
import baostock as bs

# 登录
bs.login()

# 股票基本信息
rs = bs.query_stock_basic(code="sh.600519")

# 行业分类
rs = bs.query_stock_industry()

# K线数据
rs = bs.query_history_k_data_plus(
    "sz.300058",
    "date,code,open,high,low,close,volume,amount,pctChg",
    start_date='2026-01-01',
    end_date='2026-04-10',
    frequency="d",
    adjustflag="3"  # 3=后复权
)

# 登出
bs.logout()
```

## 股票代码规则

| 前缀 | 市场 | 示例 |
|------|------|------|
| sh. | 上海主板 | sh.600519 (茅台) |
| sz. | 深圳主板 | sz.000001 (平安) |
| sz. | 创业板 | sz.300058 (蓝色光标) |
| bj. | 北交所 | bj.833171 |

## 注意事项

1. **BaoStock 是免费开源的证券数据平台，无需注册**
2. BaoStock 行业分类返回证监会行业代码（如 C27 医药制造业）
3. K线数据默认获取后复权数据
4. BaoStock 查询有时间限制，大数据量查询可能超时
5. 实时行情建议用新浪/腾讯财经 API

## 使用示例

### 查询蓝色光标
```
--mode=info --code=300058
```

### 获取近期K线
```
--mode=kline --code=300058 --days=20
```

### 生成每日早报
```
--mode=report
```
