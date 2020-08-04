import os
import sys
import logging
import pymysql
import settings
import csv




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


def set_data(query, data):
    try:
        connection = pymysql.connect(host=settings.DB_HOST, port=3306, user=settings.DB_USER,
                                     passwd=settings.DB_PASS, db=settings.DB_NAME)
        cursor = connection.cursor()
        cursor.execute(query, data)

        connection.commit()
    except Exception as e:
        print(cursor._last_executed)
        logging.log(logging.ERROR, e)


def insert_card(row):
    query = "INSERT INTO "+settings.DB_TABLE \
            + " (name, type, publisher, year, card_number, price, details, box_location, meta_data) "
    query += "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

    set_data(query, row)




if __name__ == '__main__':

    with open(settings.CSV_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        count = 1
        for row in csv_reader:

            name = str(row[0])
            type = str(row[1])
            publisher = str(row[2])
            year = str(row[3])
            card_number = str(row[4])
            price = str(row[5])
            details = str(row[6])
            box_location = str(row[7])
            meta_data = '{}'

            row = (name, type, publisher, year, card_number, price, details, box_location, meta_data)

            print(str(count) + " : " + str(row))

            insert_card(row)

            #break

            count = count + 1
