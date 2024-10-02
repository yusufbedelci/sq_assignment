import sqlite3
from cryptography.hazmat.primitives import serialization
import tkinter as tk
from pathlib import Path

from app import App
from config import Config

dir_path = Path(__file__).resolve().parent


def load_private_key():
    try:
        private_key_path = dir_path / "keys/private.pem"
        with private_key_path.open("rb") as key_file:
            return serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
    except FileNotFoundError:
        return None


def load_public_key():
    try:
        public_key_path = dir_path / "keys/public.pem"
        with public_key_path.open("rb") as key_file:
            return serialization.load_pem_public_key(
                key_file.read(),
            )
    except FileNotFoundError:
        return None


if "__main__" == __name__:
    db_path = dir_path / "data.db"
    con = sqlite3.connect(db_path)
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
