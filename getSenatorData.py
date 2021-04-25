import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame
import re
import json



class getSenatorData:

    def __init__(self, rootUrl):
        self.rootUrl = rootUrl
        self.metadataUrl = rootUrl + '/search/'
        self.landingPageUrl = rootUrl + '/search/home/'
        self.endpointAPI = rootUrl + '/search/report/data/'
        self.dataframeColumns = ['Transaction_Date', 'Position', 'Name', 'Symbol', 'Buy/Sell', 'Order_amount']

        self.report = self.getReports()
        
    # obtain csrftoken and agree to prohibition agreement
    def csrf(self, client: requests.Session) -> str:
        response = client.get(self.landingPageUrl)
        content = BeautifulSoup(response.text, 'lxml')
        formCSRF = content.find(attrs={'name': 'csrfmiddlewaretoken'})['value']
        payload = {
            'csrfmiddlewaretoken': formCSRF,
            'prohibition_agreement': '1'
        }
        client.post(self.landingPageUrl, data=payload, headers={'Referer': self.landingPageUrl})
        csrftoken = client.cookies['csrftoken']
        # redirects to 302 after above post request, and sets sessionid cookie in 302 reponse but doesn't work with requests for some reason
        client.cookies['sessionid'] = 'gASVGAAAAAAAAAB9lIwQc2VhcmNoX2FncmVlbWVudJSIcy4:1lPtAe:HdlLg5fQlBFem3FlnE-Z32WD9bw'
        return csrftoken

    # obtain senator periodic transaction links
    def getMetadata(self, client: requests.Session, index, offset):
        token = self.csrf(client)
        postData = {
            'start': str(index),
            'length': str(offset),
            'first_name': '',
            'last_name': '',
            'report_types': '[11]',
            'submitted_start_date': '10/01/2020 00:00:00',
            'submitted_end_date': '',
            'candidate_state': '',
            'senator_state': '',
            'office_id': '',
            'filer_types': '[]',
            'csrfmiddlewaretoken': token
        }
        response = client.post(self.endpointAPI, data=postData, headers={'Referer':self.metadataUrl, 'X-CSRFToken':token, 'X-Requested-With':'XMLHttpRequest'})
        jsonData = json.loads(response.text)
        return jsonData
    # obtain report data and compile into dataframe
    def getReportData(self, client: requests.Session, reportLink) -> DataFrame:
        response = client.get(self.rootUrl + '/search/view/ptr/' + reportLink).text
        soup = BeautifulSoup(response, 'html.parser')
        
        senatorName = soup.find('h2', class_='filedReport')
        senatorName = re.findall(r'\((.+)\)',senatorName.get_text())
        senatorName = "".join(senatorName)
        report = []

        htmlTable = soup.find('table', class_='table table-striped')
        for row in htmlTable.findAll("tr"):
            data = {}
            for i, cell in enumerate(row("td"), start=1):
                c = cell.get_text().strip()
                if '\n' in c:
                    c = c.replace('\n','')
                data.update({i:c})
            transactionDate, ticker, assetType, transactionType, transactionAmount = data.get(2), data.get(4), data.get(6), data.get(7), data.get(8)
            if assetType != 'Stock':
                continue
            elif ticker == '--':
                continue
            report.append([transactionDate, 'Senator', senatorName, ticker, transactionType, transactionAmount])
            return pd.DataFrame(report).rename(columns=dict(enumerate(self.dataframeColumns)))


    def getReports(self) -> DataFrame:
        client = requests.Session()
        index = 0
        offset = 50
        responseData = self.getMetadata(client, index, offset)
        metadata = json.dumps(responseData, indent=2)
        noData = False
        while(noData == False):
            index += offset
            responseData = self.getMetadata(client, index, offset)
            if not(responseData['data']):
                noData = True
            else:
                metadata += json.dumps(responseData, indent=2)
        
        allReports = pd.DataFrame()
        reportLinks = re.findall(r'/search/view/ptr/(.*?)/',metadata)
        
        for link in reportLinks:
            report = self.getReportData(client, link)
            if report is None:
                continue
            allReports = allReports.append(report)
        return allReports
    

