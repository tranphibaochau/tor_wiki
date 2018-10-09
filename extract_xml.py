try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree
import csv
import sys

#tree = ET.parse("euwiki-20180301-stub-meta-history.xml")
#parse the xml file as a tree and reads it chunk by chunk (so that big files can be handled)
"""for event, elem in etree.iterparse("euwiki-20180301-stub-meta-history.xml", events=('start', 'end', 'start-ns', 'end-ns')):
  print (event, elem)
  if (elem.tag == "siteinfo"):
  	print(elem.text)
#Resident_data.close()"""

source = sys.argv[1]
context = etree.iterparse(source, events=('start', 'end'))
 
for event, elem in context:
	tag = elem.tag.split("}")[1]
	if (tag == "sitename" and (event == 'start')):
		siteinfo = elem.text
	if (tag == "dbname" and (event == 'start')):
		dbname = elem.text
	if (tag == "title" and (event == 'start')):
		title = elem.text
	if (tag == "title" and (event == 'start')):
		title = elem.text
	if (tag == "revision" and (event == 'end')):
		timestamp =""
		revid = ""
		user = ""
		for tags in elem:
			t = tags.tag.split("}")[1]
			if (t == "timestamp"):
				timestamp = tags.text[:-1]
				timestamp = timestamp.replace("T", " ")
			if (t == "id"):
				revid = tags.text
			if (t == "contributor"):
				try: 
					user = tags[0].text
				except:
					user = "Unabled to Parse"
		try:
			print(revid + "\t" + user + "\t" + timestamp + "\t" + title + "\t" + siteinfo + "\t" + dbname)
			elem.clear()
		except:
			pass
			elem.clear()