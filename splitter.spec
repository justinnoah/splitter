# -*- mode: python -*-

block_cipher = None

def Datafiles(*filenames, **kw):
    import os

    def datafile(path, strip_path=True):
        parts = path.split('/')
        path = name = os.path.join(*parts)
        if strip_path:
            name = os.path.basename(path)
        return name, path, 'DATA'

    strip_path = kw.get('strip_path', True)
    return TOC(
        datafile(filename, strip_path=strip_path)
        for filename in filenames
        if os.path.isfile(filename))

pdftk = Datafiles('bin/pdftk.exe', 'bin/libiconv2.dll', strip_path=False)

a = Analysis(['splitter.py'],
             pathex=['c:\\Documents and Settings\\IEUser\\projects\\splitter'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             cipher=block_cipher)

pyz = PYZ(a.pure,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          pdftk,
          name='splitter.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
