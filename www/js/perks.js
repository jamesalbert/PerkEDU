$(document).ready(function() {
    document.addEventListener('deviceready', function() {
        var host = 'http://jamesalbert.com/';
        $.ajax({
            url: host + 'reportperks',
            type: 'GET',
            success: function(res) {
                if (res.status) {
                    $.ajax({
                        url: host + 'build/perk',
                        type: 'POST',
                        contentType: 'application/json',
                        dataType: 'html',
                        data: JSON.stringify(res.bodies),
                        success: function(nr) {
                            $('div.row').append(nr);
                        }
                    })
                }
            }
        })
    });

    document.addEventListener('backbutton', function() {
        window.location.replace('index.html');
    })
})
