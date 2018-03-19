$(function () {
    let blogRating = document.querySelector('.blog-rating')
    let userId = blogRating.dataset.userId
    let articleId = blogRating.dataset.articleId
    let avgRating = blogRating.dataset.avgRating
    let currentRating = blogRating.dataset.currentRating

    let spanCurrentRating = document.querySelector('#current-rating')
    let spanAvgRating = document.querySelector('#avg-rating')

    let rating = document.querySelector('.rating')
    rating && rating.addEventListener('click', (event) => {
        let target = event.target
        if (target.nodeName == 'INPUT') {
            let ratingValue = target.value
            postRating(userId, articleId, ratingValue)
            spanCurrentRating.innerText = ratingValue
        }
    })

    // 设置当前用户的rating
    if (currentRating != 'None') {
        let star = document.querySelector(`#star${currentRating}`)
        star.checked = true
    }

    // 显示所有用户的评价rating
    if (avgRating != 'None') {
        avgRating = Math.floor(avgRating)
        spanAvgRating.innerText = '★★★★★☆☆☆☆☆'.substring(5 - avgRating, 10 - avgRating)
    }

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

        request.open('POST', '/rating');
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
