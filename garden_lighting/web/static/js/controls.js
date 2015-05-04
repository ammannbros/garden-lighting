target = "http://" + window.location.host;

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

function getDuration() {
    return $("#hours").spinbox('value') * 60 * 60 + $("#minutes").spinbox('value') * 60;
}

function getStartTimeText() {
    return $($("#start-time").find("input")[0]).val();
}

function getStartTime() {
    return getStartTimeText().split(":");
}

function getDevices() {
    var devices = [];
    $(".light-selection").each(function () {
        if ($(this).is(':checked')) {
            devices.push($(this).val());
        }
    });
    return devices
}

function getDeviceNames() {
    var devices = [];
    $(".light-selection").each(function () {
        if ($(this).is(':checked')) {
            devices.push($(this).parent("label").text());
        }
    });
    return devices
}

function getWeekdays() {
    var weekdays = [];
    $('.start').children(".active").children("input").each(function () {
        weekdays.push($(this).data("value"));
    });

    return weekdays;
}

function getLocalizedWeekdays() {
    var str = "";

    var weekdays = getWeekdays();
    weekdays.forEach(function (weekday, i) {
        switch (weekday) {
            case 0:
                str += "Montag";
                break;
            case 1:
                str += "Dienstag";
                break;
            case 2:
                str += "Mittwoch";
                break;
            case 3:
                str += "Donnerstag";
                break;
            case 4:
                str += "Freitag";
                break;
            case 5:
                str += "Samstag";
                break;
            case 6:
                str += "Sonntag";
                break;
        }

        if (i == weekdays.length - 2) {
            str += " und "
        } else if (i < weekdays.length - 2) {
            str += ", "
        }

    });

    return str;
}

function deleteRule(rule, item) {
    return $.getJSON(target + "/api/delete_rule/" + rule, function (data) {
        if (data["success"]) {
            toastr.success('Erfolgreich gelöscht');
            item.remove()
        } else {
            toastr.error('Löschen fehlgeschlagen')
        }
    });
}

function addSelectedRules() {
    //Devices
    var devices = getDevices();

    //Duration
    var duration = getDuration();

    //Start Time
    var start_time = getStartTime();
    var rules = [];


    //Create on and off rule for each selected weekday
    getWeekdays().forEach(function (weekday) {
        var rule = {
            weekday: weekday,
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

    wizard.on('actionclicked.fu.wizard', function (evt, data) {
        if (data.step == 2) {
            $("#summary").text("Die Lichter " + getDeviceNames() + " werden von am " + getLocalizedWeekdays() + " von " + getStartTimeText() + " für " + getDuration() + " Sekunden an sein.")
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

    $(".remove").click(function () {
        var item = $(this).parents(".item");
        deleteRule(item.attr("id"), item);
    })
});