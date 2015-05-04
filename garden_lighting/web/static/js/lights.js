target = "http://" + window.location.host;

function on(name) {
    return $.getJSON(target + "/api/" + name + "/on/", function (data) {
        if (data["success"]) {
            toastr.success('Erfolgreich angeschalten')
        } else {
            toastr.error('Anschalten fehlgeschlagen')
        }
    });
}

function off(name) {
    return $.getJSON(target + "/api/" + name + "/off/", function (data) {
        if (data["success"]) {
            toastr.success('Erfolgreich ausgeschalten')
        } else {
            toastr.error('Auschalten fehlgeschlagen')
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

    $('#all_on').click(function () {
        on("all");

        light_toggles.removeClass('btn-danger');
        light_toggles.addClass('btn-success');
        light_toggles.text("Auschalten");
    });

    $('#all_off').click(function () {
        off("all");

        light_toggles.removeClass('btn-success');
        light_toggles.addClass('btn-danger');
        light_toggles.text("Anschalten");
    });

    light_toggles.click(function () {
        var switch_id = $(this).attr('id');

        //Find id
        var id = switch_id.substring("light-switch_".length, switch_id.length);

        if ($(this).hasClass('btn-success')) {
            $(this).text("Anschalten");

            on(id);
        } else if ($(this).hasClass('btn-danger')) {
            $(this).text("Ausschalten");

            off(id);
        }

        $(this).toggleClass('btn-success');
        $(this).toggleClass('btn-danger');

        //Reset spinbox
        $(".spinbox").spinbox('value', 0)
    });
});