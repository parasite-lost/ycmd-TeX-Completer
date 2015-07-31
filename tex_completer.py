#!/usr/bin/env python

# adaption of https://github.com/bjoernd/vim-ycm-tex

"""
Note:
    for ':' to be recognized as part of a label you need to add a custom identifier regex
    for tex files in:
       ./../../identifier_utils.py
    regex to append:
        # latex labels with ':'
        'tex': re.compile( r"[\w:-]+", re.UNICODE ),

"""

import re
import subprocess
import shlex
import glob
import logging
from enum import Enum

from ycmd.completers.completer import Completer
from ycmd import responses

LOG = logging.getLogger(__name__)

class TexCompleter( Completer ):
    """
    Completer for LaTeX that takes into account BibTex entries
    for completion.
    """

    # LaTeX query types we are going to see
    class TexComplete(Enum):
        nothing = 0
        bib     = 1
        label  = 2

    def __init__( self, user_options ):
        super( TexCompleter, self ).__init__( user_options )
        self.complete_target = self.TexComplete.nothing


    def DebugInfo( self, request_data ):
        return "TeX completer %s" % self.complete_target


    def ShouldUseNowInner( self, request_data ):
        """
        Used by YCM to determine if we want to be called for the
        current buffer state.
        """

        # we only want to be called for \cite{} and \ref{} completions,
        # otherwise the default completer will be just fine

        line = request_data["line_value"]
        col  = request_data["start_column"]
        LOG.debug('"%s"' % line)
        LOG.debug("'%s'" % line[col-5:col])

        if (line[col-6:col] == r'\cite{'):
            self.complete_target = self.TexComplete.bib
            LOG.debug("complete target %s" % self.complete_target)
            return True

        if (line[col-5:col] == r'\ref{')  or \
           (line[col-6:col] == r'\vref{'):
            self.complete_target = self.TexComplete.label
            LOG.debug("complete target %s" % self.complete_target)
            return True

        return super( TexCompleter, self ).ShouldUseNowInner( request_data )


    def SupportedFiletypes( self ):
        """
        Determines which vim filetypes we support
        """
        return ['plaintex', 'tex']


    def _FindBibEntries(self):
        """
        Find BIBtex entries.

        I'm currently assuming, that Bib entries have the format
        ^@<articletype> {<ID>,
            <bibtex properties>
            [..]
        }

        Hence, to find IDs for completion, I scan for lines starting
        with an @ character and extract the ID from there.

        The search is done by a shell pipe:
            cat *.bib | grep ^@ | grep -v @string
        """
        bibs = " ".join(glob.glob("*.bib"))
        cat_process  = subprocess.Popen(shlex.split("cat %s" % bibs),
                                        stdout=subprocess.PIPE)
        grep_process = subprocess.Popen(shlex.split("grep ^@"),
                                        stdin=cat_process.stdout,
                                        stdout=subprocess.PIPE)
        cat_process.stdout.close()
        grep2_process = subprocess.Popen(shlex.split("grep -vi @string"),
                                         stdin=grep_process.stdout,
                                         stdout=subprocess.PIPE)
        grep_process.stdout.close()

        lines = grep2_process.communicate()[0]

        ret = []
        for l in lines.split("\n"):
            ret.append(responses.BuildCompletionData(
                    re.sub(r"@([A-Za-z]*)\s*{\s*([^,]*),.*", r"\2", l)
                )
            )
        return ret


    def _FindLabels(self):
        """
        Find LaTeX labels for \ref{} completion.

        This time we scan through all .tex files in the current
        directory and extract the content of all \label{} commands
        as sources for completion.
        """
        grep_process = subprocess.Popen(shlex.split(r"grep -r --include='*.tex' \\\\label ."),
                                        stdout=subprocess.PIPE)

        lines = grep_process.communicate()[0]

        ret = []
        for label in lines.split("\n"):
            """
                BuildCompletionData(
                    insertion_text  : text to insert into buffer
                    menu_text       : menu text
                    extra_menu_info : menu info
                    kind            : kind name (??)
                    detailed_info   : detailed info for Preview Window
                    extra_data      : extra data (??)
            """
            ret.append(responses.BuildCompletionData(
                re.sub(r".*\label{([^}]*)}.*", r"\1", label)
                )
            )

        return ret


    def ComputeCandidatesInner( self, request_data ):
        """
        Worker function executed by the asynchronous
        completion thread.
        """
        LOG.debug("compute candidates %s" % self.complete_target)
        if self.complete_target == self.TexComplete.label:
            return self._FindLabels()
        if self.complete_target == self.TexComplete.bib:
            return self._FindBibEntries()

        self.complete_target = self.TexComplete.nothing

        return self._FindLabels() + self._FindBibEntries()
