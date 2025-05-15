# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.dataview
from src.client.Credentials import Credentials
import gettext
import pyperclip
from threading import Timer
from client_control_functions import get_credentials, decrypt_field
from Credentials import Credentials
from dotenv import load_dotenv
import os
load_dotenv()

KEY = os.getenv("KEY")

_ = gettext.gettext


###########################################################################
## Class PasswordManager
###########################################################################

class PasswordManager(wx.Frame):

    def __init__(self, parent, main_frame, user):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(620, 513), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.cred = None
        self.timer = None
        self.gauge_timer = None
        self.main_frame = main_frame
        self.user = user
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.token = main_frame.token
        self.cred_list = []

        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer6.Add((0, 0), 1, wx.EXPAND, 5)

        self.m_searchCtrl2 = wx.SearchCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                           wx.TE_CENTER | wx.TE_RIGHT)
        self.m_searchCtrl2.ShowSearchButton(True)
        self.m_searchCtrl2.ShowCancelButton(False)
        bSizer6.Add(self.m_searchCtrl2, 0, wx.ALL, 5)

        bSizer5.Add(bSizer6, 0, wx.EXPAND, 5)

        self.m_dataViewListCtrl2 = wx.dataview.DataViewListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                                                wx.dataview.DV_ROW_LINES)
        self.m_dataViewListCtrl2.SetFont(
            wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        self.m_dataViewListCtrl2.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND))
        self.m_dataViewListCtrl2.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVECAPTION))

        self.m_dataViewListCtrl2.AppendTextColumn("Service", width=200)
        self.m_dataViewListCtrl2.AppendTextColumn("Username", width=180)
        self.m_dataViewListCtrl2.AppendTextColumn("Last Modified", width=150)

        self.populate_grid(self.token, self.user)
        bSizer5.Add(self.m_dataViewListCtrl2, 1, wx.EXPAND | wx.ALL, 5)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)

        bSizer5.Add(self.m_staticText4, 0, wx.ALL, 5)

        bSizer51 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)

        bSizer51.Add(self.m_staticText4, 0, wx.ALL, 5)

        bSizer51.Add((0, 0), 1, wx.EXPAND, 5)

        self.m_gauge2 = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL)
        self.m_gauge2.SetValue(0)
        bSizer51.Add(self.m_gauge2, 0, wx.ALL, 5)

        bSizer5.Add(bSizer51, 0, wx.EXPAND, 5)

        self.SetSizer(bSizer5)
        self.Layout()

        self.Centre(wx.BOTH)

        self.Bind(wx.EVT_CHAR, self.copy_cmd)
        self.m_dataViewListCtrl2.Bind(wx.EVT_CHAR, self.copy_cmd)
        self.m_dataViewListCtrl2.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self.print_sel, id=wx.ID_ANY)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    # def populate_grid(self):
    #     sample_data = [
    #         ("Gmail", "user@gmail.com", 'ieri'),
    #         ("Online Banking", "john.doe", 'ieri'),
    #         ("GitHub", "dev_user", 'ieri'),
    #         ("Social Media", "social_user", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #         ("Work VPN", "j.doe@company", 'ieri'),
    #     ]
    #
    #     for item in sample_data:
    #         self.m_dataViewListCtrl2.AppendItem(item)

    def update_gauge(self, count):
        if count <= 100:
            self.m_gauge2.SetValue(count)
            count += 1
            wx.CallLater(100, self.update_gauge, count)
        else:
            self.m_gauge2.SetValue(0)

    def copy_cmd(self, event: wx.KeyEvent):
        def clear_clipboard():
            pyperclip.copy('')
            self.m_staticText4.SetLabel("")
            if self.timer:
                self.timer.cancel()
            if self.gauge_timer:
                self.gauge_timer.cancel()
            self.m_gauge2.SetValue(0)

        if event.GetKeyCode() == 2:  # B
            self.m_staticText4.SetLabel("Copied Username")
            pyperclip.copy(self.cred.get_username())
            self.update_gauge(1)  # Start gauge progress
            self.timer = Timer(10, clear_clipboard)
            self.timer.start()

        elif event.GetKeyCode() == 3:  # C
            self.m_staticText4.SetLabel("Copied Password")
            pyperclip.copy(self.cred.get_password())
            self.update_gauge(1)  # Start gauge progress
            self.timer = Timer(10, clear_clipboard)
            self.timer.start()

    def __del__(self):
        if self.timer:
            self.timer.cancel()
        if self.gauge_timer:
            self.gauge_timer.cancel()

        def on_close(self, event):
            if self.main_frame:
                self.main_frame.Show()
            self.Destroy()

    def print_sel(self, event):
        row_idx = self.m_dataViewListCtrl2.GetSelectedRow()
        title = self.m_dataViewListCtrl2.GetTextValue(row_idx, 0)
        username = self.m_dataViewListCtrl2.GetTextValue(row_idx, 1)
       # password = self.m_dataViewListCtrl2.GetTextValue(row_idx, 2)
        password = ''
        last_modified = self.m_dataViewListCtrl2.GetTextValue(row_idx, 3)
        self.cred = Credentials(title, username, password, last_modified)


    def on_close(self, event):
        if self.main_frame:
            self.main_frame.Show()
        self.Destroy()

    def populate_grid(self, token, user):
        credentials = get_credentials(token, user)
        if credentials.status_code == 200:
            cred_unpacked = credentials.json()['credentials']
            key = KEY
            for cred in cred_unpacked:
                nonce = cred[5]
                service = cred[2]
                username = decrypt_field(cred[3], nonce, key).decode('utf-8')
                password = cred[4]
                last_modified = cred[6]
                credential = Credentials(service, username, password, last_modified, nonce)


                self.m_dataViewListCtrl2.AppendItem([credential.get_title(), credential.get_username(),
                                                      credential.get_last_modified()])

                self.cred_list.append(credential)




