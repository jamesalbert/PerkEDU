$(document).ready(function() {
    document.addEventListener('deviceready', function() {
        var host = 'http://jamesalbert.com/';
        function logout() {
            $.get(host + 'logout', function(res) {
                alert('logged out');
            });
        }
        $.get(host + 'loggedin', function(res) {
            if (res.status != true) {
                alert('you\'re not logged in')
                ref = window.open(host + 'welcome', '_blank', 'location=no');
                ref.addEventListener('loadstop', function(event) {
                    if (event.url.match(host + "welcome")) {
                        ref.close();
                        $.get(host + 'welcome', function(res) { alert(res.status); });
                        window.location.replace('index.html')
                    }
                });
            }
        })
    });
})
