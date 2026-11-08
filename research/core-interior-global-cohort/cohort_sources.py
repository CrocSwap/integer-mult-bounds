"""Authenticated canonical Core/Full and frozen global-service source closure.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The unchanged retained sources keep their author and licensing notices.
"""
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VENDOR = HERE / 'vendor/global-caller'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(overrides=None):
    raw = {}
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        path = row['path']
        content = (overrides or {}).get(path)
        if content is None:
            file = ROOT/path
            need(file.is_file() and not file.is_symlink(), 'regular source: '+path)
            content = file.read_bytes()
        need(sha256(content).hexdigest() == row['sha256'], 'canonical source: '+path)
        raw[path] = content
    for row in json.loads((HERE/'GLOBAL-DEPENDENCY.json').read_text())['files']:
        file = HERE/row['path']
        need(file.is_file() and not file.is_symlink(), 'regular global dependency')
        content = file.read_bytes()
        need(len(content) == row['bytes'] and sha256(content).hexdigest() == row['sha256'],
             'frozen global dependency: '+row['path'])
    return raw


@contextmanager
def opened(overrides=None):
    """One private numerical class identity, restoring all public module aliases."""
    raw = authenticate(overrides)
    interval_name = '_retained_gaussian_intervals_'+sha256(
        raw['research/certified-gaussian-recovery/intervals.py']).hexdigest()
    need(interval_name not in sys.modules,'cold authenticated Gaussian interval module')
    aliases = ('sources','lowering','exact','engine','full','gaussian',
               'gaussian_reference','raw_gaussian','core','allocation','bridge','compiler')
    previous = {name:sys.modules.get(name) for name in aliases}
    created = [interval_name]

    def module(name, content, path):
        unique = '_core_cohort_'+name
        need(unique not in sys.modules, 'cold source module: '+unique)
        value = ModuleType(unique)
        value.__file__ = str(path)
        sys.modules[unique] = value
        sys.modules[name] = value
        created.append(unique)
        exec(compile(content, str(path), 'exec', optimize=0), value.__dict__)
        return value

    try:
        utility = module('sources',(VENDOR/'sources.py').read_bytes(),VENDOR/'sources.py')
        utility.ROOT, utility.HERE = ROOT,VENDOR
        dense,lower,source = utility.load()
        sys.modules['exact'],sys.modules['engine'],sys.modules['full'] = source.e,source.engine,source.full
        values = {}
        for name in ('gaussian','gaussian_reference','raw_gaussian','core'):
            path = 'research/rational-unitary-fft/'+name+'.py'
            values[name] = module(name,raw[path],ROOT/path)
        path = 'research/full-downset-allocation/allocation.py'
        allocator = module('allocation',raw[path],ROOT/path)
        path = 'research/gaussian-downset-grid/bridge.py'
        grid = module('bridge',raw[path],ROOT/path)
        reduced,receipt = allocator.adapted(raw['research/rational-unitary-fft/full.py'],
                                           source.e.need,source.e.ceil_log2)
        Normalized,Raw = grid.bind(values['gaussian'],values['raw_gaussian'],reduced)
        compiler = module('compiler',(VENDOR/'compiler.py').read_bytes(),VENDOR/'compiler.py')
        complete_raw = dict(source.raw)
        complete_raw.update(raw)
        yield SimpleNamespace(raw=complete_raw,dense=dense,lower=lower,source=source,
            exact=source.e,global_compiler=compiler,utility=utility,
            core=values['core'],reference=values['gaussian_reference'],
            gaussian=values['gaussian'],Raw=Raw,Normalized=Normalized,grid_receipt=receipt)
    finally:
        for name,old in previous.items():
            if old is None:
                sys.modules.pop(name,None)
            else:
                sys.modules[name] = old
        for name in created:
            sys.modules.pop(name,None)
