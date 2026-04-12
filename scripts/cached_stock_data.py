#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AKShare 智能缓存工具
解决 AKShare 实时数据接口慢的问题
"""

import akshare as ak
import json
import time
import os
from datetime import datetime
from functools import wraps
import warnings
import pandas as pd

warnings.filterwarnings('ignore')


class CachedStockData:
    """智能缓存的股票数据获取类"""

    def __init__(self, cache_dir='/tmp/stock_cache', default_cache_time=300):
        """
        初始化缓存工具

        Args:
            cache_dir: 缓存目录
            default_cache_time: 默认缓存时间（秒），默认5分钟
        """
        self.cache_dir = cache_dir
        self.default_cache_time = default_cache_time

        # 创建缓存目录
        os.makedirs(cache_dir, exist_ok=True)

        print(f"✓ 缓存工具初始化完成")
        print(f"  缓存目录: {cache_dir}")
        print(f"  默认缓存时间: {default_cache_time}秒")

    def _get_cache_file(self, cache_key):
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f'{cache_key}.json')

    def _load_cache(self, cache_key, cache_time=None):
        """
        从缓存加载数据

        Args:
            cache_key: 缓存键
            cache_time: 缓存时间（秒），None=使用默认

        Returns:
            数据或 None
        """
        if cache_time is None:
            cache_time = self.default_cache_time

        cache_file = self._get_cache_file(cache_key)

        try:
            if not os.path.exists(cache_file):
                return None

            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)

            # 检查是否过期
            if time.time() - cache['timestamp'] > cache_time:
                return None

            print(f"✓ 使用缓存数据 ({cache_key})")
            # 转换为DataFrame
            data = cache['data']
            if isinstance(data, list):
                return pd.DataFrame(data)
            return data

        except Exception as e:
            print(f"⚠️  读取缓存失败: {e}")
            return None

    def _save_cache(self, cache_key, data):
        """
        保存数据到缓存

        Args:
            cache_key: 缓存键
            data: 要缓存的数据
        """
        cache_file = self._get_cache_file(cache_key)

        try:
            cache = {
                'timestamp': time.time(),
                'data': data
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)

            print(f"✓ 数据已缓存 ({cache_key})")

        except Exception as e:
            print(f"⚠️  保存缓存失败: {e}")

    def get_realtime_quote(self, symbol, use_cache=True, cache_time=None):
        """
        获取实时行情（带缓存）

        Args:
            symbol: 股票代码（如 '600396'）
            use_cache: 是否使用缓存
            cache_time: 缓存时间（秒）

        Returns:
            DataFrame
        """
        cache_key = f'realtime_{symbol}'

        # 尝试从缓存读取
        if use_cache:
            cached_data = self._load_cache(cache_key, cache_time)
            if cached_data is not None:
                return cached_data

        # 缓存未命中，从网络获取
        print(f"⏳ 从网络获取实时数据 ({symbol})...")
        try:
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == symbol]

            if stock is None or len(stock) == 0:
                print(f"❌ 未找到股票 {symbol}")
                return None

            # 返回原始DataFrame
            # 保存到缓存
            if use_cache:
                stock_data = stock.to_dict('records')
                self._save_cache(cache_key, stock_data)

            return stock

        except Exception as e:
            print(f"❌ 获取数据失败: {e}")
            return None

    def get_history_data(self, symbol, use_cache=True, cache_time=None, period='daily'):
        """
        获取历史数据（带缓存）

        Args:
            symbol: 股票代码
            use_cache: 是否使用缓存
            cache_time: 缓存时间（秒）
            period: 周期（daily, weekly, monthly）

        Returns:
            DataFrame
        """
        cache_key = f'history_{symbol}_{period}'

        # 尝试从缓存读取
        if use_cache:
            cached_data = self._load_cache(cache_key, cache_time)
            if cached_data is not None:
                return cached_data

        # 缓存未命中，从网络获取
        print(f"⏳ 从网络获取历史数据 ({symbol})...")
        try:
            df = ak.stock_zh_a_hist(symbol=symbol, period=period, adjust='qfq')

            if df is None or len(df) == 0:
                print(f"❌ 未获取到数据 {symbol}")
                return None

            # 保存到缓存
            if use_cache:
                data = df.to_dict('records')
                self._save_cache(cache_key, data)

            return df

        except Exception as e:
            print(f"❌ 获取数据失败: {e}")
            return None

    def clear_cache(self, cache_key=None):
        """
        清除缓存

        Args:
            cache_key: 缓存键，None=清除所有
        """
        if cache_key:
            # 清除指定缓存
            cache_file = self._get_cache_file(cache_key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                print(f"✓ 已清除缓存 ({cache_key})")
        else:
            # 清除所有缓存
            files = os.listdir(self.cache_dir)
            for file in files:
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
            print(f"✓ 已清除所有缓存 ({len(files)}个文件)")

    def cache_status(self):
        """显示缓存状态"""
        files = os.listdir(self.cache_dir)
        print(f"\n缓存状态:")
        print(f"  缓存目录: {self.cache_dir}")
        print(f"  缓存文件数: {len(files)}")

        if files:
            print(f"\n缓存列表:")
            for file in files:
                cache_file = os.path.join(self.cache_dir, file)
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache = json.load(f)
                    age = time.time() - cache['timestamp']
                    print(f"  {file}: {age:.0f}秒前")
                except:
                    print(f"  {file}: 读取失败")


def main():
    """测试用例"""

    print("=" * 60)
    print("AKShare 智能缓存工具测试")
    print("=" * 60)

    # 创建缓存工具
    cache = CachedStockData(cache_dir='/tmp/stock_cache', default_cache_time=300)

    # 测试1: 获取实时数据（第一次，从网络）
    print("\n[测试1] 获取华电辽能(600396) 实时数据（第一次）...")
    data1 = cache.get_realtime_quote('600396')

    if data1 is not None:
        print("✓ 数据获取成功")
        cols = ['代码', '名称', '最新价', '涨跌幅', '成交量']
        available_cols = [c for c in cols if c in data1.columns]
        print(data1[available_cols].to_string())

    # 测试2: 获取实时数据（第二次，从缓存）
    print("\n[测试2] 获取华电辽能(600396) 实时数据（第二次，应该从缓存）...")
    data2 = cache.get_realtime_quote('600396')

    if data2 is not None:
        print("✓ 数据获取成功（应该很快）")
        print(data2[available_cols].to_string())

    # 测试3: 获取历史数据
    print("\n[测试3] 获取华电辽能(600396) 历史数据...")
    history = cache.get_history_data('600396')

    if history is not None:
        print(f"✓ 成功获取 {len(history)} 条历史数据")
        print(history.tail(3)[['日期', '开盘', '收盘', '成交量']].to_string())

    # 测试4: 查看缓存状态
    print("\n[测试4] 查看缓存状态...")
    cache.cache_status()

    # 测试5: 清除缓存
    print("\n[测试5] 清除缓存...")
    cache.clear_cache('realtime_600396')

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
