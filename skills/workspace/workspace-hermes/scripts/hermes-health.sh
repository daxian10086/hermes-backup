#!/bin/bash
# Hermes 健康检查脚本
# 检查网关和通道健康状态，发现问题则记录

set -e

LOG_FILE="/tmp/hermes-health.log"
LOCK_FILE="/tmp/hermes-health.lock"
STALE_THRESHOLD=3600  # 1小时无日志视为过时

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

# 日志轮转
if [ -f "$LOG_FILE" ] && [ "$(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)" -gt 1048576 ]; then
    mv "$LOG_FILE" "${LOG_FILE}.old"
fi

acquire_lock() {
    if [ -f "$LOCK_FILE" ]; then
        local old_pid=$(cat "$LOCK_FILE" 2>/dev/null)
        if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
            exit 0
        fi
    fi
    echo $$ > "$LOCK_FILE"
}

release_lock() { rm -f "$LOCK_FILE"; }
trap release_lock EXIT
acquire_lock

log "=== 健康检查开始 ==="

# 1. 检查进程
check_process() {
    if pgrep -f "hermes" > /dev/null; then
        log "✓ Hermes 进程运行中"
        return 0
    else
        log "✗ Hermes 进程未运行"
        return 1
    fi
}

# 2. 检查日志新鲜度
check_logs() {
    local log_dir="$HOME/.hermes/logs"
    if [ ! -d "$log_dir" ]; then
        log "○ 日志目录不存在"
        return 0
    fi
    
    local latest_log=$(find "$log_dir" -name "*.log" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
    
    if [ -z "$latest_log" ] || [ ! -f "$latest_log" ]; then
        log "○ 未找到日志文件"
        return 0
    fi
    
    local now last_mod age
    now=$(date +%s)
    last_mod=$(stat -c%Y "$latest_log" 2>/dev/null || echo 0)
    age=$((now - last_mod))
    
    if [ "$age" -gt "$STALE_THRESHOLD" ]; then
        log "✗ 日志过时 (${age}s 无更新)"
        return 1
    else
        log "✓ 日志新鲜 (${age}s 前更新)"
        return 0
    fi
}

# 3. 检查 cron 任务
check_cron() {
    # 检查 cron 是否有 heremes 相关任务
    if crontab -l 2>/dev/null | grep -q "hermes"; then
        log "✓ Cron 任务已配置"
        return 0
    else
        log "○ 无 Hermes cron 任务"
        return 0
    fi
}

# 4. 检查 skills
check_skills() {
    local skills_dir="$HOME/.hermes/skills"
    if [ -d "$skills_dir" ]; then
        local count=$(find "$skills_dir" -maxdepth 1 -type d | wc -l)
        count=$((count - 1))  # 减去 skills 本身
        log "✓ $count 个 skills 安装"
        return 0
    else
        log "○ skills 目录不存在"
        return 0
    fi
}

# 5. 检查状态数据库
check_database() {
    local db_file="$HOME/.hermes/state.db"
    if [ -f "$db_file" ]; then
        local size=$(stat -c%s "$db_file" 2>/dev/null || echo 0)
        local size_mb=$((size / 1024 / 1024))
        log "✓ 状态数据库: ${size_mb}MB"
        return 0
    else
        log "○ 状态数据库不存在"
        return 0
    fi
}

# 执行检查
check_process
check_logs
check_cron
check_skills
check_database

log "=== 健康检查完成 ==="
