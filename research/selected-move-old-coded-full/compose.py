"""One literal OLD23 -> unchanged selected MOVE24472 -> OLD23 program.
Prepared for @CubeJerry with OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import json
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
PIN = {
    'inputs/bridge.py': '119b69594a2a33550eec9b6e083db8f496c3fb3d9c1214b6703d687a0a662eba',
    'inputs/core/move.py': '42e4293ab59ffa1c99e0dbbd5fded0833a5d726e1e794f0f263ae9a4686587a5',
    'inputs/core/SOURCES.json': '26d0ef51dda5fa599381f7f31dec4ba3a37f14f63ff9055ad1661dec2d02610c',
    'inputs/core/reference/linear/inputs/controller_reference.py': 'e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73',
}
CORE_GRAPH = '14f38b15157a9c9cd2828861f6904701a29b1e27507a7e43d60030e1ae4d9238'
TAPES = 72
BLANK, LEFT = 2, 3
SYMBOL = {'_': BLANK, '0': 0, '1': 1, '|': LEFT}
PORT_MAP = (3, 2, *range(43, 72))


def authenticate(relative):
    raw = (HERE/relative).read_bytes()
    if sha256(raw).hexdigest() != PIN[relative]:
        raise ValueError('source drift: '+relative)
    return raw


def load_exact(relative, name):
    module = types.ModuleType(name); module.__file__ = str(HERE/relative)
    sys.modules[name] = module
    exec(compile(authenticate(relative), module.__file__, 'exec'), module.__dict__)
    return module


def core_graph():
    """Compile authenticated frozen sources with no possible stale cache read."""
    authenticate('inputs/core/SOURCES.json')
    old_path = list(sys.path); old_prefix = sys.pycache_prefix
    old_write = sys.dont_write_bytecode
    old_controller = sys.modules.get('controller_reference')
    try:
        with tempfile.TemporaryDirectory(prefix='selected-move-source-') as temporary:
            absent = Path(temporary)/'required-absent'
            if absent.exists(): raise ValueError('source cache prefix must be absent')
            sys.pycache_prefix = str(absent); sys.dont_write_bytecode = True
            load_exact('inputs/core/reference/linear/inputs/controller_reference.py', 'controller_reference')
            core = load_exact('inputs/core/move.py', '_joined_selected_core')
            code, alphabet = core.compile_move()
    finally:
        sys.path[:] = old_path; sys.pycache_prefix = old_prefix
        sys.dont_write_bytecode = old_write
        if old_controller is None: sys.modules.pop('controller_reference', None)
        else: sys.modules['controller_reference'] = old_controller
    if sha256(repr(code).encode()).hexdigest() != CORE_GRAPH:
        raise ValueError('unchanged selected core graph mismatch')
    return code, alphabet


def compile_composition():
    """Fixed construction: no runtime shape, value, grid, owner or recipe input."""
    bridge = load_exact('inputs/bridge.py', '_joined_bridge')
    old, labels = bridge.compile_bridge()
    child, alphabet = core_graph()
    if len(old) != 6003 or len(child) != 82813 or set(alphabet) != set(SYMBOL):
        raise ValueError('unexpected source graph')
    offset = len(old); code = []; joins = successes = 0
    for ins in old:
        if ins == ('H','PACKED'):
            code.append(('J',offset)); joins += 1
        else: code.append(ins)
    for ins in child:
        op, *args = ins
        if op == 'read':
            code.append(('R',PORT_MAP[args[0]],{SYMBOL[s]:offset+dst for s,dst in args[1].items()}))
        elif op == 'write': code.append(('W',PORT_MAP[args[0]],SYMBOL[args[1]]))
        elif op == 'move':
            if args[1] not in (-1,1): raise ValueError('nonunit source move')
            code.append(('M',PORT_MAP[args[0]],args[1]))
        elif op == 'goto': code.append(('J',offset+args[0]))
        elif op == 'halt':
            returned = len(code); code.append(('J',labels['EXIT'])); successes += 1
        else: raise ValueError('nonliteral source opcode')
    if joins != 1 or successes != 1 or len(set(PORT_MAP)) != 31:
        raise ValueError('invalid fixed invocation or return')
    return tuple(code), {'ENTER':0,'CORE':offset,'EXIT':labels['EXIT'],
                         'CORE_RETURN':returned,'NUM':70}


def digest(program):
    return sha256(json.dumps(program,separators=(',',':'),sort_keys=True).encode()).hexdigest()


class Tape:
    """Verifier hardware only. The graph receives scanned symbols/unit moves."""
    def __init__(self, body=(), origin=3, permanent_guard=True):
        if origin < 2:
            raise ValueError('verifier origin must leave opaque exterior')
        self.origin = self.head = origin
        self.cells = [BLANK] * origin + list(body)
        self.cells[origin - 2] = 7  # Opaque exterior, outside runtime alphabet.
        self.cells[origin - 1] = LEFT if permanent_guard else BLANK
        self.low = origin
        self.high = origin - 1
        self.writes = 0
    def read(self):
        self.low = min(self.low, self.head); self.high = max(self.high, self.head)
        return self.cells[self.head] if self.head < len(self.cells) else BLANK
    def write(self, symbol):
        self.writes += 1
        self.low = min(self.low, self.head); self.high = max(self.high, self.head)
        if self.head >= len(self.cells):
            self.cells.extend([BLANK] * (self.head + 1 - len(self.cells)))
        self.cells[self.head] = symbol
    def move(self, direction):
        if direction not in (-1, 1):
            raise ValueError('nonunit move')
        self.head += direction
        self.low = min(self.low, self.head); self.high = max(self.high, self.head)
        if self.head < 0:
            raise ValueError('crossed verifier physical boundary')


class CPU:
    """One uninterrupted local-instruction interpreter; counters are observers."""
    def __init__(self, code, tapes, labels):
        if len(tapes) != TAPES or len({id(t) for t in tapes}) != TAPES:
            raise ValueError('72 distinct tape owners required')
        self.code, self.tapes, self.labels = code, tuple(tapes), labels
        self.steps = self.core_entries = self.exit_entries = 0
        self.first_numerator_write = None
    def run(self, limit=300_000_000):
        pc = 0; code = self.code; tapes = self.tapes
        while self.steps < limit:
            self.steps += 1
            if pc == self.labels['CORE']: self.core_entries += 1
            if pc == self.labels['CORE_RETURN']: self.exit_entries += 1
            ins = code[pc]; op = ins[0]
            if op == 'R':
                pc = ins[2].get(tapes[ins[1]].read(), -1)
                if pc < 0: return 'REJECT'
            elif op == 'W':
                if ins[1] == self.labels['NUM'] and ins[2] in (0, 1) and self.first_numerator_write is None:
                    self.first_numerator_write = pc
                tapes[ins[1]].write(ins[2]); pc += 1
            elif op == 'M': tapes[ins[1]].move(ins[2]); pc += 1
            elif op == 'J': pc = ins[1]
            elif op == 'H': return ins[1]
            else: raise ValueError('nonliteral instruction')
        raise TimeoutError('bounded interpreter step cap')
