const React = window.React
const e = React.createElement


class ArticleList extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            articles: []
        }
    }

    loadArticlesFromServer = () => {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            cache: false,
            success: (data) => {
                this.setState({articles: data})
            },
            error: (xhr, status, err) => {
                console.error(this.props.url, status, err.toString())
            },
        })
    }

    componentDidMount() {
        this.loadArticlesFromServer()
    }

    render() {
        let articleNodes = this.state.articles.map(
            (article, index) => (
                e('li', {className: 'list-group-item', key: index},
                    e('a', {href: article.url}, article.title)
                )
            )
        )
        console.log(articleNodes)
        console.log(articleNodes.length)
        return (
            e('div', {},
                e('span', {className: 'label label-success'}, articleNodes.length > 0 ? this.props.title : (this.props.emptyTip == undefined ? this.props.title : this.props.emptyTip)),
                e('ul', {className: 'list-group'}, articleNodes)
            )
        )
    }
}

export default ArticleList
