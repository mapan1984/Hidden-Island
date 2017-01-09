'use strict';

function addLoadEvent(func){
    var oldonload = window.onload;
    if(typeof window.onload != 'function'){
        window.onload = func;
    }else{
        window.onload = function () {
            oldonload();
            func();
        }
    }
}

function insertAfter(newElement, targetElement){
    var parent = targetElement.parentNode;
    if(parent.lastChild === targetElement){
        parent.appendChild(newElement);
    }else{
        parent.insertBefore(newElement, targetElement.nextSibling);
    }
}

function showInfo(text){
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

    var  alertBtn = document.createElement("button");
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

function refresh(){
    if(!document.getElementById("refresh")) return;

    var refreshLink = document.getElementById("refresh");
    refreshLink.onclick = function(){

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
        request.open('GET', '/admin/refresh');
        request.send();
        return false;
    };
}

// 为导航条的当前项目增加 `active` class
$('.blog-nav').find('a').each(function () {
    if (this.href == document.location.href) {
        $(this).addClass('active');  // this.className += 'active';
    }
});

addLoadEvent(refresh);
