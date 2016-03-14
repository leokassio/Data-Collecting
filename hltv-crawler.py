# -*- coding: utf-8 -*- 
# ==========================================================================================
# GNU Public License
# Dev: Kassio Machado - Brazil
# Created on 2015-02-24 - Ottawa/Canada
# Script to web scrap and collect the ammount of live viewers on a list o Stream channels
# ============================================================================================


import sys
import time
import httplib
import urllib2
import colorama
import datetime
from lxml.etree import XMLSyntaxError
from tqdm import tqdm
from HTMLParser import HTMLParser
from lxml import html

def main():
	minutes = 15
	fileout = open('hltv-stream.csv', 'a', 0)
	url = 'http://www.hltv.org'
	hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'}

	while True:
		timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		try:
			req = urllib2.Request(url, headers=hdr)
			page = urllib2.urlopen(req)
			content = page.read()
			tree = html.fromstring(content)
			elmts = tree.get_element_by_id('secondCollumn')	
			for ei, ej in zip(elmts[1][1][0:-1:3], elmts[1][1][1:-1:3]): # secondCollumn>>boc1 (second element)>>BoxDodyFadeDark(second element)
				stream = ei.getchildren()[0].items()[0][1]
				viewers = int(ej.text.replace('(', '').replace(')', ''))
				streamid = ei.getchildren()[0].items()[1][1][2:]
				kind = ei.getchildren()[0].getchildren()[0].items()[2][1].replace(' ', '-')
				country = ei.getchildren()[0].getchildren()[1].items()[0][1].replace('http://static.hltv.org//images/', '')
				line = timestamp + ',' + stream + ',' + str(viewers) + ',' + country + ',' + kind + ',' + streamid
				print line
				fileout.write(line + '\n')
			for i in tqdm(range(15 * 60), desc='waiting ' + str(minutes) + 'mins'):
				time.sleep(1)
		except lxml.etree.XMLSyntaxError:
			print 'lxml.etree.XMLSyntaxError, waiting 1 minute....'
			time.sleep(60)
		except:
			print 'Not Threated Except, waiting 1 minute...'
			time.sleep(60)	

if __name__ == "__main__":
	main()





