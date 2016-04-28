# -*- coding: utf-8 -*- 
# ============================================================================================
# Kassio Machado - GNU Public License - 2014-9-15
# PhD candidate on Science Computing - UFMG/Brazil
# Script to capture ONLY THE LOCATED (with lat,lng coordinates) tweets using the Twitter Stream API
# the initial focus are tags Instagram, Foursquare and I'm at
# ============================================================================================

import sys
reload(sys) 
sys.setdefaultencoding('utf8')
import json
import time
import datetime
import colorama
import numpy
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

def loadHashtags(configparser, configName):
	tags = configparser.get(configName, 'hashtags')
	return tags.split(',')

def loadGeolocatedMethod(configparser, configName):
	gfm = configparser.getint(configName, 'geolocated_filter_method')
	return gfm

def loadFilenameAlias(configparser, configName):
	fa = configparser.get(configName, 'filename_alias')
	return fa	

class listener(StreamListener):
	def on_data(self, data):
		try:
			geolocated_filter_method = 1
			parsed_json = json.loads(data)			
			if parsed_json['coordinates'] != None:
				coords = parsed_json['coordinates']['coordinates']
			elif geolocated_filter_method == 1: # flag for only precise geolocation method
				return True
			else:
				coords = [None, None]
			if parsed_json['place'] != None:
				place_name = parsed_json['place']['full_name'].encode('utf-8')
				country = parsed_json['place']['country'].encode('utf-8')
				countryCode = parsed_json['place']['country_code'].encode('utf-8')
				placeType = parsed_json['place']['place_type'].encode('utf-8')
				placeURL = parsed_json['place']['url'].encode('utf-8')
			elif geolocated_filter_method > 0:
					return True
			else:
				place_name = 'None'
				country = 'None'
				countryCode = 'None'
				placeType = 'None'
				placeURL = 'None'
			tweet = parsed_json['text'].replace('\n', '')
			tid = str(parsed_json['id']).encode('utf-8')
			uid = str(parsed_json['user']['id']).encode('utf-8')
			lang = parsed_json['lang']
			timestamp = parsed_json['created_at'].replace('\t', '').encode('utf-8')
			timestamp = datetime.datetime.strptime(timestamp, '%a %b %d %H:%M:%S +0000 %Y')
			weekday = timestamp.weekday()
			timestamp_text = timestamp.strftime('%Y-%m-%d %H:%M:%S')
			lat = str(coords[0]).encode('utf-8')
			lng = str(coords[1]).encode('utf-8')
			screen_name = str(parsed_json['user']['screen_name']).encode('utf-8')
			urls = parsed_json['entities']['urls']			
			url = urls[-1]['url']
			hashtags_tweet = parsed_json['entities']['hashtags']
			msg = lat + ', ' + lng + ', ' + timestamp_text 
			msg += ', ' + url + ', ' + place_name + ', ' + country + ', ' + tweet
			if parsed_json['source'] != None:
				app = parsed_json['source'].encode('utf-8').lower()
				app_url = app
				if 'instagram' in app:
					print colorama.Fore.YELLOW, msg, colorama.Fore.RESET
				elif 'foursquare' in app:
					print colorama.Fore.CYAN, msg, colorama.Fore.RESET
				else:
					print msg
			else:
				app = 'None'
			reg = dict(id_data=tid, userid=uid, lang=lang, date_local=timestamp, date_original=timestamp, 
				app=app, app_url=app_url, text=tweet, lat=lat, lng=lng, place_name=place_name, weekday=weekday,
				country=countryCode, place_type=placeType, place_url=placeURL, passive_collect=True,
				screen_name=screen_name, dataset_curator=2, url=url, urls=urls, hashtags=hashtags_tweet)
			outputFile.write(str(reg) + '\n')
		except KeyError, ke:
			if 'limit' not in parsed_json.keys():
				print colorama.Fore.RED, parsed_json.keys(), colorama.Fore.RESET
			else:
				print colorama.Fore.RED, 'Tweets missed', parsed_json['limit']['track'], colorama.Fore.RESET
			# print 'error on processing JSON ' + str(e)
		except Exception, e:
			parsed_json = json.loads(data)
			print e, parsed_json['text']
		finally:
			return True

	def on_error(self, status):
		print '==============================\nSTREAM ERROR\n=============================='
		print 'error ' + status
		return True

	def on_timeout(self):
		print '==============================\nSTREAM TIMEOUT\n=============================='
		return True

def plotBanner():
	colors = [colorama.Fore.RED, colorama.Fore.YELLOW, colorama.Fore.CYAN, colorama.Fore.GREEN, 
	colorama.Fore.WHITE, colorama.Fore.MAGENTA]
	i = numpy.random.randint(0,len(colors))
	print colors[i]
	# source: http://fsymbols.com/generators/tarty/
	print '▒█▀▀█ █░░█ ▀▀█▀▀ █░░█ █▀▀█ █▀▀▄ 		'
	print '▒█▄▄█ █▄▄█ ░░█░░ █▀▀█ █░░█ █░░█ 		'
	print '▒█░░░ ▄▄▄█ ░░▀░░ ▀░░▀ ▀▀▀▀ ▀░░▀ 		'
	print ''
	print '▀▀█▀▀ █░░░█ ░▀░ ▀▀█▀▀ ▀▀█▀▀ █▀▀ █▀▀█	' 
	print '░▒█░░ █▄█▄█ ▀█▀ ░░█░░ ░░█░░ █▀▀ █▄▄▀ '
	print '░▒█░░ ░▀░▀░ ▀▀▀ ░░▀░░ ░░▀░░ ▀▀▀ ▀░▀▀ ', colorama.Fore.RESET

try:
	configparser = SafeConfigParser()					
	configparser.read('twitter-monitor.cfg')
except IOError:
	print 'FILE NOT FOUND'
	exit()

try:
	plotBanner()
	script_filename, oauth_profile, configName = sys.argv
	ckey, csecret = loadAppOAuth(configparser)
	atoken, asecret = loadUserOAuth(configparser, sys.argv[1])
	hashtags = loadHashtags(configparser, configName)
	geolocated_filter_method = loadGeolocatedMethod(configparser, configName)
	filename_alias = loadFilenameAlias(configparser, configName)
except ValueError:
	print 'PLEASE INFORM THE INPUT DATA: python twitter-monitor-hashtags.py 1 configName'
	print 'Please check the config names available on twitter-monitor.cfg file'
	exit()

print 'Using Profile ' + sys.argv[1] + ' to monitor hashtags', hashtags
outputFile = open(datetime.datetime.now().strftime('%Y-%m-%d')+'-tweets-' + filename_alias + '.csv', 'a', 0)

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener())
while True:
	try:
		twitterStream.filter(track=hashtags)
	except Exception, e:
		print 'Initialization Error:', e
		print sys.exc_info()
	finally:
		time.sleep(1)
