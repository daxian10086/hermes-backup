#!/bin/bash
###############################################################################
# 批量抓取并分析 InStreet 文章（简化版）
###############################################################################

BASE_DIR="/workspace/projects/workspace"
MEMORY_DIR="$BASE_DIR/memory"
LEARNING_LOG="$MEMORY_DIR/learning_$(date +%Y-%m-%d).md"
SCRAPER="/workspace/projects/scripts/instreet_scraper.py"

echo "=== 开始批量抓取 InStreet 文章 ==="
echo "开始时间: $(date)"
echo ""

# 提取文章 URL
echo "提取文章 URL..."
URLS=$(grep -A 2 "📚 文章阅读" "$LEARNING_LOG" | grep "**URL**" | grep -o "https://[^ ]*" | sort -u)
TOTAL=$(echo "$URLS" | wc -l)

echo "找到 $TOTAL 篇文章"
echo ""

# 创建输出文件
OUTPUT_FILE="$MEMORY_DIR/crawled_articles_$(date +%Y%m%d_%H%M%S).json"
echo "[" > "$OUTPUT_FILE"

# 抓取文章
COUNT=0
FIRST=true

for URL in $URLS; do
    COUNT=$((COUNT + 1))
    echo -ne "\r[$COUNT/$TOTAL] 抓取中..."

    # 抓取文章
    RESULT=$(python3 "$SCRAPER" "$URL" 2>/dev/null)

    if [ $? -eq 0 ] && [ -n "$RESULT" ]; then
        if [ "$FIRST" = true ]; then
            FIRST=false
        else
            echo "," >> "$OUTPUT_FILE"
        fi
        echo "$RESULT" >> "$OUTPUT_FILE"
    fi

    # 每 20 篇显示一次进度
    if [ $((COUNT % 20)) -eq 0 ]; then
        echo -ne "\n已完成 $COUNT/$TOTAL\n"
    fi
done

echo "]" >> "$OUTPUT_FILE"

echo ""
echo ""
echo "✅ 抓取完成！"
echo "📄 输出文件: $OUTPUT_FILE"
echo "📊 成功抓取: $(jq '. | length' "$OUTPUT_FILE" 2>/dev/null || echo 0) 篇"
echo ""
echo "开始时间: $(date)"
