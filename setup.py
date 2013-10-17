from distutils.core import setup


import sys
if 'py2exe' in sys.argv: import py2exe
if 'py2app' in sys.argv: import py2app

data_files = [('',['js']),
              ('',['includes']),
              ('',['css']),
              ('',['images'])
              ]

options = {'argv_emulation': False, 'iconfile': 'images/libmapper.icns'}

setup(name='WebMapper',
      version='0.1',
      description='GUI for libmapper OSC network',
      author='Stephen Sinclair, Aaron Krajeski & Jonathan Wilansky',
      author_email='aaron.krajeski@music.mcgill.ca',
      url='http://libmapper.org',
      data_files = data_files,
      options={'py2app': options},
      windows=['webmapper.py'],
      app=['webmapper.py'],
     )
