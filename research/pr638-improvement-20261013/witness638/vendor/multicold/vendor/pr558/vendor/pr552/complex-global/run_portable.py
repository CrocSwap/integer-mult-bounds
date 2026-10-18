"""Run one retained verifier with UTF-8/LF text outputs on every platform.
This changes output serialization only; no mathematical operation is replaced.
"""
from pathlib import Path
import runpy,sys,gzip
if not __debug__:
    raise RuntimeError('Assertions must remain enabled')
original_write_text=Path.write_text
def write_text_lf(self,data,encoding=None,errors=None,newline=None):
    return original_write_text(self,data,encoding=encoding or 'utf-8',errors=errors,newline='\n')
Path.write_text=write_text_lf
# Pin generated gzip serialization. Python3.11 may expose zlib's platform OS
# byte, Python3.13 normalizes it, and Python3.15 changes the default level.
# Immutable input files are never rewritten by this wrapper.
original_gzip_compress=gzip.compress
def compress_portable(data,compresslevel=9,*,mtime=0):
    raw=original_gzip_compress(data,compresslevel=compresslevel,mtime=mtime)
    assert raw[:3]==b'\x1f\x8b\x08' and len(raw)>=18
    return raw[:9]+b'\xff'+raw[10:]
gzip.compress=compress_portable
script=Path(sys.argv[1]).resolve()
sys.argv=sys.argv[1:]
sys.path.insert(0,str(script.parent))
runpy.run_path(str(script),run_name='__main__')
