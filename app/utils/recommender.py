"""
Simple Recommender
==================

Example:
    >>> # 用户对物品的评价
    ...
    >>> person_prefs = {
    ...     'Lisa Rose': {
    ...         'Lady in the Water': 2.5,
    ...         'Snakes on a Plane': 3.5,
    ...         'Just My Luck': 3.0,
    ...         'Superman Returns': 3.5,
    ...         'You, Me and Dupree': 2.5,
    ...         'The Night Listener': 3.0,
    ...     },
    ...     'Gene Seymour': {
    ...         'Lady in the Water': 3.0,
    ...         'Snakes on a Plane': 3.5,
    ...         'Just My Luck': 1.5,
    ...         'Superman Returns': 5.0,
    ...         'The Night Listener': 3.0,
    ...         'You, Me and Dupree': 3.5,
    ...     },
    ...     'Michael Phillips': {
    ...         'Lady in the Water': 2.5,
    ...         'Snakes on a Plane': 3.0,
    ...         'Superman Returns': 3.5,
    ...         'The Night Listener': 4.0,
    ...     },
    ...     'Claudia Puig': {
    ...         'Snakes on a Plane': 3.5,
    ...         'Just My Luck': 3.0,
    ...         'The Night Listener': 4.5,
    ...         'Superman Returns': 4.0,
    ...         'You, Me and Dupree': 2.5,
    ...     },
    ...     'Mick LaSalle': {
    ...         'Lady in the Water': 3.0,
    ...         'Snakes on a Plane': 4.0,
    ...         'Just My Luck': 2.0,
    ...         'Superman Returns': 3.0,
    ...         'The Night Listener': 3.0,
    ...         'You, Me and Dupree': 2.0,
    ...     },
    ...     'Jack Matthews': {
    ...         'Lady in the Water': 3.0,
    ...         'Snakes on a Plane': 4.0,
    ...         'The Night Listener': 3.0,
    ...         'Superman Returns': 5.0,
    ...         'You, Me and Dupree': 3.5,
    ...     },
    ...     'Toby': {
    ...         'Snakes on a Plane': 4.5,
    ...         'You, Me and Dupree': 1.0,
    ...         'Superman Returns': 4.0,
    ...     },
    ... }
    >>> # 物品和其用户对其的评价
    ...
    >>> item_prefs = transform_prefs(person_prefs)
"""

from math import sqrt
from collections import defaultdict

person_prefs = {
    'Lisa Rose': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'Superman Returns': 3.5,
        'You, Me and Dupree': 2.5,
        'The Night Listener': 3.0,
    },
    'Gene Seymour': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 1.5,
        'Superman Returns': 5.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 3.5,
    },
    'Michael Phillips': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.0,
        'Superman Returns': 3.5,
        'The Night Listener': 4.0,
    },
    'Claudia Puig': {
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'The Night Listener': 4.5,
        'Superman Returns': 4.0,
        'You, Me and Dupree': 2.5,
    },
    'Mick LaSalle': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'Just My Luck': 2.0,
        'Superman Returns': 3.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 2.0,
    },
    'Jack Matthews': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'The Night Listener': 3.0,
        'Superman Returns': 5.0,
        'You, Me and Dupree': 3.5,
    },
    'Toby': {
        'Snakes on a Plane': 4.5,
        'You, Me and Dupree': 1.0,
        'Superman Returns': 4.0,
    },
}


def transform_prefs(prefs):
    """
    Transform the recommendations into a mapping where persons are described
    with interest scores for a given title.
    e.g. {title: person} instead of {person: title}.

    Example:
        >>> prefs = {'person1':{'item1': 1, 'item2': 2}, 'person2':{'item1': 3, 'item2': 4}}
        >>> transform_prefs(prefs)
        defaultdict(<class 'dict'>, {'item1': {'person1': 1, 'person2': 3}, 'item2': {'person1': 2, 'person2': 4}})
    """
    result = defaultdict(dict)
    for person in prefs:
        for item in prefs[person]:
            # Flip item and person
            result[item][person] = prefs[person][item]
    return result


def sim_distance(person_prefs, person1, person2):
    """
    Returns a distance-based similarity score for person1 and person2.

    Args:
        person_prefs: 用户评分字典
        person1: 用户名1
        person2: 用户名2

    Returns:
        返回介于0~1之间的值，值越大表示两人的偏好越相似

    Example:
        >>> sim_distance(person_prefs, 'Lisa Rose', 'Gene Seymour')
        0.29429805508554946
    """
    # Get the list of shared_items
    shared_items = [item for item in person_prefs[person1] if item in person_prefs[person2]]
    # If they have no ratings in common, return 0
    if len(shared_items) == 0:
        return 0

    # Add up the squares of all the differences
    sum_of_squares = sum(
        [pow(person_prefs[person1][item] - person_prefs[person2][item], 2) for item in shared_items]
    )
    return 1 / (1 + sqrt(sum_of_squares))


def sim_pearson(person_prefs, person1, person2):
    """
    Returns the Pearson correlation coefficient for p1 and p2.

    Args:
        person_prefs: 用户评分字典
        person1: 用户名1
        person2: 用户名2

    Returns:
        返回介于-1~1之间的值，值越大表示两人的偏好越相似，值为负代表品味负相关

    Example:
        >>> sim_pearson(person_prefs, 'Lisa Rose', 'Gene Seymour')
        0.39605901719066977
    """

    # Get the list of shared_items
    shared_items = [item for item in person_prefs[person1] if item in person_prefs[person2]]
    # Sum calculations
    n = len(shared_items)

    # If they have no ratings in common, return 0
    if n == 0:
        return 0

    # Sums of all the preferences
    sum1 = sum([person_prefs[person1][it] for it in shared_items])
    sum2 = sum([person_prefs[person2][it] for it in shared_items])

    # Sums of the squares
    sum1Sq = sum([pow(person_prefs[person1][it], 2) for it in shared_items])
    sum2Sq = sum([pow(person_prefs[person2][it], 2) for it in shared_items])

    # Sum of the products
    pSum = sum([person_prefs[person1][it] * person_prefs[person2][it] for it in shared_items])

    # Calculate r (Pearson score)
    num = pSum - sum1 * sum2 / n
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0:
        return 0
    r = num / den
    return r


def get_top_matche_persons(prefs, person, n=5, similarity=sim_pearson):
    """
    Returns the best matches for person from the prefs dictionary.
    Number of results and similarity function are optional params.

    Args:
        prefs: 用户评价字典
        person: 用户名
        n: 返回结果个数，默认为5
        similarity: 相关度函数，默认为sim_pearson

    Returns:
        与person相关度最高的前n个用户及其相似度评价值的列表

    Example:
        >>> get_top_matche_persons(person_prefs, 'Toby', n=2)
        [(0.9912407071619299, 'Lisa Rose'), (0.9244734516419049, 'Mick LaSalle')]
    """
    scores = [(similarity(prefs, person, other), other) for other in prefs
              if other != person]
    scores.sort(reverse=True)
    return scores[0:n]


def _get_recommended_items(prefs, person, similarity=sim_pearson):
    """
    协作型过滤，耗时大，不推荐
    Args:
        prefs: 用户评价字典
        person: 用户名
        similarity: 相关度函数，默认为sim_pearson

    Returns:
        为用户person推荐的物品及其评分（预测）的列表

    Example:
        >>> _get_recommended_items(person_prefs, 'Toby')
        [(3.3477895267131017, 'The Night Listener'), (2.8325499182641614, 'Lady in the Water'), (2.530980703765565, 'Just My Luck')]
        >>> _get_recommended_items(person_prefs, 'Toby', similarity=sim_distance)
        [(3.457128694491423, 'The Night Listener'), (2.778584003814924, 'Lady in the Water'), (2.422482042361917, 'Just My Luck')]
    """
    sum_score = defaultdict(int)  # Weighted sum of `similarity * rating`
    sum_sim = defaultdict(int)  # Sum of all the `similarities`
    for other in prefs:
        # Don't compare me to myself
        if other == person:
            continue
        sim = similarity(prefs, person, other)  # 对每一个用户都进行相似度判断，耗时
        # Ignore scores of zero or lower
        if sim <= 0:
            continue
        for item in prefs[other]:
            # Only score movies I haven't seen yet
            if item not in prefs[person]:
                sum_score[item] += prefs[other][item] * sim
                sum_sim[item] += sim
    # Create the normalized list
    rankings = [(score / sum_sim[item], item) for (item, score) in sum_score.items()]
    # Return the sorted list
    rankings.sort(reverse=True)
    return rankings


def calculate_similar_items(item_prefs, n=10):
    """
    Create a dictionary of items showing which other items they are
    most similar to.

    Args:
        item_prefs: 物品和其用户对其评价
        n: 选择每件物品前n个最相似的物品

    Returns:
        返回一个字典，给出与每件物品最相似的其他物品

    Example:
        >>> # Invert the preference matrix to be item-centric
        >>> item_prefs = transform_prefs(person_prefs)
        >>> calculate_similar_items(item_prefs)
        {'Just My Luck': [(0.3483314773547883, 'Lady in the Water'),
          (0.32037724101704074, 'You, Me and Dupree'),
          (0.2989350844248255, 'The Night Listener'),
          (0.2553967929896867, 'Snakes on a Plane'),
          (0.20799159651347807, 'Superman Returns')],
         'Lady in the Water': [(0.4494897427831781, 'You, Me and Dupree'),
          (0.38742588672279304, 'The Night Listener'),
          (0.3483314773547883, 'Snakes on a Plane'),
          (0.3483314773547883, 'Just My Luck'),
          (0.2402530733520421, 'Superman Returns')],
         'Snakes on a Plane': [(0.3483314773547883, 'Lady in the Water'),
          (0.32037724101704074, 'The Night Listener'),
          (0.3090169943749474, 'Superman Returns'),
          (0.2553967929896867, 'Just My Luck'),
          (0.1886378647726465, 'You, Me and Dupree')],
         'Superman Returns': [(0.3090169943749474, 'Snakes on a Plane'),
          (0.252650308587072, 'The Night Listener'),
          (0.2402530733520421, 'Lady in the Water'),
          (0.20799159651347807, 'Just My Luck'),
          (0.1918253663634734, 'You, Me and Dupree')],
         'The Night Listener': [(0.38742588672279304, 'Lady in the Water'),
          (0.32037724101704074, 'Snakes on a Plane'),
          (0.2989350844248255, 'Just My Luck'),
          (0.29429805508554946, 'You, Me and Dupree'),
          (0.252650308587072, 'Superman Returns')],
         'You, Me and Dupree': [(0.4494897427831781, 'Lady in the Water'),
          (0.32037724101704074, 'Just My Luck'),
          (0.29429805508554946, 'The Night Listener'),
          (0.1918253663634734, 'Superman Returns'),
          (0.1886378647726465, 'Snakes on a Plane')]}
    """
    result = {}
    for c, item in enumerate(item_prefs.keys(), start=1):
        # Status updates for large datasets
        if c % 100 == 0:
            print('%d / %d' % (c, len(item_prefs)))
        # Find the most similar items to this one
        scores = get_top_matche_persons(item_prefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result


def get_recommended_items(person_prefs, item_match, person):
    """
    基于物品过滤，推荐
    Args:
        person_prefs: 用户评价字典
        item_match: 物品相似字典，由calculate_similar_items返回
        person: 用户名

    Returns:
        返回为person推荐的物品及其评分的列表

    Example:
        >>> item_perfs = transform_prefs(person_prefs)
        >>> item_match = calculate_similar_items(item_prefs)
        >>> get_recommended_items(person_prefs, item_match, 'Toby')
        [(3.1667425234070894, 'The Night Listener'), (2.9366294028444346, 'Just My Luck'), (2.868767392626467, 'Lady in the Water')]
    """
    person_ratings = person_prefs[person]
    sum_score = defaultdict(int)  # Weighted sum of `similarity * rating`
    sum_sim = defaultdict(int)  # Sum of all the `similarities`
    # Loop over items rated by this user
    for item, rating in person_ratings.items():
        # Loop over items similar to this one
        for similarity, item2 in item_match[item]:
            # Ignore if this user has already rated this item
            if item2 in person_ratings:
                continue
            # Ignore not similarity item2
            if similarity == 0:
                continue
            sum_score[item2] += similarity * rating
            sum_sim[item2] += similarity
    # Divide each total score by total weighting to get an average
    rankings = [(score / sum_sim[item], item) for (item, score) in sum_score.items()]
    # Return the rankings from highest to lowest
    rankings.sort(reverse=True)
    return rankings


if __name__ == '__main__':
    import doctest
    doctest.testmod()
