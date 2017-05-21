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
from pymongo import MongoClient

# OSM Files
OSM_NAME = "seattle_washington.osm"
#OSM_FILE = open(OSM_NAME, "rb")

PATH = 'C:\JupyterNotebook\MongoDB\\'  ###CHANGE THIS TO LOCAL DIRECTORY FOR OSM FILE###
SAMPLE_NAME = "seattle_sample.osm"  # k = 30
SAMPLE_FILE = open(PATH + SAMPLE_NAME, "rb")

SMALL_SAMPLE_NAME = "seattle_small_sample.osm"  # k = 900
SMALL_SAMPLE_FILE = open(PATH + SMALL_SAMPLE_NAME, "rb")

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

			
mapping = { "St": "Street",
            "St.": "Street",
            'AVE': 'Avenue',
            'Ave': 'Avenue',
            'Ave.': 'Avenue',
            'Av.': 'Avenue',
            'ave': 'Avenue',
            'Blvd': 'Boulevard',
            'Blvd.': 'Boulevard',
            'boulevard': 'Boulevard',
            'CT': 'Court',
            'Ct': 'Court',
            'Dr': 'Drive',
            'Dr.': 'Drive',
            'E': 'East',
            'E.Division': 'East Division',
            'FI': 'Fox Drive',
            'Hwy': 'Highway',
            'K10': 'NE 8th Street',
            'MainStreet': 'N Main Street',
            'N': 'North',
            'NE': 'Northeast',
            'NW': 'Northwest',
            'nw': 'Northwest',
            'PL': 'Place',
            'Pl': 'Place',
            'Rd': 'Road',
            'RD': 'Road',
            'Rd.': 'Road',
            'S': 'South',
            'S.': 'South',
            'S.E.': 'Southeast',
            'SE': 'Southeast',
            'ST': 'Street',
            'SW': 'Southwest',
            'SW,': 'Southwest',
            'Se': 'Southeast',
            'southeast': 'Southeast',
            'St': 'Street',
            'st': 'Street',
            'street': 'Street',
            'St.': 'Street',
            'Ter': 'Terrace',
            'W': 'West',
            'west': 'West',
            'WA': '17625 140th Avenue Southeast',
            'WA)': 'US 101',
            'WY': 'Way'
            }
			

'''
    Reference:  Udacity
'''
tiger = {}

def file_size(SMALL_SAMPLE_NAME):
    """
    this function will return the file size
    
    Reference:
    http://stackoverflow.com/questions/2104080/how-to-check-file-size-in-python
    """
    file_info = os.stat(PATH + SMALL_SAMPLE_NAME)
    size = convert_bytes(file_info.st_size)
    return size
	
	
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
					elif el[1] == 'postcode':
                        cleanzip = update_zip(a.attrib['v'])
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

def update_zip(zipcode):
    if zipcode == "Olympia, 98501":
        zipcode = "98501"
    elif zipcode.startswith('V') or zipcode.startswith('v'):
            z1 = zipcode[:3]
            z2 = zipcode[-3:]
            zipcode = z1 + ' ' + z2
            zipcode = zipcode.upper()
    return zipcode

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

file_name = SMALL_SAMPLE_NAME.split('.')
json_file = file_name[0] + ".json"
	
def shape_data():  
    data = process_map(PATH + file_name[0], False)
    
    print(json_file, 'created:')
    print('File size: ', file_size(json_file))
    print ('\n\n\n')
    print('Sample Shape:')    
    pprint.pprint(data[1])
    #pprint.pprint(data[5020:5240])
    pprint.pprint(data[-1])
    
shape_data()

#Insert Data into MongoDB
data = process_map(file_name[0], False)
client = MongoClient()
db = client.SeattleOSM
collection = db.Sample
collection.insert_many(data)

json_file = file_name[0] + ".json"

#Original XML Sample File Size
print('XML File: ', str(os.path.getsize(PATH + SMALL_SAMPLE_NAME)/1024/1024), 'Mb')

#JSON File Size
print('JSON File: ', str(os.path.getsize(PATH + json_file)/1024/1024), 'Mb')

#Count nodes and ways
print('Number of nodes:', collection.find({"type":"node"}).count())
print('Number of ways:  ', collection.find({"type":"way"}).count())
print('Total entries:  ', collection.count())

#Count Unique Contributors
print('Unique Contributors: ', len(db.Sample.distinct("created.uid")))

#Top 10 Contributors
pl = [{"$group":{"_id": "$created.user",
                 "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}]
result = list(collection.aggregate(pl))
print('Top 10 User Contributors: ')
pprint.pprint(result)

#Count Non-Null Attributes
fields = ['id',
     'name',
     'amenity',
     'building',
     'shop',
     'phone',
     'pos']

for field in fields: #Iterates through basic field values to count non-null occurances of each
    print(field + ':', db.Sample.find({field:{"$ne": None}}).count())
	
#Types of Buildings
pl = [{"$group":{"_id": "$building",
                 "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}]
result = list(collection.aggregate(pl))
print('Counts of Building Types: ')
pprint.pprint(result)

#Types of Shops
pl = [{"$group":{"_id": "$shop",
                 "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}]
result = list(collection.aggregate(pl))
print('Counts of Shop Types: ')
pprint.pprint(result)

#Popular Cuisines
pl = [{"$match": {"amenity":"restaurant", 
                  "cuisine": {"$ne":None}}}, 
            {"$group":{"_id":"$cuisine", 
                       "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = list(collection.aggregate(pl))
print('Most Popular Types of Food: ')
pprint.pprint(result)
