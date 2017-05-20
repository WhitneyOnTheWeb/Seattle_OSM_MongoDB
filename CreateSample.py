# Python Modules
import xml.etree.cElementTree as xET
from collections import defaultdict
import csv
import os
import pprint
import re
import codecs
import json
import ast

# OSM Files
PATH = 'C:\JupyterNotebook\MongoDB\\'  ###CHANGE THIS TO LOCAL DIRECTORY FOR OSM FILE###

OSM_NAME = "seattle_washington.osm"
OSM_FILE = open(PATH + OSM_NAME, "rb")

SAMPLE_NAME = "seattle_sample.osm"  # k = 30
SAMPLE_FILE = open(PATH + SAMPLE_NAME, "rb")

SMALL_SAMPLE_NAME = "seattle_small_sample.osm"  # k = 900
SMALL_SAMPLE_FILE = open(PATH + SMALL_SAMPLE_NAME, "rb")


# Street Types in Addresses
st_types = defaultdict(set)


# Paramenter: k-th top level element
k = 900  # Larger number, small sample

def get_element(OSM_NAME, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = xET.iterparse(OSM_NAME, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def create_sample():
    with open(PATH + SMALL_SAMPLE_NAME, 'wb') as output:
        output.write(bytes('<?xml version="1.0" encoding="UTF-8"?>\n', encoding="utf-8"))
        output.write(bytes('<osm>\n  ', encoding="utf-8"))

        # Write every 10th top level element
        for i, element in enumerate(get_element(OSM_NAME)):
            if i % k == 0:
                output.write(xET.tostring(element, encoding='utf-8'))

        output.write(bytes('</osm>', encoding="utf-8"))
        
        print(SMALL_SAMPLE_NAME, 'created:')
        print('File size: ', file_size(SMALL_SAMPLE_NAME))
        
       
    
def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    
    Reference:
    http://stackoverflow.com/questions/2104080/how-to-check-file-size-in-python
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            size = "%3.1f %s" % (num, x)
            return size
        num /= 1024.0
        
        

def file_size(SMALL_SAMPLE_NAME):
    """
    this function will return the file size
    
    Reference:
    http://stackoverflow.com/questions/2104080/how-to-check-file-size-in-python
    """
    file_info = os.stat(PATH + SMALL_SAMPLE_NAME)
    size = convert_bytes(file_info.st_size)
    return size

create_sample()