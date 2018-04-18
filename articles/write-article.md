---
title: Blog文章写作说明
date: 2016-10-10 09:26:34
category: manual
tags: [markdown]
---

### 元信息

YAML格式：

    ---
    title: Blog文章写作说明
    date: YYYY-MM-DD HH:MM:SS
    category: manual
    tags: [markdown]
    ---

### 日期格式

文章支持的日期格式为:

    date: YYYY-MM-DD HH:MM:SS

可以在linux运行以下命令查看：

    $ date +"%Y-%m-%d %H:%M:%S"

`date`的`YYYY-MM-DD`和`HH:MM:SS`俩部分可选，如果未给出时间，默认使用提交文章的时间。

`date`会被转换为Python的`datetime.datetime`类型:

    datetime.date(2017, 4, 27, 12, 34, 45)


日期格式还可以用文章名给出，文件命名：

    2016-10-10-Bolg文章写作说明.md

### 代码


#### fence code

    ```python
    def hello(name):
        print("hello, %s" % name)
    ```

```python
def hello(name):
    print("hello, %s" % name)
```

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
