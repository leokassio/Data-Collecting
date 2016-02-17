# -*- coding: utf-8 -*-

import json
import colorama

fileinput = open('foursquare-categories.json', 'r')

jsondata = fileinput.readline()
parsed = json.loads(jsondata)

totalclasses = 0
dictcategories = dict()

for catindex in range(len(parsed['response']['categories'])):
	categ = parsed['response']['categories'][catindex]
	
	categoryname = categ['name']
	print colorama.Fore.RED+categoryname+colorama.Fore.RESET
	dictcategories[categoryname] = set()
	dictcategories[categoryname].add(categoryname)
	
	for c in categ['categories']:
		print '\t' + colorama.Fore.YELLOW + c['name'] + colorama.Fore.RESET
		dictcategories[categoryname].add(c['name'])
		for c2 in c['categories']:
			print '\t\t' + colorama.Fore.CYAN + c2['name'] + colorama.Fore.RESET
			dictcategories[categoryname].add(c2['name'])
			for c3 in c2['categories']:
				print '\t\t\t' + colorama.Fore.WHITE + c3['name'] + colorama.Fore.RESET
				dictcategories[categoryname].add(c3['name'])
	totalclasses += len(dictcategories[categoryname])
	# print categoryname, str(dictcategories[categoryname])


