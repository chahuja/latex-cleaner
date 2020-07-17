'''
# Latex Cleaner

Usage
-----
python latex_cleaner.py -main <path2mainfile> -dest <path2destination_directory> -ext <list of extensions to be copied as is>

Note: -dest or destination directory is relative to the directory in which the main file exists. By default a directory named tex_cleaned will be created inside your latex directory.

Example 
-------
python latex_cleaner.py -main tex/file1.tex -dest tex_cleaned

Files that are commented out in text or not called in text are not copied
'''


import os
import warnings
import shutil
import re
import argparse
from pathlib import Path
import glob
import sys
import subprocess
import pdb

def find_snippets(path2file):
  '''
  Finds a snippet given in a regex format. 
  infers the filename by adding .tex to the end if needed
  Makes sure that the snippet was not commented out (both % and \begin{comment} and \end{comment})
  '''

  with open(path2file) as f:
    strings = f.readlines()
  
  fig_re = re.compile('includegraphics[\s]*(\[.*\])*[\s]*{(?P<filename>[^{}]*)}')
  input_re = re.compile('input[\s]*{(?P<filename>[^{}]*)}')
  comment_re = re.compile('(?P<comment>%)')
  comment_S_re = re.compile('(?P<comment>begin[\s]*{comment})')
  comment_E_re = re.compile('(?P<comment>end[\s]*{comment})')
  big_comment_flag = 0
  tex_files = []
  fig_files = []

  for line in strings:
    #if line == 
    m = comment_re.search(line)
    if m is not None:
      line = line[:m.span('comment')[0]]

    m = comment_E_re.search(line)
    if m is not None:
      if big_comment_flag != 2:
        warnings.warn('missing `\\begin{comment}`')
      line = line[m.span('comment')[1]+1:]
      big_comment_flag = 0

    m = comment_S_re.search(line)
    if m is not None:
      line = line[:m.span('comment')[0]]
      big_comment_flag += 1    

    if big_comment_flag < 2:
      m = input_re.finditer(line)
      filenames = [x.group('filename') for x in m]
      filenames = [filename + '.tex' if filename.split('.')[-1] != 'tex' else filename for filename in filenames]
      tex_files += filenames

      m = fig_re.finditer(line)
      filenames = [x.group('filename') for x in m]
      fig_files += filenames 

    if big_comment_flag == 1:
      big_comment_flag += 1
  if big_comment_flag !=0:
    warnings.warn('missing `\\end{comment}`')
  return tex_files, fig_files

def copy_files(main_file, dest_directory):
  dest_file = Path(main_file).relative_to(Path(dest_directory).parent)
  dest_file = Path(dest_directory)/dest_file
  os.makedirs(dest_file.parent, exist_ok=True)
  try:
    shutil.copy(Path(main_file), dest_file)
  except:
    warnings.warn('{} not found'.format(main_file))

def latex_cleaner(main_file, dest_directory):
  ## copy file to the destination directory
  copy_files(main_file, dest_directory)
  
  ## parse through main file to find `\includegraphics{}`
  ## and `\input{*}` snippets
  if not os.path.isfile(main_file):
    warnings.warn('`{}` not found'.format(main_file))
    return 
  tex_files, fig_files = find_snippets(main_file)
  print('{}:{}'.format(main_file, tex_files+fig_files))
  
  ## copy fig_files
  for fig_file in fig_files:
    fig_file = (Path(main_file).parent/Path(fig_file)).as_posix()
    copy_files(fig_file, dest_directory)
  
  ## recursively go into the children files
  for tex_file in tex_files:
    tex_file = (Path(main_file).parent/Path(tex_file)).as_posix()
    latex_cleaner(tex_file, dest_directory)
  ## recursion end clause
  return

def copy_style_files(ext, dest_directory, main_file):
  src_directory = Path(main_file).parent
  for ex in ext:
    files = glob.iglob((src_directory/'*.{}'.format(ex)).as_posix())
    for file in files:
      if os.path.isfile(file):
        shutil.copy(file, Path(dest_directory)/Path(file).name)
        print(file)

def run_latex(main_file, dest_directory):
  # find the path to `latexit`
  path2latexit = (Path(sys.argv[0]).parent/'latexit').resolve().as_posix()
  newpath2dest = (Path(main_file).parent/dest_directory).resolve()

  ## move to the new directory
  os.chdir(newpath2dest)

  ## run latex
  bashCommand = "{} {}".format(path2latexit, Path(main_file).stem)
  subprocess.check_call(bashCommand.split(' '), stdout=sys.stdout, stderr=subprocess.STDOUT)
 
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-main', type=str, help='path to main file')
  parser.add_argument('-dest', type=str, default='tex_cleaned',
                      help='path 2 destination directory')
  parser.add_argument('-ext', type=str, nargs='+', default=['sty', 'cls', 'bst', 'bib', 'clo'],
                      help='extra files to be copied')
  parser.add_argument('-latexit', action='store_true',
                      help='compile newly clreated latex files')

  args = parser.parse_args()
  
  main_file = args.main
  dest_directory= args.dest
  ext = args.ext
  
  dest_directory = (Path(main_file).parent/dest_directory).as_posix()
  os.makedirs(dest_directory, exist_ok=True)
  print('====================')
  print('Cleaning Latex Files')
  print('====================')
  latex_cleaner(main_file, dest_directory)
  print('====================')
  print('Copying Style Files')
  print('====================')
  copy_style_files(ext, dest_directory, main_file)
  print('====================')

  if args.latexit:
    print('====================')
    print('Compiling {}'.format(main_file))
    print('====================')
    run_latex(main_file, dest_directory)
