# Kassio Machado - GNU License - 2014-03-11 
# PhD candidate on Science Computing - UFMG/Brazil
# Python script to get the history of weather on weather underground website. All data are
# loaded considering the entire month
# INPUT: NONE (valid authorized key on API, city, country and period)
# OUTPUT: all JSON received in response of HISTORY queries
# the fields of query are describe on http://www.wunderground.com/weather/api/d/docs?d=data/history

import urllib2 
import json 
import time
import os
import datetime
import colorama
from ConfigParser import SafeConfigParser

DATE_FORMAT = '%Y-%m-%d'

parser = SafeConfigParser()				# initalizing the parser
parser.read('uweather.cfg')				# loading config file
country = parser.get('uweather', 'country') 	# loading the file with section and the propertie name
city = parser.get('uweather', 'city')
dateBegin = datetime.datetime.strptime(parser.get('uweather', 'dateBegin'), DATE_FORMAT)	# dateBegin = datetime.date(2014,9,1)
dateEnd = datetime.datetime.strptime(parser.get('uweather', 'dateEnd'), DATE_FORMAT)		# dateEnd = datetime.date(2014,12,31)
keyindex = parser.get('uweather', 'keyindex')
keyAuth = parser.get('uweather', 'keyAuth').split(',')[int(keyindex)]

filename = 'uweather-'+city.lower()+'-'+str(dateBegin.year)+'.json'
outputFile = open(filename, 'a', 0)
print colorama.Fore.WHITE + colorama.Back.RED + 'Weather Underground Data Crawler - PhD. Kassio Machado (Candidate)\nCity ' + city + '\n' + 'keyAuth ' + keyAuth \
+ '\nPeriod ' + dateBegin.strftime('%Y-%m-%d') + ' to ' + dateEnd.strftime('%Y-%m-%d') + '\nFile ' + filename + ' (a)' +colorama.Fore.RESET + colorama.Back.RESET

while True:
	try:
		dateRec = dateBegin.strftime('%Y%m%d')
		if dateBegin.weekday() >= 6:
			colorDate = colorama.Fore.RED
		else:
			colorDate = colorama.Fore.YELLOW
		url = 'URL: http://api.wunderground.com/api/'+keyAuth+'/history_'+dateRec+'/q/'+country+'/'+city+'.json'
		print url
		f = urllib2.urlopen(url) 
		json_string = f.read()
		parsed_json = json.loads(json_string)
		dateStr = parsed_json['history']['date']['pretty']
		json.dump(parsed_json, outputFile)
		outputFile.write('\n')
		f.close()
		print colorDate+'Weather Data: ' + country + '-' + city + ' ' + dateStr+' (wait 7 seconds)'+colorama.Fore.RESET
		time.sleep(7)
		if dateBegin == dateEnd:
			break
		else:
			dateBegin += datetime.timedelta(days=1)
	except Exception, e:
		print 'Error: ' + str(e)
		time.sleep(60)

outputFile.close()
