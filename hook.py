#!/usr/bin/env python

from ycmd.completers.tex.tex_completer import TexCompleter

def GetCompleter( user_options ):
    return TexCompleter( user_options )

