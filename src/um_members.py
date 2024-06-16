import sqlite3
from cryptography.hazmat.primitives import serialization
import tkinter as tk

from app import App
from config import Config


def load_private_key():
    try:
        with open("keys/private.pem", "rb") as key_file:
            return serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
    except FileNotFoundError:
        return None


def load_public_key():
    try:
        with open("keys/public.pem", "rb") as key_file:
            return serialization.load_pem_public_key(
                key_file.read(),
            )
    except FileNotFoundError:
        return None


if "__main__" == __name__:
    con = sqlite3.connect("data.db")
    config = Config(
        con=con,
        private_key=load_private_key(),
        public_key=load_public_key(),
    )

    # create the root window
    root = tk.Tk()
    app = App(root, config)
    app.run()

    # close the database connection
    con.close()
