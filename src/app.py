import tkinter as tk
from tkinter import ttk
from config import Config
from tkinter import messagebox
from entities.address import Address
from managers.address_manager import AddressManager
from managers.member_manager import MemberManager
from managers.profile_manager import ProfileManager
from managers.user_manager import UserManager
from backups import Backups

from authorization import *
from validations import *
from entities.user import User
from entities.member import Member
from app_logger import AppLogger


class App:
    config: Config
    logger = AppLogger("my_app.log")

    def __init__(self, root, config):
        self.root = root
        App.config = config
        App.logger.config = config

        self.user_manager = UserManager(App.config)
        self.address_manager = AddressManager(App.config)
        self.member_manager = MemberManager(App.config)
        self.profile_manager = ProfileManager(App.config)

        self.backup_manager = Backups(App.config)

        self.login_attempts = 0
        self.timeout = False
        self.init_db()

        self.root.title("Login")
        # set basic gui settings
        self.root.maxsize(1800, 1000)
        self.root.config(bg="RoyalBlue4")
        self.root.option_add("*Label*background", "RoyalBlue2")
        self.root.option_add("*Label*foreground", "white")

        self.user = None
        self.view_login_screen()

    def run(self):
        self.root.mainloop()

    def init_db(self):
        self.user_manager.initialize()
        self.user_manager.create_super_admin()
        self.address_manager.initialize()
        self.member_manager.initialize()
        self.profile_manager.initialize()

        self.user_manager.seed_test_users()
        self.member_manager.seed_members()
        self.address_manager.seed_addresses()
        self.profile_manager.seed_profiles()

    def start_timeout(self):
        self.timeout = True
        messagebox.showwarning("Warning", "Too many attempts. Please wait 2 minutes.")
        # Disable the login button during the timeout period
        self.login_button.config(state=tk.DISABLED)
        self.root.after(120000, self.end_timeout)

    def end_timeout(self):
        self.timeout = False
        self.login_button.config(state=tk.NORMAL)
        self.login_attempts = 0

    # ======================================== #
    # Views
    # ======================================== #

    # Login
    def view_login_screen(self):
        self.clear_screen()
        title_label = tk.Label(self.root, text="Login", font=("Arial", 16, "bold"), bg="RoyalBlue4")
        title_label.pack(pady=(20, 10))

        un = tk.StringVar(value="super_admin")
        pw = tk.StringVar(value="Admin_123?")

        # un = tk.StringVar(value="sarahm78")
        # pw = tk.StringVar(value="Pa$$w0rd1234")

        self.username_label = tk.Label(self.root, text="Username", bg="RoyalBlue4")
        self.username_label.pack(pady=10, padx=100)
        self.username_entry = tk.Entry(self.root, width=50, textvariable=un)
        self.username_entry.pack(pady=10, padx=100)

        self.password_label = tk.Label(self.root, text="Password", bg="RoyalBlue4")
        self.password_label.pack(pady=10, padx=100)
        self.password_entry = tk.Entry(self.root, show="*", width=50, textvariable=pw)
        self.password_entry.pack(pady=10, padx=100)

        self.login_button = tk.Button(self.root, text="Login", command=self.login)
        self.login_button.pack(pady=20, padx=100)

    # Logs
    @authorized(allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN))
    def view_logs(self):
        self.create_view(self.user.role, "Logs")

        title_label = tk.Label(
            self.right_frame,
            text="Manage logs",
            font=("Arial", 16, "bold"),
            fg="white",
        )
        title_label.pack(pady=10)

        @authorized_action(self, allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN))
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
            self.back_button = tk.Button(self.right_frame, text="Back", command=self.view_logs)
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
            r_id = len(logs) - id

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

        tree.column("No", width=50)
        tree.column("Datetime", width=140)
        tree.column("Level", width=65)
        tree.column("Description", width=700)

    # Users (& Consultants)
    @authorized(allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN))
    def view_users(self):
        self.create_view(self.user.role, "Users")

        title_label = tk.Label(
            self.right_frame,
            text="Manage users",
            font=("Arial", 16, "bold"),
            fg="white",
        )
        title_label.pack(pady=10)

        @authorized_action(self, allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN))
        def on_username_click(event):
            item = tree.selection()[0]
            selected_user_username = tree.item(item, "values")[0]
            selected_user_role = tree.item(item, "values")[1]
            if self.user.role == User.Role.SUPER_ADMIN.value:
                return self.view_user_update(selected_user_username)
            elif self.user.role == User.Role.SYSTEM_ADMIN.value and selected_user_role == User.Role.CONSULTANT.value:
                return self.view_consultant_update(selected_user_username)
            else:
                return

        description_label = tk.Label(
            self.right_frame,
            text="On this page users can be managed. Double click on a user to edit.",
            font=("Arial", 12),
        )
        description_label.pack()

        button = tk.Button(
            self.right_frame,
            text="Add new",
            width=10,
            command=lambda: (
                self.view_user_create()
                if self.user.role == User.Role.SUPER_ADMIN.value
                else self.view_consultant_create()
            ),
        )
        button.pack(side="top", anchor="w", pady=(20, 0), padx=10)

        tree = ttk.Treeview(self.right_frame, columns=("Username", "Role"), show="headings")
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

    @authorized(allowed_roles=(User.Role.SUPER_ADMIN,))
    def view_user_create(self):
        self.create_view(self.user.role, "Users")

        @authorized_action(self, allowed_roles=(User.Role.SUPER_ADMIN,))
        def submit():
            username = username_entry.get()
            password = password_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            role = role_combobox.get()

            try:
                errors = []
                if not validate_username(username):
                    errors.append("Username is not valid.")

                if not validate_password(password):
                    errors.append("Password is not valid.")

                if not validate_name(first_name):
                    errors.append("First name has to be between 2 and 20 characters.")

                if not validate_name(last_name):
                    errors.append("Last name has to be between 2 and 20 characters.")

                if not validate_server_input(role, choosable_roles):
                    errors.append("Role is not valid, incident will be logged.")
                    App.logger.log_activity(
                        self.user,
                        "Server-side input is modified.",
                        f"Role was not valid: {role}",
                        True,
                    )

                if not self.user_manager.is_available_username(username):
                    errors.append("Username is already taken.")

                if len(errors) == 0:
                    user = self.user_manager.create_user(username, password, role)
                    App.logger.log_activity(
                        self.user,
                        "created user",
                        f"with username: {user.username}",
                        False,
                    )

                    if user is not None:
                        profile = self.profile_manager.create_profile(first_name, last_name, user.id)
                        if profile is not None:
                            messagebox.showinfo("Information", f"User has been created.")
                            self.view_users()
                else:
                    messages = "\n".join(errors)
                    messagebox.showinfo("Information", messages)
            except Exception as e:
                print(e)
                messagebox.showerror("Error", "Something went wrong.")

        # Create a title label
        title_label = tk.Label(self.right_frame, text="Add new User", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # username
        username_label = tk.Label(self.right_frame, text="Please enter the new username", font=("Arial", 12))
        username_label.pack(pady=5, padx=25)
        username_entry = tk.Entry(self.right_frame, width=50)
        username_entry.pack(pady=5, padx=25)

        # password
        password_label = tk.Label(self.right_frame, text="Please enter the new password", font=("Arial", 12))
        password_label.pack(pady=5, padx=25)
        password_entry = tk.Entry(self.right_frame, show="*", width=50)
        password_entry.pack(pady=5, padx=25)

        # first name
        first_name_label = tk.Label(self.right_frame, text="Please enter the first name", font=("Arial", 12))
        first_name_label.pack(pady=5, padx=25)
        first_name_entry = tk.Entry(self.right_frame, width=50)
        first_name_entry.pack(pady=5, padx=25)

        # last name
        last_name_label = tk.Label(self.right_frame, text="Please enter the last name", font=("Arial", 12))
        last_name_label.pack(pady=5, padx=25)
        last_name_entry = tk.Entry(self.right_frame, width=50)
        last_name_entry.pack(pady=5, padx=25)

        # role
        choosable_roles = (User.Role.SYSTEM_ADMIN.value, User.Role.CONSULTANT.value)
        role_label = tk.Label(self.right_frame, text="Role", font=("Arial", 12))
        role_label.pack(pady=5, padx=25)
        role_combobox = ttk.Combobox(self.right_frame, values=choosable_roles)
        role_combobox.set(choosable_roles[0])
        role_combobox.pack(pady=5, padx=25)

        # submit button
        submit_button = tk.Button(self.right_frame, text="Save", command=submit)
        submit_button.pack(pady=20)

        # back button
        back_button = tk.Button(self.right_frame, text="Cancel", command=self.view_users)
        back_button.pack(pady=20)

    @authorized(allowed_roles=(User.Role.SUPER_ADMIN,))
    def view_user_update(self, username):
        self.create_view(self.user.role, "Users")

        @authorized_action(self, allowed_roles=(User.Role.SUPER_ADMIN,))
        def submit():
            current_username = current_username_entry.get()
            new_first_name = first_name_entry.get()
            new_last_name = last_name_entry.get()
            role = role_combobox.get()

            try:
                user_to_update = self.user_manager.get_user(current_username)
                if user_to_update is not None:
                    errors = []
                    if not validate_name(new_first_name):
                        errors.append("First name has to be between 2 and 20 characters.")

                    if not validate_name(new_last_name):
                        errors.append("Last name has to be between 2 and 20 characters.")

                    if not validate_server_input(role, choosable_roles):
                        errors.append("Role is not valid, incident will be logged.")
                        App.logger.log_activity(
                            self.user,
                            "Server-side input is modified.",
                            f"Role was not valid: {role}",
                            True,
                        )

                    if len(errors) == 0:
                        self.user_manager.update_user(user_to_update, current_username, role)
                        updated_user = self.user_manager.get_user(current_username)
                        if updated_user is not None:
                            profile_to_update = self.profile_manager.get_profile(user_to_update.id)
                            updated_profile = self.profile_manager.update_profile(
                                profile_to_update, new_first_name, new_last_name
                            )
                            if updated_profile is not None:
                                messagebox.showinfo("Information", "User has been updated successfully.")
                                App.logger.log_activity(
                                    self.user,
                                    "updated user",
                                    f"with username: {updated_user.username}",
                                    False,
                                )
                                self.view_users()
                        else:
                            messagebox.showerror("Error", "Failed to retrieve updated user.")
                    else:
                        messages = "\n".join(errors)
                        messagebox.showerror("Information", messages)
                else:
                    messagebox.showerror("Error", "User not found.")
            except Exception as e:
                print(e)
                messagebox.showerror("Error", f"Something went wrong.")

        @authorized_action(self, allowed_roles=(User.Role.SUPER_ADMIN,))
        def delete():
            current_username = current_username_entry.get()
            user = self.user_manager.get_user(current_username)
            self.user_manager.delete_user(user)
            messagebox.showinfo("Information", "User has been deleted.")

            App.logger.log_activity(self.user, "deleted user", f"with username: {user.username}", False)
            self.view_users()

        # Get user and profile
        updated_user = self.user_manager.get_user(username)
        updated_profile = self.profile_manager.get_profile(updated_user.id)

        # Create a title label
        title_label = tk.Label(self.right_frame, text=f"Update User", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # username
        current_username_label = tk.Label(self.right_frame, text="Current Username", font=("Arial", 12))
        current_username_label.pack(pady=5, padx=25)
        current_username_entry = tk.Entry(self.right_frame, width=50)
        current_username_entry.insert(0, updated_user.username)
        current_username_entry.config(state="readonly")
        current_username_entry.pack(pady=5, padx=25)

        # first name
        first_name_label = tk.Label(self.right_frame, text="Please enter the first name", font=("Arial", 12))
        first_name_label.pack(pady=5, padx=25)
        first_name_entry = tk.Entry(self.right_frame, width=50)
        first_name_entry.insert(0, updated_profile.first_name)
        first_name_entry.pack(pady=5, padx=25)

        # last name
        last_name_label = tk.Label(self.right_frame, text="Please enter the last name", font=("Arial", 12))
        last_name_label.pack(pady=5, padx=25)
        last_name_entry = tk.Entry(self.right_frame, width=50)
        last_name_entry.insert(0, updated_profile.last_name)
        last_name_entry.pack(pady=5, padx=25)

        # role
        choosable_roles = (User.Role.SYSTEM_ADMIN.value, User.Role.CONSULTANT.value)
        role_label = tk.Label(self.right_frame, text="Role", font=("Arial", 12))
        role_label.pack(pady=5, padx=25)
        role_combobox = ttk.Combobox(self.right_frame, values=choosable_roles)
        role_combobox.set(updated_user.role)
        role_combobox.pack(pady=5, padx=25)

        # reset password button
        reset_password_button = tk.Button(
            self.right_frame,
            text="Reset Password",
            command=lambda: self.view_password_reset(updated_user.username),
        )
        reset_password_button.pack(pady=5)

        # submit button
        submit_button = tk.Button(self.right_frame, text="Save", command=submit)
        submit_button.pack(pady=5)

        # delete button
        delete_button = tk.Button(
            self.right_frame,
            text="Delete",
            command=delete,
            fg="red",
            font=("Arial", 12, "bold"),
        )
        delete_button.pack(pady=5)

        # back button
        back_button = tk.Button(self.right_frame, text="Cancel", command=self.view_users)
        back_button.pack(pady=5)

    @authorized(allowed_roles=(User.Role.SYSTEM_ADMIN,))
    def view_consultant_create(self):
        self.create_view(self.user.role, "Users")

        @authorized_action(self, allowed_roles=(User.Role.SYSTEM_ADMIN,))
        def submit():
            username = username_entry.get()
            password = password_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()

            try:
                errors = []
                if not validate_username(username):
                    errors.append("Username is not valid.")

                if not validate_password(password):
                    errors.append("Password is not valid.")

                if not validate_name(first_name):
                    errors.append("First name has to be between 2 and 20 characters.")

                if not validate_name(last_name):
                    errors.append("Last name has to be between 2 and 20 characters.")

                if not self.user_manager.is_available_username(username):
                    errors.append("Username is already taken.")

                if len(errors) == 0:
                    user = self.user_manager.create_user(username, password, User.Role.CONSULTANT.value)
                    App.logger.log_activity(
                        self.user,
                        "created user",
                        f"with username: {user.username}",
                        False,
                    )

                    if user is not None:
                        profile = self.profile_manager.create_profile(first_name, last_name, user.id)
                        if profile is not None:
                            messagebox.showinfo("Information", f"User has been created.")
                            self.view_users()
                else:
                    messages = "\n".join(errors)
                    messagebox.showinfo("Information", messages)
            except Exception as e:
                print(e)
                messagebox.showerror("Error", "Something went wrong.")

        # Create a title label
        title_label = tk.Label(self.right_frame, text="Add new Consultant", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # username
        username_label = tk.Label(self.right_frame, text="Please enter the new username", font=("Arial", 12))
        username_label.pack(pady=5, padx=25)
        username_entry = tk.Entry(self.right_frame, width=50)
        username_entry.pack(pady=5, padx=25)

        # password
        password_label = tk.Label(self.right_frame, text="Please enter the new password", font=("Arial", 12))
        password_label.pack(pady=5, padx=25)
        password_entry = tk.Entry(self.right_frame, show="*", width=50)
        password_entry.pack(pady=5, padx=25)

        # first name
        first_name_label = tk.Label(self.right_frame, text="Please enter the first name", font=("Arial", 12))
        first_name_label.pack(pady=5, padx=25)
        first_name_entry = tk.Entry(self.right_frame, width=50)
        first_name_entry.pack(pady=5, padx=25)

        # last name
        last_name_label = tk.Label(self.right_frame, text="Please enter the last name", font=("Arial", 12))
        last_name_label.pack(pady=5, padx=25)
        last_name_entry = tk.Entry(self.right_frame, width=50)
        last_name_entry.pack(pady=5, padx=25)

        # submit button
        submit_button = tk.Button(self.right_frame, text="Save", command=submit)
        submit_button.pack(pady=20)

        # back button
        back_button = tk.Button(self.right_frame, text="Cancel", command=self.view_users)
        back_button.pack(pady=20)

    @authorized(allowed_roles=(User.Role.SYSTEM_ADMIN,))
    def view_consultant_update(self, username):
        self.create_view(self.user.role, "Users")

        @authorized_action(self, allowed_roles=(User.Role.SYSTEM_ADMIN,))
        def submit():
            current_username = current_username_entry.get()
            new_first_name = first_name_entry.get()
            new_last_name = last_name_entry.get()

            try:
                user_to_update = self.user_manager.get_user(current_username)
                if user_to_update is not None:
                    errors = []
                    if not validate_name(new_first_name):
                        errors.append("First name has to be between 2 and 20 characters.")

                    if not validate_name(new_last_name):
                        errors.append("Last name has to be between 2 and 20 characters.")

                    if len(errors) == 0:
                        self.user_manager.update_user(user_to_update, current_username, User.Role.CONSULTANT.value)
                        updated_user = self.user_manager.get_user(current_username)
                        if updated_user is not None:
                            profile_to_update = self.profile_manager.get_profile(user_to_update.id)
                            updated_profile = self.profile_manager.update_profile(
                                profile_to_update, new_first_name, new_last_name
                            )
                            if updated_profile is not None:
                                messagebox.showinfo("Information", "User has been updated successfully.")
                                App.logger.log_activity(
                                    self.user,
                                    "updated user",
                                    f"with username: {updated_user.username}",
                                    False,
                                )
                                self.view_users()
                        else:
                            messagebox.showerror("Error", "Failed to retrieve updated user.")

                    else:
                        messages = "\n".join(errors)
                        messagebox.showerror("Information", messages)
                else:
                    messagebox.showerror("Error", "User not found.")
            except Exception as e:
                print(e)
                messagebox.showerror("Error", "Something went wrong.")

        @authorized_action(self, allowed_roles=(User.Role.SYSTEM_ADMIN,))
        def delete():
            current_username = current_username_entry.get()
            user = self.user_manager.get_user(current_username)
            self.user_manager.delete_user(user)
            messagebox.showinfo("Information", "User has been deleted.")

            App.logger.log_activity(self.user, "deleted user", f"with username: {user.username}", False)
            self.view_users()

        # Get user and profile
        updated_user = self.user_manager.get_user(username)
        updated_profile = self.profile_manager.get_profile(updated_user.id)

        # Create a title label
        title_label = tk.Label(self.right_frame, text=f"Update Consultant", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # username
        current_username_label = tk.Label(self.right_frame, text="Current Username", font=("Arial", 12))
        current_username_label.pack(pady=5, padx=25)
        current_username_entry = tk.Entry(self.right_frame, width=50)
        current_username_entry.insert(0, updated_user.username)
        current_username_entry.config(state="readonly")
        current_username_entry.pack(pady=5, padx=25)

        # first name
        first_name_label = tk.Label(self.right_frame, text="Please enter the first name", font=("Arial", 12))
        first_name_label.pack(pady=5, padx=25)
        first_name_entry = tk.Entry(self.right_frame, width=50)
        first_name_entry.insert(0, updated_profile.first_name)
        first_name_entry.pack(pady=5, padx=25)

        # last name
        last_name_label = tk.Label(self.right_frame, text="Please enter the last name", font=("Arial", 12))
        last_name_label.pack(pady=5, padx=25)
        last_name_entry = tk.Entry(self.right_frame, width=50)
        last_name_entry.insert(0, updated_profile.last_name)
        last_name_entry.pack(pady=5, padx=25)

        # reset password button
        reset_password_button = tk.Button(
            self.right_frame,
            text="Reset Password",
            command=lambda: self.view_password_reset(updated_user.username),
        )
        reset_password_button.pack(pady=5)

        # submit button
        submit_button = tk.Button(self.right_frame, text="Save", command=submit)
        submit_button.pack(pady=5)

        # delete button
        delete_button = tk.Button(
            self.right_frame,
            text="Delete",
            command=delete,
            fg="red",
            font=("Arial", 12, "bold"),
        )
        delete_button.pack(pady=5)

        # back button
        back_button = tk.Button(self.right_frame, text="Cancel", command=self.view_users)
        back_button.pack(pady=5)

    # Members
    @authorized(allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN, User.Role.CONSULTANT))
    def view_members(self):
        self.create_view(self.user.role, "Members")

        title_label = tk.Label(self.right_frame, text="Manage members", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        description_label = tk.Label(
            self.right_frame,
            text="On this page members can be managed. Double click on a member to edit.",
            font=("Arial", 12),
        )
        description_label.pack()

        button = tk.Button(
            self.right_frame,
            text="Add new",
            width=10,
            command=lambda: self.view_member_create(),
        )
        button.pack(side="top", anchor="w", pady=(20, 0), padx=10)

        button = tk.Button(
            self.right_frame,
            text="🔍",
            width=10,
            command=lambda: self.view_members_search(),
        )
        button.pack(side="right", anchor="w", pady=(20, 0), padx=10)

        def on_member_click(event):
            authorized(
                allowed_roles=(
                    User.Role.SUPER_ADMIN,
                    User.Role.SYSTEM_ADMIN,
                    User.Role.CONSULTANT,
                )
            )
            item = tree.selection()[0]
            id = tree.item(item, "values")[0]
            self.view_member_update(int(id))

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

    @authorized(allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN, User.Role.CONSULTANT))
    def view_members_search(self):
        self.create_view(self.user.role, "Members")

        title_label = tk.Label(self.right_frame, text="Search members", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        search_field = tk.Entry(self.right_frame, width=50)
        search_field.pack(pady=10, padx=25)

        @authorized_action(self, allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN, User.Role.CONSULTANT))
        def handle_search():
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
            self.back_button = tk.Button(self.right_frame, text="Back", command=self.view_members)
            self.back_button.pack(pady=5)

        search_button = tk.Button(self.right_frame, text="Search", command=handle_search)
        search_button.pack(pady=5, padx=20)

    @authorized(allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN, User.Role.CONSULTANT))
    def view_member_create(self):
        self.create_view(self.user.role, "Members")

        @authorized_action(self, allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN, User.Role.CONSULTANT))
        def submit():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            age = age_entry.get()
            gender = genders_option.get()
            weight = weight_entry.get()
            email = email_entry.get()
            phone_number = phone_number_entry.get()
            street = street_entry.get()
            house_number = house_number_entry.get()
            zip_code = zip_code_entry.get()
            city = city_option.get()

            try:
                errors = []
                if not validate_name(first_name):
                    errors.append("First name has to be between 2 and 20 characters.")

                if not validate_name(last_name):
                    errors.append("Last name has to be between 2 and 20 characters.")

                if not validate_age(age):
                    errors.append("Age has to be between 1 and 100.")

                if not validate_weight(weight):
                    errors.append("Weight has to be between 1 and 200.")

                if not validate_email(email):
                    errors.append("Email is not valid.")

                if not validate_phone_number(phone_number):
                    errors.append("Phone number is not valid.")

                if not validate_street_name(street):
                    errors.append("Street name has to be between 2 and 30 characters.")

                if not validate_house_number(house_number):
                    errors.append("House number has to be between 1 and 9999.")

                if not validate_zip_code(zip_code):
                    errors.append("Zip code is not valid.")

                if not validate_server_input(gender, gender_options):
                    errors.append("Gender is not valid, incident will be reported.")
                    App.logger.log_activity(
                        self.user,
                        "Server-side input is modified.",
                        f"Gender was not valid: {gender}",
                        True,
                    )

                if not validate_server_input(city, city_options):
                    errors.append("City is not valid, incident will be reported.")
                    App.logger.log_activity(
                        self.user,
                        "Server-side input is modified.",
                        f"City was not valid: {city}",
                        True,
                    )

                if len(errors) == 0:
                    member = self.member_manager.create_member(
                        first_name, last_name, age, gender, weight, email, phone_number
                    )
                    if member is not None:
                        address = self.address_manager.create_address(street, house_number, zip_code, city, member.id)
                        if address is not None:
                            messagebox.showinfo("Information", "Member has been created.")
                            App.logger.log_activity(
                                self.user,
                                "created member",
                                f"with id: {member.id}",
                                False,
                            )
                            self.view_members()
                else:
                    messages = "\n".join(errors)
                    messagebox.showinfo("Information", messages)
            except Exception as e:
                print(e)
                messagebox.showerror("Error", "Something went wrong.")

        # Create a title label
        title_label = tk.Label(self.right_frame, text="Create new member", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # first name
        first_name_label = tk.Label(self.right_frame, text="Please enter the first name", font=("Arial", 12))
        first_name_label.pack(pady=5, padx=25)
        first_name_entry = tk.Entry(self.right_frame, width=50)
        first_name_entry.pack(pady=5, padx=25)

        # last name
        last_name_label = tk.Label(self.right_frame, text="Please enter the last name", font=("Arial", 12))
        last_name_label.pack(pady=5, padx=25)
        last_name_entry = tk.Entry(self.right_frame, width=50)
        last_name_entry.pack(pady=5, padx=25)

        # age
        age_label = tk.Label(self.right_frame, text="Please enter the age", font=("Arial", 12))
        age_label.pack(pady=5, padx=25)
        age_entry = tk.Entry(self.right_frame, width=50)
        age_entry.pack(pady=5, padx=25)

        # gender
        gender_label = tk.Label(self.right_frame, text="Select a gender:", width=100, font=("Arial", 12))
        gender_label.pack(pady=10)
        gender_options = [Member.Gender.MALE.value, Member.Gender.FEMALE.value]
        genders_option = ttk.Combobox(self.right_frame, values=gender_options)
        genders_option.pack()

        # weight
        weight_label = tk.Label(self.right_frame, text="Please enter the weight", font=("Arial", 12))
        weight_label.pack(pady=5, padx=25)
        weight_entry = tk.Entry(self.right_frame, width=50)
        weight_entry.pack(pady=5, padx=25)

        # email
        email_label = tk.Label(self.right_frame, text="Please enter the email", font=("Arial", 12))
        email_label.pack(pady=5, padx=25)
        email_entry = tk.Entry(self.right_frame, width=50)
        email_entry.pack(pady=5, padx=25)

        # phone number
        phone_number_label = tk.Label(self.right_frame, text="Please enter the phone number", font=("Arial", 12))
        phone_number_label.pack(pady=5, padx=25)
        phone_number_entry = tk.Entry(self.right_frame, width=50)
        phone_number_entry.pack(pady=5, padx=25)

        # DIVIDER
        divider = tk.Label(self.right_frame, text="---------------------------------")
        divider.pack(pady=5, padx=25)

        # address: street
        street_label = tk.Label(self.right_frame, text="Please enter the street", font=("Arial", 12))
        street_label.pack(pady=5, padx=25)
        street_entry = tk.Entry(self.right_frame, width=50)
        street_entry.pack(pady=5, padx=25)

        # address: house number
        house_number_label = tk.Label(self.right_frame, text="Please enter the house number", font=("Arial", 12))
        house_number_label.pack(pady=5, padx=25)
        house_number_entry = tk.Entry(self.right_frame, width=50)
        house_number_entry.pack(pady=5, padx=25)

        # address: zip code
        zip_code_label = tk.Label(self.right_frame, text="Please enter the zip code", font=("Arial", 12))
        zip_code_label.pack(pady=5, padx=25)
        zip_code_entry = tk.Entry(self.right_frame, width=50)
        zip_code_entry.pack(pady=5, padx=25)

        # address: city
        city_label = tk.Label(self.right_frame, text="Select a city:", width=100, font=("Arial", 12))
        city_label.pack(pady=10)
        city_options = [city.value for city in Address.City]
        city_option = ttk.Combobox(self.right_frame, values=city_options)
        city_option.pack()

        # submit button
        submit_button = tk.Button(self.right_frame, text="Submit", command=submit)
        submit_button.pack(pady=20)

        # back button
        back_button = tk.Button(self.right_frame, text="Cancel", command=self.view_members)
        back_button.pack(pady=20)

    @authorized(allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN, User.Role.CONSULTANT))
    def view_member_update(self, member_id):
        self.create_view(self.user.role, "Members")

        @authorized_action(self, allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN, User.Role.CONSULTANT))
        def submit():
            updated_first_name = updated_first_name_entry.get()
            updated_last_name = updated_last_name_entry.get()
            updated_age = updated_age_entry.get()
            updated_gender = genders_option.get()
            updated_weight = updated_weight_entry.get()
            updated_email = updated_email_entry.get()
            updated_phone_number = updated_phone_number_entry.get()
            updated_street = street_entry.get()
            updated_house_number = house_number_entry.get()
            updated_zip_code = zip_code_entry.get()
            updated_city = city_option.get()

            try:
                errors = []
                if not validate_name(updated_first_name):
                    errors.append("First name has to be between 2 and 20 characters.")

                if not validate_name(updated_last_name):
                    errors.append("Last name has to be between 2 and 20 characters.")

                if not validate_age(updated_age):
                    errors.append("Age has to be between 1 and 100.")

                if not validate_weight(updated_weight):
                    errors.append("Weight has to be between 1 and 200.")

                if not validate_email(updated_email):
                    errors.append("Email is not valid.")

                if not validate_phone_number(updated_phone_number):
                    errors.append("Phone number is not valid.")

                if not validate_street_name(updated_street):
                    errors.append("Street name has to be between 2 and 30 characters.")

                if not validate_house_number(updated_house_number):
                    errors.append("House number has to be between 1 and 9999.")

                if not validate_zip_code(updated_zip_code):
                    errors.append("Zip code is not valid.")

                if not validate_server_input(updated_gender, gender_options):
                    errors.append("Gender is not valid, incident will be reported.")
                    App.logger.log_activity(
                        self.user,
                        "Server-side input is modified.",
                        f"Gender was not valid: {updated_gender}",
                        True,
                    )

                if not validate_server_input(updated_city, city_options):
                    errors.append("City is not valid, incident will be reported.")
                    App.logger.log_activity(
                        self.user,
                        "Server-side input is modified.",
                        f"City was not valid: {updated_city}",
                        True,
                    )

                if len(errors) == 0:
                    member_to_update = member_to_update
                    self.member_manager.update_member(
                        member_to_update,
                        updated_first_name,
                        updated_last_name,
                        updated_age,
                        updated_gender,
                        updated_weight,
                        updated_email,
                        updated_phone_number,
                    )
                    updated_member = self.member_manager.get_member(member_to_update.id)
                    if updated_member is not None:
                        address_to_update = address_to_update
                        self.address_manager.update_address(
                            address_to_update,
                            updated_street,
                            updated_house_number,
                            updated_zip_code,
                            updated_city,
                            member_to_update.id,
                        )
                        updated_address = self.address_manager.get_address(member_to_update.id)
                        if updated_address is not None:
                            messagebox.showinfo("Information", "Member has been updated successfully.")
                            App.logger.log_activity(
                                self.user,
                                "updated member",
                                f"with id: {updated_member.id}",
                                False,
                            )
                            self.view_members()
                        else:
                            messagebox.showerror("Error", "Failed to retrieve updated address.")
                    else:
                        messagebox.showerror("Error", "Failed to retrieve updated member.")
                else:
                    messages = "\n".join(errors)
                    messagebox.showinfo("Information", messages)
            except Exception as e:
                print(e)
                messagebox.showerror("Error", "Something went wrong.")

        @authorized_action(self, allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN, User.Role.CONSULTANT))
        def delete():
            member = self.member_manager.get_member(member_to_update.id)
            self.member_manager.delete_member(member)
            messagebox.showinfo("Information", "Member has been deleted.")
            App.logger.log_activity(self.user, "deleted member", f"with id: {member.id}", False)
            self.view_members()

        title_label = tk.Label(self.right_frame, text="Update member", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        member_to_update = updated_member = self.member_manager.get_member(member_id)
        address_to_update = updated_address = self.address_manager.get_address(member_id)

        # first name
        updated_first_name_label = tk.Label(self.right_frame, text="First Name", font=("Arial", 12))
        updated_first_name_label.pack(pady=5, padx=25)
        updated_first_name_entry = tk.Entry(self.right_frame, width=50)
        updated_first_name_entry.insert(0, updated_member.first_name)
        updated_first_name_entry.pack(pady=5, padx=25)

        # last name
        updated_last_name_label = tk.Label(self.right_frame, text="Last Name", font=("Arial", 12))
        updated_last_name_label.pack(pady=5, padx=25)
        updated_last_name_entry = tk.Entry(self.right_frame, width=50)
        updated_last_name_entry.insert(0, updated_member.last_name)
        updated_last_name_entry.pack(pady=5, padx=25)

        # age
        updated_age_label = tk.Label(self.right_frame, text="New Age", font=("Arial", 12))
        updated_age_label.pack(pady=5, padx=25)
        updated_age_entry = tk.Entry(self.right_frame, width=50)
        updated_age_entry.insert(0, updated_member.age)
        updated_age_entry.pack(pady=5, padx=25)

        # gender
        gender_label = tk.Label(self.right_frame, text="Select a gender:", width=100, font=("Arial", 12))
        gender_label.pack(pady=10)
        gender_options = (Member.Gender.MALE.value, Member.Gender.FEMALE.value)
        genders_option = ttk.Combobox(self.right_frame, values=gender_options)
        genders_option.insert(0, updated_member.gender)
        genders_option.pack()

        # weight
        updated_weight_label = tk.Label(self.right_frame, text="New Weight", font=("Arial", 12))
        updated_weight_label.pack(pady=5, padx=25)
        updated_weight_entry = tk.Entry(self.right_frame, width=50)
        updated_weight_entry.insert(0, updated_member.weight)
        updated_weight_entry.pack(pady=5, padx=25)

        # email
        updated_email_label = tk.Label(self.right_frame, text="New Email", font=("Arial", 12))
        updated_email_label.pack(pady=5, padx=25)
        updated_email_entry = tk.Entry(self.right_frame, width=50)
        updated_email_entry.insert(0, updated_member.email)
        updated_email_entry.pack(pady=5, padx=25)

        # phone number
        updated_phone_number_label = tk.Label(self.right_frame, text="New Phone Number", font=("Arial", 12))
        updated_phone_number_label.pack(pady=5, padx=25)
        updated_phone_number_entry = tk.Entry(self.right_frame, width=50)
        updated_phone_number_entry.insert(0, updated_member.phone_number)
        updated_phone_number_entry.pack(pady=5, padx=25)

        # DIVIDER
        divider = tk.Label(self.right_frame, text="---------------------------------")
        divider.pack(pady=5, padx=25)

        # address: street
        street_label = tk.Label(self.right_frame, text="Please enter the street", font=("Arial", 12))
        street_label.pack(pady=5, padx=25)
        street_entry = tk.Entry(self.right_frame, width=50)
        street_entry.pack(pady=5, padx=25)
        street_entry.insert(0, updated_address.street_name)

        # address: house number
        house_number_label = tk.Label(self.right_frame, text="Please enter the house number", font=("Arial", 12))
        house_number_label.pack(pady=5, padx=25)
        house_number_entry = tk.Entry(self.right_frame, width=50)
        house_number_entry.pack(pady=5, padx=25)
        house_number_entry.insert(0, updated_address.house_number)

        # address: zip code
        zip_code_label = tk.Label(self.right_frame, text="Please enter the zip code", font=("Arial", 12))
        zip_code_label.pack(pady=5, padx=25)
        zip_code_entry = tk.Entry(self.right_frame, width=50)
        zip_code_entry.pack(pady=5, padx=25)
        zip_code_entry.insert(0, updated_address.zip_code)

        # address: city
        city_label = tk.Label(self.right_frame, text="Select a city:", width=100, font=("Arial", 12))
        city_label.pack(pady=10)
        city_options = (city.value for city in Address.City)
        city_option = ttk.Combobox(self.right_frame, values=city_options)
        city_option.pack()
        city_option.insert(0, updated_address.city)

        # submit button
        submit_button = tk.Button(self.right_frame, text="Submit", command=submit)
        submit_button.pack(pady=10)

        # delete button
        delete_button = tk.Button(
            self.right_frame,
            text="Delete",
            command=delete,
            fg="red",
            font=("Arial", 12, "bold"),
        )
        delete_button.pack(pady=5)

        # back button
        back_button = tk.Button(self.right_frame, text="Cancel", command=self.view_members)
        back_button.pack(pady=5)

    # Password reset
    @authorized(allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN))
    def view_password_reset(self, username):
        self.create_view(self.user.role, "Users")

        @authorized_action(self, allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN))
        def submit():
            try:
                reseted_user = self.user_manager.get_user(current_username_entry.get())
                password = password_entry.get()

                if (self.user.role == User.Role.SUPER_ADMIN.value) or (
                    self.user.role == User.Role.SYSTEM_ADMIN.value and reseted_user.role == User.Role.CONSULTANT.value
                ):
                    if validate_password(password):
                        self.user_manager.reset_password(reseted_user, password)
                        messagebox.showinfo("Information", "User temporary password has been set.")
                        self.user_manager.reset_password_status(reseted_user, True)
                        App.logger.log_activity(
                            self.user,
                            "reset password of user",
                            f"with username: {reseted_user.username}",
                            False,
                        )
                        self.view_users()
                    else:
                        messagebox.showinfo("Information", "Please try Again")
            except Exception as e:
                print(e)
                messagebox.showerror("Error", "Something went wrong.")

        title_label = tk.Label(self.right_frame, text="Reset Password", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        current_username_label = tk.Label(self.right_frame, text="Current Username", font=("Arial", 12))
        current_username_label.pack(pady=5, padx=25)
        current_username_entry = tk.Entry(self.right_frame, width=50)
        current_username_entry.insert(0, username)
        current_username_entry.config(state="readonly")
        current_username_entry.pack(pady=5, padx=25)

        password_label = tk.Label(self.right_frame, text="Enter new password", font=("Arial", 12))
        password_label.pack(pady=5, padx=25)

        password_entry = tk.Entry(self.right_frame, show="*", width=50)
        password_entry.pack(pady=5, padx=25)

        submit_button = tk.Button(self.right_frame, text="Reset Password", command=submit)
        submit_button.pack(pady=20)

    @authorized(
        allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN, User.Role.CONSULTANT),
        without_password_reset=True,
    )
    def view_my_password_reset(self):
        self.create_view(self.user.role, "Reset my password")

        @authorized_action(
            self,
            allowed_roles=(
                User.Role.SUPER_ADMIN,
                User.Role.SYSTEM_ADMIN,
                User.Role.CONSULTANT,
            ),
            without_password_reset=True,
        )
        def submit():
            try:
                reseted_user = self.user_manager.get_user(current_username_entry.get())
                password = password_entry.get()

                if validate_password(password):
                    self.user_manager.reset_password(reseted_user, password)
                    messagebox.showinfo("Information", "User password has been set.")
                    self.user_manager.reset_password_status(reseted_user)
                    App.logger.log_activity(
                        self.user,
                        "reset their own password",
                        f"with role: {reseted_user.role}",
                        False,
                    )
                    self.logout()
                else:
                    messagebox.showinfo("Information", "Please try Again")
            except Exception as e:
                print(e)
                messagebox.showerror("Error", "Something went wrong.")

        title_label = tk.Label(self.right_frame, text="Reset Password", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        current_username_label = tk.Label(self.right_frame, text="Current Username", font=("Arial", 12))
        current_username_label.pack(pady=5, padx=25)
        current_username_entry = tk.Entry(self.right_frame, width=50)
        current_username_entry.insert(0, self.user.username)
        current_username_entry.config(state="readonly")
        current_username_entry.pack(pady=5, padx=25)

        password_label = tk.Label(self.right_frame, text="Enter new password", font=("Arial", 12))
        password_label.pack(pady=5, padx=25)
        password_entry = tk.Entry(self.right_frame, show="*", width=50)
        password_entry.pack(pady=5, padx=25)

        submit_button = tk.Button(self.right_frame, text="Reset Password", command=submit)
        submit_button.pack(pady=20)

    # Backups
    @authorized(allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN))
    def view_backups(self):
        self.create_view(self.user.role, "Backups")

        title_label = tk.Label(self.right_frame, text="Backup options: ", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)

        @authorized_action(self, allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN))
        def new_backup():
            backup_name = self.backup_manager.create()
            messagebox.showinfo("Backup Created", "Backup created successfully")
            App.logger.log_activity(self.user, "created_backup", f"{backup_name}", False)
            self.view_backups()

        button = tk.Button(
            self.right_frame,
            text="Add new",
            width=10,
            command=lambda: new_backup(),
        )
        button.pack(side="top", anchor="w", pady=(20, 0), padx=10)

        backups = self.backup_manager.list()
        tree = ttk.Treeview(self.right_frame, columns=("Backup"), show="headings")
        tree.heading("Backup", text="Backup")
        tree.column("Backup", width=500)

        @authorized_action(self, allowed_roles=(User.Role.SUPER_ADMIN, User.Role.SYSTEM_ADMIN))
        def on_backup_click(event):
            item = tree.selection()[0]
            backup = tree.item(item, "values")[0]

            proceeed = messagebox.askyesno(
                "Warning",
                "Are you sure you want to restore this backup? This will overwrite the current database, and users may lose access to their accouns, including yourself.",
            )
            if proceeed:
                self.backup_manager.restore(backup)
                messagebox.showinfo("Backup Restored", "Backup restored successfully")
            return

        for i, backup in enumerate(backups):
            tree.insert("", "end", values=(backup,))

        tree.pack(padx=10, pady=10)
        tree.bind("<Double-1>", on_backup_click)

    # ======================================== #
    # Layout methods
    # ======================================== #
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def make_frames(self):
        self.left_frame = tk.Frame(self.root, width=400, height=100, bg="RoyalBlue2")
        self.left_frame.grid(row=0, column=0, padx=20, pady=50)

        self.right_frame = tk.Frame(self.root, width=1500, height=100, bg="RoyalBlue2")
        self.right_frame.grid(row=0, column=1, padx=20, pady=50)

    def create_navbar(self, role, current_page):
        def handle_options(option):
            if option == "Logs":
                self.view_logs()
            elif option == "Users":
                self.view_users()

            elif option == "Members":
                self.view_members()
            elif option == "Reset my password":
                self.view_my_password_reset()
            elif option == "Backups":
                self.view_backups()
            elif option == "Logout":
                self.logout()

        # print list of menu options
        menu_options = [
            "Logs",
            "Users",
            "Members",
            "Reset my password",
            "Backups",
            "Logout",
        ]

        greet_user_text = tk.Label(
            self.left_frame,
            text=f"Hello, {self.user.username}",
            fg="white",
            bg="RoyalBlue2",
            font=("Arial", 14, "bold"),
        )
        greet_user_text.pack()

        if role == User.Role.CONSULTANT.value:
            menu_options = [option for option in menu_options if option not in {"Backups", "Logs", "Users"}]

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

    def create_view(self, role, current_page):
        self.clear_screen()
        self.make_frames()
        self.create_navbar(role, current_page)

    # ======================================== #
    # Authentication
    # ======================================== #
    def login(self):
        if self.timeout:
            return

        username = self.username_entry.get()
        password = self.password_entry.get()
        user = self.user_manager.login(username, password)

        if user:
            self.user = user
            self.user_manager.update_last_login(user)
            if user.reset_password == 1:
                self.view_my_password_reset()

            else:
                App.logger.log_activity(self.user, "Login", "Login was sucessfull", False)

                # send user to default page (based on role)
                if self.user.role == User.Role.SUPER_ADMIN.value or self.user.role == User.Role.SYSTEM_ADMIN.value:
                    critical_logs = App.logger.get_critical_logs(self.user.last_login)
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
            if self.login_attempts == 3:
                App.logger.log_activity(
                    self.user,
                    "Unsuccesfull Login",
                    f"Multiple usernames and passwords are tried in a row",
                    True,
                )
                self.start_timeout()

            messagebox.showerror("Login Failed", "Invalid username or password")

    def logout(self):
        self.user = None
        self.view_login_screen()
