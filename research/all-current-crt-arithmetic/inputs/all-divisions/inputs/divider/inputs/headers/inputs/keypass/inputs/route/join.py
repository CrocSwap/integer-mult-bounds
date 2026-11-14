"""One exact source seam: replace B5's per-wire row loop by a literal entry.

All source/lease, all-wire payload traversal and radix providers are retained.
Apache-2.0. Prepared for @CubeJerry with substantial OpenAI assistance.
"""
from hashlib import sha256
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
CALLER_SHA = '055e86590e1cb03555f9ef6f1d585f8c23453a4cc10cd7feda7362c77f7bce1c'
REPLACEMENT = '''def route_address(leaf, point, headers, width, address, private, reverse, extra=()):
    """One fixed entry; source headers and outer wire traversal are retained."""
    need(not extra, 'only the declared twenty-owner controller')
    ports = (*private, headers['h'], headers['modulus'], headers['offsets'],
             headers['selected_layer'], address, width)
    result = point.run(ports, 'INVERSE' if reverse else 'FORWARD')
    need(result['status'] == 'DONE', 'literal complete row controller accepts')


'''


def bind():
    path = HERE/'inputs/point/caller.py'
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != CALLER_SHA:
        raise ValueError('exact B5 caller source changed')
    source = raw.decode()
    before, tail = source.split('def route_address(', 1)
    removed, after = tail.split('def prepare_keys(', 1)
    adapted = before+REPLACEMENT+'def prepare_keys('+after
    module = types.ModuleType('_literal_whole_row_join')
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(adapted, str(path)+'[one declared route_address seam]', 'exec'), module.__dict__)
    module.exact_seam = {'original_sha256': sha256(raw).hexdigest(),
                         'removed_sha256': sha256(('def route_address('+removed).encode()).hexdigest(),
                         'replacement_sha256': sha256(REPLACEMENT.encode()).hexdigest(),
                         'adapted_sha256': sha256(adapted.encode()).hexdigest()}
    return module
