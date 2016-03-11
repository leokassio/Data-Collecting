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
from tqdm import tqdm
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import PhantomJS

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
	driver.set_page_load_timeout(30)
	while True:
		timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:00')
		try:
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
						pcolor = colorama.Fore.CYAN
						if c == 'flag/br.gif':
							pcolor = colorama.Fore.YELLOW
						elif k == 'mod_csgo_caster.png':
							pcolor = colorama.Fore.RED
						elif k == 'mod_csgo_player.png':
							pcolor = colorama.Fore.BLUE
						elif k == 'mod_csgo_female.png':
							pcolor = colorama.Fore.MAGENTA
						else:
							pcolor = colorama.Fore.WHITE

						print pcolor + timestamp, s, v, h, k, c, colorama.Fore.RESET + colorama.Back.RESET	
						fileout.write(timestamp + ',' + s + ',' + v + ',' + h + ',' + k + ',' + c + '\n')
		except TimeoutException:
			print colorama.Back.RED + colorama.Fore.WHITE + 'Error on loading ' + url + colorama.Fore.RESET + colorama.Back.RESET + ' - waiting 1 minute to try again'
			time.sleep(60)
			continue
		print colorama.Fore.YELLOW
		for i in tqdm(range(60 * minutes), desc='Waiting ' + str(minutes) + ' mins'):
			time.sleep(1)
		print colorama.Fore.RESET
			

if __name__ == "__main__":
	main()





