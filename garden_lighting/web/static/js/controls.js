$(document).ready(function () {
    $("#add").click(function () {
        var devices = [];

        $(".light-selection").each(function () {
            if ($(this).is(':checked')) {
                devices.push($(this).val());
            }
        });

        var duration = $("#hours").spinbox('value') * 60 * 60 + $("#minutes").spinbox('value') * 60;

        var start_time = $($("#start-time").find("input")[0]).val().split(":");

        var rules = [];

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
            }
        });
    });
});