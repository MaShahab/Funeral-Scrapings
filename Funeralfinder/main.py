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

import pandas as pd


# Colors
Purple = '\033[95m'
Blue = '\033[94m'
Cyan = '\033[96m'
Green = '\033[92m'
Yellow = '\033[93m'
Red = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


class FuneralClass:
    def __init__(self, name, city, state, address, website, email, phone_number):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.website = website
        self.email = email
        self.phone_number = phone_number


def storeFuneral(funeral, dst):
    CRED = '\033[91m'

    try:
        funeral_specification = [funeral.name, funeral.city, funeral.state,
                                 funeral.address, funeral.website, funeral.email, funeral.phone_number]

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
        with open(r'Funeralfinder/Exceptions.csv', 'a', newline='', encoding="utf-8-sig") as e_file:
            writer = csv.writer(e_file)
            writer.writerow([exception_log, failure_log, datetime.datetime.now()])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(Red + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

def storeForbiddens(state, city):
    try:
        with open(r'Funeralfinder/Forbiddens.csv', 'a', newline='', encoding="utf-8-sig") as e_file:
            writer = csv.writer(e_file)
            writer.writerow([state, city, datetime.datetime.now()])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(Red + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

def fetchFuneralInfo(link):

    CRED = '\033[91m'
    CBLUE = '\33[94m'

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        if soup.find('h1').text.strip() == 'Forbidden':
            link_location = link.split("states/",1)[1]
            if link_location[-1] == '/':
                link_location = link_location[:-1]
            location_array = link_location.split('/')
            state = location_array[0]
            city = location_array[1]
            storeForbiddens(state,city)
        else:

            funeral_home = soup.find("h1", {"class": "page-title"})
            funeral_home = funeral_home.text.strip()
            # print(funeral_home)

            info_details = soup.find("div", {"class": "info-detail"})
            info_details = info_details.find("ul", {"class": "list-style-type-none"})
            info_details_list = info_details.find_all("li")

            full_address = info_details_list[0]
            full_address_txt = str(full_address)

            full_address_seperation = full_address_txt.split('<br/>')

            address = full_address_seperation[0]
            pure_address = re.sub(r'<li>','',address)
            
            location = full_address_seperation[1]
            pure_location = re.sub(r'</li>','',location)
            location_array = pure_location.split(',')
            city = location_array[0].strip()
            state = location_array[1].strip()
            state_parts = state.split(' ')

            if state_parts[-1].isdigit() == True:
                del state_parts[-1]
            
            state = ' '.join(state_parts)

            global website
            email = 'Null'
            phone_number = "Null"

            regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            regex_web_url = "^[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"

            for info_detail in info_details_list:
                if 'Phone' in info_detail.text.strip():
                    phone_number = info_detail.text.strip()
                if(re.fullmatch(regex_email, info_detail.text.strip())):
                    email = info_detail.text.strip()
                website = info_detail.find('a')
                
                url_validation = re.match(regex_web_url, info_detail.text.strip())
                if url_validation is not None:
                    website1 = info_detail.text.strip()
                else:
                    website1 = None

                if website is not None:
                    if is_valid_url(website['href']) == True:
                        website = website['href']
                # print(is_valid_url2(info_detail.text.strip()))

            # print(website)

            final_website = ''
            if website is None and website1 is None:
                final_website = "Null"
            elif website is not None and website1 is None:
                final_website = website
            elif website is None and website1 is not None:
                final_website = website1
            else:
                final_website = website1


            phone_number = re.sub(r'Phone:','',phone_number).strip()

            # print(funeral_home)
            # print(pure_address)
            # print(city)
            # print(state)
            # print(phone_number)
            # print(email)
            # print(final_website)

            funeralObejct = FuneralClass(funeral_home, city, state, pure_address, final_website,email, phone_number)
            storeFuneral(funeralObejct, 'Funeralfinder/output.csv')


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)

def fetchStateCities(link):
    CRED = '\033[91m'
    CBLUE = '\33[94m'

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        ul_instance = soup.find("ul",{"class":"three-col"}).find_all("li")
        state_cities = []
        for i in ul_instance:
            state_cities.append("https://www.funeralfinder.com"+i.find("a")['href'])
        
        for l in state_cities:
            fetchCityFunerals(l)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)

def fetchCityFunerals(link):
    CRED = '\033[91m'
    CBLUE = '\33[94m'

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        if soup.find('h1').text.strip() == 'Forbidden':
            link_location = link.split("states/",1)[1]
            if link_location[-1] == '/':
                link_location = link_location[:-1]
            location_array = link_location.split('/')
            state = location_array[0]
            city = location_array[1]
            storeForbiddens(state,city)
        else:
            data_table = soup.find('tbody').find_all('tr')
            links = []
            for data in data_table:
                link = data.find('a')['href']
                links.append("https://www.funeralfinder.com"+link)

            for link in links:
                fetchFuneralInfo(link)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)


def fetchStates(link):
    CRED = '\033[91m'
    CBLUE = '\33[94m'

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        ul_instance = soup.find("ul",{"class":"three-col"}).find_all("li")
        states_array = []
        for i in ul_instance:
            states_array.append("https://www.funeralfinder.com"+i.find("a")['href'])
        
        for l in range(17,len(states_array)) :
            # print(l)
            fetchStateCities(states_array[l])

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

def stringConcatenation(string):
    CRED = '\033[91m'

    try:
        split_array = string.split(' ')
        final_string = ''
        if len(split_array) > 1:
            for split in split_array:
                final_string = final_string+split+'+'
            # print(len(split_array))
        
            final_string = final_string[:-1]

        else:
            final_string = string

        return final_string


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
   


def loadCsvForbiddenData(file):
    CRED = '\033[91m'

    try:

        csv_file = csv.reader(open(file, "r", encoding="utf-8-sig"), delimiter=",")
        for row in csv_file:
            state = row[0]
            city = row[1]
            # print(stringConcatenation(state))
            # print(stringConcatenation(city))

            # 'https://www.funeralfinder.com/includes/datatables/funeralhomes_find.php?sEcho=65&iColumns=6&sColumns=&iDisplayStart=0&iDisplayLength=50&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3='+los+angeles+'&bRegex_3=false&bSearchable_3=true&sSearch_4='+california+'&bRegex_4=false&bSearchable_4=true&sSearch_5=&bRegex_5=false&bSearchable_5=true&iSortCol_0=2&sSortDir_0=asc&iSortingCols=1&bSortable_0=false&bSortable_1=true&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true'
            forbidden_page = 'https://www.funeralfinder.com/includes/datatables/funeralhomes_find.php?sEcho=65&iColumns=6&sColumns=&iDisplayStart=0&iDisplayLength=50&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3='+str(stringConcatenation(city))+'&bRegex_3=false&bSearchable_3=true&sSearch_4='+str(stringConcatenation(state))+'&bRegex_4=false&bSearchable_4=true&sSearch_5=&bRegex_5=false&bSearchable_5=true&iSortCol_0=2&sSortDir_0=asc&iSortingCols=1&bSortable_0=false&bSortable_1=true&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true'
            scrapeForbiddenCityHomes(forbidden_page)
            # print(forbidden_page)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def scrapeForbiddenCityHomes(url):
    CRED = '\033[91m'
    CBLUE = '\33[94m'

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        links = soup.find_all('a')

        for link in links:
            pure_link = link['href'].replace('\\', '')  
            pure_link = re.sub(r'"','',pure_link)
            pure_link = 'https://www.funeralfinder.com'+pure_link
            fetchFuneralInfo(pure_link)
            # print(pure_link)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))
        storeExceptions('Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno), link)


def load_data(link):
    

    CRED = '\033[91m'
    CBLUE = '\33[94m'

    try:

        edge_options = EdgeOptions()
        edge_options.use_chromium = True
        driver = Edge(executable_path='D:/pythonProjects/edgedriver_win64/msedgedriver.exe', options=edge_options)
        driver.get(link)

        # element = driver.find_element(By.XPATH, '//*[@id="table-id"]/tbody/tr[1]')

        current_page = driver.find_element(By.CLASS_NAME, 'dataTables_paginate')
        # current_page = current_page.find_element(By.CLASS_NAME, 'active').text.strip()
        current_page = current_page.find_element(By.CLASS_NAME, 'active')
        next_element = driver.find_element_by_xpath("//li[@class='active']/following-sibling::li")
        href_next_element = next_element.find_element_by_tag_name("a")

        href_next_element.click()

        # print(next_element.text)
        sleep(15)

        element = driver.find_element(By.XPATH, '//*[@class="dataTables_paginate paging_bootstrap pagination"]')
        ul_list = element.find_element(By.TAG_NAME, 'ul')
        items = ul_list.find_elements_by_tag_name("li")
        items_array = []
        global next_item
        # for num,item in enumerate(items):
            # element1 = item.find_element(By.CLASS_NAME, 'active')
            
            # print(item.get_attribute('innerHTML'))
            # items_array.append(item)
        # print(items_array)

        # print(element.text)
        # print("Row 1: ", element.text)

        # print(element1.text)
        driver.quit()


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))



def xpath_soup(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        privious = itertools.islice(parent.children,0,parent.content.index(child))
        xpath_tag = child.name
        xpath_index = sum(1 for i  in privious if i.name == xpath_tag) + 1
        components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)


def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))

def remove_specific_row_from_csv(file, index):

    CRED = '\033[91m'
    CBLUE = '\33[94m'

    try:
        df = pd.read_csv(file)
        # print(df)
        dataFrame = df.drop(index)
        # print(dataFrame)
        dataFrame.to_csv(file, index=False)

        print('\033[95m' + "data with index "+ str(index) + " successfully removed" + '\033[0m')

    except Exception  as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def removeAllDuplicates(duplicate_csv_file):

    CRED = '\033[91m'
    CBLUE = '\33[94m'
    
    try:

        my_duplicate_csv_file = csv.reader(open(duplicate_csv_file, "r", encoding="utf-8-sig"), delimiter=",")
        duplicate_csv_file_list = list(my_duplicate_csv_file)
        for row in reversed(duplicate_csv_file_list):
            # print(row)
            remove_specific_row_from_csv('Unirecorder.csv',int(row[0])-1)
            print(int(row[0]))

        
     
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))


def storeDuplicateData(file, dst_file_index, dst_duplicate_csv, *kwargs):

    funeral_name = kwargs[0]['funeral_name']
    funeral_city = kwargs[0]['funeral_city']

    dst_rows_to_remove = []

    my_comprative_csv_file = csv.reader(open(file, "r", encoding="utf-8-sig"), delimiter=",")
    for row_num,row in enumerate(my_comprative_csv_file):
        if row[0] == funeral_name and row[1] == funeral_city:
            dst_rows_to_remove.append(dst_file_index)
            with open(dst_duplicate_csv, 'a', newline='', encoding="utf-8-sig") as my_file:
                writer = csv.writer(my_file)
                dst_file_index_array = list(str(dst_file_index))
                dst_file_index_merged = [''.join(dst_file_index_array[0 : 8])]
                writer.writerow(dst_file_index_merged)
            my_file.close()

            # remove_specific_row_from_csv('Unirecorder.csv', dst_file_index - 2)

            # return True
        # else:
        #     print(False)
        #     print(row[0])
        #     print(funeral_name)
        #     print(dst_file_index)
            # return False
        



def csvContentSearch(dst_csv_file):

    my_dst_csv_file = csv.reader(open(dst_csv_file, "r", encoding="utf-8-sig"), delimiter=",")
    for row_index,row in enumerate(my_dst_csv_file):
        # print(row_index)

        storeDuplicateData(r'Funeralfinder.csv', row_index,r'test.csv', {'funeral_name': row[0], 'funeral_city': row[1]})

        # if row[0] == 'Albertville Funeral Home' and row[1] == 'Albertville':
        #     print(rown_index)
        # else:
        #     print (None)


def mainFunction():
    CRED = '\033[91m'
    
    # remove_specific_row_from_csv('Unirecorder.csv', 3)
    try:
        pass

        # print(my_text[0].text.strip())

        # removeAllDuplicates(r'test.csv')
        
        # csvContentSearch(r'Unirecorder.csv')
        # checkCsvContentExists(r'Unirecorder.csv', {'funeral_name': 'aaaaa', 'funeral_city':'zzzzzz'})

        # remove_specific_row_from_csv('Unirecorder.csv',4)

        # remove_specific_row_from_csv('Unirecorder.csv', 0)


        # load_data('https://www.lambdatest.com/selenium-playground/table-pagination-demo')
        # load_data('https://www.funeralfinder.com/funeral-homes/')

        # csvFilePath = r'Removed_Duplicate_Aggregated_data.csv'
        # jsonFilePath = r'Removed_Duplicate_Aggregated_data.json'
        # make_json(csvFilePath, jsonFilePath)

        # print(stringConcatenation("new york sdfsdf"))
        # loadCsvForbiddenData(r'Funeralfinder/Forbiddens1.csv')
        # scrapeForbiddenCityHomes('https://www.funeralfinder.com/includes/datatables/funeralhomes_find.php?sEcho=65&iColumns=6&sColumns=&iDisplayStart=0&iDisplayLength=50&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3=los+angeles&bRegex_3=false&bSearchable_3=true&sSearch_4=california&bRegex_4=false&bSearchable_4=true&sSearch_5=&bRegex_5=false&bSearchable_5=true&iSortCol_0=2&sSortDir_0=asc&iSortingCols=1&bSortable_0=false&bSortable_1=true&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true')

        # fetchStates('https://www.funeralfinder.com/funeral-homes/states/')

        # fetchFuneralInfo('https://www.funeralfinder.com/funeral-homes/mcguire-funeral-service/19773/')  
        # fetchStateCities("https://www.funeralfinder.com/funeral-homes/states/KS/")      
        # fetchCityFunerals('https://www.funeralfinder.com/funeral-homes/states/DC/Washington/')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(CRED + '\033[1m' + 'Error occurred : ' + str(e) + 'in line ' + str(exc_tb.tb_lineno))

mainFunction()