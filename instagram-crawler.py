from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
import sys
import socket
import colorama as clm
from contextlib import closing
inp = sys.argv[1]
input_file_path = inp + '-checkin.csv'
output_user_file_path = inp + '-users.csv'
output_error_file_path = inp + '-error.csv'
output_place_file_path = inp + '-places.csv'
socket.setdefaulttimeout(5)
setTweetIds = set()
setPlaceUrl = set()
output_user_file = open(output_user_file_path, 'a+')
output_place_file = open(output_place_file_path, 'a+')
output_error_file = open(output_error_file_path, 'w')
input_file = open(input_file_path, 'r')
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

with closing(Firefox()) as driver:
	input_file.seek(0) #restarting the cursor of file
	numLines = sum(1 for line in input_file)
	input_file.seek(0) #restarting the cursor of file
	lineindex = 0
	for line in input_file:
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
		print clm.Fore.CYAN, url, clm.Fore.RESET, '['+str(lineindex)+'/'+str(numLines - lineindex)+'/'+str(numLines)+']' + '[' + str((float(lineindex)/float(numLines))*100.0) + '%]'
		try:
			driver.get(url)
			search = lambda driver: driver.find_element_by_xpath("//a[contains(@href,'/explore/locations/')]")
			place_url = WebDriverWait(driver, 3).until(search).get_attribute('href').encode('utf-8')
			place_name = WebDriverWait(driver, 3).until(search).get_attribute('title').replace(',',' ')
			print clm.Fore.YELLOW, ' Place Name: ' + place_name, clm.Fore.RESET
			print clm.Fore.YELLOW, ' Place URL: ' + place_url, clm.Fore.RESET
			msg = tweetId + ',' + url + ',' + place_name + ',' + place_url + '\n'
			output_user_file.write(msg.encode('utf-8'))
			if place_url in setPlaceUrl:
				print clm.Fore.YELLOW, place_url, clm.Fore.RED, 'already defined!', clm.Fore.RESET
				continue
			else:
				setPlaceUrl.add(place_url)
				place_url = place_url + "\n"
				output_place_file.write(place_url)
		except socket.timeout:
			print clm.Fore.RED, ' ERROR ON READING INSTAGRAM PAGE', clm.Fore.RESET
			msg = tweetId + ',' + url + ',TIMED OUT' '\n'
			output_error_file.write(msg.encode('utf-8'))
		except TimeoutException:
			print clm.Fore.RED, ' ERROR ON FINDIND LINK ELEMENT', clm.Fore.RESET
			msg = tweetId + ',' + url + ',LINK ERROR' + '\n'
			output_error_file.write(msg.encode('utf-8'))
		except StaleElementReferenceException:
			print clm.Fore.RED, ' CACHE ERROR', clm.Fore.RESET
			msg = tweetId + ',' + url + ',CACHE ERROR' + '\n'
			output_error_file.write(msg.encode('utf-8'))
output_user_file.close()
output_place_file.close()
output_error_file.close()
input_file.close()
