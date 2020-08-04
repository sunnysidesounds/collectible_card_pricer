

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


if __name__ == '__main__':
    print("-----------------------------------------------")
    start_time = time.time()
    cards = get_data("SELECT * FROM cards;")
    count = 1
    for card in cards:
        print_row(count, card)
        url = settings.BASE_URL + build_query_parameters(card)
        print_url(url, '200')
        update_card_url(card[0], url)
