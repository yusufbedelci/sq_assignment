import sqlite3
from user import User

CREATE_TABLES =  [
			#TODO: add cascade on delete
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
				username TEXT NOT NULL UNIQUE,
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
			""",
			"""
				CREATE TABLE IF NOT EXISTS user_profile (
				profile_id INTEGER PRIMARY KEY ,
				name TEXT NOT NULL,
				lastname TEXT NOT NULL,
				age INTEGER NOT NULL,
				gender TEXT NOT NULL,
				weight INTEGER NOT NULL,
				FOREIGN KEY (profile_Id) REFERENCES user(user_id)
				);
			""",
			"""
			INSERT INTO role (role_id,name) VALUES (1,'super_admin');
			
			""",
			"INSERT INTO role (role_id,name) VALUES (3,'consultant');",
			
			"INSERT INTO role (role_id,name) VALUES (2,'admin');",
		
			"""
			INSERT INTO user (assigned_role_id,username, email, mobile, password) VALUES (1,'super_admin','super@company.nl',0612341566,'Admin_123?');
			""",
			"""
			INSERT INTO user_profile (name, lastname, age, gender, weight) VALUES ('SUPER', 'USER', 20, 'male',200);
			""",
			"""
			INSERT INTO user_role (user_id, role_id) VALUES (1,1);
			"""
			]




def connect():
	return sqlite3.connect("data.db")





def create_tables(connection):
	with connection:
		# connection.execute('PRAGMA foreign_keys = ON;')
		for statement in CREATE_TABLES:
			connection.execute(statement)


def get_user(connection, username:str, password:str) -> tuple:
		x = connection.execute(f'SELECT name || " " || lastname AS fullname, user_id AS id, assigned_role_id as role_id, email,password, mobile, age, gender, weight FROM user INNER JOIN user_profile ON user.user_id = user_profile.profile_id WHERE username="{username}" AND password="{password}"').fetchone()
		# TODO: change __repr__ of this x; the user
		fullname, id,role_id, email,password,mobile, age, gender, weight = x
		new_user = User(id=id,role_id=role_id, name=fullname,email=email,password=password,mobile=mobile)
		return new_user



def register_consultant(connection,email:str, password:str, mobile:str) -> tuple:
	statements = ['PRAGMA foreign_keys = ON;',f'INSERT INTO user(assigned_role_id,email,mobile, password) VALUES(2,"{email}","{mobile}","{password}")']
	for statement in statements:
		connection.execute(statement)
	connection.commit()
	print("Consultant created!")




def update_consultant(connection,assigned_role_id,mobile):
	# TODO: update only the columns when there are new values given
	connection.execute('PRAGMA foreign_keys = ON;')
	# connection.execute(f'UPDATE user SET assigned_role_id="3",email="{email}",mobile="{mobile}",password="{password}" WHERE user_id ="2"')
	connection.execute(f'UPDATE user SET assigned_role_id="{assigned_role_id}",mobile="{mobile}" WHERE user_id ="2"')
	connection.commit()
	print("user is updated")





def delete_user(connection, user_id):
	statements = ['PRAGMA foreign_keys = ON;',f'DELETE from user WHERE user_id="{user_id}"']
	for statement in statements:
		connection.execute(statement)
	connection.commit()
	print("User is deleted")