"""Load byte-identical published physical owners from their vendored location.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Only filesystem relocation is adapted; all physical source and checks remain.
"""
from contextlib import contextmanager
import sys
from types import ModuleType
from cohort_sources import ROOT,VENDOR,authenticate,need


class RelocatedRoot:
    def __truediv__(self,path):
        prefix = 'research/full-global-tensor-caller/'
        name = str(path)
        return VENDOR/name[len(prefix):] if name.startswith(prefix) else ROOT/name


@contextmanager
def opened():
    authenticate()
    aliases = ('physical_sources','physical_controls','physical_engine','frontend','global_h_boundary')
    previous = {name:sys.modules.get(name) for name in aliases}
    need(all(value is None for value in previous.values()),'cold physical adapter aliases')
    created = []

    def load(name):
        unique = '_core_cohort_'+name
        need(unique not in sys.modules,'cold physical source module')
        module = ModuleType(unique)
        module.__file__ = str(VENDOR/(name+'.py'))
        sys.modules[unique] = module
        sys.modules[name] = module
        created.append(unique)
        exec(compile((VENDOR/(name+'.py')).read_bytes(),module.__file__,'exec',optimize=0),module.__dict__)
        return module

    try:
        source = load('physical_sources')
        source.ROOT,source.HERE = RelocatedRoot(),VENDOR
        with source.opened() as state:
            state.controls = load('physical_controls')
            state.physical = load('physical_engine')
            yield state
    finally:
        for name,old in previous.items():
            if old is None:
                sys.modules.pop(name,None)
            else:
                sys.modules[name] = old
        for name in created:
            sys.modules.pop(name,None)
