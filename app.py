import os
import os.path
from owm_request import request_forecast_json, get_city_id, request_forecast
from create_ddl_schema import create_db_sqlite
from create_dict import *
from db_loader import *


#config
# API key to OpenWeatherMap.org
appid = "600e7808c4d14fe07520213ad9926375"
DB_NAME = 'weather.db'
target_path='.'
target_folder = os.path.abspath(target_path)
db_path = target_folder + os.path.sep + DB_NAME


#check connection with given API key
check_connection = request_forecast_json(519690,appid)
print('succeful connection with code -'+check_connection['cod'])


#define database schema SQlite with first run flag
check_db_file = os.path.exists(db_path)
if check_db_file == True:
    print ('Database file found: ', DB_NAME)
else:
    print('Job started')
    print('Will save output SQLite DB to folder: %s' % (target_folder,))
    create_db_sqlite(db_path)
    print('Job finished')


#create cities dictionary from list (source: github, OpenWeatherMap.org)
connection = sqlite3.connect(db_path)
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables=cursor.fetchall()
print('tables found:')
for i in tables:
    print (i[0])
last_record = cursor.execute(
    "SELECT city_sk FROM city WHERE city_sk=(SELECT max(city_sk) FROM city);"
    ).fetchone()
download_the_files()
cities = read_all_cities_into_lists()
print ('owm source amount of cities records :', len(cities))
try:
    print('last city record: ', last_record[0])
except:
    print('database is empty')
if last_record == 0 or last_record is None:
    print('Will populate SQLite DB to table city: %s' % (DB_NAME)+'.city')
    print('Job started')
    populate_db_sqlite(db_path, cities)
    connection.commit()      
    print('Dictionary is up to date. Job finished')
elif last_record[0] == len(cities):
    print('Dictionary is up to date. Job finished')


#request forecast by days with given places
print('Enter name of city as one argument. For example: Saint Petersburg,RU')
city_name_input = input("Name of city :")
query_city_id=get_city_id(city_name_input, appid)
if (query_city_id) is not None:
    print('Correct input')
    request_forecast(query_city_id, appid)
    print(
        'Will check for already stored forecasts with given city and current date.'
        )
    stored_forecasts = cursor.execute(
        "SELECT max(case when (substr(dt_txt,0,11) = date('now')) then 1 else 0 end) FROM forecast  WHERE owm_city_id="+str(query_city_id)
        ).fetchone()[0]
    if stored_forecasts==1:
        print('Forecasts for given city and current date has already stored in database')
    else:
        db_input_prompt = input("Insert new weather forecasts into database? (yes, no):")
        if db_input_prompt.startswith('y'):
            print('Will insert forecast into database')
            json_data = request_forecast_json(query_city_id, appid)
            upload_db(db_path, json_data, query_city_id)
else:
    print('Incorrect input. Please check input name.')