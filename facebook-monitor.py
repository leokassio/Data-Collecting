# -*- coding: utf-8 -*- 
# ============================================================================================
# Kassio Machado - GNU License - 2016-03-10
# PhD candidate on Science Computing - UFMG/Brazil
# Python script to get Facebook information of selected pages
# ============================================================================================

import time
import json
import socket
import urllib2 
import colorama
import datetime
from tqdm import tqdm
from prettytable import PrettyTable
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
	dictValues = dict()
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

	for p in pages:
		dictValues[p] = dict(likes=0, talking=0)

	while dt <= deadline:
		dt = datetime.datetime.now()
		timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
		collumnLabel = dt.strftime('%d/%m/%Y %H:%M')
		print '[INFO] Last timestamp check:', timestamp
		pttb = PrettyTable([collumnLabel, 'Likes', 'New Likes', 'Talking', 'New Talking'])
		for p in tqdm(pages, desc='Crawling Facebook pages'):
			url = pattern.replace(kwtoken, token).replace(kwurl, p)
			data = dict()
			for i in range(3):
				try:
					req = urllib2.urlopen(url, timeout=10)
					rawdata = req.read()
					data = json.loads(rawdata)
					if len(data.keys()) > 0:
						break
				except urllib2.HTTPError as e:
					print url, 'HTTP Error', e
					time.sleep(i)
				except socket.timeout as e:
					print url, 'Timeout', e
					time.sleep(i)
				except Exception as e:
					print 'Exception Generic'
					print url, e
					time.sleep(i)
			try:
				username = unicode(data['username'])
				idPage = unicode(data['id'])
				likes = unicode(data['likes'])
				talking = unicode(data['talking_about_count'])
				checkins = unicode(data['checkins'])
				line = timestamp + ',' + p + ',' + username + ',' + idPage + ',' + likes + ',' + talking + ',' + checkins
				fileout.write(line + '\n')
				
				likes = int(likes)
				talking = int(talking)
				difflikes = '0'
				difftalk = '0'
				
				diff = likes - dictValues[p]['likes']
				if diff > 0:
					difflikes = colorama.Fore.GREEN + '+' + str(diff) + colorama.Fore.RESET
				elif diff < 0:
					difflikes = colorama.Fore.RED + str(diff) + colorama.Fore.RESET
				
				diff = talking - dictValues[p]['talking']
				if diff > 0:
					difftalk = colorama.Fore.GREEN + '+' + str(diff) + colorama.Fore.RESET
				elif diff < 0:
					difftalk = colorama.Fore.RED + str(diff) + colorama.Fore.RESET

				dictValues[p]['likes'] = likes
				dictValues[p]['talking'] = talking

				pttb_data = [username, likes, difflikes, talking, difftalk]
				pttb.add_row(pttb_data)
			except KeyError:
				print data
			time.sleep(1)
		
		print pttb
		
		for i in tqdm(range(interval * 60), desc='Waiting ' + str(interval) + 'mins'):
			time.sleep(1)


if __name__ == "__main__":
	dataCollection()























