#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tushare Pro 稳定数据获取工具
使用说明:
1. 注册账号: https://tushare.pro/
2. 登录后获取 Token
3. 将 Token 填入下面的配置
4. 运行脚本
"""

import tushare as ts
import pandas as pd
import warnings

warnings.filterwarnings('ignore')


# ============================================================
# 配置区域
# ============================================================

# 你的 Tushare Pro Token
# 获取方式: 登录 https://tushare.pro/ → 个人中心 → API Token
TUSHARE_TOKEN = "143a0a486228bd294fb4054e1478c567d99f104a352fdcd3c31cf6cf"

# ============================================================


class TushareProData:
    """Tushare Pro 数据获取类"""

    def __init__(self, token=None):
        """
        初始化 Tushare Pro

        Args:
            token: Tushare Pro Token（如果为 None，使用配置中的 Token）
        """
        if token is None:
            token = TUSHARE_TOKEN

        if token == "请在这里填写你的Token":
            print("=" * 50)
            print("⚠️  请先配置 Tushare Pro Token！")
            print("=" * 50)
            print("\n配置步骤:")
            print("1. 访问: https://tushare.pro/")
            print("2. 注册账号（免费）")
            print("3. 登录后进入: 个人中心 → API Token")
            print("4. 复制 Token 到本脚本的 TUSHARE_TOKEN 变量")
            print("5. 重新运行脚本\n")
            self.pro = None
            return

        try:
            ts.set_token(token)
            self.pro = ts.pro_api()
            print("✓ Tushare Pro 连接成功！")
        except Exception as e:
            print(f"❌ Tushare Pro 连接失败: {e}")
            self.pro = None

    def get_daily_data(self, ts_code, start_date=None, end_date=None):
        """
        获取日线行情

        Args:
            ts_code: 股票代码（如 '600396.SH'）
            start_date: 开始日期（如 '20260101'）
            end_date: 结束日期（如 '20260326'）

        Returns:
            DataFrame
        """
        if self.pro is None:
            return None

        try:
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            return df
        except Exception as e:
            print(f"❌ 获取日线数据失败: {e}")
            return None

    def get_realtime_quote(self, ts_code_list):
        """
        获取实时行情

        Args:
            ts_code_list: 股票代码列表（如 ['600396.SH', '000001.SZ']）

        Returns:
            DataFrame
        """
        if self.pro is None:
            return None

        try:
            df = self.pro.daily(
                ts_code=','.join(ts_code_list),
                trade_date=''
            )
            return df
        except Exception as e:
            print(f"❌ 获取实时行情失败: {e}")
            return None

    def get_stock_list(self):
        """
        获取股票列表

        Returns:
            DataFrame
        """
        if self.pro is None:
            return None

        try:
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,list_date'
            )
            return df
        except Exception as e:
            print(f"❌ 获取股票列表失败: {e}")
            return None


def main():
    """测试用例"""

    print("=" * 50)
    print("Tushare Pro 数据获取工具测试")
    print("=" * 50)

    # 创建 Tushare Pro 客户端
    client = TushareProData()

    if client.pro is None:
        return

    # 测试1: 获取股票列表
    print("\n[测试1] 获取股票列表...")
    stock_list = client.get_stock_list()

    if stock_list is not None:
        print(f"✓ 成功获取 {len(stock_list)} 只股票")
        print("\n示例股票:")
        print(stock_list.head(10).to_string())

    # 测试2: 获取华电辽能数据
    print("\n[测试2] 获取华电辽能(600396.SH) 数据...")
    data = client.get_daily_data('600396.SH')

    if data is not None:
        print("✓ 数据获取成功")
        print(f"  数据量: {len(data)} 条")
        print("\n最近数据:")
        print(data.tail(5)[['trade_date', 'open', 'close', 'high', 'low', 'vol']].to_string())

    # 测试3: 获取多只股票数据
    print("\n[测试3] 获取多只股票数据...")
    symbols = ['600396.SH', '000001.SZ', '000002.SZ']
    realtime_data = client.get_realtime_quote(symbols)

    if realtime_data is not None:
        print("✓ 实时数据获取成功")
        print(realtime_data[['ts_code', 'close', 'vol', 'amount']].to_string())


if __name__ == "__main__":
    main()
