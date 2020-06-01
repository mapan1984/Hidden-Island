import React from 'react'
import ReactDOM from 'react-dom'
import ArticleList from './article-list.jsx'

const _recommendArticles = document.getElementById('recommend-articles')
const userId = _recommendArticles.dataset.userId
const url = `/api/users/${userId}/recommendation/`

ReactDOM.render(
    <ArticleList
        url={url}
        title={'推荐文章'}
    />,
    _recommendArticles
)
