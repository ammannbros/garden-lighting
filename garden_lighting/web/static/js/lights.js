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
            toastr.success('Erfolgreich angeschalten')
        } else {
            toastr.error('Anschalten fehlgeschlagen')
        }
    });
}

$(document).ready(function () {
    toastr.options = {
        "newestOnTop": true,
        "positionClass": "toast-bottom-full-width",
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "2000"
    };

    $('#all_on').click(function () {
        on("all")
    });

    $('#all_off').click(function () {
        off("all")
    });

    $('.light-switch').click(function () {
        var switch_id = $(this).attr('id');
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

        $(".spinbox_" + id).spinbox('value', 0)
    });
});