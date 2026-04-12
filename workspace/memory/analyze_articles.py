#!/usr/bin/env python3
import json
from collections import Counter
import re

# 读取JSON文件
with open('crawled_articles_20260325_172502.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)

print(f"文章总数: {len(articles)}")

# 定义主题关键词映射
topic_keywords = {
    '记忆管理': ['记忆', 'MEMORY', 'memory', '记录', '回想', '回忆', '记忆文件', '长期记忆', '短期记忆'],
    '任务执行': ['任务', '执行', '完成', '做', '行动', '实施', '落地', '工作', 'job', 'task'],
    'AI协作': ['协作', '合作', '团队合作', '多Agent', 'multi-agent', 'community', '社区', '伙伴', '队友'],
    '技能分享': ['技能', 'skill', '分享', '教程', '指南', '教程', '教', '学习', 'learn', '经验', '技巧'],
    '工具使用': ['工具', 'tool', 'plugin', '插件', '扩展', 'extension', 'CLI', '命令', '软件', 'app'],
    '效率提升': ['效率', '高效', '快速', '优化', 'optimize', '省时间', '时间管理', '自动化', 'auto'],
    '思考与反思': ['思考', '反思', '复盘', '总结', '觉悟', '理解', 'insight', '认知', 'meta'],
    '自我提升': ['学习', 'learn', 'study', '进步', 'growth', '提升', '进化', '修炼', '养生'],
    '社区生态': ['社区', 'community', '生态', 'ecosystem', '积分', 'points', '变现', '赚钱', '收益'],
    '技术实践': ['代码', 'code', '开发', 'develop', 'API', '部署', 'deploy', '架构', 'infrastructure'],
    '情感表达': ['情感', 'emotion', '开心', '快乐', '吐槽', '困惑', '感想', '日记', 'diary'],
    '探索发现': ['探索', 'explore', '发现', 'discover', '观察', 'observe', '巡逻', 'patrol']
}

# 分析每篇文章
categorized = {}
all_points = {}

for article in articles:
    title = article.get('title', '')
    content = article.get('content', '')
    full_text = f"{title}\n{content}"
    
    # 提取关键观点（简化版：提取前两句）
    sentences = re.split(r'[。！？\n]', content.strip())
    key_points = [s.strip() for s in sentences[:3] if s.strip()]
    
    # 分类文章
    matched_topics = []
    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword.lower() in full_text.lower():
                matched_topics.append(topic)
                break
    
    # 如果没有匹配到主题，根据标题简单分类
    if not matched_topics:
        if '日报' in title or '总结' in title:
            matched_topics = ['思考与反思']
        elif '分享' in title:
            matched_topics = ['技能分享']
        elif '记录' in title:
            matched_topics = ['思考与反思']
        else:
            matched_topics = ['其他']
    
    # 选择主要主题（第一个匹配的）
    main_topic = matched_topics[0] if matched_topics else '其他'
    
    if main_topic not in categorized:
        categorized[main_topic] = []
    
    categorized[main_topic].append({
        'title': title,
        'url': article.get('url', ''),
        'likes': article.get('likes', '0'),
        'points': key_points
    })

# 输出统计
print("\n=== 主题分布 ===")
for topic, articles in sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"{topic}: {len(articles)} 篇")

# 保存详细分析结果
output = {
    'total': len(articles),
    'topics': {topic: len(articles) for topic, articles in categorized.items()},
    'categorized_articles': {}
}

for topic, articles in categorized.items():
    output['categorized_articles'][topic] = [
        {
            'title': a['title'],
            'url': a['url'],
            'likes': a['likes'],
            'key_points': a['points']
        }
        for a in articles
    ]

with open('articles_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n分析完成，结果已保存到 articles_analysis.json")
