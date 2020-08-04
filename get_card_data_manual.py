
import os
import sys
import logging
import pymysql
import time
import json
import random
import requests
from decimal import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from termcolor import colored, cprint
from fake_useragent import UserAgent
from urllib.request import Request, urlopen
import settings

def set_data(query, data):
    try:
        connection = pymysql.connect(host=settings.DB_HOST, port=3306, user=settings.DB_USER,
                                     passwd=settings.DB_PASS, db=settings.DB_NAME)
        cursor = connection.cursor()
        cursor.execute(query, data)

        connection.commit()
    except Exception as e:
        #print(cursor._last_executed)
        logging.log(logging.ERROR, e)


def get_data(q):
    try:
        connection = pymysql.connect(host=settings.DB_HOST, port=3306, user=settings.DB_USER,
                                     passwd=settings.DB_PASS, db=settings.DB_NAME)
        cursor = connection.cursor()
        cursor.execute(q)

        rows = cursor.fetchall()
        rows_set = []
        for row in rows:
            rows_set.append(row)
        return rows_set

    except Exception as e:
        logging.log(logging.ERROR, e)


def build_query_parameters(card):
    name = (card[1]).strip().replace(" ", "-")
    card_type = (card[2]).lower()
    publisher = card[3]
    if publisher == 'NBA Hoops':
        publisher = 'nba'
    elif publisher == 'ProSet':
        publisher = 'pro-set'
    elif publisher == 'Upper Deck':
        publisher = 'upper-deck'

    publisher = (publisher).lower()
    card_number = card[5]
    return 'sport='+card_type+'&publisher='+publisher+'&name='+name+'&cardnumber='+card_number+'&'


def print_row(count, card):
    print(str(count) + ") id: [" + colored(card[0], 'yellow') + "] name: [" + colored(card[1], 'yellow') + "] - type: [" + colored(card[2], 'yellow')
          + "] - publisher: [" + colored(card[3], 'yellow') + "] - card_number: [" + colored(card[5], 'yellow') + "]")


def print_url(url, status):
    print("   - url: " + colored(url, 'white') + " -  status: " + colored(str(status), 'white'))


def update_card_url(id, url):
    data = (url, id)
    query = "UPDATE "+settings.DB_TABLE \
            + " SET url=%s"
    query += " WHERE id=%s"
    print(colored("   - debug: query " + query, 'yellow'))
    set_data(query, data)


def update_card(row):
    query = "UPDATE "+settings.DB_TABLE \
            + " SET average_price=%s, max_price=%s, min_price=%s, url=%s, meta_data=%s, status=%s "
    query += "WHERE id=%s"
    print(colored("   - debug: query " + query, 'yellow'))
    set_data(query, row)


def build_update_row(id, url, meta_data, status):
    average = (meta_data['year_all'][0]['average']).replace("$", "")
    max = (meta_data['year_all'][1]['max']).replace("$", "")
    min = (meta_data['year_all'][2]['min']).replace("$", "")
    return (average, max, min, url, json.dumps(meta_data), status, id)


def build_update_row_not_processed(id, url, status):
    return (0, 0, 0, url, json.dumps({}), status, id)


def get_table_data(meta_data, card, soup_list, list_name):
    print(card)
    meta_data[list_name] = []
    table_header = ['year', 'grade', 'average', 'max', 'min', 'count', 'chart']
    print(colored("   - debug: getting "+list_name+" data for " + card[1], 'yellow'))
    index = 0
    if soup_list is not None:
        for item in soup_list:
            sub_dic = {table_header[index]: item.text}

            if table_header[index] != 'year' and table_header[index] != 'chart' \
                    and table_header[index] != 'count' and table_header[index] != 'grade':
                meta_data[list_name].append(sub_dic)
                print(colored("     - debug: building: " + str(sub_dic), 'yellow'))
            index = index + 1
    else:
        print(colored("     - debug: no data for " + list_name + ", moving on..", 'yellow'))

    return meta_data


def get_url_from_filename(filename):
    return (filename).replace("https-::", "https://").replace(".txt", "").replace("cards:", "cards/")

if __name__ == '__main__':
    print("-----------------------------------------------")
    start_time = time.time()
    for filename in os.listdir(settings.DATA_DIR):

        if filename.endswith(".txt"):
            url = get_url_from_filename(filename)
            card = get_data("SELECT * FROM cards WHERE url = '" + url + "';")
            if len(card) > 0:
                card = card[0]
            else:
                card = None

            if card:

                with open(settings.DATA_DIR +filename, "r") as f:
                    html_source = f.read()
                    if html_source == 'COULD-NOT-PROCESS':
                        update_row = build_update_row_not_processed(card[0], url,"COULD-NOT-PROCESS")
                        update_card(update_row)
                        print(colored("   - status: COULD-NOT-PROCESS --> updating db " + str(url), 'yellow'))
                        os.remove(settings.DATA_DIR +filename)
                        print(colored("   - status: COULD-NOT-PROCESS --> removing file " + str(url), 'yellow'))
                    else:
                        soup = BeautifulSoup(html_source, "html.parser")
                        year_all = soup.find("tr", {"class": "year_ALL"})
                        meta_data = {}
                        meta_data['year_all'] = []
                        meta_data = get_table_data(meta_data, card, year_all, "year_all")
                        update_row = build_update_row(card[0], url, meta_data, "PROCESSED")
                        update_card(update_row)
                        print(colored("   - status: extracted data for " + card[1] + " --> " + str(meta_data), 'yellow'))
                        os.remove(settings.DATA_DIR +filename)
                        print(colored("   - status: removing data file for  " + card[1] + " --> " + str(meta_data), 'yellow'))
            else:
                print(colored("Error :  " + url + " doesn't exist in db .", 'red'))
                os.remove(settings.DATA_DIR +filename)


