"""
Simple Meta Data Extension for Python-Markdown
==============================================

This extension adds Simple Meta Data handling to markdown.

Example:
    >>> import markdown
    >>> md = markdown.Markdown(extensions=["simple_meta"])
    >>> text = '''---
    ... Title: test doc
    ... Author: mapan
    ... Tags: [markdown, python]
    ... ---
    ...
    ... This is Body.
    ... '''
    >>> md.convert(text)
    '<p>This is Body.</p>'
    >>> md.Meta # doctest: +SKIP
    {'title': 'test doc', 'author': 'mapan', 'tags': ['markdown', 'python']}
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown import Extension
from markdown.preprocessors import Preprocessor
import re


META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
LIST_VALUE_RE = re.compile(r'^\[(?P<values>.*)\]$')
BEGIN_RE = re.compile(r'^-{3}(\s.*)?')
END_RE = re.compile(r'^(-{3}|\.{3})(\s.*)?')


class SimpleMetaExtension (Extension):
    """ Simple Meta-Data extension for Python-Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Add SimpleMetaPreprocessor to Markdown instance. """
        md.preprocessors.add("simple_meta",
                             SimpleMetaPreprocessor(md),
                             ">normalize_whitespace")


class SimpleMetaPreprocessor(Preprocessor):
    """ Get Meta-Data. """

    def run(self, lines):
        """ Parse Meta-Data and store in Markdown.Meta. """
        meta = {}
        if lines and BEGIN_RE.match(lines[0]):
            lines.pop(0)
        while lines:
            line = lines.pop(0)
            if line.strip() == '' or END_RE.match(line):
                break  # blank line or end of YAML header - done
            meta_match = META_RE.match(line)
            if meta_match:
                key = meta_match.group('key').lower().strip()
                value = meta_match.group('value').strip()

                list_match = LIST_VALUE_RE.match(value)
                if list_match:
                    values = list_match.group('values').split(',')
                    values = [v.strip() for v in values]
                    meta[key] = values
                else:
                    meta[key] = value
            else:
                lines.insert(0, line)
                break  # no meta data - done
        self.markdown.Meta = meta
        return lines


def makeExtension(*args, **kwargs):
    return SimpleMetaExtension(*args, **kwargs)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
