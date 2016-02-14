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
from tqdm import tqdm

reload(sys)  
sys.setdefaultencoding('utf8')

cityName = sys.argv[1]
input_file_path = cityName + '-checkin.csv'
output_file_path = cityName + '-output.csv'
output_error_404_file_path = cityName + '-error-404.csv'

setUrls = set()
dictPlaces = dict()
seterror404 = set()

fileplaces = open(cityName + '-all-places.csv')
for line in fileplaces:
	try:
		url, url4sq, placename, category, score = line.replace('\n', '').split(',')
		dictPlaces[url] = [url4sq, placename, category, score]
	except IndexError:
		print 'error', line
try:
	output_file = open(output_file_path, 'r')
	for line in output_file:
		try:
			linesplited = line.replace('\n', '').split(',')
			url = linesplited[2]
			if url not in dictPlaces:
				dictPlaces[url] = (linesplited[3],linesplited[4],linesplited[5],linesplited[6])
			setUrls.add(linesplited[1])
		except IndexError:
			print 'error', line
	print clm.Fore.YELLOW, 'Initially '+str(len(dictPlaces))+' places and '+str(len(setUrls))+' checkins was already defined', clm.Fore.RESET
	output_file.close()
except IOError:
	print 'NO OUTPUT FILE'

try:
	output_error_404 = open(output_error_404_file_path, 'r')
	for line in output_error_404:
		seterror404.add(line.replace('\n', ''))
	output_error_404.close()
except IOError:
	print 'NO ERROR FILE'

input_file = open(input_file_path, 'r')
output_file = open(output_file_path, 'a', 0)
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

for line in tqdm(input_file, desc='Defining URLs', total=numLines):
	linefileindex += 1
	linesplited = line.replace('\n', '').split(',')
	try:
		id_data = linesplited[0].encode('utf-8')
		url = linesplited[1].encode('utf-8')
		if 'http://' not in url and 'https://' not in url:
			url = 'http://' + url
	except IndexError:
		continue

	for attempt in range(4):
		soup = False
		try:
			if url in seterror404:
				print clm.Back.WHITE+clm.Fore.RED, 'Error 404 or Already Defined:', url, clm.Fore.RESET+clm.Back.RESET
				break
			page = urllib2.urlopen(url, timeout=15).read()
			soup = BeautifulSoup(page)
			msg = id_data+','+url
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
			try:
				urldefined, placename, category, score = dictPlaces[url4sq]
				msg += ',' + category + ',' + placename + ',' + score + ','  + urldefined + '\n'
				output_file.write(msg)
				print url4sq, clm.Back.GREEN,clm.Fore.BLACK,' PLACE MATCH ',clm.Fore.RESET,clm.Back.RESET
				break
			except KeyError:
				pass
				
			try:
				page2 = urllib2.urlopen(urlFoursquare.get('href'), timeout=30).read()
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
				# output_error_file.write(line.encode('utf-8')) # TODO ERROR HANDLE
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
				dictPlaces[url4sq] = [link, name, category, score]
				# dictPlaces[url4sq] = (category, name, score,link)
				setUrls.add(url)
				# msg = msg.replace('\n','')
				output_file.write(msg + '\n')
	# else:
	# 	print clm.Fore.RED, 'ERROR ON READING PAGE OF SWARM USER', clm.Fore.RESET
	# 	output_error_file.write(line.encode('utf-8'))

print clm.Fore.GREEN, 'Finished!', clm.Fore.RESET


