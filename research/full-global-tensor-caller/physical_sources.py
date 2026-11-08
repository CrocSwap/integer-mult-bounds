"""One authenticated word/H cohort and the byte-identical raw-H boundary.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The retained numerical, tape, word and ownership sources keep their notices.
"""
from contextlib import contextmanager
from hashlib import sha256
import importlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    checked = {}
    for row in json.loads((HERE/'PHYSICAL-SOURCES.json').read_text())['files']:
        path = ROOT/row['path']
        need(path.is_file() and not path.is_symlink(), 'regular physical Full source: '+row['path'])
        raw = path.read_bytes()
        need(len(raw) == row['bytes'] and sha256(raw).hexdigest() == row['sha256'],
             'pinned physical Full source: '+row['path'])
        checked[row['path']] = row['sha256']
    return checked


def load(name, path):
    need(name not in sys.modules, 'cold physical Full module: '+name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@contextmanager
def opened():
    """The exact word owner shares the unchanged #3627 H tape cohort.

    The authenticated archive also contains numerical Fourier source, but no
    RingProduct or FftWord object is instantiated or called by this service.
    """
    need(not any(name in sys.modules for name in ('ring_sources','composed_sources',
             'word_product','ring_words','fft_arithmetic','global_h_boundary','frontend')),
         'one cold Full/word/H cohort per process')
    authenticate()
    old = sys.path[:]
    sys.path.insert(0, str(ROOT/'research/physical-ring-product'))
    try:
        import ring_sources
        with ring_sources.opened() as state:
            for name in ('word_product','ring_words','fft_arithmetic'):
                module = importlib.import_module(name)
                need(Path(module.__file__).resolve() ==
                     (ROOT/'research/physical-ring-product'/f'{name}.py').resolve(),
                     'actual authenticated exact-word module path: '+name)
            # These are the exact B1 live-source Git blobs, not compatible names.
            expected = {
                'composed_sources': '5b9a507a5f5eb7d32d76792cac4b876070d29e91',
                'composed_engine': '646c451a4cbdf0244c7782d958f257f6606b962f',
                'composed_plan': '300ee75d4171c8f0d97118a01a4e439b72ca01d6',
            }
            from hashlib import sha1
            for name, blob in expected.items():
                module = importlib.import_module(name)
                raw = Path(module.__file__).read_bytes()
                need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == blob,
                     'identical frozen raw-H dependency: '+name)
            load('frontend', HERE/'vendor/global-boundary/frontend.py')
            state.global_boundary = load('global_h_boundary', HERE/'vendor/global-boundary/bridge.py')
            from cardinal_counts import Count
            from records import Tape
            from word_product import WordProduct
            need(state.global_boundary.Count is Count and state.global_boundary.Tape is Tape,
                 'one physical Count/Tape identity for H and word services')
            state.full_word_class = WordProduct
            yield state
    finally:
        sys.path[:] = old
