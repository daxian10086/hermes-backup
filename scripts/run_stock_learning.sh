#!/bin/bash
# 每天凌晨0点执行的股票知识学习脚本

cd /workspace/projects/workspace

# 记录日志
LOG_FILE="/tmp/stock_knowledge.log"
echo "========================================" >> $LOG_FILE
echo "$(date '+%Y-%m-%d %H:%M:%S') 开始执行股票知识学习" >> $LOG_FILE

# 执行学习脚本
python3 /workspace/projects/scripts/stock_knowledge_learning.py >> $LOG_FILE 2>&1

# 记录结束时间
echo "$(date '+%Y-%m-%d %H:%M:%S') 学习任务完成" >> $LOG_FILE
echo "========================================" >> $LOG_FILE
