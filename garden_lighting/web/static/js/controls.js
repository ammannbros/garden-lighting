function getUrlVars() {
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

function updateNext(actives) {
    if (actives == 0) {
        $('#next').addClass("disabled");
    } else {
        $('#next').removeClass("disabled");
    }
}

function addSelectedRules() {
    var devices = [];

    //Devices
    $(".light-selection").each(function () {
        if ($(this).is(':checked')) {
            devices.push($(this).val());
        }
    });

    //Duration
    var duration = $("#hours").spinbox('value') * 60 * 60 + $("#minutes").spinbox('value') * 60;

    //Start Time
    var start_time = $($("#start-time").find("input")[0]).val().split(":");

    var rules = [];

    //Create on and off rule for each selected weekday
    $('.start').children(".active").children("input").each(function () {
        var rule = {
            weekday: $(this).data("value"),
            devices: devices,
            time: start_time[0] * 60 * 60 + start_time[1] * 60,
            action: "on"
        };

        rules.push(rule);

        rules.push({
            weekday: rule.weekday,
            devices: rule.devices,
            time: rule.time + duration,
            action: "off"
        });
    });


    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(rules),
        dataType: 'json',
        url: "http://" + window.location.host + "/api/add_rules/",
        success: function (e) {
            console.log(e);
            window.location.href = "http://" + window.location.host + "/controls/?completed=true";
        }
    });
}

$(document).ready(function () {
    var wizard = $('.wizard');

    //Show toast
    toastr.options = {
        "newestOnTop": true,
        "positionClass": "toast-bottom-full-width",
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "2000"
    };

    if (getUrlVars()["completed"] == "true") {
        toastr.success('Regeln erfolgreich hinzugefügt');
    }

    //Next/Previous updates
    wizard.on('actionclicked.fu.wizard', function (evt, data) {
        if (data.step == 2) {
            return;
        }

        if (data.direction == "next") {
            $('#next').addClass("disabled");
        } else {
            $('#next').removeClass("disabled");
        }
    });

    $('.checkbox-custom').click(function () {
        var active = $('.light-selection').filter(":checked").size();

        updateNext(active);
    });

    $('.start').find(".btn").click(function () {
        var active = $('.start').children(".active").children("input").size() + ($(this).hasClass("active") ? -1 : 1);

        updateNext(active);
    });

    $(".add").click(addSelectedRules);
    wizard.on('finished.fu.wizard', addSelectedRules);
});