import database






def main():
    con = database.connect()
    database.create_tables(con)


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




    """)
    username = input("Username:")
    password = input("Password:")

    if username is not None and password is not None:
        get_user = database.get_user(con,username, password)
        print(f""" Welcome, {get_user.name} choose one of the options below: """)
        print(get_user.role_id)

    # database.register_consultant(con,"c3@company.nl","test12345","0612345677")
    # database.update_consultant(con,3,"0612345699")
    # database.delete_user(con,3)





if "__main__" == __name__:
    main()