'use strict';

$(function() {
    // 在targetElement后插入newElement
    function insertAfter(newElement, targetElement) {
        let parent = targetElement.parentNode;
        if (parent.lastChild === targetElement) {
            parent.appendChild(newElement);
        } else {
            parent.insertBefore(newElement, targetElement.nextSibling);
        }
    }

    /*
     * 在页面中展示text信息
     * - text  : 要展示的信息(可以含有html标签)
     * - type  : 警告框的类型，可选`alert-success`, `alert-info`,
     *                             `alert-warning`, `alert-danger`
     * - place : 展示在place之后，place是DOM元素的类名，而且取第一个拥有
     *           此类名的DOM元素
     */
    function showAlert(text, type="alert-info", place="navbar") {
        let alertDiv = document.createElement("div");
        alertDiv.setAttribute("class", `alert ${type} alert-dismissible`);
        alertDiv.setAttribute("role", "alert");
        alertDiv.innerHTML =
            `
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
            ${text}
            `;

        let alertPlace = document.getElementsByClassName(`${place}`)[0];
        if (alertPlace) {
            insertAfter(alertDiv, alertPlace);
        } else {
            console.error(`class ${place} not exist.`);
        }
    }


    // 对url发送get请求，处理返回消息
    function getInfo(url) {
        let request = new XMLHttpRequest(); // 新建XMLHttpRequest对象

        request.onreadystatechange = function () { // 状态发生变化时，函数被回调
            if (request.readyState === 4) { // 成功完成
                // 判断响应结果:
                if (request.status === 200) {
                    // 成功，通过responseText拿到响应的文本:
                    return showAlert(request.responseText);
                } else {
                    // 失败，根据响应码判断失败原因:
                    return showAlert(request.status, type='alert-danger');
                }
            } else {
                // HTTP请求还在继续...
            }
        };

        // 发送请求:
        request.open('GET', url);
        request.send();
    }

    // 处理refresh_all
    let refreshLink = document.getElementById('refresh-all');
    if (refreshLink) {
        refreshLink.onclick = function() {
            getInfo(this.href);

            // 不让link发生作用
            return false;
        };
    }

    // 处理单个refresh
    let tbody = document.querySelectorAll('tbody')[0];
    if (tbody) {
        tbody.addEventListener('click', function(event_) {
            let event = event_ || window.event;
            let target = event.target || event.srcElement;
            if (target.nodeName.toLocaleLowerCase() == 'button') {
                getInfo(target.id);
            }
        });
    }
});
