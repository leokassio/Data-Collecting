# -*- coding: utf-8 -*-
import sys
import socket
import colorama as clm

from tqdm import tqdm
from contextlib import closing
from selenium.webdriver import Firefox
from selenium.webdriver import PhantomJS
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

inp = sys.argv[1]
input_file_path = inp + '-instagram-checkin.csv'
output_user_file_path = inp + '-instagram-users.csv'
output_error_file_path = inp + '-instagram-error.csv'
output_place_file_path = inp + '-instagram-places.csv'

socket.setdefaulttimeout(5)
setTweetIds = set()
setPlaceUrl = set()

input_file = open(input_file_path, 'r')
output_user_file = open(output_user_file_path, 'a+')
output_place_file = open(output_place_file_path, 'a+')
output_error_file = open(output_error_file_path, 'w')

output_user_file.seek(0)
for line in output_user_file:
	tweetId = line.split(',')[0]
	setTweetIds.add(tweetId)
print clm.Fore.YELLOW, ' Initially '+str(len(setTweetIds))+' users were already defined', clm.Fore.RESET

output_place_file.seek(0)
for line in  output_place_file:
	place_url = line.split(',')[0]
	setPlaceUrl.add(place_url)
print clm.Fore.YELLOW, ' Initially '+str(len(setPlaceUrl))+' places were already defined', clm.Fore.RESET


with closing(PhantomJS()) as driver: # Firefox PhantomJS
	input_file.seek(0) # restarting the cursor of file
	numLines = sum(1 for line in input_file)
	input_file.seek(0) # restarting the cursor of file
	lineindex = 0
	for line in tqdm(input_file, desc='Visiting Instagram Links', total=numLines, leave=True):
		lineindex += 1
       		tweetId = line.split(',')[0]
		if tweetId in setTweetIds:
               		print clm.Fore.YELLOW, tweetId, clm.Fore.RED, 'already defined!', clm.Fore.RESET
			setTweetIds.discard(tweetId)
               		continue
		linesplited = line.replace('\n', '').split(',')
		tweetId = linesplited[0]
		url = linesplited[1]
		if 'http://' not in url and 'https://' not in url:
        		url = 'http://' + url
		
		print clm.Fore.CYAN, url, clm.Fore.RESET
		try:
			driver.get(url)
			# search = lambda driver: driver.find_element_by_xpath("//a[contains(@href,'/explore/locations/')]")
			# place_url = WebDriverWait(driver, 3).until(search).get_attribute('href').encode('utf-8')
			# place_name = WebDriverWait(driver, 3).until(search).get_attribute('title').replace(',',' ').encode('utf-8')
			placetag = driver.find_element_by_class_name('_kul9p')
			placename = placetag.get_attribute('title')
			placeurl = placetag.get_attribute('href')
			usernametag = driver.find_element_by_class_name('_4zhc5')
			username = usernametag.get_attribute('title')
			print clm.Fore.YELLOW, username, placename, place_url, clm.Fore.RESET
			
			# msg = tweetId + ',' + url + ',' + place_name + ',' + place_url + '\n'
			# try:
			# 	output_user_file.write(msg)
			# except UnicodeDecodeError:
			# 	print msg
			# 	exit()
			
			# if place_url in setPlaceUrl:
			# 	print clm.Fore.YELLOW, place_url, clm.Fore.RED, 'already defined!', clm.Fore.RESET
			# 	continue
			# else:
			# 	setPlaceUrl.add(place_url)
			# 	output_place_file.write(str(place_name + ',' + place_url + '\n'))
		except 
		# except socket.timeout:
		# 	print clm.Fore.RED, ' ERROR ON READING INSTAGRAM PAGE', clm.Fore.RESET
		# 	msg = tweetId + ',' + url + ',TIMED OUT' '\n'
		# 	output_error_file.write(msg.encode('utf-8'))
		# except TimeoutException:
		# 	print clm.Fore.RED, ' ERROR ON FINDIND LINK ELEMENT', clm.Fore.RESET
		# 	msg = tweetId + ',' + url + ',LINK ERROR' + '\n'
		# 	output_error_file.write(msg.encode('utf-8'))
		# except StaleElementReferenceException:
		# 	print clm.Fore.RED, ' CACHE ERROR', clm.Fore.RESET
		# 	msg = tweetId + ',' + url + ',CACHE ERROR' + '\n'
		# 	output_error_file.write(msg.encode('utf-8'))

output_user_file.close()
output_place_file.close()
output_error_file.close()
input_file.close()
