$(document).ready(function() {
    var host = 'http://jamesalbert.com/';
    document.addEventListener('deviceready', function() {
        $('.popover-markup>.trigger').popover({
            html: true,
            title: function () {
                return $(this).parent().find('.head').html();
            },
            content: function () {
                return $(this).parent().find('.content').html();
            }
        });
        $.ajax({
            url: host + 'profile',
            type: 'GET',
            success: function(res) {
                var check_stat = 'checked in';
                if (!res.checked_in) {
                    check_stat = 'not ' + check_stat;
                }
                $('#user_name').append(res.name);
                $('#user_points').append(res.points);
                $('#user_email').append(res.email);
                $('#user_status').append(check_stat)
            }
        });
    }, false);

    document.addEventListener('backbutton', function() {
        var c = confirm('Are you sure you want to exit PerkEDU');
        if (c) {
            navigator.app.exitApp();
        }
    }, false);
})
