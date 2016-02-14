# -*- coding: utf-8 -*- 
# ============================================================================================
# Kassio Machado - GNU License - 2016-02-12 
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
import multiprocessing
from tqdm import tqdm
import colorama as clm
from bs4 import BeautifulSoup

reload(sys)  
sys.setdefaultencoding('utf8')

def resolveCheckin(id_data, url, fileout):
	soup = 'error'
	for attempt in range(4):
		try:
			page = urllib2.urlopen(url, timeout=5).read()
			soup = BeautifulSoup(page)
			break
		except IOError, e:
			# HTTP Error 404: Not Found
			# HTTP Error 500: Internal Server Error
			# HTTP Error 503:
			# <urlopen error [Errno -2] Name or service not known>
			e = str(e)
			if 'HTTP Error 404' in e or 'Name or service not known' in e:
				soup = None
			else:
				# print clm.Back.WHITE+clm.Fore.BLACK, 'Error Resolving Check-in:', url, e, clm.Fore.RESET+clm.Back.RESET
				soup = None
	if soup != None:
		try:
			urlFoursquare = soup.select('div > h1 > a[href^="https://foursquare.com/"]')[0]
			url4sq = urlFoursquare.get('href').encode('utf-8') 		# getting url to place on foursquare
			line = id_data + ',' + url + ',' + url4sq
			return (line, fileout)
		except IndexError:
			return None
	else:
		return None

def loadErrorLinks(cityName):
	seterror404 = set()
	try:
		output_error_404 = open(cityName + '-error-404.csv', 'r')
		for line in output_error_404:
			seterror404.add(line.replace('\n', ''))
		output_error_404.close()
	except IOError:
		print clm.Fore.RED+clm.Back.WHITE+'   ¯\_(ツ)_/¯ ERROR 404 INCEPTION (⊙_☉)    '+clm.Fore.RESET+clm.Back.RESET
		seterror404 = set()
	return seterror404

def saveDefinedPlace(ans):
	if ans != None:
		line, fileout = ans
		if line != None:
			output_file = open(fileout, 'a')
			output_file.write(line + '\n')
			output_file.close()

def define_url():
	cityName = sys.argv[1]
	bufferSize = 50
	pool = multiprocessing.Pool(bufferSize)

	urlBuffer = list()
	
	setPlaces = loadPlacesDataset(cityName)
	setPlaces, setUrls = loadDefinedPlaces(cityName, setPlaces)
	seterror404 = loadErrorLinks(cityName)

	input_file_path = cityName + '-checkin.csv'
	output_file_path = cityName + '-output.csv'
	output_error_404_file_path = cityName + '-error-404.csv'

	try:
		input_file = open(input_file_path, 'r')						# file with url checkins  to be resolved
		# output_file = open(output_file_path, 'a', 0)				# file with urls resolved
		output_error_404 = open(output_error_404_file_path, 'a')	# file of links offline
	except IOError:
		print clm.Fore.RED+clm.Back.WHITE+'   NO PLACE DATASET (⊙_☉) IMPOSSIBLE TO PROCEED...  '+clm.Fore.RESET+clm.Back.RESET

	numLines = sum(1 for line in input_file)		# counting lines on file
	input_file.seek(0) 								# restarting the cursor of file

	try:
		lineinit = sys.argv[2]						# in cases of bug, return from this line
		input_file.seek(int(lineinit))
	except IndexError:
		input_file.seek(0) 							# restarting the cursor of file

	for line in tqdm(input_file, desc='Defining URLs', total=numLines):
		linesplited = line.replace('\n', '').split(',')
		try:
			id_data = linesplited[0].encode('utf-8')
			url = linesplited[1].encode('utf-8')
			if 'http://' not in url and 'https://' not in url:
				url = 'http://' + url
		except IndexError:
			continue

		if url in seterror404:
			print clm.Back.WHITE+clm.Fore.YELLOW, 'Error 404:', url, clm.Fore.RESET+clm.Back.RESET
			continue
		elif url in setUrls:
			print clm.Back.WHITE+clm.Fore.GREEN, 'Already Defined', url, clm.Fore.RESET+clm.Back.RESET
			continue

		if len(urlBuffer) >= bufferSize:
			for i, u in urlBuffer:
				p = pool.apply_async(resolveCheckin, (i,u, output_file_path), callback=saveDefinedPlace)
			urlBuffer = list()
			p.wait()
		urlBuffer.append((id_data, url))

	print clm.Fore.GREEN, 'GG bro ;)', clm.Fore.RESET

def main():
	print 'Small and tiny script to define the Foursquare Venue/Place of Check-ins'
	define_url()

if __name__ == "__main__":
	main()




