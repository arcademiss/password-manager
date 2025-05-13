# -*- coding: utf-8 -*-
import json

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

import gettext
import os

from src.client.client_control_functions import create_creds, send_to_server, check_password
from hashlib import pbkdf2_hmac as pbkdf2
from dotenv import load_dotenv
from PasswordManager import PasswordManager

load_dotenv()

_ = gettext.gettext

###########################################################################
# Environment variables
###########################################################################

CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SALT_SECRET = os.getenv('SALT_SECRET')


###########################################################################
# Class MainFrame
###########################################################################

class MainFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=_(u"Vaulty"), pos=wx.DefaultPosition,
                          size=wx.Size(500, 300), style=wx.DEFAULT_FRAME_STYLE)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.token = None

        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText2_login = wx.StaticText(self, wx.ID_ANY, _(u"Login"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText2_login.Wrap(-1)

        self.m_staticText2_login.SetFont(
            wx.Font(50, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString))

        bSizer2.Add(self.m_staticText2_login, 0, wx.ALL, 5)

        self.m_staticText3_Username = wx.StaticText(self, wx.ID_ANY, _(u"Username:"), wx.DefaultPosition,
                                                    wx.DefaultSize, 0)
        self.m_staticText3_Username.Wrap(-1)

        bSizer2.Add(self.m_staticText3_Username, 0, wx.ALL, 5)

        self.m_textCtrl5_LoginUsername = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                                     wx.DefaultSize, 0)

        bSizer2.Add(self.m_textCtrl5_LoginUsername, 0, wx.ALL, 5)

        self.m_staticText4_Password = wx.StaticText(self, wx.ID_ANY, _(u"Password:"), wx.DefaultPosition,
                                                    wx.DefaultSize, 0)
        self.m_staticText4_Password.Wrap(-1)

        bSizer2.Add(self.m_staticText4_Password, 0, wx.ALL, 5)

        self.m_textCtrl6_LoginPassword = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                                     wx.DefaultSize, 0|wx.TE_PASSWORD)
        bSizer2.Add(self.m_textCtrl6_LoginPassword, 0, wx.ALL, 5)

        bSizer3 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button1_Submit = wx.Button(self, wx.ID_ANY, _(u"Login!"), wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer3.Add(self.m_button1_Submit, 0, wx.ALL, 5)

        self.m_button2_Register = wx.Button(self, wx.ID_ANY, _(u"Register!"), wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer3.Add(self.m_button2_Register, 0, wx.ALL, 5)

        bSizer2.Add(bSizer3, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer2)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_button1_Submit.Bind(wx.EVT_BUTTON, self.login_event)
        self.m_button2_Register.Bind(wx.EVT_BUTTON, self.register_event)

        # custom attributes

    def __del__(self):
        pass

    # Virtual event handlers, override them in your derived class
    def login_event(self, event):
        # get vault key and master password from login information
        username = self.m_textCtrl5_LoginUsername.GetValue()
        password = self.m_textCtrl6_LoginPassword.GetValue()

        if not username or not password:
            wx.MessageDialog(None, "You must fill in both fields!", "ERROR!", wx.ICON_ERROR).ShowModal()
            return

        auth_key, _, _ = create_creds(username, password, CLIENT_SECRET, SALT_SECRET)

        # todo: send to server and receive vault and begin decryption


        try:
            response = send_to_server(auth_key, username, 'login')
        except ValueError:
            wx.MessageDialog(None, "Fatal Error!", "ERROR!", wx.OK).ShowModal()
            response = 0

        if response.status_code == 401:
            wx.MessageDialog(None, "Wrong password or username!", "Error", wx.ICON_ERROR).ShowModal()
            self.m_textCtrl5_LoginUsername.Clear()
            self.m_textCtrl6_LoginPassword.Clear()

        elif response.status_code == 200:

            wx.MessageDialog(None, "User authenticated.", "Info", wx.OK).ShowModal()
            self.m_textCtrl5_LoginUsername.Clear()
            self.m_textCtrl6_LoginPassword.Clear()
            pwd = PasswordManager(parent=None, main_frame=self)
            pwd.Show()
            self.Hide()
            data_payload = json.loads(response.content.decode('utf-8'))
            self.token = data_payload['access_token']


    def register_event(self, event):

        username = self.m_textCtrl5_LoginUsername.GetValue()
        password = self.m_textCtrl6_LoginPassword.GetValue()

        if not username or not password:
            wx.MessageDialog(None, "You must fill in both fields!", "ERROR!", wx.ICON_ERROR).ShowModal()
            return



        if check_password(password)[0] < 3:
            if check_password(password)[1][0]:
                wx.MessageDialog(None, "Weak password!\n"+ check_password(password)[1][0], "ERROR!",
                             wx.ICON_ERROR).ShowModal()
            else:
                wx.MessageDialog(None, "Weak password!\n" + check_password(password)[1][0], "ERROR!",
                                 wx.ICON_ERROR).ShowModal()
            return


        auth_key, _, _ = create_creds(username, password, CLIENT_SECRET, SALT_SECRET)

        try:
            response = send_to_server(auth_key, username, 'register')
        except ValueError:
            wx.MessageDialog(None,"Fatal Error!", "ERROR!", wx.OK).ShowModal()
            response=0

        if response.status_code == 200:
            wx.MessageDialog(None, "User created.", "Info", wx.OK).ShowModal()
            self.m_textCtrl5_LoginUsername.Clear()
            self.m_textCtrl6_LoginPassword.Clear()
        elif response.status_code == 400:
            wx.MessageDialog(None, "User already exists!", "Error", wx.ICON_ERROR).ShowModal()
            self.m_textCtrl5_LoginUsername.Clear()
            self.m_textCtrl6_LoginPassword.Clear()

