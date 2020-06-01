import React from 'react'


class ArticleList extends React.Component {
    constructor(props) {
        super(props)
        this.state = {articles: []}
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
                <li className="list-group-item" key={index}>
                    <a href={article.url}>{article.title}</a>
                </li>
            )
        )
        return (
             <div className="similarity">
               <span className="label label-success">{this.props.title}</span>
               <ul className="list-group">
                   {articleNodes}
               </ul>
             </div>
        )
    }
}

export default ArticleList
