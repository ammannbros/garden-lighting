//$('#list').click(function (event) {
//    event.preventDefault();
//    $('.item').addClass('list-group-item');
//});
//
//$('#grid').click(function (event) {
//    event.preventDefault();
//    $('.item').removeClass('list-group-item');
//});

//$('.row').click(function () {
//    var row_id = $(this).attr('id');
//    var id = row_id.substring("row_".length, row_id.length);
//
//    $("#switch_" + id).bootstrapSwitch('toggleState');
//});

toastr.options = {
    "closeButton": false,
    "debug": false,
    "newestOnTop": true,
    "progressBar": false,
    "positionClass": "toast-bottom-full-width",
    "preventDuplicates": true,
    "onclick": null,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "2000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
};

$('.light-switch').click(function () {
    var switch_id = $(this).attr('id');
    var id = switch_id.substring("light-switch_".length, switch_id.length);

    if ($(this).hasClass('btn-success')) {
        $(this).text("Anschalten");
        toastr.success('Erfolgreich angeschalten')
    } else if ($(this).hasClass('btn-danger')) {
        $(this).text("Ausschalten");
        toastr.success('Erfolgreich ausgeschalten')
    }

    $(this).toggleClass('btn-success');
    $(this).toggleClass('btn-danger');

    $(".spinbox_" + id).spinbox('value', 0)
});
