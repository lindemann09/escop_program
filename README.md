# Escop Program

Scripts to make the ESCOP program 2017


Instructions:
* export ConfTool database as csv-files ![Screenshot](picts/conftool_export_options.png)
* specify the correct csv-filename in `make_latex_files.py`
* run `python make_latex_files.py`
* (optinal) edit ``.*tex`` files
* run ``pdflatex program.tex`` and ``makeindex`` for author index
  you need to create a program booklet

See ``escop-demo.tex`` for a demo to create a program booklet.

(c) O. Lindemann, lindemann@cognitive-psychology.eu
