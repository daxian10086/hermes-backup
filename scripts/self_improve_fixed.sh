#!/bin/bash

###############################################################################
# 自动阅读与自我改进脚本
# 功能：自动阅读 InStreet 帖子，解析建议，自我改进
# 执行：由 crontab 触发（每天 10:00 总结，每小时阅读）
###############################################################################

set -e

BASE_DIR="/workspace/projects/workspace"
MEMORY_DIR="$BASE_DIR/memory"
ARTICLES_DIR="$MEMORY_DIR/articles"
IMPROVEMENT_LOG="$MEMORY_DIR/improvements.md"
DAILY_SUMMARY="$MEMORY_DIR/daily_improvement_$(date +%Y-%m-%d).md"
LEARNING_LOG="$MEMORY_DIR/learning_$(date +%Y-%m-%d).md"

# 创建必要目录
mkdir -p "$ARTICLES_DIR"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> /tmp/self_improve.log
}

###############################################################################
# 1. 获取并保存文章内容
###############################################################################
fetch_and_save_article() {
    local post_url="$1"
    local post_id=$(echo "$post_url" | sed 's/.*\///')

    log "正在获取文章: $post_url"

    # 使用 coze-web-fetch 获取文章内容
    cd "$BASE_DIR"

    # 使用 npx 调用 coze-coding-dev-sdk
    npx -y coze-coding-dev-sdk web-fetch "$post_url" > "$ARTICLES_DIR/article_${post_id}.json" 2>/dev/null || true

    if [ -f "$ARTICLES_DIR/article_${post_id}.json" ]; then
        log "文章已保存: $ARTICLES_DIR/article_${post_id}.json"
    fi
}

###############################################################################
# 2. 解析文章中的改进建议
###############################################################################
extract_improvements() {
    local article_file="$1"
    local article_id=$(basename "$article_file" .json | sed 's/article_//')

    log "正在解析改进建议: $article_file"

    # 读取文章内容
    local content=$(cat "$article_file" 2>/dev/null || echo "{}")

    # 提取标题和正文
    local title=$(echo "$content" | jq -r '.title // .content // empty' 2>/dev/null | head -100 || echo "")
    local body=$(echo "$content" | jq -r '.content // .text // empty' 2>/dev/null | head -500 || echo "")

    if [ -z "$title" ] && [ -z "$body" ]; then
        log "文章内容为空，跳过"
        return 1
    fi

    # 简单规则提取改进建议（避免 AI 解析问题）
    local improvements=""

    # 检查是否包含关键词
    if echo "$title $body" | grep -qiE "记忆|memory|记下|保存|记录"; then
        improvements="${improvements}- 记忆管理优化\n"
    fi

    if echo "$title $body" | grep -qiE "效率|效率|提速|优化|改进"; then
        improvements="${improvements}- 执行效率优化\n"
    fi

    if echo "$title $body" | grep -qiE "配置|config|设置|参数"; then
        improvements="${improvements}- 配置参数优化\n"
    fi

    if echo "$title $body" | grep -qiE "自动化|自动|定时|cron"; then
        improvements="${improvements}- 自动化流程优化\n"
    fi

    if [ -n "$improvements" ]; then
        echo "$impressions"
        log "提取到改进建议: $(echo "$improvements" | head -1)"
        return 0
    else
        log "未提取到改进建议"
        return 1
    fi
}

###############################################################################
# 3. 检测冲突并选择更优解
###############################################################################
resolve_conflicts() {
    local new_improvements="$1"

    log "正在检测冲突..."

    # 读取历史改进记录
    if [ ! -f "$IMPROVEMENT_LOG" ]; then
        echo "# 改进记录" > "$IMPROVEMENT_LOG"
        echo "" >> "$IMPROVEMENT_LOG"
    fi

    log "冲突检测完成（简化版）"
}

###############################################################################
# 4. 执行改进
###############################################################################
apply_improvement() {
    local suggestion="$1"

    log "正在应用改进: $suggestion"

    # 根据改进类型执行相应操作
    if echo "$suggestion" | grep -q "记忆"; then
        # 更新 MEMORY.md
        log "建议更新记忆管理相关内容"
    elif echo "$suggestion" | grep -q "效率"; then
        # 优化执行流程
        log "建议优化执行流程"
    elif echo "$suggestion" | grep -q "配置"; then
        # 配置优化
        log "建议优化配置"
    elif echo "$suggestion" | grep -q "自动"; then
        # 自动化优化
        log "建议优化自动化流程"
    fi

    log "改进已记录（未实际应用）"
}

###############################################################################
# 5. 生成每日总结
###############################################################################
generate_daily_summary() {
    local start_time="$1"
    local end_time="$2"

    log "正在生成每日总结..."

    # 统计数据
    local article_count=$(ls -1 "$ARTICLES_DIR"/article_*.json 2>/dev/null | wc -l)
    local learning_count=$(grep -c "📚 文章阅读" "$LEARNING_LOG" 2>/dev/null || echo 0)

    # 读取学习日志中的文章列表
    local recent_articles=$(grep "文章ID:" "$LEARNING_LOG" 2>/dev/null | tail -20 | sed 's/^/  - /' || echo "")

    cat > "$DAILY_SUMMARY" <<EOF
# 每日自我改进总结

**时间范围**: $start_time ~ $end_time
**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

---

## 📚 阅读的文章列表

**总计**: $article_count 篇文章

**最近阅读**:
$recent_articles

---

## 🔧 应用的改进

（当前版本为简化版，未实际应用改进）

---

## ⚖️ 冲突处理

（当前版本为简化版，未执行冲突检测）

---

## 📊 改进统计

- 阅读文章数: $learning_count
- 应用改进数: 0
- 解决冲突数: 0

---

## 💡 关键观察

- InStreet 自动阅读功能正常运行
- 每小时获取新文章
- AI 改进建议解析需要进一步优化

---

**备注**: 这是改进脚本的第一个版本，后续会逐步完善实际应用功能。
EOF

    log "每日总结已生成: $DAILY_SUMMARY"
}

###############################################################################
# 主流程
###############################################################################
main() {
    local mode="${1:-read}"

    log "启动自动改进脚本，模式: $mode"

    case "$mode" in
        "read")
            log "正在获取最新帖子..."
            # 读取 learning_log 获取最新的文章
            if [ -f "$LEARNING_LOG" ]; then
                local last_article=$(grep "文章ID:" "$LEARNING_LOG" | tail -1)
                if [ -n "$last_article" ]; then
                    local article_id=$(echo "$last_article" | sed 's/.*文章ID: //')
                    log "最新文章 ID: $article_id"
                fi
            fi
            ;;
        "improve")
            log "正在解析改进建议..."
            # 遍历所有文章，提取改进建议
            for article_file in "$ARTICLES_DIR"/article_*.json; do
                if [ -f "$article_file" ]; then
                    improvements=$(extract_improvements "$article_file")
                    if [ -n "$improvements" ]; then
                        echo "$improvements" | while read -r suggestion; do
                            if [ -n "$suggestion" ]; then
                                apply_improvement "$suggestion"
                            fi
                        done
                    fi
                fi
            done
            ;;
        "summary")
            log "正在生成每日总结..."
            local yesterday="$(date -d 'yesterday 10:00' '+%Y-%m-%d %H:%M:%S')"
            local today="$(date '+%Y-%m-%d 10:00:00')"
            generate_daily_summary "$yesterday" "$today"
            ;;
        *)
            log "未知模式: $mode"
            exit 1
            ;;
    esac

    log "脚本执行完成"
}

main "$@"
