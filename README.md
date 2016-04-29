lyrics
======

Background
----------

This code was originally written circa 1997 to create a searchable database of Neil Young's song lyrics, hosted on my private university webspace. A somewhat updated version is still running at [Human Highway](http://www.human-highway.org/lyrics/) as of 2016. The code is unlikely to be useful these days but might serve as an interesting piece of history (if you're interested in how websites were built in the 1990s, that is).

Structure
---------

* lyrics.txt is a simple plain-text database with some annotations to mark album names, song titles, etc.
* genlyrics.py is a static page generator that reads the lyrics.txt file and writes out HTML (one page per album, album and song indexes) based on the various template.html files. This was originally done in Perl, but reimplemented later in Python.
* fuzzy.cgi is a Perl CGI script that runs fuzzy full-text searches of the lyrics.txt file. No index needed, although I usually used a stripped-down version of the lyrics file to speed things up a little. It's based on a simple but surprisingly effective and fast algorithm (n-gram similarity matching).
