"""
This is old training file. It was excluded from the main one and saved just in case I need to look at something.
"""

import requests
from requests.structures import CaseInsensitiveDict


def get_weather(key, city):
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    url = f"https://api.openweathermap.org/data/2.5/weather?appid={key}&q={city}"
    result = requests.get(url)
    return result.json()


def main():
    temp_fields = ["temp", "feels_like", "temp_min", "temp_max"]
    city = "chicago"
    key = ''
    a = get_weather(key, city)
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
