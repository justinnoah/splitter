import os

import wx

class SplitPanel(wx.Panel):

    predefined = sorted(["Cardio", "H&P", "Consult", "OP Report", "Discharge", "Clinic", "ED Report"])

    def __init__(self, parent, id):
        # THIS NEEDS TO BE CLEANED!
        wx.Panel.__init__(self, parent, id)

        # category_row, split_entry
        self.outer = wx.BoxSizer(wx.VERTICAL)
        self.outer.Add((0,10))
        # Prefix (Combo box), Path_Entry, Path_Button
        self.category_row = wx.BoxSizer(wx.HORIZONTAL)
        # Split Rules - Label, TextCtrl
        self.rules_row = wx.BoxSizer(wx.HORIZONTAL)

        # category_row contents
        self.cmb_prefix = wx.ComboBox(self, choices=self.predefined)
        self.cmb_prefix.SetValue(self.predefined[0])
        self.out_text = wx.StaticText(self, label=" Output Path: ")
        self.ent_path = wx.TextCtrl(self)
        self.btn_browse = wx.Button(self, label="Browse...")

        # Add items to category_row
        self.category_row.Add(self.cmb_prefix, proportion=0)
        self.category_row.Add(self.out_text, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.category_row.Add(self.ent_path, proportion=5)
        self.category_row.Add(self.btn_browse, proportion=0)

        # Split Rules Row contents
        self.lbl_split = wx.StaticText(self, label="  Split Ranges: ")
        self.ent_split_rules = wx.TextCtrl(self)
        self.btn_Clear = wx.Button(self, wx.ID_CLEAR)

        # Add items to rules_row
        self.rules_row.Add(self.lbl_split, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.rules_row.Add(self.ent_split_rules, proportion=5)
        self.rules_row.Add(self.btn_Clear, proportion=0)

        # Add items to outer
        self.outer.Add(self.category_row, proportion=0, flag=wx.GROW)
        self.outer.Add(self.rules_row, proportion=0, flag=wx.GROW)

        # Setup bindings
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.btn_Clear)
        self.Bind(wx.EVT_TEXT, self.ValidateRange)
        self.Bind(wx.EVT_TEXT, self.ValidatePath, self.ent_path)

        # Finish up
        self.SetSizer(self.outer)
        self.Show()

    def OnClear(self, event):
        self.ent_path.SetBackgroundColour("White")
        self.ent_path.Clear()
        self.ent_path.Refresh()
        self.ent_split_rules.SetBackgroundColour("White")
        self.ent_split_rules.Clear()
        self.ent_split_rules.Refresh()

    def ValidateRange(self, event):
        event.Skip()

    def ValidatePath(self, event):
        # Simplify some typing with 'text'
        text = event.GetEventObject()

        # For no text in the Outpath field, the background color
        # should be white. If the path doesn't exist, pink, or if the path
        # does exist, the 'pink' of green (light green).
        if not text.GetValue():
            text.SetBackgroundColour("White")
        elif os.path.isdir(os.path.join(text.GetValue())):
            text.SetBackgroundColour((192,255,203))
            print "Valid"
        else:
            text.SetBackgroundColour((255,192,203))
            print "Invalid"
        text.Refresh()
        event.Skip()
