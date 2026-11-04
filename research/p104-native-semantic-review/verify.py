"""Read-only companion entry point; preserves the exact sealed evidence."""
from pathlib import Path
import importlib.util
import sys

HERE=Path(__file__).resolve().parent/'evidence'

def load(name):
    spec=importlib.util.spec_from_file_location('companion_'+name,HERE/(name+'.py'))
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module

if __name__=='__main__':
    load('verify_files').run()
    load('verify').run()
