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

# Thu Apr 27 21:24:32 CST 2017 --> 2017-4-27
def convert_date(date):
    try:
        _, month, day, _, _, year = date.split(' ')
        month = MONTH_MAP[month]
        return datetime.date(int(year), month, int(day))
    except:
        return datetime.date.today()

# markdown
MD = markdown.Markdown(
    extensions=[
        "markdown.extensions.codehilite(css_class=highlight,linenums=None)",
        "markdown.extensions.meta",
        "markdown.extensions.tables",
        "markdown.extensions.toc",
    ]
)
