import os
import os.path
import sqlite3
from db_loader import upload_db
from owm_request import request_forecast_json
from create_ddl_schema import create_db_sqlite
from create_dict import download_the_files, populate_db_sqlite
from create_dict import read_all_cities_into_lists


# config
# API key to OpenWeatherMap.org
appid = "600e7808c4d14fe07520213ad9926375"
DB_NAME = 'weather.db'
volume_to_download = 10
target_path = '.'
target_folder = os.path.abspath(target_path)
db_path = target_folder + os.path.sep + DB_NAME


# check connection with given API key
check_connection = request_forecast_json(519690, appid)
print('succeful connection with code -'+check_connection['cod'])


# define database schema SQlite with first run flag
check_db_file = os.path.exists(db_path)
if check_db_file is True:
    print('Database file found: ', DB_NAME)
else:
    print('Job started')
    print('Will save output SQLite DB to folder: %s' % (target_folder,))
    create_db_sqlite(db_path)
    print('Job finished')


# create cities dictionary from list (source: github, OpenWeatherMap.org)
connection = sqlite3.connect(db_path)
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('tables found:')
for i in tables:
    print(i[0])
last_record = cursor.execute(
    "SELECT city_sk FROM city WHERE city_sk=(SELECT max(city_sk) FROM city);"
    ).fetchone()
download_the_files()
all_cities = read_all_cities_into_lists()
cities = all_cities[0:volume_to_download]
print('Test set of owm contains number of records :', len(cities))
try:
    print('DB last city record: ', last_record[0])
except Exception as exception:
    print('Database is not yet populated (empty). Exception: ', exception)
if last_record == 0 or last_record is None:
    print('Will populate SQLite DB to table city: %s' % (DB_NAME)+'.city')
    print('Job started')
    populate_db_sqlite(db_path, cities)
    connection.commit()
    print('Dictionary is up to date. Job finished')
elif last_record[0] == len(cities):
    print('Dictionary is up to date. Job finished')


# upload with selected cities its weather forecasts to database
print(f'For test purposes will update DB for {volume_to_download} cities')
counter = 0
for city in cities:
    query_city_id = city[0]
    stored_forecasts = cursor.execute(
        """
        SELECT
            max(case when
                    (substr(dt_txt,0,11) = date('now'))
                then
                    1
                else
                    0
                end)
        FROM
            forecast
        WHERE
            owm_city_id="""+str(query_city_id)
        ).fetchone()[0]
    if stored_forecasts == 1:
        print('Forecasts for given sample and date has already stored')
        break
    else:
        json_data = request_forecast_json(query_city_id, appid)
        rows = upload_db(db_path, json_data, query_city_id)
        counter += rows
print('Affected count or rows:'+str(counter))
print('Job finished.')
