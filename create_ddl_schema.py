import sqlite3


# SQLite DB ddl schema
def create_db_sqlite(db_path):
    with open(db_path, 'w') as _:
        pass
    sql_ddl_city = '''
    CREATE TABLE IF NOT EXISTS city (
        city_sk INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        owm_city_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        country TEXT NOT NULL,
        state TEXT,
        lat REAL NOT NULL,
        lon REAL NOT NULL
    );
    '''
    sql_ddl_weather = '''
        CREATE TABLE IF NOT EXISTS forecast (
        weather_sk INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        city_sk INTEGER NOT NULL,
        owm_city_id INTEGER NOT NULL,
        dt_txt TEXT NOT NULL,
        main_temp REAL NOT NULL,
        wind_speed REAL,
        wind_deg REAL NOT NULL,
        humidity REAL NOT NULL,
        description TEXT,
        FOREIGN KEY(city_sk) REFERENCES city(city_sk)
    );
    '''

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(sql_ddl_city)
    cur.execute(sql_ddl_weather)
    conn.commit()
    conn.close()
    print('Created SQLite empty database')