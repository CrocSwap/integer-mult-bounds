"""Replace exactly the retained all-wire prepare_keys source seam.

Source acquisition, header emission and literal radix providers are unchanged.
Apache-2.0. Prepared for @CubeJerry with substantial OpenAI assistance.
"""
from hashlib import sha256
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
CALLER_SHA = '055e86590e1cb03555f9ef6f1d585f8c23453a4cc10cd7feda7362c77f7bce1c'
REPLACEMENT = '''def prepare_keys(leaf, point, headers, record, width, index, address, private,
                 reverse, *, stale_wire=False):
    """One fixed complete key-pass entry on the original physical payload."""
    need(not stale_wire, 'no stale-wire alias in the declared twenty-two-owner ABI')
    ports = (*private, headers['h'], headers['modulus'], headers['offsets'],
             headers['selected_layer'], address, width, index, _BitPort(record.tape))
    result = point.run(ports, 'INVERSE' if reverse else 'FORWARD')
    need(result['status'] == 'DONE', 'literal complete key pass accepts')


'''


def bind(bit_port):
    path = HERE/'inputs/route/inputs/point/caller.py'
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != CALLER_SHA:
        raise ValueError('exact B5 caller source changed')
    before, tail = raw.decode().split('def prepare_keys(', 1)
    removed, after = tail.split('def run_leg(', 1)
    adapted = before+REPLACEMENT+'def run_leg('+after
    module = types.ModuleType('_literal_complete_key_join')
    module.__file__ = str(path)
    module._BitPort = bit_port
    sys.modules[module.__name__] = module
    exec(compile(adapted, str(path)+'[one declared prepare_keys seam]', 'exec'), module.__dict__)
    module.exact_seam = {'original_sha256': sha256(raw).hexdigest(),
                         'removed_sha256': sha256(('def prepare_keys('+removed).encode()).hexdigest(),
                         'replacement_sha256': sha256(REPLACEMENT.encode()).hexdigest(),
                         'adapted_sha256': sha256(adapted.encode()).hexdigest()}
    return module
