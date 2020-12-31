import ArticleList from './components/article-list.js'
const React = window.React
const ReactDOM = window.ReactDOM
const e = React.createElement

let similarArticles = document.getElementById('similar-articles')
let articleId = similarArticles.dataset.articleId
let url = `/api/articles/${articleId}/similarities/`

ReactDOM.render(
    e(ArticleList, {url: url, title: '相似文章'}),
    similarArticles
)
