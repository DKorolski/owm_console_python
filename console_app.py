import npyscreen
import os
import os.path
from owm_request import request_forecast_json, console_request
from db_searcher import *
from db_loader import upload_db
from create_ddl_schema import *
from create_dict import *

#config
# API key to OpenWeatherMap.org
appid = "600e7808c4d14fe07520213ad9926375"
DB_NAME = 'weather.db'
target_path='.'
target_folder = os.path.abspath(target_path)
db_path = target_folder + os.path.sep + DB_NAME
        

class App(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        self.addForm('MAIN', FirstForm, name="Select city")
        try:
            request_forecast_json(519690,appid)
            message = f'succeful connection with code -200'
            npyscreen.notify_confirm(message, title="connection", wrap=True, wide=True, editw=1)
        except Exception as exception:
            message = f' connection error - {exception}'
            npyscreen.notify_confirm(message, title="connection", wrap=True, wide=True, editw=1)
        check_db_file = os.path.exists(db_path)
        if check_db_file == True:
            message = f'Database file found: {DB_NAME}'
            npyscreen.notify_confirm(message, title="check_database", wrap=True, wide=True, editw=1)
        else:
            message = f'Will create database file: {DB_NAME}'
            create_db_sqlite(db_path)
            npyscreen.notify_confirm(message, title="check_database", wrap=True, wide=True, editw=1)
        #create cities dictionary from list (source: github, OpenWeatherMap.org)
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables=cursor.fetchall()
        message = f'tables found: {tables[0][0]},{tables[1][0]},{tables[2][0]}'
        npyscreen.notify_confirm(message, title="check_tables", wrap=True, wide=True, editw=1)
        last_record = cursor.execute(
            "SELECT city_sk FROM city WHERE city_sk=(SELECT max(city_sk) FROM city);"
            ).fetchone()
        download_the_files()
        cities = read_all_cities_into_lists()
        message = f'owm source amount of cities records :{len(cities)}'
        npyscreen.notify_confirm(message, title="check_tables", wrap=True, wide=True, editw=1)
        try:
            message =f'last city record:  {last_record[0]}'
            npyscreen.notify_confirm(message, title="check_tables", wrap=True, wide=True, editw=1)
        except:
            message =f'database is empty'
            npyscreen.notify_confirm(message, title="check_tables", wrap=True, wide=True, editw=1)
        if last_record == 0 or last_record is None:
            message =f'Will populate SQLite DB to table city:  {DB_NAME} .city'
            npyscreen.notify_confirm(message, title="create dictionary", wrap=True, wide=True, editw=1)
            populate_db_sqlite(db_path, cities)
            connection.commit()      
            message =f'Dictionary is up to date. Job finished'
            npyscreen.notify_confirm(message, title="create dictionary", wrap=True, wide=True, editw=1)
        elif last_record[0] == len(cities):
            message =f'Dictionary is up to date. Job finished'
            npyscreen.notify_confirm(message, title="create dictionary", wrap=True, wide=True, editw=1)


    def onCleanExit(self):
        npyscreen.notify_wait("Goodbye!")
    
    def change_form(self, name):
        self.switchForm(name)

class FirstForm(npyscreen.ActionForm, npyscreen.ThemeManager):
    def create(self):
        self.add(npyscreen.TitleText, w_id="textfield", name="Enter city (ex. lomonоsov) to search in database:")
        self.add(npyscreen.ButtonPress, name="Search city in database", when_pressed_function=self.btn_press)

    def btn_press(self):
        form_input = self.get_widget("textfield").value
        try:
            result=search_db(db_path, form_input)
            owm_city_id =str(result[1])
            name = result[2]
            country_code =result[3]
            lat = result[5]
            long = result[6]
            forecast_info = console_request(appid, db_path, owm_city_id)
            forecast_short_info = forecast_info
            n=0
            #skip id's from output message and save it to forecast_short_info
            for i in forecast_info:
                forecast_short_info[n]=i[2:]
                n+=1
            city_info = [owm_city_id, name, country_code, lat, long]
            message = f'City info (owm_id, name, country, lat, long): {city_info}'
            forecast_message = f'Forecast_brief_msg (datetime, temp, wind, direction, humidity, description): {forecast_short_info[:10]}'
            npyscreen.notify_confirm(message, title="City info", wrap=True, wide=True, editw=1)
            npyscreen.notify_confirm(forecast_message, title="forecast info", wrap=True, wide=True, editw=1)
            json_data = request_forecast_json(owm_city_id, appid)
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            stored_forecasts = cursor.execute(
                "SELECT max(case when (substr(dt_txt,0,11) = date('now')) then 1 else 0 end) FROM forecast  WHERE owm_city_id="+str(owm_city_id)
                ).fetchone()[0]
            if stored_forecasts==1:
                upload_message = f'Forecast data has already stored for given date and city. Update skipped.'
                npyscreen.notify_confirm(upload_message, title="upload info", wrap=True, wide=True, editw=1)
            else:
                upload=upload_db(db_path, json_data, owm_city_id)
                upload_message = f'Inserted new weather forecasts into database. Affected amount or rows: {upload}'
                npyscreen.notify_confirm(upload_message, title="upload info", wrap=True, wide=True, editw=1)        
        except Exception as exception:
            message = f'An exception occurred. Object not found: {form_input},{exception}'
            npyscreen.notify_confirm(message, title="City info", wrap=True, wide=True, editw=1)
        

    def on_ok(self):
        self.parentApp.switchForm(None)

    def on_cancel(self):
        npyscreen.notify_yes_no("Do you want to stop the weather report API", editw=1)
        self.parentApp.switchForm(None)

app = App()
app.run()