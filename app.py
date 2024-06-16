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
    logger = AppLogger('my_app.log')

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
        title_label = tk.Label(self.root, text="Login", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        self.username_label = tk.Label(self.root, text="Username")
        self.username_label.pack(pady=10)
        self.username_entry = tk.Entry(self.root, width=100)
        self.username_entry.pack(pady=10)

        self.password_label = tk.Label(self.root, text="Password")
        self.password_label.pack(pady=10)
        self.password_entry = tk.Entry(self.root, show="*", width=100)
        self.password_entry.pack(pady=10)

        self.login_button = tk.Button(self.root, text="Login", command=self.login)
        self.login_button.pack(pady=20)

    def logout(self):
        self.user = None
        self.create_login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = self.user_manager.login(username, password)
        if user:
            self.user = user
            if user.reset_password == 1:
                reset_form = UserResetForm(
                    self.root, App.config, self.create_login_screen
                )
                reset_form.show_form(self.user, self.user.username)

            else:
                App.logger.log_activity(self.user.username,"Login", " ", False)

                self.create_main_screen()
        else:
            self.login_attempts+=1
            App.logger.log_activity(f"{username}","Unsuccesfull Login", f"username: {username} is used for a login attempt with a wrong password", False)
            if self.login_attempts >= 3:
                App.logger.log_activity(f"{username}","Unsuccesfull Login", f"Multiple usernames and passwords are tried in a row", True)

            messagebox.showerror("Login Failed", "Invalid username or password")

    def create_main_screen(self):
        self.clear_screen()

        welcome_label = tk.Label(self.root, text=f"Welcome, {self.user.username}")
        welcome_label.pack(pady=5)

        logout_button = tk.Button(self.root, text="Logout", command=self.logout)
        logout_button.pack(pady=5)

        # make dividers
        divider = tk.Label(self.root, text="---------------------------------")
        divider.pack(pady=5)

        # Display role-based content
        if self.user.role == "super_admin":
            self.create_super_admin_screen()
        elif self.user.role == "system_admin":
            self.create_system_admin_screen()
        elif self.user.role == "consultant":
            self.create_consultant_screen()

    #
    # Super admin screens
    #
    def create_super_admin_screen(self):
        self.clear_screen()

        def handle_super_options(option):
            if option == "System Admin":
                self.view_sysadmin()
            elif option == "Consultant":
                self.view_consultant()
            elif option == "Members":
                self.view_members()
            elif option == "Reset password":
                self.view_password_reset_screen()
            elif option == "Reset my password":
                reset_form = UserResetForm(
                    self.root, App.config, self.create_login_screen
                )
                reset_form.show_form(self.user, self.user.username)
                # home button
                self.home_button = tk.Button(
                    self.root, text="🏠", command=self.correct_menu()
                )
                self.home_button.pack(pady=5)
            elif option == "Backups":
                self.view_backups()
            elif option == "Logout":
                self.logout()

        label = tk.Label(self.root, text="Super Admin Panel")
        label.pack()

        # print list of menu options
        menu_options = [
            "System Admin",
            "Consultant",
            "Members",
            "Reset password",
            "Reset my password",
            "Backups",
            "Logout",
        ]

        for i, option in enumerate(menu_options):
            button = tk.Button(
                self.root,
                text=option,
                width=50,
                command=lambda option=option: handle_super_options(option),
            )
            button.pack(pady=5)

    #
    # System admin screens
    #
    def create_system_admin_screen(self):
        self.clear_screen()

        def handle_sysadmin_options(option):
            if option == "Consultant":
                self.view_consultant()
            elif option == "Members":
                self.view_members()
            elif option == "Reset password":
                self.view_password_reset_screen()
            elif option == "Reset my password":
                reset_form = UserResetForm(
                    self.root, App.config, self.create_login_screen
                )
                reset_form.show_form(self.user, self.user.username)
                # home button
                self.home_button = tk.Button(
                    self.root, text="🏠", command=self.correct_menu()
                )
                self.home_button.pack(pady=5)
            elif option == "Backups":
                self.view_backups()
            elif option == "Logout":
                self.logout()

        label = tk.Label(self.root, text="System Admin Panel")
        label.pack()

        # print list of menu options
        menu_options = [
            "Consultant",
            "Members",
            "Reset password",
            "Reset my password",
            "Backups",
            "Logout",
        ]

        for i, option in enumerate(menu_options):
            button = tk.Button(
                self.root,
                text=option,
                width=50,
                command=lambda option=option: handle_sysadmin_options(option),
            )
            button.pack(pady=5)

    #
    # Consultant screens
    #
    def create_consultant_screen(self):
        self.clear_screen()

        def handle_consultant_options(option):
            if option == "Members":
                self.view_members()
            elif option == "Reset my password":
                reset_form = UserResetForm(
                    self.root, App.config, self.create_login_screen
                )
                reset_form.show_form(self.user, self.user.username)
                # home button
                self.home_button = tk.Button(
                    self.root, text="🏠", command=self.correct_menu()
                )
                self.home_button.pack(pady=5)
            elif option == "Logout":
                self.logout()

        label = tk.Label(self.root, text="Consultant Panel")
        label.pack()

        # print list of menu options
        menu_options = ["Members", "Reset my password", "Logout"]

        for i, option in enumerate(menu_options):
            button = tk.Button(
                self.root,
                text=option,
                width=50,
                command=lambda option=option: handle_consultant_options(option),
            )
            button.pack(pady=5)

    def view_password_reset_screen(self):
        self.clear_screen()
        reset_form = OtherResetForm(self.root, App.config, self.create_login_screen)
        tree = ttk.Treeview(
            self.root, columns=("Username", "Role", "Reset"), show="headings"
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
        self.home_button = tk.Button(self.root, text="🏠", command=self.correct_menu())
        self.home_button.pack(pady=5)

    #
    # generic screens
    #
    def view_sysadmin(self):
        self.clear_screen()
        title_label = tk.Label(
            self.root, text="Menu Options: ", font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)

        def handle_option(option):
            if option == "Create sysadmin":
                # self.view_sysadmin()
                form = CreateUserForm(
                    self.root,
                    App.config,
                    User.Role.SYSTEM_ADMIN.value,
                    self.view_sysadmin,
                )
                form.show_form()

            elif option == "Delete sysadmin":
                delete_form = DeleteUserForm(
                    self.root,
                    App.config,
                    User.Role.SYSTEM_ADMIN.value,
                    self.view_sysadmin,
                )
                delete_form.show_form()

            elif option == "List sysadmins":
                self.clear_screen()
                tree = ttk.Treeview(
                    self.root, columns=("Username", "Role"), show="headings"
                )
                tree.heading("Username", text="Username")
                tree.heading("Role", text="Role")
                tree.pack(padx=10, pady=10)

                users = self.user_manager.get_users()
                for user in users:
                    if user.role == User.Role.SYSTEM_ADMIN.value:
                        username = user.username
                        role = user.role
                        tree.insert("", "end", values=(username, role))
                tree.bind("<Double-1>")

                # back button
                self.back_button = tk.Button(
                    self.root, text="Back", command=self.view_sysadmin
                )
                self.back_button.pack(pady=5)

            elif option == "Update sysadmin":
                self.clear_screen()
                update_form = UpdateUserForm(
                    self.root,
                    App.config,
                    User.Role.SYSTEM_ADMIN.value,
                    self.view_sysadmin,
                )

                def on_username_click(event):
                    item = tree.selection()[0]
                    username = tree.item(item, "values")[0]
                    update_form.show_form(username)

                label = tk.Label(
                    self.root, text="Create new user", font=("Arial", 16, "bold")
                )
                label = tk.Label(self.root, text="Update User")
                label.pack()

                description_label = tk.Label(
                    self.root,
                    text="Double click on an user to update: ",
                    font=("Arial", 10),
                )
                description_label.pack()

                tree = ttk.Treeview(
                    self.root, columns=("Username", "Role"), show="headings"
                )
                tree.heading("Username", text="Username")
                tree.heading("Role", text="Role")
                tree.pack(padx=10, pady=10)
                tree.bind("<Double-1>", on_username_click)

                users = self.user_manager.get_users()
                for user in users:
                    if user.role == User.Role.SYSTEM_ADMIN.value:
                        username = user.username
                        role = user.role
                        tree.insert("", "end", values=(username, role))

                # back button
                self.back_button = tk.Button(
                    self.root, text="Back", command=self.view_sysadmin
                )
                self.back_button.pack(pady=5)

        menu_options = [
            "List sysadmins",
            "Create sysadmin",
            "Update sysadmin",
            "Delete sysadmin",
        ]
        for i, option in enumerate(menu_options):
            button = tk.Button(
                self.root,
                text=option,
                width=50,
                command=lambda option=option: handle_option(option),
            )
            button.pack(pady=5)

        self.home_button = tk.Button(self.root, text="🏠", command=self.correct_menu())
        self.home_button.pack(pady=5)

    def view_consultant(self):
        self.clear_screen()
        title_label = tk.Label(
            self.root, text="Menu Options: ", font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)

        def handle_option(option):
            if option == "Create consultant":
                form = CreateUserForm(
                    self.root,
                    App.config,
                    User.Role.CONSULTANT.value,
                    self.view_consultant,
                )
                form.show_form()

            elif option == "Delete consultant":
                delete_form = DeleteUserForm(
                    self.root,
                    App.config,
                    User.Role.CONSULTANT.value,
                    self.view_consultant,
                )
                delete_form.show_form()

            elif option == "List consultants":
                self.clear_screen()
                tree = ttk.Treeview(
                    self.root, columns=("Username", "Role"), show="headings"
                )
                tree.heading("Username", text="Username")
                tree.heading("Role", text="Role")
                tree.pack(padx=10, pady=10)

                users = self.user_manager.get_users()
                for user in users:
                    if user.role == User.Role.CONSULTANT.value:
                        username = user.username
                        role = user.role
                        tree.insert("", "end", values=(username, role))
                tree.bind("<Double-1>")

                # back button
                self.back_button = tk.Button(
                    self.root, text="Back", command=self.view_consultant
                )
                self.back_button.pack(pady=5)

            elif option == "Update consultant":
                self.clear_screen()
                update_form = UpdateUserForm(
                    self.root,
                    App.config,
                    User.Role.CONSULTANT.value,
                    self.view_consultant,
                )

                def on_username_click(event):
                    item = tree.selection()[0]
                    username = tree.item(item, "values")[0]
                    update_form.show_form(username)

                label = tk.Label(
                    self.root, text="Update User", font=("Arial", 16, "bold")
                )
                label.pack()

                description_label = tk.Label(
                    self.root,
                    text="Double click on a user to update: ",
                    font=("Arial", 10),
                )
                description_label.pack()

                tree = ttk.Treeview(
                    self.root, columns=("Username", "Role"), show="headings"
                )
                tree.heading("Username", text="Username")
                tree.heading("Role", text="Role")
                tree.pack(padx=10, pady=10)
                tree.bind("<Double-1>", on_username_click)

                users = self.user_manager.get_users()
                for user in users:
                    if user.role == User.Role.CONSULTANT.value:
                        username = user.username
                        role = user.role
                        tree.insert("", "end", values=(username, role))

                # back button
                self.back_button = tk.Button(
                    self.root, text="Back", command=self.view_consultant
                )
                self.back_button.pack(pady=5)

        menu_options = [
            "List consultants",
            "Create consultant",
            "Update consultant",
            "Delete consultant",
        ]
        for i, option in enumerate(menu_options):
            button = tk.Button(
                self.root,
                text=option,
                width=50,
                command=lambda option=option: handle_option(option),
            )
            button.pack(pady=5)

        self.home_button = tk.Button(self.root, text="🏠", command=self.correct_menu())
        self.home_button.pack(pady=5)

    def view_members(self):
        self.clear_screen()

        title_label = tk.Label(
            self.root, text="Menu Options: ", font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)

        def handle_option(option):
            if option == "Create member":
                form = CreateMemberForm(self.root, App.config, self.view_members)
                form.show_form()

            elif option == "Delete member":
                delete_form = DeleteMemberForm(self.root, App.config, self.view_members)
                delete_form.show_form()

            elif option == "List members":
                self.clear_screen()
                tree = ttk.Treeview(
                    self.root, columns=("First Name", "Last Name"), show="headings"
                )
                tree.heading("First Name", text="First Name")
                tree.heading("Last Name", text="Last Name")
                tree.pack(padx=10, pady=10)

                members = self.member_manager.get_members()
                for member in members:
                    first_name = member.first_name
                    last_name = member.last_name
                    tree.insert("", "end", values=(first_name, last_name))
                tree.bind("<Double-1>")

                # back button
                self.back_button = tk.Button(
                    self.root, text="Back", command=self.view_members
                )
                self.back_button.pack(pady=5)

            elif option == "Update member":
                self.clear_screen()
                update_form = UpdateMemberForm(self.root, App.config, self.view_members)

                def on_member_click(event):
                    item = tree.selection()[0]
                    id = tree.item(item, "values")[0]
                    update_form.show_form(int(id))

                label = tk.Label(
                    self.root, text="Update Member", font=("Arial", 16, "bold")
                )
                label.pack()

                description_label = tk.Label(
                    self.root,
                    text="Double click on a member to update: ",
                    font=("Arial", 10),
                )
                description_label.pack()

                tree = ttk.Treeview(
                    self.root,
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

                # back button
                self.back_button = tk.Button(
                    self.root, text="Back", command=self.view_members
                )
                self.back_button.pack(pady=5)

            elif option == "Search members":

                def handle_search():
                    search_results = self.member_manager.search_members(
                        search_field.get()
                    )
                    self.clear_screen()
                    tree = ttk.Treeview(
                        self.root,
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
                        self.root, text="Back", command=self.view_members
                    )
                    self.back_button.pack(pady=5)

                self.clear_screen()
                search_field = tk.Entry(self.root, width=100)
                search_field.pack(pady=10)

                submit_button = tk.Button(
                    self.root, text="Search", command=handle_search
                )
                submit_button.pack(pady=10)

                # home button
                self.home_button = tk.Button(
                    self.root, text="🏠", command=self.correct_menu()
                )
                self.home_button.pack(pady=5)

        menu_options = [
            "List members",
            "Create member",
            "Update member",
            "Delete member",
            "Search members",
        ]
        for i, option in enumerate(menu_options):
            button = tk.Button(
                self.root,
                text=option,
                width=50,
                command=lambda option=option: handle_option(option),
            )
            button.pack(pady=5)

        self.home_button = tk.Button(self.root, text="🏠", command=self.correct_menu())
        self.home_button.pack(pady=5)

    def view_backups(self):
        self.clear_screen()
        title_label = tk.Label(
            self.root, text="Backup options: ", font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)

        self.backup_manager = Backups(App.config)

        def handle_option(option):
            if option == "Create backup":
                self.backup_manager.create()
                messagebox.showinfo("Backup Created", "Backup created successfully")
                self.view_backups()
            elif option == "Restore backup":
                self.clear_screen()
                backups = self.backup_manager.list()
                for i, backup in enumerate(backups):
                    button = tk.Button(
                        self.root,
                        text=backup,
                        width=50,
                        command=lambda backup=backup: self.backup_manager.restore(
                            backup
                        ),
                    )
                    button.pack(pady=5)

                # back button
                self.back_button = tk.Button(
                    self.root, text="Back", command=self.view_backups
                )
                self.back_button.pack(pady=5)

        menu_options = ["Create backup", "Restore backup"]
        for i, option in enumerate(menu_options):
            button = tk.Button(
                self.root,
                text=option,
                width=50,
                command=lambda option=option: handle_option(option),
            )
            button.pack(pady=5)

        self.home_button = tk.Button(self.root, text="🏠", command=self.correct_menu())
        self.home_button.pack(pady=5)

    #
    # Helper functions
    #
    def correct_menu(self):
        if self.user.role == User.Role.SUPER_ADMIN.value:
            return self.create_super_admin_screen
        elif self.user.role == User.Role.SYSTEM_ADMIN.value:
            return self.create_system_admin_screen
        elif self.user.role == User.Role.CONSULTANT.value:
            return self.create_consultant_screen
