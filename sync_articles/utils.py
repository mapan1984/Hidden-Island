from itertools import zip_longest


def get_articles_info(articles_path):
    """
    文章目录结构：
        - articles
            - category1
                - article1.md
                - article2.md
                - ....
            - category2
                -article1.md
                -article2.md
                ...
            ...
    Args:
        articles_path <pathlib.[Windows|Posix]Path>: 文章目录位置
    Returns:
        articles_info = [
            (category_name, article_path),
            (category_name, article_path),
            ....
            (category_name, article_path),
        ]
    """
    category_names = [dir.name for dir in articles_path.iterdir()]

    articles_info = []
    for category_name in category_names:
        category_path = articles_path / category_name
        article_paths = category_path.glob('*.md')
        articles_info.extend(
            zip_longest([category_name], article_paths, fillvalue=category_name)
        )
    return articles_info
