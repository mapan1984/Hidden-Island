import markdown


MD = markdown.Markdown(
    extensions=[
        "markdown.extensions.fenced_code",
        "markdown.extensions.codehilite(css_class=highlight,linenums=None)",
        "markdown.extensions.tables",
        "markdown.extensions.toc",
        "app.utils.simple_meta",
    ]
)
