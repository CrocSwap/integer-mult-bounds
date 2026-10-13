"""Run one retained verifier with UTF-8/LF text outputs on every platform.
This changes output serialization only; no mathematical operation is replaced.
"""
from pathlib import Path
import runpy,sys
if not __debug__:
    raise RuntimeError('Assertions must remain enabled')
original_write_text=Path.write_text
def write_text_lf(self,data,encoding=None,errors=None,newline=None):
    return original_write_text(self,data,encoding=encoding or 'utf-8',errors=errors,newline='\n')
Path.write_text=write_text_lf
script=Path(sys.argv[1]).resolve()
sys.argv=sys.argv[1:]
sys.path.insert(0,str(script.parent))
runpy.run_path(str(script),run_name='__main__')
