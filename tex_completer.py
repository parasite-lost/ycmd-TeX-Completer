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

"""
Credits for inspriation: https://github.com/bjoernd/vim-ycm-tex
"""

"""
Place this file as well as the accompanying __init__.py and hook.py to:
    $VIM/bundle/YouCompleteMe/third_party/ycmd/ycmd/completers/tex/

Note:
    for ':' and '-' to be recognized as part of a label
    you need to add a custom identifier regex for tex files in:
       ./../../identifier_utils.py
    regex to append:
        # latex labels with ':'
        'tex': re.compile( r"[\w:-]+", re.UNICODE ),

"""

import re
import os
import fnmatch
import logging

from ycmd.completers.completer import Completer
from ycmd import responses

NO_COMPLETIONS_MESSAGE = 'No completions found; errors in the file?'

_logger = logging.getLogger(__name__)

class TexCompleter( Completer ):
    """
    Completer for LaTeX.

    autocompletes labels when typing
        \\ref{...}
        \\autoref{...}
        \\Cref{...}
        \\cref{..}
    and bibtex labels, providing helpfull display of actual title and author(s) of
    the bibtex entry, when typing
        \\cite{...}
    """

    def __init__( self, user_options ):
        super( TexCompleter, self ).__init__( user_options )


    def SupportedFiletypes( self ):
        return ['tex']


    def _FindBibEntries(self):
        """
        Search for BIBtex files recursively starting at cwd as root directory.

        valid bib entry:
            @<string>{<label>,
                <item> = {...},
                ...
            }
        where <string> is NOT "string", "comment" or "preamble" (.PHONY entries)

        extract label as well as author and title information (required fields)
        for easier selection (in case you don't remember the label correctly.

        author and title will be handed to YouCompleteMe to be displayed in
        vim's preview window.
        """

        # find all .bib files. search recursively
        bib_matches = []
        for root, dirnames, filenames in os.walk('.'):
            for filename in fnmatch.filter(filenames, '*.bib'):
                bib_matches.append(os.path.join(root, filename))

        # regex to find valid bib entries
        # extraction of data:
        # label: bib entry label
        # bibitems: bib entry content
        search_entries = re.compile(r""" #
                ^@ # entry
                (?!string)(?!comment)(?!preamble)   # no .PHONY entries
                [^{]*{                              # entryname -> until {
                (?P<label>[^},]+)                   # entry label
                ,\n                                 # label finished
                (?P<bibitems>(^\s.*\n)*)             # content of entry
                ^}                                  # entry finished
                """, re.IGNORECASE | re.UNICODE | re.MULTILINE | re.VERBOSE)

        # (?:...) non-capturing (..)
        # regex to find the author item in the bib entry body
        search_author = re.compile(r""" # search author = {...} in items
                ^\s*                                # line can start with whitespace
                author                              # author item
                \s*=\s*{                            # value of author
                (?P<authors>.*)                     # anything until last '}' is author
                (?: (?:},$) | (?:}$) )              # end of item, last item doesn't need ','
                """, re.UNICODE | re.IGNORECASE | re.VERBOSE | re.MULTILINE)

        # regex to find the title in the bib entry body
        search_title = re.compile(r""" # search title = {...} in items
                ^\s*                                # line can start with whitespace
                title                               # title item
                \s*=\s*{                            # value of author
                (?P<title>.*)                       # anything until last '}' is title
                (?: (?:},$) | (?:}$) )              # end of item, last item doesn't need ','
                """, re.UNICODE | re.IGNORECASE | re.VERBOSE | re.MULTILINE)

        # accumulate all results from all files
        ret = []
        for bib_match in bib_matches:
            # read each bib file
            bib_file = open(bib_match, 'r')
            content = bib_file.read()
            bib_file.close()
            # find all matches for valid entries
            for match in search_entries.finditer(content):
                # extract label
                label = match.group('label')
                # extract content of bib entry
                bib_items = match.group('bibitems')
                # search items in bib entry for author and title information
                # if not present: broken bib file
                author = "None"
                title = "None"
                try:
                    author = search_author.search(bib_items).group('authors')
                    title = search_title.search(bib_items).group('title')
                except:
                    pass
                # gather all results
                # label will be inserted into vim's buffer
                # detailed_info will be displayed in vim's preview window
                ret.append(
                        responses.BuildCompletionData(
                            insertion_text = label,
                            detailed_info = "{}\n{}".format(author, title)
                        )
                )

        return ret


    def _FindLabels(self):
        """
        Find LaTeX labels for \\ref{} (and similar commands) label-completion.

        search all .tex files recursively starting frmo cwd as root
        """

        # find all '*.tex' files
        tex_matches = []
        for root, dirnames, filenames in os.walk('.'):
            for filename in fnmatch.filter(filenames, '*.tex'):
                tex_matches.append(os.path.join(root, filename))

        # regex for finding labels
        search_label = re.compile(r"""          # search for \label{...} or \label[type]{...}
                    .*\label                    # label definition
                    (?:(?:\[[a-zA-Z0-9-]*\])?)  # optional label type
                    {                           # start label
                    (?P<label>[^}]+)            # label
                    }.*                         # end label
                    """, re.UNICODE | re.VERBOSE)

        # accumulate results from all files
        ret = []
        for tex_match in tex_matches:
            # read out file
            tex_file = open(tex_match, 'r')
            content = tex_file.read()
            tex_file.close()
            # append all matches to ret encapsulated as CompletionData
            for match in search_label.finditer(content):
                ret.append(responses.BuildCompletionData(
                    insertion_text=match.group('label')
                    )
                )

        return ret


    def ComputeCandidatesInner( self, request_data ):
        """
        Worker function executed by the asynchronous
        completion thread.
        """
        line = request_data[ 'line_value' ]
        column = request_data[ 'start_column' ]
        _logger.debug("line: {} :@: column: {}".format(line, column))

        # select correct completion
        if line[column-6:column-1] == r"\ref{" or line[column-7:column-1] == r"\Cref{" or \
                line[column-7:column-1] == r"\cref{" or line[column-10:column-1] == r"\autoref{":
            _logger.debug("looking for labels")
            return self._FindLabels()

        elif line[column-7:column-1] == r"\cite{":
            _logger.debug("looking for bib entries")
            return self._FindBibEntries()

        # no results. try adding \label{...} in your .tex files
        # and bibentries in your .bib files
        else:
            raise RuntimeError( NO_COMPLETIONS_MESSAGE )
