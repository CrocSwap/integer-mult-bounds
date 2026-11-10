"""Use the unchanged authenticated physical scalar-word cohort.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import contextmanager
import importlib.util
from hashlib import file_digest
import json
from pathlib import Path
import sys
PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parent.parent
PHYSICAL=PACKAGE.parent/'physical-gaussian-core'
@contextmanager
def physical_runtime():
    if 'gaussian_sources' in sys.modules:raise ValueError('cold union-window namespace')
    old=sys.path[:];sys.path[:0]=[str(PHYSICAL),str(PACKAGE),str(PACKAGE/"retained"),str(PACKAGE.parent/"physical-boundary-pages")]
    spec=importlib.util.spec_from_file_location('gaussian_sources',PHYSICAL/'gaussian_sources.py')
    source=importlib.util.module_from_spec(spec);sys.modules['gaussian_sources']=source
    try:
        spec.loader.exec_module(source)
        with source.opened() as state:yield state
    finally:sys.path[:]=old

def need(ok,message):
    if not ok:raise ValueError(message)

def authenticated_inputs():
    manifest=json.loads((PACKAGE/'SOURCES.json').read_text());result={}
    for row in manifest['files']:
        if row['usage']!='input':continue
        path=ROOT/row['path']
        need(path.is_file() and not path.is_symlink(),'regular seven-product source: '+row['path'])
        with path.open('rb') as stream:digest=file_digest(stream,'sha256').hexdigest()
        need(digest==row['sha256'],'pinned seven-product source: '+row['path'])
        result[row['path']]=digest
    return result

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module
