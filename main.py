import database



def main():
    con = database.connect()


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
    email = input("Email:")
    password = input("Password:")

    if email is not None and password is not None:
        get_user = database.get_user(con,email, password)
        if get_user:
            print(get_user)





if "__main__" == __name__:
    main()