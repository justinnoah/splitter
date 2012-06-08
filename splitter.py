import os
import sys
import subprocess
import random
import shutil

import wx
from splitpanel import SplitPanel
from workerwindow import WorkerWindow

class PDFSplit(wx.Frame):

    VERSION = "1.1.1 beta"
    TITLE = "PDFSplit " + VERSION
    splitters = 0
    SPLITTER_START_POS = 2
    SPLITTER_END_POS = 3

    def __init__(self, parent):
        # I need to know where I am...
        if hasattr(sys, "frozen"):
            self.app_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            self.app_path = os.path.dirname(os.path.abspath(__file__))

        # le_pdf is the pdf to be split up
        self.le_pdf = None
        self.frame = wx.Frame.__init__(self, parent,
            title=self.TITLE,
            size=(700,155),
            style=wx.MINIMIZE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|
                wx.CLOSE_BOX|wx.CLIP_CHILDREN)
        self.panel = wx.Panel(self)
        self.shell_grid = wx.BoxSizer(wx.VERTICAL)
        self.shell_grid.Add((10,10))

        # File Menu
        filemenu = wx.Menu()
        self.menuAdd = filemenu.Append(id=wx.ID_ANY, text="&Add Section\tALT-A")
        self.menuRemove = filemenu.Append(id=wx.ID_ANY, text="&Remove Section\tALT-D")
        self.menuRemove.Enable(False)
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit\tALT-F4", "Close " + self.TITLE)

        # Help Menu
        helpmenu = wx.Menu()
        helpmenu.Append(-1, "About", "Coming Soon!")
        helpmenu.AppendSeparator()
        helpmenu.Append(-1, "&License\tCTRL-L", "3 Clause BSD")

        # Put the menu together
        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        menubar.Append(helpmenu, "&Help")
        self.SetMenuBar(menubar)

        # Do the layout
        self.setup_layout()

        # Bind Menu Events
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAdd, self.menuAdd)
        self.Bind(wx.EVT_MENU, self.OnRemove, self.menuRemove)

        # Bind Button Events
        self.Bind(wx.EVT_BUTTON, self.OnBrowseInput, self.btn_pdf_in)
        self.Bind(wx.EVT_BUTTON, self.OnSplit, self.btn_split)

        # Setup the accelerators
        self.setup_accels()

        # Finish up
        self.panel.SetSizer(self.shell_grid)
        self.panel.Layout()
        self.Show()

    def setup_accels(self):
        # Give the user the ability to use ALT+A and ALT+D to add and remove
        # splitter sections.
        self.accel_table = wx.AcceleratorTable([
            (wx.ACCEL_ALT, ord('A'), self.menuAdd.GetId()),
            (wx.ACCEL_ALT, ord('D'), self.menuRemove.GetId()),
        ])
        self.SetAcceleratorTable(self.accel_table)


    def setup_layout(self):
        # For the default layout I would like to have the path of the PDF
        # that is being split, the output path for the split pages, and one
        # section for splitting.

        # First row, the input pdf and output folder
        pdf_box = wx.BoxSizer(wx.VERTICAL)
        pdf_in = wx.BoxSizer(wx.HORIZONTAL)

        # Input PDF layout (yes, it's a lot...)
        self.ent_pdf_in = wx.TextCtrl(self.panel)
        lbl_pdf_in = wx.StaticText(self.panel, label="  Input PDF: ")
        self.btn_pdf_in = wx.Button(self.panel, label="Browse...")
        pdf_in.Add(lbl_pdf_in, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        pdf_in.Add(self.ent_pdf_in, proportion=1, flag=wx.GROW)
        pdf_in.Add(self.btn_pdf_in, proportion=0)

        # Putting the path details together.
        pdf_box.Add(pdf_in, proportion=0, flag=wx.GROW)
        self.shell_grid.Add(pdf_box, proportion=0, flag=wx.GROW)

        # Add some space before the split button
        self.shell_grid.Add((0,10))

        # (Temporary) Button to initiate splitting.
        self.btn_split = wx.Button(self.panel, label="Split")
        self.shell_grid.Add(self.btn_split, proportion=0, flag=wx.ALIGN_CENTER)

        # Give one
        self.OnAdd(None)

    def OnExit(self, event):
        self.Close(True)

    def OnAdd(self, event):
        win_size = self.GetSize()
        t = SplitPanel(self.panel, wx.ID_ANY)
        if event:
            max = len(self.shell_grid.GetChildren())
            prev = self.shell_grid.GetItem(max - self.SPLITTER_END_POS).GetWindow()
            t.ent_path.SetValue(prev.ent_path.GetValue())
        self.shell_grid.Insert(len(self.shell_grid.Children) - 2, t,
            proportion=0, flag=wx.GROW)
        self.panel.Layout()

        # +1 the splitters
        self.splitters += 1
        if self.splitters > 1:
            self.menuRemove.Enable(True)

        # t.GetSize() must be called after self.panel.Layout() to get
        # the correct size.
        self.sHeight = t.GetSize().y
        self.SetSize((win_size.x, win_size.y + self.sHeight))

    def OnRemove(self, event):
        # With Remove, we want to remove one of the splitter sections
        # and shrink the window height.

        # Simplification
        win_size = self.GetSize()
        children = self.shell_grid.GetChildren()

        # if we have more that one split section, destroy the last splitter
        if self.splitters > 1:
            self.splitters -= 1
            children[len(children)-self.SPLITTER_END_POS].GetWindow().Destroy()
            self.shell_grid.Layout()
            self.panel.Layout()
            self.SetSize((win_size.x, win_size.y - self.sHeight))

        # Given 1 or less splitters, disable the remove menu item
        if self.splitters <= 1:
            self.menuRemove.Enable(False)


    def OnBrowseInput(self, event):
        # Now present the user with a file dialog to chose the pdf to split

        # Let the user know work is being done
        self.ent_pdf_in.SetValue("Loading...")
        self.ent_pdf_in.SetWindowStyleFlag(wx.TE_RIGHT)

        # Presenting the dialog box
        dlg = wx.FileDialog(self, message="Open PDF", defaultDir="",
            defaultFile="", wildcard="PDF files (*.pdf)|*.pdf", style=wx.FD_OPEN)

        # If OK, do a bunch of stuff
        if dlg.ShowModal() == wx.ID_OK:
            path = os.path.join(dlg.GetPath())
            self.le_pdf = open(path, "r")
            self.le_pdf.seek(0)

            # If the document's magic number doesn't represent a PDF,
            # we need to let the user know, but continue in case we are wrong
            if self.le_pdf.read(4) <> "%PDF":
                wx.MessageBox("Warning, document is not detected as Adobe PDF. Your mileage may vary.", 'info', wx.INFO|wx.ICON_INFO)

            # Reset the textbox's settings and set it's value as the path
            self.ent_pdf_in.SetDefaultStyle(self.ent_pdf_in.GetDefaultStyle())
            self.ent_pdf_in.SetWindowStyleFlag(wx.TE_LEFT)
            self.ent_pdf_in.SetValue(path)
            self.ent_pdf_in.SetBackgroundColour((192,255,203))

            # Burst the PDF and get some info
            self.burst()
        dlg.Destroy()

    def burst(self):
        if self.le_pdf:
            self.pdf_path = os.path.abspath(self.le_pdf.name)
            self.temp_num = random.randint(1000000,9999999)
            self.temp_dir = "tmp%d" % self.temp_num
            self.temp_path = os.path.join(self.app_path, self.temp_dir)
            os.mkdir(self.temp_path)
            os.chdir(self.temp_path)
            self.pdftk_path = os.path.join(self.app_path, "pdftk", "bin", "pdftk.exe")
            if not subprocess.check_call([self.pdftk_path, os.path.abspath(self.le_pdf.name), "burst"]):
                os.remove(os.path.join(self.temp_path, "doc_data.txt"))
                self.page_list = os.listdir(self.temp_path)
                self.page_count = len(self.page_list)

    def OnSplit(self, event):
        if self.le_pdf:
            worker = WorkerWindow(self)
            worker.Show()
            worker.process()
        else:
            wx.MessageBox("Before continuing, please give a path for the PDF to split.",
                        'info', wx.OK|wx.ICON_INFORMATION)

        # Once processed, clean up the temporary files
        """
        if self.tmp_dir:
            shutil.rmtree(self.tmp_dir, True)
            self.temp_num = None
            self.temp_dir = None
            self.temp_path = None
        """

pdfs = wx.App(False)
frame = PDFSplit(None)
pdfs.MainLoop()
