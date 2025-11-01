from distutils.core import setup

import py2exe
import glob

setup(
    # this is the file that is run when you start the game from the command line.
    console=["src\\main.py"],
    # data files - these are the non-python files, like images and sounds
    data_files=[
        ("sfx", glob.glob("sfx\\*.wav")),
        ("fonts", glob.glob("fonts\\*.otf")),
    ],
)
