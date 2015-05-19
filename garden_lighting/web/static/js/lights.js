target = "http://" + window.location.host;

function on(name, duration) {
    return apiRequest("/api/" + name + "/on/" + duration, 'Erfolgreich angeschalten', 'Anschalten fehlgeschlagen');
}

function off(name, duration) {
    return apiRequest("/api/" + name + "/off/" + duration, 'Erfolgreich ausgeschalten', 'Auschalten fehlgeschlagen');
}

function automatic(name) {
    return apiRequest("/api/" + name + "/automatic/", 'Erfolgreich auf Autamatisch geschalten', 'Fehlgeschlagen auf Autamatisch zu schalten');
}

function apiRequest(path, sucess_msg, error_msg) {

    return $.getJSON(target + path, function (data) {
        if (data["success"]) {
            toastr.success(sucess_msg)
        } else {
            toastr.error(error_msg)
        }

        reload();
    });
}

function reload() {
    //$("#lights").fadeOut(100);
    return $.getJSON(target + "/api/devices", function (data) {
        data['devices'].map( function(device) {
            html = $("#" + device['short_name']);
            if (html.length == 1) {
                var button = html.find(".light-switch");

                if (device['state']) {
                    button.text("Ausschalten");
                    button.addClass("btn-success");
                    button.removeClass("btn-danger");
                } else {
                    button.text("Anschalten");
                    button.addClass("btn-danger");
                    button.removeClass("btn-success");
                }

                var mode_button = html.find(".mode");
                console.log(mode_button);
                if (device['manual']) {
                    mode_button.removeClass("hidden")
                } else {
                    mode_button.addClass("hidden")
                }
            }
        });

         //$("#lights").fadeIn(100);
    });
}

function getDuration() {

    var duration = $('input[name=duration]:checked', '.duration-selector').data("value");

    if (duration == undefined) {
        duration = 0
    }

    return duration;
}

function addManualModeButton(id) {
    $('.mode[data-value=' + id + ']').removeClass("hidden");
}

$(document).ready(function () {
    setInterval(reload, 4000);

    var light_toggles = $('.light-switch');

    toastr.options = {
        "newestOnTop": true,
        "positionClass": "toast-bottom-full-width",
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "2000"
    };

    $('.on').click(function () {
        var duration = getDuration();
        var id = $(this).data("target");
        on(id, duration);
    });

    $('.off').click(function () {
        var duration = getDuration();
        var id = $(this).data("target");
        off(id, duration);
    });

    $('.mode').click(function () {
        var id = $(this).data("value");
        automatic(id);
    });

    light_toggles.click(function () {
        var duration = getDuration();

        var id = $(this).data("value");

        if ($(this).hasClass('btn-success')) {
            off(id, duration);
        } else if ($(this).hasClass('btn-danger')) {
            on(id, duration);
        }
    });
});