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
	#Please use your own developer key if you significantly modify this software.
	#(My dev key is not attached to a billing account, so the most you can do is cause me some minor annoyance.
	#But please don't do that.)
	myService.client_id = "100908745387.apps.googleusercontent.com"
	#Same here.
	myService.email = raw_input("Email: ") #eventually we might cache this
	myService.password = getpass.getpass() #not this, though
	
	try:
		myService.ProgrammaticLogin()
	except:
		print "FATAL ERROR: Invalid email or password."
		exit()
	
	userEntry = myService.GetYouTubeUserEntry(username="default") #i.e., currently logged-in user (you)
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
		thisVidFeed = myService.GetYouTubePlaylistVideoFeed(uri=thisPlaylist.feed_link[0].href)
		processVidFeed(thisVidFeed, videos, p["idOrUrl"], myService)
	
	
	print "======Favorites======"
	
	thisPlaylistID = "FL" + userID
	thisVidFeed = myService.GetYouTubePlaylistVideoFeed(playlist_id=thisPlaylistID)
	p = dict()
	p["name"] = thisVidFeed.title.text
	p["idOrUrl"] = thisPlaylistID
	p["creator"] = thisVidFeed.author[0].name.text
	p["description"] = ""
	playlists.append(p)
	
	processVidFeed(thisVidFeed, videos, p["idOrUrl"], myService)
	
	
	print "======Liked videos======"
	
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
	
	
	try:
		userUploads_file = open("user-uploads.txt", "r")
	except:
		userUploads_file = [] #ugly hack to prevent the for loop from doing anything
	for thisLine in userUploads_file:
		thisLine = thisLine.rstrip("\n").rstrip(" ")
		if thisLine == "":
			print "INFO: Ignoring blank line in user-uploads.txt"
			continue
		
		thisUserName = thisLine
		try:
			thisUserID_dirty = myService.GetYouTubeUserEntry(username=thisUserName).id.text
			thisUserID = re.search('(?<=feeds/api/users/).*', thisUserID_dirty).group()
			thisPlaylistID = "UU" + thisUserID
			thisVidFeed = myService.GetYouTubePlaylistVideoFeed(playlist_id=thisPlaylistID)
			p = dict()
			p["name"] = thisUserName + "'s uploads"
			p["idOrUrl"] = thisPlaylistID
			p["creator"] = thisVidFeed.author[0].name.text
			p["description"] = ""
			playlists.append(p)
			
			print "======" + p["name"] + "======"
			processVidFeed(thisVidFeed, videos, p["idOrUrl"], myService)
			
		except:
			print "WARNING: User '" + thisUserName + "' could not be found."
			print "WARNING: Continuing with next line."
	
	userUploads_file.close()
	
	
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
			#group() returns the matched string itself
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
	print ""


if __name__ == "__main__":
	main()
