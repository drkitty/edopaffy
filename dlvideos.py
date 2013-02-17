#!/usr/bin/python2.7
# coding=utf-8
import os
import urllib2
import json
import subprocess
import re

def main():
	try:
		videos_file = open("videos.json", "r")
		videos = json.load(videos_file)
		
		playlists_file = open("playlists.json", "r")
		playlists = json.load(playlists_file)
	except:
		print "Please run getlists.py first."
		print "Exiting...."
		exit()
	finally:
		try:
			videos_file.close()
			playlists_file.close()
		except:
			pass #Fail silently. It's no big deal if we can't close them. I hope.


	try:
		done_file = open("done.json", "r")
		done = json.load(done_file)
	except:
		done = []
	finally:
		try:
			done_file.close()
		except:
			pass #Same here.


	try:
		if not os.access("_videos", os.F_OK):
			os.makedirs("_videos")
		if not os.access("_incomplete", os.F_OK):
			os.makedirs("_incomplete")
		for thisPlaylist in playlists:
			if not os.access(thisPlaylist["name"], os.F_OK):
				os.makedirs(thisPlaylist["name"])
		
		for thisVideo in videos:
			fileName = thisVideo["title"] + " (~" + thisVideo["uploader"] + ")"
			fileName = fileName.replace("/", "%")
			filePath = "_videos/" + fileName
			
			#'filter(func, list)' returns the item(s) in 'list' for which func(item) is True
			#'lambda arg: foo' defines an anonymous (unnamed) function that takes 'arg' as an input and returns 'foo'
			#so this lambda returns True or False depending on whether the key "idOrUrl" maps to the value thisVideo["pageUrl"]
			#and this whole filter statement returns a list containing the item in 'playlists' that has the specified "idOrUrl"
			#'[0]' (at the end of the line) selects the first (and only) item in the list
			inPlaylist = filter(lambda pl: pl["idOrUrl"] == thisVideo["playlistIdOrUrl"], playlists)[0]
			#thus, 'inPlaylist' is a dictionary describing the playlist in which 'thisVideo' resides
			
			#note that 'thisVideo' may be in multiple playlists, in which case it will have multiple entries in 'videos', one for each playlist
			
			if done.count(thisVideo["pageUrl"]) == 0 and os.access(filePath, os.R_OK) and os.path.getsize(filePath) > 0:
				print ""
				print filePath
				if videoIsComplete(filePath):
					print thisVideo["pageUrl"] + " has already been downloaded."
					done.append(thisVideo["pageUrl"])
				else:
					print "WARNING: " + thisVideo["pageUrl"] + " did not download completely."
					#FIXME: should this be a warning or an error?
					print "WARNING: Backing up incomplete video...."
					os.rename(filePath, "_incomplete/" + fileName)
					#RATIONALE: It might have been a long time since the video was downloaded,
					#           so we back it up in case it was removed from YouTube in the
					#           intervening time.
					print "WARNING: Video will now be re-downloaded."
			
			if done.count(thisVideo["pageUrl"]) == 0: #thisVideo["pageUrl"] does not appear in 'done.json'
				print ""
				print thisVideo["pageUrl"] + ":"
				if thisVideo["title"] == "":
					print "WARNING: Video has blank title."
					#I'm not sure why we're supporting videos with blank titles. It just seems like the right thing to do.
				
				print "Retrieving raw video URL...."
				youtube_dlProcess = subprocess.Popen(['youtube-dl', '-g', thisVideo["pageUrl"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				youtube_dlProcessOutput = youtube_dlProcess.communicate()
				# 'communicate()' returns (stdout, stderr)
				if youtube_dlProcessOutput[0] == "": #if no output on stdout (i.e., something went wrong)
					if re.search('HTTP Error 402', youtube_dlProcessOutput[1]) != None: #if regex matches
						print ""
						print "FATAL ERROR: YouTube thinks you've used too much bandwidth."
						print "FATAL ERROR: Wait a few minutes and try again."
						raise KeyboardInterrupt
						#Really we should define a custom exception for terminating in a safe manner, but
						#I don't really want to do that right now.
					elif re.search('urlopen error', youtube_dlProcessOutput[1]) != None:
						print ""
						print "FATAL ERROR: Cannot connect to YouTube"
						print "FATAL ERROR: You probably don't have an Internet connection"
						raise KeyboardInterrupt
						#Same as above.
					else:
						print "WARNING: Video was removed from YouTube."
						print "WARNING: youtube-dl returned the following on stderr:"
						print "\t" + youtube_dlProcessOutput[1].rstrip("\n")
						print "WARNING: Skipping video...."
						done.append(thisVideo["pageUrl"])
						#"done" means don't retry later---removed videos don't usually come back.
						#If you want to recheck all videos, delete done.json
						continue #jump to next iteration
				else:
					thisVidRawUrl = youtube_dlProcessOutput[0].rstrip("\n")
					
					tryAgain = True
					while tryAgain:
						try:
							print "Downloading to '" + filePath + "'...."
							f = open(filePath, "w")
							payload = urllib2.urlopen(thisVidRawUrl)
							f.write(payload.read())
							if videoIsComplete(filePath):
								done.append(thisVideo["pageUrl"])
								print "Done."
								tryAgain = False
							else:
								print "WARNING: Video did not download completely."
								#FIXME: should this be a warning or an error?

								#print "Backing up incomplete video...."
								#os.rename(filePath, "_incomplete/" + fileName)
								#RATIONALE: We just downloaded the video, so it's very unlikely
								#           that it has just now been removed from YouTube;
								#           thus there's no need to back it up.

								print "WARNING: It will now be re-downloaded."
								#tryAgain remains True
						except urllib2.HTTPError as e:
							if e.code == 404:
								print "WARNING: Video was removed from YouTube."
								print "WARNING: Skipping video...."
								done.append(thisVideo["pageUrl"])
								tryAgain = False
								#not fatal!
							elif e.code == 402:
								print "FATAL ERROR: YouTube thinks you've used too much bandwidth."
								print "FATAL ERROR: Wait a few minutes and try again."
								print "FATAL ERROR: Exiting...."
								exit()
							else:
								print "FATAL ERROR: Unknown HTTP Error " + str(e.code)
								exit()
						finally:
							try:
								f.close()
							except:
								pass #silently fail
							finally:
								del f
			
			if thisVideo["playlistIndex"] == "":
				symlinkPath = inPlaylist["name"] + "/" + fileName
			else:
				symlinkPath = inPlaylist["name"] + "/" + str(thisVideo["playlistIndex"]).zfill(3) + " " + fileName
			
			if ( os.access(filePath, os.R_OK) ) and ( not os.access(symlinkPath, os.R_OK) ): #file exists but link does not
				print ""
				symlinkTarget = "../_videos/" + fileName
				print "Symlinking from '" + symlinkPath + "' to '" + symlinkTarget + "'."
				os.symlink(symlinkTarget, symlinkPath)
	except KeyboardInterrupt:
		#In every terminal I've used, ctrl-Cing inserts the text "^C", but no newline.
		#That's why we need two newlines here.
		print ""
		print ""
		print "Terminating...."
	except:
		print ""
		print "FATAL ERROR: Unhandled exception"
		print ""
		raise
	finally:
		try:
			done_file = open("done.json", "w")
			json.dump(done, done_file, separators=(',', ':'), indent=0)
			#`indent=0` inserts newlines but doesn't actually indent.
			done_file.close()
		except:
			print ""
			print "WARNING: Could not write to done.json"
			print "WARNING: Videos you manually removed from _videos might be redownloaded the"
			print "WARNING: next time dlvideos.py runs"
			print ""


def videoIsComplete(filePath):
	ffmpegArgList = ['ffmpeg', '-v', 'debug', '-i', filePath, '-codec', 'copy', '-f', 'rawvideo', '-y', '/dev/null']
	ffmpegProcess = subprocess.Popen(ffmpegArgList, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	#global ffmpegOutput
	ffmpegOutput = ffmpegProcess.communicate()
	linesWithTruncating = re.findall(r'^Truncating.*', ffmpegOutput[1], re.MULTILINE)
	#exit()
	if len(linesWithTruncating) == 0:
		#print "ffmpeg didn't Truncate! Hooray!"
		return True
	else:
		for thisLine in linesWithTruncating:
			print "\t" + thisLine
		return False
	return True

if __name__ == "__main__":
	main()
