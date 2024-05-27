import sqlite3
from typing import Any, List, Tuple

sql_statements =  [
       "PRAGMA foreign_keys = ON;",
			"""
                CREATE TABLE IF NOT EXISTS role (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
                );
			""",

			"""
			CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                role_id INTEGER NOT NULL,
                membership_id INTEGER NOT NULL,
                name TEXT NOT NULL, 
                lastname TEXT NOT NULL, 
                age INTEGER NOT NULL, 
                gender TEXT NOT NULL, 
                weight INTEGER NOT NULL, 
                email TEXT NOT NULL UNIQUE, 
                mobile INTEGER NOT NULL UNIQUE, 
                password TEXT NOT NULL,
                FOREIGN KEY (role_id) REFERENCES role(id)
                FOREIGN KEY (membership_id) REFERENCES membership(id)
                );
			"""
                ,
                
			"""
            	CREATE TABLE IF NOT EXISTS membership (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_date TEXT NOT NULL
                
                );
			""",
                
			"""
                CREATE TABLE IF NOT EXISTS address (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                streetname TEXT NOT NULL,
                house_number INTEGER NOT NULL,
                zipcode INTEGER NOT NULL,
                city TEXT NOT NULL
                
                );
			""",
                     
			"""
                CREATE TABLE IF NOT EXISTS user_address (
                user_id INTEGER,
                address_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES user(id)
                FOREIGN KEY (address_id) REFERENCES address(id)
                );
			""",
                     
					 
					 
					 
					 
					 
					 ]
        



connection = sqlite3.connect("data.db")
try:
	with sqlite3.connect('data.db') as conn:
            cursor = conn.cursor()
            for statement in  sql_statements:
                print(statement)
                cursor.execute(statement)
            
            conn.commit()
except sqlite3.Error as e:
          print(e)
          



# connection.execute(CREATE_TABLES)

def create_tables():
          pass