# -*- coding: utf-8 -*- 
# ============================================================================================
# Kassio Machado - GNU License - 2015-05-08 
# PhD candidate on Science Computing - UFMG/Brazil
# Script to capture the signal stregth and statistics from OpenSignal project
# obs: the data is queried based on latitude and longitude provided by a mongodb collection 
# that persist venues indexed by foursquare
# ============================================================================================

import urllib2 
import json 
import time
import os
import datetime
import colorama
import sys
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from ConfigParser import SafeConfigParser
from ConfigParser import NoOptionError

# json_string = '{ "apiVersion": "2", "latitude": "40.74828059", "longitude": "-73.98556262", "distance": "2", "network_type": "", "perMinuteCurrent": 0, "perMinuteLimit": 10, "perMonthCurrent": 0, "perMonthLimit": 2000, "networkRank": [ { "networkName": "AT&T", "networkId": "310410", "type4G": { "networkName": "AT&T", "networkId": "310410", "networkType": "4", "averageRsrpAsu": "55.404914", "averageRsrpDb": "-84.595086", "sampleSizeRSRP": "1733365", "downloadSpeed": "7032.0000", "uploadSpeed": "4955.5588", "pingTime": "67.9349", "reliability": "95.4802478134136" }, "type3G": { "networkName": "AT&T", "networkId": "310410", "networkType": "3", "averageRssiAsu": "18.685492", "averageRssiDb": "-75.629016", "sampleSizeRSSI": "182365", "downloadSpeed": "3768.3214", "uploadSpeed": "670.5714", "pingTime": "168.2308", "reliability": "86.9794973544981" }, "type2G": { "networkName": "AT&T", "networkId": "310410", "networkType": "2", "averageRssiAsu": "18.380838", "averageRssiDb": "-76.238325", "sampleSizeRSSI": "9770" } }, { "networkName": "Verizon", "networkId": "3104", "type4G": { "networkName": "Verizon", "networkId": "3104", "networkType": "4", "averageRsrpAsu": "50.957408", "averageRsrpDb": "-89.042592", "sampleSizeRSRP": "1700341", "downloadSpeed": "10971.3694", "uploadSpeed": "9498.2881", "pingTime": "82.5449", "reliability": "98.2799744897958" }, "type3G": { "networkName": "Verizon", "networkId": "3104", "networkType": "3", "averageRssiAsu": "17.283824", "averageRssiDb": "-78.432352", "sampleSizeRSSI": "68234" }, "type2G": { "networkName": "Verizon", "networkId": "3104", "networkType": "2", "averageRssiAsu": "12.197195", "averageRssiDb": "-88.605610", "sampleSizeRSSI": "31611" } }, { "networkName": "T-Mobile", "networkId": "310260", "type4G": { "networkName": "T-Mobile", "networkId": "310260", "networkType": "4", "averageRsrpAsu": "50.445253", "averageRsrpDb": "-89.554747", "sampleSizeRSRP": "1608206", "downloadSpeed": "11877.6959", "uploadSpeed": "10977.7000", "pingTime": "65.4171", "reliability": "98.7242926155971" }, "type3G": { "networkName": "T-Mobile", "networkId": "310260", "networkType": "3", "averageRssiAsu": "18.095907", "averageRssiDb": "-76.808187", "sampleSizeRSSI": "353714", "downloadSpeed": "4448.0326", "uploadSpeed": "947.8205", "pingTime": "147.6667", "reliability": "91.8905380333958" }, "type2G": { "networkName": "T-Mobile", "networkId": "310260", "networkType": "2", "averageRssiAsu": "19.131864", "averageRssiDb": "-74.736272", "sampleSizeRSSI": "36292" } }, { "networkName": "Sprint", "networkId": "310120", "type4G": { "networkName": "Sprint", "networkId": "310120", "networkType": "4", "averageRsrpAsu": "46.846936", "averageRsrpDb": "-93.153064", "sampleSizeRSRP": "557188", "downloadSpeed": "5279.5156", "uploadSpeed": "4149.9231", "pingTime": "86.5385", "reliability": "95.0026315789495" }, "type3G": { "networkName": "Sprint", "networkId": "310120", "networkType": "3", "averageRssiAsu": "16.099248", "averageRssiDb": "-80.801505", "sampleSizeRSSI": "112898", "downloadSpeed": "870.1667", "uploadSpeed": "762.7273", "pingTime": "143.1154", "reliability": "94.9030612244929" }, "type2G": { "networkName": "Sprint", "networkId": "310120", "networkType": "2", "averageRssiAsu": "15.065150", "averageRssiDb": "-82.869700", "sampleSizeRSSI": "9166" } }, { "networkName": "Cellular One", "networkId": "31070", "type3G": { "networkName": "Cellular One", "networkId": "31070", "networkType": "3", "averageRssiAsu": "18.080991", "averageRssiDb": "-76.838019", "sampleSizeRSSI": "14101" }, "type2G": { "networkName": "Cellular One", "networkId": "31070", "networkType": "2", "averageRssiAsu": "12.808333", "averageRssiDb": "-87.383333", "sampleSizeRSSI": "704" } } ] }'
configparser = SafeConfigParser()										# initalizing the parser
configparser.read('opensignal-crawler.cfg')								# loading config file
apikeys = list()
for i in range(1,50):
	try:
		apikeys.append(configparser.get('opensignal_oauth', 'apikey'+str(i)))
	except NoOptionError:
		break

cityName = 'new-york'
outputFile = 'opensignal-dataset-'+cityName+'.csv'
distance = 3
apindex = 1
apikey = apikeys[apindex]

setOpensignal = set() # fetch all places already defined on opensignal collection
dictFoursquarePlaces = dict() # fetch all places on foursquare collection

conn = MongoClient('localhost', 27017)
db = conn['sensing_layers']
foursquare_collection = db['foursquare_places']
social_media_collection = db['social_media_geolocated']
opensignal_collection = db['opensignal']

############################################################################################################
# connect to sensing_layers mongodb to get all places indexed by Foursquare
cursor = foursquare_collection.find({'city':cityName}, {'_id':0, 'place_name':1, 'url':1})
placeindex = 0
print '\n',colorama.Back.WHITE+colorama.Fore.RED, ' OpenSignal API Client -',cityName.upper(), colorama.Back.RESET, colorama.Fore.RESET
print colorama.Fore.YELLOW, 'Loading Foursquare Places Dataset:', cursor.count(),'places [and merging with lat & lng]', colorama.Fore.RESET
for c in cursor:
	placeindex += 1
	place = social_media_collection.find_one({'placeid':c['url']}, {'_id':0, 'placeid':1, 'lat':1, 'lng':1})
	dictFoursquarePlaces[c['url']] = place


cursor = opensignal_collection.find({'city':cityName})
print colorama.Fore.CYAN, 'Loading OpenSignal Dataset:', cursor.count(), 'places already defined', colorama.Fore.RESET
for c in cursor:
	setOpensignal.add(c['placeid'])
	try:
		del dictFoursquarePlaces[c['placeid']]
	except KeyError:
		pass
##############################################################################################################################

print colorama.Fore.GREEN, len(dictFoursquarePlaces.keys()), 'Places to collect now... ', colorama.Fore.RESET

placecount = len(dictFoursquarePlaces.keys())
for placekey in dictFoursquarePlaces.keys():
	place = dictFoursquarePlaces[placekey]
	url = 'http://api.opensignal.com/v2/networkstats.json?lat='
	url += str(place['lat'])+'&lng='+str(place['lng'])
	url += '&distance='+str(distance)+'&json_format=2&apikey='+apikey
	
	try:
		f = urllib2.urlopen(url)
		json_string = f.read()
		parsed_json = json.loads(json_string)
	except urllib2.HTTPError:
		time.sleep(5)
	except ValueError:
		print colorama.Back.YELLOW+colorama.Fore.RED, 'Error on decoding JSON data ', colorama.Fore.RESET+colorama.Back.RESET
		continue

	minuteRemain = int(parsed_json['perMinuteLimit']) - int(parsed_json['perMinuteCurrent'])
	monthRemain = int(parsed_json['perMonthLimit']) - int(parsed_json['perMonthCurrent'])
	if monthRemain <= 10:
		apikeys.remove(apikey)
	if minuteRemain <= 0:
		if apindex < len(apikeys)-1:
			apindex += 1
		else:
			apindex = 0
			print colorama.Back.RED+colorama.Fore.WHITE, 'API interval (10 sec) ... ', colorama.Fore.RESET+colorama.Back.RESET
			# time.sleep(10)
		apikey = configparser.get('opensignal_oauth', 'apikey'+str(apindex)) 
	else:
		placecount -= 1
		print 'Places Reamining',placecount ,'Apikey', apindex, '[ Minutes', minuteRemain, ' Month', monthRemain,' ]', apikey, placekey

	dictCarrier = dict()
	netstats = parsed_json['networkRank']
	for carrier in netstats:
		carrierid = carrier['networkId']
		carriername = carrier['networkName']
		try:
			del carrier['type4G']['networkId']
			del carrier['type4G']['networkType']
			del carrier['type4G']['networkName']
			del carrier['type4G']['averageRsrpAsu']
		except KeyError:
			pass
		try:
			del carrier['type3G']['networkId']
			del carrier['type3G']['networkType']
			del carrier['type3G']['networkName']
			del carrier['type3G']['averageRssiAsu']
		except KeyError:
			pass
		try:
			del carrier['type2G']['networkId']
			del carrier['type2G']['networkType']
			del carrier['type2G']['networkName']
			del carrier['type2G']['averageRssiAsu']
		except KeyError:
			pass

	opensignalregister = dict()
	opensignalregister['city'] = cityName
	opensignalregister['placeid'] = placekey
	opensignalregister['lat'] = place['lat']
	opensignalregister['lng'] = place['lng']
	opensignalregister['netstats'] = netstats
	try:
		opensignal_collection.insert(opensignalregister)
	except DuplicateKeyError:
		outputerror = open('opensignal-error.json', 'a')
		outputerror.write(opensignalregister+'\n')
		outputerror.close()
