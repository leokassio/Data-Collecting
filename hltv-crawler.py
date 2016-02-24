# -*- coding: utf-8 -*- 
# ==========================================================================================
# GNU Public License
# Dev: Kassio Machado - Brazil
# Created on 2015-02-24 - Ottawa/Canada
# Script to web scrap and collect the ammount of live viewers on a list o Twitch channels
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
	timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:00')
	while True:
		driver.get(url)
		elements = driver.find_elements_by_id('secondCollumn')
		for e in elements:
			for i, t in enumerate(e.find_elements_by_id('boc1')):
				if i != 1: continue
				stream = [a.get_attribute('title') for a in t.find_elements_by_tag_name('a')]
				viewers = [v.text for v in t.find_elements_by_tag_name('div')[4:-1:2]]
				for s, v in zip(stream, viewers):
					v = v.replace('(', '').replace(')', '')
					print colorama.Fore.CYAN+timestamp, s, v, colorama.Fore.RESET	
					fileout.write(timestamp + ',' + s + ',' + v + '\n')
		print colorama.Fore.YELLOW + 'Waiting', minutes, 'minutes' + colorama.Fore.RESET	
		try:
			time.sleep(60 * minutes)
		except:
			fileout.close()
			







if __name__ == "__main__":
	main()