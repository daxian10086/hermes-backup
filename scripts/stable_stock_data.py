#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
稳定的股票数据获取工具
支持多个数据源和自动重试
"""

import akshare as ak
import time
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')


class StableStockData:
    """稳定的股票数据获取类"""

    def __init__(self, max_retries=3, retry_delay=2):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def get_stock_data(self, symbol, data_type='history'):
        """
        获取股票数据（带重试机制）

        Args:
            symbol: 股票代码（如 '600396'）
            data_type: 数据类型（'history' 历史数据, 'realtime' 实时数据）

        Returns:
            DataFrame or None
        """

        for attempt in range(self.max_retries):
            try:
                if data_type == 'history':
                    return self._get_history_data(symbol)
                elif data_type == 'realtime':
                    return self._get_realtime_data(symbol)
                else:
                    print(f"未知数据类型: {data_type}")
                    return None

            except Exception as e:
                print(f"⚠️  尝试 {attempt + 1}/{self.max_retries} 失败: {str(e)[:50]}")

                if attempt < self.max_retries - 1:
                    print(f"   {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    print("❌ 所有尝试均失败")
                    return None

    def _get_history_data(self, symbol):
        """获取历史数据"""
        df = ak.stock_zh_a_hist(symbol=symbol, period='daily', adjust='qfq')

        # 验证数据
        if df is None or len(df) == 0:
            raise ValueError("获取的数据为空")

        return df

    def _get_realtime_data(self, symbol):
        """获取实时数据"""
        df = ak.stock_zh_a_spot_em()

        # 筛选指定股票
        stock = df[df['代码'] == symbol]

        # 验证数据
        if stock is None or len(stock) == 0:
            raise ValueError(f"未找到股票 {symbol}")

        return stock

    def get_multiple_stocks(self, symbols):
        """
        批量获取多只股票数据

        Args:
            symbols: 股票代码列表

        Returns:
            dict: {symbol: DataFrame}
        """
        results = {}

        for symbol in symbols:
            print(f"获取 {symbol} 数据...")
            data = self.get_stock_data(symbol, data_type='realtime')

            if data is not None:
                results[symbol] = data
            else:
                print(f"❌ {symbol} 数据获取失败")

        return results


def main():
    """测试用例"""

    print("=" * 50)
    print("稳定股票数据获取工具测试")
    print("=" * 50)

    # 创建稳定数据获取器
    getter = StableStockData(max_retries=3, retry_delay=2)

    # 测试1: 获取历史数据
    print("\n[测试1] 获取华电辽能(600396) 历史数据...")
    history_data = getter.get_stock_data('600396', data_type='history')

    if history_data is not None:
        print("✓ 历史数据获取成功")
        print(f"  数据量: {len(history_data)} 条")
        print(f"  最新日期: {history_data.iloc[-1]['日期']}")
        print(f"  最新价格: {history_data.iloc[-1]['收盘']}")

    # 测试2: 获取实时数据
    print("\n[测试2] 获取华电辽能(600396) 实时数据...")
    realtime_data = getter.get_stock_data('600396', data_type='realtime')

    if realtime_data is not None:
        print("✓ 实时数据获取成功")
        cols = ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量']
        available_cols = [c for c in cols if c in realtime_data.columns]
        print(realtime_data[available_cols].to_string())

    # 测试3: 批量获取
    print("\n[测试3] 批量获取多只股票数据...")
    symbols = ['600396', '000001', '000002']
    results = getter.get_multiple_stocks(symbols)

    print(f"成功获取 {len(results)}/{len(symbols)} 只股票数据")


if __name__ == "__main__":
    main()
