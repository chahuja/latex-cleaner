# Latex Cleaner

Clean your latex repositories to the files you really need.

Let's say you have a directory structure as follows where RHS indicates the files LHS is dependent on:

```
tex/
  file1.tex -> file2.tex, file7.tex, file8.tex # file1.tex takes input from 3 files
  file2.tex -> chapter/file7.tex, file3.tex, figs/file1.png
  file3.tex
  file4.tex # commented out in text
  file5.tex # commented out in text
  file6.tex # not called in text
  file7.tex
  file8.tex
  chapter/
    file7.tex -> figs/file2.png
  figs/
    file1.png
    file2.png
```
If `file1.tex` is the main file, and assuming the directory structure is a tree with `file1.tex` at the root node, we can find out the relevant files you would finally need for compiling a pdf file (extremely useful for preparing camera ready versions of your paper!!!).

A couple of things this program is able to handle well,

- finds the relevant tex files (imported using `\input{}`) as well as figures (only imported using `\includegraphics[]{}`) and copies them to a separate directory.
- handles 2 kinds of comments well: (a) single line comments `%` and (b) multiline comments `\begin{comment} ... \end{comment}`
- copies all style and bib files for now. maybe future work would detect the required files before copying. Specifically, extensions ['sty', 'cls', 'bst', 'bib', 'clo'] are all copied by default

Requirements
------------
- pathlib

Usage
-----
```
python latex_cleaner.py -main <path2mainfile> -dest <path2destination_directory> -ext <list of extensions to be copied as is> -latexit 
```

### Note
- `-dest` or destination directory is relative to the directory in which the main file exists. By default a directory named tex_cleaned will be created inside your latex directory.
- `-latexit` using latexit will compile the latex files newly created. Remove it from the command line if you want to skip that

Example + UnitTest
-------
```
python latex_cleaner.py -main tex/file1.tex -dest tex_cleaned
```

New Directory Structure

```
tex/
  file1.tex -> file2.tex, file7.tex, file8.tex # file1.tex takes input from 3 files
  file2.tex -> chapter/file7.tex, file3.tex, figs/file1.png
  file3.tex
  file7.tex
  file8.tex
  chapter/
    file7.tex -> figs/file2.png
  figs/
    file1.png
    file2.png
```
	
Files that are commented out in text or not called in text are not copied.

