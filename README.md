# Overview

Songlist is a web application for managing songlists for practice and
performance. It was originally been developed for a church worship team to 
manage songs (including chord charts and lyrics) and set lists.

# Features

* Integration with Dropbox
  Upload your chord charts, lyrics, OnSong or ChordPro files, MP3 file to a 
  folder in [Dropbox](http://dropbox.com) and they are synced into the songlist 
  site.
* Mobile-friendly
  Simple user interface that integrates well with Android and iOS devices. No
  app downloads necessary.
* Transpose Songs
  If you have OnSong or ChordPro formats of songs, these can be displayed on
  the site and transposed to any key.
* Create Songlists
  Prepare your set-list for the next performance and share the URL with the
  rest of the band.
* Metronome
  A built-in metronome that can help you keep in time as you practice, but it 
  can also be used for performance if your band plays to a click.
* Media Links
  The song library can be annotated with links to Youtube and provides a single
  location for all your media assets.
* Multi-user
  Songlist uses Google Accounts for authentication, providing secure access to
  the site.

# Deployment

Songlist is built in Python and uses a PostgreSQL database as a backend, and can
be deployed in a number of free hosting environments. The recommended 
deployment is with [Heroku](http://heroku.com).
