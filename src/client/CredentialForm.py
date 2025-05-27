# -*- coding: utf-8 -*-
from xmlrpc.client import DateTime

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from src.client.password_generator import generate_password, check_password
from src.client.Credentials import Credentials
from datetime import datetime
from src.client.client_control_functions import encrypt_field, derive_aes_key

import gettext
_ = gettext.gettext

###########################################################################
## Class CredentialForm
###########################################################################

class CredentialForm ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 416,307 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.parent = parent

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer6 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, _(u"Service"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )

        bSizer6.Add( self.m_staticText5, 0, wx.ALL, 5 )

        self.m_textCtrl3 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer6.Add( self.m_textCtrl3, 0, wx.ALL, 5 )

        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, _(u"Username"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )

        bSizer6.Add( self.m_staticText6, 0, wx.ALL, 5 )

        self.m_textCtrl4 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer6.Add( self.m_textCtrl4, 0, wx.ALL, 5 )

        self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, _(u"Password"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )

        bSizer6.Add( self.m_staticText7, 0, wx.ALL, 5 )

        self.m_textCtrl5 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PASSWORD )
        bSizer6.Add( self.m_textCtrl5, 0, wx.ALL, 5 )

        bSizer7 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_button7 = wx.Button( self, wx.ID_ANY, _(u"Generate Password"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer7.Add( self.m_button7, 0, wx.ALL, 5 )

        self.m_checkBox1 = wx.CheckBox( self, wx.ID_ANY, _(u"Show Password"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer7.Add( self.m_checkBox1, 0, wx.ALL, 5 )

        self.m_button9 = wx.Button( self, wx.ID_ANY, _(u"Check Strength"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer7.Add( self.m_button9, 0, wx.ALL, 5 )


        bSizer6.Add( bSizer7, 1, wx.EXPAND, 5 )

        self.m_button10 = wx.Button( self, wx.ID_ANY, _(u"Save"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer6.Add( self.m_button10, 0, wx.ALL, 5 )


        self.SetSizer( bSizer6 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_button7.Bind( wx.EVT_BUTTON, self.get_password )
        self.m_checkBox1.Bind( wx.EVT_CHECKBOX, self.show_password )
        self.m_button9.Bind( wx.EVT_BUTTON, self.check_strength )
        self.m_button10.Bind( wx.EVT_BUTTON, self.save_credential )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def get_password( self, event ):
        self.m_textCtrl5.SetValue(generate_password())

    def show_password(self, event):
        value = self.m_textCtrl5.GetValue()
        pos = self.m_textCtrl5.GetInsertionPoint()

        if self.m_checkBox1.IsChecked():
            style = 0  # Show plain text
        else:
            style = wx.TE_PASSWORD  # Masked text

        # Recreate TextCtrl at the same index
        parent = self.m_textCtrl5.GetParent()
        sizer = self.m_textCtrl5.GetContainingSizer()

        # Find the index of the old text control
        old_index = sizer.GetChildren().index(sizer.GetItem(self.m_textCtrl5))

        sizer.Hide(self.m_textCtrl5)
        sizer.Detach(self.m_textCtrl5)
        self.m_textCtrl5.Destroy()

        self.m_textCtrl5 = wx.TextCtrl(parent, value=value, style=style)
        self.m_textCtrl5.SetInsertionPoint(pos)

        # Insert at the original index
        sizer.Insert(old_index, self.m_textCtrl5, flag=wx.ALL, border=5)
        sizer.Layout()

    def check_strength( self, event ):
        score, advice = check_password( self.m_textCtrl5.GetValue() )
        if score<4:
            wx.MessageBox(f"Password score {score}/4. You should try a more secure password."
                          f"\n {'Suggestion:' + advice[0] if advice else ''}", style=wx.OK)
        else:
            wx.MessageBox("Strong password! Well done.", style=wx.OK)

    def save_credential( self, event ):
        title = self.m_textCtrl3.GetValue()
        password = self.m_textCtrl5.GetValue()
        user = self.m_textCtrl4.GetValue()

        self.parent.m_dataViewListCtrl2.AppendItem([title, user,
                                                      f"{datetime.now().date()}"])

        nonce, password_encrypted = encrypt_field(password.encode('utf-8').hex(), self.parent.key)

        credential = Credentials(title,user,password_encrypted, datetime.now(),nonce)
        print(credential)
        self.parent.cred_list.append(credential)
        self.Destroy()


