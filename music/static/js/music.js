var bpm = 100.0;
var bpb = 4;
var ONEMIN = 60000.0;
var metroStartTime;
var beatCount = 1;
var timeoutId;
var dateFormat = 'dd/mm/yyyy';

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

    // Save the setting for the user
    $.ajax({
        type: "POST",
        url: "/user/theme",
        data: JSON.stringify({theme: theme}),
        contentType: "application/json; charset=utf-8",
        dataType: "json"
    });
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

/* USERS */
function userEdit(userId) {
    var request = $.ajax({
      type: 'GET',
      url: '/admin/users/' + userId,
    }).done( function(data) { 
        if (data) {
            var row = $('#usr' + userId).hide();
            $(row).after(data);
        }
    });
}

function userCancel(ev, userId) {
    ev.preventDefault();
    
    // Remove the editable row and show the read-only row
    $('#usredit' + userId).remove();
    $('#usr' + userId).fadeIn(1000);
}

function userSave(userId) {
    // Get the details of the updated fields from the form
    var postdata = {
        id: userId,
        firstname: $("#usrfirst").val(),
        lastname: $("#usrlast").val(),
        email: $("#usremail").val(),
        role: $("#usrrole option:selected").val(),
    };

    var request = $.ajax({
      type: 'PUT',
      url: '/admin/users/' + userId,
      data: postdata
    }).done( function(data) { 
        if (data.response == 'Success') {
            window.location.href = '/admin';
        } else {
            // Display the error
            $('#main').prepend(getMessage(data.message, 'alert'));
            $('#message').fadeIn(1000).delay(3000).fadeOut(1000).queue(function() { $(this).remove(); });
        }
    });
}

function userAddToggle(ev) {
    ev.preventDefault();
    // Show the add user form
    $('#usrnew').toggleClass('hidden');
}

function userAdd(event) {
    // Get the details of the new person
    var data = {
        firstname: $("#usrnewfirst").val(),
        lastname: $("#usrnewlast").val(),
        email: $("#usrnewemail").val(),
        role: $("#usrnewrole option:selected").val(),
    };

    var request = $.ajax({
      type: 'POST',
      url: '/admin/users',
      data: data
    }).done( function(data) {
        if (data.response == 'Success') {
            window.location.href = '/admin';
        } else {
            // Display the error
            $('#main').prepend(getMessage(data.message, 'alert'));
            $('#message').fadeIn(1000).delay(3000).fadeOut(1000).queue(function() { $(this).remove(); });
        }
    });
}

function userDelete(userId) {

    var name = $('#usrfirstname'+userId).text() + ' ' + $('#usrlastname'+userId).text();
    var postdata = {
        id: userId
    };

    bootbox.dialog({
        message: "Are you sure you want to delete the user record for '" + name + "'?",
        title: 'Delete User',
        buttons: {
            success: {
                label: 'Yes',
                className: 'btn-info',
                callback: function() {
                    var request = $.ajax({
                      type: 'DELETE',
                      url: '/admin/users/' + userId,
                      data: postdata
                    }).done( function(data) {
                        if (data.response == 'Success') {
                            window.location.href = '/admin';
                        } else {
                            // Display the error
                            $('#main').prepend(getMessage(data.message, 'alert'));
                            $('#message').fadeIn(1000).delay(3000).fadeOut(1000).queue(function() { $(this).remove(); });
                        }
                    }).fail( function(a, b, c) {
                         // Error
                         $('#main').prepend(getMessage(a.responseText, 'alert'));
                         $('#message').fadeIn(1000).delay(3000).fadeOut(1000).queue(function() { $(this).remove(); });
                    });

                }
            },
            cancel: {
                label: 'No',
                className: 'btn-default',
                callback: function() {}
            }
        }
    });

}

/* --USERS */

function getMessage(message, type) {
    if (type=='success') {
        return '<div id="message" class="alert alert-success">' + message + '</div>'
    } else {
        return '<div id="message" class="alert alert-danger">' + message + '</div>'
    }
}

/* SONGS */

function songEdit(ev, songId) {
    ev.preventDefault();
    var container = $('#youtube' + songId);

    // Get the song details
    var request = $.ajax({
      type: 'GET',
      url: '/song/' + songId,
    }).done( function(song) {
        if (song) {
            $(container).append(song);
            $('#songedit' + songId).hide();
        }
    });

}

function songSave(songId) {
    var data = {
        url: $('#url' + songId).val(),
        tempo: $('#tempo' + songId).val(),
        time_signature: $('#time' + songId).val()
    };

    var request = $.ajax({
      type: 'POST',
      url: '/song/' + songId,
      data: JSON.stringify(data),
      contentType: "application/json; charset=utf-8",
      dataType: "json"
    }).done( function(data) {
        if (data.response == 'Success') {
            window.location.href = '/songs';
        } else {
            // Display the error
            $('#main').prepend(getMessage(data.message, 'alert'));
            $('#message').fadeIn(1000).delay(3000).fadeOut(1000).queue(function() { $(this).remove(); });
        }
    });

    return false;
}

function songCancel(ev, songId) {
    ev.preventDefault();
    $('#songsave' + songId).remove();
    $('#songedit' + songId).show();
}

/* --SONGS */

/* METRONOME */
function metroTick() {
    if (beatCount == 1) {
        document.getElementById('beepOne').play();
    } else {
        //$('#beep').trigger('play');
        document.getElementById('beep').play();
    }

    beatCount += 1;
    if (beatCount > bpb) {
        beatCount = 1;
    }
}

function metroStart(beats, songId) {
    $('#metroStart'+songId).prop('disabled', true);
    bpm = beats;
    bpb = beatsPerBar();
    metroStartTime = new Date().getTime();
    beat(true);
}

function metroStop(songId) {
    $('#metroStart'+songId).prop('disabled', false);
    clearTimeout(timeoutId);
    beatCount = 1;
}

function beat(first) {
    var interval = ONEMIN / bpm;
    var diff;
    if (!first) {
        // Calculate how far we are off the schedule
        diff = (new Date().getTime()) - metroStartTime - interval;
    } else {
        diff = 0.0;
    }

    // Set the call with an adjusted timeout
    timeoutId = setTimeout("beat()", (interval - diff));
    metroStartTime = new Date().getTime();
    metroTick();
}

/* -- METRONOME */

/* SONG LISTS */

function songlistAddToggle(ev) {
    ev.preventDefault();
    // Show the add song list form
    $('#slnew').toggleClass('hidden');
}

function songlistAdd(event) {
    // Get the details of the new person
    var data = {
        event_date: $("#slnewdate").val(),
        name: $("#slnewname").val(),
        owner_id: $("#slnewownerid").val(),
    };

    var request = $.ajax({
      type: 'POST',
      url: '/songlist/list',
      data: data
    }).done( function(data) {
        if (data.response == 'Success') {
            window.location.href = '/songlist';
        } else {
            // Display the error
            $('#main').prepend(getMessage(data.message, 'alert'));
            $('#message').fadeIn(1000).delay(3000).fadeOut(1000).queue(function() { $(this).remove(); });
        }
    });
}

function songlistEdit(listId) {
    var request = $.ajax({
      type: 'GET',
      url: '/songlist/list/' + listId,
    }).done( function(data) {
        if (data) {
            var row = $('#sl' + listId).hide();
            $(row).after(data);

            // Set up the date picker on the event date
            $('#sldate').datepicker({format: dateFormat});
        }
    });
}

function songlistCancel(ev, listId) {
    ev.preventDefault();

    // Remove the editable row and show the read-only row
    $('#sledit' + listId).remove();
    $('#sl' + listId).fadeIn(1000);
}

function songlistSave(listId) {
    // Get the details of the updated fields from the form
    var postdata = {
        id: listId,
        name: $("#slname").val(),
        event_date: $("#sldate").val(),
    };

    var request = $.ajax({
      type: 'PUT',
      url: '/songlist/list/' + listId,
      data: postdata
    }).done( function(data) {
        if (data.response == 'Success') {
            window.location.href = '/songlist';
        } else {
            // Display the error
            $('#main').prepend(getMessage(data.message, 'alert'));
            $('#message').fadeIn(1000).delay(3000).fadeOut(1000).queue(function() { $(this).remove(); });
        }
    });
}

function songlistDelete(listId) {
    var name = $('#slname'+listId).text();
    var eventDate = $('#sldate'+listId).text();
    var postdata = {
        id: listId
    };

    bootbox.dialog({
        message: "Are you sure you want to delete the song list '" + name + " (" + eventDate + ")'?",
        title: 'Delete Song List',
        buttons: {
            success: {
                label: 'Yes',
                className: 'btn-info',
                callback: function() {
                    var request = $.ajax({
                      type: 'DELETE',
                      url: '/songlist/list/' + listId,
                      data: postdata
                    }).done( function(data) {
                        if (data.response == 'Success') {
                            window.location.href = '/songlist';
                        } else {
                            // Display the error
                            $('#main').prepend(getMessage(data.message, 'alert'));
                            $('#message').fadeIn(1000).delay(3000).fadeOut(1000).queue(function() { $(this).remove(); });
                        }
                    }).fail( function(a, b, c) {
                         // Error
                         $('#main').prepend(getMessage(a.responseText, 'alert'));
                         $('#message').fadeIn(1000).delay(3000).fadeOut(1000).queue(function() { $(this).remove(); });
                    });
                }
            },
            cancel: {
                label: 'No',
                className: 'btn-default',
                callback: function() {}
            }
        }
    });
}

function songlistReorder(ev, listId) {
    ev.preventDefault();

    var request = $.ajax({
      type: 'GET',
      url: '/songlist/' + listId + '/list',
    }).done( function(html) {
        bootbox.confirm(html, function(result) {
            if (result) {
                var new_order = [];
                $('#songlist_sortable li').each( function() {
                    new_order.push(this.id.replace('item',''));
                });
                songlistReorderComplete(listId, new_order)
            }
        });
        $('.sortable').sortable();
    });
}

function songlistReorderComplete(listId, new_order) {
    var postdata = {
        new_order: new_order
    };

    var request = $.ajax({
        type: 'PUT',
        url: '/songlist/' + listId + '/list',
        data: JSON.stringify(postdata),
        contentType: "application/json; charset=utf-8",
        dataType: "json"
    }).done( function(data) {
        window.location.href = '/songlist/' + listId;
    });
}

/* -- SONG LISTS */

/* SONG LIST SONG */

function songlistSongAdd(ev) {
    ev.preventDefault();

    // Show the song search dialog
    var html = '<h3>Find a song and add it to the song list</h3>'
            + '<input id="q" name="q" placeholder="song name" onkeyup="songlistSongSearch(this)" type="search" class="form-control" />'
            + '<div id="songs"></div>';
    bootbox.alert(html, function () {
        var listId = $('#songlist').val();
        window.location.href = '/songlist/' + listId;
    });
}

function songlistSongSearch($el) {
    var q = $($el).val();
    q = $.trim(q);
    if (q.length == 0) {
        return;
    }
    var postdata = {q:q};

    // Search for songs with the text
    var request = $.ajax({
      type: 'POST',
      url: '/songs/find',
      data: postdata
    }).done( function(data) {
        var container = $('#songs');
        $(container).empty()
        $(container).append(data);
    });
}

function songlistSongSelect(songId) {
    var listId = $('#songlist').val();
    var postdata = {
        songlist_id: listId,
        song_id: songId
    };

    // Search for songs with the text
    var request = $.ajax({
      type: 'POST',
      url: '/songlist/' + listId + '/add',
      data: postdata
    }).done( function(data) {
        if (data.response == 'Success') {
            $('#songselect' + songId).fadeOut(1000);
        } else {
            // Display the error
            $('#main').prepend(getMessage(data.message, 'alert'));
            $('#message').fadeIn(1000).delay(3000).fadeOut(1000).queue(function() { $(this).remove(); });
        }
    });
}

function songlistSongRemove(listId, songId) {
    var postdata = {
        songlist_id: listId,
        song_id: songId
    };

    // Search for songs with the text
    var request = $.ajax({
      type: 'DELETE',
      url: '/songlist/' + listId + '/remove',
      data: postdata
    }).done( function(data) {
        if (data.response == 'Success') {
            window.location.href = '/songlist/' + listId;
        } else {
            // Display the error
            $('#main').prepend(getMessage(data.message, 'alert'));
            $('#message').fadeIn(1000).delay(3000).fadeOut(1000).queue(function() { $(this).remove(); });
        }
    }).fail( function(a, b, c) {
         // Error
         $('#main').prepend(getMessage(a.responseText, 'alert'));
         $('#message').fadeIn(1000).delay(3000).fadeOut(1000).queue(function() { $(this).remove(); });
    });
}

function songlistMetronome(index) {
    $('#metro_index').val(index);
    var title = songs[index].name;
    if (songs[index].tempo) {
        $('#metro_tempo').val(songs[index].tempo);
    } else {
        $('#metro_tempo').val('');
    }
    if (songs[index].time_signature) {
        $('#metro_time').text(songs[index].time_signature);
    } else {
        $('#metro_time').text('4/4');
    }
    $('#metro_title').text(title);

    $('.song_list').toggleClass('selected', false);
    $('#song' + songs[index].id).toggleClass('selected', true)
}

function metroNextSong() {
    var index = parseInt($('#metro_index').val()) + 1;
    if (index >= songs.length) {
        index = 0;
    }
    songlistMetronome(index);
}

function metroPreviousSong() {
    var index = parseInt($('#metro_index').val()) - 1;
    if (index < 0) {
        index = songs.length - 1;
    }
    songlistMetronome(index);
}

function toggleMetronome() {
    var tempo = getTempo();

    // Stop or start the metronome
    var button = $('#metro_start_stop');

    if ($(button).hasClass('btn-success')) {
        // Start the metronome
        beatCount = 1;
        bpm = tempo;
        bpb = beatsPerBar();
        metroStartTime = new Date().getTime();
        $(button).toggleClass('btn-success', false);
        $(button).toggleClass('btn-danger', true);
        $(button).text('Stop');
        beat(true);
    } else {
        // Stop the metronome
        clearTimeout(timeoutId);
        beatCount = 1;
        bpb = 4;
        $(button).toggleClass('btn-success', true);
        $(button).toggleClass('btn-danger', false);
        $(button).text('Start');
    }
}

function beatsPerBar() {
    var time_signature = $('#metro_time').text();
    if (time_signature == '3/4') {
        return 3;
    } else if (time_signature == '6/8') {
        return 6;
    }
    return 4;
}

function metroPlus() {
    var tempo = getTempo() + 1;
    if (tempo > 200) {
        tempo = 200;
    }
    $('#metro_tempo').val(tempo);
    bpb = beatsPerBar();
}

function metroMinus() {
    var tempo = getTempo() - 1 ;
    if (tempo < 1) {
        tempo = 50;
    }
    $('#metro_tempo').val(tempo);
    bpb = beatsPerBar();
}

function getTempo() {
    var tempo = $('#metro_tempo').val();
    if (tempo) {
        return parseInt(tempo);
    } else {
        return 50;
    }
}

function onKeyPress(ev) {
    //
    var key = ev.which;
    if (key == 39) {
        metroNextSong();
        ev.preventDefault();
    } else if (key == 37) {
        metroPreviousSong();
        ev.preventDefault();
    } else if (key == 32) {
        toggleMetronome();
        ev.preventDefault();
    } else if (key == 38) {
        metroPlus();
        ev.preventDefault();
    } else if (key == 40) {
        metroMinus();
        ev.preventDefault();
    }

}

/* --SONG LIST SONG */