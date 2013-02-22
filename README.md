# edopaffy — Easy Downloader of Playlists and Favorites from YouTube


### To use edopaffy:

Install Python 2.x

* Install youtube-dl (it’s probably in your distro’s repos; if not, get it from [here](http://rg3.github.com/youtube-dl/)) and, if your distro’s package depends on it, Python 3.x

* Install the Python gdata API (it might be in your repos; otherwise, get it from [here](http://code.google.com/p/gdata-python-client/))

* Clone edopaffy:

		git clone git://gitorious.org/edopaffy/edopaffy.git
		cd edopaffy

* If you want to download all of a user’s uploads, put the usernames (e.g., “anjunabeats” in “http://www.youtube.com/user/anjunabeats”), one per line, in user-uploads.txt

* Then (assuming the Python 2.x executable is /usr/bin/python2.7, as it is in Arch and Ubuntu) do:

		./getlists.py
		./dlvideos.py
