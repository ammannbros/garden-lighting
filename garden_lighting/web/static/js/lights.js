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
        addManualModeButton(id);
    });

    $('.off').click(function () {
        var duration = getDuration();
        var id = $(this).data("target");
        off(id, duration);
        addManualModeButton(id);
    });

    $('.mode').click(function () {
        var id = $(this).data("value");
        automatic(id);
        //$(this).remove();
        location.reload(); // We would need to get all information about all devices from server else
    });

    light_toggles.click(function () {
        var duration = getDuration();

        var id = $(this).data("value");

        if ($(this).hasClass('btn-success')) {
            if (duration == 0)  $(this).text("Anschalten");

            off(id, duration);

        } else if ($(this).hasClass('btn-danger')) {
            if (duration == 0)  $(this).text("Ausschalten");


            on(id, duration);
        }

        if (duration == 0) {
            $(this).toggleClass('btn-success');
            $(this).toggleClass('btn-danger');
        }


        addManualModeButton(id);
    });
});