# -*- coding: utf-8 -*-

import sys
import os
import re

import requests
import json


ALBUM_API_PREFIX='https://api.douban.com/v2/album/'
ALBUM_PREFIX='www.douban.com/photos/album/'

INVALID_FILENAME_CHARS=u'\/:*?"<>|'

'''
sdfasdf
sdfasdf
asdfsdf
'''

args = sys.argv
albumUrl = args[1] if len(args) > 1 else 'http://www.douban.com/photos/album/157958974/?start=126'
destDir = args[2] if len(args) > 2 else '~/Downloads'

print 'url: ', albumUrl
print 'dest: ', destDir


'''
tests:
http://www.douban.com/photos/album/137490512/?start=18
http://www.douban.com/photos/album/157958974/?start=126
'''


def getAlbumId(albumUrl):
	regexPtn = '(?<=' + ALBUM_PREFIX + ')[0-9]+'
	albumId = re.search(regexPtn, albumUrl).group(0)
	# todo - null check
	print '豆瓣相册id: ', albumId
	return albumId


def encodeDict(dic, encoding):
	''' cannot handle list in a dict '''

	encoding = encoding if encoding != '' else 'utf-8'
	for key in dic.keys():
		if isinstance(dic[key], unicode):
			dic[key] = dic[key].encode(encoding)
		elif isinstance(dic[key], dict):
			dic[key] = encodeDict(dic[key], encoding)
	return dic


def getProperFilenameStr(strg):
	''' get a proper string consists of at most 15 unicode chars '''

	strgUni = strg.decode('utf-8')
	candi = ''
	i = 0
	for ch in strgUni:
		if i > 15:
			candi += '..'
			break
		if ch not in INVALID_FILENAME_CHARS:
			candi += ch.encode('utf-8')
			i += 1
	return candi



def parseResAndDownload(res, destDir):

	# generate album general info txt
	alTitle = res['album']['title']
	alAuthor = res['album']['author']['name']
	alLink = res['album']['alt']
	alDesc = res['album']['desc']
	albumId = res['album']['id']
	print alTitle + ' | ' + alAuthor + ' | ' + alLink + ' | ' + alDesc

	albumDirName = '[' + albumId + '][' + getProperFilenameStr(alTitle) + ']'
	if not os.path.isdir(albumDirName):
		os.mkdir(albumDirName)
	os.chdir(albumDirName)
	print os.getcwd()


	with open('album.info.txt', 'w+') as infoText:
		infoText.write('\n相册：' + alTitle)
		infoText.write('\n作者：' + alAuthor)
		infoText.write('\n链接：' + alLink)
		infoText.write('\n简介：' + alDesc)
		infoText.write('\n')



	# get every photo
	photos = res['photos']  # this is a list
	for i in range(0, len(photos) ):
		photos[i] = encodeDict(photos[i], '')

	for photo in photos:
		photoId = str(photo['id'])
		photoUrl = photo['large'] if 'large' in photo.keys() else photo['image']
		photoDesc = photo['desc']
		
		fname = photo['id'] + '.jpg'
		print 'downloading photo', fname, '...'
		photoRq = requests.get(photoUrl)
		with open(fname, 'wb') as photoFile:
			photoFile.write(photoRq.content)

		# append photo description in "album.info.txt"
		try:
			infoText = open('album.info.txt', 'a+')
			strg = '\n' + photoId + ': ' + photoDesc
			infoText.write(strg)
		except Exception, e:
			print 'Warning: failed to append photo info in "album.info.txt"...'
			print e

	# bye
	print '\nDownload finished, find the album in:'
	print '\t' + os.getcwd()



def downloadAlbum(albumId, destDir):

	destDir = os.path.expanduser(destDir)
	if os.path.isdir(destDir):
		os.chdir(destDir)
	else:
		print 'Warning! dest dir', destDir, 'not exist! using working dir:', os.getcwd()


	photoListApiUrl = ALBUM_API_PREFIX + albumId + '/photos?count=100'
	r = requests.get(photoListApiUrl)
	print '\nrequset status: ', r.reason
	print 'request status code: ', r.status_code

	r.encoding = 'utf-8'
	res = json.loads(r.text)
	res = encodeDict(res, 'utf-8')

	# with open('album.json', 'wb') as jsn:
	# 	jsn.write(r.content)


	try:
		print '\n', len(res['photos']), 'photos found in the album.'
		parseResAndDownload(res, destDir)
	except Exception, e:
		print 'Error! ...'
		raise e



# main
downloadAlbum(getAlbumId(albumUrl), destDir)







	