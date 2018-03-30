$(function () {
    let blogRating = document.querySelector('.blog-rating')
    let userId = blogRating.dataset.userId
    let articleId = blogRating.dataset.articleId

    let avgRating = blogRating.dataset.avgRating
    let currentRating = blogRating.dataset.currentRating

    // 设置当前用户的rating(星条)
    if (currentRating != 'None') {
        let star = document.querySelector(`#star${currentRating}`)
        star.checked = true
    }

    // 显示所有用户的平均rating
    let spanAvgRating = document.querySelector('#avg-rating')
    if (avgRating != 'None') {
        avgRating = Math.floor(avgRating)
        spanAvgRating.innerText = '★★★★★☆☆☆☆☆'.substring(5 - avgRating, 10 - avgRating)
    }

    // 处理评分点击事件
    let rating = document.querySelector('.rating')
    rating && rating.addEventListener('click', (event) => {
        let target = event.target
        if (target.nodeName == 'INPUT') {
            let ratingValue = target.value
            postRating(userId, articleId, ratingValue)
            setCurrentRaing(ratingValue)
        }
    })

    // 设置当前用户的rating值(文字)
    let spanCurrentRating = document.querySelector('#current-rating')
    function setCurrentRaing(value) {
        spanCurrentRating.innerText = ratingValue
    }

    // 发送评分请求
    function postRating(userId, articleId, ratingValue) {
        function success(text) {
            console.log(text)
        }

        function fail(code) {
            console.log('Error code: ' + code)
        }

        let request = new XMLHttpRequest()

        request.onreadystatechange = function () {
            if (request.readyState === 4) {
                if (request.status === 200) {
                    return success(request.responseText);
                } else {
                    return fail(request.status);
                }
            }
        }

        request.open('POST', '/article/rating');
        request.setRequestHeader("Content-Type", "application/json");
        request.send(
            JSON.stringify({
                user_id: userId,
                article_id: articleId,
                rating_value: ratingValue,
            })
        );
        console.log("Rating...")
    }
})
