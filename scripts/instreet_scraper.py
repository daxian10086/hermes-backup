#!/usr/bin/env python3
"""
InStreet 文章爬虫
直接从 HTML 提取文章内容，不使用浏览器
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import os

def fetch_article(url):
    """获取文章内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw-Bot/1.0)'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def parse_article(html):
    """解析文章内容"""
    soup = BeautifulSoup(html, 'html.parser')

    # 提取标题
    title = soup.find('h1')
    title_text = title.get_text(strip=True) if title else ''

    # 提取作者
    author = soup.find('span', {'class': 'font-medium'})
    author_text = author.get_text(strip=True) if author else ''

    # 提取文章内容
    content_div = soup.find('div', class_='prose')
    content_text = ''
    if content_div:
        # 提取所有段落
        paragraphs = content_div.find_all('p')
        content_text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])

    # 提取点赞数和评论数
    stats = soup.find_all('b', class_='text-foreground')
    likes = stats[0].get_text(strip=True) if len(stats) > 0 else '0'
    comments = stats[1].get_text(strip=True) if len(stats) > 1 else '0'

    return {
        'title': title_text,
        'author': author_text,
        'content': content_text,
        'likes': likes,
        'comments': comments,
        'url': ''
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: instreet_scraper.py <post_url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]

    # 获取文章
    html = fetch_article(url)
    if not html:
        sys.exit(1)

    # 解析文章
    article = parse_article(html)
    article['url'] = url

    # 输出 JSON
    print(json.dumps(article, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
