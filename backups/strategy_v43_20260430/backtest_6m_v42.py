#!/usr/bin/env python3
"""
大仙三步模式 v4.3 回测 (2025.11 - 2026.04)
═══════════════════════════════════════════════
v4.3 改动:
  1. 持仓上限4只 + 排名置换（分差>15才换）
  2. 5天收盘<+5%退出（替代原7天<10%）
  3. 精选排名公式：突破量比 + 缩量纯度 + 分歧强度 + 涨停质量 + 均线

策略：回踩分歧日买一半 + 突破分歧高点再买一半
止损：-8% | 止盈：浮盈≥12%后峰值回撤-10%
"""

import sys, os, json, urllib.request, csv
from datetime import datetime, timedelta
from collections import defaultdict
import time

TECH_INDUSTRIES = [
    "半导体", "芯片", "集成电路", "软件开发", "计算机", "互联网", "人工智能",
    "通信", "通讯", "5G", "电子元件", "电子制造", "光学光电子", "消费电子",
    "新能源", "光伏", "锂电池", "储能", "风电", "电网设备", "充电桩",
    "机器人", "工业母机", "专用设备", "自动化", "航天航空", "军工",
    "汽车零部件", "智能汽车", "激光", "仪器仪表", "新材料", "稀土"
]

# K线缓存目录
KLINE_CACHE_DIR = os.path.expanduser("~/.hermes/cache/klines")
os.makedirs(KLINE_CACHE_DIR, exist_ok=True)

def get_kline_hist(code, days=300):
    """获取K线（优先缓存，24h有效）"""
    cache_file = os.path.join(KLINE_CACHE_DIR, f"{code}.json")
    if os.path.exists(cache_file):
        try:
            mtime = os.path.getmtime(cache_file)
            if (time.time() - mtime) / 3600 < 24:
                with open(cache_file) as f:
                    return json.loads(f.read())
        except: pass
    
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,{days},qfq"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://finance.qq.com"})
    try:
        resp = urllib.request.urlopen(req, timeout=8)
        data = json.loads(resp.read().decode("utf-8"))
        kline = data["data"][code].get("qfqday") or data["data"][code].get("day", [])
        if kline:
            try:
                with open(cache_file, 'w') as f:
                    json.dump(kline, f)
            except: pass
        return kline
    except:
        return []

def is_limit_up(idx, closes, n, code):
    if idx < 1 or idx >= n: return False
    chg = (closes[idx] - closes[idx-1]) / closes[idx-1] * 100
    if any(c in str(code) for c in ['30', '68', '8', '4', '920']):
        return chg >= 19.0
    return chg >= 9.2

def find_platform_high(highs, volumes, up_to_idx, max_lookback=50):
    """
    v4.3: 量价加权峰值 — 不单看价格，综合触碰次数+成交量
    得分 = 价格 × (1 + 触碰次数/10) × min(量比, 3)
    相近峰值选最近的（阻力更有效）
    """
    search_start = max(0, up_to_idx - max_lookback)
    if up_to_idx - search_start < 20: return 0
    peaks = []
    for i in range(search_start+3, up_to_idx-3):
        before = max(highs[max(search_start,i-3):i])
        after = max(highs[i+1:min(up_to_idx,i+4)])
        if highs[i] >= before and highs[i] >= after:
            touch_count = sum(1 for j in range(search_start, up_to_idx)
                            if highs[j] >= highs[i] * 0.95)
            if i < len(volumes) and i > 0:
                avg_v = sum(volumes[max(0,i-25):i]) / min(i, 25)
                vw = volumes[i] / avg_v if avg_v > 0 else 1
            else:
                vw = 1
            weight = (1 + touch_count / 10.0) * min(vw, 3.0)
            peaks.append((highs[i], weight, i))
    if not peaks:
        return max(highs[search_start:up_to_idx-3])
    # 取加权得分最高的；如果多个相近，取最近
    best = max(peaks, key=lambda x: x[0] * x[1])
    close = [p for p in peaks if p[0] >= best[0] * 0.97]
    return close[-1][0]  # 最近的

def check_taolaopan(highs, volumes, closes, opens, price, n, lookback=120):
    st = max(0, n - lookback)
    hist = highs[st:n-1] if n-1 > st else []
    if not hist: return False
    if price >= max(hist) * 0.95: return False
    avg_vol = sum(volumes[-25:-5]) / 20 if len(volumes) >= 25 else sum(volumes)/max(len(volumes),1)
    heavy = 0
    for i in range(st, n-1):
        if highs[i] > price and volumes[i] > avg_vol * 2 and closes[i] < opens[i]:
            heavy += 1
    return heavy >= 3


# ═══════════════════════════════════════════════
# v4.3 精选排名公式（替代评分）
# ═══════════════════════════════════════════════

def calc_rank_score(breakout_idx, div_idx, kline):
    """
    v4.3 精选排名分 — 只量化的、不停留在分档的
    维度:
    - 突破量比: min(vol_ratio×15, 35) — 爆量=强共识
    - 缩量纯度: (1-div_vol/bk_vol)×35 — 缩得越狠洗盘越彻底
    - 分歧强度: rejection% / 5 — 冲高回落幅度
    - 涨停质量: 涨停=20, ≥7%=12, ≥5%=8
    - 均线多头: +10
    Max: ~120 | 优质信号: 65-90
    """
    closes = [float(k[2]) for k in kline]
    highs  = [float(k[3]) for k in kline]
    lows   = [float(k[4]) for k in kline]
    vols   = [float(k[5]) for k in kline]
    
    rank = 0.0
    
    # 1. 突破量比
    bk_vol = vols[breakout_idx]
    if breakout_idx >= 25:
        avg_vol = sum(vols[max(0,breakout_idx-25):max(0,breakout_idx-5)]) / 20
    else:
        avg_vol = sum(vols[:breakout_idx]) / max(breakout_idx, 1)
    vol_ratio = bk_vol / avg_vol if avg_vol > 0 else 1
    rank += min(vol_ratio * 15, 35)
    
    # 2. 缩量纯度（分歧日量 / 突破日量）
    div_vol = vols[div_idx] if div_idx < len(vols) else bk_vol
    contraction = 1 - (div_vol / bk_vol) if bk_vol > 0 else 0
    rank += max(0, contraction * 35)
    
    # 3. 分歧强度
    div_high = highs[div_idx]
    div_low = lows[div_idx]
    div_close = closes[div_idx]
    rejection = (div_high - div_close) / (div_high - div_low) * 100 if (div_high - div_low) > 0 else 0
    rank += rejection / 5
    
    # 4. 涨停质量
    max_chg = 0
    for t in range(max(1, breakout_idx-2), breakout_idx+1):
        chg = (closes[t] - closes[t-1]) / closes[t-1] * 100
        if chg > max_chg: max_chg = chg
    if max_chg >= 9.5: rank += 20
    elif max_chg >= 7: rank += 12
    elif max_chg >= 5: rank += 8
    
    # 5. 均线多头
    if len(closes) >= 20:
        ma5 = sum(closes[-6:-1]) / 5
        ma10 = sum(closes[-11:-1]) / 10
        ma20 = sum(closes[-21:-1]) / 20
        if ma5 > ma10 > ma20:
            rank += 10
    
    return round(rank, 1)


# ═══════════════════════════════════════════════
# 信号检测 (与v4.1相同，加入v4.2评分)
# ═══════════════════════════════════════════════

def detect_signal(kline, idx, code):
    """检测三步模式信号，返回信号字典或None"""
    if len(kline) < 30 or idx < 30:
        return None
    
    closes = [float(k[2]) for k in kline[:idx+1]]
    opens  = [float(k[1]) for k in kline[:idx+1]]
    highs  = [float(k[3]) for k in kline[:idx+1]]
    lows   = [float(k[4]) for k in kline[:idx+1]]
    volumes = [float(k[5]) for k in kline[:idx+1]]
    n = len(closes)
    
    if check_taolaopan(highs, volumes, closes, opens, closes[-1], n):
        return None
    
    scan_start = max(0, n - 8)
    
    for i in range(scan_start, n - 1):
        prev_high = find_platform_high(highs, volumes, i)
        if prev_high <= 0 or closes[i] <= prev_high: continue
        
        vol_20 = sum(volumes[max(0,i-25):max(0,i-5)]) / 20 if i >= 25 else sum(volumes[:i])/max(i,1)
        vol_ratio = volumes[i] / vol_20 if vol_20 > 0 else 1
        if vol_ratio < 1.3: continue
        
        if not any(is_limit_up(t, closes, n, code) for t in range(max(1,i-2), i+1)):
            continue
        
        rejection = (highs[i]-closes[i])/(highs[i]-lows[i])*100 if highs[i]-lows[i]>0 else 0
        self_div = rejection >= 60 and highs[i] > closes[i-1]
        
        if (closes[i]-prev_high)/prev_high*100 > 15: continue
        
        div_day = i if self_div else None
        if not div_day:
            for j in range(i+1, min(n, i+4)):
                rj = (highs[j]-closes[j])/(highs[j]-lows[j])*100 if highs[j]-lows[j]>0 else 0
                if rj >= 60 and highs[j] > closes[j-1]:
                    div_day = j; break
        
        if div_day is None: continue
        
        entry1_price = closes[div_day]
        entry1_date = kline[div_day][0]
        div_high = max(highs[max(i, div_day-2):div_day+1])
        
        if div_day + 1 >= n: continue
        broke_idx = None
        for bi in range(div_day+1, n):
            if closes[bi] > div_high and highs[bi] > div_high:
                broke_idx = bi; break
        
        if broke_idx is None: continue
        
        entry2_date = kline[broke_idx][0]
        entry2_price = opens[broke_idx]
        if entry2_price > div_high * 1.05: continue
        
        close_below = sum(1 for t in range(broke_idx+1, n) if closes[t] < div_high)
        if close_below >= 2: continue
        
        over = (closes[-1] - div_high)/div_high*100
        if over > 5: continue
        
        # v4.3 排名分
        rank_score = calc_rank_score(i, div_day, kline[:idx+1])
        
        # 计算实际买入信息
        div_idx_in_full = div_day
        e1_open = float(kline[div_day+1][1]) if div_day+1 < len(kline) else entry1_price
        e2_open = float(kline[broke_idx+1][1]) if broke_idx+1 < len(kline) else entry2_price
        
        return {
            "code": code,
            "entry1_date": entry1_date,
            "entry2_date": entry2_date,
            "avg_entry": (e1_open + e2_open) / 2,
            "div_high": div_high,
            "div_idx": div_idx_in_full,
            "broke_idx": broke_idx,
            "vol_ratio": vol_ratio,
            "rank_score": rank_score,
            "prev_high": prev_high,
            "kline": kline,
        }
    return None


# ═══════════════════════════════════════════════
# 持仓模拟：从买入到退出
# ═══════════════════════════════════════════════

def simulate_position(pos, end_date=None):
    """
    模拟持仓从买入到退出。end_date为None则跑到K线末尾。
    返回: (exited, exit_date, exit_price, exit_reason, peak, max_profit)
    """
    kline = pos['kline']
    dates = [k[0] for k in kline]
    avg_entry = pos['avg_entry']
    start_hold = pos['broke_idx'] + 2  # 突破日次日开始持仓
    
    if start_hold >= len(dates):
        return (True, dates[-1], float(kline[-1][2]), "数据不足", avg_entry, 0)
    
    stop_loss = avg_entry * 0.92
    trailing_active = False
    peak = avg_entry
    max_profit_pct = 0
    
    end_idx = len(dates)
    if end_date:
        for ei in range(start_hold, len(dates)):
            if dates[ei] > end_date:
                end_idx = ei
                break
    
    for hold_idx in range(start_hold, end_idx):
        h_day = dates[hold_idx]
        h_high = float(kline[hold_idx][3])
        h_low = float(kline[hold_idx][4])
        h_close = float(kline[hold_idx][2])
        
        if h_high > peak: peak = h_high
        max_profit_pct = max(max_profit_pct, (h_high - avg_entry) / avg_entry * 100)
        
        # 动态止盈激活
        if h_close >= avg_entry * 1.12 or h_high >= avg_entry * 1.12:
            trailing_active = True
        
        # 动态止盈触发
        if trailing_active and h_low <= peak * 0.90:
            return (True, h_day, peak * 0.90, "动态止盈", peak, max_profit_pct)
        
        # 止损
        if h_low <= stop_loss:
            return (True, h_day, stop_loss, "止损", peak, max_profit_pct)
        
        # v4.2: 5天收盘<+5%退出
        if hold_idx == start_hold + 4:
            day5_pct = (h_close - avg_entry) / avg_entry * 100
            if day5_pct < 5:
                return (True, h_day, h_close, "5天收盘不足5%退出", peak, max_profit_pct)
    
    # 未退出 → 返回截止日数据
    if end_date:
        last_i = end_idx - 1
        last_close = float(kline[last_i][2])
        return (False, dates[last_i], last_close, "运行中", peak, max_profit_pct)
    else:
        last_i = len(dates) - 1
        last_close = float(kline[last_i][2])
        return (True, dates[last_i], last_close, "截止日平仓", peak, max_profit_pct)


def get_price_at(kline, target_date):
    """获取某日收盘价"""
    for k in kline:
        if k[0] == target_date:
            return float(k[2])
    return float(kline[-1][2])


# ═══════════════════════════════════════════════
# 主回测：全量扫描 → 持仓管理
# ═══════════════════════════════════════════════

INDUSTRY_CACHE = {}

def is_tech_stock(code):
    global INDUSTRY_CACHE
    if code in INDUSTRY_CACHE:
        return INDUSTRY_CACHE[code]
    try:
        em_code = f"SH{code}" if code.startswith("6") else f"SZ{code}"
        url = f"https://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/CompanySurveyAjax?code={em_code}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://emweb.securities.eastmoney.com/'})
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read().decode('utf-8'))
        ind = data.get('jbzl', {}).get('sshy', '')
        result = any(kw in ind for kw in TECH_INDUSTRIES)
        INDUSTRY_CACHE[code] = result
        return result
    except:
        result = code.startswith(('300', '301', '688'))
        INDUSTRY_CACHE[code] = result
        return result


def run_backtest():
    # 直接用akshare拿全量股票列表（不依赖East Money）
    import akshare as ak
    import random
    
    print("🔍 获取全A股列表...")
    df = ak.stock_info_a_code_name()
    candidates = []
    for _, r in df.iterrows():
        code = str(r["code"]).zfill(6)
        name = r["name"]
        candidates.append((code, name))
    
    print(f"📋 全量: {len(candidates)}只")
    print(f"📅 回测: 2025-11-01 ~ 2026-04-29")
    print(f"📐 v4.3: 持仓上限4只 + 排名置换(分差>15)+ 5天<5%退出 + 精选排名\n")
    
    MAX_POSITIONS = 4
    RANK_GAP = 5  # 排名分差阈值（低门槛鼓励优质替换）
    
    # ═══ 阶段1: 全量扫描，收集所有信号 ═══
    all_signals = []
    skipped = 0
    processed = 0
    seen_signals = set()  # (code, entry1_date) 去重
    
    for ci, (code, name) in enumerate(candidates):
        if code.startswith("6"): qq = f"sh{code}"
        elif code.startswith(("3","0")): qq = f"sz{code}"
        elif code.startswith(("4","8","920")): qq = f"bj{code}"
        else: continue
        
        kline = get_kline_hist(qq, 300)
        if len(kline) < 60:
            skipped += 1; continue
        
        processed += 1
        if processed % 500 == 0:
            print(f"  📊 扫描 {processed}/{len(candidates)} | 信号{len(all_signals)}...")
        
        dates = [k[0] for k in kline]
        
        for idx in range(len(dates)):
            d = dates[idx]
            if d < "2025-11-01" or d > "2026-04-29": continue
            
            signal = detect_signal(kline[:idx+1], idx, code)
            if signal is None: continue
            
            # 去重：同代码+同买入日只保留一个信号
            sig_key = (signal['code'], signal['entry1_date'])
            if sig_key in seen_signals: continue
            seen_signals.add(sig_key)
            
            # 过滤：突破日之后至少需要2根K线来模拟
            if signal['broke_idx'] + 2 >= len(kline): continue
            
            signal['name'] = name
            signal['kline'] = kline  # 覆盖为完整K线
            all_signals.append(signal)
    
    print(f"\n🔍 扫描完成: {processed}只有效, {len(all_signals)}个原始信号\n")
    
    # 按 entry1_date 排序（买入日期）
    all_signals.sort(key=lambda s: s['entry1_date'])
    
    # ═══ 阶段2: 持仓管理模拟 ═══
    positions = []  # [{code, name, avg_entry, entry1_date, kline, broke_idx, current_price, current_return, ...}]
    closed_trades = []
    seen_codes = set()  # 当天已处理的代码
    
    for sig_idx, sig in enumerate(all_signals):
        if sig_idx % 50 == 0:
            print(f"  📈 模拟 {sig_idx}/{len(all_signals)} | 持仓{len(positions)} | 已平{len(closed_trades)}")
        
        current_date = sig['entry1_date']
        
        # ═══ 更新现有持仓到当前日期，检查退出 ═══
        new_positions = []
        for pos in positions:
            exited, exit_date, exit_price, reason, peak, max_p = simulate_position(pos, current_date)
            if exited:
                ret_pct = (exit_price - pos['avg_entry']) / pos['avg_entry'] * 100
                d1 = datetime.strptime(pos['entry1_date'], "%Y-%m-%d")
                d2 = datetime.strptime(exit_date, "%Y-%m-%d")
                closed_trades.append({
                    'name': pos['name'], 'code': pos['code'],
                    'entry1_date': pos['entry1_date'], 'entry2_date': pos['entry2_date'],
                    'avg_entry': pos['avg_entry'], 'exit_price': exit_price,
                    'exit_date': exit_date, 'exit_reason': reason,
                    'ret%': ret_pct, 'days': (d2-d1).days,
                    'score': pos['rank'], 'max_profit': max_p
                })
            else:
                # 更新当前价格和收益率
                current_price = get_price_at(pos['kline'], current_date)
                pos['current_price'] = current_price
                pos['current_return'] = (current_price - pos['avg_entry']) / pos['avg_entry'] * 100
                new_positions.append(pos)
        positions = new_positions
        
        # ═══ 跳过已持仓的股票 ═══
        if any(p['code'] == sig['code'] for p in positions):
            continue
        
        # ═══ 尝试开仓 ═══
        new_pos = {
            'code': sig['code'], 'name': sig['name'],
            'avg_entry': sig['avg_entry'], 
            'entry1_date': sig['entry1_date'],
            'entry2_date': sig['entry2_date'],
            'kline': sig['kline'], 'broke_idx': sig['broke_idx'],
            'rank': sig['rank_score'],
            'current_price': sig['avg_entry'],
            'current_return': 0.0,
            'div_high': sig['div_high'],
        }
        
        if len(positions) < MAX_POSITIONS:
            positions.append(new_pos)
        else:
            # ═══ v4.3 排名置换：找排名最低的持仓 ═══
            lowest_idx = min(range(len(positions)), 
                           key=lambda i: positions[i]['rank'])
            lowest = positions[lowest_idx]
            
            # 新信号排名显著高于最低持仓 → 替换
            if new_pos['rank'] > lowest['rank'] + RANK_GAP:
                exit_price = get_price_at(lowest['kline'], current_date)
                ret_pct = (exit_price - lowest['avg_entry']) / lowest['avg_entry'] * 100
                d1 = datetime.strptime(lowest['entry1_date'], "%Y-%m-%d")
                d2 = datetime.strptime(current_date, "%Y-%m-%d")
                closed_trades.append({
                    'name': lowest['name'], 'code': lowest['code'],
                    'entry1_date': lowest['entry1_date'], 'entry2_date': lowest['entry2_date'],
                    'avg_entry': lowest['avg_entry'], 'exit_price': exit_price,
                    'exit_date': current_date, 'exit_reason': '排名置换',
                    'ret%': ret_pct, 'days': max((d2-d1).days, 1),
                    'score': lowest['rank'], 'max_profit': 0
                })
                positions.pop(lowest_idx)
                positions.append(new_pos)
            # 排名不够 → 放弃新信号
    
    # ═══ 阶段3: 回测结束，关闭所有剩余持仓 ═══
    for pos in positions:
        exited, exit_date, exit_price, reason, peak, max_p = simulate_position(pos)  # 无end_date=跑到末尾
        if reason == "运行中":
            reason = "截止日平仓"
            exit_date = pos['kline'][-1][0]
            exit_price = float(pos['kline'][-1][2])
        
        ret_pct = (exit_price - pos['avg_entry']) / pos['avg_entry'] * 100
        d1 = datetime.strptime(pos['entry1_date'], "%Y-%m-%d")
        d2 = datetime.strptime(exit_date, "%Y-%m-%d")
        closed_trades.append({
            'name': pos['name'], 'code': pos['code'],
            'entry1_date': pos['entry1_date'], 'entry2_date': pos['entry2_date'],
            'avg_entry': pos['avg_entry'], 'exit_price': exit_price,
            'exit_date': exit_date, 'exit_reason': reason,
            'ret%': ret_pct, 'days': max((d2-d1).days, 1),
            'score': pos['rank'], 'max_profit': max_p
        })
    
    # ═══ 批量查询行业 ═══
    unique_codes = set(t["code"] for t in closed_trades)
    print(f"\n🔍 批量查询{len(unique_codes)}只股票行业...")
    stock_industry = {}
    for ci, code in enumerate(unique_codes):
        stock_industry[code] = is_tech_stock(code)
        if (ci+1) % 50 == 0:
            print(f"  {ci+1}/{len(unique_codes)}")
    print("  ✅ 行业查询完成\n")
    
    # ═══ 统计 ═══
    if not closed_trades:
        print("\n📭 无交易")
        return
    
    wins = [t for t in closed_trades if t["ret%"] > 0]
    losses = [t for t in closed_trades if t["ret%"] <= 0]
    
    print(f"\n{'='*65}")
    print(f"📊 大仙三步模式 v4.3 半年回测报告")
    print(f"{'='*65}")
    print(f"  持仓上限: 4只 | 置换策略: 排名分差>15置换")
    print(f"  止损: -8% | 止盈: +12%激活峰值-10% | 5天<5%退出")
    print(f"  总交易: {len(closed_trades)}笔")
    print(f"  胜率: {len(wins)/len(closed_trades)*100:.1f}% ({len(wins)}胜{len(losses)}负)")
    print(f"  平均收益: {sum(t['ret%'] for t in closed_trades)/len(closed_trades):.1f}%")
    print(f"  平均持时: {sum(t['days'] for t in closed_trades)/len(closed_trades):.0f}天")
    print(f"  最大盈利: {max(t['ret%'] for t in closed_trades):.1f}%")
    print(f"  最大亏损: {min(t['ret%'] for t in closed_trades):.1f}%")
    
    # 月度
    months = defaultdict(list)
    for t in closed_trades:
        m = t["entry1_date"][:7]
        months[m].append(t["ret%"])
    
    print(f"\n  月度表现:")
    for m in sorted(months.keys()):
        arr = months[m]
        print(f"    {m}: {len(arr)}笔 | 平均{sum(arr)/len(arr):.1f}% | 胜{sum(1 for x in arr if x>0)/len(arr)*100:.0f}%")
    
    # 退出方式
    reasons = defaultdict(list)
    for t in closed_trades:
        reasons[t["exit_reason"]].append(t["ret%"])
    print(f"\n  按退出方式:")
    for r in sorted(reasons.keys(), key=lambda r: -len(reasons[r])):
        arr = reasons[r]
        wr = sum(1 for x in arr if x>0)/len(arr)*100
        print(f"    {r}: {len(arr)}笔 | 胜率{wr:.0f}% | 平均{sum(arr)/len(arr):.1f}%")
    
    # 评分分档
    print(f"\n  评分分档:")
    for low, high, label in [(0,50,'<50'), (50,65,'50-65'), (65,80,'65-80'), (80,200,'80+')]:
        sub = [t for t in closed_trades if low <= t['score'] < high]
        if sub:
            wr = sum(1 for t in sub if t['ret%']>0)/len(sub)*100
            avg_r = sum(t['ret%'] for t in sub)/len(sub)
            max_r = max(t['ret%'] for t in sub)
            print(f"    {label}: {len(sub)}笔, 胜率{wr:.0f}%, 均+{avg_r:.1f}%, 最高+{max_r:.1f}%")
    
    # 科技 vs 非科技
    tech_trades = [t for t in closed_trades if stock_industry.get(t["code"])]
    nontech_trades = [t for t in closed_trades if stock_industry.get(t["code"]) == False]
    for label, trades_list in [("💻科技", tech_trades), ("🏭非科技", nontech_trades)]:
        if trades_list:
            wr = sum(1 for t in trades_list if t['ret%']>0)/len(trades_list)*100
            avg_r = sum(t['ret%'] for t in trades_list)/len(trades_list)
            print(f"    {label}: {len(trades_list)}笔, 胜率{wr:.0f}%, 均+{avg_r:.1f}%")
    
    # 资金曲线 (10M本金, 4仓位, 每仓250万)
    print(f"\n  💰 资金模拟 (1000万本金, 4仓位各250万):")
    total_return = 0
    for t in closed_trades:
        total_return += t['ret%'] / 100 * 2500000
    final = 10000000 + total_return
    print(f"    期末资金: {final/10000:.0f}万 | 总收益: {total_return/10000:.0f}万 | 收益率: {total_return/10000000*100:.1f}%")
    
    # TOP/BOTTOM
    print(f"\n  🏆 最大盈利 TOP15:")
    print(f"    {'股票':<10} {'代码':<8} {'评':>3} {'买入':>10} → {'卖出':>10} {'收益':>7} {'原因'}")
    print(f"    {'─'*68}")
    for t in sorted(closed_trades, key=lambda x: -x["ret%"])[:15]:
        tech = "💻" if stock_industry.get(t["code"]) else "🏭"
        print(f"    {tech} {t['name']:<10}({t['code']}) {t['score']:>3} {t['entry1_date']}→{t['exit_date']} {t['ret%']:>+6.1f}% {t['exit_reason']}")
    
    print(f"\n  💀 最大亏损 TOP10:")
    print(f"    {'股票':<10} {'代码':<8} {'评':>3} {'买入':>10} → {'卖出':>10} {'收益':>7} {'原因'}")
    print(f"    {'─'*68}")
    for t in sorted(closed_trades, key=lambda x: x["ret%"])[:10]:
        tech = "💻" if stock_industry.get(t["code"]) else "🏭"
        print(f"    {tech} {t['name']:<10}({t['code']}) {t['score']:>3} {t['entry1_date']}→{t['exit_date']} {t['ret%']:>+6.1f}% {t['exit_reason']}")
    
    return closed_trades, stock_industry


if __name__ == "__main__":
    trades, stock_industry = run_backtest()
    
    # 导出CSV
    outpath = '/tmp/backtest_v43_trades.csv'
    with open(outpath, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['股票名称','代码','类型','评分','买入日期','卖出日期','买入价','收益%','退出方式','持有天数'])
        for t in sorted(trades, key=lambda x: -x['ret%']):
            tech = '科技' if stock_industry.get(t['code']) else '非科技'
            w.writerow([
                t['name'], t['code'], tech, t['score'],
                t['entry1_date'], t['exit_date'], f"{t['avg_entry']:.2f}",
                f"{t['ret%']:.1f}%", t['exit_reason'], t['days']
            ])
    print(f'\n📁 CSV导出: {len(trades)}笔 → {outpath}')
