# -*- coding: utf-8 -*- 
# ============================================================================================
# Kassio Machado - GNU License - 2016-02-12 
# PhD candidate on Science Computing - UFMG/Brazil
# Crawler to visit Instagram urls and get venues registered on dataset of check-ins
# the data if provided in an CSV file and exported in other CSV file.
# The crawler used selenium to perform the HTML/JavaScript parsing
# ============================================================================================

import sys
import time
import httplib
import colorama 
import selenium
import datetime
import urllib2
from tqdm import tqdm
from threading import Thread
from Queue import Queue
from selenium.webdriver import Firefox
from selenium.webdriver import PhantomJS

reload(sys)  
sys.setdefaultencoding('utf8')

def createDriver():
	try:
		driver = PhantomJS('./phantomjs')
	except:
		driver = PhantomJS()
	return driver 

def resolveCheckin(driver, id_data, url):
	try:
		# print 'resolving', url
		driver.get(url) 
		placetag = driver.find_element_by_class_name('_kul9p')
		placeurl = placetag.get_attribute('href').encode('utf-8')
		placename = placetag.get_attribute('title').encode('utf-8')

		usernametag = driver.find_element_by_class_name('_4zhc5')
		username = usernametag.get_attribute('title').encode('utf-8')
		data = id_data + ',' + url + ',' + placeurl + ',' + placename + ',' +  username
		return data
	except selenium.common.exceptions.NoSuchElementException:
		try:
			error = driver.find_element_by_class_name('error-container')
			return id_data + ',' + url + ',' + 'not-available'
		except selenium.common.exceptions.NoSuchElementException:
			pass
	except AttributeError:
		pass
	except httplib.BadStatusLine:
		pass
	except urllib2.URLError, e:
		print url, '- url open error'
		time.sleep(1)
	except Exception, e:
		print 'generic exception', str(e)
	return None # id_data + ',' + url + ',' + 'None'

def resolveCheckinRun(driver, urlBuffer, saveBuffer):
	while True:
		try:
			item = urlBuffer.get(timeout=30)
			id_data, url = item
			line = resolveCheckin(driver, id_data, url)
			if line != None:
				saveBuffer.put_nowait(line)
			urlBuffer.task_done()
		except Queue.Empty:
			break
	print 'Finishing thread...'
	driver.quit()

def saveCheckinRun(outputFilename, saveBuffer):
	f = open(outputFilename, 'a', 0)
	while True:
		r = saveBuffer.get()
		f.write(r + '\n')
		saveBuffer.task_done()
	f.close()

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
	urlBufferSize = 1000
	args = sys.argv[1:]
	input_file_path = args[0]
	try:
		threadBufferSize = int(args[1])
	except:
		print colorama.Fore.RED, 'Default Thread Pool Size: 10', colorama.Fore.RESET
		threadBufferSize = 10
	
	outputFilename = 'output/' + input_file_path.replace('.csv', '-output.csv')
	
	setUrlDefined = loadDefinedPlaces(outputFilename)
	print colorama.Back.RED+colorama.Fore.YELLOW+str(len(setUrlDefined))+' URLs already defined! Lets Rock more now...'+colorama.Back.RESET+colorama.Fore.RESET
	
	try:
		input_file = open(input_file_path, 'r')						# file with url checkins  to be resolved
		numLines = sum(1 for line in input_file)		# counting lines on file
		input_file.seek(0) 								# restarting the cursor of file
	except IOError:
		print colorama.Fore.RED+colorama.Back.WHITE+'   NO PLACE DATASET (⊙_☉) IMPOSSIBLE TO PROCEED...  '+colorama.Fore.RESET+colorama.Back.RESET
		exit()

	urlBuffer = Queue(maxsize=urlBufferSize) 	
	saveBuffer = Queue()
	
	t = Thread(target=saveCheckinRun, args=[outputFilename, saveBuffer])
	t.daemon = True
	t.start()
	for i in range(threadBufferSize):
		driver = createDriver() # in case of PhantomJS not available, we can use Firefox()
		t = Thread(target=resolveCheckinRun, args=[driver, urlBuffer, saveBuffer])
		t.daemon = True
		t.start()

	for line in tqdm(input_file, desc='Defining URLs', total=numLines, leave=True, dynamic_ncols=True):
		linesplited = line.replace('\n', '').split(',')
		try:
			id_data = linesplited[0].encode('utf-8')
			if id_data in setUrlDefined:
				continue
			url = linesplited[1].encode('utf-8')
			if 'http://' not in url and 'https://' not in url:
				url = 'http://' + url
		except IndexError:
			continue
		urlBuffer.put((id_data, url))
	urlBuffer.join()
	saveBuffer.join()
	print colorama.Fore.GREEN, 'GG bro ;)', colorama.Fore.RESET

def main():
	print 'Small and tiny script to define the Instagram Venue/Place of Check-ins'
	define_url()

if __name__ == "__main__":
	main()




