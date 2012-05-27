import wx
from splitpanel import SplitPanel

class PDFSplit(wx.Frame):

    VERSION = "1.0.3beta"
    TITLE = "PDFSplit " + VERSION
    splitters = []

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title=self.TITLE, size=(700,175))
        self.panel = wx.Panel(self)
        self.shell_grid = wx.BoxSizer(wx.VERTICAL)
        self.shell_grid.Add((10,10))

        # File Menu
        filemenu = wx.Menu()
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", "Close " + self.TITLE)

        # Help Menu
        helpmenu = wx.Menu()
        helpmenu.Append(-1, "Manual", "Coming Soon!")
        helpmenu.AppendSeparator()
        helpmenu.Append(-1, "License", "3 Clause BSD")
        menuExit = helpmenu.Append(wx.ID_ABOUT, "&About", "About " + self.TITLE)

        # Put the menu together
        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        menubar.Append(helpmenu, "&Help")
        self.SetMenuBar(menubar)

        # Bind Events
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.setup_layout()
        self.panel.SetSizer(self.shell_grid)
        self.panel.Layout()
        self.Show()

    def setup_layout(self):
        # For the default layout I would like to have the path of the PDF
        # that is being split, the output path for the split pages, and one
        # section for splitting.

        # First row, the input pdf and output folder
        pdf_box = wx.BoxSizer(wx.VERTICAL)
        pdf_in = wx.BoxSizer(wx.HORIZONTAL)

        # Input PDF layout (yes, it's a lot...)
        self.ent_pdf_in = wx.TextCtrl(self.panel)
        lbl_pdf_in = wx.StaticText(self.panel, label="PDF: ")
        self.btn_pdf_in = wx.Button(self.panel, label="Browse")
        pdf_in.Add(lbl_pdf_in, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        pdf_in.Add(self.ent_pdf_in, proportion=1, flag=wx.GROW)
        pdf_in.Add(self.btn_pdf_in, proportion=0)

        # Putting the path details together.
        pdf_box.Add(pdf_in, proportion=0, flag=wx.GROW)
        self.shell_grid.Add(pdf_box, proportion=0, flag=wx.GROW)

        # Here is the first row of PDF splitting rules.
        self.splitters.append(SplitPanel(self, wx.ID_ANY))
        self.shell_grid.Add(self.splitters[0], proportion=0, flag=wx.GROW)

        # (Temporary) Button to initiate splitting.
        self.btn_split = wx.Button(self.panel, label="Split", id=32)
        self.shell_grid.Add(self.btn_split, proportion=0, flag=wx.GROW)

    def OnExit(self):
        self.Close(True)

    def OnAdd(self, event):
        win_size = self.GetSize()
        t = SplitPanel(self, wx.ID_ANY)
        self.shell_grid.Insert(len(self.shell_grid.Children) - 1, t,
            proportion=0, flag=wx.GROW)
        self.panel.Layout()
        self.SetSize((win_size.x, win_size.y + self.splitters[-1].GetSize().y))

pdfs = wx.App(False)
frame = PDFSplit(None)
pdfs.MainLoop()
