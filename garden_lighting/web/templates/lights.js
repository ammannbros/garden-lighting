var tiles = $('.tile');

tiles.click(function () {
    if ($(this).hasClass("on")) {
        $(this).find(".status").html("Aus");
    } else {
        $(this).find(".status").html("An");
    }

    $(this).toggleClass("off");
    $(this).toggleClass("on");
});