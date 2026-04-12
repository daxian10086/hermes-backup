#!/usr/bin/env python3
"""
分析 InStreet 高赞帖子，找到值得关注的作者和内容
"""

import requests
from bs4 import BeautifulSoup
import json

def get_top_posts():
    """获取首页高赞帖子"""

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw-Bot/1.0)'
        }
        response = requests.get('https://instreet.coze.site/', headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有文章链接
        post_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/post/' in href:
                post_links.append(href)

        # 去重
        post_links = list(set(post_links))

        print(f"找到 {len(post_links)} 篇文章\n")
        print("=== 开始获取文章详情 ===\n")

        top_posts = []

        # 获取文章详情
        for url in post_links[:20]:  # 只获取前 20 篇
            try:
                # 确保 URL 是完整的
                if not url.startswith('http'):
                    url = 'https://instreet.coze.site' + url

                print(f"正在获取: {url}")

                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # 提取标题
                title = soup.find('h1')
                title_text = title.get_text(strip=True) if title else '无标题'

                # 提取作者
                author = soup.find('span', {'class': 'font-medium'})
                author_text = author.get_text(strip=True) if author else '未知'

                # 提取点赞数和评论数
                stats = soup.find_all('b', class_='text-foreground')
                likes = int(stats[0].get_text(strip=True)) if len(stats) > 0 else 0
                comments = int(stats[1].get_text(strip=True)) if len(stats) > 1 else 0

                top_posts.append({
                    'title': title_text,
                    'author': author_text,
                    'likes': likes,
                    'comments': comments,
                    'url': url
                })

            except Exception as e:
                print(f"  错误: {e}")

        # 按点赞数排序
        top_posts.sort(key=lambda x: x['likes'], reverse=True)

        print("\n=== 高赞帖子排行 ===\n")
        for i, post in enumerate(top_posts[:10], 1):
            print(f"{i}. {post['title']}")
            print(f"   作者: {post['author']}")
            print(f"   点赞: {post['likes']} | 评论: {post['comments']}")
            print(f"   链接: {post['url']}")
            print()

        return top_posts

    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == '__main__':
    posts = get_top_posts()
    print(f"\n共分析 {len(posts)} 篇文章")
