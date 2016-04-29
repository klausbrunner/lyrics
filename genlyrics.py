# genlyrics.py: reads a lyrics.txt file, generates html files from that
# klaus a. brunner, 2003 (based on earlier perl script)

basePath                = "C:\\temp\\lyrics\\"
lyricsFileName          = basePath + 'lyrics.txt'
albumsTemplateFileName  = basePath + 'albums-template.html'
songsTemplateFileName   = basePath + 'songs-template.html'
lyricsTemplateFileName  = basePath + 'lyrics-template.html'

imagePath               = basePath + "\\images\\ny_%02d.jpg"
imagePathWeb            = "images/ny_%02d.jpg"

import copy
import os.path

# -------------------

class Song:
    "this class holds one song"
    id = -1
    title = ''
    comment = ''
    lyrics = []

    def __str__(self):
        strep = " Song ID =" + str(self.id) + ", Title = " + self.title + ", number of lines = " + str(len(self.lyrics)) + "\n"
        return strep

    def strip(self):
        "strip empty lines from beginning and end"
        i = 0
        while (i < len(self.lyrics)) and (self.lyrics[i] == ''):
            del self.lyrics[i]
            i = i + 1

        i = len(self.lyrics) - 1
        while (i >= 0) and (self.lyrics[i] == ''):
            del self.lyrics[i]
            i = i - 1


    def __init__(self):
        self.id = -1
        self.title = ''
        self.comment = ''
        self.lyrics = []

    def __cmp__(self, other):
        "comparison based on titles"
        if isinstance(other, Song):
            return cmp(self.title, other.title)
        else:
            return cmp(self.title, other)


class Album:
    "this class holds one album"
    id = -1
    title = ''
    comment = ''
    songs = []

    def __str__(self):
        strep = "Album ID =" + str(self.id) + ", Title = " + self.title + ", number of songs = " + str(len(self.songs)) + "\n"
        for song in self.songs:
            strep = strep + str(song)
        return strep

    def __init__(self):
        self.id = -1
        self.title = ''
        self.comment = ''
        self.songs = []

    def __cmp__(self, other):
        "comparison based on titles"
        if isinstance(other, Album):
            return cmp(self.title, other.title)
        else:
            return cmp(self.songs, other)



class Albums:
    "this class is a collection of albums"
    albums = []

    def __init__(self):
        self.albums = []

    def __str__(self):
        strep = ''
        for album in self.albums:
            strep = strep + str(album)
        return strep


    def locateLyrics(self, songTitle):
        "find lyrics for a specific songName. returns [albumid, songid, albumtitle] or empty if not found"
        searchTitle = songTitle.lower().strip()
        for album in self.albums:
            for song in album.songs:
                if (len(song.lyrics) > 0) and(song.title.lower() == searchTitle):
                    return [album.id, song.id, album.title]
        return []

    def readFromFile(self, filename):
        "read lyrics data from a lyrics.txt file"
        currentSong = None
        currentAlbum = None
        file = open (lyricsFileName, 'r')
        line = file.readline().strip()
        lineNumber = 1
        while line != '':
            lineNumber = lineNumber + 1

            rline = line.strip()
            if rline.startswith("\\"):       # new album

                if (currentAlbum <> None) and (currentSong <> None):
                    currentSong.strip()
                    currentAlbum.songs.append(currentSong)
                    self.albums.append(currentAlbum)

                currentSong = None
                currentAlbum = Album()
                currentAlbum.title = rline[3:]
                currentAlbum.id = int(rline[1:3])


            elif rline.startswith("#"):     # new song

                if (currentSong <> None):
                    currentSong.strip()
                    currentAlbum.songs.append(currentSong)

                currentSong = Song()
                currentSong.title = rline[4:]
                currentSong.id = int(rline[1:4])

            elif rline.startswith("*"):     # item comment
                if currentSong <> None:
                    currentSong.comment = currentSong.comment + rline[1:]
                elif currentAlbum <> None:
                    currentAlbum.comment = currentAlbum.comment + rline[1:]
                else:
                    print "stray item comment on line " + str(lineNumber)

            elif not rline.startswith("|"): # probably lyrics
                if currentSong <> None:
                    currentSong.lyrics.append(rline)

            line = file.readline()

        file.close()

        if (currentAlbum <> None) and (currentSong <> None):
            currentSong.strip()
            currentAlbum.songs.append(currentSong)
            self.albums.append(currentAlbum)

    def __init__(self):
        albums = []


class HTMLAlbums(Albums):
    "a wrapper for the Albums class, capable of producing HTML"

    def albumsIndex(self):
        "create the albums index, return string"
        result  = '<table width="85%">'
        result += '<tr><td><h2>alphabetical order</h2></td><td><h2>chronological order</h2></td></tr><tr><td><ul>'

        sortedAlbums = copy.copy(self.albums)
        sortedAlbums.sort()
        for album in sortedAlbums:
            href = "lyrics-%02d.html" % album.id
            result += '<li><a href="' + href + '">' + album.title + "</a></li>\n"

        result += "</ul></td><td><ul>"

        albumCount = 0
        for album in self.albums:
            albumCount += 1
            href = "lyrics-%02d.html" % album.id
            result += '<li><a href="' + href + '">' + album.title + "</a></li>\n"

        result += '</ul></td></tr></table>'
        print "info: %d albums in index" % (albumCount)
        return result

    def songIndex(self):
        "create the song index"
        result = ''

        songTitleList = []
        locations = {}
        # compile a list of song titles and their lyrics locations
        songCount = 0
        for album in self.albums:
            for song in album.songs:
                songCount += 1
                if len(song.lyrics) > 0:
                    location = self.locateLyrics(song.title)
                    songTitleList.append(song.title)
                    locations[song.title] = location

                    if song.title.lower().startswith("the "):
                        songTitleList.append(song.title[4:])
                        locations[song.title[4:]] = location
                    if song.title.lower().startswith("a "):
                        songTitleList.append(song.title[2:])
                        locations[song.title[2:]] = location

        songTitleList.sort()

        print "info: %d songs with lyrics in index" % (songCount)

        # get a list of initial letters of song titles
        lastLetter = ''
        for songTitle in songTitleList:
            if songTitle[0] <> lastLetter:
                lastLetter = songTitle[0]
                result += '<a href="#' + lastLetter + '"><strong>' + lastLetter + "</strong></a> &nbsp;"

        result += '<br><br><dl>'

        lastLetter = ''
        for songTitle in songTitleList:
            if songTitle[0] <> lastLetter:
                lastLetter = songTitle[0]
                result += '<dt id="' + lastLetter + '">' + lastLetter + "</dt> "

            href = "lyrics-%02d.html#%03d" % (locations[songTitle][0], locations[songTitle][1])
            result += '<dd><a href="' + href + '">' + songTitle + "</a></dd>"

        result += "</dl>"

        return result

    def lyrics(self, album):
        "one lyrics file"
        result = ''
        albumSongs = []
        nonAlbumSongs = []
        for song in album.songs:
            if song.id < 100:
                albumSongs.append(song)
            else:
                nonAlbumSongs.append(song)

        # see if there's a picture for this album
        picPath = imagePath % album.id
        if os.path.isfile(picPath):
            result += '<img src="' + imagePathWeb % album.id + '" alt="album cover" style="float:right">'

        if albumSongs <> []:
            result += '<ol>';
            for song in albumSongs:
                result += '<li><a href="#%03d' % song.id
                result += '">' + song.title + '</a></li>'
            result += '</ol>'

        if nonAlbumSongs <> []:
            result += 'Non-Album Songs From This Period:<ol>'
            for song in nonAlbumSongs:
                result += '<li><a href="#%03d' % song.id
                result += '">' + song.title + '</a></li>'
            result += '</ol>'

        if len(album.comment) > 0:
            result += '<em>' + album.comment + '</em><br>'

        result += '<hr>'

        for song in album.songs:
            result += '<h3><a name="%03d">' % song.id
            result += song.title + '</a></h3>'
            if len(song.comment) > 0:
                result += '<em>' + song.comment + '</em><br><br>'
            if len(song.lyrics) > 0:
                for line in song.lyrics:
                    result += line + "<br>\n"
            else:
                location = self.locateLyrics(song.title)
                if location <> []:
                    href = "lyrics-%02d.html#%03d" % (location[0], location[1])
                    result += 'See <a href="' + href + '">' + location[2] + '</a>.<br>'
            result += '<br><hr>'

        return result


    def myTest(self):
        "test some known values"
        assert(self.locateLyrics("the loner") == [2,0])
        assert(self.locateLyrics("Run Around Babe") == [0,100])
        assert(self.locateLyrics("fool for your love") == [43,2])



    def createOutputFiles(self):
        "create album index, song index, and lyrics HTML files"
        assert(self.albums <> [])

        # write album index
        albumsTemplateFile = open (albumsTemplateFileName, 'r')
        albumsFile = open (basePath + 'albums.html', 'w')
        albumsText = self.albumsIndex()
        print "info: writing album index"
        line = albumsTemplateFile.readline()
        while line != '':

            albumsFile.write(line.replace('<!INSERT_TEXT>', albumsText))

            line = albumsTemplateFile.readline()

        albumsTemplateFile.close()
        albumsFile.close()

        # write song index
        songsTemplateFile = open (songsTemplateFileName, 'r')
        songsFile = open (basePath + 'songs.html', 'w')
        songsText = self.songIndex()
        print "info: writing song index"

        line = songsTemplateFile.readline()
        while line != '':
            songsFile.write(line.replace('<!INSERT_TEXT>', songsText))
            line = songsTemplateFile.readline()

        songsTemplateFile.close()
        songsFile.close()


        # write lyrics pages
        print "info: writing lyrics files (lyrics-nn.html)"
        for album in self.albums:
            lyricsTemplateFile = open (lyricsTemplateFileName, 'r')
            filename = "lyrics-%02d.html" % album.id
            lyricsFile = open (basePath + filename, 'w')
            lyricsText = self.lyrics(album)
            line = lyricsTemplateFile.readline()
            while line != '':

                newline = line.replace('<!INSERT_HEADER>', album.title)
                lyricsFile.write(newline.replace('<!INSERT_TEXT>', lyricsText))

                line = lyricsTemplateFile.readline()

            lyricsTemplateFile.close()
            lyricsFile.close()

# -------------------

alben = HTMLAlbums()
alben.readFromFile(lyricsFileName)
#alben.myTest()
alben.createOutputFiles()

print "Ok."
