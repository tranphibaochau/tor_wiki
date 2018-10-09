import sys
import re
import csv
import socket
import pandas as pd
import numpy as np

tor_nodes = pd.read_csv("/com/users/chau/tor_wikiedits/tor_nodes_2018.tsv", delimiter="\t", quotechar='"', header = None, names = ['IP_Adress', 'Published', 'LastStatus'], skiprows = 1)
nodes_dict = {}
print("moron")
#or_nodes = pd.DataFrame(columns = ['exitaddress', 'publish_date', 'last_status'])
for index, line in tor_nodes.iterrows():
    tor_ip = line['IP_Adress']
    publish_date = line['Published']
    last_status = line['LastStatus']
    nodes_dict[str(tor_ip)] = [str(publish_date), str(last_status)]

tor_nodes = pd.read_csv(sys.argv[1], delimiter="\t", quotechar='"', header = None, names = ['revid', 'editor', 'timestamp', 'title', 'sitename', 'dbname'])
for index, line in tor_nodes.iterrows():
    revid = str(line['revid'])
    editor = str(line['editor'])
    timestamp = np.datetime64(line['timestamp'])
    title = str(line['title'])
    sitename =str(line['sitename'])
    dbname = str(line['dbname'])
    try: 
        socket.inet_aton(editor)
        if editor in nodes_dict:
            s = nodes_dict[editor]
            p_date = np.datetime64(s[0])
            l_status = np.datetime64(s[1])
            if (timestamp > p_date):
                print (revid + "\t" + editor + "\t" + str(timestamp)+  "\t" +title + "\t" + sitename + "\t" + dbname)
    except:
        pass

