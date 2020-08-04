
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


def get_url_status_code(url):
    try:
        ua = UserAgent()
        random_user_agent = ua.random
        print(colored("   - debug: using user-agent : " + random_user_agent + " for http status", 'yellow'))
        random_proxy = get_random_proxy()
        print(colored("   - debug: using proxy : " + random_proxy + "", 'yellow'))
        headers = {
            'User-Agent': random_user_agent,
        }
        proxies = {
            "http": random_proxy,
            "https": random_proxy
        }

        response = requests.get(url,proxies=proxies)
        return response.status_code
#
        #ua = UserAgent()
        #random_user_agent = ua.random
        #req = Request(url, headers={'User-Agent': random_user_agent})
        #print(colored("   - debug: using user-agent : " + random_user_agent + " for http status", 'yellow'))
        #return urlopen(req).getcode()



    except Exception as e:
        print(colored("   - error: " + str(e), 'red'))


def print_row(count, card):
    print(str(count) + ") id: [" + colored(card[0], 'yellow') + "] name: [" + colored(card[1], 'yellow') + "] - type: [" + colored(card[2], 'yellow')
          + "] - publisher: [" + colored(card[3], 'yellow') + "] - card_number: [" + colored(card[5], 'yellow') + "]")


def print_url(url, status):
    print("   - url: " + colored(url, 'white') + " -  status: " + colored(str(status), 'white'))


def wait_for(seconds):
    for i in range(seconds, 0, -1):
        print(colored("   - debug: waiting for :" + str(i), 'yellow'), end='\r')
        time.sleep(1)


def log_occurance(message):
    with open("./logs/script.log", "a") as logFile:
        logFile.write(message)


def get_table_data(meta_data, card, soup_list, list_name):
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


def build_update_row(id, url, meta_data, status):
    average = (meta_data['year_all'][0]['average']).replace("$", "")
    max = (meta_data['year_all'][1]['max']).replace("$", "")
    min = (meta_data['year_all'][2]['min']).replace("$", "")
    return (average, max, min, url, json.dumps(meta_data), status, id)


def update_card(row):
    query = "UPDATE "+settings.DB_TABLE \
            + " SET average_price=%s, max_price=%s, min_price=%s, url=%s, meta_data=%s, status=%s "
    query += "WHERE id=%s"
    print(colored("   - debug: query " + query, 'yellow'))
    set_data(query, row)


def update_card_status(id, status, url):
    data = (status, url, id)
    query = "UPDATE "+settings.DB_TABLE \
            + " SET status=%s, url=%s"
    query += " WHERE id=%s"
    print(colored("   - debug: query " + query, 'yellow'))
    set_data(query, data)


def get_click_list(rows):
    click_list = []
    for row in rows:
        cells = row.find_all('td')
        for cell in cells:
            if cell.has_attr("class"):
                if "noDataCard" not in cell['class'] and cell.has_attr("id"):
                    if "Standard" in cell.text:
                        click_list.insert(0, {"id": cell["id"], "text": cell.text})
                    else:
                        click_list.append({"id": cell["id"], "text": cell.text})
    return click_list


def extract_card_data_s2(url, card):
    options = Options()
    ua = UserAgent()
    random_user_agent = ua.random
    options.add_argument(f'user-agent={random_user_agent}')
    print(colored("   - debug: using user-agent : " + random_user_agent + " for selenium", 'yellow'))
    driver = webdriver.Chrome(settings.CHROME_DRIVER, options=options)
    driver.get("https://www.priceguide.cards/en")
    wait_for(800)
    #driver.quit()


def get_random_proxy():
    proxies = settings.PROXY_LIST
    secure_random = random.SystemRandom()
    return secure_random.choice(proxies)


def extract_card_data_s1(url, card):
    options = Options()
    ua = UserAgent()
    random_user_agent = ua.random
    #options.headless = True
    options.add_argument(f'user-agent={random_user_agent}')
    options.add_argument('--proxy-server=http://%s' % get_random_proxy())


    print(colored("   - debug: using user-agent : " + random_user_agent + " for selenium", 'yellow'))
    card_status = "UNPROCESSED"
    driver = webdriver.Chrome(settings.CHROME_DRIVER, options=options)
    driver.get(url)

    driver.execute_script("window.scrollTo(0,300);")
    print(colored("   - debug: scrolling window to 300", 'yellow'))

    try:
        # Wait for page load / gif loader to complete
        wait_for(7)

        # Get HTML source of page
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")

        # Check for 521 errors, website blocking
        check_521_error = soup.find("div", {"id": "cf-error-details"})
        if check_521_error:
            print(colored("   - error: 521 error aborting process ", 'red'))
            driver.quit()
            return False

        # Check to see what rows are visible to click on
        table_container = soup.find("div", {"id": "cardList"})
        card_rows = table_container.find("table").find_all('tr')

        # If no card rows return
        if len(card_rows) == 0:
            print(colored("   - debug: No clickable rows for " + card[1] + " moving on...", 'yellow'))
            driver.quit()
            update_card_status(card[0], "NO-CARD-ROWS", url)
            return False

        else:
            clickable_list = get_click_list(card_rows)

            # If no clickable list return
            if len(clickable_list) == 0:
                print(colored("   - debug: No clickable list for " + card[1] + " : " + str(clickable_list), 'yellow'))
                update_card_status(card[0], "EMPTY-CLICKABLE-LIST", url)
                driver.quit()
                return False

            else:
                print(colored("   - debug: " + card[1] + " click list " + str(clickable_list), 'yellow'))
                selectable_link = clickable_list[0]['id']
                print(colored("   - debug: selected " + str(selectable_link) + " as clickable element", 'yellow'))
                clickable_link = driver.find_element_by_id(selectable_link)

                # Check again, if no clickable link return
                if not clickable_link:
                    print(colored("   - debug: No clickable link for " + card[1], 'yellow'))
                    update_card_status(card[0], "NO-CLICKABLE-LINK", url)
                    driver.quit()

                    return False
                else:
                    print(colored("   - debug: Clicking on link with id: " + selectable_link + " for " + card[1], 'yellow'))
                    clickable_link.click()
                    wait_for(7)

                    # Re-grab page source as the click has added the pricing table
                    html_source = driver.page_source
                    soup = BeautifulSoup(html_source, "html.parser")
                    year_all = soup.find("tr", {"class": "year_ALL"})

                    # if no year_ALL return as it's not worth checking for year_2018
                    if not year_all:
                        print(colored("   - debug: No year_ALL row for " + card[1] + " moving on...", 'yellow'))
                        update_card_status(card[0], "NO-YEAR-ALL-DATA", url)
                        driver.quit()
                        return False
                    else:
                        meta_data = {}
                        meta_data['year_all'] = []
                        meta_data = get_table_data(meta_data, card, year_all, "year_all")
                        year_2018 = soup.find("tr", {"class": "year_2018"})

                        # If no year_2018, don't add it to the meta_data
                        if not year_2018:
                            print(colored("   - debug: No year_2018 row for " + card[1] + " moving on...", 'yellow'))
                        else:
                            meta_data['year_2018'] = []
                            meta_data = get_table_data(meta_data, card, year_2018, "year_2018")

                        if len(meta_data['year_all']) > 0:
                            update_row = build_update_row(card[0], url, meta_data, "PROCESSED")
                            update_card(update_row)
                            print(colored("   - status: extracted data for  " + card[1] + " --> " + str(meta_data), 'yellow'))
                            driver.quit()
                            return True
                        else:
                            print(colored("   - error: no meta_data for year_all for " + card[1], 'red'))
                            update_card_status(card[0], "EMPTY-META-DATA", url)
                            driver.quit()
                            return False

    except TimeoutException:
        print(colored("   - error: " + card[1] + "failed and could not process", 'red'))
        update_card_status(card[0], "COULD-NOT-PROCESS", url)
        driver.quit()
        return False



if __name__ == '__main__':
    print("-----------------------------------------------")
    start_time = time.time()
    cards = get_data("SELECT * FROM cards WHERE name >= 'A.C. Green' AND status IS NULL ORDER BY name;")
    failed_count = 0
    success_count = 0

    index = 1
    if len(sys.argv) == 2:
        index = int(sys.argv[1])

    print(colored("PROCESS INDEX set to " + str(index), 'green'))
    count = 1
    for card in cards:
        print_row(count, card)

        url = settings.BASE_URL + build_query_parameters(card)
        status = get_url_status_code("https://www.priceguide.cards/en")
        #status = 200

        print_url(url, status)
        if status == 200:
            print(colored("   - debug: " + card[1] + " http status is 200", 'yellow'))
            #got_data = extract_card_data_s1(url, card)
            got_data = extract_card_data_s2(url, card)

            if got_data:
                print(colored("   - status: SUCCESSFUL extraction of " + card[1] + "", 'magenta'))
                success_count = success_count + 1
            else:
                print(colored("   - status: FAILED extraction of " + card[1] + "", 'red'))
                failed_count = failed_count + 1

        else:
            print(colored("   - error: " + url + " had a status of " + str(status), 'red'))

        if count == index:
            break

        count = count + 1
    print("-----------------------------------------------")
    seconds = (time.time() - start_time)
    minutes = (seconds / 60)
    print(colored("Total of "+ str(index) + " records completed", 'white'))
    print(colored("Total of SUCCESS records : "+ str(success_count) + "", 'white'))
    print(colored("Total of FAILED records : "+ str(failed_count) + "", 'white'))
    print(colored("Total Time : %s seconds " % (seconds), 'white'))
    print(colored("Total Time : %s minutes " % (minutes), 'white'))
    processed_count = get_data("SELECT COUNT(*) as count FROM cards WHERE status = 'PROCESSED'")
    no_card_rows = get_data("SELECT COUNT(*) as count FROM cards WHERE status = 'NO-CARD-ROWS'")
    empty_clickable_list = get_data("SELECT COUNT(*) as count FROM cards WHERE status = 'EMPTY-CLICKABLE-LIST'")
    print(colored("Total Records Processed (To-Date) : %s " % (processed_count[0][0]), 'white'))
    print(colored("Total No Card Rows (To-Date) : %s " % (no_card_rows[0][0]), 'white'))
    print(colored("Total Empty / Commented Out List (To-Date) : %s " % (empty_clickable_list[0][0]), 'white'))
    print("-----------------------------------------------")
    print("Completed!")
#
#
