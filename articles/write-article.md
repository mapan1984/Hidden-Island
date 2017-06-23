---
title: Blog文章写作说明
date: Mon Oct 10 09:26:34 CST 2016
category: write
tag: markdown
---

### 元信息

YAML格式：

    ---
    title: Blog文章写作说明
    date: Mon Oct 10 09:26:34 CST 2016
    category: write
    tag: markdown
    ---

### 日期格式

文章支持的日期格式为:

    date: Thu Apr 27 21:36:25 CST 2017

它会被转换为Python datetime.date类型:

    datetime.date(2017, 4, 27)

### 代码

#### shebang(with path)

    #!/usr/bin/python
    def hello(name):
        print("hello, %s" % name)

#### shebang(no path)

    #!python
    def hello(name):
        print("hello, %s" % name)

#### colons

    :::python
    def hello(name):
        print("hello, %s" % name)

