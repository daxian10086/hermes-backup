#!/bin/bash

# 64卦数据库进度检查脚本
# 检查v26版本的总卦提取进度

DB_PATH="/tmp/hexagrams_v26.db"
LOG_FILE="/tmp/hexagram_progress.log"

# 获取当前时间
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 检查数据库文件
if [ ! -f "$DB_PATH" ]; then
    echo "[$TIMESTAMP] 数据库文件不存在: $DB_PATH" >> "$LOG_FILE"
    exit 1
fi

# 使用Python检查数据质量
python3 << 'PYEOF' >> "$LOG_FILE"
import sqlite3
import pandas as pd

conn = sqlite3.connect('/tmp/hexagrams_v26.db')
df = pd.read_sql('SELECT * FROM hexagrams', conn)

# 检查总卦（爻位0）的mnop列
total_gua = df[df['爻位'] == 0]
check_cols = ['运势', '财运', '家庭', '健康']

# 统计每个字段的填充情况
stats = {}
for col in check_cols:
    filled_count = total_gua[col].notna().sum()
    stats[col] = filled_count

# 统计完整率
complete_gua = 0
for idx in total_gua.index:
    row = total_gua.loc[idx]
    if all(not pd.isna(row[col]) and str(row[col]).strip() != '' for col in check_cols):
        complete_gua += 1

complete_rate = (complete_gua / len(total_gua) * 100) if len(total_gua) > 0 else 0

# 打印进度信息
import datetime
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f"[{timestamp}] 总卦提取进度:")
print(f"  运势: {stats['运势']}/64")
print(f"  财运: {stats['财运']}/64")
print(f"  家庭: {stats['家庭']}/64")
print(f"  健康: {stats['健康']}/64")
print(f"  完整率: {complete_rate:.1f}% ({complete_gua}/64)")
print()

conn.close()
PYEOF

echo "[$TIMESTAMP] 进度检查完成" >> "$LOG_FILE"
