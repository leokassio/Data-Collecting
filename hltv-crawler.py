# -*- coding: utf-8 -*- 
# ==========================================================================================
# GNU Public License
# Dev: Kassio Machado - Brazil
# Created on 2015-02-24 - Ottawa/Canada
# Script to web scrap and collect the ammount of live viewers on a list o Stream channels
# ============================================================================================


import sys
import time
import colorama
import datetime
from selenium.webdriver import PhantomJS
from selenium.webdriver import Firefox

def createDriver():
	try:
		# driver = Firefox()
		driver = PhantomJS('./phantomjs')
	except:
		driver = PhantomJS()
	return driver

def main():
	fileout = open('hltv-stream.csv', 'a', 0)
	url = 'http://www.hltv.org'
	minutes = 2
	driver = createDriver()
	while True:
		timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:00')
		driver.get(url)
		elements = driver.find_elements_by_id('secondCollumn')
		for e in elements:
			for i, t in enumerate(e.find_elements_by_id('boc1')):
				if i != 1: continue
				stream = [a.get_attribute('title') for a in t.find_elements_by_tag_name('a')]
				href = [a.get_attribute('href') for a in t.find_elements_by_tag_name('a')]
				viewers = [v.text for v in t.find_elements_by_tag_name('div')[4:-1:2]]
				kind = [img.get_attribute('src') for img in t.find_elements_by_tag_name('img')[1::2]]
				country = [img.get_attribute('src') for img in t.find_elements_by_tag_name('img')[2::2]]
				for s, v, h, k, c in zip(stream, viewers, href, kind, country):
					v = v.replace('(', '').replace(')', '')
					k = k.replace('http://static.hltv.org//images/', '')
					c = c.replace('http://static.hltv.org//images/', '')
					print colorama.Fore.CYAN+timestamp, s, v, h, k, c, colorama.Fore.RESET	
					fileout.write(timestamp + ',' + s + ',' + v + ',' + h + ',' + k + ',' + c + '\n')
		print colorama.Fore.YELLOW + 'Waiting', minutes, 'minutes' + colorama.Fore.RESET	
		try:
			time.sleep(60 * minutes)
		except:
			fileout.close()
			

if __name__ == "__main__":
	main()





