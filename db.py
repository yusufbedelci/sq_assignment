import sqlite3
from user import Profile, User

def get_user(connection, username: str, password: str) -> tuple:
    user_object = connection.execute(
        f'SELECT name || " " || lastname AS fullname, user_id AS id, assigned_role_id as role_id, email,username, password, mobile, age, gender, weight FROM user INNER JOIN user_profile ON user.user_id = user_profile.profile_id WHERE username="{username}" AND password="{password}"'
    ).fetchone()
    if user_object is not None:
        (
            fullname,
            id,
            role_id,
            email,
            username,
            password,
            mobile,
            age,
            gender,
            weight,
        ) = user_object
        new_user = Profile(
            id,
            fullname,
            role_id,
            email,
            username,
            password,
            mobile,
            age,
            gender,
            weight,
        )
        return new_user
    else:
        print("User is invalid!")
    # TODO change global Exception to custom Exception.


def create_admin_account(
    connection,
    current_role,
    new_user_role,
    username: str,
    email: str,
    password: str,
    mobile,
    name,
    lastname,
    age,
    gender,
    weight,
) -> tuple:

    if current_role == 1:
        statements = [
            "PRAGMA foreign_keys = ON;",
            f'INSERT INTO user(assigned_role_id,username, email,mobile, password) VALUES({new_user_role},"{username}","{email}","{mobile}","{password}");',
            f'INSERT INTO user_profile (name, lastname, age, gender, weight) VALUES ("{name}", "{lastname}", "{age}", "{gender}","{weight}");',
        ]
        for statement in statements:
            connection.execute(statement)
        connection.commit()

        id, role = connection.execute(
            f'SELECT user_id, assigned_role_id FROM user WHERE username="{username}"'
        ).fetchone()
        connection.execute(
            f'INSERT INTO user_role (user_id, role_id) VALUES ("{id}","{role}")'
        )
        connection.commit()

        return True
    else:
        # TODO: trow exception because you are not superadmin!
        return False


def update_consultant(connection, assigned_role_id, mobile):
    # TODO: update only the columns when there are new values given
    connection.execute("PRAGMA foreign_keys = ON;")
    # connection.execute(f'UPDATE user SET assigned_role_id="3",email="{email}",mobile="{mobile}",password="{password}" WHERE user_id ="2"')
    connection.execute(
        f'UPDATE user SET assigned_role_id="{assigned_role_id}",mobile="{mobile}" WHERE user_id ="2"'
    )
    connection.commit()
    print("user is updated")


def get_all_users(connection, user_id):
    users = connection.execute(
        f'SELECT name || " " || lastname AS fullname, user_id AS id, assigned_role_id as role_id, email,username, password, mobile, age, gender, weight FROM user INNER JOIN user_profile ON user.user_id = user_profile.profile_id'
    ).fetchall()
    user_objects = []
    if users != 0:
        for user in users:
            (
                fullname,
                id,
                role_id,
                email,
                username,
                password,
                mobile,
                age,
                gender,
                weight,
            ) = user
            user_profile = Profile(
                id,
                fullname,
                role_id,
                email,
                username,
                password,
                mobile,
                age,
                gender,
                weight,
            )
            if id != user_id:
                user_objects.append(user_profile)
    else:
        print()
        print("Message: \nThere are currenlty no users stored in the database.")

    print(
        "-----------------------------------USERS----------------------------------------------------"
    )
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
        print(
            "-----------------------------------------------------------------------------------------"
        )


def delete_user(connection, role_id, user_id):
    if int(user_id) != 1 and int(role_id) == 1 or int(role_id) == 2:
        statements = [
            "PRAGMA foreign_keys = ON;",
            f'DELETE from user WHERE user_id="{user_id}"',
        ]
        for statement in statements:
            connection.execute(statement)
        connection.commit()
        print("User is deleted")
    else:
        # TODO: make try-except block

        print("Deletion has failed")
