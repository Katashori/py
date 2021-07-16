"""
This is the main training file.
"""

import requests
from requests.structures import CaseInsensitiveDict
import sqlite3
import argparse
import time
from datetime import datetime
import pandas as pd


# This is a function for web request. It's used by "main" function.
def get_weather_db(key):
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    url = f"https://api.openweathermap.org/data/2.5/box/city?bbox=12,32,15,37,10&appid={key}"
    result = requests.get(url)
    return result.json()


# This is a function for getting information from specified template. We get this using function "get_weather_db".
def get_temp(data):
    ts = time.time()
    dt = datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
    city = data['name']
    temp = data['main']['temp']
    wind = data['wind']['speed']
    weather = f"{data['weather'][0]['main']} ({data['weather'][0]['description']})"
    return ts, dt, city, temp, weather, wind


# This is the main function of this file. Please run it with arguments to get result.
def main():
    # This is a block for parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--key", type=str, help="API key", required=True)
    parser.add_argument("-l", "--list", action="store_true", help="prints full list of data", default=False)
    parser.add_argument("-c", "--city", type=str, help="prints the list of data for specified city")
    parser.add_argument("--history", action="store_true", help="prints last 7 rows of data (use it with -c/--city)",
                        default=False)
    args = parser.parse_args()
    if args.key:
        key = args.key

    # This is a block for db creation (if not exists)
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE if not exists temp_data
                      (request_timestamp timestamp, date datetime, city text, temp float, weather text, wind float)
                   """)
    a = get_weather_db(key)

    # This is a block for inserting data to db using "get_temp" function.
    for n in a["list"]:
        ts, dt, city, temp, weather, wind = get_temp(n)
        cursor.execute(f"insert into temp_data values('{ts}', '{dt}', '{city}', '{temp}', '{weather}', '{wind}')")

    # This is a block for checking parameters and returning results.
    if args.list:
        print(pd.read_sql_query("SELECT date, city, temp, weather, wind FROM temp_data LIMIT 1000", conn))
    elif args.history and args.city:
        cursor.execute(f"""SELECT date, city, temp, weather, wind
                            FROM temp_data WHERE city = '{args.city}'
                            ORDER BY request_timestamp DESC LIMIT 7""")
        rows = cursor.fetchall()
        print("Последние 7 измерений:\n")
        for row in rows:
            result = (f"""дата/время: {row[0]} \nгород: {row[1]} \nтемпература: {row[2]} \nпогода: {row[3]} 
            ветер: {row[4]} м/с \n""").replace('    ', '')
            print(result)
    elif args.city:
        cursor.execute(f"""SELECT date, city, temp, weather, wind 
                            FROM temp_data WHERE city = '{args.city}'
                            ORDER BY request_timestamp DESC LIMIT 1""")
        rows = cursor.fetchall()
        for row in rows:
            print(f"""город: {row[1]} \nтемпература: {row[2]} \nпогода: {row[3]} \nветер: {row[4]} м/с \n""")

    # This is a block for closing of db connection.
    cursor.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
