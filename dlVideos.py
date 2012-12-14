#!/usr/bin/python2.7
import os
import urllib2
import json
import subprocess

try:
	videosJson_file = open("videos.json", "r")
	videos = json.load(videosJson_file)
	videosJson_file.close()
	
	playlistsJson_file = open("playlists.json", "r")
	playlists = json.load(playlistsJson_file)
	playlistsJson_file.close()
except:
	print "Please download the playlists first."
	print "Exiting...."
	exit()


try:
	done_file = open("done.json", "r")
	done = json.load(done_file)
	done_file.close()
except:
	done = []






try:
	for thisPlaylist in playlists:
		if not os.access(thisPlaylist["name"], os.F_OK):
			os.makedirs(thisPlaylist["name"])
	
	for thisVideo in videos:
		if done.count(thisVideo["pageUrl"]) == 0:
			print ""
			print thisVideo["pageUrl"] + ":"
			
			#'filter(func, list)' returns item(s) in list for which func(item) is true
			#'lambda arg: foo' defines an anonymous (unnamed) function that takes 'arg' as an input and returns 'foo'
			#so this lambda returns True or False depending on whether the key "idOrUrl" maps to the value thisVideo["pageUrl"]
			#and this whole filter statement returns a list containing the item in 'playlists' that has the specified "idOrUrl"
			inPlaylist = filter( lambda pl: pl["idOrUrl"] == thisVideo["playlistIdOrUrl"], playlists )[0]
			#'inPlaylist' is the playlist thisVideo is in
			
			#print inPlaylist
			#print thisVideo
			#exit()
			
			fileName = inPlaylist["name"] + "/" + thisVideo["title"]
			print "Downloading to '" + fileName + "'"
			
			
			myProcess = subprocess.Popen(['youtube-dl', '-g', thisVideo["pageUrl"]], stdout=subprocess.PIPE)
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
			
			done.append(thisVideo["pageUrl"])
		#<<<<  MAKE LINK TO VIDEO  >>>>
finally:
	#try:
	done_file = open("done.json", "w")
	json.dump(done, done_file)
	#except:
		#print "Couldn't write 'dl.json'."
		#print "Looks like you're SOL."
	#finally:
		#if done_file != None:
			#done_file.close()
