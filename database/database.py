import sqlite3

sql_statements =  [
			"""
                CREATE TABLE IF NOT EXISTS role (
                role_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
                );
			""",

			"""
			CREATE TABLE IF NOT EXISTS user (
                user_id INTEGER PRIMARY KEY , 
                assigned_role_id INTEGER,
                name TEXT NOT NULL, 
                lastname TEXT NOT NULL, 
                age INTEGER NOT NULL, 
                gender TEXT NOT NULL, 
                weight INTEGER NOT NULL, 
                email TEXT NOT NULL UNIQUE, 
                mobile TEXT NOT NULL UNIQUE, 
                password TEXT NOT NULL,
                FOREIGN KEY (assigned_role_id) REFERENCES role(role_id)
                );
			"""
                
                ,
			"""
            	CREATE TABLE IF NOT EXISTS membership (
                id INTEGER PRIMARY KEY,
                member_user_id INTEGER,
                registration_date TEXT NOT NULL,
                FOREIGN KEY(member_user_id) REFERENCES user(user_id)
                
                );
			""",
                
			"""
                CREATE TABLE IF NOT EXISTS address (
                address_id INTEGER PRIMARY KEY,
                streetname TEXT NOT NULL,
                house_number INTEGER NOT NULL,
                zipcode INTEGER NOT NULL,
                city TEXT NOT NULL
                
                );
			""",
                     
			"""
                CREATE TABLE IF NOT EXISTS user_address (
                user_Id INTEGER,
                address_Id INTEGER,
                PRIMARY KEY (user_id, address_id),
                FOREIGN KEY (user_Id) REFERENCES user(user_id)
                FOREIGN KEY (address_Id) REFERENCES address(address_id)
                );
			""",
			"""
                CREATE TABLE IF NOT EXISTS user_role (
                user_Id INTEGER,
                role_id INTEGER,
                PRIMARY KEY (user_id, role_id),
                FOREIGN KEY (user_Id) REFERENCES user(user_id)
                FOREIGN KEY (role_Id) REFERENCES role(role_id)
                );
			"""
]




def create_tables():
    try:
        with sqlite3.connect('data.db') as conn:
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            for statement in sql_statements:
                cursor.execute(statement)
                conn.commit()
    except sqlite3.Error as e:
            print(e)
          
create_tables()

