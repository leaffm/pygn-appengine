pygn-appengine
==============

pygn-appengine (pronounced "pigeon appengine") is a simple [Google AppEngine](code.google.com/appengine/) app that lets you interact with the [Gracenote Music API](https://developer.gracenote.com/sites/prod-gracenote/files/web/html/index.html) using JSON requests.

pygn-appengine makes use of [pygn](https://github.com/cweichen/pygn), a simple Python client for the Gracenote Music API.

Gracenote technology and metadata helps hundreds of millions of music fans identify, discover and connect with the songs and artists they love every day, but their APIs are all XML based, making it difficult to create modern web apps using JavaScript.

pygn-appengine allows you to look up artists, albums, and tracks in the Gracenote database, and returns a number of metadata fields, including:

- basic metadata like Artist Name, Album Title, Track Title
- descriptors like Genre, Origin, Mood, Tempo
- related content like Album Art, Artist Image, Biographies

You will need a Gracenote Client ID to run this app. Please visit https://developer.gracenote.com to get yours.
