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
from urllib.parse import urlparse

warnings.filterwarnings("ignore", category=DeprecationWarning)

import itertools

# from selenium import webdriver
# from selenium.webdriver.edge.options import Options
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from seleniumbase import SB
from seleniumbase import Driver

import undetected_chromedriver as uc

import pandas as pd
import pprint

from datetime import datetime

import time


# Colors
Purple = '\033[95m'
Blue = '\033[94m'
Cyan = '\033[96m'
Green = '\033[92m'
Yellow = '\033[93m'
Red = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


class NewsPaperClass:
    def __init__(self, title, page_url,years_coverage,collection, state, city):
        self.title = title
        self.page_url = page_url
        self.years_coverage = years_coverage
        self.collection = collection
        self.state = state
        self.city = city


def storeNewsPaper(news_paper, dst):
    CRED = '\033[91m'

    try:
        news_paper_specification = [news_paper.title, news_paper.page_url, news_paper.years_coverage, news_paper.collection, news_paper.state, news_paper.city]

        with open(dst, 'a', newline='', encoding="utf-8-sig") as newspaper_file:
            writer = csv.writer(newspaper_file)
            writer.writerow(news_paper_specification)
        print(Blue + "The news paper with title of " + '(' + str(news_paper.title) +')' + " successfully scraped and stored")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), news_paper_specification.url)

def storeExceptions(exception_log, failure_log):
    try:
        with open(r'Exceptions.csv', 'a', newline='', encoding="utf-8-sig") as e_file:
            writer = csv.writer(e_file)
            writer.writerow([exception_log, failure_log, datetime.datetime.now()])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(Red + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def fetchAllNewsPapers():
    try:

        counter = 0

        while True:
            with open('locations_links.csv', 'r', encoding="utf-8-sig") as f:
                line_data = f.readlines()[counter].strip()
                line_data_split = line_data.split(',')
                pure_url = line_data_split[0]
                fetchPageNewsPapers(pure_url)
                counter = counter + 1

                

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(Red + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

def fetchPageNewsPapers(link):

    CRED = '\033[91m'
    CBLUE = '\33[94m'
    
    global final_city
    global final_title
    global final_years_coverage
    global final_collection

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        newspaper_state_text = soup.find('h1', {'class':'pane-title'}).text.strip()
        newspaper_state_split = newspaper_state_text.split(' ')
        newspaper_state = newspaper_state_split[-1]
        # print(newspaper_state)



        state_urls = [link+'?page=0']

        is_pagination = soup.find('ul', {'class':'pagination'})
        if is_pagination is not None:
            pages = soup.find_all('li',{'class':'page-item hidden-sm hidden-xs'})
            for page in pages:
                state_urls.append(link+'?page='+page.text.strip())

        else:
            newspapers_continer = soup.find("div",{"class":"table-responsive"})
            newspapers_rows = newspapers_continer.find_all('tr')
            for index, row in enumerate(newspapers_rows):
                city = row.find('td',{'class':'views-field-field-pub-city'})
                if city is not None:
                    final_city = city.text.strip()
                else:
                    final_city = "Null"
                title = row.find('td',{'class':'views-field-title'})
                if title is not None:
                    final_title = title.text.strip()
                    title_url = title.find("a")['href']
                else:
                    title_url = "Null"
                    final_title = "Null"
                years_coverage = row.find('td',{'class':'views-field-field-pub-range-details-value'})
                if years_coverage is not None:
                    final_years_coverage = years_coverage.text.strip()
                else:
                    final_years_coverage = "Null"
                collection = row.find('td',{'class':'views-field-field-pub-product-value'})
                if collection is not None:
                    final_collection = collection.text.strip()
                else:
                    final_collection = "Null"
                    

                newsPaperObejct = NewsPaperClass(final_title,title_url,final_years_coverage,final_collection,newspaper_state,final_city)
                storeNewsPaper(newsPaperObejct, 'news_papers.csv')            


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)


def storeLocationsLinks(link):
    CRED = '\033[91m'
    CBLUE = '\33[94m'

    try:
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        states_container = soup.find("table",{"id":"state-list"})
        states_parts = states_container.find_all("td")
        for index, state_part in enumerate(states_parts):
            states = state_part.find_all("a")
            for state in states:
                final_pure_state_url = "https://www.genealogybank.com" + state['href']
                state_title = state.text.strip()
                state_href = [final_pure_state_url]
                with open(r'locations_links.csv', 'a', newline='', encoding="utf-8-sig") as newspaper_file:
                    writer = csv.writer(newspaper_file)
                    writer.writerow(state_href)
                    print(Blue + f"The state with title ({state_title}) stored.")


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)


def is_valid_url(url):
    url_regex = re.compile(r'https?://(?:www\.)?[a-zA-Z0-9./]+')
    return bool(url_regex.match(url))

def is_valid_url2(url):
    url_regex = re.compile(r'www\.)?[a-zA-Z0-9./]+')
    return bool(url_regex.match(url))

def make_json(csvFilePath, jsonFilePath):

    data = {}

    with open(csvFilePath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)

        for num, rows in enumerate(csvReader):
            data[int(num)] = rows
 
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))



def storeNewspaperObituaries(data):
    try:
        with open(r'newspapers_obituaries.csv', 'a', newline='', encoding="utf-8-sig") as e_file:
            writer = csv.writer(e_file)
            writer.writerow(data)
            print(Blue + "The Newspaper obituaries with title link " + '(' + data[0] +' )' + " successfully scraped and stored")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(Red + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def fetchAllNewsPapersObituaries(index):
    try:
        while True:
            with open('news_papers.csv', 'r', encoding="utf-8-sig") as f:
                line_data = f.readlines()[index].strip()
                line_data_split = line_data.split(',')
                newspaper_link = line_data_split[1].strip()
                # print(newspaper_link)
                sleep(1)

                findSiteObituariesLink(newspaper_link)
                # print(Green+str(index))

                index = index + 1

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(Red + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def fetchAllNewsPapersObituaries2(start_index):
    CRED = '\033[91m'
    Green = '\033[92m'
    driver = Driver(uc=True)
    driver.maximize_window()
    try:
        final_obituaris_urls = []
        with open('news_papers.csv', 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            rows_count = len(rows)
            for i in range(start_index,rows_count):
                final_url = rows[i][1]

                news_paper_location = final_url.split('/')
                news_paper_location = news_paper_location[-1].strip()

                driver.execute_script("window.open('" + str(final_url) + "');")
                WebDriverWait(driver, 5).until(
                    lambda wd: driver.execute_script("return document.readyState") == 'complete',
                    "Page taking too long to load"
    )
                time.sleep(1)
                driver.close()
                window_name = driver.window_handles[0]
                driver.switch_to.window(window_name=window_name)

                html = driver.page_source
                soup = BeautifulSoup(html)

                obituaries_href_list = []
                obituaries = soup.find_all("a", string=re.compile(r'[o]bituar', re.IGNORECASE))
                for obituary in obituaries:
                    obituaries_href_list.append(obituary['href'])

                removed_duplicates_obituaries = list(dict.fromkeys(obituaries_href_list))

                dot_pattern = re.compile(r'\.')
                http_pattern = re.compile(r'http')      

                for item in removed_duplicates_obituaries:
                    if http_pattern.search(item) and dot_pattern.search(item):
                        final_obituaris_urls.append(item)
                    else:
                        final_obituaris_urls.append(str(final_url)+str(item))

                
                purged_obituaries_urls = list(dict.fromkeys(final_obituaris_urls))

                output_result = purged_obituaries_urls
                output_result.insert(0, str(final_url))
                storeNewspaperObituaries(output_result)
                time.sleep(1)

                
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(Red + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def findSiteObituariesLink(link):

    CRED = '\033[91m'
    CBLUE = '\33[94m'

    try:
        final_obituaris_urls = []
        news_paper_location = link.split('/')
        news_paper_location = news_paper_location[-1].strip()

        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        # r = requests.get(link, headers=headers)
        # soup = BeautifulSoup(r.text, 'html.parser')

        driver = Driver(uc=True)
        driver.maximize_window()
        driver.get(link)
        time.sleep(5)

        
        html = driver.page_source
        soup = BeautifulSoup(html)


        obituaries_href_list = []
        obituaries = soup.find_all("a", string=re.compile(r'[o]bituar', re.IGNORECASE))
        for obituary in obituaries:
            obituaries_href_list.append(obituary['href'])

        removed_duplicates_obituaries = list(dict.fromkeys(obituaries_href_list))

        dot_pattern = re.compile(r'\.')
        http_pattern = re.compile(r'http')      

        for item in removed_duplicates_obituaries:
            if http_pattern.search(item) and dot_pattern.search(item):
                final_obituaris_urls.append(item)
            else:
                final_obituaris_urls.append(str(link)+str(item))

        
        purged_obituaries_urls = list(dict.fromkeys(final_obituaris_urls))

        # print(purged_obituaries_urls)

        output_result = purged_obituaries_urls
        output_result.insert(0, str(link))
        storeNewspaperObituaries(output_result)
        # print(output_result)


        time.sleep(1)
        driver.quit()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)

def mainFunction():
    CRED = '\033[91m'
    try:
        # storeLocationsLinks("https://www.genealogybank.com/newspapers/sourcelist")
        # fetchPageNewsPapers('https://www.genealogybank.com/newspapers/sourcelist/ca')
        # fetchPageNewsPapers('https://www.genealogybank.com/newspapers/sourcelist/de')
        fetchAllNewsPapers()

        # findSiteObituariesLink('https://www.al.com/birmingham/')
        # fetchAllNewsPapersObituaries(0)
        # fetchAllNewsPapersObituaries2(0)


        # make_json('news_papers.csv', 'W3newspapers_Newspappers.json')


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

mainFunction()