#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信实时数据获取 - 简化版
"""

from tdxpy.hq import TdxHq_API

print('========================================')
print('通达信实时数据测试')
print('========================================')

api = TdxHq_API()

try:
    # 连接服务器
    print('\n连接通达信服务器...')
    if api.connect('119.147.212.81', 7709):
        print('✓ 连接成功')

        # 方法1: 获取股票列表
        print('\n[测试1] 获取股票列表...')
        stocks = api.get_security_list(1, 0)  # 上海市场
        print(f'✓ 获取到 {len(stocks)} 只股票')

        # 显示前5只
        print('\n前5只股票:')
        for i in range(min(5, len(stocks))):
            stock = stocks[i]
            print(f'  {stock[0]} - {stock[1]}')

        # 方法2: 获取行情数据
        print('\n[测试2] 获取前20只股票行情...')
        # 构造股票代码列表 [(市场, 代码), ...]
        stock_codes = [(1, 600000), (1, 600001), (1, 600002), (1, 600003), (1, 600004)]

        try:
            quotes = api.get_security_quotes(stock_codes)
            if quotes:
                print(f'✓ 获取到 {len(quotes)} 只股票行情')
                for quote in quotes:
                    print(f'  {quote[1]} - {quote[2]}: {quote[3]/100:.2f}')
        except Exception as e:
            print(f'  获取行情失败: {e}')

        # 方法3: 获取华电辽能
        print('\n[测试3] 获取华电辽能(600396)...')
        try:
            quote = api.get_security_quotes([(1, 600396)])
            if quote and len(quote) > 0:
                q = quote[0]
                print(f'✓ 获取成功:')
                print(f'  代码: {q[1]}')
                print(f'  名称: {q[2]}')
                print(f'  最新价: {q[3]/100:.2f}')
            else:
                print('  未获取到数据')
        except Exception as e:
            print(f'  失败: {e}')

    else:
        print('✗ 连接失败')

except Exception as e:
    print(f'错误: {e}')
    import traceback
    print(traceback.format_exc())

finally:
    api.disconnect()

print('\n========================================')
