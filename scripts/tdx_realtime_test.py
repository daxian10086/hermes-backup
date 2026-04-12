#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信实时数据获取工具
使用 tdxpy 直接连接通达信服务器
"""

from tdxpy.hq import TdxHq_API
import time

print('========================================')
print('通达信实时数据测试')
print('========================================')

# 创建 API 实例
api = TdxHq_API()

# 通达信公开服务器列表
servers = [
    ('119.147.212.81', 7709),
    ('60.12.136.250', 7709),
    ('218.108.47.69', 7709),
    ('218.108.98.244', 7709),
    ('61.152.107.141', 7709),
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
    print('提示: 通达信服务器可能不可用或网络问题')
    api.disconnect()
    exit(1)

# 测试2: 获取股票列表
print('\n[2/3] 获取股票列表...')
try:
    # 获取上海市场股票
    stocks = api.get_security_list(1, 0)  # 1=上海, 0=从0开始
    print(f'  ✓ 成功获取 {len(stocks)} 只股票')
    print('\n  示例股票:')
    for stock in stocks[:5]:
        print(f'    {stock[0]} - {stock[1]}')  # 代码, 名称
except Exception as e:
    print(f'  ❌ 获取失败: {e}')

# 测试3: 获取华电辽能实时行情
print('\n[3/3] 获取华电辽能(600396) 实时行情...')
try:
    # 获取实时行情
    # 600396 = 0x250C = 上海市场
    quotes = api.get_security_quotes([1, 0, 0x250C])
    if quotes:
        quote = quotes[0]
        print(f'  ✓ 成功获取行情数据')
        print(f'  代码: {quote[1]}')
        print(f'  名称: {quote[2]}')
        print(f'  最新价: {quote[3]/100:.2f}')
        print(f'  昨收: {quote[4]/100:.2f}')
        print(f'  今开: {quote[5]/100:.2f}')
        print(f'  最高: {quote[6]/100:.2f}')
        print(f'  最低: {quote[7]/100:.2f}')
        print(f'  成交量: {quote[10]/10000:.2f}万手')
    else:
        print('  ❌ 未获取到行情数据')
except Exception as e:
    print(f'  ❌ 获取失败: {e}')

# 断开连接
api.disconnect()

print('\n========================================')
print('测试完成')
print('========================================')
