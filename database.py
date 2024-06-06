import sqlite3
from user import Profile, User

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
				FOREIGN KEY (assigned_role_id) REFERENCES role(role_id) ON DELETE CASCADE
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
				FOREIGN KEY (profile_Id) REFERENCES user(user_id) ON DELETE CASCADE
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
		user_object = connection.execute(f'SELECT name || " " || lastname AS fullname, user_id AS id, assigned_role_id as role_id, email,username, password, mobile, age, gender, weight FROM user INNER JOIN user_profile ON user.user_id = user_profile.profile_id WHERE username="{username}" AND password="{password}"').fetchone()
		if(user_object is not None):
			fullname, id,role_id, email,username, password,mobile, age, gender, weight, = user_object
			new_user = Profile(id,fullname,role_id,email,username,password,mobile, age, gender, weight)
			return new_user
		else:
			print("User is invalid!")
		# TODO change global Exception to custom Exception.
			



def register_administrative_user(connection,current_role, new_user_role,
									username:str, email:str, password:str,mobile,
									name, lastname,age, gender, weight) -> tuple:
	
	if current_role == 1 or current_role == 2:
		statements = ['PRAGMA foreign_keys = ON;',f'INSERT INTO user(assigned_role_id,username, email,mobile, password) VALUES({new_user_role},"{username}","{email}","{mobile}","{password}");',f'INSERT INTO user_profile (name, lastname, age, gender, weight) VALUES ("{name}", "{lastname}", "{age}", "{gender}","{weight}");']
		for statement in statements:
			connection.execute(statement)
		connection.commit()
		return True
	else:
		return False




def update_consultant(connection,assigned_role_id,mobile):
	# TODO: update only the columns when there are new values given
	connection.execute('PRAGMA foreign_keys = ON;')
	# connection.execute(f'UPDATE user SET assigned_role_id="3",email="{email}",mobile="{mobile}",password="{password}" WHERE user_id ="2"')
	connection.execute(f'UPDATE user SET assigned_role_id="{assigned_role_id}",mobile="{mobile}" WHERE user_id ="2"')
	connection.commit()
	print("user is updated")



def get_all_users(connection, user_id):
	users = connection.execute(f'SELECT name || " " || lastname AS fullname, user_id AS id, assigned_role_id as role_id, email,username, password, mobile, age, gender, weight FROM user INNER JOIN user_profile ON user.user_id = user_profile.profile_id').fetchall()
	user_objects = []
	if users != 0:
		for user in users:
				fullname, id,role_id, email,username, password,mobile, age, gender, weight, = user
				user_profile = Profile(id,fullname,role_id,email,username,password,mobile, age, gender, weight)
				if id != user_id:
					user_objects.append(user_profile)
	else:
		print()
		print("Message: \nThere are currenlty no users stored in the database.")
		
	print("-----------------------------------USERS----------------------------------------------------")
	for u in user_objects:
		print("ID:", u.id)
		print("Full Name:", u.fullname)
		print("Role ID:", u.role_id)
		print("Email:", u.email)
		print("Username:", u.username)
		print("Password:", u.password)
		print("Mobile:", u.mobile)
		print("Age:", u.age)
		print("Gender:", u.gender)
		print("Weight:", u.weight)
		print("-----------------------------------------------------------------------------------------")




def delete_user(connection,role_id, user_id):
	if int(user_id) != 1 and int(role_id) == 1 or int(role_id) == 2:
		statements = ['PRAGMA foreign_keys = ON;',f'DELETE from user WHERE user_id="{user_id}"']
		for statement in statements:
			connection.execute(statement)
		connection.commit()
		print("User is deleted")
	else:
		# TODO: make try-except block

		print("Deletion has failed")



