from entities.profile import Profile


class MemberManager:
    def __init__(self, con):
        self.con = con

    @staticmethod
    def initialize(con):
        CREATE_PROFILES_TABLE = """
                CREATE TABLE IF NOT EXISTS profiles (
                profile_id INTEGER PRIMARY KEY ,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                registration_date TEXT NOT NULL,
                FOREIGN KEY (profile_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
            """

        cursor = con.cursor()
        cursor.execute(CREATE_PROFILES_TABLE)
        con.commit()
        cursor.close()
