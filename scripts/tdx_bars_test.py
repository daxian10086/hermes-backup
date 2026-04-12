#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信实时数据 - 使用 get_security_bars
"""

from tdxpy.hq import TdxHq_API
import pandas as pd

print('========================================')
print('通达信实时数据获取（使用 security_bars）')
print('========================================')

api = TdxHq_API()

try:
    # 连接服务器
    print('\n连接通达信服务器...')
    if api.connect('119.147.212.81', 7709):
        print('✓ 连接成功')

        # 获取华电辽能的日线数据
        print('\n[测试1] 获取华电辽能(600396) 日线数据...')
        try:
            # 参数: 周期(9=日线), 市场(1=上海), 代码(600396), 起始位置(0), 数量(100)
            data = api.get_security_bars(9, 1, 600396, 0, 10)

            if data:
                print(f'✓ 成功获取 {len(data)} 条数据')
                print('\n最近5天数据:')
                for i, bar in enumerate(data[-5:]):
                    print(f'  {bar[0]} 开:{bar[1]/100:.2f} 高:{bar[2]/100:.2f} 低:{bar[3]/100:.2f} 收:{bar[4]/100:.2f}')
            else:
                print('  未获取到数据')

        except Exception as e:
            print(f'  失败: {e}')

        # 获取股票列表
        print('\n[测试2] 获取股票列表...')
        try:
            stocks = api.get_security_list(1, 0)  # 上海市场
            print(f'✓ 获取到 {len(stocks)} 只股票')
        except Exception as e:
            print(f'  失败: {e}')

        # 获取实时行情（尝试不同方法）
        print('\n[测试3] 获取实时行情...')
        try:
            # 尝试获取前几只股票
            quotes = api.get_security_bars(9, 1, 600000, 0, 1)
            if quotes:
                print(f'✓ 成功获取数据（方法: get_security_bars）')
                bar = quotes[0]
                print(f'  平安银行(600000): {bar[4]/100:.2f}')
        except Exception as e:
            print(f'  失败: {e}')

    else:
        print('✗ 连接失败')
        print('\n尝试其他服务器...')

        # 尝试其他服务器
        servers = [
            ('60.12.136.250', 7709),
            ('218.108.47.69', 7709),
        ]

        for host, port in servers:
            print(f'\n尝试 {host}:{port}...')
            if api.connect(host, port):
                print(f'✓ 连接成功！')
                # 尝试获取数据
                try:
                    data = api.get_security_bars(9, 1, 600396, 0, 5)
                    if data:
                        print(f'✓ 成功获取华电辽能数据: {len(data)}条')
                        break
                except:
                    pass
                api.disconnect()

except Exception as e:
    print(f'错误: {e}')
    import traceback
    print(traceback.format_exc())

finally:
    if hasattr(api, 'closed') and not api.closed:
        api.disconnect()

print('\n========================================')
print('测试完成')
print('========================================')
