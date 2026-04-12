#!/bin/bash
# Hermes 自动备份脚本
# 每天凌晨4点执行

cd ~/.hermes || exit 1

# 暂存所有更改（包括新增和删除）
git add -A

# 检查有没有变化
git diff --cached --quiet && {
    echo "[$(date)] 没有变化，跳过提交"
    exit 0
}

# 提交，标题带时间戳
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
git commit -m "backup: ${TIMESTAMP}"

# 推送到 GitHub
git push origin master

echo "[$(date)] 备份完成"
