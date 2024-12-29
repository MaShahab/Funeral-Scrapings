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
import urllib.request

warnings.filterwarnings("ignore", category=DeprecationWarning)

import itertools

# from selenium import webdriver
# from selenium.webdriver.edge.options import Options
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import pandas as pd
import pprint


# Colors
Purple = '\033[95m'
Blue = '\033[94m'
Cyan = '\033[96m'
Green = '\033[92m'
Yellow = '\033[93m'
Red = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


class Person:
    def __init__(self, first_name, middle_name, last_name, birth_date, death_date, obituary_text, image):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.death_date = death_date
        self.obituary_text = obituary_text
        self.image = image


def storePerson(person, dst):
    CRED = '\033[91m'

    try:
        person_specification = [person.first_name, person.middle_name, person.last_name,
                                 person.birth_date, person.death_date, person.obituary_text, person.image]

        with open(dst, 'a', newline='', encoding="utf-8-sig") as products_file:
            writer = csv.writer(products_file)
            writer.writerow(person_specification)
        print(Blue + "The product with title of " + '(' + str(person.last_name) +')' + " successfully scraped and stored")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), person.last_name)

def storeExceptions(exception_log, failure_log):
    try:
        with open(r'Exceptions.csv', 'a', newline='', encoding="utf-8-sig") as e_file:
            writer = csv.writer(e_file)
            writer.writerow([exception_log, failure_log, datetime.datetime.now()])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(Red + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def removeDatesFromText(text,removeAllNums=False):

    # Removes times in the format "00:00"
    pattern = r'\d{2}:\d{2}'
    text = re.sub(pattern, '', text)

    #Try to remove dates from name
    day_names_pattern = r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b'
    text = re.sub(day_names_pattern, "", text)

    #Date strings
    date_str1 = r'\d{1,2}(?:st|nd|rd|th)?(?: day of)?\s*(?:Jan(?:uary)?\.?|Feb(?:ruary)?\.?|Mar(?:ch)?\.?|Apr(?:il)?\.?|May|Jun(?:e)?\.?|Jul(?:y)?\.?|Aug(?:ust)?\.?|Sep(?:t(?:\.|ember)?)?|Oct(?:ober)?\.?|Nov(?:ember)?\.?|Dec(?:ember)?\.?),?(?:\s*\d{4})'
    date_str2 = r'(?:Jan(?:uary)?\.?|Feb(?:ruary)?\.?|Mar(?:ch)?\.?|Apr(?:il)?\.?|May|Jun(?:e)?\.?|Jul(?:y)?\.?|Aug(?:ust)?\.?|Sep(?:t(?:\.|ember)?)?|Oct(?:ober)?\.?|Nov(?:ember)?\.?|Dec(?:ember)?\.?)\s+\d{1,2}(?:st|nd|rd|th)?,?(?:\s*\d{4})'
    date_str3 = r'\d{1,2}\/\d{1,2}\/\d{2}(?:\d{2})?'
    date_str4 = r'(?:0?[1-9]|1[0-2])-(?:0?[1-9]|[1-2][0-9]|3[0-1])-(?:\d{2}(?:\d{2})?)'
    date_str5 = r'(\d{4}\s*[-–-]\s*\d{4})'
    date_str6 = r'(\b\d{2,4}\b)'
    if removeAllNums:
        date_pattern = f'({date_str1}|{date_str2}|{date_str3}|{date_str4}|{date_str5}|{date_str6})'
    else:
        date_pattern = f'({date_str1}|{date_str2}|{date_str3}|{date_str4}|{date_str5})'
        
    text = re.sub(date_pattern, "", text)
    return text


def preprocessText(text):
    '''Remove HTML tags, Reduce whitespace characters'''
    if text is None:
        return None
    text = text.replace('<br>', ' ')
    text = text.splitlines()
    text = " ".join(text).strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def split_name(name, format='default'):
    # List of common name prefixes and suffixes for reference
    if name is None:
        return None, None, None, None, None, None
    
    #Remove html tags + clean up text
    name = preprocessText(name.strip())
    
 
    #Remove common FH strings:
    obit_strs = ['Obituary','Funeral','Services','Memorial','Service']
    for fh_str in obit_strs:
        name = name.replace(fh_str,'').replace(fh_str.lower(),'').strip()
    
    name = removeDatesFromText(name,removeAllNums=True)

    prefixes = set([
                    "dr.", "dr", "mr.", "mr", "mrs.", "mrs", "ms.", "ms", "sir", "prof.", "prof", "rev.", "rev",
                    "1sg", "a1c", "amn", "cmsaf", "cmssf", "cmsgt", "cpl", "cpo", "csm", "cpl", "fccm", "gysgt", "lcpl", "mcpo",
                    "mcpocg", "mcpo", "mgysgt", "msg", "msgt", "pfc", "po1", "po2", "po3", "pv2", "sa", "scpo", "sfc", "sgm", "sgt",
                    "sma", "smsgt", "sn", "spc", "ssg", "ssgt", "sgt", "sgtmaj", "sgtmajmc", "spc1", "spc2", "spc3", "spc4",
                    "sra", "tsgt", "sister", "brother", "father", "mother", "fr.", "fr"
                ])
    suffixes = set(["jr.", "sr.", "i", "ii", "iii", "iv", "v", "ph.d.", "md", "esq.", "jr", "sr", "esq", "ba", "ph.d", "phd", "phd.","m.d","m.d.","md."])
    
    if format == 'comma':
            pass
            #if ',' in name:
            #   parts = name.split(',')
            #   name = parts[1].strip() + ' ' + parts[0].strip()
    else:
        name = name.replace(',', '')  # Remove commas from the name

    #Further preprocess
        
    # Extract nickname and remove it from the name
    nickname = None
    match = re.search(r'[\("\'](.*?)[\)"\']', name)
    if match:
        nickname = match.group(1)
        name = re.sub(r'[\("\'].*?[\)"\']', '', name).strip()
    
        if len(nickname) >= 50:
            nickname = None
    #Remove trailing and leading punctuation
    pattern = re.compile(r'^[\W_\d]+|[\W_]+$')
    name = pattern.sub('', name).strip()

    parts = re.split(r'(?<! -) (?![\-])', name)
    parts = [p.lower() for p in parts]
    prefix = None
    first_name = None
    middle_name = None
    last_name = None
    suffix = None

    # Check for prefix (using lower for case insensitivity)
    if parts and parts[0] in prefixes:
        prefix = name.split()[0]  # Take original cased prefix from the name
        parts.pop(0)

    # Check for suffix (using lower for case insensitivity)
    if parts and parts[-1] in suffixes:
        suffix = name.split()[-1]  # Take original cased suffix from the name
        suffix = suffix[0].upper() + suffix[1:].lower()
        parts.pop()

    for i, part in enumerate(parts):
        if '-' in part:
            # Split by dash and capitalize each word
            dashed_names = [name.strip().capitalize() for name in part.split('-')]
            parts[i] = '-'.join(dashed_names)

    # Assign names based on the remaining parts
    if parts:
        first_name = parts[0]
        if first_name == first_name.lower():
            first_name = first_name.capitalize().strip()

    if len(parts) > 1:
        last_name = parts[-1]
        pattern = re.compile(r'^[\W_\d]+|[\W_]+$')
        last_name = pattern.sub('', last_name).strip()
        if last_name == last_name.lower():
            last_name = last_name.capitalize().strip()

    if len(parts) > 2:
        middle_name = " ".join([word.capitalize() if word == word.lower() else word for word in parts[1:-1]])
        middle_name = middle_name.strip()

    return prefix, first_name, middle_name, nickname, last_name, suffix


def imageNameConverter(url):
    CRED = '\033[91m'
    try:
        # postfix = url[url.rindex('.') + 1:]
        postfix = 'jpg'
        postfix = postfix.strip()
        currentTime = datetime.datetime.now().strftime("%m-%d %H:%M:%S:%f")
        currentTime_str = re.sub(r':', '', currentTime)
        currentTime_str = re.sub(r'-', '', currentTime_str)
        currentTime_str = re.sub(r' ', '', currentTime_str)
        image_name = 'Obituary-' + currentTime_str + '.' + postfix
        return image_name
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), url)


def fetchObituaries(link):
    CRED = '\033[91m'
    CBLUE = '\33[94m'

    global final_first_name, final_middle_name, final_last_name, final_birth_date, final_death_date, final_obituary_text, final_image

    try:
        edge_options = EdgeOptions()
        edge_options.use_chromium = True
        driver = Edge(executable_path='D:/pythonProjects/edgedriver_win64/msedgedriver.exe', options=edge_options)
        driver.get(link)

        timeout = 2
        try:
            element_present = EC.presence_of_element_located((By.ID, 'obituariesResults'))
            WebDriverWait(driver, timeout).until(element_present)

            html = driver.page_source
            soup = BeautifulSoup(html)

            obituaries = soup.find_all("div",{"class":"obit-result-container"})
            for WebElement in obituaries:

                full_name = WebElement.find("h3",{"class":"screen-title-title"})
                splited_name = split_name(full_name.text.strip())

                first_name = splited_name[1]
                final_first_name = first_name
                middle_name = splited_name[2]
                final_middle_name = middle_name
                last_name = splited_name[4]
                final_last_name = last_name

                full_date = WebElement.find("p",{"class":"screen-title-date"}).text.strip()
                if full_date != '':
                    split_date = full_date.split('–')
                    final_birth_date = split_date[1]
                    final_death_date = split_date[0]
                else:
                    final_birth_date = "Null"
                    final_death_date = "Null"
                
                a = WebElement.find("a",{"class":"obit-result-link"})
                obituary_text = a.findNextSibling()
                if obituary_text != '' or obituary_text != None:
                    final_obituary_text = obituary_text.text.strip()
                else:
                    final_obituary_text = "Null"
                
                image = WebElement.find("img",{"class":"preview-obit-image"})
                image_address = image['src']


                image_new_name = imageNameConverter(image_address)
                if image_address != None or image_address != "" or image_address != 'null' :
                    try:
                        urllib.request.urlretrieve(image_address, "images/"+image_new_name)
                    except:
                        pass

                personObject = Person(final_first_name, final_middle_name, final_last_name, final_birth_date, final_death_date,
                               final_obituary_text, image_new_name)
                
                storePerson(personObject, 'output.csv')



            # print(len(obituaries))
        except TimeoutException:
            print("Timed out waiting for page to load")

        # current_page = driver.find_element(By.CLASS_NAME, 'dataTables_paginate')

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

def mainFunction():
    CRED = '\033[91m'

    try:
        pass
        
        # csvFilePath = r'output.csv'
        # jsonFilePath = r'output.json'
        # make_json(csvFilePath, jsonFilePath)

        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20(or%20locationstate:%27on%27)%20%20%20)&start=5000&size=10&filtergroup=locationstate&filtervalue=%27on%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27or%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27or%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27pa%27))&start=1000&size=10&filtergroup=locationstate&filtervalue=%27pa%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27qc%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27qc%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27ri%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27ri%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27sk%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27sk%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27sc%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27sc%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27tn%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27tn%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27tx%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27tx%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27ut%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27ut%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27vt%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27vt%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27va%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27va%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27wa%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27wa%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27wv%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27wv%27&filterchecked=true&grave=false')
        
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20%20(or%20locationstate:%27wi%27))&start=5000&size=10&filtergroup=locationstate&filtervalue=%27wi%27&filterchecked=true&grave=false')
        # fetchObituaries('https://www.dignitymemorial.com/obituaries?q=(and%20(and%20%27%27)%20(or%20cmicreationdate:[%271900-01-01t00:00:00z%27,})%20%20%20)&start=5000&size=10&filtergroup=cmicreationdate&filtervalue=null&filterchecked=false&grave=false')
        


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

mainFunction()