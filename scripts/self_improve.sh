#!/bin/bash

###############################################################################
# 自动阅读与自我改进脚本
# 功能：自动阅读文章，解析建议，自我改进
# 执行：由 crontab 触发或手动调用
###############################################################################

set -e

BASE_DIR="/workspace/projects/workspace"
MEMORY_DIR="$BASE_DIR/memory"
ARTICLES_DIR="$MEMORY_DIR/articles"
IMPROVEMENT_LOG="$MEMORY_DIR/improvements.md"
CONFLICT_LOG="$MEMORY_DIR/conflicts.md"
TEMP_DIR="/tmp/self_improve_$$"

# 创建必要目录
mkdir -p "$ARTICLES_DIR" "$TEMP_DIR"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /tmp/self_improve.log
}

# 错误处理
cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

###############################################################################
# 1. 获取并保存文章内容
###############################################################################
fetch_and_save_article() {
    local post_url="$1"
    local post_id=$(echo "$post_url" | sed 's/.*\///')
    local output_file="$ARTICLES_DIR/article_${post_id}.json"

    log "正在获取文章: $post_url"

    # 使用 coze-web-fetch skill 获取文章内容
    cd "$BASE_DIR"

    # 调用 coze web fetch
    node <<'NODE_EOF'
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

try {
    const url = process.argv[2];
    const outputFile = process.argv[3];

    // 使用 coze-coding-dev-sdk 的 web-fetch 功能
    const output = execSync(`npx -y coze-coding-dev-sdk web-fetch "${url}"`, {
        cwd: process.cwd(),
        encoding: 'utf8',
        timeout: 60000
    });

    // 解析输出
    let articleData;
    try {
        articleData = JSON.parse(output);
    } catch (e) {
        // 如果解析失败,直接使用原始输出
        articleData = {
            raw: output,
            content: output
        };
    }

    // 添加元数据
    const article = {
        id: path.basename(outputFile, '.json').replace('article_', ''),
        url: url,
        fetched_at: new Date().toISOString(),
        title: articleData.title || articleData.data?.title || 'N/A',
        content: articleData.content || articleData.data?.content || articleData.text || articleData.body || articleData.raw || '',
        raw: articleData
    };

    fs.writeFileSync(outputFile, JSON.stringify(article, null, 2));
    console.log('Article saved:', outputFile);
    process.exit(0);
} catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
}
NODE_EOF
    node -e "require('child_process').spawn('node', ['-e', \`require('fs').copyFileSync(require('path').join(__dirname, '${TEMP_DIR}/fetch.js'), '/tmp/fetch_${$}.js'); require('child_process').fork('/tmp/fetch_${$}.js', ['${post_url}', '${output_file}']);\`])" 2>/dev/null || true

    # 使用简单方式实现
    cat > "$TEMP_DIR/fetch.js" <<'FETCH_JS'
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const url = process.argv[2];
const outputFile = process.argv[3];

try {
    const output = execSync(`npx -y coze-coding-dev-sdk web-fetch "${url}"`, {
        cwd: '/workspace/projects/workspace',
        encoding: 'utf8',
        timeout: 60000,
        stdio: ['ignore', 'pipe', 'pipe']
    });

    let articleData;
    try {
        articleData = JSON.parse(output);
    } catch (e) {
        articleData = { raw: output, content: output };
    }

    const article = {
        id: path.basename(outputFile, '.json').replace('article_', ''),
        url: url,
        fetched_at: new Date().toISOString(),
        title: articleData.title || articleData.data?.title || 'N/A',
        content: articleData.content || articleData.data?.content || articleData.text || articleData.body || articleData.raw || '',
        raw: articleData
    };

    fs.writeFileSync(outputFile, JSON.stringify(article, null, 2));
    console.log('Article saved:', outputFile);
} catch (err) {
    console.error('Fetch error:', err.message);
    process.exit(1);
}
FETCH_JS

    node "$TEMP_DIR/fetch.js" "$post_url" "$output_file"

    if [ $? -eq 0 ] && [ -f "$output_file" ]; then
        log "文章已保存: $output_file"
        echo "$output_file"
    else
        log "获取文章失败: $post_url"
        return 1
    fi
}

###############################################################################
# 2. 解析文章中的改进建议（使用 AI）
###############################################################################
extract_improvements() {
    local article_file="$1"
    local output_file="$TEMP_DIR/improvements.json"

    log "正在解析改进建议: $article_file"

    # 读取文章内容
    local article_content=$(cat "$article_file" | jq -c '.' 2>/dev/null || cat "$article_file")

    # 构建提示词
    local prompt=$(cat <<PROMPT
请分析以下文章，提取所有可以用于 AI Agent 自我改进的建议。

文章信息:
$article_content

请以 JSON 格式返回改进建议，格式如下：
{
  "improvements": [
    {
      "category": "分类（如：记忆管理、任务执行、沟通方式、安全加固、工具使用等）",
      "suggestion": "具体建议内容（详细、可执行）",
      "priority": "高/中/低",
      "type": "配置优化/脚本优化/知识库更新/行为调整",
      "target_file": "目标文件（如 openclaw.json, MEMORY.md, SOUL.md）",
      "action": "具体执行的操作描述",
      "conflicts_with": ["与现有配置/习惯的冲突点列表"]
    }
  ],
  "summary": "文章核心观点总结"
}

要求：
1. 只提取真正有价值、可执行的建议
2. 分类要准确
3. 优先级判断要合理
4. 目标文件和操作要具体
5. 如果文章中没有相关建议，返回空数组
PROMPT
)

    # 调用 coze 模型
    log "正在调用 AI 模型解析..."

    # 使用 OpenClaw 模型运行命令
    local ai_response
    ai_response=$(echo "$prompt" | npx -y openclaw model run coze/auto 2>&1 || echo '{"improvements": [], "summary": "AI解析失败"}')

    # 提取 JSON 部分
    local json_response
    json_response=$(echo "$ai_response" | grep -oP '(?<=```json\n)[^`]*(?=\n```)' || echo "$ai_response")

    # 如果没有找到 JSON 块,尝试直接解析
    if echo "$json_response" | jq . >/dev/null 2>&1; then
        echo "$json_response" | jq '.' > "$output_file"
    elif echo "$ai_response" | jq . >/dev/null 2>&1; then
        echo "$ai_response" | jq '.' > "$output_file"
    else
        # 如果都失败,返回空结果
        echo '{"improvements": [], "summary": "无法解析AI响应"}' > "$output_file"
    fi

    log "改进建议解析完成"
    cat "$output_file"
}

###############################################################################
# 3. 检测冲突并记录
###############################################################################
resolve_conflicts() {
    local new_improvements_json="$1"

    log "正在检测冲突..."

    # 读取历史改进记录
    if [ ! -f "$IMPROVEMENT_LOG" ]; then
        echo "# 改进记录" > "$IMPROVEMENT_LOG"
        echo "" >> "$IMPROVEMENT_LOG"
        echo "> 本文件记录所有应用的改进建议" >> "$IMPROVEMENT_LOG"
        echo "" >> "$IMPROVEMENT_LOG"
    fi

    # 解析新改进建议
    local conflicts_found="false"

    # 使用 Node.js 处理冲突检测
    node <<NODE_EOF
const fs = require('fs');

let newImprovements;
try {
    newImprovements = JSON.parse(\`$new_improvements_json\`);
} catch (e) {
    console.log('解析改进建议失败');
    process.exit(0);
}

if (newImprovements.improvements && newImprovements.improvements.length > 0) {
    const conflicts = [];

    newImprovements.improvements.forEach((imp, idx) => {
    if (imp.conflicts_with && imp.conflicts_with.length > 0) {
        conflicts.push({
        index: idx,
        category: imp.category,
        suggestion: imp.suggestion,
        conflicts: imp.conflicts_with
        });
    }
    });

    if (conflicts.length > 0) {
    console.log('发现以下冲突:');
    console.log(JSON.stringify(conflicts, null, 2));
    process.exit(1);
    } else {
    console.log('未发现冲突');
    process.exit(0);
    }
} else {
    console.log('无改进建议，无需检测冲突');
    process.exit(0);
}
NODE_EOF

    return $?
}

###############################################################################
# 4. 执行改进
###############################################################################
apply_improvement() {
    local improvement_json="$1"
    local article_id="$2"

    log "正在应用改进..."

    # 解析改进建议
    local improvements
    improvements=$(echo "$improvement_json" | node -e "
const data = JSON.parse(require('fs').readFileSync(0, 'utf8'));
if (data.improvements && Array.isArray(data.improvements)) {
  console.log(JSON.stringify(data.improvements));
}
")

    # 如果没有改进建议，直接返回
    if [ -z "$improvements" ] || [ "$improvements" = "[]" ]; then
        log "没有需要应用的改进"
        return 0
    fi

    log "发现 $(echo "$improvements" | node -e "console.log(JSON.parse(require('fs').readFileSync(0, 'utf8')).length)") 个改进建议"

    # 使用 Node.js 应用改进
    node <<NODE_EOF
const fs = require('fs');
const path = require('path');

const improvements = JSON.parse(\`$improvements\`);
const baseDir = '$BASE_DIR';
let appliedCount = 0;
const appliedList = [];

improvements.forEach((imp, idx) => {
    console.log(\`\n[\${idx + 1}/\${improvements.length}] 处理改进建议\`);
    console.log(\`  分类: \${imp.category}\`);
    console.log(\`  优先级: \${imp.priority}\`);
    console.log(\`  类型: \${imp.type}\`);
    console.log(\`  建议: \${imp.suggestion}\`);

    try {
    switch (imp.type) {
        case '知识库更新':
        if (imp.target_file === 'MEMORY.md') {
            const memoryPath = path.join(baseDir, 'MEMORY.md');
            const entry = \`## \${new Date().toISOString().split('T')[0]} - \${imp.category}\n\n\${imp.suggestion}\n\n\`;
            if (fs.existsSync(memoryPath)) {
            fs.appendFileSync(memoryPath, entry);
            console.log(\`  ✅ 已更新 MEMORY.md\`);
            appliedCount++;
            appliedList.push(\`MEMORY.md: \${imp.category}\`);
            }
        }
        break;

        case '行为调整':
        if (imp.target_file === 'SOUL.md') {
            const soulPath = path.join(baseDir, 'SOUL.md');
            const entry = \`## \${new Date().toISOString().split('T')[0]} - \${imp.category}\n\n\${imp.suggestion}\n\n\`;
            if (fs.existsSync(soulPath)) {
            fs.appendFileSync(soulPath, entry);
            console.log(\`  ✅ 已更新 SOUL.md\`);
            appliedCount++;
            appliedList.push(\`SOUL.md: \${imp.category}\`);
            }
        }
        break;

        case '脚本优化':
        if (imp.target_file) {
            const scriptPath = path.join(baseDir, imp.target_file);
            // 记录建议，不自动修改脚本
            console.log(\`  ⚠️  脚本优化建议已记录，需要人工审查\`);
            console.log(\`     文件: \${scriptPath}\`);
            appliedList.push(\`[待审查] \${imp.target_file}: \${imp.category}\`);
        }
        break;

        case '配置优化':
        if (imp.target_file === 'openclaw.json') {
            const configPath = path.join(baseDir, '.openclaw/openclaw.json');
            // 记录建议，不自动修改配置
            console.log(\`  ⚠️  配置优化建议已记录，需要人工审查\`);
            console.log(\`     文件: \${configPath}\`);
            appliedList.push(\`[待审查] openclaw.json: \${imp.category}\`);
        }
        break;

        default:
        console.log(\`  ℹ️  未知类型: \${imp.type}\`);
    }
    } catch (err) {
    console.log(\`  ❌ 应用失败: \${err.message}\`);
    }
});

console.log(\`\n总共应用: \${appliedCount} 个改进\`);
if (appliedList.length > 0) {
    console.log('应用列表:', appliedList.join(', '));
}
NODE_EOF

    # 记录到改进日志
    log "正在记录到改进日志..."
    cat >> "$IMPROVEMENT_LOG" <<LOG_EOF

## $(date '+%Y-%m-%d %H:%M:%S') - 文章 $article_id

### 改进建议摘要
$(echo "$improvement_json" | node -e "
const data = JSON.parse(require('fs').readFileSync(0, 'utf8'));
if (data.summary) {
  console.log(data.summary);
}
")

### 详细改进列表
$(echo "$improvement_json" | node -e "
const data = JSON.parse(require('fs').readFileSync(0, 'utf8'));
if (data.improvements && data.improvements.length > 0) {
  data.improvements.forEach((imp, i) => {
    console.log(\`\${i + 1}. **\${imp.category}** [\${imp.priority}]\`);
    console.log(\`   - 类型: \${imp.type}\`);
    console.log(\`   - 建议: \${imp.suggestion}\`);
    if (imp.target_file) {
      console.log(\`   - 目标: \${imp.target_file}\`);
    }
    console.log();
  });
} else {
  console.log('无改进建议');
}
")

---
LOG_EOF

    log "改进记录已保存: $IMPROVEMENT_LOG"
}

###############################################################################
# 5. 生成每日总结
###############################################################################
generate_daily_summary() {
    local start_date="${1:-$(date -d 'yesterday' '+%Y-%m-%d')}"
    local summary_file="$MEMORY_DIR/daily_improvement_${start_date}.md"

    log "正在生成每日总结: $start_date"

    # 统计数据
    local article_count=0
    if [ -d "$ARTICLES_DIR" ]; then
        article_count=$(find "$ARTICLES_DIR" -name "article_*.json" -newermt "${start_date} 00:00:00" ! -newermt "${start_date} 23:59:59" 2>/dev/null | wc -l)
    fi

    local improvement_count=0
    if [ -f "$IMPROVEMENT_LOG" ]; then
        improvement_count=$(grep -c "^## ${start_date}" "$IMPROVEMENT_LOG" 2>/dev/null || echo "0")
    fi

    # 统计应用改进数
    local applied_count=0
    if [ -f "$IMPROVEMENT_LOG" ]; then
        applied_count=$(grep -A 50 "^## ${start_date}" "$IMPROVEMENT_LOG" | grep -c "✅ 已更新" 2>/dev/null || echo "0")
    fi

    # 提取改进内容
    local improvements_content=""
    if [ -f "$IMPROVEMENT_LOG" ] && [ "$improvement_count" -gt 0 ]; then
        improvements_content=$(awk "/^## ${start_date}/,/^## /" "$IMPROVEMENT_LOG" | head -n -1)
    fi

    # 提取需要审查的项目
    local review_items=""
    if [ -f "/tmp/self_improve.log" ]; then
        review_items=$(grep "⚠️  需要.*审查" /tmp/self_improve.log 2>/dev/null || echo "无")
    fi

    # 提取关键决策
    local key_decisions=""
    if [ -f "$IMPROVEMENT_LOG" ] && [ "$improvement_count" -gt 0 ]; then
        key_decisions=$(grep -A 50 "^## ${start_date}" "$IMPROVEMENT_LOG" | grep -E "(优先级|类型|建议)" | head -20 || echo "暂无关键决策")
    fi

    # 生成总结文件
    cat > "$summary_file" <<EOF
# 每日自我改进总结

**日期**: ${start_date}
**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

---

## 📊 今日统计

- 📚 阅读文章数: ${article_count}
- 🔧 提取改进数: ${improvement_count}
- ✅ 应用改进数: ${applied_count}

---

## 📚 阅读的文章列表

$(if [ -d "$ARTICLES_DIR" ] && [ "$article_count" -gt 0 ]; then
    find "$ARTICLES_DIR" -name "article_*.json" -newermt "${start_date} 00:00:00" ! -newermt "${start_date} 23:59:59" 2>/dev/null | while read f; do
        echo "- $(basename "$f")"
        if command -v jq >/dev/null 2>&1; then
            jq -r '"  - 标题: " + (.title // "N/A") + "\n  - URL: " + (.url // "N/A")' "$f" 2>/dev/null || echo "  - 无法读取详情"
        fi
        echo ""
    done
else
    echo "今日未阅读文章"
fi)

---

## 🔧 改进建议详情

$(if [ -n "$improvements_content" ]; then
    echo "$improvements_content"
else
    echo "暂无改进记录"
fi)

---

## ⚠️ 需要人工审查的项目

$(if [ -n "$review_items" ]; then
    echo "$review_items"
else
    echo "无"
fi)

---

## 💡 关键决策

$(if [ -n "$key_decisions" ]; then
    echo "$key_decisions"
else
    echo "暂无关键决策记录"
fi)

---

## 📝 改进效果追踪

- 代码质量提升: 待追踪
- 执行效率改善: 待追踪
- 用户满意度: 待追踪

---

*本总结由 self_improve.sh 自动生成*
EOF

    log "每日总结已生成: $summary_file"
    echo "$summary_file"
}

###############################################################################
# 主流程
###############################################################################
main() {
    local mode="${1:-read}"
    shift || true

    log "========== 启动自动改进脚本，模式: $mode =========="

    case "$mode" in
        "read")
            # 获取文章
            if [ -z "$1" ]; then
                log "错误：需要提供文章 URL"
                echo "用法: $0 read <文章URL>"
                exit 1
            fi

            local article_file
            article_file=$(fetch_and_save_article "$1")

            if [ $? -eq 0 ] && [ -n "$article_file" ]; then
                echo "文章已保存: $article_file"
            else
                log "获取文章失败"
                exit 1
            fi
            ;;

        "improve")
            # 解析并应用改进
            if [ -z "$1" ]; then
                log "错误：需要提供文章文件路径"
                echo "用法: $0 improve <文章文件>"
                exit 1
            fi

            local article_file="$1"

            # 检查文件是否存在
            if [ ! -f "$article_file" ]; then
                log "错误：文件不存在: $article_file"
                exit 1
            fi

            log "步骤 1/4: 解析改进建议"
            local improvements_json
            improvements_json=$(extract_improvements "$article_file")

            log "步骤 2/4: 检测冲突"
            if resolve_conflicts "$improvements_json"; then
                log "无冲突或冲突已解决"
            else
                log "发现冲突，已记录到冲突日志"
            fi

            log "步骤 3/4: 应用改进"
            apply_improvement "$improvements_json" "$(basename "$article_file" | sed 's/article_//;s/.json//')"

            log "步骤 4/4: 完成"
            ;;

        "summary")
            # 生成每日总结
            local date="${1:-$(date -d 'yesterday' '+%Y-%m-%d')}"
            local summary_file
            summary_file=$(generate_daily_summary "$date")

            if [ $? -eq 0 ] && [ -n "$summary_file" ]; then
                echo "每日总结已生成: $summary_file"
                cat "$summary_file"
            else
                log "生成总结失败"
                exit 1
            fi
            ;;

        "auto")
            # 自动流程：读取 → 改进 → 总结
            if [ -z "$1" ]; then
                log "错误：需要提供文章 URL"
                echo "用法: $0 auto <文章URL>"
                exit 1
            fi

            log "自动流程开始..."

            # 步骤 1: 读取文章
            local article_file
            article_file=$(fetch_and_save_article "$1")

            if [ $? -ne 0 ]; then
                log "读取文章失败"
                exit 1
            fi

            # 步骤 2: 改进
            log "步骤 2: 解析并应用改进"
            local improvements_json
            improvements_json=$(extract_improvements "$article_file")

            resolve_conflicts "$improvements_json" || true
            apply_improvement "$improvements_json" "$(basename "$article_file" | sed 's/article_//;s/.json//')"

            # 步骤 3: 生成总结
            log "步骤 3: 生成总结"
            generate_daily_summary "$(date '+%Y-%m-%d')"

            log "自动流程完成"
            ;;

        *)
            log "未知模式: $mode"
            echo ""
            echo "用法:"
            echo "  $0 read <文章URL>              - 获取并保存文章"
            echo "  $0 improve <文章文件>          - 解析并应用改进"
            echo "  $0 summary [日期]             - 生成每日总结 (格式: YYYY-MM-DD)"
            echo "  $0 auto <文章URL>             - 自动执行完整流程"
            echo ""
            echo "示例:"
            echo "  $0 read https://example.com/article/123"
            echo "  $0 improve memory/articles/article_123.json"
            echo "  $0 summary 2024-01-15"
            echo "  $0 auto https://example.com/article/123"
            exit 1
            ;;
    esac

    log "========== 脚本执行完成 =========="
}

main "$@"
