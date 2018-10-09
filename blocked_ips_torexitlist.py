import csv
import os
import socket
import pandas as pd
import numpy as np
import sys
from datetime import *
dict1 = {}
revisions = []
wiki_edits = pd.read_csv(sys.argv[1], delimiter=",", quotechar='"', header = None, names = ['exitaddress', 'publish_date', 'last_status', 'days_active', 'exit_node', 'numberofexitnodes', 'date'])
for index, line in wiki_edits.iterrows():
	tor_ip = line['exitaddress']
	publish_date = line['publish_date']
	#check if tor_ip already exists in current database and update the latest revision date
	dict1[tor_ip] = publish_date
wikiq_reader = pd.read_csv(sys.argv[2], delimiter="\t", quotechar='"', header = None, names = ['id', 'user', 'action', 'date', 'comment'])
with open(sys.argv[3], 'w') as file:
	for index, line in wikiq_reader.iterrows():
		string = ""
		users = line['user']
		
		try:
			blocked_ip = users.split(":")
			blocked_ip = blocked_ip[1]
			socket.inet_aton(blocked_ip)
			block_date = np.datetime64(line['date'])
			if blocked_ip in dict1 and block_date > np.datetime64(dict1[blocked_ip]):
				string += str(blocked_ip) + '\t' + str(dict1[blocked_ip]) + '\t' + str(line['action'])
				string += '\t' + str(block_date)[:10] + " "+ str(block_date)[11:] + "\t" + line['comment'] +'\n'
				file.write(string)
		except:
			pass
	file.close()
		# block_date = line['date']
		# try:
		# 	block_date = datetime.strptime(block_date, '%Y-%m-%d')
		# except:
		# 	print("can't convert to datetime")
# 	except socket.error:
# 		# Not legal
# 	published_date = dict1.get(ip)
# 	try:
# 		published_date = published_date.split()
# 		published_date = datetime.strptime(published_date[0], '%Y-%m-%d')
# 	except:
# 		print("can't convert to datetime")
# 	try:
# 		delta = revision_date - published_date
# 		li[2] = li[2] + ' ' + li[3]
# 		li[3] = li[4]
# 		li[4] = delta.days
# 	except:
# 		li.append('DaysSincePublished')
# 	new_data.append(li)
# #print(new_data)
# for item in new_data:
	
# 	string = ""
# 	for x in range(4):
# 		string += str(item[x]) + '\t'
# 	string += str(item[4]) + '\n'
# 	file3.write(string)

