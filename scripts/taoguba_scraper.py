#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘股吧爬虫 - 获取股票讨论、实战经验、技术分析
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os
import re

class TaogubaScraper:
    """淘股吧爬虫"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = "https://www.taoguba.com.cn"

    def get_hot_topics(self):
        """获取热门话题"""
        print("正在获取热门话题...")

        url = f"{self.base_url}/"

        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                topics = []
                # 获取热门话题（根据实际HTML结构调整选择器）
                hot_items = soup.find_all('div', class_='topic-item')[:10]

                for item in hot_items:
                    title_elem = item.find('a', class_='title')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get('href', '')
                        if link and not link.startswith('http'):
                            link = self.base_url + link

                        # 获取回复数
                        reply_elem = item.find('span', class_='reply-count')
                        reply_count = reply_elem.get_text(strip=True) if reply_elem else '0'

                        topics.append({
                            'title': title,
                            'link': link,
                            'reply_count': reply_count
                        })

                return topics
            else:
                print(f"获取热门话题失败：{response.status_code}")
                return []

        except Exception as e:
            print(f"获取热门话题错误：{e}")
            return []

    def get_stock_discussion(self, stock_code):
        """获取指定股票的讨论"""
        print(f"正在获取股票 {stock_code} 的讨论...")

        url = f"{self.base_url}/search?q={stock_code}"

        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                discussions = []
                items = soup.find_all('div', class_='discussion-item')[:10]

                for item in items:
                    title_elem = item.find('a', class_='title')
                    author_elem = item.find('span', class_='author')
                    time_elem = item.find('span', class_='time')

                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        author = author_elem.get_text(strip=True) if author_elem else '匿名'
                        post_time = time_elem.get_text(strip=True) if time_elem else '未知'

                        discussions.append({
                            'title': title,
                            'author': author,
                            'time': post_time
                        })

                return discussions
            else:
                return []

        except Exception as e:
            print(f"获取股票讨论错误：{e}")
            return []

    def get_article_content(self, url):
        """获取文章内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # 移除广告和无关元素
                for tag in soup(['script', 'style', 'nav', 'footer']):
                    tag.decompose()

                # 获取主要内容
                content = soup.find('div', class_='article-content') or soup.find('div', class_='post-content')

                if content:
                    text = content.get_text('\n', strip=True)
                    return text[:1500]  # 限制长度

            return ""

        except Exception as e:
            print(f"获取文章内容错误：{e}")
            return ""

    def extract_sentiment(self, text):
        """简单的情绪分析"""
        positive_words = ['看好', '上涨', '突破', '强势', '机会', '买入', '牛', '暴涨', '大涨']
        negative_words = ['看空', '下跌', '破位', '弱势', '风险', '卖出', '熊', '暴跌', '大跌']

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            return '积极'
        elif negative_count > positive_count:
            return '消极'
        else:
            return '中性'

    def run_scraper(self):
        """执行爬虫"""
        print("=" * 50)
        print("淘股吧爬虫启动")
        print("=" * 50)

        data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'hot_topics': [],
            'stock_discussions': [],
            'market_sentiment': '中性'
        }

        # 获取热门话题
        hot_topics = self.get_hot_topics()
        data['hot_topics'] = hot_topics
        time.sleep(2)

        # 获取热门股票的讨论
        hot_stocks = ['000001', '600036', '600519', '000858']

        for stock in hot_stocks:
            discussions = self.get_stock_discussion(stock)
            if discussions:
                data['stock_discussions'].extend(discussions)
            time.sleep(2)

        # 分析市场情绪
        all_text = ' '.join([t['title'] for t in hot_topics])
        data['market_sentiment'] = self.extract_sentiment(all_text)

        print(f"\n爬取完成！")
        print(f"热门话题: {len(hot_topics)} 条")
        print(f"股票讨论: {len(data['stock_discussions'])} 条")
        print(f"市场情绪: {data['market_sentiment']}")

        return data


def save_to_file(data):
    """保存数据到文件"""

    # 生成Markdown
    md_content = f"""# 淘股吧每日情报

**日期**: {data['date']}
**爬取时间**: {datetime.now().strftime('%H:%M:%S')}
**市场情绪**: {data['market_sentiment']}

## 热门话题
"""

    for i, topic in enumerate(data['hot_topics'][:5], 1):
        md_content += f"""
### {i}. {topic['title']}

- 回复数: {topic['reply_count']}
- 链接: {topic['link']}

---

"""

    md_content += f"""
## 股票讨论精选
"""

    for i, discussion in enumerate(data['stock_discussions'][:5], 1):
        md_content += f"""
### {i}. {discussion['title']}

- 作者: {discussion['author']}
- 时间: {discussion['time']}

---

"""

    md_content += f"""
## 情绪分析

**整体情绪**: {data['market_sentiment']}

**备注**:
- 积极: 看好、上涨、突破等关键词
- 消极: 看空、下跌、破位等关键词
- 中性: 没有明显的情绪倾向

---

**爬取状态**: 完成 ✅
**下次更新**: 明天0点
"""

    # 保存文件
    today = datetime.now().strftime('%Y-%m-%d')
    md_file = f"/workspace/projects/workspace/memory/淘股吧情报-{today}.md"
    json_file = f"/workspace/projects/workspace/memory/淘股吧情报-{today}.json"

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 情报已保存: {md_file}")
    print(f"✅ 数据已保存: {json_file}")


def main():
    """主函数"""
    scraper = TaogubaScraper()
    data = scraper.run_scraper()
    save_to_file(data)

    print("\n" + "=" * 50)
    print("爬虫任务完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
