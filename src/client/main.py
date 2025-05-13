from MainFrame import MainFrame
import wx
import os
from dotenv import load_dotenv, dotenv_values
from random import random

BASE_DIR = os.getcwd()


def check_env():
    file_name = BASE_DIR + '\\.env'
    if os.path.isfile(file_name):
        load_dotenv()
    else:
        with open(file_name, 'w') as file:
            secret_key = os.urandom(32).hex()
            file.write(f"CLIENT_SECRET='{secret_key}'\n")
            salt = os.urandom(32).hex()
            file.write(f"SALT_SECRET='{salt}'\n")
            print("Created .env file.")


def main():
    app = wx.App()
    main_frame = MainFrame(parent=None)
    main_frame.Show()
    check_env()
    app.MainLoop()


if __name__ == "__main__":
    main()
