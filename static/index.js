$(document).ready(function() {
    $.support.cors = true;
    document.addEventListener("deviceready", main, false);
    main();
    function main() {
        var netstate;
        var test = cordova.exec(
                function(p) {netstate = p;},
                function(error) {alert("Network Manager error: "+error);},
                "NetworkStatus",
                "getConnectionInfo",
                []
        );

        if (navigator.connection.type == 'wifi') {
            alert('connected to router');
            num = 0;
            i = setInterval(incr, 1000); //900000); // 15 minutes
            function incr() {
                if (num > 1) {
                    clearInterval(i);
                }
                else {
                    num += 1;
                    $.ajax({
                        url: "http://jamesalbert.com/ping",
                        type: "GET",
                        dataType: "html",
                        success: function(res) {
                            $('li.active').append(JSON.stringify(res) + "<br />");
                        },
                        error: function(x,s,h) {
                            $('li.active').append(JSON.stringify(x)+"<br />")
                        }
                    })
                }
            }
        }
    }
})
