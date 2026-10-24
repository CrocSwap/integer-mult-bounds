"""Source-bound whole-packet adapter for FOUR/base data climbs.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
The physical recursive child and helper gathering remain separate obligations.
"""
import ast
from functools import lru_cache
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/staged544-mixed-fourth-entry'
BORROW = SOURCE / 'native/vendor/native/new/code/borrow'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def functions(path, namespace, names=None):
    """Load pinned definitions without running a predecessor's full CLI replay."""
    tree = ast.parse(path.read_text())
    nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
             and (names is None or node.name in names)]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec', optimize=0), namespace)
    return namespace


@lru_cache(None)
def source():
    from dataclasses import dataclass
    from fractions import Fraction
    c = read(SOURCE / 'evidence/NATIVE-CANONICAL-base.json.gz')
    algebra = functions(BORROW / 'vendor/clifford/clifford_exact.py', {'dataclass': dataclass})
    emit = functions(BORROW / 'bw_emit.py', {'c': c, 'frames': c['frames'], 'v': c['v'],
                     'n': 2*c['v']+c['R'], 'Q': Fraction})
    geometry = functions(ROOT / 'research/e8-signed-prefix/code/data_phases.py',
                         {**algebra, 'H': 9, 'M': 73}, {'basis', 'rho', 'stage_frame'})
    return c, algebra, emit, geometry


def mv(rows, x):
    return sum(((row & x).bit_count() & 1) << i for i, row in enumerate(rows))


def inverse(rows):
    n = len(rows)
    need(all(type(r) is int and 0 <= r < 1 << n for r in rows), 'matrix bounds')
    a = [r | (1 << (n+i)) for i, r in enumerate(rows)]
    for j in range(n):
        k = next((i for i in range(j, n) if a[i] >> j & 1), None)
        need(k is not None, 'singular chart')
        a[j], a[k] = a[k], a[j]
        for i in range(n):
            if i != j and a[i] >> j & 1:
                a[i] ^= a[j]
    return tuple(r >> n for r in a)


def compose(a, b):
    return tuple(sum(((mv(a, mv(b, 1 << j)) >> i) & 1) << j for j in range(len(a)))
                 for i in range(len(a)))


def phase(rec, x):
    q, alpha = rec['quadratic_rows'], rec['linear_Z4']
    return (rec['phase'] + sum(alpha[i] for i in range(9) if x >> i & 1)
            + 2*sum(((q[i] >> (i+1)) & (x >> (i+1))).bit_count()
                    for i in range(9) if x >> i & 1)) % 4


def mono(rec, x, undo=False):
    if undo:
        y = mv(inverse(rec['matrix_rows']), x ^ rec['offset'])
        return y, -phase(rec, y) % 4
    return mv(rec['matrix_rows'], x) ^ rec['offset'], phase(rec, x)


@lru_cache(None)
def recipe(old, new):
    c, a, _, _ = source()
    op = a['canonical_frame'](9, c['frames'][old]).adjoint().then(
         a['canonical_frame'](9, c['frames'][new]))
    rec, compiled = a['lower_child'](op)
    need(compiled.tab == op.tab and compiled.zero_state() == op.zero_state(), 'source recipe endpoint')
    return rec


def request(tick, event_index, e, remaining_rows, cover, return_site='next-event'):
    c, _, emitter, geo = source()
    dispatch = read(SOURCE / 'owner/MIXED-DISPATCH.json')
    need(type(tick) is int and 0 <= tick < len(dispatch), 'dispatch tick')
    stage, replica, provider = dispatch[tick]
    need(provider == 'gauge44-four', 'not FOUR/base')
    template = read(SOURCE / 'owner/TEMPLATE.json.gz')
    stage_rec = next(x for x in template['recipe'] if x['kind'] == 'local' and x['stage'] == stage)
    back = stage_rec['reverse']
    events = emitter['emit'](back)
    need(type(event_index) is int and 0 <= event_index < len(events), 'event index')
    event = events[event_index]
    need(event[0] == 'climb', 'not a paid climb')
    _, part, reg, old, new, rank = event
    need(reg < 224, 'helper hosting unimplemented: requires owner fill and residual wrapper chart')
    need(type(e) is int and e >= 73, 'node width')
    need(type(remaining_rows) is int and remaining_rows >= 1, 'remaining row stock')
    need(len(cover) == 73, 'cover dimension')
    ci = inverse(cover)
    need(all(((a & b).bit_count() & 1) == (i == j) for i,a in enumerate(cover)
             for j,b in enumerate(cover)), 'not an orthogonal cover')
    side, port = divmod(reg, 112)
    q = c['ports'][port]
    rho = geo['rho'](q, stage)
    actual_cover = compose(cover, rho)
    rec = recipe(old, new)
    need(rec['rank'] == rank, 'emitted rank differs from recipe')
    ph = read(SOURCE / 'inputs/DATA-PHASES.json')['recipes'][port]
    need(ph['q'] == q, 'actual port binding')
    return {'schema': 'four-base-data-packet-v1', 'tick': tick, 'stage': stage,
            'replica': replica, 'provider': provider, 'orientation': 'backward' if back else 'forward',
            'event_index': event_index, 'event': event, 'family': 896*replica+112*(2*stage_rec['pair']+side)+port,
            'e': e, 'f': e//73, 't': e%73, 'rank': rank, 'child_width': rank*(e//73),
            'remaining_rows': remaining_rows, 'common_cover_rows': list(cover),
            'physical_cover_rows': list(actual_cover), 'physical_cover_inverse': list(inverse(actual_cover)),
            'native_chart_rows': list(cover), 'native_chart_inverse': list(ci),
            'source_rho_rows': list(rho),
            'stage_alignment': ph['stage_alignment'][stage], 'recipe': rec,
            'return_site': return_site, 'child_calls': 1 if rank else 0}


def check_packet(d, packet):
    need(set(packet) == {'remaining_row','address','compact','prefix','suffix','dirty'}, 'complete packet fields')
    need(type(packet['address']) is int and 0 <= packet['address'] < 1 << d['e'], 'address bounds')
    need(type(packet['remaining_row']) is int and 0 <= packet['remaining_row'] < d['remaining_rows'], 'row bounds')


def chart(d, address, rec, enter, undo=False):
    """Enter/leave the fixed physical cover view and apply a literal monomial."""
    total = 0
    out = address >> (73*d['f']) << (73*d['f'])
    for j in range(d['f']):
        x = (address >> (73*j)) & ((1 << 73)-1)
        if enter:
            x = mv(d['native_chart_inverse'], x)
        low, ph = mono(rec, x & 511, undo)
        x = (x >> 9 << 9) | low
        if not enter:
            x = mv(d['native_chart_rows'], x)
        out |= x << (73*j)
        total += ph
    return out, total % 4


def regroup(d, address):
    active = inactive = 0
    r = d['rank']
    for j in range(d['f']):
        col = address >> (73*j) & ((1 << 73)-1)
        active |= (col & ((1 << r)-1)) << (r*j)
        inactive |= (col >> r) << ((73-r)*j)
    return active, inactive, address >> (73*d['f'])


def ungroup(d, active, inactive, remainder):
    r, f = d['rank'], d['f']
    need(0 <= active < 1 << (r*f) and 0 <= inactive < 1 << ((73-r)*f)
         and 0 <= remainder < 1 << d['t'], 'child address bounds')
    return (remainder << (73*f)) | sum((((active >> (r*j)) & ((1 << r)-1)) |
          (((inactive >> ((73-r)*j)) & ((1 << (73-r))-1)) << r)) << (73*j) for j in range(f))


def pack(d, packet):
    check_packet(d, packet)
    x, ph = chart(d, packet['address'], d['recipe']['right'], True)
    active, inactive, remainder = regroup(d, x)
    child = {k:v for k,v in packet.items() if k != 'address'}
    child.update(active=active, inactive=inactive, remainder=remainder)
    return child, ph


def unpack(d, child):
    need(set(child) == {'remaining_row','active','inactive','remainder','compact','prefix','suffix','dirty'}, 'complete child fields')
    x = ungroup(d, child['active'], child['inactive'], child['remainder'])
    address, ph = chart(d, x, d['recipe']['left'], False)
    out = {k:v for k,v in child.items() if k not in {'active','inactive','remainder'}}
    out['address'] = address
    check_packet(d, out)
    return out, ph


def unprepare(d, child):
    """Inverse packing, distinct from post-child left-chart application."""
    x = ungroup(d, child['active'], child['inactive'], child['remainder'])
    address, ph = chart(d, x, d['recipe']['right'], False, undo=True)
    out = {k:v for k,v in child.items() if k not in {'active','inactive','remainder'}}
    out['address'] = address
    return out, ph


def rotate(value, exponent):
    re, im = value
    return ((re,im),(-im,re),(-re,-im),(im,-re))[exponent % 4]


def execute(d, records, child):
    """Reindex a complete tagged record stream around exactly one child call.

    Record ordering is not a fixed-tape implementation or a sorting cost claim.
    The child must retain every inactive field and process the complete rf field.
    """
    def prepared():
        for packet, value in records:
            packed, ph = pack(d, packet)
            yield packed, rotate(value, ph)
    returned = child(d, prepared())
    for packet, value in returned:
        unpacked, ph = unpack(d, packet)
        yield unpacked, rotate(value, ph)
