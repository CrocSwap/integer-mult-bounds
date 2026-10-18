import sys,json,gzip,copy,importlib.util,math,os
from pathlib import Path
BASE=Path(os.environ['SOURCE_PARTNER_SEARCH_WORK']).resolve()
def mod(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
