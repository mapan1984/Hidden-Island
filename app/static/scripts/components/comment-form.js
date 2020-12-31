const React = window.React
const e = React.createElement

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
            e('div', {className: 'comment-form'},
                e('p', {}, '请输入评论'),
                e('form', {className: 'form', role: 'form', onSubmit: this.handleSubmit},
                    e('div', {className: 'form-group required'},
                        e('label', {className: 'control-label', htmlFor: 'comment-body'}),
                        e('input', {
                            type: 'text',
                            className: 'from-control',
                            id: 'comment-body',
                            value: this.state.body,
                            onChange: this.handleBodyChange
                        })
                    ),
                    e('input', {type: 'submit', className: 'btn btn-default', value: '提交评论'}),
                )
            )
        )
    }
}

export default CommentForm
