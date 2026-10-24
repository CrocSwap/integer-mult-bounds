"""Unchanged CRT operations sharing the authenticated Tensor Tape cohort."""
from contextlib import contextmanager
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(test,message):
    if not test:raise ValueError(message)

@contextmanager
def opened():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']!='input':continue
        path=ROOT/row['path']
        need(path.is_file() and not path.is_symlink() and sha256(path.read_bytes()).hexdigest()==row['sha256'],'authenticated input: '+row['path'])
    need('tensor_sources' not in sys.modules and 'crt_sources' not in sys.modules,'cold physical namespace')
    old=sys.path[:]
    sys.path[:0]=[str(ROOT/'research/physical-gaussian-tensor'),str(ROOT/'research/crt-address-streams')]
    tensor=importlib.import_module('tensor_sources')
    try:
        with tensor.opened() as state:
            crt=importlib.import_module('crt_sources');crt.authenticate()
            need(crt._active is None,'unbound CRT lifecycle token')
            # Interface byte equivalence is separate from this shared Tape identity.
            crt._active=state
            try:yield state
            finally:crt._active=None
    finally:sys.path[:]=old
