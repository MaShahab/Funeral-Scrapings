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

        while counter<232:
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

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        news_papers = soup.find("div",{"class":"li1"})
        news_papers_items = news_papers.find_all("li")

        for index, news_paper in enumerate(news_papers_items):
            item = news_paper.find("a")

            item_value = item.text.strip()
            item_href = item['href']

            newsPaperObejct = NewsPaperClass(item_value, item_href, news_paper_location)
            storeNewsPaper(newsPaperObejct, 'output.csv')


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

        main_container = soup.find("div",{"class":"wrapWideLeft"})

        minor_containers = main_container.find_all("ul",{"class":"nlink"})

        for index, minor_container in enumerate(minor_containers):
            minor_hrefs = minor_container.find_all("a")
            for minor_href in minor_hrefs:
                minor_href_specifications = ["https://www.newspaperlists.com"+minor_href['href'], minor_href.text.strip()]
                print(f'https://www.newspaperlists.com{minor_href["href"]} , {minor_href.text.strip()} ')
                with open(r'locations_links.csv', 'a', newline='', encoding="utf-8-sig") as newspaper_file:
                    writer = csv.writer(newspaper_file)
                    writer.writerow(minor_href_specifications)

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
            with open('output.csv', 'r', encoding="utf-8-sig") as f:
                line_data = f.readlines()[index].strip()
                line_data_split = line_data.split(',')
                newspaper_link = line_data_split[1].strip()

                findSiteObituariesLink(newspaper_link)
                print(Green+str(index))

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
        with open('output.csv', 'r') as f:
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
        # fetchPageNewsPapers('https://newspaperlists.com/new-york')
        # storeLocationsLinks("https://newspaperlists.com/usa")
        # fetchAllNewsPapers()
        # make_json(r'output.csv', 'output.json')

        
        # findSiteObituariesLink('https://www.currentargus.com/')
        # findSiteObituariesLink('https://www.annistonstar.com/')

        # fetchAllNewsPapersObituaries(1)

        fetchAllNewsPapersObituaries2(1)


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

mainFunction()