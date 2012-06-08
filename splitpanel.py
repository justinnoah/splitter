import os
import re

import wx

class SplitPanel(wx.Panel):

    predefined = sorted(["Cardio", "H&P", "Consult", "OP Report", "Discharge", "Clinic", "ED Report"])

    def __init__(self, parent, id):
        # THIS NEEDS TO BE CLEANED!
        wx.Panel.__init__(self, parent, id)

        # category_row, split_entry
        self.outer = wx.BoxSizer(wx.VERTICAL)
        self.outer.Add((0,5))
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
        self.outer.Add(wx.StaticLine(self), proportion=1, flag=wx.GROW)
        self.outer.Add((0,5))
        self.outer.Add(self.category_row, proportion=0, flag=wx.GROW)
        self.outer.Add(self.rules_row, proportion=0, flag=wx.GROW)

        # Setup bindings
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.btn_Clear)
        self.Bind(wx.EVT_BUTTON, self.OnBrowse, self.btn_browse)
        self.Bind(wx.EVT_TEXT, self.ValidateRange, self.ent_split_rules)
        self.Bind(wx.EVT_TEXT, self.ValidatePath, self.ent_path)

        # Finish up
        self.SetSizer(self.outer)
        self.Show()

    def OnClear(self, event):
        # Reset background color to white and clear the text of
        # the text fields.
        self.ent_path.SetBackgroundColour(wx.NullColour)
        self.ent_path.Clear()
        self.ent_path.Refresh()
        self.ent_split_rules.SetBackgroundColour(wx.NullColour)
        self.ent_split_rules.Clear()
        self.ent_split_rules.Refresh()

    def ValidateRange(self, event):
        text_field = event.GetEventObject()
        text = text_field.GetValue()
        result = False

        # Change all , to . for splitting simplification
        text = text.replace(',','.')
        text = text.strip('.')
        sections = text.split('.')

        # Need to match any number or range of numbers separated by a -.
        pattern = "(\d+-\d+$|\d+$)"

        # Now to check each number or range individually, but break early and
        # color pink if invalid input is given.
        for t in sections:

            m = re.match(pattern, t)

            # If we have a match, let's see if it is a number or range.
            if m:
                # Checking for a range
                if '-' in t:
                    # Split at the -
                    numbers = t.split('-')
                    # and check if we have an increasing range.
                    if int(numbers[1]) - int(numbers[0]) >= 0:
                        result = True
                    # break if not
                    else:
                        result = False
                        break
                # If not a range, then it is a single integer according
                # to the regex and we want a green light.
                else:
                    result = True
            # A valid digit or possible range was not found, lets flag the user
            else:
                result = False
                break

        if not text:
            text_field.SetBackgroundColour(wx.NullColour)
        else:
            if result:
                text_field.SetBackgroundColour(wx.WHITE)
            elif not result:
                text_field.SetBackgroundColour((255,192,203))

        text_field.Refresh()
        event.Skip()

    def ValidatePath(self, event):
        # Simplify some typing with 'text'
        text = event.GetEventObject()

        # For no text in the Outpath field, the background color
        # should be white. If the path doesn't exist, pink, or if the path
        # does exist, the 'pink' of green (light green).
        if not text.GetValue():
            text.SetBackgroundColour(wx.NullColour)
        elif os.path.isdir(os.path.join(text.GetValue())):
            text.SetBackgroundColour(wx.WHITE)
        else:
            text.SetBackgroundColour((255,192,203))
        text.Refresh()
        event.Skip()

    def OnBrowse(self, event):
        # Openning the PDF for manipulation
        dlg = wx.DirDialog(self, message=self.cmb_prefix.GetValue() + " Output Folder", defaultPath=self.ent_path.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            self.ent_path.Clear()
            path = os.path.join(dlg.GetPath())
            self.ent_path.AppendText(path)
        dlg.Destroy()
        event.Skip()

if __name__ == '__main__':
    print "Not a standalone module"
    exit(0)