'use strict';

// 增加加载函数
function addLoadEvent(func) {
    var oldonload = window.onload;
    if (typeof window.onload != 'function') {
        window.onload = func;
    } else {
        window.onload = function () {
            oldonload();
            func();
        }
    }
}

// 在targetElement后插入newElement
function insertAfter(newElement, targetElement) {
    var parent = targetElement.parentNode;
    if (parent.lastChild === targetElement) {
        parent.appendChild(newElement);
    } else {
        parent.insertBefore(newElement, targetElement.nextSibling);
    }
}

// 在页面中展示text信息
function showInfo(text) {
    /*
    <div class="alert alert-info">
      <button type="button" class="close" data-dismiss="alert">
        <span aria-hidden="true">×</span>
        <span class="sr-only">Close</span>
      </button>
      <text>
    </div>
    */
    var alertDiv = document.createElement("div");
    alertDiv.setAttribute("class", "alert alert-info");

    var alertBtn = document.createElement("button");
    alertBtn.setAttribute("type", "button");
    alertBtn.setAttribute("class", "close");
    alertBtn.setAttribute("data-dismiss", "alert");

    var alertSpan1 = document.createElement("span");
    alertSpan1.setAttribute("aria-hidden", "true")
    var span1Text = document.createTextNode("x");
    alertSpan1.appendChild(span1Text);

    var alertSpan2 = document.createElement("span");
    alertSpan2.setAttribute("class", "sr-only")
    var span2Text = document.createTextNode("Close");
    alertSpan2.appendChild(span2Text);

    alertBtn.appendChild(alertSpan1);
    alertBtn.appendChild(alertSpan2);

    var info = document.createTextNode(text);

    alertDiv.appendChild(alertBtn);
    alertDiv.appendChild(info);

    var blogMasthead = document.getElementsByClassName("blog-masthead")[0];
    insertAfter(alertDiv, blogMasthead);
}

// 处理refresh链接的点击
function refresh() {
    if (!document.getElementById("refresh")) return;

    var refreshLink = document.getElementById("refresh");
    refreshLink.onclick = function () {

        function success(text) {
            showInfo(text);
        }

        function fail(code) {
            alert(code);
        }

        var request = new XMLHttpRequest(); // 新建XMLHttpRequest对象

        request.onreadystatechange = function () { // 状态发生变化时，函数被回调
            if (request.readyState === 4) { // 成功完成
                // 判断响应结果:
                if (request.status === 200) {
                    // 成功，通过responseText拿到响应的文本:
                    return success(request.responseText);
                } else {
                    // 失败，根据响应码判断失败原因:
                    return fail(request.status);
                }
            } else {
                // HTTP请求还在继续...
            }
        }

        // 发送请求:
        request.open('GET', '/admin/refresh_all');
        request.send();

        // 不让link发生作用
        return false;
    };
}

// 为导航条的当前项目增加 `active` class
var curHref = document.location.href;
$('.blog-nav').find('a').each(function () {
    var curHrefReg = new RegExp('^'+this.href+'(|[\\d\\s#])$')
    if (curHrefReg.test(curHref)) {
        $(this).addClass('active');  // this.className += 'active';
    }
});

$(function() {
    function footerPosition() {
        let footer = $('.blog-footer')
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

addLoadEvent(refresh);

