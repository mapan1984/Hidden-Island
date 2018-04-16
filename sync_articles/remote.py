import asyncio
import aiofiles
import aiohttp

from .utils import get_articles_info
from .config import POST_URL, AUTH_HEADER, ARTICLES_PATH


async def fetch_article(article_path):
    """读取文章内容并返回"""
    async with aiofiles.open(article_path, encoding='utf-8') as fd:
        content = await fd.read()
    return content


async def post_article(article_json, session):
    async with session.post(POST_URL, headers=AUTH_HEADER, json=article_json) as resp:
        return resp.status


async def work(articles_info, session, sema):
    """读取文章内容，上传至博客网站
    Args:
        articles_info: (category_name, article_path)
    """
    with await sema:
        category_name, article_path = articles_info
        content = await fetch_article(str(article_path))
        article_file_name = article_path.name
        article_json = {
            'category_name': category_name,
            'article_file_name': article_file_name,
            'content': content,
        }
        print(f'logging {article_file_name}...')
        status = await post_article(article_json, session)
        print(status)


async def run():
    articles_info = get_articles_info(ARTICLES_PATH)
    sema = asyncio.Semaphore(10)
    async with aiohttp.ClientSession() as session:
        works = [work(article_info, session, sema) for article_info in articles_info]
        await asyncio.gather(*works)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run())
    loop.run_until_complete(future)
