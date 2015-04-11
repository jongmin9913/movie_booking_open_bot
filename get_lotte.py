# -*- coding: utf8 -*-
import httplib, urllib
import sys
import os.path
from datetime import date
import xml.etree.ElementTree as ET
import json


def get_list_from_lotte():
	today_str = date.today().isoformat()

	## get list from megabox
	params = ''
	headers = {"Content-type": "application/json"}
	conn = httplib.HTTPConnection("www.lottecinema.co.kr")
	conn.request("POST", "/LHS/LHFS/Ticket/Selection/getmcddata.aspx", params, headers)
	response = conn.getresponse()

	#print response.status, response.reason

	## make current movie list
	json_data = json.loads(response.read())
	return json_data['movies']
	
def make_current_movie_list(data):
	cur_movie_list = set()
	for item in data:
		cur_movie_list.add(item['title'].encode('utf-8').decode('utf-8'))
		
	return cur_movie_list

def load_previous_movie_list():
	## load previous movie list
	prev_movie_list = set()
	filename = 'list_lotte.txt'
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
	f = open('list_lotte.txt', 'w')
	for item in cur_movie_list:
		f.write(item.encode('utf-8'))
		f.write('\n')
	f.close()

def print_set(movie_set):
	for item in movie_set:
		print item

def run():
	raw_data = get_list_from_lotte()	
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


