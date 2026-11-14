"""Literal 70-tape old-coded -> positive C -> old-coded composition.

Prepared for @CubeJerry with OpenAI assistance. Apache-2.0.
The two retained graphs are unmodified inputs. Only fixed ports, symbols,
addresses, and the two successful continuation instructions are translated.
"""
from pathlib import Path
from hashlib import sha256
import json
import sys
import types

HERE = Path(__file__).resolve().parent
PIN = {
    'inputs/bridge.py': '119b69594a2a33550eec9b6e083db8f496c3fb3d9c1214b6703d687a0a662eba',
    'inputs/leaf/leaf.py': 'bb46c1a55f1119957a52cd61f2cd957f3f7ad1e9b818c54a852bde09a0773744',
    'inputs/leaf/inputs/controller_reference.py': 'e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73',
}
TAPES = 70
BLANK, LEFT = 2, 3
SYMBOL = {'_': BLANK, '0': 0, '1': 1, '|': LEFT}
# Exact leaf order is HEADER, DATA, then the 27 private tapes.
PORT_MAP = (3, 2, *range(43, 70))


def load_exact(relative, name):
    path = HERE / relative
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PIN[relative]:
        raise ValueError('source drift: ' + relative)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def compile_composition():
    """No runtime parameters, payload, counts, widths, or origins are inputs."""
    bridge = load_exact('inputs/bridge.py', '_joined_bridge')
    previous_path = list(sys.path)
    previous_controller = sys.modules.get('controller_reference')
    try:
        load_exact('inputs/leaf/inputs/controller_reference.py', 'controller_reference')
        leaf = load_exact('inputs/leaf/leaf.py', '_joined_leaf')
        child, alphabet = leaf.compile_leaf()
    finally:
        sys.path[:] = previous_path
        if previous_controller is None:
            sys.modules.pop('controller_reference', None)
        else:
            sys.modules['controller_reference'] = previous_controller
    old, labels = bridge.compile_bridge()
    if len(old) != 6003 or len(child) != 6826 or set(alphabet) != set(SYMBOL):
        raise ValueError('unexpected fixed source graph')
    offset = len(old)
    code = []
    joins = 0
    for ins in old:
        if ins == ('H', 'PACKED'):
            code.append(('J', offset)); joins += 1
        else:
            code.append(ins)
    successes = 0
    for ins in child:
        op, *args = ins
        if op == 'read':
            code.append(('R', PORT_MAP[args[0]],
                         {SYMBOL[s]: offset + target for s, target in args[1].items()}))
        elif op == 'write':
            code.append(('W', PORT_MAP[args[0]], SYMBOL[args[1]]))
        elif op == 'move':
            if args[1] not in (-1, 1):
                raise ValueError('nonunit child move')
            code.append(('M', PORT_MAP[args[0]], args[1]))
        elif op == 'goto':
            code.append(('J', offset + args[0]))
        elif op == 'halt':
            leaf_return = len(code)
            code.append(('J', labels['EXIT'])); successes += 1
        else:
            raise ValueError('nonliteral child instruction')
    if joins != 1 or successes != 1 or len(set(PORT_MAP)) != 29:
        raise ValueError('invalid static continuation or port wiring')
    return tuple(code), {'ENTER': 0, 'LEAF': offset, 'EXIT': labels['EXIT'], 'LEAF_RETURN': leaf_return,
                         'NUM': PORT_MAP[leaf.NUM]}


def digest(program):
    return sha256(json.dumps(program, separators=(',', ':'), sort_keys=True).encode()).hexdigest()


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
            raise ValueError('70 distinct tape owners required')
        self.code, self.tapes, self.labels = code, tuple(tapes), labels
        self.steps = self.leaf_entries = self.exit_entries = 0
        self.first_numerator_write = None
    def run(self, limit=300_000_000):
        pc = 0; code = self.code; tapes = self.tapes
        while self.steps < limit:
            self.steps += 1
            if pc == self.labels['LEAF']: self.leaf_entries += 1
            if pc == self.labels['LEAF_RETURN']: self.exit_entries += 1
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
