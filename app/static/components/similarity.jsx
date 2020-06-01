import React from 'react'
import ReactDOM from 'react-dom'
import ArticleList from './article-list.jsx'

let _similarArticles = document.getElementById('similar-articles')
let articleId = _similarArticles.dataset.articleId
let url = `/api/articles/${articleId}/similarities/`

ReactDOM.render(
    <ArticleList
        url={url}
        title={'相似文章'}
    />,
    _similarArticles
)
