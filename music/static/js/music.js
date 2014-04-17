
function changeTheme(theme) {
    if (theme == 'dark') {
        $('body').toggleClass('body-dark', true);
        $('#light').toggleClass('active', false);
        $('#dark').toggleClass('active', true);
    } else {
        $('body').toggleClass('body-dark', false);
        $('#light').toggleClass('active', false);
        $('#dark').toggleClass('active', true);        
    }
    
}