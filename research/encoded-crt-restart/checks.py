"""Verifier support only: byte pins, fixtures and independent CRT arithmetic.

None of the decoded values or schedules in this file enters production.
Prepared for CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
from math import prod
from pathlib import Path
from types import ModuleType, SimpleNamespace
import json
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, relative):
    path = HERE / relative
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def authenticate():
    pins = json.loads((HERE / 'EXPORT-PINS.json').read_text())
    for row in pins:
        raw = (HERE / row['local']).read_bytes()
        need(len(raw) == row['bytes'], 'exact source length')
        need(sha256(raw).hexdigest() == row['sha256'], 'exact source SHA256')
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
             == row['git_blob'], 'exact source Git blob')
    return len(pins)


def modules():
    root = 'predecessor/source/research/'
    w = load('words', root + 'r437-preparation-composition/predecessor4025/source/words.py')
    r = load('restart_records', root + 'r437-preparation-composition/predecessor4025/source/records.py')
    e = load('restart_entry', root + 'encoded-crt-entry-lifecycle/entry.py')
    n = load('restart_numeric', root + 'encoded-current-crt/producer.py')
    o = load('restart_owner', root + 'crt-persistent-numerical-owner/owner.py')
    c = load('restart_canonical', root + 'crt-mixed-row-entry/bridge.py')
    f = load('restart_frontend', root + 'encoded-balanced-crt-entry/frontend.py')
    writer = load('restart_writer', root + 'encoded-balanced-crt-endpoint/endpoint.py')
    inv = load('restart_inverse', 'predecessor/inverse_frontend.py')
    sub = load('restart_subtractive', 'predecessor/inverse_producer.py')
    restart = load('restart', 'restart.py')
    return SimpleNamespace(w=w, r=r, e=e, n=n, o=o, c=c, f=f, writer=writer,
                           inv=inv, sub=sub, restart=restart)


def acquire(m, ports=None, cls=None):
    return (cls or m.restart.Restart)(m.w, m.r, m.e, m.n, m.o, m.c,
                                     m.f, m.inv, m.sub, m.writer, ports)


class ShiftedCells:
    """Test-only physical backing view with an opaque left prefix.

    The scientific code sees the same local cell indices. Every view has
    one disjoint backing; no alias detection claim for arbitrary views.
    """
    def __init__(self, raw, prefix):
        self.origin = len(prefix)
        self.data = bytearray(prefix) + bytearray(raw)

    def __len__(self):
        return len(self.data) - self.origin

    def __getitem__(self, key):
        if isinstance(key, slice):
            return bytearray(self[i] for i in range(*key.indices(len(self))))
        if key < 0:
            key += len(self)
        return self.data[self.origin + key]

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            need(step == 1 and stop-start == len(value), 'history-preserving fixture slice')
            self.data[self.origin+start:self.origin+stop] = value
        else:
            if key < 0:
                key += len(self)
            self.data[self.origin + key] = value

    def append(self, value):
        self.data.append(value)

    def __iter__(self):
        return iter(self.data[self.origin:])


def fixture(m, source, moduli, widths, values, tail=0):
    """Admit new caller-supplied bytes without discarding source history."""
    raw, fields = bytearray([m.w.LEFT]), []
    for s, h, x in zip(moduli, widths, values, strict=True):
        raw.append(m.r.ROOT)
        raw.extend([m.w.ONE] * h)
        raw.append(m.r.WORD_END)
        for value, end in ((s, m.r.WORD_END), (x, m.r.RECORD_END)):
            start = len(raw)
            raw.extend((value >> j) & 1 for j in range(h))
            if end == m.r.RECORD_END:
                fields.append(tuple(range(start, len(raw))))
            raw.append(end)
    raw.append(m.w.RIGHT)
    raw.extend((m.w.ONE, m.w.ZERO, m.w.BLANK)[j % 3] for j in range(tail))
    while len(source.cells) < len(raw):
        source.cells.append(m.w.BLANK)
    source.cells[:len(raw)] = raw
    source.head = 1
    return fields


def values(source, fields):
    return tuple(sum(source.cells[at] << j for j, at in enumerate(field))
                 for field in fields)


def node_oracle(moduli, current, start, half, reverse):
    """Defining congruences by exhaustive search, no producer arithmetic."""
    left, xs = moduli[start:start+half], current[start:start+half]
    prefix, residues = 1, []
    for s, x in zip(left, xs):
        residues.append(prefix*x % s)
        prefix *= s
    lower = 0
    if all(x < s for x, s in zip(xs, left)):
        lower = next(k for k in range(prod(left))
                     if all(k % s == residue for s, residue in zip(left, residues)))
    out = list(current)
    for i in range(start+half, start+2*half):
        s, x = moduli[i], current[i]
        offset = next(c for c in range(s) if (prefix*c-lower) % s == 0)
        out[i] = ((x-offset if reverse else x+offset) % s) if x < s else x
        prefix *= s
    return tuple(out)


def schedule(d, reverse):
    levels = range(1, d.bit_length())
    for j in reversed(tuple(levels)) if reverse else levels:
        half = 1 << (j-1)
        for start in range(0, d, 2*half):
            yield start, half


def role_envelope(a, d):
    p, length = a+1, 2+3*a+4*d
    return ([p+1] + [2*a+2*d+2]*2 + [p+2]*57
            + [d*(p+2)+2]*3 + [p+2]*8 + [d+2]*6
            + [a+2, length])


def actions(ports):
    return sum(p.meter.reads+p.meter.writes+p.meter.moves for p in ports)


def blank(m, ports):
    return all(p.head == 1 and all(x == m.w.BLANK for x in p.cells) for p in ports)


@contextmanager
def sealed(m):
    old = m.e.Port.__init__, m.w.Word.__init__, m.w.Arena.__init__, m.w.Word.inspect
    def denied(*_args, **_kwargs):
        raise ValueError('new role or decoded word forbidden')
    m.e.Port.__init__ = m.w.Word.__init__ = m.w.Arena.__init__ = m.w.Word.inspect = denied
    try:
        yield
    finally:
        m.e.Port.__init__, m.w.Word.__init__, m.w.Arena.__init__, m.w.Word.inspect = old


def poison(module):
    def denied(*_args, **_kwargs):
        raise ValueError('decoded runtime geometry forbidden')
    for name in ('int', 'float', 'range', 'sum', 'min', 'max', 'enumerate', 'pow', 'sorted', 'zip'):
        module.__dict__[name] = denied
