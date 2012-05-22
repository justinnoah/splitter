import wx
from splitpanel import SplitPanel

class PDFSplit(wx.Frame):

    VERSION = "1.0beta"
    TITLE = "PDFSplit " + VERSION

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title=self.TITLE, size=(500,310))
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
        # First row, the input pdf and output folder
        pdf_box = wx.BoxSizer(wx.VERTICAL)
        pdf_in = wx.BoxSizer(wx.HORIZONTAL)
        pdf_out = wx.BoxSizer(wx.HORIZONTAL)
        
        # Now the Label, TextCtrl and Buttons for this top group
        lbl_pdf_in = wx.StaticText(self.panel, label="PDF: ")
        self.ent_pdf_in = wx.TextCtrl(self.panel)
        self.btn_pdf_in = wx.Button(self.panel, label="Browse")
        pdf_in.Add(lbl_pdf_in, proportion=0, flag=wx.GROW)
        pdf_in.Add(self.ent_pdf_in, proportion=1, flag=wx.GROW)
        pdf_in.Add(self.btn_pdf_in, proportion=0, flag=wx.GROW)
        
        lbl_pdf_out = wx.StaticText(self.panel, label="Output Folder: ")
        self.ent_pdf_out = wx.TextCtrl(self.panel)
        self.btn_pdf_out = wx.Button(self.panel, label="Browse")
        pdf_out.Add(lbl_pdf_out, proportion=0, flag=wx.GROW)
        pdf_out.Add(self.ent_pdf_out, proportion=1, flag=wx.GROW)
        pdf_out.Add(self.btn_pdf_out, proportion=0, flag=wx.GROW)
        
        pdf_box.Add(pdf_in, proportion=0, flag=wx.GROW)
        pdf_box.Add(pdf_out, proportion=0, flag=wx.GROW)
        
        self.shell_grid.Add(pdf_box, proportion=0, flag=wx.GROW)
        
        self.first = SplitPanel(self.panel, wx.ID_ANY)
        self.shell_grid.Add(self.first, proportion=0, flag=wx.GROW)
        self.second = SplitPanel(self.panel, wx.ID_ANY)
        self.shell_grid.Add(self.second, proportion=0, flag=wx.GROW)
        self.third = SplitPanel(self.panel, wx.ID_ANY)
        self.shell_grid.Add(self.third, proportion=0, flag=wx.GROW)
        self.shell_grid.Add(wx.Button(self.panel, label="Split"), proportion=0, flag=wx.GROW)

    def OnExit(self):
        self.Close(True)

pdfs = wx.App(False)
frame = PDFSplit(None)
pdfs.MainLoop()
