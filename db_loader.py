import sqlite3


def upload_db(path, data, query_city_id):
    """upload to table forecasts
    create
    process data manipulation (dml)
    """
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
    cursor.executemany(
            """
                insert into forecast(
                    city_sk,
                    owm_city_id,
                    dt_txt,
                    main_temp,
                    wind_speed,
                    wind_deg,
                    humidity,
                    description
                ) values (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )""", (
                    forecasts
                )
        )
    connection.commit()
    connection.close()
    return n
