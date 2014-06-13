$(document).ready(function() {
    document.addEventListener('deviceready', function() {
        var host = 'http://jamesalbert.com/';
        $('body').popover({
            placement: 'top',
            container: 'body',
            html: true,
            selector: '.question_box',
            content: function() {
                return '<div class="head">Question</div>\
                            <div class="content">\
                                <div class="form-group">\
                                    <input type="text" class="form-control" placeholder="Post an answer...">\
                                </div>\
                                <button type="submit" class="btn btn-default btn-block">Post</button>\
                            </div>\
                        <div class="footer ">JetSpring&copy;</div>';
            }
        }).on('click', function() {
            $('.question_box').not('#'+$(this).attr('id')).popover('hide');
            $(this).popover('show');
        });
        $.get(host+'reportquestions', function(res) {
            if (res.status == []) {
                alert('There doesn\'t seem to be anything here.');
            }
            else {
                questions = JSON.stringify(res.status);
                /*
                $('ul.chat').load(host + 'build/question/'+encodeURIComponent(questions), function() {
                    $('.popover-markup>.trigger').popover({
                        html: true,
                        title: function () {
                            return $(this).parent().find('.head').html();
                        },
                        content: function () {
                            return $(this).parent().find('.content').html();
                        },
                        selector: 'div#test'
                    });
                });
                */
                $.ajax({
                    url: host + 'build/question',
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'html',
                    data: questions,
                    success: function(er) {
                        $('ul.chat').append(er);
                    }
                });
            }
        })
            .fail(function() {
                $('div#questions').html('<p>Check your network settings</p>');
            });
    }, false);

    document.addEventListener('backbutton', function() {
        window.location.replace('index.html');
    }, false);
});
