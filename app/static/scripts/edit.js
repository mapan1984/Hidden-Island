$(function() {
    let preview = $('.flask-pagedown-preview');
    let editForm = $('.flask-pagedown textarea');
    
    let preHeight = preview.height();
    let winHeight = window.innerHeight;

    editForm.css('height', Math.max(preHeight, winHeight)+'px');

    editForm.change(function() {
        // console.log('preview is change');
        let preHeight = preview.height();
        let winHeight = window.innerHeight;

        editForm.css('height', Math.max(preHeight, winHeight)+'px');
    })
});

