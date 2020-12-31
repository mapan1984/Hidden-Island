import CommentBox from './components/comment-box.js'
const React = window.React
const ReactDOM = window.ReactDOM
const e = React.createElement

let commentBox = document.getElementById('comment-box')
let userId = commentBox.dataset.userId
let articleId = commentBox.dataset.articleId
let isAuthenticated = commentBox.dataset.isAuthenticated
let url = `/api/articles/${articleId}/comments/`

ReactDOM.render(
    e(CommentBox, {
        url: url,
        pollInterval: 2000,
        userId: userId,
        articleId: articleId,
        isAuthenticated: isAuthenticated,
    }),
    commentBox
)
