CREATE_ROLE_TABLE = """
				CREATE TABLE IF NOT EXISTS role (
				role_id INTEGER PRIMARY KEY,
				name TEXT NOT NULL UNIQUE
				);
			"""

INSERT_DEFAULT_ROLES = [
    "PRAGMA foreign_keys = ON;",
    "INSERT INTO role (role_id, name) SELECT 1, 'super_admin' WHERE NOT EXISTS (SELECT 1 FROM role WHERE role_id = 1);",
    "INSERT INTO role (role_id, name) SELECT 2, 'admin' WHERE NOT EXISTS (SELECT 1 FROM role WHERE role_id = 2);",
    "INSERT INTO role (role_id, name) SELECT 3, 'consultant' WHERE NOT EXISTS (SELECT 1 FROM role WHERE role_id = 3);",
]


def intitialize_role_table(con):
    cursor = con.cursor()
    cursor.execute(CREATE_ROLE_TABLE)
    con.commit()


def add_default_user_roles(con):
    cursor = con.cursor()
    for role in INSERT_DEFAULT_ROLES:
        cursor.execute(role)
    con.commit()
