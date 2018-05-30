import React from 'react'
import ReactDOM from 'react-dom'
import CommentBox from './comments.jsx'

let _commentBox = document.getElementById('comment-box')
let userId = _commentBox.dataset.userId
let articleId = _commentBox.dataset.articleId
let url = `/api/articles/${articleId}/comments/`

ReactDOM.render(
    <CommentBox
        url={url}
        pollInterval={2000}
        userId={userId}
        articleId={articleId}
    />,
    _commentBox
)
