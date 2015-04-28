$("#toggle-on-off").bootstrapSwitch();


$('#list').click(function (event) {
    event.preventDefault();
    $('.item').addClass('list-group-item');
});

$('#grid').click(function (event) {
    event.preventDefault();
    $('.item').removeClass('list-group-item');
});
