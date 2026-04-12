#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
华电辽能（600396）实时监控脚本
监控开盘、盘中、收盘的关键数据
"""

import sys
sys.path.insert(0, '/workspace/projects/scripts')

from cached_stock_data import CachedStockData
from mootdx.quotes import Quotes
import time
from datetime import datetime, timedelta
import json

# 配置
STOCK_CODE = '600396'
STOCK_NAME = '华电辽能'
COST_PRICE = 8.81
CURRENT_PRICE = 8.88
MONITOR_INTERVAL = 300  # 5分钟检查一次

# 通知函数（这里只是打印，实际可以发送微信通知）
def notify(message, level='INFO'):
    """
    发送通知

    Args:
        message: 通知内容
        level: INFO, WARNING, CRITICAL
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    prefix = {
        'INFO': '✅',
        'WARNING': '⚠️',
        'CRITICAL': '🚨'
    }.get(level, '📌')

    print(f'\n{prefix} [{timestamp}] {message}\n')

    # 保存到日志
    log_file = '/tmp/hualiao_monitor.log'
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] [{level}] {message}\n')

def get_market_status():
    """获取市场状态"""
    now = datetime.now()
    current_time = now.strftime('%H:%M')

    # 判断交易时段
    if current_time < '09:25':
        return '盘前'
    elif current_time < '09:30':
        return '集合竞价'
    elif current_time < '11:30':
        return '上午交易'
    elif current_time < '13:00':
        return '午休'
    elif current_time < '15:00':
        return '下午交易'
    else:
        return '收盘'

def monitor_once():
    """执行一次监控"""
    status = get_market_status()
    notify(f'{STOCK_NAME}({STOCK_CODE}) - {status}', 'INFO')

    # 获取数据
    cache = CachedStockData(cache_dir='/tmp/stock_cache', default_cache_time=60)

    try:
        # 获取实时数据
        data = cache.get_realtime_quote(STOCK_CODE, use_cache=True, cache_time=60)

        if data is not None and len(data) > 0:
            row = data.iloc[0]
            current_price = row['最新价']
            change_pct = row['涨跌幅']
            volume = row['成交量']
            turnover = row['换手率']

            # 计算盈亏
            profit_loss = (current_price - COST_PRICE) / COST_PRICE * 100

            print('='*60)
            print(f'{STOCK_NAME}({STOCK_CODE}) - {status}')
            print('='*60)
            print(f'当前价: {current_price:.2f}元')
            print(f'涨跌幅: {change_pct:+.2f}%')
            print(f'成交量: {volume:.0f}手')
            print(f'换手率: {turnover:.2f}%')
            print(f'成本价: {COST_PRICE:.2f}元')
            print(f'盈亏: {profit_loss:+.2f}%')
            print('='*60)

            # 判断是否需要预警
            warning_triggered = False

            # 1. 跌破成本价
            if current_price < COST_PRICE:
                notify(f'⚠️ 跌破成本价！当前价{current_price:.2f}元，亏损{profit_loss:.2f}%', 'WARNING')
                warning_triggered = True

            # 2. 跌幅超过3%
            if change_pct < -3:
                notify(f'⚠️ 大幅下跌！跌幅{change_pct:.2f}%，当前价{current_price:.2f}元', 'WARNING')
                warning_triggered = True

            # 3. 跌停
            if change_pct < -9:
                notify(f'🚨 跌停！跌幅{change_pct:.2f}%，当前价{current_price:.2f}元', 'CRITICAL')
                warning_triggered = True

            # 4. 涨停（检查是否在"躲监管"）
            if change_pct > 9:
                notify(f'✅ 涨停！可能是在"躲监管"，当前价{current_price:.2f}元', 'INFO')
                warning_triggered = True

            # 5. 换手率异常
            if turnover > 20:
                notify(f'⚠️ 换手率异常高！{turnover:.2f}%，主力可能在出货', 'WARNING')
                warning_triggered = True

            return {
                'time': datetime.now().strftime('%H:%M'),
                'price': current_price,
                'change_pct': change_pct,
                'volume': volume,
                'turnover': turnover,
                'profit_loss': profit_loss,
                'warning': warning_triggered
            }

        else:
            notify('未获取到数据，可能是收盘或网络问题', 'WARNING')
            return None

    except Exception as e:
        notify(f'获取数据失败: {e}', 'WARNING')
        return None

def monitor_continuous(duration_minutes=360):
    """
    持续监控

    Args:
        duration_minutes: 监控时长（分钟），默认6小时（9:30-15:30）
    """
    notify(f'开始持续监控{STOCK_NAME}({STOCK_CODE})，时长{duration_minutes}分钟', 'INFO')

    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    records = []

    while datetime.now() < end_time:
        # 获取市场状态
        status = get_market_status()

        # 如果是收盘时间，停止监控
        if status == '收盘':
            notify('收盘，停止监控', 'INFO')
            break

        # 如果是午休，跳过
        if status == '午休':
            notify('午休时间，暂停30分钟', 'INFO')
            time.sleep(1800)
            continue

        # 执行一次监控
        record = monitor_once()
        if record:
            records.append(record)

        # 等待下一次检查
        time.sleep(MONITOR_INTERVAL)

    # 生成监控报告
    if records:
        generate_report(records)

def generate_report(records):
    """生成监控报告"""
    notify(f'监控结束，共记录{len(records)}次数据', 'INFO')

    if len(records) == 0:
        return

    # 提取关键数据
    prices = [r['price'] for r in records]
    changes = [r['change_pct'] for r in records]
    volumes = [r['volume'] for r in records]

    max_price = max(prices)
    min_price = min(prices)
    max_change = max(changes)
    min_change = min(changes)
    avg_volume = sum(volumes) / len(volumes)

    last_record = records[-1]
    final_price = last_record['price']
    final_change = last_record['change_pct']
    final_profit = last_record['profit_loss']

    print('\n' + '='*60)
    print('📊 监控报告')
    print('='*60)
    print(f'最高价: {max_price:.2f}元')
    print(f'最低价: {min_price:.2f}元')
    print(f'最大涨幅: {max_change:+.2f}%')
    print(f'最大跌幅: {min_change:+.2f}%')
    print(f'平均成交量: {avg_volume:.0f}手')
    print(f'收盘价: {final_price:.2f}元')
    print(f'收盘涨跌幅: {final_change:+.2f}%')
    print(f'最终盈亏: {final_profit:+.2f}%')
    print('='*60)

    # 判断走势
    if final_change < -9:
        notify('🚨 跌停收盘！主力出货确认！', 'CRITICAL')
    elif final_change < -3:
        notify('⚠️ 大幅下跌收盘，风险很大！', 'WARNING')
    elif final_change < 0:
        notify('⚠️ 下跌收盘，不看好后续走势', 'WARNING')
    elif final_change > 9:
        notify('✅ 涨停收盘！可能在"躲监管"，但风险仍大', 'INFO')
    elif final_change > 0:
        notify('✅ 上涨收盘，但需谨慎', 'INFO')
    else:
        notify('⚠️ 平盘收盘，方向不明', 'WARNING')

    # 保存报告
    report_file = f'/tmp/hualiao_report_{datetime.now().strftime("%Y%m%d")}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'records': records,
            'summary': {
                'max_price': max_price,
                'min_price': min_price,
                'max_change': max_change,
                'min_change': min_change,
                'avg_volume': avg_volume,
                'final_price': final_price,
                'final_change': final_change,
                'final_profit': final_profit
            }
        }, f, ensure_ascii=False, indent=2)

    notify(f'报告已保存到: {report_file}', 'INFO')

def main():
    """主函数"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'once':
            # 执行一次监控
            monitor_once()
        elif command == 'monitor':
            # 持续监控
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 360
            monitor_continuous(duration_minutes=duration)
        else:
            print('用法:')
            print('  python3 hualiao_monitor.py once      # 执行一次监控')
            print('  python3 hualiao_monitor.py monitor   # 持续监控（6小时）')
            print('  python3 hualiao_monitor.py monitor 120 # 持续监控2小时')
    else:
        print('用法:')
        print('  python3 hualiao_monitor.py once      # 执行一次监控')
        print('  python3 hualiao_monitor.py monitor   # 持续监控（6小时）')
        print('  python3 hualiao_monitor.py monitor 120 # 持续监控2小时')

if __name__ == "__main__":
    main()
