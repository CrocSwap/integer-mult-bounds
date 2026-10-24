"""Authenticate source exports before compiling any predecessor byte."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent


def activate():
    exports=json.loads((HERE/'EXPORTS.json').read_text())['exports']
    for row in exports:
        if sha256((HERE/row['file']).read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('source export drift: '+row['file'])
    for name in ('stack','return_output','adapter','streams','compact'):
        if name in sys.modules:raise ValueError('preloaded source module: '+name)
        path=HERE/'vendor'/ (name+'.py')
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module
        exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return tuple(sys.modules[name] for name in ('stack','return_output','adapter','streams','compact'))
