#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 AKShare 获取股票数据和技术指标
"""

import akshare as ak
import pandas as pd
from datetime import datetime

def get_stock_data(stock_code):
    """获取股票历史数据"""

    print(f"正在获取股票 {stock_code} 的数据...")

    try:
        # 获取历史数据
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            adjust="qfq"  # 前复权
        )

        print(f"✅ 成功获取 {len(df)} 条数据")
        print(f"日期范围: {df['日期'].min()} 至 {df['日期'].max()}")

        return df

    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        return None

def calculate_indicators(df):
    """计算技术指标"""

    try:
        import talib

        # MACD
        df['MACD'], df['MACD_SIGNAL'], df['MACD_HIST'] = talib.MACD(
            df['收盘'].values
        )

        # KDJ
        low = df['最低'].values
        high = df['最高'].values
        close = df['收盘'].values
        df['K'], df['D'] = talib.STOCH(high, low, close, fastk_period=9)

        # RSI
        df['RSI'] = talib.RSI(df['收盘'].values, timeperiod=14)

        # 移动平均线
        df['MA5'] = talib.MA(df['收盘'].values, timeperiod=5)
        df['MA10'] = talib.MA(df['收盘'].values, timeperiod=10)
        df['MA20'] = talib.MA(df['收盘'].values, timeperiod=20)
        df['MA60'] = talib.MA(df['收盘'].values, timeperiod=60)

        print("✅ 技术指标计算完成")

        return df

    except ImportError:
        print("⚠️  未安装 talib，跳过指标计算")
        print("   安装命令: pip install TA-Lib")
        return df
    except Exception as e:
        print(f"❌ 计算指标失败: {e}")
        return df

def analyze_stock(stock_code):
    """分析股票"""

    # 获取数据
    df = get_stock_data(stock_code)
    if df is None:
        return

    # 计算指标
    df = calculate_indicators(df)

    # 显示最新数据
    latest = df.iloc[-1]
    print(f"\n最新数据 ({latest['日期']}):")
    print(f"  开盘: {latest['开盘']:.2f}")
    print(f"  收盘: {latest['收盘']:.2f}")
    print(f"  最高: {latest['最高']:.2f}")
    print(f"  最低: {latest['最低']:.2f}")
    print(f"  成交量: {latest['成交量']:.0f}")

    # 技术指标
    if 'MACD' in df.columns:
        print(f"\n技术指标:")
        print(f"  MACD: {latest['MACD']:.4f}")
        print(f"  MACD_SIGNAL: {latest['MACD_SIGNAL']:.4f}")
        print(f"  MACD_HIST: {latest['MACD_HIST']:.4f}")

    if 'MA5' in df.columns:
        print(f"\n均线:")
        print(f"  MA5: {latest['MA5']:.2f}")
        print(f"  MA10: {latest['MA10']:.2f}")
        print(f"  MA20: {latest['MA20']:.2f}")
        print(f"  MA60: {latest['MA60']:.2f}")

    # 保存数据
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"/tmp/stock_{stock_code}_{today}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n✅ 数据已保存: {filename}")

    return df


if __name__ == "__main__":
    # 示例：分析平安银行
    stock_code = "000001"

    print("=" * 50)
    print("股票数据分析工具")
    print("=" * 50)

    df = analyze_stock(stock_code)

    print("\n" + "=" * 50)
    print("分析完成！")
    print("=" * 50)
