import requests
from requests.structures import CaseInsensitiveDict
import sqlite3
import argparse
import time
from datetime import datetime
import pandas as pd


conn = sqlite3.connect("weather.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE if not exists temp_data
                  (request_timestamp timestamp, date datetime, city text, temp float, weather text, wind float)
               """)
cursor.close()
conn.close()


def get_weather(city):
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    url = f"https://api.openweathermap.org/data/2.5/weather?appid={key}&q={city}"
    result = requests.get(url)
    return result.json()


def get_weather_db(key):
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    url = f"https://api.openweathermap.org/data/2.5/box/city?bbox=12,32,15,37,10&appid={key}"
    result = requests.get(url)
    return result.json()


def get_temp(data):
    #data = {'id': 2563191, 'dt': 1626005361, 'name': 'Birkirkara', 'coord': {'Lon': 14.4611, 'Lat': 35.8972}, 'main': {'temp': 31.22, 'feels_like': 30.77, 'temp_min': 31.22, 'temp_max': 31.22, 'pressure': 1014, 'humidity': 37}, 'visibility': 10000, 'wind': {'speed': 4.63, 'deg': 0}, 'rain': None, 'snow': None, 'clouds': {'today': 20}, 'weather': [{'id': 801, 'main': 'Clouds', 'description': 'few clouds', 'icon': '02d'}]}
    ts = time.time()
    dt = datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
    city = data['name']
    temp = data['main']['temp']
    wind = data['wind']['speed']
    weather = f"{data['weather'][0]['main']} ({data['weather'][0]['description']})"
    return ts, dt, city, temp, weather, wind


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--key", type=str, help="API key", required=True)
    parser.add_argument("-l", "--list", action="store_true", help="prints full list of data", default=False)
    parser.add_argument("-c", "--city", type=str, help="prints the list of data for specified city")
    parser.add_argument("--history", action="store_true", help="prints last 7 rows of data (use it with -c/--city)",
                        default=False)
    args = parser.parse_args()
    if args.key:
        key = args.key
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    a = get_weather_db(key)
    for n in a["list"]:
        ts, dt, city, temp, weather, wind = get_temp(n)
        cursor.execute(f"insert into temp_data values('{ts}', '{dt}', '{city}', '{temp}', '{weather}', '{wind}')")
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
    cursor.close()
    conn.commit()
    conn.close()


def main_old():
    temp_fields = ["temp", "feels_like", "temp_min", "temp_max"]
    city = "chicago"
    a = get_weather(city)
    for n in a.keys():
        if n == 'main':
            print(n)
            for m in a[n].keys():
                if m in temp_fields:
                    print(f'  {m}: {int(a[n][m] - 273.15)}')
                else:
                    print(f'  {m}: {a[n][m]}')
        else:
            print(f'{n}: {a[n]}')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
