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
from lxml import html
from tqdm import tqdm
from lxml.etree import XMLSyntaxError
from HTMLParser import HTMLParser
from prettytable import PrettyTable

def main():
	minutes = 5
	fileout = open('hltv-crawler-streams.csv', 'a', 0)
	url = 'http://www.hltv.org'
	hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'}

	while True:
		timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		pttb = PrettyTable(['Time', 'Stream', 'Viewers', 'Country', 'Class'])
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
				country = ei.getchildren()[0].getchildren()[1].items()[0][1].replace('http://static.hltv.org//images/flag/', '')
				country = country.replace('.gif', '').upper()
				line = timestamp + ',' + stream + ',' + str(viewers) + ',' + country + ',' + kind + ',' + streamid
				fileout.write(line + '\n')
				pttb_data = [timestamp, stream, viewers, country, kind]
				pttb.add_row(pttb_data)
			print pttb
			for i in tqdm(range(minutes * 60), desc='waiting ' + str(minutes) + 'mins'):
				time.sleep(1)
		except lxml.etree.XMLSyntaxError:
			print pttb
			print 'lxml.etree.XMLSyntaxError, waiting 1 minute....'
			time.sleep(60)
		except:
			print pttb
			print 'Not Threated Except, waiting 1 minute...'
			time.sleep(60)	

if __name__ == "__main__":
	main()





