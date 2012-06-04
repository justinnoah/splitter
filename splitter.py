import os
import wx

from pyPdf import PdfFileReader
from splitpanel import SplitPanel
from splitpdf import Actuator

class PDFSplit(wx.Frame):

    VERSION = "1.0.4beta"
    TITLE = "PDFSplit " + VERSION
    splitters = 0
    SPLITTER_START_POS = 2

    def __init__(self, parent):
        self.le_pdf = ""
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

        # (Temporary) Button to initiate splitting.
        self.btn_split = wx.Button(self.panel, label="Split", id=32)
        self.shell_grid.Add(self.btn_split, proportion=0, flag=wx.GROW)

        # Give one
        self.OnAdd(None)

    def OnExit(self, event):
        if self.le_pdf:
            self.le_pdf.close()
        self.Close(True)

    def OnAdd(self, event):
        win_size = self.GetSize()
        t = SplitPanel(self.panel, wx.ID_ANY)
        self.shell_grid.Insert(len(self.shell_grid.Children) - 1, t,
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
            children[len(children)-2].GetWindow().Destroy()
            self.shell_grid.Layout()
            self.panel.Layout()
            self.SetSize((win_size.x, win_size.y - self.sHeight))

        # Given 1 or less splitters, disable the remove menu item
        if self.splitters <= 1:
            self.menuRemove.Enable(False)


    def OnBrowseInput(self, event):
        # If we have an open file handle, let's close it
        if self.le_pdf:
            self.le_pdf.close()

        # Now present the user with a file dialog to chose the pdf to split
        dlg = wx.FileDialog(self, message="Open PDF", defaultDir="",
            defaultFile="", wildcard="PDF files (*.pdf)|*.pdf", style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.ent_pdf_in.Clear()
            path = os.path.join(dlg.GetPath())
            self.ent_pdf_in.AppendText(path)
            self.le_pdf = open(path)
        dlg.Destroy()

    def OnSplit(self, event):
        if self.le_pdf:
            actuator = Actuator(self)
            actuator.Show()
            actuator.process()

pdfs = wx.App(False)
frame = PDFSplit(None)
pdfs.MainLoop()
