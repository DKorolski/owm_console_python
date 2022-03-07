import sqlite3


# search in dictionary
def search_db(path, input_name):
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    city_sk = cursor.execute(
        """SELECT * FROM city WHERE lower(name)='"""+str(input_name)+"""'"""
        ).fetchall()[0]
    return (city_sk)