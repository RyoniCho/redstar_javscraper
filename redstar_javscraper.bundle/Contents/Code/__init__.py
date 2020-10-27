# -*- coding: utf-8 -*-
import re
import random
import urllib
import urllib2
import urlparse
import json
import ssl
from datetime import datetime
from cStringIO import StringIO
import inspect

HDR = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

HDR_javdb = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8',
		'referer': 'www.google.com',
       'Connection': 'keep-alive'}

def Papago_Trans(txt,lang='en'):
	# 번역언어:	# ko	한국어	# en	영어	# ja	일본어	# zh-CN	중국어 간체	# zh-TW	중국어 번체	# vi	베트남어
	# id	인도네시아어	# th	태국어	# de	독일어	# ru	러시아어	# es	스페인어	# it	이탈리아어	# fr	프랑스어

	# Log('===========> 파파고 설정(PapagoUSE): ' + str(Prefs['papago_use']))
	# Log('===========> 파파고 키값(PapagoKey): ' + str(Prefs['papagokey']))
	if (str(Prefs['papago_use']) == 'False'):
		# Log('### 파파고 사용 안함 체크됨(Papago Not use checked) ###')
		return txt
	if (str(Prefs['papagokey']) == 'None' ):
		# Log('### 파파고 키가 빈 값임(Papago key empty) ###')
		return txt

	try:
		# 환경변수에 입력한 파파고 키를 랜덤으로 추출해 사용함
		# 환경변수에는 key,secret key2,secret2 .... 으로 입력되어야 함
		# Log('### PapagoKEY : ' + str(Prefs['papagokey']))
		client_key=str(Prefs['papagokey'])
		papagokey = client_key.split(' ')
		get_papagokey = random.choice(papagokey)
		client_key_array = get_papagokey.split(',')
		client_id = client_key_array[0]
		client_secret = client_key_array[1]
		# Log('### ID: ' + str(client_id) + ' Secret: ' + str(client_secret))

		source_lang =  lang
		target_lang = "ko"
		encText = txt
		# Log('### Trans Original TXT: ' + encText)
		data = "source=" + source_lang + "&target=" + target_lang + "&text=" + encText
		url = "https://openapi.naver.com/v1/papago/n2mt"
		request = urllib2.Request(url)
		request.add_header("X-Naver-Client-Id", client_id)
		request.add_header("X-Naver-Client-Secret", client_secret)
		response = urllib2.urlopen(request, data=data.encode("utf-8"), timeout=int(Prefs['timeout']))
		rescode = response.getcode()
		if (rescode == 200):
			response_body = response.read()
			nResult = String_slice(response_body, 'translatedText":"', '","engineType')
			# Log('#### Papago Trans Result : ' + str(response_body))
			# Log('####  Trans Result Cut : ' + str(nResult))
			return nResult
		else:
			print("Error Code:" + rescode)
			return txt
	except:
		# Log('papago Exception')
		return txt

def String_slice(nStr,nStartstr,nEndstr):
	# 문자열 자르기(입력: 원본, 시작문자열, 끝 문자열)String slice. org: nStr  findString: nStartstr   Endstring: nEndstr
	nStr_find=''

	if (nStr == ''):
		return ''
	if (nStartstr == ''):
		nStartstr=0
	else:
		nStr_find = nStr.find(nStartstr)
		if(nStr_find == -1 ):
			return ''
	nStartstr = nStr_find + len(nStartstr)

	if (nEndstr == ''):
		nEndstr=len(nStr)
	nEndstr = nStr.find(nEndstr, nStartstr)
	nResult = nStr[nStartstr:nEndstr].strip() # .strip()하면 개행문자를 모두 제거해줌
	# Log('#### StringSlice StartPos : ' + str(startpos) + ' EndPos: ' + str(endpos) + ' nResult: ' + str(nResult) )
	return nResult

def Extract_str(nStr,nStartstr,nEndstr):
	# nStr: 원본 문자열
	# nStartstr: 시작 문자열
	# nEndstr: 끝 문자열
	# 시작~끝 문자열로 자른 뒤 a href의 문자열을 추출해 배열로 리턴함
	# ex> ABC, DEF, GHI값을 배열로 반환
	# <span id = "performer" >
	# <a href = "/digital/videoa/-/list/=/article=actress/id=1047128/">ABC</a>
	# <a href = "/digital/videoa/-/list/=/article=actress/id=1042219/">DEF</a>
	# <a href = "/digital/videoa/-/list/=/article=actress/id=1051357/">GHI</a>
	# </td >

	nStr=String_slice(nStr,nStartstr,nEndstr)
	nNotfound=nStr.find('----')
	nFound=nStr.find('a href')
	nResult=[]

	if (nNotfound == -1 ):
		if (nFound <> -1):
			sTemp=nStr.split('a href')
			j = len(sTemp)
			for i in range(1, j):
				# Log('Before Cut: ' + sTemp[i])
				nCut=String_slice(sTemp[i],'>','<')
				nResult.append(nCut)
				# Log('After Cut: ' + nCut)

			return nResult
	return #Return 결과는 None

def Extract_imgurl(nStr,nStartstr,nEndstr,hreforsrc='src'):
	# nStr: 원본 문자열
	# nStartstr: 시작 문자열
	# nEndstr: 끝 문자열
	# 시작~끝 문자열로 자른 뒤 이미지 URL을 모두 반환함
	# Log('Original  Str: ' + nStr)
	FindSplittxt=''

	nStr=String_slice(nStr,nStartstr,nEndstr)
	nNotfound=nStr.find('----')
	if (hreforsrc == 'src'):
		FindSplittxt='img src'
		Log('Extract from "img src"')
	elif(hreforsrc == 'href'):
		FindSplittxt = 'href'
		Log('Extract from "href"')
	elif(hreforsrc == 'data-original'):
		FindSplittxt = 'data-original'
		Log('Extract from "data-original"')
	nFound = nStr.find(FindSplittxt)
	nResult=[]
	if (nNotfound == -1 ):
		if (nFound <> -1):
			sTemp=nStr.split(FindSplittxt)
			j = len(sTemp)
			# Log('Length: ')
			# Log(int(j))
			for i in range(1, j):
				# Log('Before Cut: ' + sTemp[i])
				nCut=String_slice(sTemp[i],'="','"')
				if (nCut.find('preview-video') == -1 ):
					nResult.append(nCut)
				Log('Extract_url  After Cut: ' + nCut)
			return nResult
	return #Return 결과는 None

# def Extract_Actor_Name_URL(nStr,nStartstr,nEndstr):
# 	## javbus에서 배우명과 배우 이미지를 가져오는데 사용하는 함수
# 	nStr=String_slice(nStr,nStartstr,nEndstr)
# 	nFound=nStr.find('avatar-waterfall')
# 	nResult=[]
# 	if (nNotfound == -1 ):
# 		if (nFound <> -1):
# 			sTemp=nStr.split('</a>')
# 			j = len(sTemp)
# 			for i in range(1, j):
# 				Log('Before Cut: ' + sTemp[i])
# 				nURL=  Regex(r'<img src="(.*)" ').search(sTemp[i])
# 				nResult.append(nURL)
# 				nName=  Regex(r'title="(.*)"').search(sTemp[i])
# 				nResult.append(nName)
# 				Log('nURL: ' + nURL + ' nName: ' + nName)
# 			return nResult
# 	return #Return 결과는 None

def Start():
	HTTP.CacheTime = 0

def detailItem(root,selector):
	elements = root.xpath(selector)
	if len(elements) > 0:
		text = elements[0].text_content().strip()
		# Log(' DetailItem Function Text: ' + text)
		if "----" in text:
			return None
		return elements[0].text_content().strip()
	return None

def Get_actor_info(nEntity):
	# hentaku	홈페이지에서	배우정보를	가져옴(DMM의	경우만.r18은	페이지에	배우	정보	나옴)
	if (nEntity == ''):
		return
	Log('nEntity(Search Actor String) : ' + nEntity)
	Search_URL = 'https://hentaku.co/search/'
	post_values = {'search_str': nEntity}
	searchResults = HTTP.Request(Search_URL, values=post_values, timeout=int(Prefs['timeout'])).content
	Log('############# Actor Info from Hentaku ##############')
	# Log(searchResults)
	nResult=[]
	if (searchResults == '' or searchResults.find('class="avstar_wrap"') == -1):
		# 리턴값이 없을 경우
		nResult.append('') #image url
		nResult.append(Papago_Trans(nEntity,'ja')) # kor name
		nResult.append(Papago_Trans(nEntity,'en')) # eng name
		Log('Actor Return not found')
	else:
		# 검색결과 존재시
		nStr = String_slice(searchResults, '<s_article_rep>', '</s_article_rep>')
		# Log(nStr)
		nimgurl = Extract_imgurl(nStr, 'avstar_wrap', '</div>')
		Log('Actor image: ' + nimgurl[0])
		if (nimgurl is None):
			nResult[0]=''
		else:
			nResult.append(nimgurl[0])
		nResult.append(String_slice(nStr, 'px;">', ' /'))
		nResult.append(String_slice(nStr, ' / ', ' /'))
		Log('Actor info  #img:' + nResult[0] + '  Name_kor: ' + nResult[1] + '  Name_eng: '+nResult[2] )
	return nResult

def Get_search_url(SEARCH_URL, txt, reqMode='GET'):
	con = ''
	try:
		if (reqMode == 'POST'):
			# Log('Request is POST')
			data = {'search_str': txt}
			Log('POST SearchURL: ' + SEARCH_URL + ' data: ' + txt)
			req = urllib2.Request(SEARCH_URL, data)
		else:
			# Log('Request is GET')
			encodedId = urllib2.quote(txt)
			url = SEARCH_URL + encodedId
			Log('GET SearchURL: ' + url)
			req = urllib2.Request(url)
		try:
			con = urllib2.urlopen(req,timeout=int(Prefs['timeout']))
			Log('URL Open Success')
		except urllib2.URLError as e:
			Log(e.reason)
		web_byte = con.read()
		# Log('webbyte completed')
		webpage = web_byte.decode('utf-8')
		# Log('webpage : ' + str(webpage))
		Log("검색결과 가져옴(Got search result)")
		return webpage
	except:
		Log("검색결과 Search Result: exception")
	return ''

def poombun_check(txt):
	# 입력 문자에서 품번만 추출해 리턴함
	# (?i) 대소문자포함
	#  \w{2,}-[0-9]{3,}  xxx-yyy 품번 구분
	#  \w{2,} [0-9]{3,}  xxx yyy 품번 구분
	#  (?i)(FC2).*(PPV)-[0-9]{3,}   fc2ppv-0000 / fc2-ppv-00000 (단, scanner에서 하이픈 두개일때 뒤는 자르므로 파일명을 FC2PPV-0000으로 해야함
	# (?i)(carib.*)-[0-9]{3,} carib-9999 / caribbeancom-9999-9999 (carib는 하이픈 두개도 됨)

	# (?i)(tokyo.*)-n[0-9]{3,} / tokyohot-n000
	# (?i)((carib.*)|(1pondo.*)|\w{2,}|((FC2).*(PPV)))-[0-9]{3,}

	# (?i)(tokyo.*)-n[0-9]{3,}|((carib.*)|(1pondo.*)|\w{2,}|((FC2).*(PPV)))-[0-9]{3,} 위 두개를 합친 표현식
	Log('### Poombun input: ' + txt)
	if (txt <> ''):
		txt = txt.replace(' ', '-')
		# Log('txt: ' + txt)
		pattern = '(?i)(tokyo.*)-n[0-9]{3,}|((carib.*)|(1pondo.*)|\w{2,}|((FC2).*(PPV)))-[0-9]{3,}'
		nMatch = re.search(pattern, txt)
		# Log(nMatch)
		if (nMatch is not None):
			Log('### Poombun output: ' + nMatch.group(0))
			return nMatch.group(0)
	Log('@@@ Poombun is wrong')
	return txt

def uncensored_check(txt):
	# 파일명에 노모 포함인지 여부 확인

	if (txt is None): return 0
	txt=txt.upper()
	txt=urllib.unquote(txt).decode('utf8')
	Log('Uncensored check txt: ' + txt	)

	if (str(Prefs['uncensored_class']) == 'True'):
		if ((txt.find('UNC') > -1) or (txt.find('노모') > -1) ):
			return 1
	return 0

		# nUnctxt = str(Prefs['uncensored_class']).split(' ')
		# j = len(nUnctxt)
		# for i in range(0, j):
		# 	Log('Uncensored text Check: ' + nUnctxt[i])
		# 	a=txt.find(nUnctxt[i])
		# 	Log('a: ' + str(a))
		# 	if (a > -1):
		# 		Log('Text Found!')
		# 		return 1
		# return 0

class redstar_javscraper(Agent.Movies):
	name = 'redstar_javscraper'
	languages = [Locale.Language.English,]
	primary_provider = True
	accepts_from = ['com.plexapp.agents.localmedia']

	# def Log(self, message, *args):
	# 	if Prefs['debug']:
	# 		Log(message, *args)

	def search(self, results, media, lang):
		#https://www.javlibrary.com/
		#https://javdb.com/
		# https://pornav.co/  fc2등 노모 검색
		# https://www.jav321.com/
		# https://aa9969.com/ko/ #7mmtv

		nResult=0
		Log("####### Start search #########")
		Log('option Check dmm: ' + str(Prefs['dmm_use']))
		Log('option check r18: ' + str(Prefs['r18_use']))
		Log('option check javbus: ' + str(Prefs['javbus_use']))
		Log('option check pornav: ' + str(Prefs['pornav_use']))
		Log('option check javdb: ' + str(Prefs['javdb_use']))

		media.name=poombun_check(media.name).replace(' ','-').upper()

		if (str(Prefs['dmm_use']) == 'True'):
			nResult=self.dmm_search(results, media, lang)
			# Log('dmm result: ' + str(nResult))
		if (str(Prefs['r18_use']) == 'True' and nResult == 0):
			nResult=self.r18_search(results, media, lang)
			# Log('r18 result: ' + str(nResult))
		if (str(Prefs['javbus_use']) == 'True' and nResult == 0):
			nResult=self.javbus_search(results, media, lang)
			# Log('jabus result: '  + str(nResult))
		if (str(Prefs['pornav_use']) == 'True' and nResult == 0):
			nResult=self.pornav_search(results, media, lang)
			# Log('pornav result: '  + str(nResult))
		if (str(Prefs['javdb_use']) == 'True' and nResult == 0):
			nResult=self.javdb_search(results, media, lang)
			# Log('javdb result: '  + str(nResult))
		if (nResult == 0):
			Log('xxx Search failed on all sites. xxx')
		Log('search end')

	def update(self, metadata, media, lang):

		Log("####### Start Update #########")
		nTitle=media.title
		Log('MediaTitle: ' + nTitle)
		# name = '[' + id + ']§' + title + '§' + 'DMMa' + '§' + uncResult
		# 0: ID값[OAE-101]   /   1: 타이틀명 PerfectBody..   /  2: 검색사이트 구분자   /  3: 노모유모확인
		if (nTitle.find('§') <> -1):
			nIDs = nTitle.split('§')
			nOrgID = nIDs[0]
			nSite = nIDs[2]
			Log('### Uncensored: ' + nIDs[3] + ' Update site : ' + nSite)
			if (nIDs[3] == 'U'):
				metadata.content_rating = '노모'
				Log('ContentRating: 노모')
			if (nIDs[3] == 'C'):
				metadata.content_rating = '유모'
				Log('ContentRating: 유모')
		else:
			nSite=' '
			nOrgID=nTitle

		if (str(Prefs['dmm_use']) == 'True' and ((nSite == 'DMMa') or (nSite == 'DMMo') or (nSite == ' '))):
			nResult=self.dmm_update(metadata, media, lang, nOrgID)
			Log('dmm result: ' + str(nResult))
		elif (str(Prefs['r18_use']) == 'True' and ((nSite == 'r18')or (nSite == ' '))):
			nResult=self.r18_update(metadata, media, lang, nOrgID)
			Log('r18 result: ' + str(nResult))
		elif (str(Prefs['javbus_use']) == 'True' and ((nSite == 'javbus')or (nSite == ' '))):
			nResult=self.javbus_update(metadata, media, lang, nOrgID)
			Log('jabus result: ' + str(nResult))
		elif (str(Prefs['pornav_use']) == 'True' and ((nSite == 'pornav')or (nSite == ' '))):
			nResult=self.pornav_update(metadata, media, lang, nOrgID)
			Log('pornav result: ' + str(nResult))
		elif (str(Prefs['javdb_use']) == 'True' and ((nSite == 'javdb')or (nSite == ' '))):
			nResult=self.javdb_update(metadata, media, lang, nOrgID)
			Log('javdb result: ' + str(nResult))
		Log("####### End update #########")

	def dmm_search(self,results,media,lang):
		##############################
		###### dmm video 검색  ########
		##############################
		Log('##### Start dmm video search #####')
		SEARCH_URL = 'https://www.dmm.co.jp/digital/videoa/-/list/search/=/?searchstr='

		org_id = media.name
		if (org_id == ''): return 0
		if (org_id.find('DV-') > -1):
			release_id = org_id.replace('-', '0')
		else:
			release_id=org_id.replace('-','00')

		Log('******* DMM Video 검색 시작(Media search start) ****** ')
		Log("### Release ID:    " + str(release_id) + ' org_id: ' + str(org_id))  # Release ID: IPZ00929 org_id: IPZ-929
		searchResults = Get_search_url(SEARCH_URL, release_id)
		if (searchResults <> ''):
			nResult = searchResults.find('<ul id="list">') #검색결과 없음
			# Log(searchResults)
			# Log(nResult)
			if (nResult <> -1):
				Log('##### dmm Video Result Found #####')
				if (uncensored_check(media.filename) == 1):
					uncResult = 'U'
				else:
					uncResult = 'C'
				Log('### UNC:' + uncResult)
				searchResults=String_slice(searchResults,'<ul id="list">','(function()')
				content_id = String_slice(searchResults,'content_id":"','"')
				Log(' Content_id: ' + content_id)
				title = String_slice(searchResults, 'class="txt">', '<')
				id= org_id
				name= '[' + id + ']§' + title + '§' + 'DMMo' + '§' + uncResult
				score=100
				results.Append(MetadataSearchResult(id=content_id, name=name, score=score, lang=lang))
				Log('##Search Update Result ==> id: ' + content_id + ' name: ' + name + ' score : ' + str(score))
				return 1
			else:
				Log('DMM Video result Not found')
		else:
			Log('DMM Video result not found1')

		###### dmm Amateur 검색  ########
		SEARCH_URL = 'https://www.dmm.co.jp/digital/videoc/-/list/search/=/?searchstr='
		release_id = org_id.replace('-','')
		Log("org_id ID:    " + str(org_id) + " release_id: " + str(release_id))
		Log('******* DMM Amateur 검색 시작(Media search start) ****** ')
		searchResults = Get_search_url(SEARCH_URL, release_id)
		# Log(searchResults)
		if (searchResults <> ''):
			nResult = searchResults.find('id="list"') #검색 결과 있을때 이 텍스트가 있음
			Log(nResult)
			if (nResult <> -1):
				Log('##### dmm Amateur Result Found #####')
				if (uncensored_check(media.filename) == 1):
					uncResult = 'U'
				else:
					uncResult = 'C'
				Log('### UNC:' + uncResult)
				searchResults=String_slice(searchResults,'<ul id="list">','(function()')
				content_id = String_slice(searchResults,'content_id":"','"')
				Log('amature ContentID: ' + content_id)
				id= org_id
				title=String_slice(searchResults,'class="txt">','<')
				name = '[' + id + ']§' + title + '§' + 'DMMa' + '§' + uncResult
				score=100
				results.Append(MetadataSearchResult(id=content_id, name=name, score=score, lang=lang))
				return 1
		else:
			Log('DMM Amateur result Not found')
			return 0

	def r18_search(self,results,media,lang):
		##############################
		######### r18 검색  ##########
		##############################
		Log('##### Start r18 video search #####')
		SEARCH_URL = 'https://www.r18.com/common/search/searchword='
		org_id = media.name
		release_id=org_id

		Log('******* r18 미디어 검색 시작(r18 Media search start) ****** ')
		Log("Release ID:    " + str(release_id) + ' org_id: ' + org_id)
		try:
			encodedId = urllib2.quote(release_id)
			url = SEARCH_URL + encodedId
			searchResults = HTML.ElementFromURL(url, timeout=int(Prefs['timeout']))
			Log("검색결과 가져옴(Got search result)")
		except:
			return 0
		if (searchResults <> None):
			# Log('##### r18 Result Found #####')
			findcontent=0
			for searchResult in searchResults.xpath('//li[contains(@class, "item-list")]'):
				if (uncensored_check(media.filename) == 1):
					uncResult = 'U'
				else:
					uncResult = 'C'
				Log('### UNC:' + uncResult)
				findcontent=1 #xpath에 내용이 검색되면 값을 1로
				# Log(searchResult.text_content())
				content_id = searchResult.get("data-content_id")
				id = searchResult.xpath('a//p//img')[0].get("alt")
				id = id.upper()
				title = searchResult.xpath('a//dl//dt')[0].text_content()
				if title.startswith("SALE"):
					title = title[4:]
				Log(id + " : " + title)
				name = '[' + id + ']§' + title + '§' + 'r18' + '§' + uncResult
				score = 100 - Util.LevenshteinDistance(id.lower(), release_id.lower())
				results.Append(MetadataSearchResult(id=content_id, name=name, score=score, lang=lang))
				Log('ID: ' + content_id + ' name: ' + "[" + id + "] " + title)
			if (findcontent==0):
				Log('@@@ r18 검색결과 없음(Result not found)')
				return 0
			else:
				results.Sort('score', descending=True)
				Log('******* r18 검색 완료(Search Completed) ****** ')
				return 1
		else:
			Log('@@@ r18 검색결과 없음(Result not found)')
			return 0

	def javbus_search(self, results, media, lang):
		###############################
		##### javbus video 검색  #######
		###############################
		Log('##### Start javbus video search #####')
		SEARCH_URL = 'https://www.javbus.com/search/'
		org_id = media.name
		release_id=org_id

		# Log('******* javbus Video 검색 시작(Media search start) ****** ')
		Log("Release ID:    " + str(release_id))
		try: searchResults=HTTP.Request(SEARCH_URL + release_id, timeout=int(Prefs['timeout'])).content # post로 보낼경우 value={'aaa' : 내용} 으로 보냄
		except:	return 0
		# Log(searchResults)
		if (searchResults <> ''):
			nResult = searchResults.find('<div id="waterfall">')  # 검색결과 확인
			# Log(searchResults)
			# Log(nResult)
			if (nResult <> -1):
				Log('##### javbus Video Result Found #####')
				if (uncensored_check(media.filename) == 1):
					uncResult = 'U'
				else:
					uncResult = 'C'
				Log('### UNC:' + uncResult)
				searchResults = String_slice(searchResults, '<div id="waterfall">', '<script')
				content_id = String_slice(searchResults, '<date>', '</date>')
				id = org_id
				title = String_slice(searchResults, 'title="', '">')
				score = 100
				name = '[' + id + ']§' + title + '§' + 'javbus' + '§' + uncResult
				results.Append(MetadataSearchResult(id=content_id, name=name , score=score, lang=lang))# id는 내부적사용, name은 미리보기 타이틀명
				Log('ContentID: ' + content_id + ' org_id: ' + org_id)
				# Log('Title: ' + title)
				return 1
			else:
				Log('javbus Video result Not found')
				return 0
		else:
			Log('javbus result Not found')
			return 0

	def pornav_search(self, results, media, lang):
		###############################
		##### pornav video 검색  #######
		###############################
		Log('##### Start pornav video search #####')
		SEARCH_URL = 'https://pornav.co/jp/search?q='

		nMediaName = media.name
		nMediaName = nMediaName.upper()
		org_id = nMediaName
		if (nMediaName.find('FC2') > -1):
			release_id = nMediaName.replace('FC2PPV-', '')  # 검색을 위해 FC2 품번만 발췌함
		elif (media.name.find('TOKYO') > -1):
			release_id = nMediaName.replace('TOKYOHOT-', '')  # 검색을 위해 품번만 발췌함
		else:
			release_id = org_id

		Log("Release ID:    " + str(release_id) + ' # org_id: ' + org_id)
		try:#, headers={'Referer': 'http://www.google.com'}, timeout=int(Prefs['timeout'])
			# HTTP.ClearCache()
			# HTTP.CacheTime = 10800
			# HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
			# HTTP.Headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
			# HTTP.Headers['Accept-Language'] = 'ko,en-US;q=0.9,en;q=0.8'
			# HTTP.Headers['Accept-Encoding'] = 'gzip, deflate'
			# HTTP.Headers['Host'] = 'pornav.co'
			# HTTP.Headers['Upgrade-Insecure-Requests'] = '1'
			# HTTP.Headers['Connection'] = 'keep-alive'
			searchResults = HTTP.Request(SEARCH_URL + release_id).content  # post로 보낼경우 value={'aaa' : 내용} 으로 보냄
		except:
			Log( 'pornav search exception')
			return 0

		Log(searchResults)
		if (searchResults <> ''):
			nResult = searchResults.find('<div id="grid-container')  # 검색결과 확인
			# Log(searchResults)
			# Log(nResult)
			if (nResult <> -1):
				searchResults = String_slice(searchResults, '<div id="grid-container', '</ul>')
				nResult = searchResults.find(release_id)  # 2차 검색결과 확인
				if (nResult <> -1):
					Log('##### pornav Video Result Found #####')
					if (uncensored_check(media.filename) == 1):
						uncResult = 'U'
					else:
						uncResult = 'C'
					Log('### UNC:' + uncResult)
					searchResults = String_slice(searchResults, '<li class="cbp-item', '</li>')
					# content_id = String_slice(searchResults, '<a itemprop="url" href="', '"')
					content_id=org_id
					id = org_id
					title = String_slice(searchResults, 'data-title="' + release_id + ' ', '"')
					score = 100
					name = '[' + id + ']§' + title + '§' + 'pornav' + '§' + uncResult
					results.Append(MetadataSearchResult(id=content_id, name=name , score=score,
														lang=lang))  # id는 내부적사용, name은 미리보기 타이틀명
					Log('ContentID: ' + content_id + ' org_id: ' + org_id)
					return 1

		Log('pornav result Not found')
		return 0

	def javdb_search(self,results,media,lang):
		##############################
		###### javdb video 검색  ######
		##############################
		Log('##### Start javdb video search #####')
		SEARCH_URL = 'https://javdb.com/search?q='

		org_id = media.name
		if (org_id == ''): return 0
		release_id=org_id.replace(' ','-')

		Log('******* javdb Video 검색 시작(Media search start) ****** ')
		Log("### Release ID:    " + str(release_id) + ' org_id: ' + str(org_id))  # Release ID: IPZ00929 org_id: IPZ-929
		# searchResults = Get_search_url(SEARCH_URL + '&f=all', release_id)

		try:
			searchResults = HTTP.Request(SEARCH_URL + release_id + '&f=all').content
		except:
			Log( 'javdb search exception')
			return 0
		if (searchResults <> ''):
			nResult = searchResults.find('div class="empty-message"') #검색결과 없음
			# Log(searchResults)
			# Log(nResult)
			if (nResult == -1):
				Log('##### javdb Video Result Found #####')
				if (uncensored_check(media.filename) == 1):
					uncResult = 'U'
				else:
					uncResult = 'C'
				Log('### UNC:' + uncResult)
				searchResults=String_slice(searchResults,'videos video-container','</section>')
				content_id = String_slice(searchResults, 'a href="','"').replace('/v/','')
				Log(' Content_id: ' + content_id)
				title = String_slice(searchResults, 'video-title">', '<')
				id= org_id
				name= '[' + id + ']§' + title + '§' + 'javdb' + '§' + uncResult
				score=100
				results.Append(MetadataSearchResult(id=content_id, name=name, score=score, lang=lang))
				Log('##Search Update Result ==> id: ' + content_id + ' name: ' + name + ' score : ' + str(score))
				return 1
			else:
				Log('javdb Video result Not found')
		else:
			Log('javdb Video result not found1')
		return 0

	def dmm_update(self, metadata, media, lang, nOrgID):

		################################################
		################## DMM update ##################
		################################################
		if (nOrgID.find('[') <> -1 ):
			org_id=poombun_check(nOrgID)
		else:
			org_id=metadata.id.replace('00','-')

		Log('### 검색 사이트: DMM 일반 영상 / UpdateSite: DMM Video ###')
		DETAIL_URL = 'https://www.dmm.co.jp/digital/videoa/-/detail/=/cid='
		bgimgURL='https://pics.dmm.co.jp/digital/video/'
		bgimgExt='jp-'

		Log('ORG_ID: ' + org_id + ' metadataID: ' + str(metadata.id))

		searchResults = Get_search_url(DETAIL_URL, metadata.id)
		searchResults = String_slice(searchResults, 'area-headline group', 'div id="recommend"')
		if (searchResults == ''):
			Log('### 검색 사이트: DMM 아마추어 영상 / UpdateSite: DMM Amateur ###')
			DETAIL_URL = 'https://www.dmm.co.jp/digital/videoc/-/detail/=/cid='
			bgimgURL = 'https://pics.dmm.co.jp/digital/amateur/'
			bgimgExt = 'jp-00'
			searchResults = Get_search_url(DETAIL_URL, metadata.id)
			searchResults = String_slice(searchResults, 'area-headline group', 'div id="recommend"')
			if (searchResults == ''):
				return 0
		# Log(searchResults)
		id =org_id.upper()
		nTitle=String_slice(searchResults, 'alt="', '"')
		nTitle_Trans = Papago_Trans(nTitle,'ja')
		Log(' title : ' + nTitle + ' title_ko: ' + nTitle_Trans)

		# 제목
		metadata.title = '[' + id + "] " + nTitle_Trans
		metadata.title_sort = id.replace('[','').replace(']','') + ' ' + nTitle_Trans
		metadata.original_title = nTitle
		Log('## Title: ' + metadata.title + '  sort: ' + metadata.title_sort + '  orgtitle: ' + metadata.original_title)

		# 스튜디오
		sTemp = String_slice(searchResults, 'メーカー：', '</tr>') # 스튜디오 정보
		metadata.studio = String_slice(sTemp, '/">', '</a')
		metadata.studio = Papago_Trans(str(metadata.studio),'ja')

		# 감독
		sTemp=String_slice(searchResults, '監督：', '</tr>')
		director_info = Extract_str(sTemp, '<td>', '</td>')
		# Log('### Director info / 감독 정보 ###')
		# Log(director_info)
		if (director_info is not None):
			if (director_info[0] <> '----'):
				director_info_ko = Papago_Trans(director_info[0],'ja')
				metadata.directors.clear()
				try:
					meta_director = metadata.directors.new()
					meta_director.name = director_info_ko
				except:
					try:
						metadata.directors.add(director_info_ko)
					except:
						pass

		# 일자 표시(미리보기, 원출처) 제품발매일:商品発売日 전달개시일:配信開始日
		if (searchResults.find('商品発売日') <> -1):
			sTemp = String_slice(searchResults, '>商品', '</tr>')
		elif (searchResults.find('配信開始日') <> -1):
			sTemp = String_slice(searchResults, '>配信', '</tr>')
		else:
			sTemp=''
		if (sTemp<>''):
			nYear = String_slice(sTemp, '<td>', '</td>')
			nYearArray=nYear.split('/')
			# 미리보기 항목의 이미지 아래 표시되는 년도
			metadata.year = int(nYearArray[0])
			# 상세항목의 '원출처' 일자
			nYear = nYear.replace('/', '-')
			metadata.originally_available_at = datetime.strptime(nYear,'%Y-%m-%d')

		# 국가
		metadata.countries.clear()
		metadata.countries.add(Papago_Trans('Japan').replace('.',''))

		# 줄거리
		sTemp = String_slice(searchResults, 'mg-b20 lh4">', '</div')
		# sTemp=sTemp.strip()
		if (sTemp <> ''):
			sTemp=re.sub('<.+?>', '', sTemp, 0, re.I|re.S)
			# Log('#################### SUMMARY' + sTemp)
			metadata.summary = Papago_Trans(sTemp,'ja')
			if (str(Prefs['searchsiteinfo']) == 'True'):metadata.summary='[DMM] ' + metadata.summary

		# 장르
		metadata.genres.clear()
		nGenreName=Extract_str(searchResults,'ジャンル：', '</tr>')
		j=len(nGenreName)
		for i in range(0,j):
			role = metadata.roles.new()
			# nGenreName[i]=nGenreName[i].replace('.','')
			nGenreName_ko=Papago_Trans(nGenreName[i],'ja').replace('.','')
			# Log(nGenreName[i])
			# Log(nGenreName_ko)
			metadata.genres.add(nGenreName_ko)

		# 배우정보
		metadata.roles.clear()
		nActorName=Extract_str(searchResults,'出演者：', '</tr>')
		# Log('===================')
		# Log(nActorName)
		if (nActorName is not None):
			j=len(nActorName)
			for i in range(0,j):
				role = metadata.roles.new()
				nActorInfo = Get_actor_info(nActorName[i])
				role.photo = nActorInfo[0]
				role.name = nActorInfo[1]

		# Posters/Background
		nposterMain=String_slice(searchResults,'id="sample-video"', '</div>')
		posterURL_Small = String_slice(nposterMain, 'img src="', '"') # 큰이미지가 없을수도 있음(아마추어의 경우)
		posterURL_Large = String_slice(nposterMain, 'a href="', '"')
		Log("small Poster URL / 포스터 주소 : " + posterURL_Small)
		Log("Large Poster URL / 포스터 주소 : " + posterURL_Large)
		try:
			if(posterURL_Small<>''):
				metadata.posters[posterURL_Small] = Proxy.Preview(HTTP.Request(posterURL_Small, timeout=int(Prefs['timeout'])), sort_order=1)
		except:
			Log(' Can not load Small Poster')

		try:
			if(posterURL_Large<>''):
				metadata.posters[posterURL_Large] = Proxy.Preview(HTTP.Request(posterURL_Large, timeout=int(Prefs['timeout'])), sort_order=2)
		except:	Log(' Can not load Large Poster')
		sTemp = String_slice(searchResults, 'div id="sample-image-block"', '<div class')
		# Log(sTemp)
		j=sTemp.count('img src')
		imgcnt=int(Prefs['img_cnt'])
		if(imgcnt <= j): j=imgcnt
		Log('Image count: ')
		Log(j)
		if (j <> -1):
			for i in range(0,j):
				bgimg=bgimgURL + metadata.id + '/' + metadata.id + bgimgExt + str(i+1) + '.jpg'
				try:
					if (bgimg <> ''):
						metadata.art[bgimg] = Proxy.Preview(HTTP.Request(bgimg, headers={'Referer': 'http://www.google.com'}, timeout=int(Prefs['timeout'])).content, sort_order=i+1)
				except:
					Log('###' + bgimg + ' Can not load')

		# Series 정보(plex에는 seires 항목이 없으므로 '주제' 항목에 이 값을 넣음)
		Log('######## series info')
		sTemp=String_slice(searchResults, 'シリー', '</tr>')
		# Log(sTemp)
		series_info = Extract_str(sTemp, '<td>', '</td>')
		# Log(series_info)
		# Log('SeriesInfo: ' + series_info)
		if (series_info is not None):
			if (series_info[0] <> '----'):
				series_info_ko = Papago_Trans(series_info[0],'ja')
				Log(series_info_ko)
				metadata.tagline=series_info_ko
		else:
			Log('Series info not found')

		# studio 컬렉션 생성
		if (str(Prefs['create_collection_studio']) == 'True'):
			if metadata.studio != None:
				metadata.collections.add(metadata.studio)
				Log(' metadata.collections studio: ' + str(metadata.studio))
		else:
			Log('### Studio 컬렉션 생성 안함(설정 미체크) / Studio connection not create(prefrence not check ###')

		# series 컬렉션 생성
		if (str(Prefs['create_collection_series']) == 'True'):
			if metadata.tagline != None:
				metadata.collections.add(metadata.tagline)
				Log(' metadata.collections series: ' + str(metadata.tagline))
		else:
			Log('### series 컬렉션 생성 안함(설정 미체크) Series connection not create(prefrence not check ###')

		Log('******* DMM 미디어 업데이트 완료/Media Update completed ****** ')
		return 1

	def r18_update(self, metadata, media, lang, nOrgID):

		Log('****** 미디어 업데이트(상세항목) 시작 / r18 Media Update Start *******')
		# Log("Update ID:   " + str(metadata.id) +  ' Original ID: ' + org_id)

		################################################
		################## r18 update ##################
		################################################
		# r18 사이트 검색
		DETAIL_URL = 'https://www.r18.com/videos/vod/movies/detail/-/id='
		DETAIL_URL2 = 'https://www.r18.com/videos/vod/amateur/detail/-/id='

		org_id = poombun_check(nOrgID)

		#일반 검색에서 안나올 경우 아마추어 URL로 다시 확인함
		try:
			url = DETAIL_URL + metadata.id
			root = HTML.ElementFromURL(url,timeout=int(Prefs['timeout']))
		except:
			try:
				url = DETAIL_URL2 + metadata.id
				root = HTML.ElementFromURL(url, timeout=int(Prefs['timeout']))
			except:
				return 0

		# id = detailItem(root, '//dt[contains(text(), "DVD ID")]/following-sibling::dd[1]')  # 작품 ID
		id = org_id.upper()
		nTitle=detailItem(root,'//cite[@itemprop="name"]')
		nTitle_Trans=Papago_Trans(nTitle)
		metadata.title= '[' + id + '] ' + nTitle_Trans
		metadata.title_sort = id.replace('[','').replace(']','') + ' ' + nTitle_Trans
		metadata.original_title = nTitle
		metadata.studio = detailItem(root,'//dd[@itemprop="productionCompany"]//a') # 스튜디오 정보
		metadata.studio = Papago_Trans(str(metadata.studio))

		#줄거리 요약정보(r18은 요약정보가 없으므로 검색된 사이트 이름만 표기
		if (str(Prefs['searchsiteinfo']) == 'True'): metadata.summary = '[r18]'

		#Log('### 감독정보 가져오기 ###')
		director_info = detailItem(root,'//dd[@itemprop="director"]') # 감독 정보
		director_info = Papago_Trans(director_info)
		metadata.directors.clear()
		try:
			meta_director = metadata.directors.new()
			meta_director.name = director_info
		except:
			try:
				metadata.directors.add(director_info)
			except:
				pass

		date = detailItem(root,'//dd[@itemprop="dateCreated"]') # 릴리즈 날짜
		date_object = datetime.strptime(date.replace(".", "").replace("Sept", "Sep").replace("July", "Jul").replace("June", "Jun"), '%b %d, %Y')
		metadata.originally_available_at = date_object
		metadata.year = metadata.originally_available_at.year

		#

		metadata.genres.clear()
		categories = root.xpath('//div[contains(@class, "product-categories-list")]//div//a')
		for category in categories:
			genreName = category.text_content().strip()
			if "Featured" in genreName or "Sale" in genreName:
				continue
			genreName=genreName.replace('.','')
			nTrans=Papago_Trans(genreName)
			metadata.genres.add(nTrans)
			Log('metadata.genre : ' + nTrans)

		# 국가
		metadata.countries.clear()
		metadata.countries.add(Papago_Trans('Japan').replace('.',''))

		# 배우정보
		metadata.roles.clear()
		actors = root.xpath('//div[contains(@class, "js-tab-contents")]//ul[contains(@class, "cmn-list-product03")]//a')
		if len(actors) > 0:
			for actorLink in actors:
				role = metadata.roles.new()
				actorName = actorLink.text_content().strip()
				nTrans=Papago_Trans(actorName)

				role.name = nTrans
				actorPage = actorLink.xpath("p/img")[0].get("src")
				role.photo = actorPage
				Log("Actor: " + nTrans)
		else:
			Log("배우 정보를 찾을 수 없음")

		# Posters/Background
		posterURL = root.xpath('//img[@itemprop="image"]')[0].get("src")
		Log("Poster URL / 포스터 주소 : " + posterURL)
		try:
			if(posterURL<>''):
				metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}, timeout=int(Prefs['timeout'])).content, sort_order = 1)
		except: Log(posterURL + ' Not Load')
		posterURL=posterURL.replace('ps.jpg','pl.jpg')
		try:
			if (posterURL <> ''):
				metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}, timeout=int(Prefs['timeout'])).content, sort_order=2)
		except: Log(posterURL + ' Not Load')
		scenes = root.xpath('//ul[contains(@class, "product-gallery")]//img')
		i=1
		imgcnt=int(Prefs['img_cnt'])

		Log('Image count: ')
		for scene in scenes:
			background = scene.get("data-original").replace("js-", "jp-")
			Log("백그라운드 URL BackgroundURL: " + background)
			try:
				if(background <>''):
					metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}, timeout=int(Prefs['timeout'])).content, sort_order = i)
			except:Log(background + ' Not Load')
			if (imgcnt <= i): break
			i=i+1

		Log('******* 미디어 업데이트 완료 ****** ')

		# studio 컬렉션 생성
		if (str(Prefs['create_collection_studio']) == 'True'):
			if metadata.studio != None:
				metadata.collections.add(metadata.studio)
				Log(' metadata.collections studio: ' + str(metadata.studio))
		else:
			Log('### Studio 컬렉션 생성 안함(설정 미체크)')
		# series 컬렉션 생성
		if (str(Prefs['create_collection_series']) == 'True'):
			series = detailItem(root,'//div[contains(@class, "product-details")]//a[contains(@href, "type=series")]')
			if series != None:
				nTrans=Papago_Trans(series)
				metadata.collections.add(nTrans)
				Log(' metadata.collections series: ' + str(nTrans))
		else:
			Log('### series 컬렉션 생성 안함(설정 미체크)')

		return 1

	def javbus_update(self, metadata, media, lang, nOrgID):

		# nIDs[0]: 검색용 품번  nIDs[1]: 검색된 사이트(DMM, R18)   nIDs[2]: 아마추어(C)or일반(A)  nIDs[3]: 오리지널 품번(OAE-101)
		Log('****** 미디어 업데이트(상세항목) 시작 / Javbus Media Update Start *******')
		# Log("Update ID:   " + str(metadata.id) +  ' Original ID: ' + org_id)

		################################################
		################# javbus update #################
		################################################
		Log('### 검색 사이트: javbus 일반 영상 / UpdateSite: javbus Video ###')
		DETAIL_URL = 'https://www.javbus.com/'

		org_id=poombun_check(nOrgID)

		try:
			searchResults = HTTP.Request(DETAIL_URL + metadata.id , headers = {'Referer': 'http://www.google.com'}, timeout=int(Prefs['timeout'])).content
		except:
			Log('@@@ Update content load failed')
			return 0

		# Log(searchResults)
		nResult = searchResults.find('<div class="container">')  # 검색결과 확인
		if (nResult == -1):
			Log('@@@ Update content search result failed1')
			return 0
		searchResults = String_slice(searchResults, '<div class="container">', '<div class="clearfix">')
		if (searchResults == ''):
			Log('@@@ Update content search result failed2')
			return 0
		# Log(searchResults)
		id = org_id.upper()
		nTitle = String_slice(searchResults, 'title="', '"')
		nTitle_Trans = Papago_Trans(nTitle, 'ja')
		Log(' title : ' + nTitle)
		Log(' title_ko: ' + nTitle_Trans)

		# 제목
		try:
			Log('=======  title Info start =========')
			metadata.title = '[' + id + '] ' + nTitle_Trans
			metadata.title_sort = id.replace('[','').replace(']','') + ' ' + nTitle_Trans
			metadata.original_title = nTitle
			Log('=======  title Info end =========')
		except:
			Log('@@@ Title failed')

		# 스튜디오=> 제조사
		try:
			Log('=======  Studio Info start =========')
			sTemp = String_slice(searchResults, '製作商', '</p>')
			metadata.studio = String_slice(sTemp, '">', '</a')
			metadata.studio = Papago_Trans(str(metadata.studio), 'ja')
			Log('Studio: ' + str(metadata.studio))
			Log('=======  Studio Info end =========')
		except:
			Log('@@@ Studio failed')

		# 감독
		try:
			Log('=======  Director Info start =========')
			# sTemp = String_slice(searchResults, '導演', '<p>')
			director_info = Extract_str(searchResults, '導演', '</p>')
			if (director_info is not None):
				director_info_ko = Papago_Trans(director_info[0], 'ja')
				metadata.directors.clear()
				try:
					meta_director = metadata.directors.new()
					meta_director.name = director_info_ko
				except:
					try:
						metadata.directors.add(director_info_ko)
					except:
						pass
			Log('=======  Director Info end =========')
		except:
			Log('@@@ Director failed')

		# 일자 표시(미리보기, 원출처) 제품발매일:商品発売日 전달개시일:配信開始日
		try:
			Log('=======  Date Info start =========')
			if (searchResults.find('發行日') <> -1):
				nYear = String_slice(searchResults, '發行日期:</span>', '</p>')
				nYearArray = nYear.split('-')
				# 미리보기 항목의 이미지 아래 표시되는 년도
				metadata.year = int(nYearArray[0])
				# 상세항목의 '원출처' 일자
				metadata.originally_available_at = datetime.strptime(nYear, '%Y-%m-%d')
			Log('=======  Date Info start =========')
		except:
			Log('@@@ Date Failed')

		# 줄거리(javbus는 줄거리 없음)
		if (str(Prefs['searchsiteinfo']) == 'True'): metadata.summary = '[javbus]'

		# 국가
		metadata.countries.clear()
		metadata.countries.add(Papago_Trans('Japan').replace('.',''))

		# 장르
		try:
			Log('=======  Genre Info start =========')
			metadata.roles.clear()
			nGenreName = Extract_str(searchResults, '類別:</p>', '</p>')
			j = len(nGenreName)
			for i in range(0, j):
				role = metadata.roles.new()
				# nGenreName[i] = nGenreName[i].replace('.', '')
				nGenreName_ko = Papago_Trans(nGenreName[i], 'ja').replace('.','')
				# Log(nGenreName[i])
				# Log(nGenreName_ko)
				metadata.genres.add(nGenreName_ko)
			Log('=======  Genre Info end =========')
		except:
			Log('@@@ Genre failed')

		# 배우정보
		metadata.roles.clear()
		Log('=======  Actor Info start =========')
		nFound = searchResults.find('<div id="star-div">')
		try:
			if (nFound <> -1):
				nStr = String_slice(searchResults, '<div id="star-div">', '<h4 id="mag-submit-show')
				nActorURL = []
				nActorName= []
				linksList = re.findall('<img src="(.*)" ', nStr)
				for link in linksList: nActorURL.append(link)
				linksList = re.findall('title="(.*)"', nStr)
				for link in linksList: nActorName.append(link)
				j=len(nActorURL)
				for i in range(j):
					role = metadata.roles.new()
					rolename_kr = Papago_Trans(nActorName[i],'ja')
					role.photo = str(nActorURL[i])
					role.name = rolename_kr
					Log('nURL: ' + str(nActorURL[i]) + ' nName: ' + rolename_kr)
		except:
			Log('@@@ Get actor info exception')

		Log('=======  Actor Info end =========')

		# Posters
		Log('=======  Poster Info start =========')
		try:
			nposterMain = String_slice(searchResults, 'col-md-9 screencap', '</div>')
			posterURL_Large = String_slice(nposterMain, 'href="', '"')
			posterURL_Small = posterURL_Large.replace('_b.jpg','.jpg').replace('cover', 'thumb')
			Log("small Poster URL / 포스터 주소 : " + posterURL_Small)
			Log("Large Poster URL / 포스터 주소 : " + posterURL_Large)
			try:
				if(posterURL_Small <>''):
					metadata.posters[posterURL_Small] = Proxy.Preview(HTTP.Request(posterURL_Small, timeout=int(Prefs['timeout'])), sort_order=1)
			except:	Log(' Can not load Small Poster')
			try:
				if(posterURL_Large <>''):
					metadata.posters[posterURL_Large] = Proxy.Preview(HTTP.Request(posterURL_Large, timeout=int(Prefs['timeout'])), sort_order=2)
			except:	Log(' Can not load Large Poster')
			Log('=======  Poster Info end =========')
		except:
			Log('@@@ Poster Failed')

		#background images
		try:
			Log('=======  Background Info start =========')
			nBgackgroundimg=Extract_imgurl(searchResults, '<div id="sample-waterfall">', '<div class="clearfix','href')
			j = len(nBgackgroundimg)
			imgcnt = int(Prefs['img_cnt'])
			if (imgcnt <= j): j = imgcnt
			Log('Image count: ')
			if (j <> -1):
				for i in range(0, j):
					bgimg = nBgackgroundimg[i]
					try:
						if(bgimg <>''):
							metadata.art[bgimg] = Proxy.Preview(
							HTTP.Request(bgimg, headers={'Referer': 'http://www.google.com'}, timeout=int(Prefs['timeout'])).content, sort_order=i + 1)
					except:
						Log('@@@' + bgimg + ' Can not load')
			Log('=======  Background Info end =========')
		except:
			Log('@@@ Background Image failed')

		# Series 정보(plex에는 seires 항목이 없으므로 '주제' 항목에 이 값을 넣음)
		try:
			Log('=======  Series Info start =========')
			# Log('######## series info')
			# Log(sTemp)
			series_info = Extract_str(searchResults, '系列', '</p>')
			# Log(series_info)
			# Log('SeriesInfo: ' + series_info)
			if (series_info is not None):
				if (series_info[0] <> '----'):
					series_info_ko = Papago_Trans(series_info[0], 'ja')
					Log(series_info_ko)
					metadata.tagline = series_info_ko
			else:
				Log('Series info not found')
			Log('=======  Series Info end =========')
		except:
			Log('@@@ Series failed')

		# studio 컬렉션 생성
		try:
			if (str(Prefs['create_collection_studio']) == 'True'):
				if metadata.studio != None:
					metadata.collections.add(metadata.studio)
					Log(' metadata.collections studio: ' + str(metadata.studio))
			else:
				Log('### Studio 컬렉션 생성 안함(설정 미체크) / Studio connection not create(prefrence not check ###')
		except:
			Log('@@@ Studio collection failed')

		# series 컬렉션 생성
		try:
			if (str(Prefs['create_collection_series']) == 'True'):
				if metadata.tagline != None:
					metadata.collections.add(metadata.tagline)
					Log(' metadata.collections series: ' + str(metadata.tagline))
			else:
				Log('### series 컬렉션 생성 안함(설정 미체크) Series connection not create(prefrence not check ###')

			Log('******* javbus 미디어 업데이트 완료/Media Update completed ****** ')
			return
		except:
			Log('@@@ Series collection failed')

		return 1

	def pornav_update(self, metadata, media, lang, nOrgID):

		# nIDs[0]: 검색용 품번  nIDs[1]: 검색된 사이트(DMM, R18)   nIDs[2]: 아마추어(C)or일반(A)  nIDs[3]: 오리지널 품번(OAE-101)
		Log('****** 미디어 업데이트(상세항목) 시작 / pornav Media Update Start *******')
		# Log("Update ID:   " + str(metadata.id) +  ' Original ID: ' + org_id)
		# id: /jp/article-179279/N0836-Saionji-Reo-vs-TOKYO-HOT-Devil-Kang

		################################################
		################# pornav update #################
		################################################
		Log('### 검색 사이트: pornav 일반 영상 / UpdateSite: pornav Video ###')
		DETAIL_URL = 'https://pornav.co/'
		SEARCH_URL = 'https://pornav.co/jp/search?q='

		nMediaName=metadata.id
		if (nMediaName.find('FC2') > -1):
			release_id = nMediaName.replace('FC2PPV-', '')  # 검색을 위해 FC2 품번만 발췌함
		elif (nMediaName.find('TOKYO') > -1):
			release_id = nMediaName.replace('TOKYOHOT-', '')  # 검색을 위해 품번만 발췌함
		else:
			release_id = poombun_check(nOrgID) #.replace('[','').replace(']','')
		try:
			searchResults = HTTP.Request(SEARCH_URL + release_id, timeout=int(Prefs['timeout'])).content  # post로 보낼경우 value={'aaa' : 내용} 으로 보냄
		except:
			return 0
		content_id = String_slice(searchResults, '<a itemprop="url" href="', '"')
		try:
			searchResults = HTTP.Request(DETAIL_URL + content_id , headers = {'Referer': 'http://www.google.com'}, timeout=int(Prefs['timeout'])).content
			nResult = searchResults.find('<div class="container content"')  # 검색결과 확인
			if (nResult == -1):
				Log('@@@ Update content search result failed1')
				return 0
		except:
			Log('@@@ Update content load failed')
		# Log(searchResults)

		searchResults = String_slice(searchResults, '<div class="container content"', '</ul>')
		if (searchResults == ''):
			Log('@@@ Update content search result failed2')
			return 0
		# Log(searchResults)
		id= String_slice(media.title,'[',']').upper()
		nTitle = String_slice(searchResults, 'alt="', '"').replace(id,'').upper()
		nTitle = nTitle.replace('FC2 PPV ', '')
		nTitle = nTitle.replace(release_id.upper(), '')
		nTitle = nTitle.replace('TOKYO HOT','')
		nTitle_Trans = Papago_Trans(nTitle, 'ja')
		Log(' title : ' + nTitle)
		Log(' title_ko: ' + nTitle_Trans)

		# 제목
		try:
			Log('=======  title Info start =========')
			metadata.title = "[" + id.upper() + "] " + nTitle_Trans
			metadata.title_sort = id + ' ' + nTitle_Trans
			metadata.original_title = nTitle
			Log(' Title: ' + metadata.title)
			Log('=======  title Info end =========')
		except:
			Log('@@@ Title failed')

		# 스튜디오=> 제조사
		try:
			Log('=======  Studio Info start =========')
			sTemp = String_slice(searchResults, 'メーカー： ', '<')
			metadata.studio = Papago_Trans(str(sTemp), 'ja')
			Log('Studio: ' + str(metadata.studio))
			Log('=======  Studio Info end =========')
		except:
			Log('@@@ Studio failed')

		# 감독
		try:
			Log('=======  Director Info start =========')
			# sTemp = String_slice(searchResults, '導演', '<p>')
			director_info = String_slice(searchResults, '監督： ', '<')
			Log(director_info)
			if (director_info <> ''):
				director_info_ko = Papago_Trans(director_info, 'ja')
				metadata.directors.clear()
				try:
					meta_director = metadata.directors.new()
					meta_director.name = director_info_ko
				except:
					try:
						metadata.directors.add(director_info_ko)
						Log(' Director: ' + director_info_ko)
					except:
						pass
			Log('=======  Director Info end =========')
		except:
			Log('@@@ Director failed')

			# 일자 표시(미리보기, 원출처) 제품발매일:商品発売日 전달개시일:配信開始日
		try:
			Log('=======  Date Info start =========')
			if (searchResults.find('発売日') <> -1):
				nYear = String_slice(searchResults, '発売日： ', '<')
				nYear = nYear.replace('/','-')
				nYearArray = nYear.split('-')
				# 미리보기 항목의 이미지 아래 표시되는 년도
				metadata.year = int(nYearArray[0])
				# 상세항목의 '원출처' 일자
				metadata.originally_available_at = datetime.strptime(nYear, '%Y-%m-%d')
				Log(' Year: ' + nYear)
			Log('=======  Date Info end =========')
		except:
			Log('@@@ Date Failed')

			# 줄거리
			if (str(Prefs['searchsiteinfo']) == 'True'): metadata.summary = '[pornav]'
		try:
			Log('=======  summary Info start =========')
			sTemp = String_slice(searchResults, 'class="tag-box tag-box-v2">', '</div>')
			metadata.summary = metadata.summary + Papago_Trans(sTemp, 'ja')
			Log('summary: ' + str(metadata.summary))
			Log('=======  summary Info end =========')
		except:
			Log('@@@ summary failed')

		# 국가
		metadata.countries.clear()
		metadata.countries.add(Papago_Trans('Japan').replace('.',''))

		# 장르
		try:
			Log('=======  Genre Info start =========')
			metadata.roles.clear()
			nGenreName = String_slice(searchResults, 'ジャンル：', '<')
			Log('########## Genre str: ' + nGenreName)
			nGenreName_arr=nGenreName.split(' ')
			j = len(nGenreName_arr)
			for i in range(0, j):
				role = metadata.roles.new()
				if (nGenreName_arr[i] == '' or nGenreName_arr[i] <> ' '):
					# nGenreName_arr[i] = nGenreName_arr[i].replace('.', '')
					nGenreName_ko = Papago_Trans(nGenreName_arr[i], 'ja').replace('.','')
					# Log(nGenreName[i])
					# Log(nGenreName_ko)
					metadata.genres.add(nGenreName_ko)
					Log(' Genre add: ' + nGenreName_ko)
			Log('=======  Genre Info end =========')
		except:
			Log('@@@ Genre failed')

		# 배우정보 => 이시키들이 배우 구분자가 스페이스인데 이름이 2글자면 이것도 스페이스로 나눠서 이름을 당췌 알 수 없음.. 통짜로 넣어야할듯
		metadata.roles.clear()
		Log('=======  Actor Info start =========')
		nFound = searchResults.find('出演者： ')
		try:
			if (nFound <> -1):
				nStr = String_slice(searchResults, '出演者： ', '<')
				nActor=nStr.split(' ')
				j = len(nActor)
				for i in range(0, j):
					if (nActor[i] == '' or nActor[i] <> ' '):
						role = metadata.roles.new()
						rolename_kr = Papago_Trans(nActor[i], 'ja')
						role.photo = str(nActor[i])
						role.name = rolename_kr
						Log('nURL: ' + str(nActor[i]) + ' nName: ' + rolename_kr)
				Log('=======  Genre Info end =========')
		except:
			Log('@@@ Get actor info exception')

		# Log('=======  Actor Info end =========')

		# Posters
		Log('=======  Poster Info start =========')
		try:
			posterURL_Small = String_slice(searchResults, '<img itemprop="image" src="', '"')
			Log("small Poster URL / 포스터 주소 : " + posterURL_Small)
			try:
				if(posterURL_Small <>''):
					metadata.posters[posterURL_Small] = Proxy.Preview(HTTP.Request(posterURL_Small, timeout=int(Prefs['timeout'])), sort_order=1)
			except:	Log(' Can not load Small Poster')
			Log('=======  Poster Info end =========')
		except:
			Log('@@@ Poster Failed')

		#background images
		try:
			Log('=======  Background Info start =========')
			nBgackgroundimg=Extract_imgurl(searchResults, 'preview-images">', '<div class','data-original')
			j = len(nBgackgroundimg)
			imgcnt = int(Prefs['img_cnt'])
			if (imgcnt <= j): j = imgcnt
			Log('Image count: ')
			if (j <> -1):
				for i in range(0, j):
					bgimg = nBgackgroundimg[i]
					try:
						if(bgimg <>''):
							metadata.art[bgimg] = Proxy.Preview(
							HTTP.Request(bgimg, headers={'Referer': 'http://www.google.com'}, timeout=int(Prefs['timeout'])).content, sort_order=i + 1)
					except:
						Log('@@@' + bgimg + ' Can not load')
			Log('=======  Background Info end =========')
		except:
			Log('@@@ Background Image failed')

		# Series 정보(plex에는 seires 항목이 없으므로 '주제' 항목에 이 값을 넣음)
		try:
			Log('=======  Series Info start =========')
			# Log('######## series info')
			# Log(sTemp)
			series_info = String_slice(searchResults, 'シリーズ： ', '<')
			# Log(series_info)
			# Log('SeriesInfo: ' + series_info)
			if (series_info <> ''):
				series_info_ko = Papago_Trans(series_info, 'ja')
				Log(series_info_ko)
				metadata.tagline = series_info_ko
			else:
				Log('Series info not found')
			Log('=======  Series Info end =========')
		except:
			Log('@@@ Series failed')

		# studio 컬렉션 생성
		try:
			if (str(Prefs['create_collection_studio']) == 'True'):
				if metadata.studio != None:
					metadata.collections.add(metadata.studio)
					Log(' metadata.collections studio: ' + str(metadata.studio))
			else:
				Log('### Studio 컬렉션 생성 안함(설정 미체크) / Studio connection not create(prefrence not check ###')
		except:
			Log('@@@ Studio collection failed')

		# series 컬렉션 생성
		try:
			if (str(Prefs['create_collection_series']) == 'True'):
				if metadata.tagline != None:
					metadata.collections.add(metadata.tagline)
					Log(' metadata.collections series: ' + str(metadata.tagline))
			else:
				Log('### series 컬렉션 생성 안함(설정 미체크) Series connection not create(prefrence not check ###')

			Log('******* pornav 미디어 업데이트 완료/Media Update completed ****** ')
		except:
			Log('@@@ Series collection failed')

		return 1

	def javdb_update(self, metadata, media, lang, nOrgID):

		# nIDs[0]: 검색용 품번  nIDs[1]: 검색된 사이트(DMM, R18)   nIDs[2]: 아마추어(C)or일반(A)  nIDs[3]: 오리지널 품번(OAE-101)
		Log('****** 미디어 업데이트(상세항목) 시작 / javdb Media Update Start *******')
		# Log("Update ID:   " + str(metadata.id) +  ' Original ID: ' + org_id)

		################################################
		################# javdb update #################
		################################################
		Log('### 검색 사이트: javdb 일반 영상 / UpdateSite: javdb Video ###')
		DETAIL_URL = 'https://javdb.com/v/'

		org_id=poombun_check(nOrgID)

		try:
			searchResults = HTTP.Request(DETAIL_URL + metadata.id , headers = {'Referer': 'http://www.google.com'}, timeout=int(Prefs['timeout'])).content
		except:
			Log('@@@ Update content load failed')
			return 0

		# Log(searchResults)
		nResult = searchResults.find('頁面未找到 (404)')  # 검색결과 확인
		if (nResult <> -1):
			Log('@@@ Update content search result failed1')
			return 0
		searchResults = String_slice(searchResults, 'title is-4', '</article>')
		if (searchResults == ''):
			Log('@@@ Update content search result failed2')
			return 0
		# Log(searchResults)
		id = org_id.upper()
		nTitle = String_slice(searchResults, '<strong>', '<').replace(id,'')
		nTitle_Trans = Papago_Trans(nTitle, 'ja')
		Log(' title : ' + nTitle)
		Log(' title_ko: ' + nTitle_Trans)

		# 제목
		try:
			Log('=======  title Info start =========')
			metadata.title = '[' + id + '] ' + nTitle_Trans
			metadata.title_sort = id.replace('[','').replace(']','') + ' ' + nTitle_Trans
			metadata.original_title = nTitle
			Log('=======  title Info end =========')
		except:
			Log('@@@ Title failed')

		# 스튜디오=> 제조사
		try:
			Log('=======  Studio Info start =========')
			sTemp = String_slice(searchResults, '片商', '</div>')
			sTemp = String_slice(sTemp, 'a href', '</span>')
			metadata.studio = String_slice(sTemp, '">', '</a')
			metadata.studio = Papago_Trans(str(metadata.studio), 'ja')
			Log('Studio: ' + str(metadata.studio))
			Log('=======  Studio Info end =========')
		except:
			Log('@@@ Studio failed')

		# 감독
		try:
			Log('=======  Director Info start =========')
			# sTemp = String_slice(searchResults, '導演', '<p>')
			director_info = Extract_str(searchResults, '導演', '</div>')
			if (director_info is not None):
				director_info_ko = Papago_Trans(director_info[0], 'ja')
				Log('Director: ' + director_info_ko)
				metadata.directors.clear()
				try:
					meta_director = metadata.directors.new()
					meta_director.name = director_info_ko
				except:
					try:
						metadata.directors.add(director_info_ko)
					except:
						pass
			Log('=======  Director Info end =========')
		except:
			Log('@@@ Director failed')

		# 일자 표시(미리보기, 원출처) 제품발매일:商品発売日 전달개시일:配信開始日
		try:
			Log('=======  Date Info start =========')
			if (searchResults.find('日期') <> -1):
				nYear = String_slice(searchResults, '日期', '</div>')
				nYear = String_slice(nYear, 'value">', '<')
				nYearArray = nYear.split('-')
				# 미리보기 항목의 이미지 아래 표시되는 년도
				metadata.year = int(nYearArray[0])
				# 상세항목의 '원출처' 일자
				metadata.originally_available_at = datetime.strptime(nYear, '%Y-%m-%d')
			Log('=======  Date Info start =========')
		except:
			Log('@@@ Date Failed')

		# 줄거리(javdb는 줄거리 없음)
		if (str(Prefs['searchsiteinfo']) == 'True'): metadata.summary = '[javdb]'

		# 국가
		metadata.countries.clear()
		metadata.countries.add(Papago_Trans('Japan').replace('.',''))

		# 장르
		try:
			Log('=======  Genre Info start =========')
			metadata.roles.clear()
			nGenreName = Extract_str(searchResults, '類別', '</div>')
			j = len(nGenreName)
			for i in range(0, j):
				role = metadata.roles.new()
				# nGenreName[i] = nGenreName[i].replace('.', '')
				nGenreName_ko = Papago_Trans(nGenreName[i], 'ja').replace('.','')
				Log(nGenreName[i])
				Log(nGenreName_ko)
				metadata.genres.add(nGenreName_ko)
			Log('=======  Genre Info end =========')
		except:
			Log('@@@ Genre failed')

		# 배우정보
		Log('=======  Actor Info end =========')
		metadata.roles.clear()
		nActorName=Extract_str(searchResults,'演員', '</div>')
		# Log('===================')
		Log(nActorName)
		if (nActorName is not None):
			j=len(nActorName)
			for i in range(0,j):
				role = metadata.roles.new()
				# if (nActorName[i].find('(') > -1): nActorName = nActorName[i][0:nActorName[i].find('(')]
				nTemp=nActorName[i]
				if (nTemp.find('(') <> -1) : nTemp=nTemp[0:nTemp.find('(')]
				nActorInfo = Get_actor_info(nTemp)
				role.photo = nActorInfo[0]
				role.name = nActorInfo[1]
		Log('=======  Actor Info end =========')

		# Posters
		Log('=======  Poster Info start =========')
		try:
			posterURL_Small = String_slice(searchResults, 'gallery" href="', '"')
			Log("small Poster URL / 포스터 주소 : " + posterURL_Small)
			try:
				if(posterURL_Small <>'' or posterURL_Small <> '#preview-video'):
					metadata.posters[posterURL_Small] = Proxy.Preview(HTTP.Request(posterURL_Small, timeout=int(Prefs['timeout'])), sort_order=1)
			except:	Log(' Can not load Small Poster')
			Log('=======  Poster Info end =========')
		except:
			Log('@@@ Poster Failed')

		#background images
		try:
			Log('=======  Background Info start =========')
			nBgackgroundimg=Extract_imgurl(searchResults, 'tile-images preview-images', '</article>','href')
			j = len(nBgackgroundimg)
			imgcnt = int(Prefs['img_cnt'])
			if (imgcnt <= j): j = imgcnt
			Log('Image count: ')
			if (j <> -1):
				for i in range(0, j):
					bgimg = nBgackgroundimg[i]
					try:
						if(bgimg <>''):
							metadata.art[bgimg] = Proxy.Preview(
							HTTP.Request(bgimg, headers={'Referer': 'http://www.google.com'}, timeout=int(Prefs['timeout'])).content, sort_order=i + 1)
					except:
						Log('@@@' + bgimg + ' Can not load')
			Log('=======  Background Info end =========')
		except:
			Log('@@@ Background Image failed')

		# Series 정보(plex에는 seires 항목이 없으므로 '주제' 항목에 이 값을 넣음)
		try:
			Log('=======  Series Info start =========')
			# Log('######## series info')
			# Log(sTemp)
			series_info = Extract_str(searchResults, '系列', '</div>')
			Log(series_info)
			# Log('SeriesInfo: ' + series_info)
			if (series_info is not None):
				if (series_info[0] <> '----'):
					series_info_ko = Papago_Trans(series_info[0], 'ja')
					Log(series_info_ko)
					metadata.tagline = series_info_ko
			else:
				Log('Series info not found')
			Log('=======  Series Info end =========')
		except:
			Log('@@@ Series failed')

		# studio 컬렉션 생성
		try:
			if (str(Prefs['create_collection_studio']) == 'True'):
				if metadata.studio != None:
					metadata.collections.add(metadata.studio)
					Log(' metadata.collections studio: ' + str(metadata.studio))
			else:
				Log('### Studio 컬렉션 생성 안함(설정 미체크) / Studio connection not create(prefrence not check ###')
		except:
			Log('@@@ Studio collection failed')

		# series 컬렉션 생성
		try:
			if (str(Prefs['create_collection_series']) == 'True'):
				if metadata.tagline != None:
					metadata.collections.add(metadata.tagline)
					Log(' metadata.collections series: ' + str(metadata.tagline))
			else:
				Log('### series 컬렉션 생성 안함(설정 미체크) Series connection not create(prefrence not check ###')

			Log('******* javdb 미디어 업데이트 완료/Media Update completed ****** ')

		except:
			Log('@@@ Series collection failed')

		return 1
