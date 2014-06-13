$(document).ready(function() {
    var host = 'http://jamesalbert.com/';
    var lat = lan = 0;
    $('button#checkin').attr('disabled', 'disabled');
    $('button#checkout').attr('disabled', 'disabled');

    function check_distance() {
        navigator.geolocation.getCurrentPosition(function(p) {
            lat = window.btoa(p.coords.latitude.toString());
            lon = window.btoa(p.coords.longitude.toString());
            payload = {
                latitude: lat,
                longitude: lon
            };
            $.ajax({
                url: host + 'checkin',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(payload),
                success: function(res) {
                    if (res.status) {
                        alert(res.status);
                        $('button#checkin').attr('disabled', 'disabled');
                        $('button#checkout').removeAttr('disabled');
                        incrPoints();
                    }
                    else if (res.error) {
                        alert(res.error);
                    }
                }
            });
        }, function(e) { alert(e.code);
            alert(e.message);
            //return e.message;
        },  {enableHighAccuracy: false});
    }

    function recheck_distance() {
        navigator.geolocation.getCurrentPosition(function(p) {
            lat = window.btoa(p.coords.latitude.toString());
            lon = window.btoa(p.coords.longitude.toString());
            payload = {
                latitude: lat,
                longitude: lon
            };
            $.ajax({
                url: host + 'checkup',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(payload),
                success: function(res) {
                    if (res.status) {
                        alert(res.status);
                    }
                    else if (res.error) {
                        alert(res.error);
                    }
                }
            });
        }, function(e) {
            alert(e.code);
            alert(e.message);
            //return e.message;
        },  {enableHighAccuracy: false});
    }

    function incrPoints() {
        setInterval(function() {
            recheck_distance();
        }, 5000); //900000);
    }

    document.addEventListener('deviceready', function() {
        $('button#checkin').removeAttr('disabled');
        $.get(host + 'checkstat', function(res) {
            if (res.status == true) {
                $('button#checkout').removeAttr('disabled');
                $('button#checkin').attr('disabled', 'disabled');
                incrPoints();
            }
            else {
                $('button#checkin').removeAttr('disabled');
            }
        })
    }, false);

    document.addEventListener('backbutton', function() {
        window.location.replace('index.html');
    }, false);

    $('button#checkin').click(function() {
        check_distance();
    });
    $('button#checkout').click(function() {
        $.ajax({
            url: host + 'checkout',
            type: 'POST',
            // contentType: 'application/json',
            success: function(res) {
                if (res.status) {
                    alert(res.status);
                    $('button#checkin').removeAttr('disabled');
                    $('button#checkout').attr('disabled', 'disabled');
                }
                else if (res.error) {
                    alert(res.error);
                }
            }
        })
    })
})
