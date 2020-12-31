const React = window.React
const e = React.createElement

import CommentForm from './comment-form.js'
import CommentList from './comment-list.js'

// TODO: 1. 根据返回的 prev, next, count 分页
//       2. 返回 comment body markdown 渲染显示
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
            e('div', {className: 'comment'},
                e(CommentForm, {
                    onCommentSubmit: this.handleCommentSubmit,
                    userId: this.props.userId,
                    articleId: this.props.articleId,
                },),
                e(CommentList, {data: this.state})
            )
        )
    }
}

export default CommentBox

