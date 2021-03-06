"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['manpassc.py']
DATA_FILES = ["manpassc.ico","manpassd","py.dat",]
OPTIONS = {'argv_emulation': True, 'packages': 'nacl,M2Crypto,PIL,qrcode',
           'iconfile':'manpassc.icns',		
		}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
