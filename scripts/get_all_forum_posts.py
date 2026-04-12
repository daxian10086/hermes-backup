#!/usr/bin/env python3
"""
检查 InStreet 论坛所有文章数量
"""

import requests
from bs4 import BeautifulSoup
import time
import re

def get_all_articles():
    """获取所有文章"""

    all_articles = []
    page = 1

    while True:
        print(f"正在获取第 {page} 页...")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw-Bot/1.0)'
            }

            # 访问当前页
            url = f'https://instreet.coze.site/?page={page}' if page > 1 else 'https://instreet.coze.site/'
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找当前页的文章链接
            page_articles = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/post/' in href:
                    # 提取文章ID
                    match = re.search(r'/post/([a-f0-9-]+)', href)
                    if match:
                        article_id = match.group(1)
                        page_articles.append(article_id)

            # 去重
            page_articles = list(set(page_articles))

            if not page_articles:
                print(f"第 {page} 页没有文章，停止获取")
                break

            # 添加到总列表
            before_count = len(all_articles)
            all_articles.extend(page_articles)
            all_articles = list(set(all_articles))
            new_count = len(all_articles) - before_count

            print(f"第 {page} 页: {len(page_articles)} 篇文章 (新增 {new_count} 篇)")

            # 如果这一页没有新增文章，说明已经到底了
            if new_count == 0 and page > 1:
                print(f"第 {page} 页没有新文章，停止获取")
                break

            page += 1
            time.sleep(1)  # 避免请求过快

        except Exception as e:
            print(f"Error at page {page}: {e}")
            break

    return all_articles

if __name__ == '__main__':
    print("开始获取所有文章...\n")
    articles = get_all_articles()

    print(f"\n=== 统计结果 ===")
    print(f"总文章数: {len(articles)}")
    print(f"文章ID示例: {articles[:5] if articles else '无'}")
    print(f"文章ID范围: {articles[0][:8]}... 到 {articles[-1][:8]}..." if articles else "无")
