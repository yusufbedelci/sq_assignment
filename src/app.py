import os
import tkinter as tk
from tkinter import ttk
from config import Config
from tkinter import messagebox
from forms.reset_form import OtherResetForm, UserResetForm
from managers.address_manager import AddressManager
from managers.member_manager import MemberManager
from managers.profile_manager import ProfileManager
from managers.user_manager import UserManager
from backups import Backups

# from forms.Form import CreateForm, DeleteForm, UpdateForm
from forms.user_forms import *
from forms.member_forms import *
from entities.user import User
from entities.member import Member
from app_logger import AppLogger


class App:
    config: Config
    logger = AppLogger("my_app.log")

    def __init__(self, root, config):
        self.root = root
        App.config = config

        self.user_manager = UserManager(config)
        self.address_manager = AddressManager(config)
        self.member_manager = MemberManager(config)
        self.profile_manager = ProfileManager(config)

        self.login_attempts = 0
        self.init_db()

        self.root.title("Login")
        # set basic gui settings
        self.root.maxsize(1200, 1000)
        self.root.config(bg="RoyalBlue4")
        self.root.option_add("*Label*background", "RoyalBlue2")
        self.root.option_add("*Label*foreground", "white")

        self.user = None
        self.create_login_screen()

    def run(self):
        self.root.mainloop()

    def init_db(self):
        self.user_manager.initialize()
        self.user_manager.create_super_admin()
        self.address_manager.initialize()
        self.member_manager.initialize()
        self.profile_manager.initialize()

    def create_login_screen(self):
        self.clear_screen()
        title_label = tk.Label(
            self.root, text="Login", font=("Arial", 16, "bold"), bg="RoyalBlue4"
        )
        title_label.pack(pady=10)

        un = tk.StringVar(value="super_admin")
        pw = tk.StringVar(value="Admin_123?")

        self.username_label = tk.Label(self.root, text="Username", bg="RoyalBlue4")
        self.username_label.pack(pady=10, padx=100)
        self.username_entry = tk.Entry(self.root, width=100, textvariable=un)
        self.username_entry.pack(pady=10, padx=100)

        self.password_label = tk.Label(self.root, text="Password", bg="RoyalBlue4")
        self.password_label.pack(pady=10, padx=100)
        self.password_entry = tk.Entry(self.root, show="*", width=100, textvariable=pw)
        self.password_entry.pack(pady=10, padx=100)

        self.login_button = tk.Button(self.root, text="Login", command=self.login)
        self.login_button.pack(pady=20, padx=100)

    def logout(self):
        self.user = None
        self.create_login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def make_frames(self):
        self.left_frame = tk.Frame(self.root, width=400, height=100, bg="RoyalBlue2")
        self.left_frame.grid(row=0, column=0, padx=20, pady=50)

        self.right_frame = tk.Frame(self.root, width=1000, height=100, bg="RoyalBlue2")
        self.right_frame.grid(row=0, column=1, padx=20, pady=50)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = self.user_manager.login(username, password)

        if user:
            self.user = user
            self.user_manager.update_last_login(user)
            if user.reset_password == 1:
                reset_form = UserResetForm(
                    self.root, App.config, self.create_login_screen
                )
                reset_form.show_form(self.user, self.user.username)

            else:
                App.logger.log_activity(
                    self.user, "Login", "Login was sucessfull", False
                )

                # send user to default page (based on role)
                if (
                    self.user.role == User.Role.SUPER_ADMIN.value
                    or self.user.role == User.Role.SYSTEM_ADMIN.value
                ):
                    critical_logs = App.logger.get_critical_logs(self.user.last_login)
                    print(critical_logs)
                    if len(critical_logs) > 0:
                        messagebox.showwarning(
                            "Critical log warning",
                            "There are some critical logs to review",
                        )
                        self.view_logs()
                    else:
                        self.view_users()

                elif self.user.role == User.Role.CONSULTANT.value:
                    self.view_members()
        else:
            self.login_attempts += 1
            App.logger.log_activity(
                user,
                "Login failed",
                f"username: {username} is used for a login attempt with a wrong password",
                False,
            )
            if self.login_attempts >= 3:
                App.logger.log_activity(
                    self.user,
                    "Unsuccesfull Login",
                    f"Multiple usernames and passwords are tried in a row",
                    True,
                )

            messagebox.showerror("Login Failed", "Invalid username or password")

    #
    # Navbar screens
    #
    def create_navbar(self, role, current_page):
        def handle_options(option):
            if option == "Logs":
                self.view_logs()
            elif option == "Users":
                self.view_users()

            elif option == "Members":
                self.view_members()
            elif option == "Reset password":
                self.view_password_reset_screen()
            elif option == "Reset my password":
                self.reset_my_password()
            elif option == "Backups":
                self.view_backups()
            elif option == "Logout":
                self.logout()

        label = tk.Label(
            self.left_frame, text="Super Admin Panel", fg="white", bg="RoyalBlue2"
        )
        label.pack()

        # print list of menu options
        menu_options = [
            "Logs",
            "Users",
            "Members",
            "Reset password",
            "Reset my password",
            "Backups",
            "Logout",
        ]

        if role == User.Role.CONSULTANT.value:
            menu_options = menu_options[2:]

        for i, option in enumerate(menu_options):
            if current_page == option:
                button = tk.Button(
                    self.left_frame,
                    text=option,
                    width=10,
                    fg="blue",
                    command=lambda option=option: handle_options(option),
                )
            else:
                button = tk.Button(
                    self.left_frame,
                    text=option,
                    width=10,
                    command=lambda option=option: handle_options(option),
                )

            button.pack(pady=10, padx=10)

    def view_password_reset_screen(self):
        self.clear_screen()
        self.make_frames()
        self.create_navbar(self.user.role, "Reset password")

        reset_form = OtherResetForm(self.right_frame, App.config, self.correct_menu())
        tree = ttk.Treeview(
            self.right_frame, columns=("Username", "Role", "Reset"), show="headings"
        )

        def on_username_click(event):
            item = tree.selection()[0]
            username = tree.item(item, "values")[0]
            reset_form.show_form(self.user, username)

        users_list = self.user_manager.get_users()
        users = []
        for user in users_list:
            if (
                self.user.role == User.Role.SUPER_ADMIN.value
                and user.role != User.Role.SUPER_ADMIN.value
            ):
                users.append(user)
            elif (
                self.user.role == User.Role.SYSTEM_ADMIN.value
                and user.role != User.Role.SUPER_ADMIN.value
                and user.role != User.Role.SYSTEM_ADMIN.value
            ):
                users.append(user)

        for user in users:
            username = user.username
            role = user.role
            reset = user.reset_password
            tree.insert("", "end", values=(username, role, reset))
        tree.heading("Username", text="Username")
        tree.heading("Role", text="Role")
        tree.heading("Reset", text="Reset")
        tree.pack(padx=10, pady=10)
        tree.bind("<Double-1>", on_username_click)

        # home button
        self.home_button = tk.Button(
            self.right_frame, text="🏠", command=self.correct_menu()
        )
        self.home_button.pack(pady=5)

    def reset_my_password(self):
        self.clear_screen()
        self.make_frames()
        self.create_navbar(self.user.role, "Reset my password")

        reset_form = UserResetForm(
            self.right_frame, App.config, self.create_login_screen
        )
        reset_form.show_form(self.user, self.user.username)

    #
    # generic screens
    #
    def view_logs(self):
        self.clear_screen()
        self.make_frames()
        self.create_navbar(self.user.role, "Logs")

        title_label = tk.Label(
            self.right_frame,
            text="Manage logs",
            font=("Arial", 16, "bold"),
            fg="white",
        )
        title_label.pack(pady=10)

        def on_log_click(event):
            item = tree.selection()[0]
            no = tree.item(item, "values")[0]
            datetime = tree.item(item, "values")[1]
            level = tree.item(item, "values")[2]
            description = tree.item(item, "values")[3]
            self.clear_screen()
            self.make_frames()
            self.create_navbar(self.user.role, "Logs")

            content = tk.Text(self.right_frame, wrap="word", width=100, height=10)
            content.insert("end", f"No: {no}\n")
            content.insert("end", f"Date & Time: {datetime}\n")
            content.insert("end", f"Level: {level}\n")
            content.insert("end", f"Description: {description}\n")

            content.pack()

            # back button
            self.back_button = tk.Button(
                self.right_frame, text="Back", command=self.view_logs
            )
            self.back_button.pack(pady=5)

        tree = ttk.Treeview(
            self.right_frame,
            columns=("No", "Datetime", "Level", "Description"),
            show="headings",
        )
        tree.heading("No", text="No")
        tree.heading("Datetime", text="Datetime")
        tree.heading("Level", text="Level")
        tree.heading("Description", text="Description")

        tree.tag_configure(
            "bold_tag",
            background="red",
            font="TkFixedFont",
        )

        tree.pack(padx=10, pady=10)
        tree.bind("<Double-1>", on_log_click)

        logs = App.logger.get_logs_sorted(self.user.last_login)
        for id, line in enumerate(logs):
            r_id = len(logs) - id - 1

            if line[0] == "unread":
                tree.insert(
                    "",
                    "end",
                    values=(r_id, line[1][0], line[1][1], line[1][2]),
                    tags=("bold_tag",),
                )
            else:
                tree.insert(
                    "",
                    "end",
                    values=(r_id, line[1][0], line[1][1], line[1][2]),
                )

    def view_users(self):
        self.clear_screen()
        self.make_frames()
        self.create_navbar(self.user.role, "Users")

        title_label = tk.Label(
            self.right_frame,
            text="Manage users",
            font=("Arial", 16, "bold"),
            fg="white",
        )
        title_label.pack(pady=10)

        def on_username_click(event):
            item = tree.selection()[0]
            username = tree.item(item, "values")[0]
            role = tree.item(item, "values")[1]
            if (
                self.user.role == User.Role.SYSTEM_ADMIN.value
                and role == User.Role.SYSTEM_ADMIN.value
            ):
                return

            update_form = UpdateUserForm(
                self.right_frame,
                App.config,
                role,
                self.user,
                self.user.role,
                self.view_users,
            )
            update_form.show_form(username)

        description_label = tk.Label(
            self.right_frame,
            text="On this page users can be managed. Double click on a user to edit.",
            font=("Arial", 12),
        )
        description_label.pack()

        def add_new_user():
            form = CreateUserForm(
                self.right_frame,
                App.config,
                User.Role.SYSTEM_ADMIN.value,
                self.user.role,
                self.user,
                self.view_users,
            )
            form.show_form()

        button = tk.Button(
            self.right_frame,
            text="Add new",
            width=10,
            command=lambda: add_new_user(),
        )
        button.pack(side="top", anchor="w", pady=(20, 0), padx=10)

        tree = ttk.Treeview(
            self.right_frame, columns=("Username", "Role"), show="headings"
        )
        tree.heading("Username", text="Username")
        tree.heading("Role", text="Role")
        tree.pack(padx=10, pady=10)
        tree.bind("<Double-1>", on_username_click)

        users = reversed(sorted(self.user_manager.get_users(), key=lambda x: x.role))
        for user in users:
            if user.role == User.Role.SUPER_ADMIN.value:
                continue
            username = user.username
            role = user.role
            tree.insert("", "end", values=(username, role))

    def view_members(self):
        self.clear_screen()
        self.make_frames()
        self.create_navbar(self.user.role, "Members")

        title_label = tk.Label(
            self.right_frame, text="Manage members", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        description_label = tk.Label(
            self.right_frame,
            text="On this page members can be managed. Double click on a member to edit.",
            font=("Arial", 12),
        )
        description_label.pack()

        def add_new_member():
            form = CreateMemberForm(self.right_frame, App.config, self.view_members)
            form.show_form()

        button = tk.Button(
            self.right_frame,
            text="Add new",
            width=10,
            command=lambda: add_new_member(),
        )
        button.pack(side="top", anchor="w", pady=(20, 0), padx=10)

        button = tk.Button(
            self.right_frame, text="🔍", width=10, command=lambda: go_search()
        )
        button.pack(side="right", anchor="w", pady=(20, 0), padx=10)

        def on_member_click(event):
            item = tree.selection()[0]
            id = tree.item(item, "values")[0]
            update_form = UpdateMemberForm(
                self.right_frame, App.config, self.view_members
            )
            update_form.show_form(int(id))

        tree = ttk.Treeview(
            self.right_frame,
            columns=("ID", "First Name", "Last Name"),
            show="headings",
        )
        tree.heading("ID", text="ID")
        tree.heading("First Name", text="First Name")
        tree.heading("Last Name", text="Last Name")
        tree.pack(padx=10, pady=10)
        tree.bind("<Double-1>", on_member_click)

        members = self.member_manager.get_members()
        for member in members:
            id = member.id
            first_name = member.first_name
            last_name = member.last_name
            tree.insert("", "end", values=(id, first_name, last_name))

        def go_search():
            self.clear_screen()
            self.make_frames()
            self.create_navbar(self.user.role, "Members")

            title_label = tk.Label(
                self.right_frame, text="Search members", font=("Arial", 16, "bold")
            )
            title_label.pack(pady=10)

            search_field = tk.Entry(self.right_frame, width=50)
            search_field.pack(pady=10, padx=25)

            search_button = tk.Button(
                self.right_frame, text="Search", command=handle_search
            )
            search_button.pack(pady=5, padx=20)

        def handle_search():
            search_field = tk.Entry(self.right_frame, width=50)
            search_field.pack(pady=10, padx=25)

            search_results = self.member_manager.search_members(search_field.get())

            self.clear_screen()
            self.make_frames()
            self.create_navbar(self.user.role, "Members")

            tree = ttk.Treeview(
                self.right_frame,
                columns=(
                    "Membership ID",
                    "First Name",
                    "Last Name",
                    "Email",
                    "Phone Number",
                ),
                show="headings",
            )
            tree.heading("Membership ID", text="Membership ID")
            tree.heading("First Name", text="First Name")
            tree.heading("Last Name", text="Last Name")
            tree.heading("Email", text="Email")
            tree.heading("Phone Number", text="Phone Number")
            tree.pack(padx=10, pady=10)

            for member in search_results:
                tree.insert(
                    "",
                    "end",
                    values=(
                        member.membership_id,
                        member.first_name,
                        member.last_name,
                        member.email,
                        member.phone_number,
                    ),
                )

            # back button
            self.back_button = tk.Button(
                self.right_frame, text="Back", command=self.view_members
            )
            self.back_button.pack(pady=5)

    def view_backups(self):
        self.clear_screen()
        self.make_frames()
        self.create_navbar(self.user.role, "Backups")

        title_label = tk.Label(
            self.right_frame, text="Backup options: ", font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)

        self.backup_manager = Backups(App.config)

        def new_backup():
            self.backup_manager.create()
            messagebox.showinfo("Backup Created", "Backup created successfully")
            self.view_backups()

        button = tk.Button(
            self.right_frame,
            text="Add new",
            width=10,
            command=lambda: new_backup(),
        )
        button.pack(side="top", anchor="w", pady=(20, 0), padx=10)

        backups = self.backup_manager.list()
        tree = ttk.Treeview(self.right_frame, columns=("Back up"), show="headings")

        def on_backup_click(event):
            item = tree.selection()[0]
            backup = tree.item(item, "values")[0]
            self.backup_manager.restore(backup)
            messagebox.showinfo("Backup Restored", "Backup restored successfully")

        for i, backup in enumerate(backups):
            tree.insert("", "end", values=(backup,))

        tree.pack(padx=10, pady=10)
        tree.bind("<Double-1>", on_backup_click)

    #
    # Helper functions
    #
    def correct_menu(self):
        if self.user.role == User.Role.SUPER_ADMIN.value:
            return self.view_users
        elif self.user.role == User.Role.SYSTEM_ADMIN.value:
            return self.view_users
        elif self.user.role == User.Role.CONSULTANT.value:
            return self.view_members
