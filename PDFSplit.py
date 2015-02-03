import os
import sys
import subprocess
import random
from shutil import rmtree
from tempfile import mkdtemp

import wx
from twisted.internet import wxreactor, threads
wxreactor.install()
from twisted.internet import reactor
from splitpanel import SplitPanel
from workerwindow import WorkerWindow

class PDFSplit(wx.Frame):

    VERSION = "1.5"
    TITLE = "PDFSplit " + VERSION
    splitters = 0
    SPLITTER_START_POS = 2
    SPLITTER_END_POS = 3
    temp_paths = []

    def __init__(self, parent):
        self.page_count = 0

        # I need to know where I am...
        if hasattr(sys, "frozen"):
            self.app_path = os.path.dirname(os.path.abspath(sys.executable))
            self.extract_path = sys._MEIPASS
        else:
            self.app_path = os.path.dirname(os.path.abspath(__file__))
            self.extract_path = self.app_path

        # le_pdf is the pdf to be split up
        self.le_pdf = None
        self.frame = wx.Frame.__init__(
            self, parent,
            title=self.TITLE,
            size=(705,150),
            style=wx.MINIMIZE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|
                wx.CLOSE_BOX|wx.CLIP_CHILDREN
        )

        self.panel = wx.Panel(self)
        self.shell_grid = wx.BoxSizer(wx.VERTICAL)
        self.shell_grid.Add((0,5))

        # File Menu
        filemenu = wx.Menu()
        self.menuAdd = filemenu.Append(
            id=wx.ID_ANY, text="&Add Section\tALT-A"
        )
        self.menuRemove = filemenu.Append(
            id=wx.ID_ANY, text="&Remove Section\tALT-D"
        )
        self.menuRemove.Enable(False)
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(
            wx.ID_EXIT, "E&xit\tALT-F4", "Close " + self.TITLE
        )

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

        # Bind the close event
        self.Bind(wx.EVT_CLOSE, self.OnExit)

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
        pdf_in.Add((10,0))
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
        self.panel.GetTopLevelParent().Hide()
        os.chdir(self.app_path)

        for path in self.temp_paths:
            rmtree(path)

        self.Destroy()

    def OnAdd(self, event):
        win_size = self.GetSize()
        t = SplitPanel(self, wx.ID_ANY)

        if event:
            max = len(self.shell_grid.GetChildren())
            prev = self.shell_grid.GetItem(max - self.SPLITTER_END_POS).GetWindow()
            t.ent_path.SetValue(prev.ent_path.GetValue())

        self.shell_grid.Insert(
            len(self.shell_grid.Children) - 2, t, proportion=0, flag=wx.GROW
        )
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
        choice = False
        children = self.shell_grid.GetChildren()

        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            dlg = wx.MessageDialog(
                None,
                "Are you sure you want to remove this section?",
                'Question',
                wx.YES_NO|wx.NO_DEFAULT
            )
            if self.splitters > 1 and dlg.ShowModal() == wx.ID_YES:
                choice = True
                self.splitters -= 1
                event.GetEventObject().GetParent().Destroy()

        # 10014 is a menu clicked event type. Can't find the correct wx.wx????
        # event type that matches 10014
        elif event.GetEventType() == 10014:
            dlg = wx.MessageDialog(
                None,
                "Are you sure you want to remove the last section?",
                'Question',
                wx.YES_NO|wx.NO_DEFAULT
            )
            if self.splitters > 1 and dlg.ShowModal() == wx.ID_YES:
                choice = True
                self.splitters -= 1
                children[len(children)-self.SPLITTER_END_POS].GetWindow().Destroy()

        if choice:
            win_size = self.GetSize()
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
                wx.MessageBox(
                    "Document is not detected as Adobe PDF.",
                    'info', wx.INFO|wx.ICON_INFO
                )

            # Burst the PDF and get some info
            d = threads.deferToThread(self.burst)
            d.addCallback(self.bursted, path)
            d.addErrback(self.failed_burst)
        dlg.Destroy()

    def failed_burst(self, *args, **kwa):
        self.ent_pdf_in.SetDefaultStyle(self.ent_pdf_in.GetDefaultStyle())
        self.ent_pdf_in.SetWindowStyleFlag(wx.TE_LEFT)
        self.ent_pdf_in.SetValue(
            "There was an error loading the PDF you selected."
        )
        self.ent_pdf_in.SetBackgroundColour((255,192,203))

    def bursted(self, d, path):
        # Reset the textbox's settings and set it's value as the path
        self.ent_pdf_in.SetDefaultStyle(self.ent_pdf_in.GetDefaultStyle())
        self.ent_pdf_in.SetWindowStyleFlag(wx.TE_LEFT)
        self.ent_pdf_in.SetValue(path)
        self.ent_pdf_in.SetBackgroundColour(wx.WHITE)

    def burst(self):
        self.panel.Layout()
        if self.le_pdf:
            self.pdf_path = os.path.abspath(self.le_pdf.name)
            temp_path = mkdtemp()
            os.chdir(temp_path)
            self.pdftk_path = os.path.join(
                self.extract_path, "bin", "pdftk.exe"
            )
            self.temp_paths.append(temp_path)
            if os.path.exists(self.pdftk_path):
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
                call = [
                    self.pdftk_path, os.path.abspath(self.le_pdf.name), "burst"
                ]
                if not subprocess.check_call(call, startupinfo=info):
                    os.remove(os.path.join(temp_path, "doc_data.txt"))
                    self.page_list = os.listdir(temp_path)
                    self.page_count = len(self.page_list)
            else:
                wx.MessageDialog(
                    "Unable to locate pdftk. PDFSplit may be corrupted.",
                    'error', wx.OK|wx.ICON_ERROR
                )

    def OnSplit(self, event):
        if self.le_pdf:
            worker = WorkerWindow(self)
            worker.Show()
            worker.process()
        else:
            wx.MessageBox(
                "Before continuing, please give the path of a PDF to split.",
                'info', wx.OK|wx.ICON_INFORMATION
            )


pdfs = wx.App(False)
frame = PDFSplit(None)
reactor.registerWxApp(pdfs)
reactor.run()
