import tkinter as tk
from tkinter import ttk
from config import Config
from tkinter import messagebox
from forms.reset_form import UserResetForm
from managers.address_manager import AddressManager
from managers.member_manager import MemberManager
from managers.profile_manager import ProfileManager
from managers.user_manager import UserManager
from forms.Form import CreateForm, DeleteForm, UpdateForm
from entities.user import User
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
        self.history = []
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
        self.history=[]
        self.create_login_screen()
    
    def go_back(self):
        if self.history:
            last_screen = self.history.pop()  
            self.clear_screen()
            last_screen()  

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        # Uncomment when you are done!
        username = self.username_entry.get()
        password = self.password_entry.get()
        # username = "super_admin"
        # password = "Admin_123?"

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
            self.history.append(self.create_main_screen)
            self.create_super_admin_screen()
        elif self.user.role == "system_admin":
            self.history.append(self.create_main_screen)
            self.create_system_admin_screen()
        elif self.user.role == "consultant":
            self.history.append(self.create_main_screen)
            self.create_consultant_screen()

    #
    # Super admin screens
    #
    def create_super_admin_screen(self):
        self.clear_screen()
        def handle_super_options(option):
            if option == "System Admin":
                self.history.append(self.create_super_admin_screen)
                self.view_sysadmin()
            elif option == "Consultant":
                self.history.append(self.create_super_admin_screen)
                self.view_consultant()
            elif option == "Members":
                self.history.append(self.create_super_admin_screen)
                self.view_members()
            elif option == "Profiles":
                self.history.append(self.create_super_admin_screen)
                self.view_profiles()
            elif option == "Reset password":
                self.view_password_reset_screen()
                
                            


            if self.history:
                back_button = tk.Button(self.root, text="Back", command=self.go_back)
                back_button.pack(pady=5)

        label = tk.Label(self.root, text="Super Admin Panel")
        label.pack()

        # print list of menu options
        menu_options = [
            "System Admin",
            "Consultants",
            "Members",
            "Reset password",
            "Profiles",
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
        label = tk.Label(self.root, text="System Admin Panel")
        label.pack()    

    #
    # Consultant screens
    #
    def create_consultant_screen(self):
        label = tk.Label(self.root, text="Consultant Panel")
        label.pack()
    
    def view_password_reset_screen(self):
        self.clear_screen()
        reset_form = UserResetForm(self.root, App.config)
        tree = ttk.Treeview(self.root, columns=("Username", "Role", "Reset"), show="headings")
        def on_username_click(event):
            item = tree.selection()[0]
            username = tree.item(item, "values")[0]  
            reset_form.show_form(self.user,username)
        
        users = self.user_manager.get_users()
        for user in users:
            if user.role != User.Role.SUPER_ADMIN.value:
                username = user.username
                role = user.role
                reset = user.reset_password
                tree.insert("", "end", values=(username,role, reset))
        tree.heading("Username", text="Username")
        tree.heading("Role", text="Role")
        tree.heading("Reset", text="Reset")
        tree.pack(padx=10, pady=10)
        tree.bind("<Double-1>", on_username_click)

    def view_members(self):
        self.clear_screen()
        users = self.member_manager.get_members()
        for user in users:
            label = tk.Label(self.root, text=f"{user}")
            label.pack()

    def view_sysadmin(self):
        self.clear_screen()
        title_label = tk.Label(self.root, text="Menu Options: ", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)

        def handle_option(option):
            if option == "Create sysadmin":
                # self.view_sysadmin()
                form = CreateForm(self.root, App.config)
                form.show_form(User.Role.SYSTEM_ADMIN.value)

            elif option == "Delete sysadmin":
                self.history.append(self.view_sysadmin)
                delete_form = DeleteForm(self.root, App.config)
                delete_form.show_form()

            elif option == "List sysadmins":
                    self.clear_screen()
                    tree = ttk.Treeview(self.root, columns=("Username", "Role"), show="headings")
                    tree.heading("Username", text="Username")
                    tree.heading("Role", text="Role")
                    tree.pack(padx=10, pady=10)

                    users = self.user_manager.get_users()
                    for user in users:
                        if user.role == User.Role.SYSTEM_ADMIN.value:
                            username = user.username
                            role = user.role
                            tree.insert("", "end", values=(username,role))
                    tree.bind("<Double-1>")

            elif option == "Update sysadmin":
                self.clear_screen()
                update_form = UpdateForm(self.root, App.config)
                def on_username_click(event):
                    item = tree.selection()[0]
                    username = tree.item(item, "values")[0]  
                    update_form.show_form(username)
                    
                label = tk.Label(self.root, text="Create new user", font=("Arial", 16, "bold"))
                label = tk.Label(self.root, text="Update User")
                label.pack()

                description_label = tk.Label(self.root, text="Double click on an user to update: ", font=("Arial", 10))
                description_label.pack()

                tree = ttk.Treeview(self.root, columns=("Username", "Role"), show="headings")
                tree.heading("Username", text="Username")
                tree.heading("Role", text="Role")
                tree.pack(padx=10, pady=10)
                tree.bind("<Double-1>", on_username_click)

                users = self.user_manager.get_users()
                for user in users:
                    if user.role != User.Role.SUPER_ADMIN.value:
                        username = user.username
                        role = user.role
                        tree.insert("", "end", values=(username,role))

            if self.history:
                back_button = tk.Button(self.root, text="Back", command=self.go_back)
                back_button.pack(pady=5)

        menu_options = [
            "Create sysadmin",
            "Delete sysadmin",
            "Update sysadmin",
            "List sysadmins",
            
        ]
        for i, option in enumerate(menu_options):
            button = tk.Button(
                self.root,
                text=option,
                width=50,
                command=lambda option=option: handle_option(option),
            )
            button.pack(pady=5)
