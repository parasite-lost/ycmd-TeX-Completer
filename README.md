# YouCompleteMe LaTeX Completer Plugin
## What does it do?
Extension for the vim plugin YouCompleteMe (https://github.com/Valloric/YouCompleteMe) adding LaTeX autocompletion suggestions when typing one of

```
  \ref{
  \autoref{
  \cite{
```
in vim's insert buffer while editing a LaTeX file. When typing ``\cite{`` suggestions from your ``*.bib`` files are loaded, otherwise labels from ``\label{...}`` commands in your ``*.tex`` files. For ``\cite``ations the values of the author and title fields in the BIBtex entry are displayed in the preview window (after successful completion the preview window is closed, YouCompleteMe setting)

## How to install?

Assuming YouCompleteMe is installed to
```
$VIM/bundle/YouCompleteMe
```
otherwise adjust the following path accordingly.
```
cd $VIM/bundle/YouCompleteMe/third_party/ycmd/ycmd/completers/
git clone https://github.com/parasite/ycmd-TeX-Completer.git tex
```

EDIT: The following optional modification is already present in the current version of YCMD
__Optional__: If you want labels of the form ``lem:MyLemma`` or ``lemma-42`` to work you need to adjust the symbols YouCompleteMe accepts as part of keywords (these are recognized substrings that can be completed):
```
vim $VIM/bundle/YouCompleteMe/third_party/ycmd/ycmd/identifier_utils.py
```
Find the variable
```
FILETYPE_TO_IDENTIFIER_REGEX = {
  ...
  'haskell': re.compile( r"[_a-zA-Z][\w']*", re.UNICODE ),
}
```
and add the following line before the closing ``}``:
```
  'tex': re.compile( r"[\w:-]+", re.UNICODE ),
```

Now vim still needs to know when to do all this magic stuff:
```
vim $VIM/ftplugin/tex.vim
```
and add the following lines
```
let g:tex_isk='48-57,a-z,A-Z,192-255,:'
let g:ycm_semantic_triggers={
  \ 'tex' : ['\ref{', '\cref{', '\Cref{', '\autoref{', '\cite{'],
  \ }
let g:ycm_autoclose_preview_window_after_completion = 1
```
Documentation for the latter two can be found at https://github.com/Valloric/YouCompleteMe

# Other tips:
This completion plugin does not magically find out where your document root is. So if your ``*.tex`` and ``*.bib`` are distributed over several directories with the ``main.tex`` in the root directory, make sure you stay in that directory. Otherwise not all labels and ``*.bib`` files will be found. This plugin searches for files recursively starting at ``cwd`` as root directory.
