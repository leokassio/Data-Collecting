# ============================================================================================
# Kassio Machado - GNU Public License - 2015-01-15 
# PhD candidate on Science Computing - UFMG/Brazil
# Python script to get the information about traffic on the sevice of Chicago Traffic Tracker
# ============================================================================================

import sys
sys.path.append("/home/leokassio/Dropbox/PhD Sensing Layers/data-processing/scripts/lib")
import libutils as utils
import urllib2 
import json
import time
import hashlib

timeStampSet = set()
try:
	inputFile = open('chicago-traffic-tracker.dat', 'r')
	for line in inputFile:
		lineSplited = line.split('\t')
		idRegister = lineSplited[0]+':'+lineSplited[1]
		timeStampSet.add(idRegister)
	print timeStampSet
except:
	#do nothing
	print 'no file previously created'


outputFile = open('chicago-traffic-tracker.dat', 'a', 0)

while True:
	try:
		url = 'https://data.cityofchicago.org/resource/t2qc-9pjd.json'
		f = urllib2.urlopen(url) 
		json_string = f.read()
		parsed_json = json.loads(json_string)
		print '========================================================================='
		print 'Chicago Traffic Tracker - Crawler by Kassio M. '
		print '========================================================================='
		for region in parsed_json:
			idRegister = str(region['_last_updt'])+':'+str(region['_region_id'])
			if idRegister in timeStampSet:
				continue
			timeStampSet.add(idRegister)
			fileLine = str(region['_last_updt']) + '\t' + str(region['_region_id']) + '\t' + str(region['current_speed']) + '\t' + str(region['region']) + '\t' + str(region['_description']) + '\n'
			outputFile.write(fileLine)
			print 'TimeStamp: ' + str(region['_last_updt']) + ' - Region #' + str(region['_region_id']) + ' - ' + str(region['current_speed'])
		print 'Waiting 7 minutes to next ' + utils.getTime()
		t = 5*60
		time.sleep(t)
	except:
		print 'Error on Stream'
		print sys.exc_traceback.tb_lineno
	finally:
		t = 2 * 60
		time.sleep(t)
