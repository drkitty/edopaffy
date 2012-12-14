#!/usr/bin/python2.7
import os
import urllib2
import json
import subprocess

try:
	videosJson_file = open("videos.json", "r")
	videosList = json.load(videosJson_file)
	videosJson_file.close()
	
	playlistsJson_file = open("playlists.json", "r")
	playlistsList = json.load(playlistsJson_file)
	playlistsJson_file.close()
except:
	print "Please download the playlists first."
	print "Exiting...."
	exit()


try:
	myDlFile = open("dl.json", "r")
	dlList = json.load(myDlFile)
	myDlFile.close()
except:
	dlList = []






try:
	for thisPlaylist in playlistsList:
		if not os.access(thisPlaylist["name"], os.F_OK):
			os.makedirs(thisPlaylist["name"])
	
	for thisVideo in videosList:
		if dlList.count(thisVideo["pageUrl"]) == 0:
			print ""
			print thisVideo["pageUrl"] + ":"
			
			myProcess = subprocess.Popen(['youtube-dl', '-g', vidPageURL], stdout=subprocess.PIPE)
			vidRawURL = myProcess.communicate()[0].rstrip("\n")
			print vidRawURL
			#f = open(fileName, "w")
			#thing = urllib2.urlopen(thisVidRawURL)
			#try:
				#f.write(thing.read())
			#except:
				#print "fak u dolan."
			#finally:
				#f.close()
			
			dlList.append(vidPageUrl)
finally:
	try:
		myDlFile = open("dl.json", "w")
		json.dump(dlList, myDlFile)
		myDlFile.close()
	except:
		print "Couldn't write 'dl.json'."
		print "Looks like you're SOL."
