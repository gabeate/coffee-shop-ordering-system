import pymysql

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='[INSERT PASSWORD HERE]',
        database='coffeeshopdb',
        charset='utf8'
    )