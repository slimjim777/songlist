
function changeTheme(theme) {
    if (theme == 'dark') {
        $('body').toggleClass('body-dark', true);
        $('#light').toggleClass('btn-default', true);
        $('#light').toggleClass('btn-primary', false);
        $('#dark').toggleClass('btn-default', false);
        $('#dark').toggleClass('btn-primary', true);
    } else {
        $('body').toggleClass('body-dark', false);
        $('#light').toggleClass('btn-default', false);
        $('#light').toggleClass('btn-primary', true);
        $('#dark').toggleClass('btn-default', true);
        $('#dark').toggleClass('btn-primary', false);
    }
}

function changeKey(key) {
    // Send POST message to change key
    $('#key').val(key);
    $('#transpose').submit();
    console.log(key);
    return false;
}