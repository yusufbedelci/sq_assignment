import tkinter as tk
from tkinter import ttk
from entities.user import User
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

        self.roles_option = ttk.Combobox(self.root, values=options)
        self.roles_option.pack()

        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=20)
        

    def submit(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.roles_option.get()
    
        if validate_username(username) and validate_password(password):
            user = self.user_manager.create_user(username, password,role)
            if user is not None:
                messagebox.showinfo("Information", "User has been created.")
        else:
            messagebox.showinfo("Information", "Please try Again")


class DeleteForm(BaseForm):
    config: Config = None
    def __init__(self, root, config):
        super().__init__(root)
        DeleteForm.config = config

        self.user_manager = UserManager(config)

    def show_form(self):
        self.clear_screen()
        title_label = tk.Label(self.root, text="Create new user", font=("Arial", 16, "bold"))
        title_label.pack()
        options = []
        for user in self.user_manager.get_users():
            options.append(user.username)

        self.roles_option = ttk.Combobox(self.root, values=options)
        self.roles_option.pack()

        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=20)
        
    def submit(self):
        form_user = self.roles_option.get()
        deleted_user = self.user_manager.get_user(form_user)
        self.user_manager.delete_user(deleted_user)
        messagebox.showinfo("Information", "User has been deleted.")


class UpdateForm(BaseForm):
    config: Config = None
    def __init__(self, root, config):
        super().__init__(root)
        UpdateForm.config = config
        self.user_manager = UserManager(config)
    

    def show_form(self, username):
        self.clear_screen()
        
        title_label = tk.Label(self.root, text="Update user", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        updated_user = self.user_manager.get_user(username)

        self.current_username_label = tk.Label(self.root, text="Current Username", font=("Arial", 12))
        self.current_username_label.pack(pady=5)
        self.current_username_entry = tk.Entry(self.root, width=100)
        self.current_username_entry.insert(0, updated_user.username)
        self.current_username_entry.config(state='readonly')
        self.current_username_entry.pack(pady=5)

        self.current_role_label = tk.Label(self.root, text="Current Role", font=("Arial", 12))
        self.current_role_label.pack(pady=5)
        self.current_role_entry = tk.Entry(self.root, width=100)
        self.current_role_entry.insert(0, updated_user.role)
        self.current_role_entry.config(state='readonly')
        self.current_role_entry.pack(pady=5)

        self.username_label = tk.Label(self.root, text="Username", font=("Arial", 12))
        self.username_label.pack(pady=5)
        self.username_entry = tk.Entry(self.root, width=100)
        self.username_entry.insert(0, updated_user.username)
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

        self.roles_option = ttk.Combobox(self.root, values=options)
        self.roles_option.pack()

        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=20)



    def submit(self):
        current_username = self.current_username_entry.get()  
        new_username = self.username_entry.get()  
        new_password = self.password_entry.get()
        new_role = self.roles_option.get()

        try:
            user_to_update = self.user_manager.get_user(current_username)
            if user_to_update is not None:
                self.user_manager.update_user(user_to_update, new_username, new_password, new_role)
                updated_user = self.user_manager.get_user(new_username)
                if updated_user is not None:
                    messagebox.showinfo("Information", "User has been updated successfully.")
                else:
                    messagebox.showerror("Error", "Failed to retrieve updated user.")
            else:
                messagebox.showerror("Error", "User not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update user: {str(e)}")
