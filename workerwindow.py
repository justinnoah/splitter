import os
import subprocess

import wx

# This class actually does the verification of splitting parameters and the
# writing of the new PDF files.

class WorkerWindow(wx.Dialog):
    """
    WorkerWindow: the window that lets the user know what work is being done
                  and does all the pdf splitting and so forth.

    arrow : unichr(ord(u'\u25BA'))
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
        wx.Dialog.__init__(self, parent=wx.GetApp().TopWindow, id=wx.ID_ANY,
            #style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLIP_CHILDREN|
            #wx.FRAME_NO_TASKBAR|wx.FRAME_FLOAT_ON_PARENT,
            size=(375,110),
            style=wx.DEFAULT_DIALOG_STYLE & ~wx.CLOSE_BOX,
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
        self.hb_verify.Add(wx.StaticText(self.panel, label="", style=wx.ALIGN_RIGHT), proportion=1)
        self.hb_verify.Add(wx.StaticText(self.panel, label="Verifying input", style=wx.ALIGN_LEFT), proportion=3)
        self.hb_verify.Add(wx.StaticText(self.panel, label="", style=wx.ALIGN_LEFT), proportion=2)
        self.vbox.Add(self.hb_verify, proportion=0, flag=wx.GROW)

        # 2) Analyze input
        self.hb_analyze = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_analyze.Add(wx.StaticText(self.panel, label="", style=wx.ALIGN_RIGHT), proportion=1)
        self.hb_analyze.Add(wx.StaticText(self.panel, label="Analyzing input", style=wx.ALIGN_LEFT), proportion=3)
        self.hb_analyze.Add(wx.StaticText(self.panel, label="", style=wx.ALIGN_LEFT), proportion=2)
        self.vbox.Add(self.hb_analyze, proportion=0, flag=wx.GROW)
        self.helper_color(self.hb_analyze, 'Gray')

        # Layout stuff
        size = self.GetSize()
        self.SetSize((self.GetSize().x, self.GetSize().y+(10*(self.rows))))

        # Finish up
        self.panel.SetSizer(self.vbox)
        self.panel.Layout()

    def process(self):
        """
        Verify
        Analyze
        Generate
        Done
        """

        # Begin by verifying input exists
        self.helper_color(self.hb_verify, 'Black')
        self.hb_verify.GetItem(0).GetWindow().SetLabel(">> ")
        self.panel.Layout()
        if not self.verify_input():
            self.Destroy()
            return (False, "Failed to Verify")
        else:
            self.helper_color(self.hb_verify, 'Gray')
            self.hb_verify.GetItem(0).GetWindow().SetLabel("")
            self.hb_verify.GetItem(2).GetWindow().SetLabel("Success!")

        # Redraw
        self.panel.Layout()

        self.helper_color(self.hb_analyze, 'Black')
        self.hb_analyze.GetItem(0).GetWindow().SetLabel(">> ")
        # Redraw
        self.panel.Layout()
        if not self.analyze_input():
            self.Destroy()
            return (False, "Failed to Analyze")
        else:
            # Ugh, magic numbers...
            # 2: "Success!"
            self.helper_color(self.hb_analyze, 'Gray')
            self.hb_analyze.GetItem(0).GetWindow().SetLabel("")
            self.hb_analyze.GetItem(2).GetWindow().SetLabel("Success!")

        # Redraw
        self.panel.Layout()

        # Temporary magic
        self.generate()

        # Done
        self.btn_close.Enable()

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
                hbox = wx.BoxSizer(wx.HORIZONTAL)
                hbox.Add(wx.StaticText(self.panel, label="", style=wx.ALIGN_RIGHT), proportion=1)
                hbox.Add(wx.StaticText(self.panel, label="Generating " + window.cmb_prefix.GetValue() + " documents", style=wx.ALIGN_LEFT), proportion=3)
                hbox.Add(wx.StaticText(self.panel, label="", style=wx.ALIGN_LEFT), proportion=2)
                self.vbox.Add(hbox, proportion=0, flag=wx.GROW)
                self.helper_color(hbox, "Gray")

        # So this is getting really messy and needs to be reconstructed, but in the mean time, here's a random button.
        self.vbox.Add((0,10))
        self.btn_close = wx.Button(self.panel, label="Close")
        self.btn_close.Disable()
        self.vbox.Add(self.btn_close, proportion=0, flag=wx.GROW)
        # Close button binding
        self.Bind(wx.EVT_BUTTON, self.OnClose, self.btn_close)
        self.panel.Layout()
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
                wx.MessageBox("Your split rule \"" + section.ent_split_rules.GetValue() + "\" is not valid!", "Error", wx.OK|wx.ICON_ERROR)
                return False

        return True

    def generate(self):
        # The 3rd item of self.vbox is the first sizer related to document generation
        START = 3
        END = len(self.vbox.GetChildren()) - 2

        # For the time being this method will take over it's parent methods functionality
        # regarding color changing of text to identify to the user the current process.
        for i in range(START, END):
            # First, let the user know what is being worked on
            item_sizer = self.vbox.GetItem(i).GetSizer()
            self.helper_color(item_sizer, 'Black')
            item_sizer.GetItem(0).GetWindow().SetLabel(">> ")

            # Now we grab the splitpanel and start mining the info
            window = self.le_splitters[i-START]
            output_folder = os.path.join(window.ent_path.GetValue())
            splits = str(window.ent_split_rules.GetValue()).replace(',','.').strip('.').split('.')

            pdf = self.parent.le_pdf

            for k,split in enumerate(splits):
                # Terrible, terrible hack, but I am tired and this should be in
                # asap. This WILL be corrected, but deal with it for the time
                # being.
                combine = []
                if '-' in split:
                    resplit = split.split('-')
                    if (int(resplit[0]) or int(split[1])) >= self.parent.page_count:
                        wx.MessageBox("Your range containtains a value larger than the number of pages in the PDF you are generating documents from.", 'error', wx.OK|wx.ICON_ERROR)
                        return False
                    for i in range(int(resplit[0]), int(resplit[1])+1):
                        add = []
                        for f in self.parent.page_list:
                            if str(i) in f:
                                add.append(f)
                        combine.append(sorted(add)[0])
                else:
                    print "SDLSDJLKFSDJ: " + str(int(split))
                    if self.parent.page_count >= int(split):
                        add = []
                        for f in self.parent.page_list:
                            if str(k) in f:
                                add.append(f)
                        combine.append(sorted(add)[0])
                    else:
                        return False
                # File list to be combined has been created, let's create
                # us a PDF.
                files = ""
                cat = ""
                for key,f in enumerate(combine):
                    files += chr(65+key) + "=\"" + os.path.abspath(f) + "\" "
                    cat += chr(65+key) + " "

                if not os.path.isdir(output_folder):
                    os.path.makedirs(output_folder)

                prefix = os.path.join(window.cmb_prefix.GetValue())
                file_name = prefix + str(k) + ".pdf"
                combine_out_path = os.path.join(output_folder, file_name)

                subprocess.check_call(str(self.parent.pdftk_path.replace("\\", "/") + " " + files.replace("\\","/") + " cat " + cat + " output \"" + combine_out_path.replace("\\","/") + "\""))

                #except Exception,e:
                #    print "Error: " + str(e)
                #    wx.MessageBox("Error: " + str(e), 'error', wx.OK|wx.ICON_ERROR)

            self.helper_color(item_sizer, 'Gray')
            item_sizer.GetItem(0).GetWindow().SetLabel("")

        return True

    def helper_color(self, sizer, color):
        for child in sizer.GetChildren():
            child.GetWindow().SetForegroundColour(color)

    def OnClean(self):
        pass

    def OnClose(self, event):
        self.Destroy()
        event.Skip()

if __name__ == '__main__':
    print "Not a standalone module"
    exit(0)
