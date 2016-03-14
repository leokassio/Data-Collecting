# -*- coding: utf-8 -*- 
# ============================================================================================
# Kassio Machado - GNU Public License - 2014-10-01
# PhD candidate on Science Computing - UFMG/Brazil
# Script to capture ONLY THE LOCATED (even withou lat,lng coordinates) tweets using the Twitter Stream API
# ============================================================================================

import os
import sys
import json
import time
import datetime
import colorama
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from ConfigParser import SafeConfigParser

outputFile = None

def loadAppOAuth(configparser):
	configSection = 'twitter_oauth'
	ckey = configparser.get(configSection, 'ckey') 
	csecret = configparser.get(configSection, 'csecret')
	return ckey, csecret

def loadUserOAuth(configparser, profile):
	configSection = 'twitter_oauth'
	atoken = configparser.get(configSection, 'atoken'+profile) 	# loading the file with section and the propertie name
	asecret = configparser.get(configSection, 'asecret'+profile)
	return atoken, asecret

def loadBoundBox(configparser, locationName):
	configSection = 'cities_bbox'
	locationLabel = configparser.get(configSection, locationName+'_label')
	print colorama.Fore.YELLOW + 'Loading', colorama.Fore.RED + locationLabel, colorama.Fore.YELLOW + 'coordinates...' + colorama.Fore.RESET
	lng0 = configparser.getfloat(configSection, locationName+'_lng0')
	lngn = configparser.getfloat(configSection, locationName+'_lngn')
	lat0 = configparser.getfloat(configSection, locationName+'_lat0')
	latn = configparser.getfloat(configSection, locationName+'_latn')
	coordinates = [lng0, lat0, lngn, latn]
	print colorama.Fore.RED + locationLabel , colorama.Fore.YELLOW + 'Bounding Box', coordinates, colorama.Fore.GREEN + '[OK]' + colorama.Fore.RESET
	return locationLabel, coordinates

def main():
	if len(sys.argv) == 3:
		configparser = SafeConfigParser()										# initalizing the parser
		configparser.read('twitter-monitor.cfg')								# loading config file
		ckey, csecret = loadAppOAuth(configparser)
		atoken, asecret = loadUserOAuth(configparser, sys.argv[1])
		locationLabel, cooordinates = loadBoundBox(configparser, sys.argv[2])
	else:
		print 'PLEASE INFORM THE INPUT DATA'
		print 'python twitter-monitor-geolocation.py auth-index(int) location-name (string)'
		exit()

	global outputFile
	outputFile = open(datetime.datetime.now().strftime('%Y-%m-%d')+'-tweets-geolocation-' + locationLabel.lower() + '.csv', 'a', 0)

	auth = OAuthHandler(ckey, csecret)
	auth.set_access_token(atoken, asecret)
	twitterStream = Stream(auth, listener())
	while True:
		try:
			twitterStream.filter(locations=cooordinates)
		except Exception as e:
			print 'init error', sys.exc_info()
		finally:
			time.sleep(5)

class listener(StreamListener):
	geolocated_filter_method = 0
	def __init__(self):
		geolocated_filter_method = 1
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
			if parsed_json['place'] != None:
				location = parsed_json['place']['full_name'].encode('utf-8')
				location = location.replace(',', '')
			else:
				location = 'None'
			if parsed_json['source'] != None:
				source = parsed_json['source'].encode('utf-8')
			else:
				source = 'None'
			msg = tid + ', ' + uid + ', ' + str(coords[0]).encode('utf-8') + ', ' + str(coords[1]).encode('utf-8') + ', ' + timestamp + ', ' + location + ', ' + tweet + ', ' + source
			if 'four' in source:
				print colorama.Fore.GREEN, msg, colorama.Fore.RESET
			elif 'insta' in source:
				print colorama.Fore.YELLOW, msg, colorama.Fore.RESET
			elif coords[0] != None:
				print colorama.Fore.CYAN, msg, colorama.Fore.RESET
			else:
				print msg
			outputFile.write(msg+'\n')
		except KeyError:
			if 'limit' not in parsed_json.keys():
				print colorama.Fore.RED, parsed_json.keys(), colorama.Fore.RESET
			else:
				print colorama.Fore.RED, '[INFO] Stream limit message:', parsed_json['limit']['track'], colorama.Fore.RESET
		# except Exception as e:
		# 	exc_type, exc_obj, exc_tb = sys.exc_info()
		# 	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		# 	print(exc_type, fname, exc_tb.tb_lineno)

	def on_error(self, status):
		print '==============================\nSTREAM ERROR\n=============================='
		print 'error ' + status
		return True

	def on_timeout(self):
		print '==============================\nSTREAM TIMEOUT\n=============================='
		return True


if __name__ == "__main__":
	main()
