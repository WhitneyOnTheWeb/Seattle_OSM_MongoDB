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
OSM_NAME = "seattle_washington.osm"
OSM_FILE = open(OSM_NAME, "rb")

SAMPLE_NAME = "seattle_sample.osm"  # k = 30
SAMPLE_FILE = open(SAMPLE_NAME, "rb")

SMALL_SAMPLE_NAME = "seattle_small_sample.osm"  # k = 900
SMALL_SAMPLE_FILE = open(SMALL_SAMPLE_NAME, "rb")

# Street Types in Addresses
st_types = defaultdict(set)

# Regexes
REGEX_ST_TYPE = re.compile(r'\b\S+\.?$', re.IGNORECASE)
REGEX_LOWER = re.compile(r'^([a-z]|_)*$')
REGEX_LOWER_COLON = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
REGEX_PROBLEMCHAR = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Metadata
METADATA = [ 'version', 'changeset', 'timestamp', 'user', 'uid', 'id']


# Street Types in Addresses
st_types = defaultdict(set)
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types = defaultdict(set)

expected_street_types = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]


'''
    Reference:  Udacity
'''
tiger = {}

def tag_attributes(f):
    attribs = []
    for ev, elem in xET.iterparse(f):
        if elem.tag == 'way' or elem.tag == 'node': # Specify parent tag to filter nested tag list
            for t in elem.iter('tag'):
            #Iterate through tag types, adding new ones to the set for the parent tag
                if t.attrib['k'] not in attribs:
                    if REGEX_LOWER.search(t.attrib['k']): # Only add values for lowercase attributes
                        attribs.append(t.attrib['k'])
    return attribs

#attributes = tag_attributes(SMALL_SAMPLE_NAME)
#pprint.pprint(sorted(attributes))

def shape_element(element):
    node = {
        "id": None, 
        "type": None,
        'name': None,
        'amenity': None,
        'building' : None,
        'shop' : None,
        'cuisine' : None,
        'phone' : None,
        "created": {
            "changeset": None, 
            "user": None, 
            "version": None, 
            "uid": None, 
            "timestamp": None
        },
        "pos": [None, None],
        "refs": [None],
        "address": {
                  "housenumber": None,
                  "postcode": None,
                  "street": None,
                  "state": None,
                  "city": None,
                },
        "tiger": { 
                 'country': None,
                 'name_base': None,
                 'name_base_1': None,
                 'name_base_2': None,
                 'name_base_3': None,
                 'name_direction_prefix': None,
                 'name_direction_prefix_1': None,
                 'name_direction_prefix_2': None,
                 'name_direction_prefix_3': None,
                 'name_direction_suffix': None,
                 'name_direction_suffix_1': None,
                 'name_direction_suffix_2': None,
                 'name_direction_suffix_3': None,
                 'name_type': None,
                 'name_type_1': None,
                 'name_type_2': None,
                 'name_type_3': None,
                 'zip_left': None,
                 'zip_right': None,
                }
        }       
    refs = []

    if element.tag == "node" or element.tag == "way":
        node['id'] = element.attrib['id'] # Get node ID
        node['type'] = element.tag        # Get node type (node or way)
        
        if 'lat' in element.attrib:       # Get node position (lat/lon)
            node['pos'] = [ast.literal_eval(element.attrib['lat']), 
                           ast.literal_eval(element.attrib['lon'])]
            
        for m in METADATA:                # Get 'created' metadata
            if m in element.attrib:
                node['created'][m] = element.attrib[m]
        
        for nd in element.iter('nd'):     # Iterate through nodes references
            refs.append(nd.attrib['ref'])
        if refs != []:
            node['refs'] = refs
        else:
            node['refs'] = None
            
        for a in element.iter('tag'):             # Check each child tag for attributes
            k = a.attrib['k']
            if not(REGEX_PROBLEMCHAR.search(k)):  # Filter out tags with invalid characters
                if k.startswith('addr:'):
                    el = k.split(':')
                    if el[1] == 'street':
                        clean_street = update_name(a.attrib['v'], mapping) #Clean Street Types
                        node['address'][el[1]] = clean_street
                    else:
                        node['address'][el[1]] = a.attrib['v'] # Add other address parts
                elif k.startswith('tiger:'):      # Get TIGER address info
                    el = k.split(':')
                    if el[1] == 'name_type':
                        clean_type = update_name(a.attrib['v'], mapping) #Clean Street Types
                        node['tiger'][el[1]] = clean_type
                    elif el[1] in node['tiger'].keys():
                        node['tiger'][el[1]] = a.attrib['v'] # Add other tiger parts
                else:
                    if k in node.keys():
                        node[k] = a.attrib['v'] # Add key/value for all other attributes found  
                        
                #if node['tiger']['name_type'] != None:
                #    pprint.pprint(node)
        return node
    else:
        return None


def update_name(name, mapping):
    n = street_type_re.search(name)
    n = n.group()
    for m in mapping:
        if n == m:
            name = name[:-len(n)] + mapping[m]
    return name    
    
def process_map(file_in, pretty = False):
    json_file = file_in + ".json"
  
    data = []
    with codecs.open(json_file, "w") as fo:
        for _, element in xET.iterparse(file_in + '.osm'):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    
    #file_info = os.stat(json_file)
    #size = convert_bytes(file_info.st_size)

    return data

def shape_data():
    file_name = SAMPLE_NAME.split('.')
    json_file = file_name[0] + ".json"
    
    data = process_map(file_name[0], False)
    
    print(json_file, 'created:')
    print('File size: ', file_size(json_file))
    print ('\n\n\n')
    print('Sample Shape:')    
    pprint.pprint(data[1])
    #pprint.pprint(data[5020:5240])
    pprint.pprint(data[-1])
    
shape_data()
