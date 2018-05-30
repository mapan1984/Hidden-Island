import React from 'react'
import Remarkable from 'remarkable'

import './comments.css'


/**
 * CommentBox
 *   CommentForm
 *   CommentList
 *     Comment
 */
class CommentBox extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            comments: [],
            prev: null,
            next: null,
            count: 0,
        }
    }
    loadCommentsFromServer = () => {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            cache: false,
            success: (data) => {
                this.setState(data)
            },
            error: (xhr, status, err) => {
                console.error(this.props.url, status, err.toString())
            }
        })
    }
    handleCommentSubmit = (comment) => {
        // submit comment to the server and refresh the list
        $.ajax({
            type: 'POST',
            url: this.props.url,
            data: comment,
            contentType: 'application/json;charset=UTF-8',
            success: (data) => {
                // FIXME: 分页错误?
                let newState = this.state
                newState.comments.push(data)
                this.setState(newState)
            },
            error: (xhr, status, err) => {
                console.error(this.props.url, status, err.toString())
            }
        })

    }
    componentDidMount() {
        this.loadCommentsFromServer()
        // setInterval(this.loadCommentsFromServer, this.props.pollInterval)
    }
    render() {
        return (
            <div className="commentBox">
              <CommentForm
                onCommentSubmit={this.handleCommentSubmit}
                userId={this.props.userId}
                articleId={this.props.articleId}
              />
              <CommentList data={this.state} />
            </div>
        )
    }
}

class CommentList extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {
        let commentNodes = this.props.data.comments.map(
            (comment, index) => (
                <Comment author={comment.author} timestamp={comment.timestamp} key={comment.id}>
                  {comment.body}
                </Comment>
            )
        )
        return (
            <ul className="commentList">
              {commentNodes}
            </ul>
        )
    }
}

class Comment extends React.Component {
    constructor(props) {
        super(props)
    }

    getRawMarkup() {
        let md = new Remarkable()
        let rawMarkup = md.render(this.props.children.toString())
        return { __html: rawMarkup }
    }

    render() {
        return (
            <li className="comment">
              <span className="commentAuthor">
                {this.props.author}
              </span>
              <span className="commentDate">
                {this.props.timestamp}
              </span>
              <span dangerouslySetInnerHTML={this.getRawMarkup()} />
            </li>
        )
    }
}

class CommentForm extends React.Component {
    constructor(props) {
        super(props)
        this.state = {body: ''}
    }
    handleBodyChange = (e) => {
        this.setState({body: e.target.value})
    }
    handleSubmit = (e) => {
        e.preventDefault()  // 阻止浏览器提交表单的默认行为
        let body = this.state.body.trim()
        let authorId = this.props.userId
        let articleId = this.props.articleId
        if (!body || !authorId) {
            return
        }

        // send request to the server
        this.props.onCommentSubmit(JSON.stringify({
            author_id: authorId,
            article_id: articleId,
            body: body
        }), null, '\t')

        this.setState({body: ''})
    }
    render() {
        return (
            <form className="commentForm" onSubmit={this.handleSubmit}>
              <input
                type="text"
                placeholder="Say something..."
                value={this.state.body}
                onChange={this.handleBodyChange}
              />
              <input type="submit" value="Post" />
            </form>
        )
    }
}

export default CommentBox
