import os

import wx
from pyPdf import PdfFileWriter, PdfFileReader

# This class actually does the verification of splitting parameters and the
# writing of the new PDF files.

class WorkerWindow(wx.Frame):
    """
    WorkerWindow: the window that lets the user know what work is being done
                  and does all the pdf splitting and so forth.

    -----------------------------------------
    |                                       |
    | spce | arrow | Text | check/x | space |
    | spce | arrow | Text | check/x | space |
    | spce | arrow | Text | check/x | space |
    | spce | arrow | Text | check/x | space |
    |                                       |
    |              |DONE|                   |
    -----------------------------------------
    """

    def __init__(self, parent):
        # Initially passing off the PdfFileReader object to this class
        # self.le_pdf = pdf
        # Followed by setting up the UI
        self.parent = parent
        wx.Frame.__init__(self, parent=wx.GetApp().TopWindow, id=wx.ID_ANY,
            style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLIP_CHILDREN|
            wx.FRAME_NO_TASKBAR|wx.FRAME_FLOAT_ON_PARENT,
            size=(300,110)
        )
        self.panel = wx.Panel(self)

        # Some basic time savers
        self.rows = parent.splitters
        self.le_splitters = []

        # Layout
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add((0,10))

        # 1) Verify input
        self.hb_verify = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_verify.Add(wx.StaticText(self.panel, label=unichr(ord(u'\u27A4')), style=wx.ALIGN_RIGHT), proportion=1)
        self.hb_verify.Add(wx.StaticText(self.panel, label="Verifying input...", style=wx.ALIGN_LEFT), proportion=3)
        self.hb_verify.Add(wx.StaticText(self.panel, label="", style=wx.ALIGN_LEFT), proportion=3)
        self.vbox.Add(self.hb_verify, proportion=0, flag=wx.GROW)
        self.hb_verify.ShowItems(False)

        # 2) Analyze input
        self.hb_analyze = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_analyze.Add(wx.StaticText(self.panel, label=unichr(ord(u'\u27A4')), style=wx.ALIGN_RIGHT), proportion=1)
        self.hb_analyze.Add(wx.StaticText(self.panel, label="Analyzing input...", style=wx.ALIGN_LEFT), proportion=3)
        self.hb_analyze.Add(wx.StaticText(self.panel, label="", style=wx.ALIGN_LEFT), proportion=3)
        self.vbox.Add(self.hb_analyze, proportion=0, flag=wx.GROW)
        self.hb_analyze.ShowItems(False)

        """
        for new_row in range(0, self.rows):
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            hbox.Add(wx.StaticText(self.panel, label=unichr(ord(u'\u27A4')), style=wx.ALIGN_RIGHT), proportion=1)
            hbox.Add(wx.StaticText(self.panel,
                    label="Generating " + parent.get_splitter(new_row).cmb_prefix.GetValue() + " documents...",
                    style=wx.ALIGN_LEFT),
                proportion=3
            )
            hbox.Add(wx.StaticText(self.panel, label="", style=wx.ALIGN_LEFT), proportion=3)
            self.vbox.Add(hbox, proportion=0, flag=wx.GROW)
            hbox.ShowItems(False)
            size = self.GetSize()
            self.SetSize((size.x, size.y+10))
        """
        #self.vbox.Add(wx.Button(self.panel, label="Close"), proportion=0, flag=wx.GROW)
        self.SetSize((self.GetSize().x, self.GetSize().y+(10*self.rows)))

        self.panel.SetSizer(self.vbox)
        self.panel.Layout()

    def process(self):
        """
        Verify
        Analyze
        Generate
        Done
        """

        # Begin by analyzing (or creating a list of splitpanels to work with
        self.hb_verify.ShowItems(True)
        # Redraw
        self.panel.Layout()

        if not self.verify_input():
            self.Destroy()
            return (False, "Failed to Verify")
        else:
            self.helper_gray(self.hb_verify)
            self.hb_verify.GetItem(2).GetWindow().SetLabel("Success!")

        # Redraw
        self.hb_analyze.ShowItems(True)
        self.panel.Layout()

        if not self.analyze_input():
            self.Destroy()
            return (False, "Failed to Analyze")
        else:
            # Ugh, magic numbers...
            # 2: "Success!"
            self.helper_gray(self.hb_analyze)
            self.hb_analyze.GetItem(2).GetWindow().SetLabel("Success!")

        # Redraw
        self.panel.Layout()

    def verify_input(self):
        """
        Generate a list of the splitpanels for ease of use
        """
        for k,v in enumerate(self.parent.shell_grid.GetChildren()):
            if k >= self.parent.SPLITTER_START_POS and k < len(self.parent.shell_grid.GetChildren())-1:
                window = v.GetWindow()
                # Check for whites
                if (window.ent_path.GetValue() == "" or
                    window.ent_split_rules.GetValue() == ""):
                    # Temp hack, because I can.
                    self.hb_verify.GetItem(2).GetWindow().SetLabel("FAILED!")
                    self.hb_verify.GetItem(2).GetWindow().SetForegroundColour("Red")
                    self.panel.Layout()
                    wx.MessageBox("Please fill out all fields before splitting.",
                        "info", wx.OK|wx.ICON_INFORMATION)
                    return False
                self.le_splitters.append(window)
        return True

    def analyze_input(self):
        # Should always have analyzed before verify
        if not self.le_splitters:
            wx.MessageBox("Verify should be ran first!", "Error", wx.OK|wx.ICON_ERROR)
            return False

        for k,section in enumerate(self.le_splitters):
            # Verify output path
            if not os.path.isdir(os.path.join(section.ent_path.GetValue())):
                wx.MessageBox(section.ent_path.GetValue() + " is not a valid path!", "Error", wx.OK|wx.ICON_ERROR)
                return False

            if not section.ent_split_rules.GetBackgroundColour() <> (255,192,203):
                wx.MessageBox("Your split rules \"" + section.ent_split_rules.GetValue() + "\" are not valid!", "Error", wx.OK|wx.ICON_ERROR)
                return False

        return True

    def helper_gray(self, sizer):
        for child in sizer.GetChildren():
            child.GetWindow().SetForegroundColour('Gray')

if __name__ == '__main__':
    print "Not a standalone module"
    exit(0)
