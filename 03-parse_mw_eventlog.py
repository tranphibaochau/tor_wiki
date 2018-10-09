#!/usr/bin/env python3

import re
import sys
import os.path

from xml.sax import handler, make_parser
from xml.sax.saxutils import XMLFilterBase
from collections import defaultdict
import calendar

class WikiLogItem(object):
    """
    Holds data related to one <logitem> element parsed from the dump
    """
    __slots__ = (
        'id',
        'action',
        'type',
        'timestamp',
        'logtitle',
        'comment',
        'params',
        'username',
        'userid',
        'contrib_deleted'
    )
    def __init__(self):
        for attr in self.__slots__:
            setattr(self, attr, '')

    def __str__(self):
        return repr({k: getattr(self, k) for k in self.__slots__})

class text_normalize_filter(XMLFilterBase):
    """
    SAX filter to ensure that contiguous texts nodes are merged into one
    That hopefully speeds up the parsing process a lot, specially when
    reading revisions with long text
    
    Recipe by Uche Ogbuji, James Kew and Peter Cogolo Retrieved from: Python
    Cookbook, 2nd ed., by Alex Martelli, Anna Martelli Ravenscroft, and
    David Ascher (O'Reillly Media, 2005) 0-596-00797-3
    """
    def __init__(self, upstream, downstream):
        XMLFilterBase.__init__(self, upstream)
        self._downstream=downstream
        self._accumulator=[]
    def _complete_text_node(self):
        if self._accumulator:
            self._downstream.characters(''.join(self._accumulator))
            self._accumulator=[]
    def characters(self, text):
        self._accumulator.append(text)
    def ignorableWhiteSpace(self, ws):
        self._accumulator.append(text)

def _wrap_complete(method_name):
    def method(self, *a, **k):
        self._complete_text_node()
        getattr(self._downstream, method_name)(*a, **k)
    method.__name__= method_name
    setattr(text_normalize_filter, method_name, method)

for n in '''startElement endElement'''.split():
    _wrap_complete(n)

class WikiDumpHandler(handler.ContentHandler):
    """
    A ContentHandler designed to pull out page ids, titles and text from
    Wiki pages. These are assembled into WikiLogItem objects and sent off to
    the supplied callback.
    """
    def __init__(self, logItemCallBack=None):
        handler.ContentHandler.__init__(self)
        self.currentTag = ''
        self.insideContribTag = False
        self.logItemCallBack = logItemCallBack
        self.logItemsProcessed = 0

    def startElement(self, name, attrs):
        self.currentTag = name
        if (name == 'logitem'):
            # add a log item
            self.currentLogItem = WikiLogItem()
        elif (name == 'contributor'):
            # when we're in revision, ignore ids
            self.insideContribTag = True
            if 'deleted' in attrs:
                self.currentLogItem.contrib_deleted = True
            else:
                self.currentLogItem.contrib_deleted = False

    def endElement(self, name):
        if (name == 'logitem'):
            if self.logItemCallBack is not None:
                self.logItemCallBack(self.currentLogItem)
            self.logItemsProcessed += 1
        elif (name == 'contributor'):
            # we've finished the revision section
            self.insideContribTag = False
        self.currentTag = ''

    def characters(self, content):
        if (self.currentTag == 'id' and not self.insideContribTag):
            self.currentLogItem.id = content
        elif (self.currentTag == 'id' and self.insideContribTag):
            self.currentLogItem.userid = content
        elif (self.currentTag == 'username' and self.insideContribTag):
            self.currentLogItem.username = content
        elif (self.currentTag == 'action'):
            self.currentLogItem.action = content
        elif (self.currentTag == 'type'):
            self.currentLogItem.type = content
        elif (self.currentTag == 'logtitle'):
            self.currentLogItem.logtitle = content
        elif (self.currentTag == 'timestamp'):
            self.currentLogItem.timestamp = content
        elif (self.currentTag == 'comment'):
            self.currentLogItem.comment = content
        elif (self.currentTag == 'params'):
            self.currentLogItem.params = content

class logExporter:
    def __init__(self, input, output_base="output"):
        self.input_file = input
        self.move_log = open(output_base + "-moves.tsv", "w")
        self.prot_log = open(output_base + "-protections.tsv", "w")
        self.del_log = open(output_base + "-deletions.tsv", "w")

        self.prot_titles = defaultdict(None)

        self.cal_dict = {v: k for k,v in enumerate(calendar.month_name)}
        self.r_param_string = re.compile(r'\[(?P<right>\w+)=(?P<group>\w+)\] \((?P<period>.*?)\)+')
        self.r_expir_string = re.compile(r'expires (?P<hour>\d{2}):(?P<min>\d{2}), (?P<day>\d+) (?P<month>\w+) (?P<year>\d{4})')

        # this marks whether we have moved into late 2008
        # when material is being recorded consistently
        self.in_window = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.move_log.close()
        self.prot_log.close()
        self.del_log.close()

    def __flush(self):
        self.move_log.flush()
        self.prot_log.flush()
        self.del_log.flush()
        sys.stdout.flush()
        sys.stderr.flush()

    def __clean_timestamp(self, timestamp):
        timestamp = timestamp.replace("T", " ")
        timestamp = timestamp.replace("Z", "")

        return timestamp 

    def __clean_logItem(self, logItem):
        logItem.comment = re.sub(r'\s', r' ', logItem.comment)
        logItem.params = re.sub(r'\s', r' ', logItem.params)

        # add userid and username, but only if it's not deleted
        if logItem.contrib_deleted:
            logItem.userid = ""
            logItem.username = ""
        else:
            logItem.username = re.sub(r'\s', r' ', logItem.username)

        logItem.timestamp = self.__clean_timestamp(logItem.timestamp)
        
        return logItem
        
    def printDelete(self, logItem):
        logItem = self.__clean_logItem(logItem)

        output = [logItem.id, '"' + logItem.logtitle + '"',
                  logItem.action, logItem.timestamp]

        print("\t".join(output), file=self.del_log)

    def printMove(self, logItem):
        logItem = self.__clean_logItem(logItem)

        output = [logItem.id, logItem.timestamp,
                  '"' + logItem.params  + '"', # old location
                  '"' + logItem.logtitle + '"'] # new location
        print("\t".join(output), file=self.move_log)

        # add the title to the list of titles
        self.prot_titles[logItem.logtitle] = None

    def printProtect(self, logItem):
        logItem = self.__clean_logItem(logItem)

        param_string = logItem.params
        rights = {}

        for m in self.r_param_string.finditer(param_string):
            right = m.group("right")
            group = m.group("group")
            raw_period = m.group("period")

            if not re.search("indefinite", raw_period):
                m2 = self.r_expir_string.match(raw_period)
                period_nums = [int(x) for x in [m2.group("year"),
                                                self.cal_dict[m2.group("month")],
                                                m2.group("day"),
                                                m2.group("hour"),
                                                m2.group("min")]]
                period_nums = tuple(period_nums)
                period = "%d-%02d-%02d %02d:%02d:00" % period_nums
            else:
                period = ""

            rights[right] = (group, period)

        output = [logItem.id, '"' + logItem.logtitle + '"',
                  logItem.action, logItem.timestamp]

        for right in rights:
            group, expir = rights[right]
            print("\t".join(output + [right, group, expir]),
            file=self.prot_log)

        # add the title to the list of titles
        self.prot_titles[logItem.logtitle] = None

    def printUnprotect(self, logItem):
        logItem = self.__clean_logItem(logItem)

        output = [logItem.id, '"' + logItem.logtitle + '"', 
                  logItem.action, logItem.timestamp,
                  '', '', '']
        print("\t".join(output), file=self.prot_log)

        # remove the current title from the list of titles
        self.prot_titles.pop(logItem.logtitle, None)

    def conditionallyPrint(self, logItem):
        # print deletions only if we've seen a protection event
        if logItem.type == 'delete' \
            and logItem.logtitle in self.prot_titles:
            self.printDelete(logItem)

        elif logItem.type == "protect":
            if logItem.action == "move_prot":
                self.printMove(logItem)

            elif logItem.action == "protect" \
                or logItem.action == "modify":

                # this limits it to only things after 2008 when this
                # data started being stored in params
                if not logItem.params:
                    return
                else:
                    self.in_window = True
                    self.printProtect(logItem)

            elif logItem.action == "unprotect":
                if self.in_window: self.printUnprotect(logItem)

            else:
                # this is some kind of error so we'll print the article and
                # return
                print(logItem, file=sys.stderr)


def parseWithCallback(incoming_data, callback):
    parser = make_parser()
    parser.setFeature(handler.feature_namespaces, 0)

    # apply the text_normalize_filter
    wdh = WikiDumpHandler(logItemCallBack=callback)
    filter_handler = text_normalize_filter(parser, wdh)

    filter_handler.parse(incoming_data)

if __name__ == "__main__":
    """
    When called as script, argv[1] is assumed to be a filename and we
    simply print pages found. If it's missing, we just use sys.stdin
    instead.
    """

    if len(sys.argv) > 1:
        input_file = open(sys.argv[1], "r")
        output_base = re.sub(r'\.\w+$', '', os.path.basename(sys.argv[1]))
    else:
        input_file = sys.stdin
        output_base = "output"

    with logExporter(input_file, output_base) as exporter:
        parseWithCallback(input_file, exporter.conditionallyPrint)

