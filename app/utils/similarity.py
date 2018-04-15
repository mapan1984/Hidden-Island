import math
from collections import Counter

import jieba
import jieba.analyse


PUNCT = set(u''':;"',<.>/?[{}]|\()-_=+!@#$%^&*~` ''')


def remove(word):
    return word not in PUNCT


def tags(article):
    # 这里使用了TF-IDF算法，所以分词结果会有些不同->https://github.com/fxsjy/jieba#3-关键词提取
    res = jieba.analyse.extract_tags(
        sentence=article, topK=1000, withWeight=True)
    return res


def cut_word(article):
    # 分词并返回{word:weight, ...}
    res = filter(remove, jieba.cut_for_search(article))
    return Counter(res).items()


def tf_idf(res1=None, res2=None):
    # 向量，可以使用list表示
    vector_1 = []
    vector_2 = []
    # 词频，可以使用dict表示
    tf_1 = {i[0]: i[1] for i in res1}
    tf_2 = {i[0]: i[1] for i in res2}
    res = set(list(tf_1.keys()) + list(tf_2.keys()))

    # 填充词频向量
    for word in res:
        if word in tf_1:
            vector_1.append(tf_1[word])
        else:
            vector_1.append(0)
        if word in tf_2:
            vector_2.append(tf_2[word])
        else:
            vector_2.append(0)

    return vector_1, vector_2


def numerator(vector1, vector2):
    # 分子
    return sum(a * b for a, b in zip(vector1, vector2))


def denominator(vector):
    # 分母
    return math.sqrt(sum(a * b for a, b in zip(vector, vector)))


def similarity(str1, str2):
    # 关键词向量
    vector1, vector2 = tf_idf(res1=cut_word(article=str1),
                              res2=cut_word(article=str2))

    # 相似度
    try:
        similarity = (numerator(vector1, vector2)
                      / (denominator(vector1) * denominator(vector2)))
    except ZeroDivisionError:
        similarity = 0

    # 使用arccos计算弧度
    # rad = math.acos(similarity)

    return similarity


if __name__ == '__main__':
    article_a = '我喜欢中国，也喜欢美国。'
    article_b = '我喜欢足球，不喜欢篮球。'
    similarity(article_a, article_b)
