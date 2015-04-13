# -*- coding: utf8 -*-
import httplib, urllib
import sys
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
from datetime import date
import os.path
import re

def get_list_from_interpark():
	today_str = date.today().isoformat()

	## get movie code
	params = ''
	headers = {"Content-type": "text/html"}
	conn = httplib.HTTPConnection("movie.interpark.com")
	conn.request("GET", "/Movie/2.0/WebControl/MovieSelect.asp?Type=M&From", params, headers)
	response = conn.getresponse()

	#print response.status, response.reason

	## make current movie list
	return response.read()
	
def extract_movie_code(data):
	soup = BeautifulSoup(data)
	movie_code_dic = {}
	p = re.compile('GroupCode : "(.*?)", GroupName : "(.*?)",')
	for item in soup.find_all('script'):
		m = p.findall(item.text)
		#print len(m)
		for m_code in m:			
			movie_code_dic[m_code[0]] = m_code[1].encode('utf-8').decode('utf-8')

	return movie_code_dic
	
def get_date_list(movie_code):
	return ['20150413']

	#params = ''
	#headers = {"Content-type": "text/html"}
	#conn = httplib.HTTPConnection("movie.interpark.com")
	#url = '/Movie/2.0/WebControl/DateSelect.asp?Type=M&GroupCode=' + movie_code
	#conn.request("GET", url, params, headers)
	#response = conn.getresponse()
	#
	#soup = BeautifulSoup(response.read())
	#date_list = []
	#p = re.compile('TheaterDate\.PlayDate\.push\(\'(.*?)\'\)')
	#for item in soup.find_all('script'):
	#	m = p.findall(item.text)
	#	#print len(m)
	#	for m_code in m:
	#		date_list.append(m_code)
	#return date_list
	
	
def parse_theater_info(movie_name, raw_data):
	soup = BeautifulSoup(raw_data)
	theater_dic = {}
	p = re.compile('Region : "42001", .* PlaceName : "(.*?)"')
	for item in soup.find_all('script'):
		m = p.findall(item.text)
		for m_code in m:
			data = m_code.encode('utf-8').decode('utf-8').split(' ')
			if len(data) < 2:
				continue
			theater_name = '"' + movie_name + '" ' + data[0] + ' ' + data[1]
			#print theater_name
			if theater_name in theater_dic:
				theater_dic[theater_name] += 1
			else:
				theater_dic[theater_name] = 1
	
	return theater_dic
	
def get_theater_movie_list(movie_code_dic):
	#today_str = date.today().strftime("%Y%m%d")
	
	current_dic = {}	
	f = open('list_interpark.txt', 'w')
	
	for movie_code in movie_code_dic.keys():		
		date_list = get_date_list(movie_code)
		for target_date in date_list:
			params = ''
			headers = {"Content-type": "text/html"}
			conn = httplib.HTTPConnection("movie.interpark.com")
			url = '/Movie/2.0/WebControl/TheaterDateSelect.asp?Type=M&GroupCode=' + movie_code + '&PlayDate=' + target_date
			conn.request("GET", url, params, headers)
			response = conn.getresponse()
			#print movie_code_dic[movie_code]
			info_dic = parse_theater_info(movie_code_dic[movie_code], response.read())
			current_dic.update(info_dic)
			
	for name in sorted(current_dic.keys()):
		text = name.encode('utf-8') + ' (' + str(current_dic[name]) + ')'
		f.write(text)
		f.write('\n')
		
	f.close()
	return current_dic
	

def load_previous_movie_list():
	## load previous movie list
	prev_movie_dic = {}
	
	filename = 'list_interpark.txt'
	if not os.path.exists(filename):
		return prev_movie_dic
		
	f = open(filename, 'r')
	
	while 1: 
		line = f.readline()
		if not line: break
		text = line.decode('utf-8').strip('\n')
		sp = text.rfind(' ')
		name = text[:sp]
		value = text[sp:].replace('(','').replace(')','')
		#print name, value
		prev_movie_dic[name] = int(value)
	
	f.close()	
	return prev_movie_dic

def write_movie_list_file(cur_movie_dic):
	## write file : current movie list 
	f = open('list_interpark.txt', 'w')
	for key in cur_movie_dic.keys():
		text = key + ' (' + str(cur_movie_dic[key]) + ')'
		f.write(text.encode('utf-8'))
		f.write('\n')
	f.close()

def print_set(movie_set):
	for item in movie_set:
		print item

class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect 
    def removed(self):
        return self.set_past - self.intersect 
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])
		
def run():
	prev_movie_dic = load_previous_movie_list()
	print 'end load_previous_movie_list (size:' + str(len(prev_movie_dic.keys())) + ')'
	
	raw_data = get_list_from_interpark()
	print 'end get_list_from_interpark'
	
	movie_code = extract_movie_code(raw_data)
	print 'extract_movie_code (size:' + str(len(movie_code.keys())) + ')'
	
	cur_movie_dic = get_theater_movie_list(movie_code)
	print 'get_theater_movie_list (size:' + str(len(cur_movie_dic.keys())) + ')'
	
	write_movie_list_file(cur_movie_dic)
	print 'write_movie_list_file'
	
	#print prev_movie_dic.values()
	#print cur_movie_dic.values()
	
	differ = DictDiffer(cur_movie_dic, prev_movie_dic)
	
	add_dic = {}
	for name in differ.added():
		add_dic[name] = cur_movie_dic[name]
		
	remove_dic = {}	
	for name in differ.removed():
		remove_dic[name] = prev_movie_dic[name]
		
	change_dic = {}
	for name in differ.changed():
		change_dic[name] = cur_movie_dic[name]
	
	return (remove_dic, add_dic, change_dic)
	

if __name__ == "__main__":
	run()