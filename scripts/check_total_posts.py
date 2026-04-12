#!/usr/bin/env python3
"""
检查 InStreet 论坛文章总数
"""

import requests
from bs4 import BeautifulSoup
import json

def get_total_posts():
    """获取论坛文章总数"""

    # 尝试访问首页
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw-Bot/1.0)'
        }
        response = requests.get('https://instreet.coze.site/', headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找文章链接
        article_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/post/' in href:
                article_links.append(href)

        # 统计去重后的文章数
        unique_articles = list(set(article_links))
        count = len(unique_articles)

        print(f"首页找到的文章数: {count}")
        print(f"文章ID示例: {unique_articles[:5] if count > 0 else '无'}")

        # 尝试查看是否有分页信息
        # 检查页码
        pagination = soup.find_all('a', string=lambda x: x and x.isdigit())
        if pagination:
            max_page = max([int(p.text) for p in pagination])
            print(f"找到 {max_page} 页")

        return count

    except Exception as e:
        print(f"Error: {e}")
        return 0

if __name__ == '__main__':
    count = get_total_posts()
    print(f"\n首页显示的文章数: {count}")
