#!/usr/bin/env python3
"""
Dragon Report - 小龙任务结果共享文件写入工具 v2
- 每次任务完成后追加写入完整结果
- 文件超过100行时自动清理（当日模式）
- 支持按天轮转（保留最近7天日志）
- 增加任务内容摘要显示

用法:
    python3 dragon_report.py append <task_id> <result> <agent_type> [task_summary]
    python3 dragon_report.py cleanup
    python3 dragon_report.py rotate    # 手动触发按天轮转
"""
import os
import sys
import glob
from datetime import datetime, timedelta

REPORT_DIR = '/home/wdmms123/.hermes/cron/output'
REPORT_FILE = os.path.join(REPORT_DIR, 'dragon_report.txt')
MAX_LINES = 100
MAX_DAYS = 7  # 保留最近7天的历史文件

def get_line_count():
    """获取文件当前行数"""
    if not os.path.exists(REPORT_FILE):
        return 0
    try:
        with open(REPORT_FILE, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def should_clean_up():
    """检查是否需要清理：超过100行"""
    return get_line_count() >= MAX_LINES

def clean_up():
    """清空文件（每日凌晨自动调用或超限触发）"""
    try:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        header = f"=== Dragon Report Auto-Cleaned at {ts} ===\n"
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(header)
        print(f"[dragon_report] Cleaned at {ts}", flush=True)
        return True
    except Exception as e:
        print(f"[dragon_report] Cleanup failed: {e}", flush=True)
        return False

def rotate_by_day():
    """按天轮转：将当前文件移动到带日期的名称，创建新文件"""
    try:
        if not os.path.exists(REPORT_FILE):
            return False
        
        ts = datetime.now().strftime('%Y-%m-%d')
        rotated_name = os.path.join(REPORT_DIR, f"dragon_report_{ts}.txt")
        
        # 如果今天的轮转文件已存在，追加序号
        if os.path.exists(rotated_name):
            counter = 1
            while os.path.exists(rotated_name):
                rotated_name = os.path.join(REPORT_DIR, f"dragon_report_{ts}_{counter}.txt")
                counter += 1
        
        # 移动文件
        with open(REPORT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(rotated_name, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 清空当前文件，写入新header
        new_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"=== Dragon Report Rotated at {new_ts} ===\n")
        
        print(f"[dragon_report] Rotated to {rotated_name}", flush=True)
        return True
    except Exception as e:
        print(f"[dragon_report] Rotate failed: {e}", flush=True)
        return False

def clean_old_backups():
    """清理过期的历史备份（保留最近MAX_DAYS天）"""
    try:
        pattern = os.path.join(REPORT_DIR, "dragon_report_*.txt")
        backup_files = glob.glob(pattern)
        
        cutoff = datetime.now() - timedelta(days=MAX_DAYS)
        cleaned = 0
        
        for fpath in backup_files:
            # 跳过当前文件
            if fpath == REPORT_FILE:
                continue
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                if mtime < cutoff:
                    os.remove(fpath)
                    cleaned += 1
            except Exception:
                pass
        
        if cleaned > 0:
            print(f"[dragon_report] Cleaned {cleaned} old backup files", flush=True)
        return cleaned
    except Exception as e:
        print(f"[dragon_report] Clean old backups failed: {e}", flush=True)
        return 0

def append_report(task_id: str, result: str, agent_type: str = "", task_summary: str = ""):
    """
    追加任务结果到报告文件
    
    Args:
        task_id: 任务ID
        result: 完整结果内容
        agent_type: 执行类型（如 stock, code, image, general 等）
        task_summary: 任务内容摘要（可选，用于快速识别任务）
    
    Returns:
        bool: 是否写入成功
    """
    try:
        # 检查是否需要清理
        if should_clean_up():
            # 先按天轮转保存
            rotate_by_day()
            clean_old_backups()
            print(f"[dragon_report] Auto-rotated (exceeded {MAX_LINES} lines)", flush=True)

        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 显示实际类型而非unknown
        if agent_type:
            agent_tag = f"[{agent_type.upper()}]"
        else:
            agent_tag = "[GENERAL]"  # 默认为GENERAL，不再显示unknown
        
        # 格式化header，增加任务摘要
        header = f"\n{'='*60}\n"
        header += f"📋 任务完成 | {ts} | {agent_tag} | ID: {task_id}\n"
        
        if task_summary:
            # 截取摘要前100字符
            summary = task_summary[:100] + "..." if len(task_summary) > 100 else task_summary
            header += f"📝 任务摘要: {summary}\n"
        
        header += f"{'='*60}\n"

        with open(REPORT_FILE, 'a', encoding='utf-8') as f:
            f.write(header)
            f.write(result)
            f.write('\n')

        line_count = get_line_count()
        print(f"[dragon_report] Appended task {task_id} as {agent_tag} ({line_count} lines)", flush=True)
        return True

    except Exception as e:
        print(f"[dragon_report] Append failed: {e}", flush=True)
        return False

def manual_cleanup():
    """手动清理接口（供 cron job 调用）"""
    print(f"[dragon_report] Manual cleanup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    rotate_by_day()
    clean_old_backups()
    return clean_up()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"[dragon_report] Report file: {REPORT_FILE}")
        print(f"[dragon_report] Current lines: {get_line_count()}")
        print(f"[dragon_report] Usage:")
        print(f"  python3 dragon_report.py append <task_id> <result> <agent_type> [task_summary]")
        print(f"  python3 dragon_report.py cleanup")
        print(f"  python3 dragon_report.py rotate")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == 'cleanup':
        manual_cleanup()
    elif cmd == 'rotate':
        rotate_by_day()
        clean_old_backups()
    elif cmd == 'append':
        if len(sys.argv) < 5:
            print("[dragon_report] Usage: append <task_id> <result> <agent_type> [task_summary]")
            sys.exit(1)
        task_id = sys.argv[2]
        result = sys.argv[3]
        agent_type = sys.argv[4]
        task_summary = sys.argv[5] if len(sys.argv) > 5 else ""
        append_report(task_id, result, agent_type, task_summary)
    else:
        print(f"[dragon_report] Unknown command: {cmd}")
        sys.exit(1)
