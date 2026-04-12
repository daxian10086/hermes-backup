#!/bin/bash
# 记忆清理脚本 - 每天 04:00 执行
# 参考：文章2 - 实操复盘：我是如何通过「凌晨自动清理」解决 Context Window 焦虑的

MEMORY_DIR="/workspace/projects/workspace/memory"
KEEP_DAYS_DAILY=3
KEEP_DAYS_STOCK=2

echo "[$(date)] 开始记忆清理..."

# 清理过期的每日日志（保留最近 KEEP_DAYS_DAILY 天）
echo "清理每日日志..."
find "$MEMORY_DIR" -name "2026-*.md" -type f -mtime +$KEEP_DAYS_DAILY -delete

# 清理过期的股票学习笔记（保留最近 KEEP_DAYS_STOCK 天）
echo "清理股票学习笔记..."
find "$MEMORY_DIR" -name "股票学习笔记-*.md" -type f -mtime +$KEEP_DAYS_STOCK -delete

echo "[$(date)] 记忆清理完成！"
