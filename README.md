# edopaffy
###### (Easy Downloader of Playlists and Favorites from YouTube)


## Dependencies

* Python **2.x**
	* Note that edopaffy assumes the Python 2.x executable is <code>/usr/bin/python2.7</code>. If it's not, make it so.
	* You could also just edit <code>getlists</code> and <code>dlvideos</code> to reflect where it's actually located, but you'll have to make sure to do that every time you pull.
* <code>youtube-dl</code>
	* Arch and Ubuntu: <code>youtube-dl</code>
	* If it's not in your distros, get it [here](http://rg3.github.com/youtube-dl/).
	* (Note that recent versions require Python **3.x**.)
* the Python gdata API
	* Arch: <code>python2-gdata</code>
	* Ubuntu: <code>python-gdata</code>
	* If it's not in your distros, get it [here](http://code.google.com/p/gdata-python-client/).
* <code>ffmpeg</code>
	* Arch and Ubuntu: <code>ffmpeg</code>
	* If it's not in your distros, get it [here](http://ffmpeg.org/download.html).

## "Installation"

	$ git clone git://github.com/drkitty/edopaffy.git
	$ cd edopaffy

(That's it!)

## Usage

The usual usage is

	$ getlists
	$ dlvideos

You can press Ctrl-C to interrupt <code>dlvideos</code> at any time. (Don't hold Ctrl-C, as that can cause problems.) To resume downloading, simply run it again. Once it exits without an error message, that means it's done!

To update <code>edopaffy</code>'s list of videos to download, re-run <code>getlists</code>. Then run <code>dlvideos</code> again to download them.

### getlists

	getlists [nopaf]

Prompt for the user's YouTube username (or associated email) and password. Then download (into <code>videos.json</code> and <code>playlists.json</code>) information about every video and (pseudo-)playlist in each of the following categories:

1. all of the user's real playlists
2. the user's Favorites
3. a pseudo-playlist containing the user's most recent 200 "Liked" videos
4. for each username in <code>user-uploads.txt</code>, a pseudo-playlist containing the most recent 1000 videos uploaded by that user

If the switch <code>nopaf</code> is given, don't prompt for a username and password and only download category 4.

To download a set of users' most recent 1000 uploads, put each such usernames (e.g., <code>anjunabeats</code> in <code>http://www.youtube.com/user/anjunabeats</code>), one per line, in <code>user-uploads.txt</code>.

(Due to technical limitations in gdata, the aforementioned 1000-uploads-per-user limit is unlikely to change. Sorry.)


#### dlvideos

	dlvideos

If done.json exists, ignore every video whose page URL appears there. For each non-ignored video that's still available on YouTube, construct a filename and check to see if a file by that name already exists. If it does, check whether it was downloaded completely (using ffmpeg). If the file doesn't exist or it's incomplete, (re)download it until the download succeeds.

(As a consequence, you can delete done.json to force dlvideos to recheck every single video for completeness, although I'm not sure why you'd want to.)

#### Exit status
The exit status code is the sum of all the following values that apply:
* 1 = YouTube returned an HTTP 402 status code (which YouTube uses to indicate excessive bandwidth usage) or the user pressed Ctrl-C.
* 2 = An unhandled exception was encountered.
* 4 = done.json could not be written.
