""" 
将post中的markdown文件转为html文件，
放置在'app/templates/post'目录中
"""

import os
import markdown
import markdown.extensions.codehilite

basedir = os.path.abspath(os.path.dirname(__file__))
sourcedir = basedir + '\\post\\'
targetdir = basedir + '\\app\\templates\\post\\'

md = markdown.Markdown(extensions=["codehilite"])

for post in os.listdir(sourcedir):
    post_name = post.split('.')[0]
    md.convertFile(input=sourcedir+post, 
                   output=targetdir+post_name+'.html')