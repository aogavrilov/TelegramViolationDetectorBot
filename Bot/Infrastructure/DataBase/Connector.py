from mysql.connector import connect, Error

try:
    with connect(
            host="localhost",
            user="root",
            password="TempQwertyPassword"
    ) as connection:
        print(connection)
except Error as e:
    print(e)
