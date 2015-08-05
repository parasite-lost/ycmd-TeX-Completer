#!/usr/bin/env python

"""
    ycmd-TeX-Completer, LaTeX Completion Plugin for YouCompleteMe
    Copyright (C) 2015  Ulrich Dorsch

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

# import the TexCompleter class that extends the Completer class to handle completion requests
from ycmd.completers.tex.tex_completer import TexCompleter

# hook that is called wenn filetype = tex
def GetCompleter( user_options ):
    return TexCompleter( user_options )
