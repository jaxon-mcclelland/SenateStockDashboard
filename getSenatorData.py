from types import MemberDescriptorType
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame
from sqlalchemy import create_engine
from datetime import datetime
import re
import json
import os
import lxml
from xml.etree import ElementTree as ET

# TO DO: Get senator party and state info from this site: https://www.senate.gov/senators/ 
# will need to refine name data
# XML Link: https://www.senate.gov/general/contact_information/senators_cfm.xml

# Additional TO DO: Track bond purchases


rootUrl = 'https://efdsearch.senate.gov'
metadataUrl = rootUrl + '/search/'
landingPageUrl = rootUrl + '/search/home/'
endpointAPI = rootUrl + '/search/report/data/'
dataframeColumns = ['transaction_date', 'senatorName', 'party', 'state', 'symbol', 'transaction_type']

# example creds
dbUsername = 'root'
dbPassword = 'password'
dbHost = '127.0.0.1'
dbName = 'transactions'

dbEngine = create_engine('mysql://'+dbUsername+':'+dbPassword+'@'+dbHost+'/'+dbName)

def getGeneralData():
    headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    }
    generalSenatorData = requests.get('https://www.senate.gov/general/contact_information/senators_cfm.xml',headers=headers).content
    xmltree = ET.fromstring(generalSenatorData)
    xmltree = xmltree.findall('member')
    return xmltree

def findSenatorinfo(xmltree, senatorName):
    for item in xmltree:
        lastName = item.find('last_name').text
        if lastName in senatorName:
            return item

# obtain csrftoken and agree to prohibition agreement
def csrf(client: requests.Session) -> str:
    response = client.get(landingPageUrl)
    content = BeautifulSoup(response.text, 'lxml')
    formCSRF = content.find(attrs={'name': 'csrfmiddlewaretoken'})['value']
    payload = {
        'csrfmiddlewaretoken': formCSRF,
        'prohibition_agreement': '1'
    }
    client.post(landingPageUrl, data=payload, headers={'Referer': landingPageUrl})
    csrftoken = client.cookies['csrftoken']
    # redirects to 302 after above post request, and sets sessionid cookie in 302 reponse but doesn't work with requests for some reason
    client.cookies['sessionid'] = 'gASVGAAAAAAAAAB9lIwQc2VhcmNoX2FncmVlbWVudJSIcy4:1lPtAe:HdlLg5fQlBFem3FlnE-Z32WD9bw'
    return csrftoken

# obtain senator periodic transaction links
def getMetadata(client: requests.Session, index, offset):
    token = csrf(client)
    postData = {
        'start': str(index),
        'length': str(offset),
        'first_name': '',
        'last_name': '',
        'report_types': '[11]',
        'submitted_start_date': '01/01/2021 00:00:00',
        'submitted_end_date': '',
        'candidate_state': '',
        'senator_state': '',
        'office_id': '',
        'filer_types': '[]',
        'csrfmiddlewaretoken': token
    }
    response = client.post(endpointAPI, data=postData, headers={'Referer':metadataUrl, 'X-CSRFToken':token, 'X-Requested-With':'XMLHttpRequest'})
    jsonData = json.loads(response.text)
    return jsonData


# obtain report data and compile into dataframe
# TO DO: Add comments?
def getReportData(client: requests.Session, reportLink, generaldata) -> DataFrame:
    response = client.get(rootUrl + '/search/view/ptr/' + reportLink).text
    soup = BeautifulSoup(response, 'html.parser')
    
    senatorName = soup.find('h2', class_='filedReport')
    senatorName = re.findall(r'\((.+)\)',senatorName.get_text())
    senatorName = "".join(senatorName)

    item = findSenatorinfo(generaldata, senatorName)
    if item is None:
        party = '0'
        state = '0'
    else:
        senatorName = item.find('first_name').text + ' ' + item.find('last_name').text
        party = item.find('party').text
        state = item.find('state').text




    report = []

    htmlTable = soup.find('table', class_='table table-striped')
    for row in htmlTable.findAll("tr"):
        data = {}
        for i, cell in enumerate(row("td"), start=1):
            c = cell.get_text().strip()
            if '\n' in c:
                c = c.replace('\n','')
            data.update({i:c})
        # transactionAmount = data.get(8)
        transactionDate, ticker, assetType, transactionType = data.get(2), data.get(4), data.get(6), data.get(7)
        # Other asset types of interest: Corporate Bond and Municipal Security, info for those is in 'data.get(5)'
        if (assetType != 'Stock') and (assetType != 'Stock Option'):
            #print(assetType)
            continue
        elif ticker == '--':
            continue
        elif (party == '0') and (state == '0'):
            continue
        report.append([transactionDate, senatorName, party, state, ticker, transactionType]) 
        return pd.DataFrame(report).rename(columns=dict(enumerate(dataframeColumns)))


def getReports() -> DataFrame:
    client = requests.Session()
    index = 0
    offset = 50
    responseData = getMetadata(client, index, offset)
    metadata = json.dumps(responseData, indent=2)
    generaldata = getGeneralData()
    noData = False
    while(noData == False):
        index += offset
        responseData = getMetadata(client, index, offset)
        if not(responseData['data']):
            noData = True
        else:
            metadata += json.dumps(responseData, indent=2)
    
    allReports = pd.DataFrame()
    reportLinks = re.findall(r'/search/view/ptr/(.*?)/',metadata)
    
    for link in reportLinks:
        report = getReportData(client, link, generaldata)
        if report is None:
            continue
        allReports = allReports.append(report)
    return allReports

if __name__ == '__main__':
    report = getReports()
    report['transaction_date'] = pd.to_datetime(report['transaction_date']).dt.strftime('%m/%d/%Y')
    report.to_sql('transactions', dbEngine, index=True, if_exists='replace')
