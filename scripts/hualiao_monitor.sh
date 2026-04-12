#!/bin/bash
# 华电辽能监控定时任务

# 设置Python路径
export PYTHONPATH=/workspace/projects/scripts:$PYTHONPATH

# 监控脚本路径
MONITOR_SCRIPT="/workspace/projects/scripts/hualiao_monitor.py"

# 日志路径
LOG_FILE="/tmp/hualiao_monitor.log"

# 添加定时任务到crontab
add_crontab() {
    echo "添加华电辽能监控定时任务..."

    # 备份当前crontab
    crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

    # 添加新的定时任务
    (crontab -l 2>/dev/null | grep -v "hualiao_monitor"; \
        echo "# 华电辽能(600396)监控任务"; \
        echo "# 集合竞价开始（9:15）"; \
        echo "15 9 * * 1-5 /usr/bin/python3 $MONITOR_SCRIPT once >> $LOG_FILE 2>&1"; \
        echo "# 集合竞价结束（9:25）"; \
        echo "25 9 * * 1-5 /usr/bin/python3 $MONITOR_SCRIPT once >> $LOG_FILE 2>&1"; \
        echo "# 开盘时检查（9:30）"; \
        echo "30 9 * * 1-5 /usr/bin/python3 $MONITOR_SCRIPT once >> $LOG_FILE 2>&1"; \
        echo "# 上午收盘前检查（11:25）"; \
        echo "25 11 * * 1-5 /usr/bin/python3 $MONITOR_SCRIPT once >> $LOG_FILE 2>&1"; \
        echo "# 下午开盘时检查（13:00）"; \
        echo "0 13 * * 1-5 /usr/bin/python3 $MONITOR_SCRIPT once >> $LOG_FILE 2>&1"; \
        echo "# 收盘后检查（15:05）"; \
        echo "5 15 * * 1-5 /usr/bin/python3 $MONITOR_SCRIPT once >> $LOG_FILE 2>&1"; \
        echo "# 每小时检查一次（10:30-14:30）"; \
        echo "30 10-14 * * 1-5 /usr/bin/python3 $MONITOR_SCRIPT once >> $LOG_FILE 2>&1") | crontab -

    echo "✓ 定时任务已添加"
    echo ""
    echo "当前定时任务："
    crontab -l | grep "hualiao_monitor"
}

# 删除定时任务
remove_crontab() {
    echo "删除华电辽能监控定时任务..."

    # 备份当前crontab
    crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

    # 删除监控任务
    (crontab -l 2>/dev/null | grep -v "hualiao_monitor") | crontab -

    echo "✓ 定时任务已删除"
}

# 显示定时任务
show_crontab() {
    echo "当前华电辽能监控定时任务："
    crontab -l | grep "hualiao_monitor" || echo "未找到监控任务"
}

# 立即执行一次
run_now() {
    echo "立即执行一次监控..."
    /usr/bin/python3 $MONITOR_SCRIPT once
}

# 持续监控（6小时）
run_monitor() {
    echo "启动持续监控（9:30-15:30）..."
    /usr/bin/python3 $MONITOR_SCRIPT monitor 360
}

# 查看日志
show_log() {
    echo "最近20条日志："
    if [ -f "$LOG_FILE" ]; then
        tail -20 "$LOG_FILE"
    else
        echo "日志文件不存在"
    fi
}

# 查看监控报告
show_report() {
    REPORT_FILE="/tmp/hualiao_report_$(date +%Y%m%d).json"
    if [ -f "$REPORT_FILE" ]; then
        echo "今日监控报告："
        cat "$REPORT_FILE" | python3 -m json.tool
    else
        echo "今日报告不存在，可能还未收盘"
    fi
}

# 显示帮助
show_help() {
    echo "华电辽能(600396)监控工具"
    echo ""
    echo "用法:"
    echo "  $0 add         - 添加定时任务"
    echo "  $0 remove      - 删除定时任务"
    echo "  $0 show        - 显示定时任务"
    echo "  $0 run         - 立即执行一次监控"
    echo "  $0 monitor     - 持续监控6小时"
    echo "  $0 log         - 查看日志"
    echo "  $0 report      - 查看今日报告"
    echo "  $0 help        - 显示帮助"
}

# 主函数
case "$1" in
    add)
        add_crontab
        ;;
    remove)
        remove_crontab
        ;;
    show)
        show_crontab
        ;;
    run)
        run_now
        ;;
    monitor)
        run_monitor
        ;;
    log)
        show_log
        ;;
    report)
        show_report
        ;;
    help|*)
        show_help
        ;;
esac
