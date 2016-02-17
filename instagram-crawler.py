import sys
import selenium
import colorama
from tqdm import tqdm
from selenium.webdriver import Firefox
from selenium.webdriver import PhantomJS

cityName = sys.argv[1]
basic_file_path = '-instagram-checkin.csv'

inputfile = open(cityName + basic_file_path, 'r')
numLines = sum(1 for line in inputfile)
inputfile.seek(0)

setUrlDefined = set()
try:
	outputfile = open(cityName + '-instagram-output.csv', 'r')
	for line in outputfile:
		linesplited = line.replace('\n', '').split(',')
		setUrlDefined.add(linesplited[0])
	outputfile.close()
except IOError:
	pass
outputfile = open(cityName + '-instagram-output.csv', 'a', 0)

print colorama.Back.RED+colorama.Fore.YELLOW+str(len(setUrlDefined))+' URLs already defined! Lets Rock more now...'+colorama.Back.RESET+colorama.Fore.RESET

driver = PhantomJS('./phantomjs') # in case of PhantomJS not available, we can use Firefox
for line in tqdm(inputfile, total=numLines, desc='Crawling Instagram', leave=True):
	try:
		idtweet, url = line.replace('\n', '').split(',')
		if idtweet in setUrlDefined:
			continue
	except IndexError:
		print colorama.Fore.RED, 'Corrupted Line', colorama.Fore.RESET
		continue
	try:
		driver.get(url)
		placetag = driver.find_element_by_class_name('_kul9p')
		placeurl = placetag.get_attribute('href').encode('utf-8')
		placename = placetag.get_attribute('title').encode('utf-8')

		usernametag = driver.find_element_by_class_name('_4zhc5')
		username = usernametag.get_attribute('title').encode('utf-8')
		
	except selenium.common.exceptions.NoSuchElementException:
		try:
			error = driver.find_element_by_class_name('error-container')
			print colorama.Fore.RED, 'Sample Not Available Anymore', colorama.Fore.RESET
			outputfile.write(idtweet + ',' + url + ',404\n')
			continue
		except selenium.common.exceptions.NoSuchElementException:
			print colorama.Fore.RED, 'No Coords Available', colorama.Fore.RESET
			outputfile.write(idtweet + ',' + url + ',NoCoords\n')
			continue
	except AttributeError:
		print colorama.Fore.RED + 'No place link ¯\_(ツ)_/¯' + colorama.Fore.RESET
		outputfile.write(idtweet + ',' + url + ',NoPlaceLink\n')
		continue
	
	try:
		outputfile.write(idtweet + ',' + url + ',' + placeurl + ',' + placename + ',' + username + '\n')
		print colorama.Fore.CYAN, idtweet, url
		print colorama.Fore.YELLOW, placeurl, colorama.Fore.RESET
	except UnicodeDecodeError:
		print placeurl, placename, username







