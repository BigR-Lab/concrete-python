#!/bin/bash
pdoc --html --overwrite concrete.util
pdoc --html --overwrite concrete.validate
python pdoc_whitelisted_submodules.py concrete.util concrete.validate > concrete/index.html

rm -rf util
mv concrete/* .
rmdir concrete
