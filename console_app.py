import npyscreen
import os
import os.path
import sqlite3
from owm_request import request_forecast_json, console_request
from db_searcher import search_db
from db_loader import upload_db
from create_ddl_schema import create_db_sqlite
from create_dict import download_the_files, populate_db_sqlite
from create_dict import read_all_cities_into_lists


# API key to OpenWeatherMap.org
appid = "600e7808c4d14fe07520213ad9926375"
DB_NAME = 'weather.db'
target_path = '.'
target_folder = os.path.abspath(target_path)
db_path = target_folder + os.path.sep + DB_NAME


def get_msg_screen(message, title):
    npyscreen.notify_confirm(
        message,
        title,
        wrap=True,
        wide=True,
        editw=1
    )


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        self.addForm('MAIN', FirstForm, name="Select city")
        try:
            request_forecast_json(519690, appid)
            message = 'succeful connection with code -200'
            get_msg_screen(message, 'Connection test')
        except Exception as exception:
            message = f' connection error - {exception}'
            get_msg_screen(message, 'Connection test')
        check_db_file = os.path.exists(db_path)
        if check_db_file is True:
            message = f'Database file found: {DB_NAME}'
            get_msg_screen(message, 'Database test')
        else:
            message = f'DB file not found. Will create DDL schema: {DB_NAME}'
            create_db_sqlite(db_path)
            get_msg_screen(message, 'Database test')
# create cities dictionary from list (source: github, OpenWeatherMap.org)
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        message = f'tables found: {tables[0][0]},{tables[1][0]},{tables[2][0]}'
        get_msg_screen(message, 'Database tables test')
        message = 'Will compare amount of records DB and external source'
        get_msg_screen(message, 'Database tables test')
        last_record = cursor.execute(
            "SELECT city_sk FROM city WHERE city_sk=(SELECT max(city_sk) FROM city);"
            ).fetchone()
        download_the_files()
        cities = read_all_cities_into_lists()
        message = f' external source owm  amount of records:{len(cities)}'
        get_msg_screen(message, 'Database tables test')
        try:
            message = f'Dictionary table amount of records:  {last_record[0]}'
            get_msg_screen(message, 'Database tables test')
        except Exception as exception:
            message = f'Database dictionary table is empty - {exception}'
            get_msg_screen(message, 'Database tables test')
        if last_record == 0 or last_record is None:
            message = f'Will populate SQLite DB:  {DB_NAME} .city'
            get_msg_screen(message, 'Create dictionary table')
            populate_db_sqlite(db_path, cities)
            connection.commit()
            message = 'Dictionary is up to date. Job finished'
            get_msg_screen(message, 'Create dictionary table')
        elif last_record[0] == len(cities):
            message = 'Dictionary is up to date.'
            get_msg_screen(message, 'Create dictionary table')

    def onCleanExit(self):
        npyscreen.notify_wait("Goodbye!")

    def change_form(self, name):
        self.switchForm(name)


class FirstForm(npyscreen.ActionForm, npyscreen.ThemeManager):
    def create(self):
        self.add(
            npyscreen.TitleText,
            w_id="textfield",
            name="Enter city (ex. lomonоsov) to search in database:"
            )
        self.add(
            npyscreen.ButtonPress,
            name="Search city in database",
            when_pressed_function=self.btn_press
            )

    def btn_press(self):
        form_input = self.get_widget("textfield").value
        try:
            result = search_db(db_path, form_input)
            owm_city_id = str(result[1])
            name = result[2]
            country_code = result[3]
            lat = result[5]
            long = result[6]
            forecast_info = console_request(appid, db_path, owm_city_id)
            forecast_short_info = forecast_info
            n = 0
            # skip id's from output message and save it to forecast_short_info
            for i in forecast_info:
                forecast_short_info[n] = i[2:]
                n += 1
            city_info = [owm_city_id, name, country_code, lat, long]
            message = f'City info (id, name, country, lat, long): {city_info}'
            forecast_message = f'Forecast_brief_msg (datetime, temp, wind, direction, humidity, description): {forecast_short_info[:10]}'
            get_msg_screen(message, 'City info (source: database)')
            get_msg_screen(forecast_message, 'External source forecast info')
            json_data = request_forecast_json(owm_city_id, appid)
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            stored_forecasts = cursor.execute(
                "SELECT max(case when (substr(dt_txt,0,11) = date('now')) then 1 else 0 end) FROM forecast  WHERE owm_city_id="+str(owm_city_id)
                ).fetchone()[0]
            if stored_forecasts == 1:
                upload_message = 'Forecast data has already stored.'
                get_msg_screen(upload_message, 'Upload info')
            else:
                upload = upload_db(db_path, json_data, owm_city_id)
                upload_message = f'Inserted to DB weather forecasts. Amount or rows: {upload}'
                get_msg_screen(upload_message, 'Upload info')
        except Exception as exception:
            message = f'An exception occurred. Object not found: {form_input},{exception}'
            get_msg_screen(message, 'City info (source: database)')

    def on_ok(self):
        self.parentApp.switchForm(None)

    def on_cancel(self):
        npyscreen.notify_yes_no("Do you want to stop?", editw=1)
        self.parentApp.switchForm(None)


app = App()
app.run()