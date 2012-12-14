#!/usr/bin/python2.7
import gdata.youtube
import gdata.youtube.service
import re
import subprocess
import os
import urllib2
import json
import getpass


def main():
	myService = gdata.youtube.service.YouTubeService()
	myService.ssl = True
	myService.developer_key = "AI39si6xcOAkaUaIHmKKlktQkNWA3zm6VNErFNK9SLPucmwhtrYPsT-lGYhSPjslE27Z5jSqsxEyWGLi4sRyiy8A2tyfS0xN5w"
	myService.client_id = "100908745387.apps.googleusercontent.com"
	myService.email = raw_input("Email: ")
	myService.password = getpass.getpass()
	myService.ProgrammaticLogin()
	
	userEntry = myService.GetYouTubeUserEntry(username="default")
	userID = re.search(r'(?<=users/).*', userEntry.id.text).group()
	
	videos = []
	playlists = []
	
	playlistFeed = myService.GetYouTubePlaylistFeed(username="default")
	for thisPlaylist in playlistFeed.entry:
		p = dict()
		p["name"] = thisPlaylist.title.text
		p["idOrUrl"] = thisPlaylist.id.text
		p["creator"] = thisPlaylist.author[0].name.text
		thisPlaylistDescription = thisPlaylist.description.text
		if thisPlaylistDescription == None:
			p["description"] = ""
		else:
			p["description"] = thisPlaylistDescription
		playlists.append(p)
		
		print "======" + p["name"] + "======"
		#thisPlaylistURL = thisPlaylist.id.text
		thisVidFeed = myService.GetYouTubePlaylistVideoFeed(uri=thisPlaylist.feed_link[0].href)
		processVidFeed(thisVidFeed, videos, p["idOrUrl"], myService)
	
	thisPlaylistID = "FL" + userID
	thisVidFeed = myService.GetYouTubePlaylistVideoFeed(playlist_id=thisPlaylistID)
	p = dict()
	p["name"] = thisVidFeed.title.text
	p["idOrUrl"] = thisPlaylistID
	p["creator"] = thisVidFeed.author[0].name.text
	p["description"] = ""
	playlists.append(p)
	
	processVidFeed(thisVidFeed, videos, p["idOrUrl"], myService)
	
	
	thisPlaylistID = "LL" + userID
	thisVidFeed = myService.GetYouTubePlaylistVideoFeed(playlist_id=thisPlaylistID)
	thisPlaylistTitle = thisVidFeed.title.text
	p = dict()
	p["name"] = thisVidFeed.title.text
	p["idOrUrl"] = thisPlaylistID
	p["creator"] = thisVidFeed.author[0].name.text
	p["description"] = ""
	playlists.append(p)
	
	processVidFeed(thisVidFeed, videos, p["idOrUrl"], myService)
	
	
	
	videosJson_file = open("videos.json", "w")
	json.dump(videos, videosJson_file, separators=(',', ':'), indent=1)
	videosJson_file.close()
	
	playlistsJson_file = open("playlists.json", "w")
	json.dump(playlists, playlistsJson_file, separators=(',', ':'), indent=1)
	playlistsJson_file.close()


def processVidFeed(aVidFeed, aVideoList, playlistIdOrUrl, aService):
	while True:
		for thisVid in aVidFeed.entry:
			v = dict()
			v["playlistIdOrUrl"] = playlistIdOrUrl
			
			for thisLink in thisVid.link:
				thisVidPageURL_dirty = thisLink.href
				if re.search(r'^https://www.youtube.com/watch', thisVidPageURL_dirty) != None:
					break
			v["pageUrl"] = re.search(r'[^&]*', thisVidPageURL_dirty).group()
			v["title"] = thisVid.media.title.text
			v["uploader"] = thisVid.author[0].name.text
			v["playlistIndex"] = thisVid.position.text
			if thisVid.description == None:
				v["description"] = ""
			else:
				v["description"] = thisVid.description.text
			aVideoList.append(v)
		print v["playlistIndex"]
		thisNextLink = aVidFeed.GetNextLink()
		if thisNextLink == None:
			break
		aVidFeed = aService.GetYouTubePlaylistVideoFeed(uri=thisNextLink.href)


if __name__ == "__main__":
	main()
