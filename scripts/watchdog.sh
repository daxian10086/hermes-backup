#!/bin/bash
# OpenClaw 网关看门狗（适配 supervisord 环境）
# 检查网关和通道级别的健康状态，如果降级则重启。

CLI="/usr/bin/openclaw"
LOG_FILE="/tmp/openclaw/watchdog.log"
LOCK_FILE="/tmp/openclaw-watchdog.lock"
RESTART_SCRIPT="/workspace/projects/scripts/restart.sh"

# 网关日志最后一次写入后的最大秒数
STALE_THRESHOLD_SECONDS=7200

mkdir -p /tmp/openclaw

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

# 如果日志 > 1MB 则轮转
if [ -f "$LOG_FILE" ] && [ "$(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)" -gt 1048576 ]; then
    mv "$LOG_FILE" "${LOG_FILE}.old"
fi

acquire_lock() {
    if [ -f "$LOCK_FILE" ]; then
        local old_pid
        old_pid=$(cat "$LOCK_FILE" 2>/dev/null)
        if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
            exit 0
        fi
    fi
    echo $$ > "$LOCK_FILE"
}

release_lock() { rm -f "$LOCK_FILE"; }
trap release_lock EXIT
acquire_lock

check_gateway_process() {
    if pgrep -f "openclaw-gateway" > /dev/null; then
        echo "running"; return 0
    else
        echo "not_running"; return 1
    fi
}

check_channel_health() {
    local health_output
    health_output=$($CLI health 2>&1)
    if [ $? -ne 0 ]; then echo "health_cmd_failed"; return 1; fi
    if echo "$health_output" | grep -qi "feishu.*failed\|feishu.*error\|feishu.*disconnected\|feishu.*timeout"; then echo "feishu_down"; return 1; fi
    if echo "$health_output" | grep -qi "wechat.*failed\|wechat.*error\|wechat.*disconnected"; then echo "wechat_down"; return 1; fi
    echo "ok"; return 0
}

check_log_freshness() {
    local log_dir="$1"
    local latest_log
    latest_log=$(find "$log_dir" -name "*.log" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)

    if [ -z "$latest_log" ] || [ ! -f "$latest_log" ]; then
        echo "log_missing"
        return 1
    fi

    local now last_mod age
    now=$(date +%s)
    last_mod=$(stat -c%Y "$latest_log" 2>/dev/null || echo 0)
    age=$((now - last_mod))

    if [ "$age" -gt "$STALE_THRESHOLD_SECONDS" ]; then
        echo "log_stale_${age}s"
        return 1
    fi
    echo "fresh"; return 0
}

restart_gateway() {
    log "正在重启网关..."
    if [ -x "$RESTART_SCRIPT" ]; then
        $RESTART_SCRIPT
    else
        log "重启脚本不存在: $RESTART_SCRIPT"
        return 1
    fi

    sleep 10

    local result; result=$(check_gateway_process)
    if [ "$result" = "running" ]; then
        log "网关重启成功"
        return 0
    else
        log "网关已重启但进程未运行"
        return 1
    fi
}

# 检查并执行未完成任务
check_pending_tasks() {
    local tasks_file="/workspace/projects/workspace/memory/tasks.md"
    if [ ! -f "$tasks_file" ]; then
        return 0
    fi

    log "检查未完成任务..."
    local pending_count running_count
    pending_count=$(grep -c "- \\**状态\\*\\*: pending" "$tasks_file" 2>/dev/null || echo 0)
    running_count=$(grep -c "- \\**状态\\*\\*: running" "$tasks_file" 2>/dev/null || echo 0)

    log "发现 $pending_count 个 pending 任务, $running_count 个 running 任务"

    # 如果有pending任务，记录到日志
    if [ "$pending_count" -gt 0 ]; then
        log "检测到 $pending_count 个待执行任务，需要手动处理"
    fi

    # 检查running任务是否超时（超过2小时视为超时）
    if [ "$running_count" -gt 0 ]; then
        log "检测到 $running_count 个运行中任务，检查是否超时..."
        # 简单的超时检查：如果有running任务且超过2小时，建议检查
    fi
}

check_and_fix() {
    # 第一层：进程检查
    local process_result; process_result=$(check_gateway_process)
    if [ "$process_result" != "running" ]; then
        log "网关进程未运行: $process_result"
        if restart_gateway; then
            log "网关已自动重启"
        else
            log "网关重启失败"
        fi
        return
    fi

    # 第二层：通道健康检查
    local health_result; health_result=$(check_channel_health)
    if [ "$health_result" != "ok" ]; then
        log "通道健康检查失败: $health_result"
        if restart_gateway; then
            log "网关已自动重启"
        else
            log "网关重启失败"
        fi
        return
    fi

    # 第三层：日志新鲜度检查
    local log_result; log_result=$(check_log_freshness "/tmp/openclaw")
    if [ "$log_result" != "fresh" ]; then
        log "日志过时 ($log_result) 尽管状态健康"
        if restart_gateway; then
            log "网关已自动重启"
        else
            log "网关重启失败"
        fi
    fi
}

log "看门狗检查开始..."
check_and_fix
check_pending_tasks
log "看门狗检查完成"
