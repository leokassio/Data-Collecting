# -*- coding: utf-8 -*- 
# ============================================================================================
# Kassio Machado - GNU Public License - 2014-9-15
# PhD candidate on Science Computing - UFMG/Brazil
# Script to capture ONLY THE LOCATED (with lat,lng coordinates) tweets using the Twitter Stream API
# the initial focus are tags Instagram, Foursquare and I'm at
# ============================================================================================

import sys
import json
import time
import datetime
import colorama
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from ConfigParser import SafeConfigParser

def loadAppOAuth(configparser):
	ckey = configparser.get('twitter_oauth', 'ckey') 
	csecret = configparser.get('twitter_oauth', 'csecret')
	yield ckey
	yield csecret

def loadUserOAuth(configparser, profile):
	atoken = configparser.get('twitter_oauth', 'atoken'+profile) 	# loading the file with section and the propertie name
	asecret = configparser.get('twitter_oauth', 'asecret'+profile)
	yield atoken
	yield asecret

def loadHashtags(configparser):
	tags = configparser.get('twitter_oauth', 'hashtags')
	return tags.split(',')

if len(sys.argv) == 1:
	print 'PLEASE INFORM THE INPUT DATA'
	exit()
else:
	configparser = SafeConfigParser()					
	configparser.read('twitter-monitor.cfg')
	ckey, csecret = loadAppOAuth(configparser)
	atoken, asecret = loadUserOAuth(configparser, sys.argv[1])
	hashtags = loadHashtags(configparser)


print 'Using Profile ' + sys.argv[1] + ' to monitor hashtags'

outputFile = open(datetime.datetime.now().strftime('%Y-%m-%d')+'-tweets-instagram.dat', 'a', 0)

class listener(StreamListener):
	def on_data(self, data):
		try:
			parsed_json = json.loads(data)
			tweet = parsed_json['text'].replace('\n', '').encode('utf-8')
			tweet = tweet.replace(',', ' ')
			tid = str(parsed_json['id']).encode('utf-8')
			uid = str(parsed_json['user']['id']).encode('utf-8')
			timestamp = parsed_json['created_at'].replace('\t', '').encode('utf-8')
                        timestamp = datetime.datetime.strptime(timestamp, '%a %b %d %H:%M:%S +0000 %Y')
                        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
			if parsed_json['coordinates'] != None:
				coords = parsed_json['coordinates']['coordinates']
			else:
				coords = [None, None]
				return True ################################################# JUST GEOLOCATED TWEETS
			if parsed_json['place'] != None:
				location = parsed_json['place']['full_name'].encode('utf-8')
				location = location.replace(',', ' ')
			else:
				location = 'None'
			if parsed_json['source'] != None:
				source = parsed_json['source'].encode('utf-8')
			else:
				source = 'None'
			msg = tid + ', ' + uid + ', ' + str(coords[0]).encode('utf-8') + ', ' + str(coords[1]).encode('utf-8') + ', ' + timestamp + ', ' + location + ', ' + tweet + ', ' + source
                        if 'insta' in source:
                                print colorama.Fore.YELLOW, msg, colorama.Fore.RESET
                        else:
                                print msg

			outputFile.write(msg+'\n')
		except KeyError:
			if 'limit' not in parsed_json.keys():
				print colorama.Fore.RED, parsed_json.keys(), colorama.Fore.RESET
			else:
				print colorama.Fore.RED, 'Tweets missed', parsed_json['limit']['track'], colorama.Fore.RESET
			# print 'error on processing JSON ' + str(e)
		finally:
			return True

	def on_error(self, status):
		print '==============================\nSTREAM ERROR\n=============================='
		print 'error ' + status
		return True

	def on_timeout(self):
		print '==============================\nSTREAM TIMEOUT\n=============================='
		return True

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener())
while True:
	try:
		twitterStream.filter(track=hashtags)
	except Exception as e:
		print 'init error', sys.exc_info()
		#print 'Error on Stream: ' + str(e)
	finally:
		time.sleep(5)
