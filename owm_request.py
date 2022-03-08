import requests
import sqlite3


def get_wind_direction(deg):
    rumb = ['N ', 'NE', ' E', 'SE', 'S ', 'SW', ' W', 'NW']
    for i in range(0, 8):
        step = 45.
        min = i*step - 45/2.
        max = i*step + 45/2.
        if i == 0 and deg > 360-45/2.:
            deg = deg - 360
        if deg >= min and deg <= max:
            res = rumb[i]
            break
    return res


# get city_id with given name
def get_city_id(s_city_name, appid):
    try:
        res = requests.get(
            "http://api.openweathermap.org/data/2.5/find", params={
                    'q': s_city_name,
                    'type': 'like',
                    'units': 'metric',
                    'lang': 'ru',
                    'APPID': appid})
        data = res.json()
        cities = ["{} ({})".format(d['name'], d['sys']['country'])
                  for d in data['list']]
        print("city:", cities)
        city_id = data['list'][0]['id']
        print('city_id=', city_id)
        assert isinstance(city_id, int)
        return city_id
    except Exception as e:
        print("Exception (find):", e)
        pass


# Forecast output
def request_forecast(city_id, appid):
    try:
        res = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast", params={
                               'id': city_id,
                               'units': 'metric',
                               'lang': 'ru',
                               'APPID': appid
                               }
                           )
        data = res.json()
        print('city:', data['city']['name'], data['city']['country'])
        for i in data['list']:
            print((
                i['dt_txt'])[:16],
                '{0:+3.0f}'.format(i['main']['temp']),
                '{0:2.0f}'.format(
                i['wind']['speed']
                ) + " м/с",
                get_wind_direction(i['wind']['deg']),
                str(i['main']['humidity']) + " %",
                i['weather'][0]['description'])
    except Exception as e:
        print("Exception (forecast):", e)
        pass


# Forecast json
def request_forecast_json(city_id, appid):
    try:
        res = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast", params={
                               'id': city_id,
                               'units': 'metric',
                               'lang': 'ru',
                               'APPID': appid
                               }
                           )
        data = res.json()
    except Exception as e:
        print("Exception (forecast):", e)
        pass
    return data


def console_request(appid, path, query_city_id):
    """upload to table forecasts"""
    try:
        res = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast", params={
                               'id': query_city_id,
                               'units': 'metric',
                               'lang': 'ru',
                               'APPID': appid
                               }
                           )
        data = res.json()
        weather_lists = data['list']
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        city_sk = cursor.execute(
            'SELECT city_sk FROM city WHERE owm_city_id='+str(query_city_id)
            ).fetchone()[0]
        forecasts = [[] for _ in range(len(weather_lists))]
        n = 0
        for i in weather_lists:
            forecasts[n] = (
                [
                    city_sk,
                    int(query_city_id),
                    i['dt_txt'],
                    i['main']['temp'],
                    i['wind']['speed'],
                    i['wind']['deg'],
                    i['main']['humidity'],
                    i['weather'][0]['description']
                    ]
                )
            n += 1
    except Exception as e:
        print("Exception (forecast):", e)
    return forecasts
