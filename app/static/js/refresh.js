'use strict';

function refresh(){
    function success(text) {
        alert(text);
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
}

var refreshLink = document.getElementById("refresh");
refreshLink.onclick = function(){
    refresh()
    return false;
};
