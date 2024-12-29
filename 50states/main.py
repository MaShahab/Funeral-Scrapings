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
    def __init__(self, title, url, location):
        self.title = title
        self.url = url
        self.location = location


def storeNewsPaper(news_paper, dst):
    CRED = '\033[91m'

    try:
        news_paper_specification = [news_paper.title, news_paper.url, news_paper.location]

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

    try:

        news_paper_location = link.split('/')
        news_paper_location = news_paper_location[-1].strip()
        news_paper_location = re.sub(r'.htm','',news_paper_location).strip()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        news_papers_content = soup.find("div",{"class":"entry-content"})
        news_papers_content = news_papers_content.find("ul")
        news_papers = news_papers_content.find_all("a")

        for index, news_paper in enumerate(news_papers):
            item_value = news_paper.text.strip()
            item_href = news_paper['href']
            newsPaperObejct = NewsPaperClass(item_value, item_href, news_paper_location)

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

        states_container = soup.find("ul",{"class":"listStates clearAfter"})
        column_states = states_container.find_all("li",{"class":"floatLeft"})
        for index, coumn_state in enumerate(column_states):
            column_states_items = coumn_state.find_all("li")
            for column_state_item in column_states_items:
                column_state_link = column_state_item.find("a")
                column_state_link = column_state_link['href']
                state_href = [column_state_link]
                print(Blue + f"The state with title ({column_state_link}) stored.")
                with open(r'locations_links.csv', 'a', newline='', encoding="utf-8-sig") as newspaper_file:
                    writer = csv.writer(newspaper_file)
                    writer.writerow(state_href)



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
        # storeLocationsLinks("https://www.50states.com/news/")
        # fetchPageNewsPapers('https://www.50states.com/news/alabama.htm')
        # fetchAllNewsPapers()

        # findSiteObituariesLink('https://www.andalusiastarnews.com/')
        # fetchAllNewsPapersObituaries(0)
        # fetchAllNewsPapersObituaries2(0)


        make_json('news_papers.csv', '50states_Newspappers.json')


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

mainFunction()