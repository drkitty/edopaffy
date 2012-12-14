#!/usr/bin/python2.7
import os
import urllib2
import json
import subprocess

try:
	videosJson_file = open("videos.json", "r")
	videos = json.load(videosJson_file)
	
	playlistsJson_file = open("playlists.json", "r")
	playlists = json.load(playlistsJson_file)
except:
	print "Please run getPlaylists.py first."
	print "Exiting...."
	exit()
finally:
	try:
		videosJson_file.close()
		playlistsJson_file.close()
	except:
		pass


try:
	done_file = open("done.json", "r")
	done = json.load(done_file)
except:
	done = []
finally:
	try:
		done_file.close()
	except:
		pass


try:
	if not os.access("_videos", os.F_OK):
		os.makedirs("_videos")
	for thisPlaylist in playlists:
		if not os.access(thisPlaylist["name"], os.F_OK):
			os.makedirs(thisPlaylist["name"])
	
	for thisVideo in videos:
		fileName = thisVideo["title"] + " (~" + thisVideo["uploader"] + ")"
		filePath = "_videos/" + fileName
		
		#'filter(func, list)' returns the item(s) in 'list' for which func(item) is True
		#'lambda arg: foo' defines an anonymous (unnamed) function that takes 'arg' as an input and returns 'foo'
		#so this lambda returns True or False depending on whether the key "idOrUrl" maps to the value thisVideo["pageUrl"]
		#and this whole filter statement returns a list containing the item in 'playlists' that has the specified "idOrUrl"
		#'[0]' (at the end of the line) selects the first (and only) item in the list
		inPlaylist = filter(lambda pl: pl["idOrUrl"] == thisVideo["playlistIdOrUrl"], playlists)[0]
		#thus, 'inPlaylist' is a dictionary describing the playlist in which 'thisVideo' resides
		
		#note that 'thisVideo' may be in multiple playlists, in which case it will have multiple entries in 'videos', one for each playlist
		
		if done.count(thisVideo["pageUrl"]) == 0:
			print ""
			print thisVideo["pageUrl"] + ":"
			
			print "Downloading to '" + filePath + "'"
			
			
			myProcess = subprocess.Popen(['youtube-dl', '-g', thisVideo["pageUrl"]], stdout=subprocess.PIPE)
			thisVidRawUrl = myProcess.communicate()[0].rstrip("\n")
			
			try:
				f = open(filePath, "w")
				thing = urllib2.urlopen(thisVidRawUrl)
				f.write(thing.read())
			except urllib2.HTTPError as e:
				if e.code == 404:
					print "WARNING: Video has been removed from YouTube or something like that."
					print "WARNING: Skipping video...."
					#not fatal!
				elif e.code == 402:
					print "FATAL ERROR: YouTube has apparently taken issue with the amount of bandwidth you're using."
					print "FATAL ERROR: Wait a few minutes and try again."
					print "FATAL ERROR: Exiting...."
					raise
				else:
					print "FATAL ERROR: Unknown HTTP Error " + str(e.code)
					raise
			finally:
				try:
					f.close()
					del f
				except:
					pass
			
			done.append(thisVideo["pageUrl"])
		if inPlaylist["name"] == "Liked videos":
			symlinkPath = inPlaylist["name"] + "/" + fileName
		else:
			symlinkPath = inPlaylist["name"] + "/" + str(thisVideo["playlistIndex"]).zfill(3) + " " + fileName
		
		if ( os.access(filePath, os.R_OK) ) and ( not os.access(symlinkPath, os.R_OK) ): #file exists but link does not
			symlinkTarget = "../_videos/" + fileName
			print "Symlinking from '" + symlinkPath + "' to '" + symlinkTarget + "'...."
			os.symlink(symlinkTarget, symlinkPath)
except:
	print "Terminating...."
	raise
finally:
	done_file = open("done.json", "w")
	json.dump(done, done_file)
	done_file.close()
	
	#try:
		#f.close()
	#except:
		#pass
