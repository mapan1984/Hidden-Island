"""
文章内容相似度判断
"""

import re
import math
from collections import Counter

import jieba
import jieba.analyse


IGNORE_WORDS = set(['是', '的'])
IGNORE_PATTERN = re.compile(r'(\W+|\s+|_+)')


def should_ignore(word):
    """ 如果word应被ignore，返回true """
    return word in IGNORE_WORDS or IGNORE_PATTERN.match(word)


def not_should_ignore(word):
    """ 如果word不应被ignore，返回true """
    return not should_ignore(word)


def get_words_weight(string):
    """ 对string进行分词处理
    Args:
        string: 要进行分词的字符串
    Return:
        返回词与词频信息字典(collections.Counter)，格式为{word1: weight, word2: weight, ...}
    """
    words = [word.lower() for word in jieba.cut_for_search(string) if not_should_ignore(word)]
    return Counter(words)


def get_vectors(words_weight_1=None, words_weight_2=None):
    """ 构造词频向量并返回
    Args:
        words_weight_1 (dict): 词频1，格式为{word1: weight, word2: weight, ...}
        words_weight_2 (dict): 词频2，格式为{word1: weight, word2: weight, ...}
    Returns:
        vector_1 (list): 根据words_weight_1构造的词频向量
        vector_2 (list): 根据words_weight_2构造的词频向量
    Exemples:
        >>> get_vectors({'a': 2, 'b':1}, {'a':3, 'c':4})
        ([1, 2, 0], [0, 3, 4])
    """
    # 向量，可以使用list表示
    vector_1, vector_2 = [], []

    # 共有单词
    words = list(set(list(words_weight_1.keys()) + list(words_weight_2.keys())))

    # 填充词频向量
    for word in words:
        if word in words_weight_1:
            vector_1.append(words_weight_1[word])
        else:
            vector_1.append(0)
        if word in words_weight_2:
            vector_2.append(words_weight_2[word])
        else:
            vector_2.append(0)

    return vector_1, vector_2


def inner_product(vector1, vector2):
    """ 返回vector1和vector2的点积，即vector1和vector2的对应项乘积之和 """
    return sum(a * b for a, b in zip(vector1, vector2))


def magnitude(vector):
    """ 返回vector的模长，即vector各项平方和的开方 """
    return math.sqrt(sum(math.pow(v, 2) for v in vector))


def similarity(str1, str2):
    """ 分别生成str1和str2的词频向量
    根据词频向量的夹角大小评价str1和str2的相似度
    """
    # 关键词向量
    vector1, vector2 = get_vectors(
        words_weight_1=get_words_weight(str1),
        words_weight_2=get_words_weight(str2)
    )

    # 以向量距离衡量相似度
    try:
        similarity = (inner_product(vector1, vector2)
                      / (magnitude(vector1) * magnitude(vector2)))
    except ZeroDivisionError:
        similarity = 0

    # 使用arccos计算弧度
    # rad = math.acos(similarity)

    return similarity


if __name__ == '__main__':
    article_a = '我喜欢中国，也喜欢美国。'
    article_b = '我喜欢足球，不喜欢篮球。'
    print(similarity(article_a, article_b))
