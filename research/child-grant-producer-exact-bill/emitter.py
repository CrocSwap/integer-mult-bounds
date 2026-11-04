"""Authenticated complete nine-tape source producer construction only.

Source macro/producer thu-nmrc; machine/counters David Arias PR2776.
ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
PINS = {
 'source/producer.py':'dbd58802087ce10e39a72202960dbb5d4aa5ce50dc1b99b7ec98e07273c292b6',
 'source/inputs/PR6719/machine.py':'04b7b76b9f06653d94d2158196cdd1bed7883dd1f59fcbc81a486e3ffb248681',
 'source/inputs/PR6719/counters.py':'2b51181a3efd403be14111ed2d556ba10e63a8939756e69d488d12344d5a7ad1',
 'source/inputs/PR6719/router.py':'ccfb60465cacd3d0f458f96a505c43f5ccda6bb8eacd6ca67f8177f5fb1796a3',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def emit_tables():
    """Import exact closure and call build(L), not Machine/Tape/router build.

    A,H,R do not enter this constructor. They are runtime physical tape data.
    Imported source names are restored after all finite tables are rendered.
    """
    for name, sha in PINS.items():
        need(hashlib.sha256((HERE/name).read_bytes()).hexdigest() == sha,
             'producer emitter source drift: '+name)
    names = ('machine','counters','router')
    saved = {name:sys.modules.get(name) for name in names}
    try:
        spec = importlib.util.spec_from_file_location('_s8_pinned_producer', HERE/'source/producer.py')
        need(spec is not None and spec.loader is not None, 'producer loader')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        need([module.A_INPUT,module.H_INPUT,module.R_INPUT,module.A_CHILD,module.R_CHILD,
              module.A_UNARY,module.H_UNARY,module.R_UNARY,module.WORK] == list(range(9)),
             'exact nine physical roles')
        need([module.m.BLANK,module.m.LEFT,module.m.RIGHT,module.m.ZERO,
              module.m.ONE,module.m.UNIT,module.m.MARK] == list(range(7)), 'source alphabet')
        result=[]
        for low_types in (2,3,4,7):
            program=module.build(low_types)
            need(program.tapes == 9, 'nine source tapes')
            result.append({'low_types':low_types,'tapes':program.tapes,
                           'entry':program.entry,'instructions':program.instructions})
        return json.loads(json.dumps(result,sort_keys=True))
    finally:
        for name, old in saved.items():
            if old is None:
                sys.modules.pop(name,None)
            else:
                sys.modules[name]=old
