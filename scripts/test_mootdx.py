#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mootdx 使用示例
"""

from mootdx.quotes import Quotes
import pandas as pd

def test_mootdx():
    """测试 mootdx 功能"""

    print("=" * 50)
    print("mootdx 测试")
    print("=" * 50)

    # 1. 创建客户端
    print("\n[1/3] 创建通达信客户端...")
    try:
        client = Quotes.factory(market='std')  # 标准市场
        print("✓ 客户端创建成功")
    except Exception as e:
        print(f"✗ 客户端创建失败: {e}")
        print("\n提示: mootdx 需要通达信软件和数据")
        return

    # 2. 获取股票列表
    print("\n[2/3] 获取股票列表...")
    try:
        stocks = client.stocks(market=0)  # 上海市场
        print(f"✓ 成功获取 {len(stocks)} 只股票")
        print("\n示例股票:")
        print(stocks.head(10).to_string())
    except Exception as e:
        print(f"✗ 获取股票列表失败: {e}")
        print("\n提示: 需要通达信数据文件")

    # 3. 尝试获取K线数据（需要通达信数据）
    print("\n[3/3] 尝试获取K线数据...")
    try:
        # 获取平安银行日线数据
        bars = client.bars(symbol='000001', frequency=9)  # 9=日线
        print(f"✓ 成功获取 K线数据")
        print(bars.tail(5).to_string())
    except Exception as e:
        print(f"✗ 获取K线数据失败: {e}")
        print("\n提示: 需要安装通达信软件并下载数据")

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


def compare_with_akshare():
    """与 AKShare 对比"""

    print("\n" + "=" * 50)
    print("mootdx vs AKShare 对比")
    print("=" * 50)

    print("\n| 特性 | mootdx | AKShare |")
    print("|------|--------|---------|")
    print("| 数据来源 | 通达信本地 | 网络API |")
    print("| 需要通达信 | ✅ 是 | ❌ 否 |")
    print("| 实时性 | 取决于更新 | ✅ 实时 |")
    print("| 安装复杂度 | 中等 | 简单 |")
    print("| 离线使用 | ✅ 支持 | ❌ 不支持 |")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    # 测试 mootdx
    test_mootdx()

    # 对比说明
    compare_with_akshare()

    print("\n💡 提示:")
    print("- mootdx 需要通达信软件和数据文件")
    print("- 如果没有通达信，建议使用 AKShare")
    print("- AKShare 已经安装，可以直接使用")
