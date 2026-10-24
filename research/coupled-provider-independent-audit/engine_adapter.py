#!/usr/bin/env python3
"""Execute authenticated unchanged engines without loading bytecode or stripping asserts."""
import sys
if not sys.flags.isolated:
    import posix
    posix.execv(sys.executable,[sys.executable,'-I',*(['-O']*sys.flags.optimize),'-B',*sys.argv])
import importlib.abc
import importlib.machinery
from pathlib import Path
import os
sys.dont_write_bytecode=True
root=Path(sys.argv[1]).resolve()
engine=(root/sys.argv[2]).resolve()
if not engine.is_relative_to(root):raise ValueError('Engine outside private scratch')
class SourceOnly(importlib.machinery.SourceFileLoader):
    def get_code(self, fullname):
        raw=self.get_data(self.path)
        return compile(raw,self.path,'exec',dont_inherit=True,optimize=0)
class LocalFinder(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        spec=importlib.machinery.PathFinder.find_spec(fullname,path,target)
        if spec and spec.origin and spec.origin.endswith('.py') and Path(spec.origin).resolve().is_relative_to(root):
            spec.loader=SourceOnly(fullname,spec.origin)
        return spec
sys.meta_path.insert(0,LocalFinder())
sys.path.insert(0,str(engine.parent))
sys.argv=[str(engine),*sys.argv[3:]]
os.chdir(root)
raw=engine.read_bytes()
exec(compile(raw,str(engine),'exec',dont_inherit=True,optimize=0),{'__name__':'__main__','__file__':str(engine)})
