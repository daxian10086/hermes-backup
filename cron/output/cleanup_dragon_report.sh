#!/bin/bash
# 清理 dragon_report.txt 如果超过100行
FILE="/home/wdmms123/.hermes/cron/output/dragon_report.txt"
if [ -f "$FILE" ]; then
  LINES=$(wc -l < "$FILE")
  if [ "$LINES" -gt 100 ]; then
    echo "=== $(date) ===" > "$FILE"
    echo "文件已清理（超过100行）" >> "$FILE"
  fi
fi
