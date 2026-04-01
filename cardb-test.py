# Test program for cars database

import mysql.connector
from dotenv import load_dotenv
import getpass
import os

load_dotenv()

# DB_PASSWORD should be defined in .env
pw = os.environ.get("DB_PASSWORD")

# If password is not defined, prompt the user to input it
if not pw:
    pw = getpass.getpass()

mydb = mysql.connector.connect(
    host="localhost", user="root", password=pw, database="cardb"
)

mycursor = mydb.cursor()

car_name = input("Input car name: ")
query = f"select Name, `Retail Price` from cars where name like '{car_name}%'"

# Execute the query
mycursor.execute(query)
results = mycursor.fetchall()

if results:
    for row in results:
        print(row)
else:
    print("No matching records.")

mycursor.close()
mydb.close()
