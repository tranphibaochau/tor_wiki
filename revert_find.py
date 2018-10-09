import csv
import os
import socket
import pandas as pd
import numpy as np
import sys
from datetime import *
dict1 = {}
revisions = []
#Read revert_list to find revisions that were reverted
with open(sys.argv[1], 'r') as file:
    for line in file:
        revisions.append(line[:-1])
#open a file to store the output
    #read tor_wiki_edits and match with revert_list
wiki_edits = pd.read_csv(sys.argv[2], delimiter="\t", quotechar='"', header = None, names = ['revid', 'editor', 'datetime', 'reverted'])
for index, line in wiki_edits.iterrows():
    s =""
    revid = line['revid']
    if revid in revisions:
        s = str(line['revid']) + "\t" + str(line['editor']) + "\t" + str(line['datetime']) + "\t" +str(line['reverted']) + "\t" + "True"

    else:
        s = str(line['revid']) + "\t" + str(line['editor']) + "\t" + str(line['datetime']) + "\t" + str(line['reverted']) + "\t" + "False" 
    print(s)
file.close()



