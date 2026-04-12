#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信实时数据获取工具（修正版）
"""

from tdxpy.hq import TdxHq_API
import time

print('========================================')
print('通达信实时数据测试（修正版）')
print('========================================')

# 创建 API 实例
api = TdxHq_API()

# 通达信公开服务器列表
servers = [
    ('119.147.212.81', 7709),
    ('60.12.136.250', 7709),
    ('218.108.47.69', 7709),
]

print('\n[1/3] 连接通达信服务器...')
connected = False
for host, port in servers:
    try:
        print(f'  尝试连接 {host}:{port}...')
        if api.connect(host, port):
            print(f'  ✓ 连接成功！')
            connected = True
            break
    except Exception as e:
        print(f'  ✗ 连接失败: {str(e)[:30]}')
        time.sleep(0.5)

if not connected:
    print('\n❌ 所有服务器连接失败')
    api.disconnect()
    exit(1)

# 测试2: 获取市场行情（所有股票）
print('\n[2/3] 获取市场行情...')
try:
    # 获取上海市场最新行情
    # 使用 get_security_quotes 获取多只股票的实时行情
    # 上海市场前10只股票
    sh_stocks = [1, 0, 1] + [0]*10  # 格式: [市场, 起始位置, 数量]

    # 或者使用 get_security_list 获取股票列表
    stock_list = api.get_security_list(1, 0)  # 1=上海, 0=从0开始
    print(f'  ✓ 成功获取 {len(stock_list)} 只股票')

    # 显示前5只股票
    print('\n  前5只股票:')
    for i, stock in enumerate(stock_list[:5]):
        if isinstance(stock, dict):
            code = stock.get("code", "N/A")
            name = stock.get("name", "N/A")
            print(f'    {code} - {name}')
        elif len(stock) >= 2:
            print(f'    {stock[0]} - {stock[1]}')

except Exception as e:
    print(f'  ❌ 获取失败: {e}')
    print(f'  错误详情: {type(e).__name__}')

# 测试3: 获取特定股票行情
print('\n[3/3] 获取华电辽能(600396) 实时行情...')
try:
    # 通达信股票编码：
    # 市场代码: 1=上海, 0=深圳
    # 600396 = 0x250C (十六进制)

    # 方法1: 使用 get_security_quotes
    # 格式: [市场, 代码]
    code = 0x250C  # 600396
    quotes = api.get_security_quotes([(1, code)])

    if quotes and len(quotes) > 0:
        quote = quotes[0]
        print(f'  ✓ 成功获取行情数据')

        # 解析数据字段
        print(f'\n  详细数据:')
        print(f'    数据类型: {type(quote)}')
        print(f'    数据长度: {len(quote)}')
        print(f'    数据内容: {quote}')

    else:
        print('  ❌ 未获取到行情数据')

except Exception as e:
    print(f'  ❌ 获取失败: {e}')
    import traceback
    print(f'  堆栈: {traceback.format_exc()}')

# 断开连接
api.disconnect()

print('\n========================================')
print('测试完成')
print('========================================')
