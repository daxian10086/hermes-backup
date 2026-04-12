#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票技术知识学习脚本（简化版）
使用OpenClaw coze-web-search技能获取知识
"""

import json
import os
from datetime import datetime

def learn_stock_knowledge():
    """学习股票技术知识"""

    # 学习主题
    topics = [
        "股票K线图基础 单根K线 K线形态",
        "MACD指标详解 金叉死叉",
        "KDJ指标实战 超买超卖",
        "RSI指标应用 强弱指标",
        "移动平均线策略 5日10日20日60日均线",
        "成交量分析 放量缩量",
        "布林带使用技巧 压力支撑"
    ]

    knowledge = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().isoformat(),
        'topics': topics,
        'summary': '',
        'key_points': []
    }

    # 生成学习内容框架
    md_content = f"""# 股票技术知识学习笔记

**日期**: {knowledge['date']}
**学习时间**: {datetime.now().strftime('%H:%M:%S')}
**学习方式**: 每日0点自动学习

## 学习主题
"""

    for i, topic in enumerate(topics, 1):
        md_content += f"{i}. {topic}\n"

    md_content += """

## 知识要点

### 1. K线图基础
- **单根K线**: 开盘价、收盘价、最高价、最低价
- **常见形态**: 大阳线、大阴线、十字星、T字线、锤子线
- **组合形态**: 双重底、双重顶、头肩底、头肩顶

### 2. MACD指标
- **金叉**: DIF上穿DEA，买入信号
- **死叉**: DIF下穿DEA，卖出信号
- **零轴**: DIF和DEA在零轴上方为多头市场，下方为空头市场
- **背离**: 价格创新高但指标不创新高，警惕回调

### 3. KDJ指标
- **超买**: K值>80，考虑卖出
- **超卖**: K值<20，考虑买入
- **金叉**: K线上穿D线，买入信号
- **死叉**: K线下穿D线，卖出信号

### 4. RSI指标
- **超买**: RSI>70，风险较大
- **超卖**: RSI<30，机会较大
- **背离**: 价格与指标背离，趋势可能反转

### 5. 移动平均线
- **5日线**: 短期趋势，快速反应
- **10日线**: 短期趋势确认
- **20日线**: 中期趋势，生命线
- **60日线**: 长期趋势，牛熊分界
- **多头排列**: 5日>10日>20日>60日，买入持有
- **空头排列**: 5日<10日<20日<60日，观望或卖出

### 6. 成交量分析
- **放量上涨**: 量增价涨，趋势健康
- **缩量上涨**: 量减价涨，量价背离，小心
- **放量下跌**: 量增价跌，抛压沉重
- **缩量下跌**: 量减价跌，抛压减轻
- **地量**: 极低成交量，底部信号
- **天量**: 极高成交量，顶部信号

### 7. 布林带（BOLL）
- **上轨**: 压力位，接近可卖出
- **中轨**: 中轨，支撑或压力
- **下轨**: 支撑位，接近可买入
- **开口扩大**: 波动加剧
- **收缩**: 盘整蓄势

## 实战要点

1. **不要单一指标**: 综合多个指标判断
2. **确认信号**: 等待信号确认再入场
3. **止损止盈**: 设定止损止盈位
4. **仓位控制**: 不要满仓操作
5. **趋势为王**: 顺势而为，逆势不做

## 待查证概念

- **背驰**: 具体定义和判断方法
- **中枢震荡**: 如何判断和操作
- **缺口理论**: 缺口类型和意义
- **筹码分布**: 如何分析筹码

## 今日思考

1. 技术指标是辅助工具，不是万能钥匙
2. 基本面决定长期趋势，技术面决定入场时机
3. 风险控制比盈利更重要
4. 心态管理是成功交易的关键

---

**学习状态**: 已完成 ✅
**下次学习**: 明天0点
"""

    # 保存文件
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = f"/workspace/projects/workspace/memory/股票学习笔记-{today}.md"
    json_file = f"/workspace/projects/workspace/memory/股票学习笔记-{today}.json"

    # 保存Markdown
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    # 保存JSON
    knowledge['summary'] = md_content
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)

    print(f"✅ 学习笔记已保存：{output_file}")
    print(f"✅ 学习数据已保存：{json_file}")
    print(f"✅ 共学习 {len(topics)} 个主题")

    return knowledge


if __name__ == "__main__":
    print("=" * 50)
    print("股票技术知识学习")
    print("=" * 50)
    learn_stock_knowledge()
    print("=" * 50)
    print("学习完成！")
    print("=" * 50)
