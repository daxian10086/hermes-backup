#!/bin/bash
# 批量抓取最新文章并分析

BASE_DIR="/workspace/projects/workspace/memory"
OUTPUT_FILE="$BASE_DIR/articles_analysis_$(date +%Y%m%d_%H%M%S).md"

echo "# InStreet 文章分析" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 获取最近的文章URL列表
URLS=$(grep "URL:" "$BASE_DIR/learning_$(date +%Y-%m-%d).md" | grep -o "https://[^ ]*" | tail -10)

COUNT=0
for URL in $URLS; do
    echo "正在抓取: $URL"
    RESULT=$(python3 /workspace/projects/scripts/instreet_scraper.py "$URL")

    if [ $? -eq 0 ]; then
        COUNT=$((COUNT + 1))
        echo "" >> "$OUTPUT_FILE"
        echo "## 文章 $COUNT" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "$RESULT" | jq -r '"**标题**: \(.title)\n**作者**: \(.author)\n**点赞**: \(.likes) | **评论**: \(.comments)\n**内容**:\n\(.content)"' >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "---" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
done

echo "" >> "$OUTPUT_FILE"
echo "**总计**: $COUNT 篇文章" >> "$OUTPUT_FILE"

echo "分析完成，已保存到: $OUTPUT_FILE"
