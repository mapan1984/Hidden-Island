import jieba
from collections import defaultdict

from app import db, create_app
from app.models import Words, Article


def build_query(word_values):
    """ 构造查询字符串
    假设q为两个单词，单词id分别为10和17
    则fullquery为：
        select w0.article_id, w0.location
        from wordlocation w0
        where w0.word_id=10

        select w0.article_id, w0.location, w1.location
        from wordlocation w0, wordlocation w1
        where w0.word_id=10
              and w0.article_id=w1.article_id
              and w1.word_id=17
    即返回同时含有这两个单词的titleid
    """
    fieldlist = 'w0.article_id'
    tablelist = ''
    clauselist = ''
    wordids = []

    table_number = 0

    for word_value in word_values:
        word = Words.query.filter_by(value=word_value).first()
        if word is not None:
            word_id = word.id
            wordids.append(word_id)
            if table_number > 0:
                tablelist += ','
                clauselist += ' and w%d.article_id=w%d.article_id and ' % (table_number - 1, table_number)
            fieldlist += ',w%d.location' % table_number
            tablelist += 'wordlocation w%d' % table_number
            clauselist += 'w%d.word_id=%d' % (table_number, word_id)
            table_number += 1

    # 根据各个组分，建立查询
    fullquery = 'select %s from %s where %s' % (fieldlist, tablelist, clauselist)
    # print(fullquery)
    return fullquery, wordids


def get_match_rows(query):
    """
    Returns:
        rows: [(article_id, word1location, word2location, ...), ....]
        wordids: [word_id_1, word_id_2, ...]
    """
    # 拆分查询关键词
    word_values = [value.lower() for value in jieba.cut(query) if not Words._should_ignore(value)]
    # print(word_values)

    # 构造查询的字符串
    fullquery, wordids = build_query(word_values)
    if len(wordids) > 0:
        cur = db.session.execute(fullquery).cursor

        articleid_locations = [row for row in cur]

        # print(wordids)
        # print(articleid_locations[:10])
        return articleid_locations, wordids
    else:
        return None, None


def normalize_scores(scores, smallIsBetter=False):
    """
    scores为一个包含title_id与对应评价值的字典，
    函数根据smallIsBetter是否，返回一个带有相同ID，
    而评价值介于0和1之间的新字典(最佳结果的对应值为1)
    """
    vsmall = 0.00001  # 避免被零整除
    if smallIsBetter:
        minscore = min(scores.values())
        return {
            u: float(minscore) / max(vsmall, l) for u, l in scores.items()
        }
    else:
        maxscore = max(scores.values())
        if maxscore == 0:
            maxscore = vsmall
        return {
            u: float(c) / maxscore for u, c in scores.items()
        }


def frequency_score(rows):
    """
    根据词频对每个网页进行打分，词频越大分值越高
    """
    counts = defaultdict(int)
    for row in rows:
        counts[row[0]] += 1
    return normalize_scores(counts)


def location_score(rows):
    """
    根据词在网页中出现的位置对网页进行打分，越靠前分值越高
    """
    locations = {row[0]: 100000 for row in rows}
    for row in rows:
        loc = sum(row[1:])
        if loc < locations[row[0]]:
            locations[row[0]] = loc
    return normalize_scores(locations, smallIsBetter=True)


def distance_score(rows):
    """
    根据词与词之间的距离对网页进行打分，距离越小分值越高
    """
    # 如果仅有一个单词，则得分都一样
    if len(rows[0]) <= 2:
        return {row[0]: 1.0 for row in rows}

    mindistance = {row[0]: 1000000 for row in rows}

    for row in rows:
        dist = sum([abs(row[i] - row[i - 1]) for i in range(2, len(row))])
        if dist < mindistance[row[0]]:
            mindistance[row[0]] = dist
    return normalize_scores(mindistance, smallIsBetter=True)


def get_scored_list(rows, wordids):
    total_scores = {row[0]: 0 for row in rows}

    # 此处是稍后放置评价函数的地方
    weights = [
        (1.0, frequency_score(rows)),
        (1.0, location_score(rows)),
        (1.0, distance_score(rows)),
    ]

    for weight, scores in weights:
        for title in total_scores:
            total_scores[title] += weight * scores[title]

    return total_scores


def get_title(article_id):
    return Article.query.get(article_id).title


def query(q, limit=8, offset=0):
    """进行一次查询
    Args:
        q (str): 查询的关键词
        limit (int): 返回查询结果的最大数量
        offset (int): 返回查询结果的开始偏移
    Return:
        query_result (List[Tuple[str, float]]): 返回查询得到的`title,score`列表
    """
    query_result = []
    articleid_locations, wordids = get_match_rows(q)
    if articleid_locations and wordids:
        articleid_scores = get_scored_list(articleid_locations, wordids)
        # print(articleid_scores)

        ranked_articleid_scores = sorted(articleid_scores.items(), key=lambda x: x[1], reverse=True)
        for articleid, score in ranked_articleid_scores[offset:limit]:
            article = Article.query.get(articleid)
            # print("%f\t%s" % (score, article.title))
            query_result.append((article, score))
    else:
        pass
        # print("你的查询 - '%s' - 没有匹配到任何文章" % q)
    return query_result


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    args = parser.parse_args()

    with create_app('development').app_context():
        name_scores = query(args.query)
        if len(name_scores) > 0:
            article_scores = [
                (Article.query.filter_by(name=name).first(), score)
                for name, score in name_scores
            ]
        else:
            article_scores = []
