#!/usr/bin/env python


import urllib2
import httplib
import sys
import time
import socket
import threading
import Queue
import re
from multiprocessing.dummy import Pool as threadPool

final_list = []
urls = Queue.Queue()

#spawn a thread pool to execute fetch for each url
def run_parallel(target, args_list):
    pool = threadPool(50)
    #while there is still urls in the queue
    while not urls.empty():
        pool.apply_async(target, [urls])
    pool.close()
    pool.join() 

#iterate through list and get only urls
def get_urls(url_file):
    f = open(url_file, 'r')
    for line in f.readlines():
	site_search = re.match(r'\d+\s+(\S+)', line)
        if site_search and urls.qsize() < 51:
            formatted_url = 'http://' + site_search.group(1)
            urls.put(formatted_url)
    return urls


#make urlopen request, if successful append download_time, size, and url to final_list
def fetch(urls):
    start = time.clock()
    url = urls.get()
    try:
        response = urllib2.urlopen(url)
    except (urllib2.URLError, urllib2.HTTPError, httplib.HTTPException, Exception, httplib.IncompleteRead, socket.timeout), e:
        response = None
        pass	
    except:
        response = None
        pass
    download_time = time.clock() - start
    if response:
        #convert size to kb
	size = (len(response.read()))/(1<<10)
        final_list.append((download_time, size, url))
        return True

def get_median(url_list, type=None):
    if type is 'speed':
        median = (final_list[25][0] + final_list[26][0])/2
    if type is 'size':
        median = (final_list[25][1] + final_list[26][1])/2
    return median

def getKey(item):
    return item[0]

if __name__ == '__main__':
    input_file = str(sys.argv[1])
    urls = get_urls(input_file)
    run_parallel(fetch, urls)
    sorted_list = sorted(final_list, key=getKey)
    top_5 = sorted_list[:5]
    bottom_5 = sorted_list[-5:]
    median_speed = get_median(sorted_list, type='speed')
    median_size = get_median(sorted_list, type='size')
