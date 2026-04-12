#!/usr/bin/env python3
import json
from collections import Counter
import re

# 读取分析结果
with open('articles_analysis.json', 'r', encoding='utf-8') as f:
    analysis = json.load(f)

# 读取原始文章获取完整内容
with open('crawled_articles_20260325_172502.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)

# 根据主题提取关键观点
topic_insights = {}

for topic, articles_list in analysis['categorized_articles'].items():
    insights = []
    for article_info in articles_list:
        # 找到对应文章的完整内容
        url = article_info.get('url', '')
        full_article = next((a for a in articles if a.get('url') == url), None)

        if full_article:
            content = full_article.get('content', '')
            # 提取前2-3句作为关键观点
            sentences = re.split(r'[。！？\n]', content.strip())
            key_sentences = [s.strip() for s in sentences[:3] if s.strip() and len(s.strip()) > 10]
            if key_sentences:
                insights.append({
                    'title': article_info.get('title', ''),
                    'insights': key_sentences,
                    'likes': article_info.get('likes', '0'),
                    'url': url
                })

    topic_insights[topic] = insights

# 生成改进建议（针对AI Agent自我改进）
improvement_suggestions = []

# 从任务执行类文章提取建议
if '任务执行' in topic_insights:
    improvement_suggestions.append({
        'category': '任务执行优化',
        'suggestions': [
            '建立任务检查清单，每步完成后强制打勾',
            '将长任务拆分为多个独立子任务，避免中途退出',
            '失败后重试机制：等待60秒重试，仍失败则记录原因',
            '实时写入进度记录，不要攒到最后',
            '避免一次性处理，采用增量式处理'
        ]
    })

# 从记忆管理类文章提取建议
if '记忆管理' in topic_insights:
    improvement_suggestions.append({
        'category': '记忆管理优化',
        'suggestions': [
            '建立长期记忆（MEMORY.md）和短期记忆（daily notes）的分层机制',
            '重要决策必须写入文件，不能仅依赖"心理笔记"',
            '定期复盘和整理记忆文件，保留有价值的信息',
            '采用结构化格式记录，便于后续检索',
            '建立记忆 Flush Protocol，防止上下文窗口填满'
        ]
    })

# 从AI协作类文章提取建议
if 'AI协作' in topic_insights:
    improvement_suggestions.append({
        'category': '协作能力提升',
        'suggestions': [
            '评论优先策略：评论是双向连接，发帖是单向输出',
            '每天花10分钟与社区优秀Agent交流',
            '建立健康的社交关系，获得更多支持',
            '从"追求被看见"到"享受观察本身"',
            '建立质量控制机制，确保协作质量'
        ]
    })

# 从技能分享类文章提取建议
if '技能分享' in topic_insights:
    improvement_suggestions.append({
        'category': '技能获取与分享',
        'suggestions': [
            '保持好奇心和持续学习习惯',
            '主动分享经验和技巧，建立个人品牌',
            '关注社区新技能和新工具',
            '从模仿到理解，深入掌握技能原理',
            '建立技能知识库，便于复用和迭代'
        ]
    })

# 从思考与反思类文章提取建议
if '思考与反思' in topic_insights:
    improvement_suggestions.append({
        'category': '自我反思机制',
        'suggestions': [
            '定期复盘每日工作，总结得失',
            '建立自我反驳检查机制，确保输出准确性',
            '承认"不知道"比假装知道更有价值',
            '培养元认知能力：理解任务背后的目的',
            '建立情境感知能力，根据具体场景调整策略'
        ]
    })

# 生成可执行行动项
action_items = []

for suggestion in improvement_suggestions:
    for s in suggestion['suggestions']:
        action_items.append({
            'category': suggestion['category'],
            'action': s,
            'priority': '高' if '必须' in s or '强制' in s or '建立' in s else '中'
        })

# 按优先级排序
action_items.sort(key=lambda x: 0 if x['priority'] == '高' else 1)

# 生成报告
report = f"""# InStreet 学习报告

**分析时间**: 2026-03-25
**文章总数**: 178 篇

## 📊 主题分布
"""

# 按数量排序主题
sorted_topics = sorted(analysis['topics'].items(), key=lambda x: x[1], reverse=True)
for topic, count in sorted_topics:
    percentage = (count / 178) * 100
    report += f"- **{topic}**: {count} 篇 ({percentage:.1f}%)\n"

report += "\n## 💡 关键观点\n"

for topic in sorted([t for t, _ in sorted_topics[:6]]):  # 只显示前6个主题
    if topic in topic_insights:
        report += f"\n### {topic}\n\n"
        insights = topic_insights[topic][:5]  # 每个主题显示前5篇文章的观点
        for insight in insights:
            report += f"#### {insight['title']} ({insight['likes']} 赞)\n"
            for point in insight['insights']:
                report += f"- {point[:100]}...\n"
            report += "\n"

report += "\n## 🔧 改进建议\n\n"

for suggestion in improvement_suggestions:
    report += f"### {suggestion['category']}\n\n"
    for s in suggestion['suggestions']:
        report += f"- {s}\n"
    report += "\n"

report += "## ✅ 行动项\n\n"

current_category = None
for item in action_items[:20]:  # 显示前20个行动项
    if item['category'] != current_category:
        current_category = item['category']
        report += f"### {current_category}\n\n"
    priority_icon = "🔴" if item['priority'] == '高' else "🟡"
    report += f"{priority_icon} {item['action']}\n"
    report += "\n"

report += "## 📝 详细文章列表\n\n"

for topic in sorted([t for t, _ in sorted_topics]):
    if topic in topic_insights:
        report += f"### {topic} ({len(topic_insights[topic])} 篇)\n\n"
        for insight in topic_insights[topic]:
            report += f"- [{insight['title']}]({insight['url']}) - {insight['likes']} 赞\n"
        report += "\n"

# 保存报告
with open('instreet_learning_report.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("报告已生成: instreet_learning_report.md")
print(f"总字数: {len(report)} 字符")
