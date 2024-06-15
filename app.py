import tkinter as tk
from config import Config
from tkinter import messagebox
from managers.address_manager import AddressManager
from managers.member_manager import MemberManager
from managers.profile_manager import ProfileManager
from managers.user_manager import UserManager
from forms.Form import CreateForm, DeleteForm

class App:
    config: Config = None

    def __init__(self, root, config):
        self.root = root
        App.config = config

        self.user_manager = UserManager(config)
        self.address_manager = AddressManager(config)
        self.member_manager = MemberManager(config)
        self.profile_manager = ProfileManager(config)

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

        self.username_label = tk.Label(self.root, text="Username")
        self.username_label.pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(self.root, text="Password")
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = tk.Button(self.root, text="Login", command=self.login)
        self.login_button.pack(pady=20)

    def logout(self):
        self.user = None
        self.create_login_screen()
    
    def go_back(self):
        self.clear_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        # username = self.username_entry.get()
        # password = self.password_entry.get()
        username = "super_admin"
        password = "Admin_123?"

        user = self.user_manager.login(username, password)
        if user:
            self.user = user
            self.create_main_screen()
        else:
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
        def handle_option(option):
            if option == "System Admin":
                self.view_sysadmin()
            elif option == "Consultant":
                self.view_consultant()
            elif option == "Members":
                self.view_members()
            elif option == "Profiles":
                self.view_profiles()

        label = tk.Label(self.root, text="Super Admin Panel")
        label.pack()

        # print list of menu options
        menu_options = [
            "System Admin",
            "Consultants",
            "Members",
            "Profiles",
        ]

        for i, option in enumerate(menu_options):
            button = tk.Button(
                self.root,
                text=option,
                command=lambda option=option: handle_option(option),
            )
            button.pack(pady=5)

    #
    # System admin screens
    #
    def create_system_admin_screen(self):
        label = tk.Label(self.root, text="System Admin Panel")
        label.pack()

    #
    # Consultant screens
    #
    def create_consultant_screen(self):
        label = tk.Label(self.root, text="Consultant Panel")
        label.pack()

    def create_delete_screen(self):
        pass


    def view_members(self):
        self.clear_screen()
        users = self.member_manager.get_members()
        for user in users:
            label = tk.Label(self.root, text=f"{user}")
            label.pack()

    def view_sysadmin(self):
        self.clear_screen()
        def handle_option(option):
            if option == "Create sysadmin":
                # self.view_sysadmin()
                form = CreateForm(self.root, App.config)
                form.show_form()

            elif option == "Delete sysadmin":
                delete_form = DeleteForm(self.root, App.config)
                delete_form.show_form()

            elif option == "Search syadmin":
                print("page for Search sysadmin")

            elif option == "Update sysadmin":
                print("page for update sysadmin")


        menu_options = [
            "Create sysadmin",
            "Delete sysadmin",
            "Search syadmin",
            "Update sysadmin",
        ]
        for i, option in enumerate(menu_options):
            button = tk.Button(
                self.root,
                text=option,
                command=lambda option=option: handle_option(option),
            )
            button.pack(pady=5)
