import ArticleList from './components/article-list.js'
const React = window.React
const ReactDOM = window.ReactDOM
const e = React.createElement

const recommendArticles = document.getElementById('recommend-articles')
const userId = recommendArticles.dataset.userId
const url = `/api/users/${userId}/recommendation/`

ReactDOM.render(
    e(ArticleList, {url: url, title: '推荐文章', emptyTip: ''}),
    recommendArticles
)
