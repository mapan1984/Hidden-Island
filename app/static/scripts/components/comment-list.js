const React = window.React
const Remarkable = window.remarkable.Remarkable
const e = React.createElement

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
            e('li', {className: 'comment'},
                e('span', {className: 'commentAuthor'}, this.props.author),
                e('span', {className: 'commentDate'}, this.props.timestamp),
                e('span', {dangerouslySetInnerHTML: this.getRawMarkup()}),
            )
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
                e(Comment, {
                    author: comment.author,
                    timestamp: comment.timestamp,
                    key: comment.id
                }, comment.body)
            )
        )
        return (
            e('ul', {className: 'comments'}, commentNodes)
        )
    }
}

export default CommentList

