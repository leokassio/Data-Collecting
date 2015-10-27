# -*- coding: utf-8 -*- 
# ============================================================================================
# Kassio Machado - GNU License - 2015-07-06 
# PhD candidate on Science Computing - UFMG/Brazil
# Crawler to visit Foursquare of venues registered on dataset of check-ins
# the data if provided in an CSV file and exported in other CSV file.
# The crawler used BeautifulSoup to perform the HTML parsing
# ============================================================================================

import re
import os
import io
import sys 
import urllib2
import codecs
import colorama as clm
from bs4 import BeautifulSoup

reload(sys)  
sys.setdefaultencoding('utf8')

cityName = sys.argv[1]
input_file_path = cityName + '-checkin.csv'
output_file_path = cityName + '-output.csv'
output_error_404_file_path = cityName + '-error-404.csv'

setUrls = set()
dictPlaces = dict()
seterror404 = set()

try:
	output_file = open(output_file_path, 'r')
	for line in output_file:
		try:
			linesplited = line.split(',')
			url4sq = linesplited[4]
			dictPlaces[url4sq] = (linesplited[5],linesplited[6],linesplited[7],linesplited[8])
			setUrls.add(linesplited[3])
		except IndexError:
			# print line
			# print clm.Back.RED+clm.Fore.WHITE, 'INDEX ERROR:',line, clm.Fore.RESET+clm.Back.RESET
			continue
	print clm.Fore.YELLOW, 'Initially '+str(len(dictPlaces.keys()))+' places and '+str(len(setUrls))+' checkins was already defined', clm.Fore.RESET
	output_file.close()
except IOError:
	pass
	print 'INPUT FILE NOT FOUND'

try:
	output_error_404 = open(output_error_404_file_path, 'r')
	for line in output_error_404:
		seterror404.add(line.replace('\n', ''))
	output_error_404.close()
except IOError:
	pass

input_file = open(input_file_path, 'r')
output_file = open(output_file_path, 'a')
output_error_404 = open(output_error_404_file_path, 'a')

input_file.seek(0) #restarting the cursor of file
numLines = sum(1 for line in input_file)
try:
	lineinit = sys.argv[2]
	input_file.seek(int(lineinit))
	linefileindex = int(lineinit)
except IndexError:
	input_file.seek(0) #restarting the cursor of file
	linefileindex = 0

for line in input_file:
	linefileindex += 1
	lineindex = len(setUrls)
	printFlag = lineindex %5 == 0
	# line example - 555566193625792512,41.90987.677,262338018,https://t.co/tfz5klPqMQ
	linesplited = line.replace('\n', '').split(',')
	try:
		id_data = linesplited[0].encode('utf-8')
		placeid = linesplited[1].encode('utf-8')
		userid = linesplited[2].encode('utf-8')
		url = linesplited[3].encode('utf-8')
		if 'http://' not in url and 'https://' not in url:
			url = 'http://' + url
	except IndexError:
		continue

	for attempt in range(1,4):
		soup = False
		try:
			if url in setUrls:
				if printFlag:
					print clm.Fore.CYAN, url, clm.Fore.RESET, '['+str(lineindex)+'/'+str(numLines)+'/'+str(numLines - lineindex)+'] ' + clm.Back.YELLOW+clm.Fore.BLACK+'  USER MATCH  '+clm.Fore.RESET+clm.Back.RESET
				break
			elif url in seterror404:
				if printFlag:
					print clm.Back.WHITE+clm.Fore.RED, 'Error 404 Already Defined:', url, clm.Fore.RESET+clm.Back.RESET
				break
			page = urllib2.urlopen(url, timeout=15).read()
			soup = BeautifulSoup(page)
			msg = id_data+','+placeid+','+userid+','+url
			break
		except IOError, e:
			if 'HTTP Error 404' in str(e) or 'Name or service not known' in str(e):
				output_error_404.write(url+'\n')
				break
			else:
				print clm.Back.WHITE+clm.Fore.BLACK, 'Error:', url, e, clm.Fore.RESET+clm.Back.RESET
				 
			# HTTP Error 404: Not Found
			# HTTP Error 500: Internal Server Error
			# HTTP Error 503:
			# <urlopen error [Errno -2] Name or service not known>
	if soup:
		matchflag = False
		for urlFoursquare in soup.select('div > h1 > a[href^="https://foursquare.com/"]'):
			url4sq = urlFoursquare.get('href').encode('utf-8')
			msg += ','+url4sq
			try: # test if that url of FOURSQUARE-PLACE was already fetched 
				t = dictPlaces[url4sq]
				try:
					msg += ',' + t[0] + ',' + t[1] + ',' + t[2] + ',' + t[3] + '\n'
				except TypeError:
					print t
					exit()
				output_file.write(msg)
				print clm.Fore.CYAN, url4sq, clm.Fore.RESET, str(linefileindex), '['+str(numLines),'|',str(linefileindex - lineindex),']', clm.Back.GREEN,clm.Fore.BLACK,' PLACE MATCH ',clm.Fore.RESET,clm.Back.RESET
				break
			except KeyError:
				pass

			try:
				page2 = urllib2.urlopen(urlFoursquare.get('href'), timeout=30).read()
				print clm.Fore.CYAN, url4sq, clm.Fore.RESET, str(linefileindex), '['+str(numLines), '|', str(linefileindex - lineindex),']', clm.Fore.RESET
				soup2 = BeautifulSoup(page2)
				sp = soup2.find_all('div', class_= 'categories')
			except urllib2.HTTPError:
				continue
			
			if sp:
				for category in sp:
					print clm.Fore.YELLOW, 'Place Class:', category.get_text(), clm.Fore.RESET
					category = category.get_text().replace(',', '*')
					msg += ',' + category
					matchflag = True
					break
			else:
				category = ',NoClass'
				msg += category
				output_error_file.write(line.encode('utf-8')) # TODO ERROR HANDLE
			sp = soup2.find_all('h1', class_= 'venueName')
			if sp:
				for name in sp:
					print clm.Fore.YELLOW, 'Place Name:', name.get_text(), clm.Fore.RESET
					name = name.get_text().replace(',', '*').encode('utf-8')
					msg += ',' + name
					break
			else:
				name = ',NoName'
				msg += name
			sp = soup2.find_all('span', itemprop='ratingValue')
			if sp:
				for score in sp:
					print clm.Fore.YELLOW, 'Place Rating:', score.get_text(), clm.Fore.RESET
					score = score.get_text().replace(',', '').encode('utf-8')
					msg += ',' + score
					break
			else:
				score = ',NoScore' 
				msg += score
			sp = soup2.find_all('input', class_= 'shareLink formStyle')
			if sp:
				for link in sp:
					if 'http://4sq.com' in link['value']:
						print clm.Fore.YELLOW, 'Link Official:', link['value'], clm.Fore.RESET
						link = link['value'].replace(',', '*').encode('utf-8')
						msg += ',' + link
						break					

			
			if matchflag == False:
				print clm.Fore.RED, 'X', clm.Fore.RESET
			else:
				dictPlaces[url4sq] = (category, name, score,link)
				setUrls.add(url)
				# msg = msg.replace('\n','')
				output_file.write(msg + '\n')
	# else:
	# 	print clm.Fore.RED, 'ERROR ON READING PAGE OF SWARM USER', clm.Fore.RESET
	# 	output_error_file.write(line.encode('utf-8'))

print clm.Fore.GREEN, 'Finished!', clm.Fore.RESET


