"""
Convert format date string to python date/datetime
==================================================

Date formt: YYYY-MM-DD HH:MM:SS +/-TTTT
Date example: see linux command `date +"%Y-%m-%d %H:%M:%S %z"`
"""

from datetime import date, datetime

from app import logger


def todate(article_date):
    """
    Exemple:
        >>> article_date = '2017-08-09'
        >>> todate(article_date)
        datetime.date(2017, 8, 9)
        >>> article_file_name = '2017-08-09-同步jekyll博客文章.md'
        >>> todate(article_file_name)
        datetime.date(2017, 8, 9)
    """
    if article_date is None or article_date == '':
        return date.today()
    try:
        year, month, day, *_ = article_date.split('-')
        res_date = date(int(year), int(month), int(day))
    except (TypeError, KeyError, ValueError) as exc:
        logger.warning("Date Convert Error: %s" % str(exc))
        logger.warning("Error Date: %s" % article_date)
        return date.today()
    else:
        return res_date


def todatetime(article_datetime):
    """
    Exemple:
        >>> article_date = '2017-08-09'
        >>> todate(article_date)  # doctest: +SKIP
        datetime.datetime(2017, 8, 9, 23, 6, 33, 476358)
        >>> article_datetime = '2017-08-09 12:45:30'
        >>> todatetime(article_datetime)
        datetime.datetime(2017, 8, 9, 12, 45, 30)
        >>> article_file_name = '2017-08-09-同步jekyll博客文章.md'
        >>> todate(article_file_name)  # doctest: +SKIP
        datetime.datetime(2017, 8, 9, 23, 6, 33, 476358)
    """
    if article_datetime is None or article_datetime == '':
        return datetime.utcnow()
    try:
        _date, *_time = article_datetime.split(' ')
        if not _time:
            time = datetime.now().time()
            return datetime.combine(todate(_date), time)
        else:
            year, month, day = _date.split('-')
            hour, minute, second = _time[0].split(':')
            res_datetime = datetime(int(year), int(month), int(day),
                                    int(hour), int(minute), int(second))
    except (TypeError, KeyError, ValueError) as exc:
        logger.warning("Datetime Convert Error: %s" % str(exc))
        logger.warning("Error Datetime: %s" % article_datetime)
        return datetime.utcnow()
    else:
        return res_datetime


if __name__ == '__main__':
    import doctest
    doctest.testmod()
