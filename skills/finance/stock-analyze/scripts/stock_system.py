#!/usr/bin/env python3
"""
股票分析系统 - BaoStock核心版
以BaoStock为主要数据源
"""

import sqlite3
import requests
import json
from datetime import datetime, timedelta
import os
import sys
import time

# ==================== 配置 ====================
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'stock_analysis.db')
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# ==================== 数据库 ====================
def init_db():
    """初始化数据库"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 涨停池表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zt_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            code TEXT NOT NULL,
            name TEXT,
            pct_change REAL,
            price REAL,
            amount REAL,
            industry TEXT,
            board_count INTEGER DEFAULT 0,
            source TEXT,
            UNIQUE(date, code)
        )
    ''')
    
    # 龙虎榜表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lhb_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            code TEXT NOT NULL,
            name TEXT,
            buy_amount REAL,
            sell_amount REAL,
            net_amount REAL,
            reason TEXT,
            source TEXT,
            UNIQUE(date, code)
        )
    ''')
    
    # 情绪评分表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_score (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            total_zt INTEGER,
            zt_amount REAL,
            emotion_level TEXT,
            score INTEGER,
            top_industry TEXT
        )
    ''')
    
    # K线表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_kline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            code TEXT NOT NULL,
            name TEXT,
            open REAL, high REAL, low REAL, close REAL,
            volume INTEGER, amount REAL, pct_change REAL,
            UNIQUE(date, code)
        )
    ''')
    
    # 股票信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT,
            list_date TEXT,
            industry TEXT,
            industry_code TEXT
        )
    ''')
    
    conn.commit()
    return conn

# ==================== BaoStock 核心数据源 ====================
def login_baostock():
    """登录BaoStock"""
    import baostock as bs
    lg = bs.login()
    return lg.error_code == '0'

def logout_baostock():
    """登出BaoStock"""
    import baostock as bs
    bs.logout()

def get_stock_basic(code=None, name=None):
    """获取股票基本信息（BaoStock）
    如果不传参数，返回所有A股基本信息
    """
    import baostock as bs
    
    if not login_baostock():
        return {}
    
    rs = bs.query_stock_basic(code=code, code_name=name)
    
    data_list = []
    while rs.error_code == '0' and rs.next():
        data_list.append(rs.get_row_data())
    
    logout_baostock()
    
    if not data_list:
        return {}
    
    # 转为dict: code -> info
    result = {}
    for item in data_list:
        code_raw = item[0]
        code = code_raw.replace('sh.', '').replace('sz.', '').replace('bj.', '')
        result[code] = {
            'name': item[1],
            'list_date': item[2],
            'type': item[4] if len(item) > 4 else ''
        }
    return result

def get_stock_industry_all():
    """获取所有股票行业分类（BaoStock）- 完整版，用于sync模式"""
    import baostock as bs
    
    if not login_baostock():
        return {}
    
    rs = bs.query_stock_industry()
    
    data_list = []
    while rs.error_code == '0' and rs.next():
        data_list.append(rs.get_row_data())
    
    logout_baostock()
    
    if not data_list:
        return {}
    
    # 转为dict: code -> industry
    result = {}
    for item in data_list:
        code = item[1].replace('sh.', '').replace('sz.', '').replace('bj.', '')
        result[code] = {
            'name': item[2],
            'industry': item[3]
        }
    return result

def get_stock_industry(code):
    """获取单只股票行业分类（BaoStock）- 快速版"""
    import baostock as bs
    
    if code.startswith('6'):
        bs_code = f"sh.{code}"
    elif code.startswith('0') or code.startswith('3'):
        bs_code = f"sz.{code}"
    else:
        bs_code = code
    
    if not login_baostock():
        return {}
    
    rs = bs.query_stock_industry(code=bs_code)
    
    industry = ''
    while rs.error_code == '0' and rs.next():
        data = rs.get_row_data()
        industry = data[3] if len(data) > 3 else ''
    
    logout_baostock()
    return industry

def get_kline_data(code, days=20, frequency='d', adjustflag='3'):
    """获取K线数据（BaoStock）
    frequency: d=日k, w=周, m=月, 5=5分钟
    adjustflag: 3=后复权, 2=前复权, 1=不复权
    """
    import baostock as bs
    
    # 转换代码
    if code.startswith('6'):
        bs_code = f"sh.{code}"
    elif code.startswith('0') or code.startswith('3'):
        bs_code = f"sz.{code}"
    else:
        bs_code = code
    
    if not login_baostock():
        return None
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y-%m-%d')
    
    rs = bs.query_history_k_data_plus(
        bs_code,
        "date,code,open,high,low,close,volume,amount,pctChg",
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
        adjustflag=adjustflag
    )
    
    data_list = []
    while rs.error_code == '0' and rs.next():
        data_list.append(rs.get_row_data())
    
    logout_baostock()
    
    if data_list:
        return {
            'code': code,
            'data': data_list[-days:] if len(data_list) > days else data_list
        }
    return None

def get_realtime_data(codes):
    """获取实时行情（腾讯接口）"""
    try:
        stocks = ','.join([f"{'sh' if c.startswith('6') else 'sz'}{c}" for c in codes])
        url = f"https://qt.gtimg.cn/q={stocks}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        
        result = {}
        for line in resp.text.strip().split('\n'):
            parts = line.split('~')
            if len(parts) > 32:
                code_raw = parts[2]  # sh600519
                code = code_raw.replace('sh', '').replace('sz', '')
                result[code] = {
                    'name': parts[1],
                    'price': float(parts[3]) if parts[3] else 0,
                    'change': float(parts[31]) if parts[31] else 0,
                    'pct': float(parts[32]) if parts[32] else 0,
                    'open': float(parts[5]) if parts[5] else 0,
                    'high': float(parts[33]) if parts[33] else 0,
                    'low': float(parts[34]) if parts[34] else 0,
                    'volume': int(parts[36]) if parts[36] else 0
                }
        return result
    except Exception as e:
        print(f"  ⚠️ 腾讯实时行情失败: {e}")
    return {}

# ==================== 辅助函数 ====================
def save_stock_info(conn, info_dict, industry_dict):
    """保存股票信息"""
    cursor = conn.cursor()
    saved = 0
    for code, info in info_dict.items():
        ind_info = industry_dict.get(code, {})
        industry = ind_info.get('industry', '')
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO stock_info (code, name, list_date, industry)
                VALUES (?, ?, ?, ?)
            ''', (code, info.get('name', ''), info.get('list_date', ''), industry))
            saved += 1
        except:
            pass
    conn.commit()
    return saved

def save_kline(conn, kline_data):
    """保存K线"""
    if not kline_data:
        return 0
    
    cursor = conn.cursor()
    saved = 0
    for item in kline_data.get('data', []):
        try:
            code = item[1].replace('sh.', '').replace('sz.', '')
            cursor.execute('''
                INSERT OR REPLACE INTO stock_kline 
                (date, code, open, high, low, close, volume, amount, pct_change)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item[0], code,
                float(item[2]) if item[2] else 0,
                float(item[3]) if item[3] else 0,
                float(item[4]) if item[4] else 0,
                float(item[5]) if item[5] else 0,
                int(item[6]) if item[6] else 0,
                float(item[7]) if item[7] else 0,
                float(item[8]) if item[8] else 0
            ))
            saved += 1
        except:
            pass
    conn.commit()
    return saved

def save_zt_pool(conn, date_str, zt_list):
    """保存涨停池"""
    cursor = conn.cursor()
    saved = 0
    for item in zt_list:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO zt_pool 
                (date, code, name, pct_change, price, amount, industry, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                date_str,
                item.get('code', ''),
                item.get('name', ''),
                item.get('pct', 0),
                item.get('price', 0),
                item.get('amount', 0),
                item.get('industry', ''),
                item.get('source', 'baostock')
            ))
            saved += 1
        except:
            pass
    conn.commit()
    return saved

def calculate_emotion(zt_count):
    """计算情绪"""
    if zt_count >= 100:
        return ("高潮", 90)
    elif zt_count >= 60:
        return ("活跃", 75)
    elif zt_count >= 30:
        return ("平稳", 60)
    elif zt_count >= 10:
        return ("低迷", 40)
    else:
        return ("冰点", 20)

def generate_report(conn):
    """生成早报"""
    cursor = conn.cursor()
    
    # 最新情绪
    cursor.execute('SELECT * FROM emotion_score ORDER BY date DESC LIMIT 1')
    emotion = cursor.fetchone()
    
    # 涨停龙头
    cursor.execute('''
        SELECT name, code, pct_change, industry 
        FROM zt_pool 
        WHERE date = (SELECT MAX(date) FROM zt_pool)
        ORDER BY pct_change DESC
        LIMIT 8
    ''')
    leaders = cursor.fetchall()
    
    # 近期K线（示范股票）
    cursor.execute('''
        SELECT code, name, close, 0 as pct_change 
        FROM stock_kline 
        WHERE date = (SELECT MAX(date) FROM stock_kline)
        ORDER BY close DESC
        LIMIT 5
    ''')
    hot_stocks = cursor.fetchall()
    
    report = f"""
{'='*50}
📊 每日股票早报 - {datetime.now().strftime('%Y-%m-%d')}
{'='*50}

📈 市场情绪
"""
    if emotion:
        report += f"   {emotion[3]}: {emotion[4]}分\n"
        report += f"   涨停家数: {emotion[2]}\n"
        report += f"   强势板块: {emotion[5] or '待观察'}\n"
    
    report += "\n🔥 涨停龙头\n"
    if leaders:
        for name, code, pct, industry in leaders:
            ind = industry[:10] if industry else '其他'
            report += f"   {name}({code}): {pct:.2f}% [{ind}]\n"
    else:
        report += "   暂无数据\n"
    
    report += "\n📉 热门股票\n"
    if hot_stocks:
        for code, name, close, pct in hot_stocks:
            sign = '+' if pct > 0 else ''
            report += f"   {name}({code}): {close:.2f} {sign}{pct:.2f}%\n"
    else:
        report += "   暂无数据\n"
    
    report += f"""
{'='*50}
⚠️ 仅供参考，不构成投资建议
{'='*50}
"""
    return report

# ==================== 主程序 ====================
def main():
    import argparse
    parser = argparse.ArgumentParser(description='股票分析系统 - BaoStock核心版')
    parser.add_argument('--mode', default='all', 
                        choices=['all', 'info', 'zt', 'kline', 'report', 'emotion', 'sync'])
    parser.add_argument('--code', default=None, help='股票代码')
    parser.add_argument('--days', default=20, type=int, help='K线天数')
    args = parser.parse_args()
    
    print(f"\n{'='*50}")
    print(f"📊 股票分析系统 - BaoStock核心版")
    print(f"{'='*50}")
    
    conn = init_db()
    
    if args.mode == 'sync':
        """同步所有股票基本信息和行业"""
        print("🔄 同步股票基本信息和行业...")
        
        print("  → 获取股票基本信息...")
        basic_info = get_stock_basic_all()
        print(f"    ✅ 获取 {len(basic_info)} 只股票")
        
        print("  → 获取行业分类...")
        industry_info = get_stock_industry_all()
        print(f"    ✅ 获取 {len(industry_info)} 个行业")
        
        print("  → 保存到数据库...")
        saved = save_stock_info(conn, basic_info, industry_info)
        print(f"    ✅ 保存 {saved} 条")
    
    elif args.mode == 'info':
        """查询股票信息"""
        code = args.code or '600519'
        print(f"📋 查询 {code} 信息...")
        
        # 基本信息
        print("\n基本信息和行业:")
        industry = get_stock_industry(code)
        if industry:
            print(f"  行业: {industry}")
        else:
            print("  未找到行业信息")
        
        # K线
        print("\n📈 最近K线:")
        kline = get_kline_data(code, days=5)
        if kline:
            for item in kline['data']:
                print(f"  {item[0]}: 开{item[2]} 高{item[3]} 低{item[4]} 收{item[5]} 涨跌{item[8]}%")
    
    elif args.mode == 'kline':
        """获取K线"""
        code = args.code or '000001'
        print(f"📈 获取 {code} K线（{args.days}天）...")
        
        kline = get_kline_data(code, days=args.days)
        if kline:
            saved = save_kline(conn, kline)
            print(f"✅ 保存 {saved} 条K线")
            
            print("\n最近5天:")
            for item in kline['data'][-5:]:
                print(f"  {item[0]}: 收{item[5]} 涨跌{item[8]}%")
        else:
            print("❌ 获取失败")
    
    elif args.mode == 'zt':
        """采集涨停池"""
        date_str = datetime.now().strftime('%Y%m%d')
        print("📈 采集涨停池...")
        
        # 获取所有涨停股（涨幅>=9.9%）
        # 通过腾讯接口获取全部A股，然后筛选
        print("  → 获取实时行情...")
        all_codes = list(get_stock_basic_all().keys())[:500]  # 先取500只测试
        
        realtime = get_realtime_data(all_codes[:50])
        print(f"    ✅ 获取 {len(realtime)} 只实时数据")
        
        # 筛选涨停
        zt_list = []
        for code, data in realtime.items():
            if data.get('pct', 0) >= 9.9:
                industry_info = get_stock_industry_all()
                ind = industry_info.get(code, {}).get('industry', '其他')
                zt_list.append({
                    'code': code,
                    'name': data.get('name', ''),
                    'pct': data.get('pct', 0),
                    'price': data.get('price', 0),
                    'industry': ind,
                    'source': 'tencent+baostock'
                })
        
        if zt_list:
            saved = save_zt_pool(conn, date_str, zt_list)
            print(f"✅ 保存 {saved} 只涨停股")
            
            # 情绪
            level, score = calculate_emotion(len(zt_list))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO emotion_score (date, total_zt, emotion_level, score)
                VALUES (?, ?, ?, ?)
            ''', (date_str, len(zt_list), level, score))
            conn.commit()
            print(f"📊 情绪: {level} ({score}分)")
        else:
            print("⚠️ 今日无涨停")
    
    elif args.mode == 'emotion':
        """计算情绪"""
        date_str = datetime.now().strftime('%Y%m%d')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM zt_pool WHERE date = ?', (date_str,))
        count = cursor.fetchone()[0]
        
        level, score = calculate_emotion(count)
        cursor.execute('''
            INSERT OR REPLACE INTO emotion_score (date, total_zt, emotion_level, score)
            VALUES (?, ?, ?, ?)
        ''', (date_str, count, level, score))
        conn.commit()
        print(f"✅ 情绪: {level} ({score}分) | 涨停: {count}家")
    
    elif args.mode == 'report':
        """生成早报"""
        print(generate_report(conn))
    
    elif args.mode == 'all':
        """完整流程"""
        date_str = datetime.now().strftime('%Y%m%d')
        
        # 1. 同步股票信息
        print("\n🔄 同步股票信息...")
        basic_info = get_stock_basic_all()
        industry_info = get_stock_industry_all()
        save_stock_info(conn, basic_info, industry_info)
        print(f"  ✅ {len(basic_info)} 只股票已同步")
        
        # 2. 获取示例K线
        print("\n📈 获取热门股票K线...")
        sample_codes = ['000001', '600519', '600036', '000002', '600276']
        for code in sample_codes:
            kline = get_kline_data(code, days=5)
            if kline:
                save_kline(conn, kline)
                print(f"  ✅ {code} K线已保存")
        
        # 3. 生成报告
        print("\n📋 生成早报:")
        print(generate_report(conn))
    
    conn.close()
    print(f"\n✅ 完成!")

if __name__ == '__main__':
    main()
