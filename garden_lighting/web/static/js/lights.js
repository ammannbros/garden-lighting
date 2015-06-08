target = "http://" + window.location.host;

function on(name, duration) {
    return apiRequest("/api/" + name + "/on/" + duration, 'Erfolgreich eingeschalten.', 'Einschalten fehlgeschlagen.');
}

function off(name, duration) {
    return apiRequest("/api/" + name + "/off/" + duration, 'Erfolgreich ausgeschalten.', 'Auschalten fehlgeschlagen.');
}

function automatic(name) {
    return apiRequest("/api/" + name + "/automatic/", 'Erfolgreich auf autamatischen Modus geschalten', 'Fehler beim Schalten auf automatischen Modus.');
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
    return $.getJSON(target + "/api/devices", function (data) {
        data['devices'].map(function (device) {
            html = $("#" + device['short_name']);
            if (html.length == 1) {
                var button = html.find(".light-switch");

                if (device['state']) {
                    button.text("Ausschalten");
                    button.addClass("btn-success");
                    button.removeClass("btn-danger");
                } else {
                    button.text("Einschalten");
                    button.addClass("btn-danger");
                    button.removeClass("btn-success");
                }

                var mode_button = html.find(".mode");
                if (device['manual']) {
                    mode_button.removeClass("hidden")
                } else {
                    mode_button.addClass("hidden")
                }

                timer = html.find(".timer");

                if ('next_time' in device) {

                    var date = new Date(device['next_time'] * 1000);
                    timer.data("action", device['next_action']);


                    timer.countdown(new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(),
                        date.getUTCHours(), date.getUTCMinutes(), date.getUTCSeconds(), date.getUTCMilliseconds()), function (event) {

                        var action = $(this).data("action");

                        if (action == "on") {
                            action = "Einschalten"
                        } else if (action == "off") {
                            action = "Ausschalten"
                        }

                        var format = '';

                        if (event.offset.days > 0) {
                            format += '%dd ';
                        }

                        if (event.offset.days > 0 || event.offset.hours > 0) {
                            format += '%Hh ';
                        }

                        if (event.offset.hours > 0 || event.offset.minutes > 0) {
                            format += '%Mm ';
                        }

                        if (event.offset.minutes > 0 || event.offset.seconds > 0) {
                            format += '%Ss ';
                        }

                        var formattedTime = event.strftime(format);

                        if (formattedTime != "") {
                            $(this).text(action + " in " + formattedTime);
                        } else {
                            $(this).text("");
                        }

                    });
                } else {
                    timer.countdown('')
                }

            }
        });
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

function disableButton(button) {
    $(button).prop('disabled', true);
    setTimeout(function () {
        $(button).prop('disabled', false);
    }, 3000);
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
        disableButton(this)
    });

    $('.off').click(function () {
        var duration = getDuration();
        var id = $(this).data("target");
        off(id, duration);
        disableButton(this)
    });

    $('.mode').click(function () {
        var id = $(this).data("value");
        automatic(id);
    });

    $('#refresh').click(function () {
        reload();
        toastr.success("Lichter neu geladen.")
    });

    light_toggles.click(function () {
        var duration = getDuration();

        var id = $(this).data("value");

        if ($(this).hasClass('btn-success')) {
            off(id, duration);
        } else if ($(this).hasClass('btn-danger')) {
            on(id, duration);
        }

        reload();
        disableButton(this);
    });

    reload()
});