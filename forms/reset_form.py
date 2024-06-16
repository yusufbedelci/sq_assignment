from tkinter import messagebox
from entities.user import User
from forms.Form import BaseForm
from config import Config
from managers.user_manager import UserManager
import tkinter as tk

class UserResetForm(BaseForm):
    config: Config = None

    def __init__(self, root, config):
        super().__init__(root)
        UserResetForm.config = config

        self.user_manager = UserManager(config)

    def show_form(self, current_user:User, reseted_username:str):
        self.clear_screen()
        title_label = tk.Label(self.root, text="Reset Password", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        self.current_username_label = tk.Label(self.root, text="Current Username", font=("Arial", 12))
        self.current_username_label.pack(pady=5)
        self.current_username_entry = tk.Entry(self.root, width=100)
        self.current_username_entry.insert(0, reseted_username)
        self.current_username_entry.config(state='readonly')
        self.current_username_entry.pack(pady=5)



        self.password_label= tk.Label(self.root, text="Enter new password",font=("Arial", 12))
        self.password_label.pack(pady=5)

        self.password_entry = tk.Entry(self.root, show="*", width=100)
        self.password_entry.pack(pady=5)

        # self.repeat_password_label= tk.Label(self.root, text="Repeat new password",font=("Arial", 12))
        # self.repeat_password_label.pack(pady=5)

        # self.repeat_password_entry = tk.Entry(self.root, show="*", width=100)
        # self.repeat_password_entry.pack(pady=5)

        self.submit_button = tk.Button(self.root, text="Reset Password", command=self.submit)
        self.submit_button.pack(pady=20)
    
    def submit(self):
        reseted_user = self.user_manager.get_user(self.current_username_entry.get())
        self.user_manager.reset_password(reseted_user, self.password_entry.get())
        messagebox.showinfo("Information", "User temp password has been set.")
    
        