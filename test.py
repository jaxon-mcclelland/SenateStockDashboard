import xml
from xml.etree.ElementTree import ElementTree
import requests
from xml.etree import ElementTree as ET

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
}
generalSenatorData = requests.get('https://www.senate.gov/general/contact_information/senators_cfm.xml',headers=headers).content


xmltree = ET.fromstring(generalSenatorData)
'''
first_names = []
for member in xmltree.iter(tag='first_name'):
    first_names.append(member)
last_names = []
for member in xmltree.iter(tag='last_name'):
    last_names.append(member)
party = []
for member in xmltree.iter(tag='party'):
    party.append(member)
state = []
for member in xmltree.iter(tag='state'):
    state.append(member)

new_dict = {}


for member in xmltree:
    if member is not None:
        print(member[0].text)
'''
list = xmltree.findall('member')
for item in list:
    print('Name', item.find('last_name').text)
    print('Party', item.find('party').text)