#!/usr/bin/python3

import requests
from urllib.request import urlopen, Request

import time
from bs4 import BeautifulSoup
import feedparser
import json
import socket
import reverse_geocoder as rg
import country_converter as coco
from os import system

HOST = '0.0.0.0'  
PORT = 8099
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serv.bind(('0.0.0.0', 8099))
serv.listen(5)
dummy = "                    "
lastdeaths = 0
system('clear')

def do_forever():

#Simple Socket Server

	while True:
		conn, addr = serv.accept()
		from_client = ''
		while True:
			try:
				data = conn.recv(4096)
			except ConnectionResetError:
				print("Connection Error")
			
			if not data: break
			else:
				print("Received : "+data.decode("ascii"))
				if data.decode("ascii") == "button1":
					returndata=covid_stats()
				if data.decode("ascii") == "button2":
					returndata = weather()
				if data.decode("ascii") == "button3":
					returndata = topsearch()
				if data.decode("ascii") == "button4":
					returndata = iss()
				if data.decode("ascii") == "button5":
					returndata = hackaday()
				try :
					conn.send(returndata.encode("ascii"))
				except BrokenPipeError:
					print("Broken Pipe")
		conn.close()

#Convert F to C
def toc(temp):
	c = (5/9) * (temp - 32)
	return round(c)

#Format strings so they don't split words
def pretty(instring):
	rowlen = 20
	rowtotal=0
	rowcount = 1

	instring=instring.replace("‘","\"")
	instring=instring.replace("’","\"")
	length = len(instring)
	wordlist = instring.split(" ")
	finalstring = ""
	for word in wordlist:

		if rowtotal+ len(word) < rowlen:
			rowtotal = rowtotal + len(word)+1
			finalstring = finalstring + word+" "
		else:
			finalstring = finalstring.ljust(20*rowcount," ")
			finalstring = finalstring + word+" "
			rowtotal = len(word)+1
			rowcount += 1
	return finalstring

#Center Strings
def centerstr(instr):
	length=len(instr)
	if length < 20:
		spacer = (20-length)/2
		spacer = round(spacer)
		returnstr = instr.rjust(length+spacer," ")
	else:
		returnstr = instr
	return returnstr

# ------- BUTTON FUNCTIONS EXAMPLES -----------

def weather():
	url="https://weather.com/weather/today/l/91cdfbd64567d9d60d0e9ebbe8f9cd84266766670c239dc9fa47d7c245e5c0fe"
	page = requests.get(url)
	soup=BeautifulSoup(page.content,'html.parser')

	def toc(temp):
		c = (5/9) * (temp - 32)
		return round(c)


	now=soup.find("div",attrs={"class":"today_nowcard-temp"}).text
	hilodata=soup.find("div", attrs={"class": "today_nowcard-hilo"})
	hilo = hilodata.findAll("span",attrs={"class":"deg-hilo-nowcard"})
	high = hilo[0].get_text()
	low = hilo[1].get_text()

	high =high.rstrip("°")
	low = low.rstrip("°")	

	now = int(now[:-1])

	if high != "--":
		high=int(high)
		high=toc(high)
		
	if low != "--":
		low=int(low)
		low=toc(low)
		
	now = toc(now)

	high=str(high)
	low=str(low)
	now=centerstr(str(now)+" C")

	hilostring = centerstr("Hi:" +high+" | Lo:"+low)
	title=centerstr("W E A T H E R")
	return_string = title+"&"+dummy+"&"+now+"&"+hilostring
	return return_string

	
def covid_stats():
	url="https://www.worldometers.info/coronavirus/country/us/"
	response = requests.get(url)
	soup=BeautifulSoup(response.text,"html.parser")

	cases=soup.findAll('span')[4]
	deaths=soup.findAll('span')[5]

	cases = cases.get_text('span')
	deaths = deaths.get_text('span')
	numdeaths = deaths.replace(',', '')
	
	global lastdeaths
	if lastdeaths != 0:
		deathchange = str(int(numdeaths) - lastdeaths)
	else:
		deathchange = "--"
	lastdeaths	
	lastdeaths = int(numdeaths)
	
	allcases = "Cases  " + cases
	alldeaths = "Deaths " + deaths
	change = "Change " + deathchange
	title = centerstr("US COVID19 STATS")
	return_string = title+"&"+allcases+"&"+alldeaths+"&"+change
	return return_string

def golfcount():
	url = f"https://trumpgolfcount.com/"
	response = requests.get(url)
	soup = BeautifulSoup(response.content, "html.parser")
	all_links = soup.findAll("a")
	count = centerstr(all_links[7].text)
	title=centerstr("Trump Golf Outings")
	return_string=title+"&"+dummy+"&"+count+"&"+dummy
	return return_string
	
def nyt():

	feed = feedparser.parse('https://rss.nytimes.com/services/xml/rss/nyt/US.xml')
	title = feed.entries[1].title
	return_string = pretty(title)
	return return_string

def hackaday():

	url = "https://hackaday.com/blog/"
	response = requests.get(url)
	soup = BeautifulSoup(response.content, "html.parser")
	links = soup.find_all('h1')
	i = 0
	return_string=''
	title = links[1].text
	return pretty(title)

def iss():

	req = Request("http://api.open-notify.org/iss-now.json")
	response = urlopen(req)
	obj = json.loads(response.read())

	lat = (obj['iss_position']['latitude'])
	lon = (obj['iss_position']['longitude'])

	coordinates = (lat,lon)
	results=rg.search((lat,lon))
	location = results[0]
	city = location.get('name')
	prov1= location.get('admin1')
	prov2 = location.get('admin2')
	cc = location.get('cc')
	country = coco.convert(names = cc, to = 'name_short')
	title = centerstr("ISS LOCATION")
	closeloc1 = city+","+prov1
	closeloc2 = country
	return_string = title+"&"+dummy+"&"+closeloc1+"&"+closeloc2
	return return_string

def topsearch():
	url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
	response = requests.get(url)
	soup = BeautifulSoup(response.content, "lxml")
	titles = soup.find_all("title")
	list = []
	return_string = ""
	for title in titles:
		list.append(title.text)
	for i in range (1,5):
		return_string = return_string + list[i]
		if i < 4:
			return_string = return_string + "&"
	return return_string

do_forever()
