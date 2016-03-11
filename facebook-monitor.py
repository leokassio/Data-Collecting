# -*- coding: utf-8 -*- 
# ============================================================================================
# Kassio Machado - GNU License - 2016-03-10
# PhD candidate on Science Computing - UFMG/Brazil
# Python script to get Facebook information of selected pages
# ============================================================================================

import time
import json
import urllib2 
import colorama
import datetime
from tqdm import tqdm

from ConfigParser import RawConfigParser

infoPrefix = '[INFO] '

def loadConfiguration(facebookConfigFilename='facebook-monitor.cfg'):
	print colorama.Fore.CYAN + infoPrefix + 'Loading Configuration File' + colorama.Fore.RESET
	dictConfig = dict()
	parser = RawConfigParser()
	parser.read(facebookConfigFilename)
	dictConfig['access_token'] = parser.get('auth', 'access_token')
	dictConfig['page_info_url_keyword'] = parser.get('page_info', 'page_info_url_keyword')
	dictConfig['page_info_token_keyword'] = parser.get('page_info', 'page_info_token_keyword')
	dictConfig['page_info_pattern'] = parser.get('page_info', 'page_info_pattern')
	dictConfig['page_info_targets'] = parser.get('page_info', 'page_info_targets').split(',')
	dictConfig['page_info_interval'] = parser.getint('page_info', 'page_info_interval') # secs
	dictConfig['page_info_out'] = parser.get('page_info', 'page_info_out')
	dictConfig['page_info_deadline'] = parser.get('page_info', 'page_info_deadline')

	try:
		dictConfig['page_info_deadline'] = datetime.datetime.strptime(dictConfig['page_info_deadline'], '%Y-%m-%d %H:%M:%S')
	except ValueError:
		dictConfig['page_info_deadline'] = datetime.datetime.now() + datetime.timedelta(days=(365 * 10)) # lol hahahaha
	return dictConfig


def dataCollection():
	configFile = loadConfiguration()
	
	pattern = configFile['page_info_pattern']
	token = configFile['access_token']
	kwurl = configFile['page_info_url_keyword']
	kwtoken = configFile['page_info_token_keyword']
	pages = configFile['page_info_targets']
	interval = configFile['page_info_interval']
	fileout = configFile['page_info_out']
	deadline = configFile['page_info_deadline']

	fileout = open(fileout, 'a', 0)
	dt = datetime.datetime.now()

	while dt <= deadline:
		dt = datetime.datetime.now()
		timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
		for p in pages:
			url = pattern.replace(kwtoken, token).replace(kwurl, p)
			data = dict()
			for i in range(3):
				try:
					req = urllib2.urlopen(url)
					rawdata = req.read()
					data = json.loads(rawdata)
					if len(data.keys()) > 0:
						break
				except urllib2.HTTPError:
					print url
					time.sleep(i)
			try:
				username = unicode(data['username'])
				idPage = unicode(data['id'])
				likes = unicode(data['likes'])
				talking = unicode(data['talking_about_count'])
				checkins = unicode(data['checkins'])
				line = timestamp + ',' + p + ',' + username + ',' + idPage + ',' + likes + ',' + talking + ',' + checkins
				fileout.write(line + '\n')
				print line
			except KeyError:
				print data
			time.sleep(1)
		for i in tqdm(range(interval * 6), desc='Waiting ' + str(interval) + 'mins'):
			time.sleep(10)


if __name__ == "__main__":
	dataCollection()























