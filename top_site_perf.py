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
urls = []

#spawn a thread pool to execute fetch for each url
def run_pool(target):
    '''
    param target: target function for each thread to execute
    '''

    pool = threadPool(50)
    pool.map_async(target, urls)
    pool.close()
    pool.join() 

#iterate through list and get only urls
def get_urls(url_file):
    '''
    param url_file: name of file to open and acquire first 50 urls
    '''
    f = open(url_file, 'r')
    num_urls = 50
    for line in f.readlines():
	site_search = re.match(r'\d+\s+(\S+)', line)
        if site_search and num_urls > 0:
            formatted_url = 'http://' + site_search.group(1)
            urls.append(formatted_url)
            num_urls = num_urls - 1
    return urls

#make urlopen request, if successful append download_time, size, and url to final_list. Some urls might lead to dead pages, so skip them.
def fetch(url):
    '''
    param url: a string containing the url to send with request
    '''

    start = time.clock()  
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

#gets the median of either the speed or the size
def get_median(url_list, type=None):
    '''
    param url_list: a list of urls sorted by their download speed
    param type:     None by default, speed if requesting median of webpage download speeds, size if requesting median of webpage sizes
    '''
    
    if type is 'speed':
        return (final_list[25][0] + final_list[26][0])/2
    if type is 'size':
        return (final_list[25][1] + final_list[26][1])/2

# print output of data
def print_output(fast_5_sites, slow_5_sites, med_speed, med_size):
    '''
    param fast_5_sites: list of 5 fastest webpages
    param slow_5_sites: list of 5 slowest webpages
    param med_speed:    integer containing median speed of download
    param med_size:     integer containing median size of webpages
    '''
    
    print 'Fasted 5 Sites:'
    for obj in fast_5_sites:
        print obj[2], str(obj[1]) + 'kb', str(obj[0]) + 's'
    print 'Slowest 5 Sites:'
    for obj in slow_5_sites:
        print obj[2], str(obj[1]) + 'kb', str(obj[0]) + 's'
    print ('Median Homepage Size: %skb')%str(med_size)
    print ('Median Download Speed: %ss')%str(med_speed)

#gets key to sort list on
def getKey(item):
    return item[0]

if __name__ == '__main__':
    input_file = str(sys.argv[1])
    urls = get_urls(input_file)
    run_pool(fetch)
    sorted_list = sorted(final_list, key=getKey)
    fast_5 = sorted_list[:5]
    slow_5 = sorted_list[-5:]
    median_speed = get_median(sorted_list, type='speed')
    median_size = get_median(sorted_list, type='size')
    print_output(fast_5, slow_5, median_speed, median_size)
