import markdown
import datetime

MONTH_MAP = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}


def convert_date(date):
    """convert linux `date` output string to python datetime date instance

    Args:
        date <string>: linux `date` output stirng, or None

    Return:
        datetime date instance

    Example:
        >>> cst_date = 'Thu Apr 27 21:24:32 CST 2017'
        >>> convert_date(cst_date)
        datetime.date(2017, 4, 27)
    """
    if date is None:
        return datetime.date.today()

    try:
        _, month, day, _, _, year = date.split(' ')
        res_date = datetime.date(int(year), MONTH_MAP[month], int(day))
    except (TypeError, KeyError, ValueError) as exc:
        print("Date Convert Error: %s" % str(exc))
        print("Error Date: %s" % date)
        return datetime.date.today()
    else:
        return res_date


# markdown
MD = markdown.Markdown(
    extensions=[
        "markdown.extensions.fenced_code",
        "markdown.extensions.codehilite(css_class=highlight,linenums=None)",
        "markdown.extensions.tables",
        "markdown.extensions.toc",
        "app.utils.simple_meta",
    ]
)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
