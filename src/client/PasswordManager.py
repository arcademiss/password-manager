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
from setuptools.package_index import Credential

from src.client.Credentials import Credentials
from src.client.CredentialForm import CredentialForm
from src.client.CredentialFormEdit import CredentialFormEdit
import gettext
import pyperclip
from threading import Timer
from client_control_functions import get_credentials, decrypt_field, derive_aes_key
from Credentials import Credentials
from dotenv import load_dotenv
import os
load_dotenv()

KEY = os.getenv("KEY")
SALT = os.getenv("SALT_SECRET")

_ = gettext.gettext


###########################################################################
## Class PasswordManager
###########################################################################

class PasswordManager(wx.Frame):

    def __init__(self, parent, main_frame, user, password):
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
        self.password = password
        self.key = None

        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button3 = wx.Button(self, wx.ID_ANY, _(u"Add"), wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_button3, 0, wx.ALL, 5)

        self.m_button4 = wx.Button(self, wx.ID_ANY, _(u"Edit"), wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_button4, 0, wx.ALL, 5)

        self.m_button5 = wx.Button(self, wx.ID_ANY, _(u"Delete"), wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_button5, 0, wx.ALL, 5)

        self.m_button6 = wx.Button(self, wx.ID_ANY, _(u"Save"), wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_button6, 0, wx.ALL, 5)

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
        self.m_button3.Bind(wx.EVT_BUTTON, self.add_credential)
        self.m_button4.Bind(wx.EVT_BUTTON, self.edit_credential)
        self.m_button5.Bind(wx.EVT_BUTTON, self.delete_credential)

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
            pyperclip.copy(decrypt_field(self.cred.get_password().hex(), self.cred.get_nonce().hex(), self.key).decode('utf-8'))
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
        if row_idx >= 0:
            self.cred = self.cred_list[row_idx]  # Reference the actual object, don't recreate it

    def on_close(self, event):
        if self.main_frame:
            self.main_frame.Show()
        self.Destroy()

    def populate_grid(self, token, user):
        credentials = get_credentials(token, user)
        if credentials.status_code == 200:
            cred_unpacked = credentials.json()['credentials']

            key= derive_aes_key(self.password, KEY, bytes.fromhex(SALT))
            self.key = key
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




    def add_credential(self, event):
        credential_form = CredentialForm(self)
        credential_form.Show()

    def edit_credential(self, event):
        if self.cred:
            credential_form = CredentialFormEdit(self, self.cred)
            credential_form.Show()
        else:
            self.m_staticText4.SetLabel("Select an entry to edit first!")
            event.Skip()

    def delete_credential(self, event):
        row_idx = self.m_dataViewListCtrl2.GetSelectedRow()

        if row_idx == wx.NOT_FOUND:
            self.m_staticText4.SetLabel("Select an entry to delete first!")
            return

        # Optional: confirm with the user
        confirm = wx.MessageBox("Are you sure you want to delete this credential?", "Confirm Delete",
                                wx.YES_NO | wx.ICON_WARNING)
        if confirm != wx.YES:
            return

        # Remove from grid
        self.m_dataViewListCtrl2.DeleteItem(row_idx)

        # Remove from internal list
        deleted_cred = self.cred_list.pop(row_idx)

        # If the deleted item is the current self.cred, clear it
        if self.cred == deleted_cred:
            self.cred = None

        # Optional: set status message
        self.m_staticText4.SetLabel("Credential deleted.")



