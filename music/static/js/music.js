
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

function keySelectClick(el) {
    // Change the key
    var key = el.innerHTML;
    changeKey(key);

    // Deactivate/activate the buttons
    $('#key-select > .btn').removeClass('active');
    $('#key-select > .btn').removeClass('btn-primary');
    $('#key-select > .btn').addClass('btn-default');
    $(el).toggleClass('btn-primary');
}

function changeKey(key) {
    // Send POST message to change key
    var t = {
        song: song,
        key: key
    };
    
    $.ajax({
        type: "POST",
        url: "/song/transpose",
        data: JSON.stringify(t),
        contentType: "application/json; charset=utf-8",
        dataType: "json"
        
    }).done( function(data){
        if ((data.response) && (data.response == 'Failed')) {
            var html = '<div id="alert" class="alert alert-danger"> Error: ' + data.error + '</div>';
            $('#main').prepend(html);
            $('#alert').hide().fadeIn(1000);
            return;
        }
        // Song returned in the new key
        song = data;
        renderSong();
    }).fail( function(a, b, c) {
        // Error
        var html = '<div class="alert alert-danger"> Error: ' + c + '</div>';
        $('#main').prepend(html);
    });

}

function renderSong() {
    var html = '';
    
    // Go through the song sections
    for (var i in song.display_order) {
        var section = song.display_order[i];
        html += '<h3>' + section + '</h3>';
        
        // Get the lines for the section
        for (var j in song[section]) {
            var line = song[section][j];
            var html_line = '<div class="cnl_line">';
            
            for (var k in line.lyrics) {
                html_line += '<div class="cnl">';
                html_line += '  <div class="chord">' + (line.chords[k] ? line.chords[k] : '') + '&nbsp;</div>';
                html_line += '  <div class="lyric">' + (line.lyrics[k] ? line.lyrics[k] : '') + '&nbsp;</div>';
                html_line += '</div>';
            }
            html_line += '</div>';
            
            // Add the lyric line to the section
            html += html_line;
        }
        
        html += '<br />';
    }
    
    // Add the Copyright section
    if ((song.Copyright) && (song.CCLI)) {
        html += '<p class="footer">Copyright ' + song.Copyright + ' (CCLI:' + song.CCLI + ')</p>';
    } else if (song.Copyright) {
        html += '<p class="footer">Copyright ' + song.Copyright + '</p>';    
    } else if (song.CCLI) {
        html += '<p class="footer">' + song.CCLI + '</p>';
    };
    
    var main = $('#main');
    main.empty();
    main.append(html);
}