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
from selenium import webdriver

from seleniumbase import Driver
import undetected_chromedriver as uc

import pprint

from datetime import datetime

import time
import asyncio


# Colors
Purple = '\033[95m'
Blue = '\033[94m'
Cyan = '\033[96m'
Green = '\033[92m'
Yellow = '\033[93m'
Red = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
CRED = '\033[91m'


class Person:
    def __init__(self, first_name, middle_name, last_name, nick_name, birth_date, death_date, birth_year, death_year, age, funeral_home, obituary_id, image):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.nick_name = nick_name
        self.birth_date = birth_date
        self.death_date = death_date
        self.birth_year = birth_year
        self.death_year = death_year
        self.age = age
        self.funeral_home = funeral_home
        self.obituary_id = obituary_id
        self.image = image


def storePerson(person, dst):
    CRED = '\033[91m'

    try:
        person_specification = [person.first_name, person.middle_name, person.last_name, person.nick_name,
                                 person.birth_date, person.death_date, person.birth_year, person.death_year, person.age , person.funeral_home , person.obituary_id, person.image]

        with open(dst, 'a', newline='', encoding="utf-8-sig") as products_file:
            writer = csv.writer(products_file)
            writer.writerow(person_specification)
        print(Blue + "The person with last_name " + '(' + str(person.last_name) +')' + " successfully scraped and stored")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), person.last_name)

def storeExceptions(exception_log, failure_log):
    try:
        with open(r'Exceptions.csv', 'a', newline='', encoding="utf-8-sig") as e_file:
            writer = csv.writer(e_file)
            writer.writerow([exception_log, failure_log, str(datetime.now())])
        
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


async def fetchObituary(link):
    CRED = '\033[91m'
    CBLUE = '\33[94m'

    global final_first_name, final_middle_name, final_last_name, final_birth_date, final_death_date, final_obituary_text, final_image

    try:
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        
        personObject = Person(final_first_name, final_middle_name, final_last_name, final_birth_date, final_death_date,
                               final_obituary_text, final_image)

        storePerson(personObject, 'output.csv')


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)

def fetchObituariesPage(link):
    try:
       pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)

def fetchAllObituaries(page_no):
    try:
        pass

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        # storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)


def onlyDeathDate(str):
    value = standardDateFormat(str.strip())
    value = re.sub(r',','',value)
    value = date_converter(value)
    value = value.strftime("%m/%d/%Y")
    return value


def removeAgeFromDate(str):
    if '(' in str:
        new_txt = re.compile(re.escape('(')+'.*')
        new_txt = new_txt.sub('', str)
        return new_txt

def standardDateFormat(str):
    final_output = []
    output = str.split(' ')
    for i in range(0,len(output)):
        if i == 0:
            final_output.append(str[:3])
        else:
            final_output.append(output[i])
    result = [' '.join(final_output[0 : 80])]
    return result[0]

def split_dates(str):
    try:
        dates_txt = removeAgeFromDate(str)

        if ',' in dates_txt:
            dates_txt = re.sub(r',','',dates_txt)

        if '-' in dates_txt:
            final_output = []
            output = dates_txt.split('-')
            for index, parameter in enumerate(output):
                value = standardDateFormat(parameter.strip())
                value = date_converter(value)
                value = value.strftime("%m/%d/%Y")
                final_output.append(value)
            return final_output[0], final_output[1]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

def date_converter(input_date):
    if re.match(r"^\d{8}$", input_date):
        dateObj = datetime.strptime(input_date,'%Y%m%d')
    elif re.match(r"^\d{1,2}/", input_date):
        dateObj = datetime.strptime(input_date,'%m/%d/%Y')
    elif re.match(r"^[a-z]{3}", input_date, re.IGNORECASE):
        dateObj = datetime.strptime(input_date,'%b %d %Y')
    elif re.match(r"^\d{1,2} [a-z]{3}", input_date, re.IGNORECASE):
        dateObj = datetime.strptime(input_date,'%d %b %Y')

    return dateObj

def make_json(csvFilePath, jsonFilePath):

    data = {}

    with open(csvFilePath, encoding='utf-8-sig') as csvf:
        csvReader = csv.DictReader(csvf)

        for num, rows in enumerate(csvReader):
            data[int(num)] = rows
 
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))


def fetchStatesLinks(link):
    try:
        CRED = '\033[91m'
        CBLUE = '\33[94m'

        global final_first_name, final_middle_name, final_last_name, final_birth_date, final_death_date, final_obituary_text, final_image

        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        main_division = soup.find('div',{'class':'hero-sections'})
        states = main_division.find_all('a','col-6 col-md-4 col-lg-3 item')
        for state in states:
            state_url = "https://www.tributearchive.com" + state['href'].strip()
            with open(r'States_Urls.csv', 'a', newline='', encoding="utf-8-sig") as e_file:
                writer = csv.writer(e_file)
                writer.writerow([state_url])
                e_file.close()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def fetchStateFuneralHomes(link,country,state):
    try:
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Authorization': 'Bearer R0YwSUN6NlRDbm9rRDRycjNHOW10MHlETUtIYk53R1pyb0dBbEtMTEUrdz06Kzo4OS4yMTkuOTguMTYyOis6NjM4NjM4NDgwNTQwMDAzMDM2'}
        data = {'country': 'usa', 'state': state, 'pageNumber': 1, 'pageSize': 2000}
        r = requests.post(link, headers=headers, data=data)
        soup = BeautifulSoup(r.text, 'html.parser')
        dict_from_json = json.loads(soup.text)
        funeral_homes = dict_from_json['funeralHomes']

        for funeral_home in funeral_homes:

            funeral_home_id = funeral_home['funeralHomeId']
            funeral_home_name = funeral_home['name'].strip()
            funeral_home_name_site_format = re.sub(r' ','-',funeral_home_name)
            funeral_home_country = country
            funeral_home_state = state
            funeral_home_city = funeral_home['city'].strip()

            final_funeral_home_url = "https://www.tributearchive.com/funeral-homes/"+str(funeral_home_country)+"/"+str(funeral_home_state)+"/"+str(funeral_home_city)+"/"+str(funeral_home_name_site_format)+"/fh-"+str(funeral_home_id)


            with open(r'funeral_homes_links.csv', 'a', newline='', encoding="utf-8-sig") as e_file:
                writer = csv.writer(e_file)
                writer.writerow([final_funeral_home_url,funeral_home_country,funeral_home_state])
                e_file.close()

        # soup = BeautifulSoup(r.text, 'html.parser')


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def fetchAllStatesFuneralHomes(link):
    try:
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        main_division = soup.find('div',{'class':'hero-sections'})
        states = main_division.find_all('a','col-6 col-md-4 col-lg-3 item')
        for state in states:
            link_parts = state['href'].split('/')
            url_country = link_parts[-2]
            url_state = link_parts[-1]
            fetchStateFuneralHomes("https://api.secure.tributecenteronline.com/archiveapi/FuneralHomeSearch",url_country,url_state)
            print(Blue + f"{url_country} ( {url_state} ) funeral homes successfully scraped.")



    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))




def saveFuneralHomesApiFormat(csv_file):
    try:
        with open(csv_file, 'r', newline="") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                url = str(row[0])
                funeral_home_id = url.rsplit('fh-', 1)[-1]
                final_url = "https://api.secure.tributecenteronline.com/archiveapi/obituarysearch/?funeralhomeId="+str(funeral_home_id)
                with open(r'funeral_homes_links(api_format).csv', 'a', newline='', encoding="utf-8-sig") as e_file:
                    writer = csv.writer(e_file)
                    writer.writerow([final_url])
                    e_file.close()

            f.close()


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()


def fetchObituary(obituary):
    try:
        global final_first_name, final_middle_name, final_last_name, final_nick_name, final_birth_date, final_death_date, final_birth_year, final_death_year, final_age, final_funeral_home, final_obituary_id, final_image
        
        full_name = obituary['fullName'].strip()
        splitted_name = split_name(full_name)
        # print(splitted_name[1])

        # first_name, middle_name, last_name, nick_name, birth_date, death_date, birth_year, death_year, age, funeral_home, obituary_id, image

        if splitted_name[1] is not None:
            final_first_name = splitted_name[1]
        else:
            final_first_name = None
        if splitted_name[2] is not None:
            final_middle_name = splitted_name[2]
        else:
            final_middle_name = None
        if splitted_name[4] is not None:
            final_last_name = splitted_name[4]
        else:
            final_last_name = None
        if splitted_name[3] is not None:
            final_nick_name = splitted_name[3]
        else:
            final_nick_name = None

        final_birth_date = obituary['birthDate']
        final_death_date = obituary['deathDate']

        final_birth_year = final_birth_date.rsplit('/', 1)[-1]
        final_death_year = final_death_date.rsplit('/', 1)[-1]


        if final_birth_date == "" or final_death_date == "":
            final_age = None
        else:
            int_death_year = int(final_death_year)
            int_birth_year = int(final_birth_year)
            final_age = int_death_year - int_birth_year
            

        final_funeral_home = obituary['funeralHomeName']
        final_obituary_id = obituary['obituaryId']
        final_image = obituary['thumbnailUrl']

        # print(final_first_name, final_middle_name, final_last_name, final_nick_name, final_birth_date, final_death_date, final_birth_year, final_death_year, final_age, final_funeral_home, final_obituary_id, final_image)

        personObject = Person(final_first_name, final_middle_name, final_last_name, final_nick_name, final_birth_date, final_death_date, final_birth_year, final_death_year, final_age, final_funeral_home,
                            final_obituary_id, final_image)
            
        storePerson(personObject, 'output.csv')



    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

def fetchFuneralStateObituaries(funeral_home_line_no):
    try:
        global authorization_status
        global dict_from_json

        with open('funeral_homes_links(api_format).csv', 'r', encoding='utf-8-sig') as f:
            data_line = f.readlines()[funeral_home_line_no].strip()
            page_no = 1
            page_size = 12

            while True:
                page_url = data_line + "&pageNumber="+str(page_no)+"&pageSize="+str(page_size)
                funeral_home_id = re.search('funeralhomeId=(.*)&pageNumber', page_url)
                funeral_home_id = str(funeral_home_id.group(1).strip())

            
                headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                'Authorization': 'Bearer RzRBcjNIY04wN3lnZkpTUG1RaWlYekJVVWdnbHMzQXZLL0dHNlBTenhXYz06KzoxOTIuMTUxLjE0NS4yMDI6Kzo2Mzg2NDE4MDkyOTAwMDc4MTY='}
                data = {'funeralhomeId': funeral_home_id, 'pageNumber': str(page_no), 'pageSize': str(page_size)}
                r = requests.get(page_url, headers=headers, data=data)
                if r.status_code == 401:
                    authorization_status = False
                    break
                    # print("Hi")
                else:
                    authorization_status = True
                    soup = BeautifulSoup(r.text, 'html.parser')
                    try:
                        dict_from_json = json.loads(soup.text)
                        hasNextPage = dict_from_json['hasNextPage']
                        if hasNextPage == True:
                            obituaries = dict_from_json['searchResult']
                            for obituary in obituaries:
                                fetchObituary(obituary)
                            time.sleep(0.1)
                            print(Green + f"obituaries in page number ( {str(page_no)} ) are successfully fetched.")
                            time.sleep(0.1)

                            page_no = page_no + 1
                            # fetch_status = True
                        else:
                            page_no = page_no + 1
                            break
                    except:
                        page_no = page_no + 1
                        pass
                        # break
                
            if authorization_status == True:
                return dict_from_json
            elif authorization_status == False:
                return None

        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def fetchAllObituaries(line_no):
    try:
        currnet_line_no = line_no
        while True:
            with open('funeral_homes_links(api_format).csv', 'r', encoding="utf-8-sig") as f:
                line_data = f.readlines()[currnet_line_no].strip()

                try:

                    result_json = fetchFuneralStateObituaries(currnet_line_no)

                    # print(result_json)

                    if result_json is None:
                        print("Unauthorized")
                        break
                    
                    else:
                        storeUrlLineNo(currnet_line_no)
                        print(Purple + f"link ({line_data}) with line number ({currnet_line_no}) successfully scraped.")

                    f.close()
                    currnet_line_no = currnet_line_no + 1
                except:
                    print("Authorization error")
                    break
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

def storeUrlLineNo(index):
    try:
        with open('url_line_no.txt', 'w', encoding='utf-8') as f:
            f.write(str(index)+'\n')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def read_lastLineScrapedData(file):
    try:
        global last_line
        with open(file, 'r', encoding="utf-8-sig") as f:
            last_line = f.readlines()[-1].strip()
            print(last_line)
            f.close()


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

def mainFunction():
    CRED = '\033[91m'

    try:
        # fetchStatesLinks('https://www.tributearchive.com/funeral-homes')
        # fetchStateFuneralHomes("https://api.secure.tributecenteronline.com/archiveapi/FuneralHomeSearch","us","California")
        # fetchAllStatesFuneralHomes('https://www.tributearchive.com/funeral-homes')
        # saveFuneralHomesApiFormat('funeral_homes_links.csv')
        # fetchFuneralStateObituaries(0)

        # read_lastLineScrapedData('output.csv')

        global last_line_index
        with open('url_line_no.txt', 'r') as f:
            last_line = f.readlines()[-1].strip()
            last_line_int = int(last_line)
            last_line_index = last_line_int
            f.close()
        fetchAllObituaries(last_line_index)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

mainFunction()