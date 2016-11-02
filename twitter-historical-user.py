# -*- coding: utf-8 -*-
# ============================================================================================
# Kassio Machado - GNU Public License - 2016-04-23
# PhD candidate on Science Computing - UFMG/Brazil & uOttawa/Canada
# Python script to collect all geolocated data from specific list of
# users on Twitter. Its a kind of active data collection ¯\_(ツ)_/¯ hehe
# credits to Fabio Rocha de Araujo who started the code.
# ============================================================================================ 

import sys
reload(sys) 
sys.setdefaultencoding('utf8')
import tweepy 
import csv
import time
import colorama
import setproctitle
from tqdm import tqdm
from Queue import Queue
from threading import Thread
from datetime import datetime, timedelta

def loadDefinedUsers(outputDir, outputFile):
	setDefinedUsers = set()
	try:
		outputDefinedUsers = open(outputDir + outputFile + '-collected-users.csv', 'r')
		for line in outputDefinedUsers:
			line = line.replace('\n','')
			try:
				setDefinedUsers.add(line.split(',')[0])
			except:
				continue
		print len(setDefinedUsers), 'users already collected!'
	except IOError:
		print colorama.Fore.RED + '¯\_(ツ)_/¯ No users previously defined!' + colorama.Fore.RESET
	return setDefinedUsers

def twitterCrawlerRun(idCrawler, usersBuffer, usersSaveBuffer):
	idCrawlerStr = str(idCrawler)
	threadMsg = 'Thread Crawler #' + idCrawlerStr
	print 'Starting', threadMsg
	logfile = open('logs/thread-crawler' + idCrawlerStr + '.log', 'a', 0)
	apiTwitter = twitterAuth(idCrawler)
	while True:
		try:
			userid = usersBuffer.get()
			if userid == 'kill':
				usersBuffer.task_done()
				break
			r = getUserTimeline(apiTwitter, userid, usersSaveBuffer, idCrawler, logfile)
			usersBuffer.task_done()
			msg = colorama.Fore.YELLOW + r['screen_name'] + ': ' + r['total_tweets'] + ' tweets w/ '
			msg += r['valid_tweets'] + ' geocoords (' + r['calls'] + ' calls)' + colorama.Fore.RESET
			print msg
			# time.sleep(3)
		except Exception, e:
			logfile.write('Thread #' + idCrawlerStr + ': ' + str(e) + ' - ' + datetime.now().strftime('%m-%d %H:%M:%S') + '\n')
			time.sleep(1)
	logfile.write('Thread #' + idCrawlerStr + ': finishing on ' + userid + ' ' + datetime.now().strftime('%m-%d %H:%M:%S') + '\n')
	logfile.close()
	print 'Finishing', '#' + str(idCrawler), 'thread crawler'

def getUserTimeline(apiTwitter, userid, usersSaveBuffer, idCrawler, logfile):
	noCoords = 0
	total = 0
	idMax = None
	calls = 0
	timeout = 0
	attempt = 0
	timeline = list()
	setTimeline = set() # used to define the most recent tweet visited
	while True:
		calls += 1
		try:
			logfile.write(datetime.now().strftime('%m-%d %H:%M:%S') + ' loading timeline ' + userid + ' call ' + str(calls) + '\n')
			if idMax == None:
				timeline = apiTwitter.user_timeline(user_id=userid, count=200)
			else:
				timeline = apiTwitter.user_timeline(user_id=userid, count=200, max_id=idMax)
				timeline = timeline[1:]
			logfile.write(datetime.now().strftime('%m-%d %H:%M:%S') + ' loaded ' + str(len(timeline)) + ' tweets\n')
		except tweepy.error.TweepError as e:
			exceptMsg = str(e)
			logfile.write(datetime.now().strftime('%m-%d %H:%M:%S') + ' error on load ' + exceptMsg + ' attempt ' + str(attempt) + '\n')
			if 'Not authorized.' in exceptMsg:
				usersSaveBuffer.put([userid, 'not-authorized'])	# user changed its privacy settings (not public anymore)
				break
			elif attempt >= 3 or timeout >= 3:
				usersSaveBuffer.put([userid, '3-attempts']) 	# maybe can be tried again later
				break
			elif 'Read timed out' in exceptMsg:
				timeout += 1
				time.sleep(60)
				continue
			elif 'Failed to parse JSON payload' in exceptMsg:
				attempt += 1
				time.sleep(1)
				continue
			try:
				if e.message[0]['code'] == 88:
					ratelimit = apiTwitter.rate_limit_status()
					ratelimitStatuses = ratelimit['resources']['statuses']['/statuses/user_timeline']
					remainingCalls = ratelimitStatuses['remaining']
					resetTime = datetime.fromtimestamp(ratelimitStatuses['reset'])
					resetTimeDelta = resetTime - datetime.now()
					sleeptime = int(resetTimeDelta.total_seconds()) + 2
					print 'Thread Crawler #' + str(idCrawler) +'\tsleeping until', resetTime.strftime('%H:%M:%S'), 'Calls:', calls, 'Remaining:', remainingCalls
					logfile.write(datetime.now().strftime('%m-%d %H:%M:%S') + ' sleeping ' + str(sleeptime) + ' secs\n')
					time.sleep(sleeptime)
					continue
				elif e.message[0]['code'] == 34:
					usersSaveBuffer.put([userid, 'error404']) # user does not exist anymore
					break
				elif e.message[0]['code'] == 89:
					print colorama.Fore.RED + 'Thread #' + str(idCrawler) + ' TweepError 89: Invalid or expired token!'
					exit()
			except TypeError:
				msg = colorama.Fore.RED + 'Thread #' + str(idCrawler) + ' TweepError: ' + userid + ' \n'
				msg += str(e)
				msg += '\n------------------------------------------------------------------------' + colorama.Fore.RESET
				print msg
				attempt += 1
				time.sleep(15)
				continue
		except Exception, e:
			msg = colorama.Fore.RED + 'Thread #' + str(idCrawler) + ' Generic Exception\n'
			msg += str(e)
			msg += '\n------------------------------------------------------------------------' + colorama.Fore.RESET
			print msg
			time.sleep(1)
			logfile.write('Thread #' + str(idCrawler) + ': ' + str(e) + ' - ' + datetime.now().strftime('%m-%d %H:%M:%S') + '\n')
			break

		if len(timeline) == 0:
			break

		total += len(timeline)
		for status in timeline:
			idMax = status.id_str
			if status.coordinates != None:
				id_data = status.id_str
				userid_status = status.author.id_str
				screenName = status.author.screen_name
				lang = status.lang
				tweetText = status.text.replace('\n', '')
				app = status.source.lower()
				appURL = status.source_url.lower()
				timestamp = status.	
				weekday = timestamp.weekday()
				activeCollection = True
				lng, lat = status.coordinates['coordinates']
				hashtags = status.entities['hashtags']
				urls = status.entities['urls']	
				for ui in range(len(urls)):
					try:
						del urls[ui]['indices']
					except KeyError:
						continue
				hashtags = [hashtags[hi]['text'] for hi in range(len(hashtags))]
				try:
					country = status.place.country
					country_code = status.place.country_code
					place_name = status.place.full_name
					place_url = status.place.url
					place_type = status.place.place_type
				except AttributeError:
					country = None
					country_code = None
					place_name = None
					place_url = None
					place_type = None

				document = dict(id_data=id_data, date_orinal=timestamp, date_local=timestamp, lat=lat, lng=lng,
					userid=userid_status, dataset_curator=2, text=tweetText, app=app, app_url=appURL, lang=lang,
					hashtags=hashtags, urls=urls, weekday=weekday, screen_name=screenName, active_collect=True,
					country=country_code, place_name=place_name, place_url=place_url, place_type=place_type)
				setTimeline.add((timestamp,id_data))
				usersSaveBuffer.put(document)
			else:
				noCoords += 1
		# time.sleep(2)
	
	try:
		screenName = colorama.Fore.GREEN + '@' + screenName + colorama.Fore.RESET
	except:
		screenName = userid
	docReturn = dict(screen_name=screenName, total_tweets=str(total), valid_tweets=str(total - noCoords), calls=str(calls))
	dt = sorted(setTimeline)[0]
	usersSaveBuffer.put([userid, 'ok@' + dt[0].strftime('%y-%m-%d %H:%M:%S') + '@' + dt[1]]) # user completely visited
	return docReturn

def twitterCrawlerSaveRun(usersSaveBuffer, outputDir, outputFile):
	print colorama.Fore.RED + 'Starting save thread' + colorama.Fore.RESET
	setDefinedUsers = set()
	
	logfile = open('logs/thread-save.log', 'a', 0)
	outputGeneral = open(outputDir + outputFile + '-general.csv', 'a')
	outputInstagram = open(outputDir + outputFile + '-instagram.csv', 'a')
	outputFoursquare = open(outputDir + outputFile + '-foursquare.csv', 'a')
	outputDefinedUsers = open(outputDir + outputFile + '-collected-users.csv', 'a', 0)
	
	while True:
		document = usersSaveBuffer.get()
		try:
			if document['app'] == 'instagram':
				outputInstagram.write(str(document) + '\n')
			elif document['app'] == 'foursquare':
				outputFoursquare.write(str(document) + '\n')
			else:
				outputGeneral.write(str(document) + '\n')
		except TypeError:
			if type(document) == list:
				userid, code = document
				outputDefinedUsers.write(userid + ',' + code + '\n')
				logfile.write('Thread Save: saving on ' + str(userid) + ' ' + datetime.now().strftime('%m-%d %H:%M:%S') + '\n')
			elif document == 'kill':
				usersSaveBuffer.task_done()
				logfile.write('Thread Save: finishing on ' + datetime.now().strftime('%m-%d %H:%M:%S') + '\n')
				break
			else:
				logfile.write('Thread save: review queue -> ' + str(document) + '\n')
		usersSaveBuffer.task_done()

	outputGeneral.close()
	outputInstagram.close()
	outputFoursquare.close()
	outputDefinedUsers.close()

	logfile.close()
	print colorama.Fore.RED + 'Finishing save thread' + colorama.Fore.RESET

def main():
	outputDir = 'outputfiles/'
	inputFile = sys.argv[1]
	outputFile = inputFile.replace('.csv', '')
	
	threadBufferSize = 43
	setDefinedUsers = loadDefinedUsers(outputDir, outputFile)

	inputUsers = open(inputFile,'r')

	usersSaveBuffer = Queue()
	usersBuffer = Queue(maxsize=250) 	
	saveThread = Thread(target=twitterCrawlerSaveRun, args=[usersSaveBuffer, outputDir, outputFile])
	saveThread.daemon = True
	saveThread.start()
	for i in range(threadBufferSize):
		t = Thread(target=twitterCrawlerRun, args=[i, usersBuffer, usersSaveBuffer])
		t.daemon = True
		t.start()

	nLines = sum(1 for line in inputUsers)
	inputUsers.seek(0)

	for line in tqdm(inputUsers, total=nLines, desc='Loading users dataset'):
		userid, checkins = line.split(',')
		if userid in setDefinedUsers:
			# print 'skipping', userid
			continue
		usersBuffer.put(userid)

	for i in range(threadBufferSize):
		usersBuffer.put('kill')
	usersBuffer.join()		
	
	usersSaveBuffer.put('kill')
	usersSaveBuffer.join()		

def test():
	# ratelimit = rate_limit_status()
	# ratelimit['resources']['statuses']['/statuses/user_timeline'] -> {u'limit': 180, u'remaining': 179, u'reset': 1461510226}
	userids = ['950796265', '367818064', '1733886168', '189315450', '2473667478', '1274129971']
	fileout = open('temp.txt', 'a')
	
	apiTwitter = twitterAuth(0)
	for userid in userids:		
		idMax = None
		while True:
			ratelimit = apiTwitter.rate_limit_status()
			ratelimit = ratelimit['resources']['statuses']['/statuses/user_timeline']
			remainingCalls = ratelimit['remaining']
			resetTime = datetime.fromtimestamp(ratelimit['reset']) - datetime.now()
			print 'Calls Reamining:', remainingCalls, 'Next Reset (minutes):', resetTime.total_seconds()/60, 'and in secs', int(resetTime.total_seconds())

			if remainingCalls == 0:
				sleeptime = int(resetTime.total_seconds()) + 2
				print 'Waiting', sleeptime, 'secs...'
				time.sleep(sleeptime)
			
			try:
				if idMax == None:
					timeline = apiTwitter.user_timeline(user_id=userid, count=200)
				else:
					timeline = apiTwitter.user_timeline(user_id=userid, count=200, max_id=idMax)
					timeline = timeline[1:]
			except tweepy.error.TweepError as e:
				print '--- ERROR ---'
				print e

			if len(timeline) == 0:
				time.sleep(1)
				break

			noCoords = 0
			for status in timeline:
				idMax = status.id_str
				if str(status.author.id) != userid:
					print 'Different author!', userid, status.author.id, 
				if status.coordinates != None:
					lat, lng = status.coordinates['coordinates']
					tweetText = status.text.replace('\n', '')
					id_data = status.id_str
					userid_status = str(status.author.id)
					screenName = status.author.screen_name
					app = status.source.lower()
					appURL = status.source_url
					timestamp = status.created_at
					weekday = timestamp.weekday()
					hashtags = [ht['text'] for ht in status.entities['hashtags']]
					urls = status.entities['urls']
					activeCollection = True
					for ui in range(len(urls)):
						try:
							del urls[ui]['indices']
						except KeyError:
							continue # print 'error', urls[ui]
					document = dict(id_data=id_data, date_orinal=timestamp, date_local=timestamp, lat=lat, lng=lng,
						userid=userid_status, dataset_curator=2, text=tweetText, app=app, app_url=appURL, 
						hashtags=hashtags, urls=urls, weekday=weekday, screen_name=screenName, active_collect=True)
					msg = str(id_data) + ',' + str(userid_status) + ',' + timestamp.strftime('%y-%m-%d %H:%M')
					fileout.write(msg + '\n')
				else:
					noCoords += 1
			print userid, 'fetch', len(timeline), 'tweets with', len(timeline) - noCoords, 'valids'
			# time.sleep(1)

	exit()

	# for i in new_tweets:
	# 	if i.source == 'Instagram':
	# 		urls = i.entities['urls']
	# 		if len(urls) > 0:
	# 			for u in urls:
	# 				try:
	# 					del u['indices']
	# 				except KeyError:
	# 					continue
	# 			print urls

if __name__ == "__main__":
	# test()
	main()




