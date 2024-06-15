import tkinter as tk
from tkinter import ttk

from tkinter import messagebox
from managers.user_manager import UserManager
from config import Config
from utils import validate_password, validate_username
from entities.user import User



class BaseForm():

    def __init__(self, root):
        self.root = root
    
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


class CreateForm(BaseForm):
    config: Config = None

    def __init__(self, root, config):
        super().__init__(root)
        CreateForm.config = config

        self.user_manager = UserManager(config)


   
    def show_form(self):
        self.clear_screen()
        # Create a title label
        title_label = tk.Label(self.root, text="Create new user", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        self.username_label = tk.Label(self.root, text="Please enter the new username", font=("Arial", 12))
        self.username_label.pack(pady=5)
        self.username_entry = tk.Entry(self.root, width=100)
        self.username_entry.pack(pady=5)

        
        self.password_label  = tk.Label(self.root, text="Please enter the new password",font=("Arial", 12))
        self.password_label .pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*", width=100)
        self.password_entry.pack(pady=5)

        self.role_label = tk.Label(self.root, text="Select an role:", width=100, font=("Arial", 12))
        self.role_label.pack(pady=10)

        options = [
            User.Role.CONSULTANT.value,
            User.Role.SYSTEM_ADMIN.value,
            "Member"         
        ]

        

        # Create a Combobox widget
        self.roles_option = ttk.Combobox(self.root, values=options)
        self.roles_option.pack()

        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=20)
        

    def submit(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.roles_option.get()
        print(username, password, role)
        
        print(validate_username(username))
        print(validate_password(password))

        if validate_username(username) and validate_password(password):
            user = self.user_manager.create_user(username, password,role)
            if user is not None:
                messagebox.showinfo("Information", "User has been created.")
        else:
            messagebox.showinfo("Information", "Please try Again")