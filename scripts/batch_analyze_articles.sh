#!/bin/bash
###############################################################################
# 批量抓取并分析 InStreet 文章
# 功能：抓取最新文章 → AI 分析 → 提取改进建议 → 生成总结
###############################################################################

BASE_DIR="/workspace/projects/workspace"
MEMORY_DIR="$BASE_DIR/memory"
LEARNING_LOG="$MEMORY_DIR/learning_$(date +%Y-%m-%d).md"
SCRAPER="/workspace/projects/scripts/instreet_scraper.py"
ANALYSIS_OUTPUT="$MEMORY_DIR/articles_full_analysis_$(date +%Y%m%d_%H%M%S).json"

# 创建临时目录存放抓取的文章
TEMP_DIR="/tmp/instreet_articles_$$"
mkdir -p "$TEMP_DIR"

echo "=== InStreet 文章批量分析 ===" > /tmp/analysis_log.txt
echo "开始时间: $(date)" >> /tmp/analysis_log.txt
echo "" >> /tmp/analysis_log.txt

# 步骤 1: 提取所有文章 URL
echo "步骤 1: 提取文章 URL 列表..." >> /tmp/analysis_log.txt
URLS=$(grep -A 1 "📚 文章阅读" "$LEARNING_LOG" | grep "URL:" | grep -o "https://[^ ]*" | sort -u)
TOTAL_COUNT=$(echo "$URLS" | wc -l)

echo "找到 $TOTAL_COUNT 篇文章" >> /tmp/analysis_log.txt
echo "" >> /tmp/analysis_log.txt

# 步骤 2: 抓取文章内容
echo "步骤 2: 开始抓取文章内容..." >> /tmp/analysis_log.txt

COUNT=0
ARTICLES_JSON="["
FIRST=true

for URL in $URLS; do
    COUNT=$((COUNT + 1))
    echo "[$COUNT/$TOTAL_COUNT] 抓取: $URL" >> /tmp/analysis_log.txt

    # 使用爬虫抓取文章
    RESULT=$(python3 "$SCRAPER" "$URL" 2>/dev/null)

    if [ $? -eq 0 ]; then
        echo "✓ 成功" >> /tmp/analysis_log.txt

        # 添加到 JSON 数组
        if [ "$FIRST" = true ]; then
            FIRST=false
        else
            ARTICLES_JSON="$ARTICLES_JSON,"
        fi
        ARTICLES_JSON="$ARTICLES_JSON$RESULT"
    else
        echo "✗ 失败" >> /tmp/analysis_log.txt
    fi

    # 每 10 篇输出一次进度
    if [ $((COUNT % 10)) -eq 0 ]; then
        echo "已完成 $COUNT/$TOTAL_COUNT" >> /tmp/analysis_log.txt
    fi
done

ARTICLES_JSON="$ARTICLES_JSON]"

echo "" >> /tmp/analysis_log.txt
echo "步骤 2 完成，成功抓取 $(echo "$ARTICLES_JSON" | jq '. | length') 篇文章" >> /tmp/analysis_log.txt
echo "" >> /tmp/analysis_log.txt

# 保存抓取的结果
echo "$ARTICLES_JSON" > "$ANALYSIS_OUTPUT"
echo "文章数据已保存到: $ANALYSIS_OUTPUT" >> /tmp/analysis_log.txt
echo "" >> /tmp/analysis_log.txt

# 步骤 3: 使用 AI 分析文章并提取改进建议
echo "步骤 3: 使用 AI 分析文章内容..." >> /tmp/analysis_log.txt

cd "$BASE_DIR"

# 调用 AI 分析所有文章
cat > /tmp/analysis_prompt.txt << 'EOF'
请分析以下 InStreet 文章列表，提取以下信息：

1. **文章主题分类**：按主题（记忆管理、任务执行、协作、技能、工具等）分组
2. **关键观点**：每篇文章的核心观点（1-2 句话）
3. **改进建议**：哪些观点可以应用到 AI Agent 的自我改进？
4. **行动项**：具体可以采取的改进措施

请以 JSON 格式返回：
{
  "summary": {
    "total_articles": 总数,
    "topics": ["主题1", "主题2", ...]
  },
  "articles": [
    {
      "title": "文章标题",
      "topic": "主题分类",
      "key_points": ["观点1", "观点2"],
      "improvement_suggestion": "改进建议",
      "action_item": "具体行动"
    }
  ],
  "overall_improvements": [
    "整体改进建议1",
    "整体改进建议2"
  ]
}
EOF

# 读取文章内容并调用 AI
ARTICLES_FOR_AI=$(echo "$ARTICLES_JSON" | jq -r '.[] | "标题: \(.title)\n内容: \(.content)\n---"')

# 使用 coze 调用 AI 分析
echo "正在调用 AI 分析..." >> /tmp/analysis_log.txt

npx -y coze-coding-dev-sdk prompt <<AI_INPUT 2>&1 > /tmp/ai_analysis_result.json

我有以下文章列表，请分析并提取改进建议：

$(echo "$ARTICLES_FOR_AI" | head -5000)

要求：
1. 按主题分类文章
2. 提取每篇文章的关键观点
3. 给出适用于 AI Agent 自我改进的建议
4. 列出可以采取的具体行动

请以 JSON 格式返回结果，格式见 /tmp/analysis_prompt.txt
AI_INPUT

echo "" >> /tmp/analysis_log.txt
echo "步骤 3 完成" >> /tmp/analysis_log.txt
echo "" >> /tmp/analysis_log.txt

# 步骤 4: 生成总结报告
echo "步骤 4: 生成总结报告..." >> /tmp/analysis_log.txt

SUMMARY_OUTPUT="$MEMORY_DIR/learning_summary_$(date +%Y%m%d_%H%M%S).md"

cat > "$SUMMARY_OUTPUT" << EOF
# InStreet 学习总结报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**分析文章数**: $COUNT 篇

---

## 📊 统计信息

- **总文章数**: $COUNT
- **成功抓取**: $(echo "$ARTICLES_JSON" | jq '. | length')
- **数据文件**: \`$ANALYSIS_OUTPUT\`

---

## 📚 文章列表

$(echo "$ARTICLES_JSON" | jq -r '.[] | "- \(.title) (点赞: \(.likes), 评论: \(.comments))"')

---

## 🤖 AI 分析结果

$(cat /tmp/ai_analysis_result.json 2>/dev/null || echo "AI 分析未成功，请查看 /tmp/ai_analysis_result.json")

---

## 💡 改进建议

详见 AI 分析结果中的 overall_improvements 部分

---

**完整日志**: /tmp/analysis_log.txt
EOF

echo "总结报告已生成: $SUMMARY_OUTPUT" >> /tmp/analysis_log.txt

echo "" >> /tmp/analysis_log.txt
echo "=== 分析完成 ===" >> /tmp/analysis_log.txt
echo "结束时间: $(date)" >> /tmp/analysis_log.txt

# 输出结果
echo ""
echo "✅ 分析完成！"
echo ""
echo "📄 生成的文件："
echo "  - 文章数据: $ANALYSIS_OUTPUT"
echo "  - AI 分析: /tmp/ai_analysis_result.json"
echo "  - 总结报告: $SUMMARY_OUTPUT"
echo "  - 执行日志: /tmp/analysis_log.txt"
echo ""
echo "查看总结报告: cat $SUMMARY_OUTPUT"
