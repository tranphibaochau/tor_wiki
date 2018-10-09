import csv
import os
import socket
import pandas as pd
import numpy as np
import sys
from datetime import *
dict1 = {}
revisions = []
#Read tor_wiki_edits file
wiki_edits = pd.read_csv(sys.argv[1], delimiter="\t", quotechar='"', header = None, names = ['revid', 'editor', 'datetime', 'reverted'])
for index, line in wiki_edits.iterrows():

	tor_ip = line['editor']
	#print(tor_ip)
	publish_date = line['datetime']
	#print(publish_date)
	#check if tor_ip already exists in current database and update the latest revision date
	if tor_ip in dict1:
		if publish_date > dict1[tor_ip]:
			dict1[tor_ip] = publish_date
	else:
		dict1[tor_ip] = publish_date
#print(dict1)
#Read block events on blocked_ips data file
wikiq_reader = pd.read_csv(sys.argv[2], delimiter="\t", quotechar='"', header = None, names = ['id', 'user', 'action', 'date', 'comment'])
with open(sys.argv[3], 'w') as file:
	for index, line in wikiq_reader.iterrows():
		string = ""
		users = line['user']
		#if IP address is detected in username, check to see if it is in the previous dictionary
		try:
			blocked_ip = users.split(":")
			blocked_ip = blocked_ip[1]
			socket.inet_aton(blocked_ip)
			block_date = line['date']
			print(block_date)
			if blocked_ip in dict1 and block_date < publish_date:
				print ("True")
				string += str(blocked_ip) + '\t' + str(dict1[blocked_ip]) + '\t' + str(line['action'])
				string += '\t' + str(block_date)[:10] + " "+ str(block_date)[11:] + "\t" + line['comment'] +'\n'
				file.write(string)
		except:
			pass
	file.close()


