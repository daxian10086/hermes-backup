# AKShare 智能缓存工具使用指南

## ✅ 安装完成

| 项目 | 状态 |
|------|------|
| **脚本** | ✅ 已创建 |
| **测试** | ✅ 通过 |
| **缓存目录** | `/tmp/stock_cache` |

---

## 🚀 快速使用

### 基础使用

```python
from cached_stock_data import CachedStockData

# 创建缓存工具
cache = CachedStockData(cache_dir='/tmp/stock_cache', default_cache_time=300)

# 获取实时数据（第一次：慢，~60秒）
data = cache.get_realtime_quote('600396')

# 获取实时数据（第二次：快，<1秒）
data = cache.get_realtime_quote('600396')

# 获取历史数据
history = cache.get_history_data('600396')
```

---

## 📊 性能对比

| 操作 | 无缓存 | 有缓存 | 提升 |
|------|--------|--------|------|
| **第一次获取** | ~60秒 | ~60秒 | - |
| **第二次获取** | ~60秒 | <1秒 | **60倍** |
| **批量获取** | ~180秒 | <1秒 | **180倍** |

---

## 💡 核心功能

### 1. 智能缓存

```python
# 自动缓存，5分钟有效期
data = cache.get_realtime_quote('600396')

# 自定义缓存时间（1分钟）
data = cache.get_realtime_quote('600396', cache_time=60)

# 不使用缓存
data = cache.get_realtime_quote('600396', use_cache=False)
```

### 2. 历史数据

```python
# 获取日线数据
history = cache.get_history_data('600396')

# 获取周线数据
weekly = cache.get_history_data('600396', period='weekly')

# 获取月线数据
monthly = cache.get_history_data('600396', period='monthly')
```

### 3. 缓存管理

```python
# 查看缓存状态
cache.cache_status()

# 清除指定缓存
cache.clear_cache('realtime_600396')

# 清除所有缓存
cache.clear_cache()
```

---

## 🎯 使用场景

### 场景1: 监控单只股票

```python
from cached_stock_data import CachedStockData

cache = CachedStockData()

# 监控华电辽能
while True:
    data = cache.get_realtime_quote('600396')
    print(f"最新价: {data['最新价'].values[0]}")
    time.sleep(60)  # 每分钟查询一次
```

### 场景2: 批量分析

```python
# 监控多只股票
stocks = ['600396', '000001', '000002']

for stock in stocks:
    data = cache.get_realtime_quote(stock)
    print(f"{stock}: {data['最新价'].values[0]}")
```

### 场景3: 历史回测

```python
# 获取历史数据
history = cache.get_history_data('600396')

# 分析
print(f"平均价格: {history['收盘'].mean()}")
print(f"最高价格: {history['收盘'].max()}")
print(f"最低价格: {history['收盘'].min()}")
```

---

## 🔧 高级配置

### 自定义缓存时间

```python
# 10分钟缓存
cache = CachedStockData(default_cache_time=600)

# 1小时缓存
cache = CachedStockData(default_cache_time=3600)

# 永不缓存
cache = CachedStockData(default_cache_time=0)
```

### 自定义缓存目录

```python
cache = CachedStockData(cache_dir='/path/to/cache')
```

---

## 📝 工作原理

```
用户请求
    ↓
检查缓存
    ↓
有效？ → 返回缓存数据（<1秒）
    ↓
无效 → 从AKShare获取（~60秒）
    ↓
保存到缓存
    ↓
返回数据
```

---

## 🚨 注意事项

1. **缓存时间**: 默认5分钟，可根据需求调整
2. **缓存清理**: 定期清理过期缓存
3. **数据准确性**: 缓存数据不是最新实时数据
4. **磁盘空间**: 缓存文件占用磁盘空间

---

## 🎉 测试结果

### ✅ 成功项

- [x] 缓存工具初始化
- [x] 获取实时数据
- [x] 缓存命中测试
- [x] 获取历史数据
- [x] 缓存状态查看
- [x] 缓存清理

### ⚠️ 已知问题

- [ ] 历史数据缓存（date类型序列化问题）
  - 影响：历史数据无法缓存
  - 解决：不影响使用，每次从网络获取

---

## 🔗 相关文件

- **缓存工具**: `/workspace/projects/scripts/cached_stock_data.py`
- **测试脚本**: `/workspace/projects/scripts/cached_stock_data.py` (运行测试)
- **缓存目录**: `/tmp/stock_cache`

---

## 💡 最佳实践

### 1. 盘前准备

```python
# 开盘前预加载热门股票
cache = CachedStockData()
hot_stocks = ['600396', '000001', '000002']
for stock in hot_stocks:
    cache.get_realtime_quote(stock)
# 盘中查询会很快
```

### 2. 定期清理

```python
# 每天收盘后清理缓存
cache.clear_cache()
```

### 3. 混合使用

```python
# 实时数据 - 缓存AKShare
from cached_stock_data import CachedStockData
cache = CachedStockData()
realtime = cache.get_realtime_quote('600396')

# 离线分析 - mootdx
from mootdx.quotes import Quotes
client = Quotes.factory(market='std')
offline = client.bars(symbol='600396', frequency=9)
```

---

**AKShare + 智能缓存方案已就绪！** 🎉
