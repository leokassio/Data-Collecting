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

boundingBoxNames = ['New_York', 'Chicago', 'Los_Angeles', 'Belo_Horizonte', 'Sao_Paulo', 'Rio', 'Istanbul', 'Paris', 'London']
boundingBoxes = [[-74.25909,40.491369,-73.700272,40.915256], #new_york
[-87.940267,41.644335,-87.524044,42.023131], #chicago 
[-118.668176,33.703692,-118.155289,34.337306], #los angeles 
[-44.063313,-20.029118,-43.864787,-19.776315], #belo hoizonte 
[-46.825514,-24.008221,-46.365084,-23.356604], #sao paulo 
[-43.79506,-23.076347,-43.101836,-22.746199], #rio de janeiro
[28.595554,40.811404,29.428805,41.199239], #istanbul
[2.224199,48.815573,2.469921,48.902145], #paris
[-0.351468,51.38494,0.148271,51.672343]] #london

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


def getBoundBox(index):
	index = int(index)
	yield boundingBoxes[index]
	yield boundingBoxNames[index]

if len(sys.argv) == 3:
	configparser = SafeConfigParser()										# initalizing the parser
	configparser.read('twitter-monitor.cfg')								# loading config file
	ckey, csecret = loadAppOAuth(configparser)
	atoken, asecret = loadUserOAuth(configparser, sys.argv[1])
	cooordinates, city = getBoundBox(sys.argv[2])
	print city
else:
	print 'PLEASE INFORM THE INPUT DATA'
	exit()

outputFile = open(datetime.datetime.now().strftime('%Y-%m-%d')+'-tweets-geolocation-' + city + '.csv', 'a', 0)

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
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)

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
		twitterStream.filter(locations=cooordinates)
	except Exception as e:
		print 'init error', sys.exc_info()
	finally:
		time.sleep(5)
