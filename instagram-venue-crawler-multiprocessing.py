# -*- coding: utf-8 -*- 
# ============================================================================================
# Kassio Machado - GNU License - 2016-02-12 
# PhD candidate on Science Computing - UFMG/Brazil
# Crawler to visit Instagram urls and get venues registered on dataset of check-ins
# the data if provided in an CSV file and exported in other CSV file.
# The crawler used selenium to perform the HTML/JavaScript parsing
# ============================================================================================

import sys
import colorama 
import selenium
import datetime
from tqdm import tqdm
from threading import Thread
from selenium.webdriver import Firefox
from selenium.webdriver import PhantomJS

reload(sys)  
sys.setdefaultencoding('utf8')

bufferSize = 100
threadBufferSize = 10
driverBuffer = list()
outputFilename = '-instagram-output.csv'
input_file_path = '-instagram-checkin.csv'


def resolveCheckin(driver, id_data, url):
	try:
		driver.get(url)
		placetag = driver.find_element_by_class_name('_kul9p')
		placeurl = placetag.get_attribute('href').encode('utf-8')
		placename = placetag.get_attribute('title').encode('utf-8')

		usernametag = driver.find_element_by_class_name('_4zhc5')
		username = usernametag.get_attribute('title').encode('utf-8')
		return id_data + ',' + url + ',' + placeurl + ',' + placename + ',' +  username
	except selenium.common.exceptions.NoSuchElementException:
		try:
			error = driver.find_element_by_class_name('error-container')
			return id_data + ',' + url
		except selenium.common.exceptions.NoSuchElementException:
			return id_data + ',' + url
	except AttributeError:
		return id_data + ',' + url

def resolveCheckinBatch(thread_id, driver, urlBuffer):
	t0 = datetime.datetime.now()
	# driver = driver = PhantomJS('./phantomjs')
	results = list()
	for id_data, url in urlBuffer:
		r = resolveCheckin(driver, id_data, url)
		results.append(r)
	global outputFilename
	global driverBuffer
	driverBuffer.append(driver)
	f = open(outputFilename, 'a')
	for r in results:
		f.write(r + '\n')
	f.close()
	print 'Thread Finished', '#' + (thread_id), (datetime.datetime.now() - t0).total_seconds(), 'secs'
	return results

def loadDefinedPlaces(outputFilename):
	setUrlDefined = set()
	try:
		outputfile = open(outputFilename, 'r')
		for line in outputfile:
			linesplited = line.replace('\n', '').split(',')
			setUrlDefined.add(linesplited[0])
		outputfile.close()
	except IOError:
		print colorama.Fore.RED+colorama.Back.WHITE+'   ¯\_(ツ)_/¯ NO OUTPUT FILE FOUND    '+colorama.Fore.RESET+colorama.Back.RESET
	return setUrlDefined

def define_url():
	global driverBuffer
	global bufferSize
	global threadBufferSize
	global outputFilename
	global input_file_path

	cityName = sys.argv[1]
	outputFilename = cityName + outputFilename
	input_file_path = cityName + input_file_path
	
	urlBuffer = list()
	threadBuffer = list()

	for i in range(threadBufferSize):
		driver = PhantomJS('./phantomjs') # in case of PhantomJS not available, we can use Firefox
		driverBuffer.append(driver)
	setUrlDefined = loadDefinedPlaces(outputFilename)

	print colorama.Back.RED+colorama.Fore.YELLOW+str(len(setUrlDefined))+' URLs already defined! Lets Rock more now...'+colorama.Back.RESET+colorama.Fore.RESET

	try:
		input_file = open(input_file_path, 'r')						# file with url checkins  to be resolved
	except IOError:
		print colorama.Fore.RED+colorama.Back.WHITE+'   NO PLACE DATASET (⊙_☉) IMPOSSIBLE TO PROCEED...  '+colorama.Fore.RESET+colorama.Back.RESET

	numLines = sum(1 for line in input_file)		# counting lines on file
	input_file.seek(0) 								# restarting the cursor of file

	try:
		lineinit = sys.argv[2]						# in cases of bug, return from this line
		input_file.seek(int(lineinit))
	except IndexError:
		input_file.seek(0) 							# restarting the cursor of file

	for line in tqdm(input_file, desc='Defining URLs ' + cityName, total=numLines, leave=True):
		linesplited = line.replace('\n', '').split(',')
		try:
			id_data = linesplited[0].encode('utf-8')
			url = linesplited[1].encode('utf-8')
			if 'http://' not in url and 'https://' not in url:
				url = 'http://' + url
		except IndexError:
			continue

		if id_data in setUrlDefined:
			continue

		urlBuffer.append((id_data, url))
		if len(urlBuffer) == bufferSize:
			tid = str(len(threadBuffer)+1)
			driver =driverBuffer.pop()
			t = Thread(target=resolveCheckinBatch, args=[tid, driver, urlBuffer])
			t.start()
			threadBuffer.append(t)
			urlBuffer = list()
		if len(threadBuffer) == threadBufferSize:
			for t in threadBuffer:
				t.join()
			threadBuffer = list()
	print colorama.Fore.GREEN, 'GG bro ;)', colorama.Fore.RESET

def main():
	print 'Small and tiny script to define the Instagram Venue/Place of Check-ins'
	define_url()

if __name__ == "__main__":
	main()




