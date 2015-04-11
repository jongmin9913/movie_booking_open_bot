# -*- coding: utf8 -*-
import httplib, urllib
import sys
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
from datetime import date
import os.path

def get_list_from_megabox():
	today_str = date.today().isoformat()

	## get list from megabox
	params = urllib.urlencode({'type': 'movie', 'playDate': today_str, 'startNo': '0', 'count': '100', 'sortBy': 'rank'})
	headers = {"Content-type": "application/x-www-form-urlencoded","charset": "UTF-8"}
	conn = httplib.HTTPConnection("www.megabox.co.kr")
	conn.request("POST", "/pages/booking/step1/Booking_SelectMovie_List.jsp", params, headers)
	response = conn.getresponse()

	#print response.status, response.reason

	## make current movie list
	return response.read().decode('utf-8')
	
def make_current_movie_list(data):
	soup = BeautifulSoup(data)
	cur_movie_list = set()
	for item in soup.find_all('li'):
		cur_movie_list.add(item['data-title'])
	return cur_movie_list

def load_previous_movie_list():
	## load previous movie list
	prev_movie_list = set()
	
	filename = 'list_megabox.txt'
	if not os.path.exists(filename):
		return prev_movie_list
		
	f = open(filename, 'r')
	
	while 1: 
		line = f.readline()
		if not line: break
		prev_movie_list.add(line.decode('utf-8').strip('\n'))
	
	#lines = f.readlines()
	#for item in lines:
	#	prev_movie_list.add(item.decode('utf-8'))
	f.close()	
	return prev_movie_list

def write_movie_list_file(cur_movie_list):
	## write file : current movie list 
	f = open('list_megabox.txt', 'w')
	for item in cur_movie_list:
		f.write(item.encode('utf-8'))
		f.write('\n')
	f.close()

def print_set(movie_set):
	for item in movie_set:
		print item

def run():
	raw_data = get_list_from_megabox()	
	cur_movie_list = make_current_movie_list(raw_data)	
	prev_movie_list = load_previous_movie_list()	
	write_movie_list_file(cur_movie_list)		
	
	close_list = prev_movie_list - cur_movie_list
	#print 'close_list : '
	#print_set(close_list)
	
	open_list = cur_movie_list - prev_movie_list
	#print 'open_list : '
	#print_set(open_list)
	return (close_list, open_list)
	#return (cur_movie_list, prev_movie_list)

if __name__ == "__main__":
	run()