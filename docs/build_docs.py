import os, sys
# Use this script to build the documentation for the project.
# All the necessary will be installed.
# do not move this file from the docs/source directory, 
# if you do, you will have to change commands in this file.

os.chdir("./source")




# if requirnments are not installed, install them
try:
    import pygame
except:
    os.system('pip install pygame')

try:
    import OpenGL
except:
    os.system('pip install pyOpenGL')


## install sphinx and sphinx_rtd_theme
os.system('pip install sphinx sphinx_rtd_theme')


## apidoc
## remove all rst files in the source directory except index.rst
for file in os.listdir():
    if file.endswith(".rst") and file != "index.rst":
        os.remove(file)
        
os.system('sphinx-apidoc -o . ../../')


## run sphinx-build to generate docs
os.system('sphinx-build -b html . ..')