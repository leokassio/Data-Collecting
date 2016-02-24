# -*- coding: utf-8 -*- 
# ============================================================================================
# GNU Public License
# Dev: Kassio Machado - Brazil
# Created on 2015-12-11 - Ottawa/Canada
# Simple script to collect the ammount of live viewers on a list o Twitch channels
# ============================================================================================

import sys
import datetime
import time
import colorama
import twitch.api.v3 as twitchpy

args = sys.argv
filename = args[1]
fileout = open(filename + '.data', 'a', 0)

# TODO: tranfers the list of channel to an external configuration file.
twitch_channels = list() 
twitch_channels.append('ESL_Bida')
twitch_channels.append('esl_csgo')
twitch_channels.append('esl_csgo_pl')
twitch_channels.append('stormstudio_csgo_ru')
twitch_channels.append('ESL_YTGlitchGamer')
twitch_channels.append('esl_esmaroc')
twitch_channels.append('esl_csgoitalia')
twitch_channels.append('esl_gplaytv')
twitch_channels.append('esl_clanmystik')
twitch_channels.append('esl_csgo_es')

while True:
	for ch in twitch_channels:
		stream = twitchpy.streams.by_channel(ch)
		if stream['stream'] != None:
			timestamp = datetime.datetime.now()
			stream['timestamp'] = timestamp
			del stream['stream']['preview']
			del stream['_links']
			del stream['stream']['video_height']
			del stream['stream']['_links']
			del stream['stream']['average_fps']
			del stream['stream']['channel']['video_banner']
			del stream['stream']['channel']['logo']
			del stream['stream']['channel']['partner']
			del stream['stream']['channel']['display_name']
			del stream['stream']['channel']['delay']
			del stream['stream']['channel']['_links']
			del stream['stream']['channel']['broadcaster_language']
			del stream['stream']['channel']['background']
			del stream['stream']['channel']['banner']
			del stream['stream']['channel']['language']
			del stream['stream']['channel']['url']
			del stream['stream']['channel']['created_at']
			del stream['stream']['channel']['mature']
			del stream['stream']['channel']['profile_banner_background_color']
			del stream['stream']['channel']['_id']
			del stream['stream']['channel']['profile_banner']
			del stream['stream']['channel']['game']
			print timestamp.strftime('%H:%M:%S (%d-%m)'), stream['stream']['channel']['name'], 'Viewers:', stream['stream']['viewers'], 'playing:', stream['stream']['game']
			time.sleep(2)
			fileout.write(str(stream) + '\n')
		else:
			time.sleep(4)




