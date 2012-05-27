import wx
from splitpanel import SplitPanel

# With wxPython (maybe just wxWidgets in general) it's all about the FLOW.

class PDFSplit(wx.Frame):

    VERSION = "1.0.3beta"
    TITLE = "PDFSplit " + VERSION

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title=self.TITLE, size=(700,175))
        self.panel = wx.Panel(self)
        self.shell_grid = wx.BoxSizer(wx.VERTICAL)

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
        lbl_pdf_in = wx.StaticText(self.panel, label="PDF: ")
        self.ent_pdf_in = wx.TextCtrl(self.panel)
        self.btn_pdf_in = wx.Button(self.panel, label="Browse")
        pdf_in.Add(lbl_pdf_in, proportion=0, flag=wx.GROW)
        pdf_in.Add(self.ent_pdf_in, proportion=1, flag=wx.GROW)
        pdf_in.Add(self.btn_pdf_in, proportion=0, flag=wx.GROW)

        # Putting the path details together.
        pdf_box.Add(pdf_in, proportion=0, flag=wx.GROW)
        self.shell_grid.Add(pdf_box, proportion=0, flag=wx.GROW)

        # Here is the first row of PDF splitting rules.
        self.first = SplitPanel(self.panel, wx.ID_ANY)
        self.shell_grid.Add(self.first, proportion=0, flag=wx.GROW)

        # (Temporary) Button to initiate splitting.
        self.shell_grid.Add(wx.Button(self.panel, label="Split"), proportion=0, flag=wx.GROW)

    def OnExit(self):
        self.Close(True)

pdfs = wx.App(False)
frame = PDFSplit(None)
pdfs.MainLoop()