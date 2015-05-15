target = "http://" + window.location.host;

function on(name) {
    return apiRequest("/api/" + name + "/on/", 'Erfolgreich angeschalten', 'Anschalten fehlgeschlagen');
}

function off(name) {
    return apiRequest("/api/" + name + "/off/", 'Erfolgreich ausgeschalten', 'Auschalten fehlgeschlagen');
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
    });
}

$(document).ready(function () {
    var light_toggles = $('.light-switch');

    toastr.options = {
        "newestOnTop": true,
        "positionClass": "toast-bottom-full-width",
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "2000"
    };

    $('.on').click(function () {
        on($(this).data("target"));
    });

    $('.off').click(function () {
        off($(this).data("target"));
    });

    $('.mode').click(function () {
        var id = $(this).data("value");
        automatic(id);
    });

    light_toggles.click(function () {
        var id = $(this).data("value");

        if ($(this).hasClass('btn-success')) {
            $(this).text("Anschalten");

            off(id);
        } else if ($(this).hasClass('btn-danger')) {
            $(this).text("Ausschalten");

            on(id);
        }

        $(this).toggleClass('btn-success');
        $(this).toggleClass('btn-danger');
    });
});