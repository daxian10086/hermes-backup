#!/bin/bash
# 每天凌晨0点执行淘股吧情报爬取

cd /workspace/projects/workspace

# 记录日志
LOG_FILE="/tmp/taoguba.log"
echo "========================================" >> $LOG_FILE
echo "$(date '+%Y-%m-%d %H:%M:%S') 开始执行淘股吧情报爬取" >> $LOG_FILE

# 执行爬虫（使用示例版本，因为反爬限制）
python3 /workspace/projects/scripts/taoguba_sample.py >> $LOG_FILE 2>&1

# 记录结束时间
echo "$(date '+%Y-%m-%d %H:%M:%S') 爬取任务完成" >> $LOG_FILE
echo "========================================" >> $LOG_FILE
