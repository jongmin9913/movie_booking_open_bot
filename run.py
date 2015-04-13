import tweepy
import get_interpark
import os

def tweet(twitter_api, status, movie_dic):
	print status + ' ' + str(len(movie_dic.keys()))
	
	for item in movie_dic.keys():
		text = ''
		sp = item.rfind('" ')
		if status == 'Open':
			text += 'Open\n' + item[sp+2:] + ' (' + str(movie_dic[item]) + ')\n' + item[:sp+1]
		elif status == 'Change':
			text += 'Change\n' + item[sp+2:] + ' (' + str(movie_dic[item]) + ')\n' + item[:sp+1]
		elif status == 'Close':
			text += 'Close\n' + item[sp+2:] + '\n' + item[:sp+1]
		#print text
		api.update_status(status=text)

def loadConfigure():
	filename = 'config.txt'
	if not os.path.exists(filename):
		print 'need config.txt : use config.txt.sample'
		return (False, None)
		
	f = open(filename, 'r')
	
	config_dic = {}
	
	while 1: 
		line = f.readline()
		if not line: break
		text = line.decode('utf-8').split('=')
		if len(text) < 2:
			continue
		
		key = text[0].strip('\n')
		value = text[1].strip('\n')
		#print key.encode('utf-8'), value.encode('utf-8')
		config_dic[key] = value
		
	f.close()
	
	return (True, config_dic)
		
if __name__ == "__main__":
	(ret, config_dic) = loadConfigure()
	
	if ret == True:
		auth = tweepy.OAuthHandler(config_dic['CONSUMER_KEY'], config_dic['CONSUMER_SECRET'])
		auth.set_access_token(config_dic['ACCESS_KEY'], config_dic['ACCESS_SECRET'])
		api = tweepy.API(auth)

		(close_list, open_list, change_list) = get_interpark.run()
		tweet(api, 'Close', close_list)
		tweet(api, 'Change', change_list)
		tweet(api, 'Open', open_list)
			
		#api.update_status(status='#test run')
	
	
