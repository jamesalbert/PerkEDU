$(document).ready(function() {
    document.addEventListener('deviceready', function() {
        $('button#submit').removeAttr('disabled');
    }, false);

    document.addEventListener('backbutton', function() {
        window.location.replace('bulletin.html');
    }, false);

    $('#qform').submit(function(e) {
        e.preventDefault();
        var post = $.post('http://jamesalbert.com/postquestion', $('#qform').serialize() );
        post.done(function() {
            window.location.replace('bulletin.html')
        });
    });
});
