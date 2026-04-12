#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票技术知识学习爬虫
每天0点自动执行，爬取知乎、CSDN等技术分析文章
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os

class StockKnowledgeScraper:
    """股票知识爬虫"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.knowledge = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'topics': [],
            'articles': []
        }

    def crawl_zhihu(self, keyword):
        """爬取知乎技术分析文章"""
        print(f"正在爬取知乎：{keyword}")

        # 知乎搜索URL
        url = f"https://www.zhihu.com/api/v4/search_v3"
        params = {
            't': 'general',
            'q': keyword,
            'correction': 1,
            'offset': 0,
            'limit': 5
        }

        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = []

                for item in data.get('data', []):
                    if item.get('type') == 'search_result':
                        obj = item.get('object', {})
                        title = obj.get('title', '')
                        excerpt = obj.get('excerpt', '')
                        url = obj.get('url', '')

                        if title:
                            articles.append({
                                'title': title,
                                'excerpt': excerpt,
                                'url': url,
                                'source': '知乎'
                            })

                return articles
            else:
                print(f"知乎请求失败：{response.status_code}")
                return []

        except Exception as e:
            print(f"知乎爬取错误：{e}")
            return []

    def crawl_csdn(self, keyword):
        """爬取CSDN技术分析文章"""
        print(f"正在爬取CSDN：{keyword}")

        url = f"https://so.csdn.net/api/v3/search"
        params = {
            'q': keyword,
            't': 'blog',
            'p': 1,
            's': 0,
            'tm': 0
        }

        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = []

                for item in data.get('result', {}).get('data', [], [])[:5]:
                    title = item.get('title', '').replace('<em>', '').replace('</em>', '')
                    summary = item.get('summary', '').replace('<em>', '').replace('</em>', '')
                    url = item.get('url', '')
                    author = item.get('nickname', '')

                    if title:
                        articles.append({
                            'title': title,
                            'excerpt': summary,
                            'url': url,
                            'author': author,
                            'source': 'CSDN'
                        })

                return articles
            else:
                print(f"CSDN请求失败：{response.status_code}")
                return []

        except Exception as e:
            print(f"CSDN爬取错误：{e}")
            return []

    def get_article_content(self, url):
        """获取文章详细内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # 移除广告和无关元素
                for tag in soup(['script', 'style', 'nav', 'footer']):
                    tag.decompose()

                # 获取主要内容
                if 'zhihu' in url:
                    content = soup.find('div', class_='Post-RichText')
                elif 'csdn' in url:
                    content = soup.find('div', class_='markdown_views')
                else:
                    content = soup.find('article') or soup.find('div', class_='content')

                if content:
                    text = content.get_text('\n', strip=True)
                    return text[:2000]  # 限制长度

            return ""
        except Exception as e:
            print(f"获取文章内容错误：{e}")
            return ""

    def learn_knowledge(self):
        """执行知识学习"""
        print("=" * 50)
        print(f"开始学习：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        # 学习主题
        topics = [
            "股票K线图基础",
            "MACD指标详解",
            "KDJ指标实战",
            "RSI指标应用",
            "移动平均线策略",
            "成交量分析",
            "布林带使用技巧"
        ]

        all_articles = []

        for topic in topics:
            print(f"\n学习主题：{topic}")
            self.knowledge['topics'].append(topic)

            # 爬取知乎
            zhihu_articles = self.crawl_zhihu(topic)
            all_articles.extend(zhihu_articles)
            time.sleep(2)  # 避免请求过快

            # 爬取CSDN
            csdn_articles = self.crawl_csdn(topic)
            all_articles.extend(csdn_articles)
            time.sleep(2)

        # 去重
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                unique_articles.append(article)

        self.knowledge['articles'] = unique_articles

        print(f"\n学习完成！共获取 {len(unique_articles)} 篇文章")
        return self.knowledge

    def save_to_file(self, output_file):
        """保存学习结果到文件"""
        knowledge = self.learn_knowledge()

        # 生成Markdown格式
        md_content = f"""# 股票技术知识学习笔记

**日期**: {knowledge['date']}
**学习时间**: {knowledge['timestamp']}
**文章数量**: {len(knowledge['articles'])}

## 学习主题
"""
        for topic in knowledge['topics']:
            md_content += f"- {topic}\n"

        md_content += f"\n## 学习文章\n\n"

        for i, article in enumerate(knowledge['articles'], 1):
            md_content += f"""### {i}. {article['title']}

**来源**: {article['source']}
**链接**: {article.get('url', 'N/A')}

**摘要**:
{article.get('excerpt', '暂无摘要')}

---

"""

        # 保存文件
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"\n学习笔记已保存：{output_file}")

        # 同时保存JSON格式
        json_file = output_file.replace('.md', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, ensure_ascii=False, indent=2)

        print(f"学习数据已保存：{json_file}")

        return knowledge


def main():
    """主函数"""
    # 获取当前日期
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = f"/workspace/projects/workspace/memory/股票学习笔记-{today}.md"

    # 创建爬虫实例
    scraper = StockKnowledgeScraper()

    # 执行学习
    scraper.save_to_file(output_file)

    print("\n" + "=" * 50)
    print("学习任务完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
