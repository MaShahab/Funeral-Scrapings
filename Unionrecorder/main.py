import warnings

warnings.filterwarnings("ignore")

import csv
import sys
import requests
from bs4 import BeautifulSoup
from time import sleep
import datetime
import re
import json

# Colors
Purple = '\033[95m'
Blue = '\033[94m'
Cyan = '\033[96m'
Green = '\033[92m'
Yellow = '\033[93m'
Red = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


class FuneralWebsiteInfo:
    def __init__(self, name, city, state, address, website, phone_number):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.website = website
        self.phone_number = phone_number


def storeFuneral(funeral, dst):
    CRED = '\033[91m'

    try:
        funeral_specification = [funeral.name, funeral.city, funeral.state,
                                 funeral.address, funeral.website, funeral.phone_number]

        with open(dst, 'a', newline='', encoding="utf-8-sig") as products_file:
            writer = csv.writer(products_file)
            writer.writerow(funeral_specification)
        print(Blue + "The product with title of " + '(' + str(funeral.name) +')' + " successfully scraped and stored")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), funeral.website)



def storeExceptions(exception_log, failure_log):
    try:
        with open(r'Exceptions/Exceptions.csv', 'a', newline='', encoding="utf-8-sig") as e_file:
            writer = csv.writer(e_file)
            writer.writerow([exception_log, failure_log, datetime.datetime.now()])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(Red + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def fetchFuneralInfo(link):

    CRED = '\033[91m'
    CBLUE = '\33[94m'

    try:
        purge_link = link+'0'
        print(purge_link)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(purge_link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        funerals = soup.find_all("div", {"class": "fh-result-info"})
        websites = soup.find_all("div", {"class": "fh-results-cta"})

        
        for i in range(0, len(funerals)):

            funeral_home_name = funerals[i].find("span", {"class": "funeral-home-name"}).text.strip()
            funeral_home_address = funerals[i].find("span", {"class": "funeral-results-city"}).text.strip()
            funeral_phone_number = funerals[i].find("span", {"class": "funeral-home-phone"}).text.strip()
            funeral_website = websites[i].find("a",{"aria-label":"Funeral home website - opens a new window"})['href']
            if funeral_website == '':
                purge_funeral_website = "Null"
            else:
                purge_funeral_website = funeral_website
            
            funeral_address = funerals[i].find("span", {"class": "funeral-results-city"})
            funeral_location = funeral_address.find_next().text.strip()
            words = funeral_location.split(',')
            city = words[0].strip()
            state = words[-1].strip()

            funeralObejct = FuneralWebsiteInfo(funeral_home_name, city, state, funeral_home_address, funeral_phone_number, purge_funeral_website)
            storeFuneral(funeralObejct, 'Outputs/output.csv')
        

        # print(funeral_home_name)
        # print(funeral_home_address)
        # print(funeral_phone_number)
        # print(purge_funeral_website)
        # print(city)
        # print(state)

        

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)



def scrapeStateCities(link):
    CRED = '\033[91m'
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        cities = soup.find_all("a", {"class": "funeral-home-city"})
        for i in cities:
            city_funerals = 'https://obituaries.unionrecorder.com' + str(i['href'])
            fetchFuneralInfo(city_funerals)
       

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)

def scrapeStates(link):
    CRED = '\033[91m'
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        states_block = soup.find_all("div", {"class": "state-block"})
        # print(states)

        states_links = []

        for i in states_block:
            for a in i.find_all('a', href=True):
                states_links.append('https://obituaries.unionrecorder.com'+a['href'])

        for i in range(26,len(states_links)) :
            scrapeStateCities(states_links[i])
        # print(states_links[25])
       

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)


def make_json(csvFilePath, jsonFilePath):

    data = {}

    with open(csvFilePath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)

        for num, rows in enumerate(csvReader):
            data[int(num)] = rows
 
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))
         

 
# Call the make_json function


def mainFunction():
    CRED = '\033[91m'
    try:
                       
        csvFilePath = r'Output_backups/output.csv'
        jsonFilePath = r'Names.json'
        make_json(csvFilePath, jsonFilePath)

        # fetchFuneralInfo('https://obituaries.unionrecorder.com/funeral-home-directory/search?location=Los+Angeles%2C+CA%2C+US&pagesize=10')
        # scrapeStateCities('https://obituaries.unionrecorder.com/funeral-home-directory/me')
        # scrapeStates('https://obituaries.unionrecorder.com/funeral-home-directory')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


mainFunction()