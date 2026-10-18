"""Run an unchanged verifier with deterministic gzip headers across Python versions.
Python 3.11 delegates mtime=0 compression to zlib, which exposes the platform
OS byte. Pin that metadata byte to 255; compressed payload and proof bytes
are untouched. This changes serialization only, not any mathematical check.
"""
import gzip,runpy,sys
from pathlib import Path
original=gzip.compress
def compress(data,compresslevel=9,*,mtime=0):
    raw=original(data,compresslevel=compresslevel,mtime=mtime)
    return raw[:9]+b'\xff'+raw[10:] if mtime==0 else raw

gzip.compress=compress
sys.argv=sys.argv[1:]
sys.path[0]=str(Path(sys.argv[0]).resolve().parent)
runpy.run_path(sys.argv[0],run_name='__main__')
