from database import initialize_database_tables, connect
import db


def main():
    initialize_database_tables()
    con = connect()
    print(
        """
                    ********************************************************
                    *                                                      *
                    *          Welcome to the Member Management System     *
                    *                                                      *
                    *           Unauthorized access is prohibited          *
                    *                                                      *
                    *                  Please login to continue            *
                    *                                                      *
                    ********************************************************
    """
    )
    # username = input("Username:")
    # password = input("Password:")
    count = 0

    while True:
        username = "super_admin"
        password = "Admin_123?"
        if username and password:
            user_account = db.get_user(con, username, password)
            if user_account != None:
                if user_account.role_id == 1:
                    choice = input(
                        f""" 
                        Welcome, {user_account.username} choose one of the options below. Role: {user_account.role_id}: 
                        (q)uit, to Exit the program.
                        (s)how users and roles
                        (u)pdate user
                        (d)elete consultant
                        (r)eset consultant
                        (a)dd new admin
                        (u)pdate admin
                        (d)elete admin
                        (r)eset admin
                        (m)ake backup
                        (rb)restore backup
                        (l)ogs
                        (a)dd member
                        (u)pdate member
                        (d)elete member
                        (s)earch for member
                        """
                    )
                    if choice == "q":
                        print("You have been logged out")
                        break
                    elif choice == "s":
                        db.get_all_users(con, user_account.role_id)

                    elif choice == "u":
                        pass
                    elif choice == "a":
                        print(count)
                        count += 4100
                        print(count)
                        # name = input("Firstname of new admin: ")
                        # lastname = input("Lastname of new admin: ")
                        username = f"qmina{count}"
                        email = f"qmin1{count}@company.nl"
                        password = "Test123"
                        mobile = f"0612362{count}"

                        # username = input("Username of new admin: ")
                        # email = input("Email of new admin: ")
                        # password = input("Password of new admin: ")
                        age = 400
                        # age = input("Age of user")
                        gender = "Female"
                        # gender = input("Gender of user")
                        # weight = input("Weight of user")
                        weight = 10000
                        name = "Mary"
                        lastname = "Joe"

                        db.create_admin_account(
                            con,
                            user_account.role_id,
                            2,
                            username,
                            email,
                            password,
                            mobile,
                            name,
                            lastname,
                            age,
                            gender,
                            weight,
                        )

                    elif choice == "d":
                        print(db.get_all_users(con, user_account.role_id))
                        user_id = input("Which user do you want to delete? ")
                        db.delete_user(con, user_account.role_id, user_id)

    # database.register_consultant(con,"c3@company.nl","test12345","0612345677")
    # database.update_consultant(con,3,"0612345699")
    # database.delete_user(con,3)


if "__main__" == __name__:
    main()
