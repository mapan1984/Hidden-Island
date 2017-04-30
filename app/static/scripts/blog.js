'use strict';

$(function() {
    // 为导航条的当前项目增加 `active` class
    let curHref = document.location.href;
    $('.blog-nav').find('a').each(function () {
        let curHrefReg = new RegExp('^'+this.href+'(|[\\d\\s#])$')
        if (curHrefReg.test(curHref)) {
            $(this).addClass('active');  // this.className += 'active';
        }
    });

    // 固定页脚在页面底部
    function footerPosition() {
        let footer = $('.blog-footer');
        footer.removeClass("fixed-bottom");
        let contentHeight = document.body.scrollHeight,  //网页正文全文高度
            winHeight = window.innerHeight;  //可视窗口高度，不包括浏览器顶部工具栏
        if(!(contentHeight > winHeight)){
            //当网页正文高度小于可视窗口高度时，为footer添加类fixed-bottom
            footer.addClass("fixed-bottom");
        } else {
            footer.removeClass("fixed-bottom");
        }
    }
    footerPosition();
    $(window).resize(footerPosition);
});

