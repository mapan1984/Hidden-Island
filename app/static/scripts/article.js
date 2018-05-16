'use strict';

(function($){
    $.fn.toc = function(options) { // bind toc fun to $
        var defaults = {
            noBackToTopLinks: true,
            title: '<span class="label label-info">文章目录</span>',
            minimumHeaders: 2,
            headers: 'h1, h2, h3, h4, h5, h6',
            listType: 'ul', // values: [ol|ul]
            listStyle: 'list-group', // `nav nav-pills nav-stacked`|`list-group`
            listItemStyle: 'list-group-item', // `nav nav-pills nav-stacked`|`list-group`
            showEffect: 'show', // values: [show|slideDown|fadeIn|none]
            showSpeed: 'slow' // set to 0 to deactivate effect
        };
        var settings = $.extend(defaults, options);// use options > defaults

        function fixedEncodeURIComponent (str) {
            return encodeURIComponent(str).replace(/[!'()*]/g, function(c) {
                return '%' + c.charCodeAt(0).toString(16);
            });
        }

        var headers = $(settings.headers).filter(function() {
            // get all headers with an ID
            var previousSiblingName = $(this).prev().attr( "name" );
            if (!this.id && previousSiblingName) {
                this.id = $(this).attr( "id", previousSiblingName.replace(/\./g, "-") );
            }
            return this.id;
        }), output = $(this);
        if (!headers.length || headers.length < settings.minimumHeaders || !output.length) {
            $(this).hide();
            return;
        }

        if (0 === settings.showSpeed) {
            settings.showEffect = 'none';
        }

        var render = {
            show: function() { output.hide().html(html).show(settings.showSpeed); },
            slideDown: function() { output.hide().html(html).slideDown(settings.showSpeed); },
            fadeIn: function() { output.hide().html(html).fadeIn(settings.showSpeed); },
            none: function() { output.html(html); }
        };

        var get_level = function(ele) { return parseInt(ele.nodeName.replace("H", ""), 10); }
        var highest_level = headers.map(function(_, ele) { return get_level(ele); }).get().sort()[0];
        var return_to_top = '<i class="icon-arrow-up back-to-top"> </i>';

        var last_level = get_level(headers[0]);
        var this_level;

        // Start of Toc html
        //let html = `${settings.title} <${settings.listType} class='nav nav-pills nav-stacked'>`;
        let html = `${settings.title} <${settings.listType} class="${settings.listStyle}">`;

        // Add all headers html
        headers.on('click', function() { // bind click fun in header
            if (!settings.nobacktotoplinks) {
                window.location.hash = this.id;
            }
        })
        .addClass('clickable-header')
        //.addClass('anchor')
        .each(function(_, header) {
            this_level = get_level(header);
            if (!settings.noBackToTopLinks && this_level === highest_level) {
                $(header).addClass('top-level-header').after(return_to_top);
            }

            if (this_level === last_level){// same level as before; same indenting
                html += `<li class="${settings.listItemStyle}"><a href='#${fixedEncodeURIComponent(header.id)}'>${header.innerHTML}</a>`;
            } else if (this_level < last_level){ // higher level than before; end parent ol
                for(let i = this_level; i < last_level; i++) {
                    html += `</li></${settings.listType}>`
                }
                html += `<li class="${settings.listItemStyle}"><a href='#${fixedEncodeURIComponent(header.id)}'>${header.innerHTML}</a>`;
            } else if (this_level > last_level) { // lower level than before; expand the previous to contain a ol
                for(let i = this_level; i > last_level; i--) {
                    html += `<${settings.listType} class="${settings.listStyle}"><li class="${settings.listItemStyle}">`
                }
                html += `<a href='#${fixedEncodeURIComponent(header.id)}'>${header.innerHTML}</a>`;
            }

            last_level = this_level; // update for the next one
        });

        // End of toc html
        html += "</"+settings.listType+">";

        if (!settings.noBackToTopLinks) {
            $(document).on('click', '.back-to-top', function() {
            $(window).scrollTop(-70);
            window.location.hash = '';
          });
        }
        render[settings.showEffect]();
    };
})(jQuery);

/**
 * @param {number} initTop 初始距顶部距离
 * @param {number} finalTop 最终希望距顶部距离
 */
$(document).ready(function() {
    let toc = $('#toc');                      // dom侧栏
    toc.toc();                                // fun生成侧栏标题目录

    $('body').scrollspy({ target: '#toc' });  // fun开启滚动监听

    let initTop = 550;
    let finalTop = 80;
    $(window).on('scroll', function(){        // fun动态调整侧栏位置
        let osTop = $(document).scrollTop();  // num获取滚动条距离顶部的高度
        if (osTop <= initTop) {
            toc.css('top', (initTop - osTop + osTop/initTop*finalTop) + 'px');
        } else {
            toc.css('top', finalTop + 'px');
        }
    });
});

$(document).ready(function() {                // fun返回顶部按钮行为
    let obtn = $('#back-to-top');
    obtn.on('click', function(){
        $('html, body').animate({scrollTop: 0}, 800)
    });
    $(window).on('scroll', function(){
        if($(window).scrollTop() > $(window).height()){
            obtn.fadeIn();
        }else{
            obtn.fadeOut();
        }
    });
    $(window).trigger('scroll');
});
