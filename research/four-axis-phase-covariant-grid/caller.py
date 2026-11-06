"""Checked four-axis backend for the retained dirty ports.

@CubeJerry with substantial OpenAI Codex assistance; Apache-2.0.
Retained port schedules are by Ali Romman and JoyboyBrian.
"""
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path

from construction import build_tables, need, source_key, target_key
from kernel import rotate

HERE = Path(__file__).resolve().parent


def load_ports():
    """Authenticate unchanged predecessor bytes before loading either module."""
    pins = json.loads((HERE / 'CALLER-SOURCES.json').read_text())
    modules = []
    for item in pins['files']:
        raw = (HERE / item['local_path']).read_bytes()
        need(len(raw) == item['size'] and sha256(raw).hexdigest() == item['sha256']
             and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == item['git_blob'],
             'Exact retained caller source: '+item['local_path'])
        spec = importlib.util.spec_from_file_location(item['module'], HERE / item['local_path'])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules.append(module)
    return tuple(modules)


def checked_block(values, tables, width, inverse=False, trace=None):
    """Same certified map, with fast butterflies and checked finite words."""
    need(type(width) is int and width >= 2 and type(inverse) is bool, 'Block word format')
    need(type(values) in (tuple, list) and len(values) == 16
         and all(type(z) in (tuple, list) and len(z) == 2 for z in values), 'Block dimensions')
    trace = trace if trace is not None else {}
    def word(x):
        need(type(x) is int and -(1 << (width-1)) <= x < (1 << (width-1)), 'Word overflow')
        trace['checked_values'] = trace.get('checked_values', 0)+1
        trace['peak_integer'] = max(trace.get('peak_integer', 0), abs(x))
        return x
    for z in values:
        for x in z:
            word(x)
    z = [rotate(tuple(word(-a) for a in values[j]), j.bit_count()) if inverse
         else rotate(values[j], -j.bit_count()) for j in range(16)]
    for pair in z:
        for x in pair:
            word(x)
    out = []
    for component in range(2):
        a = [pair[component] for pair in z]
        # Classification acts only on three-bit residues, but is payable work.
        residues = [x % 8 for x in a]
        key = target_key(residues) if inverse else source_key(residues)
        correction = tables[1 if inverse else 0][key]
        for bit in range(4):
            step = 1 << bit
            for base in range(0, 16, 2*step):
                for low in range(step):
                    i, j = base+low, base+low+step
                    x, y = a[i], a[j]
                    a[i], a[j] = word(x+y), word(x-y)
        for j in range(16):
            a[j] = word(a[j]+correction[j])
            need(a[j] % 4 == 0, 'Exact quarter')
            a[j] = word(a[j]//4)
        out.append(a)
    result = [rotate((out[0][j], out[1][j]), j.bit_count()) if inverse
              else rotate((-out[0][j], -out[1][j]), -j.bit_count()) for j in range(16)]
    for pair in result:
        for x in pair:
            word(x)
    trace['blocks'] = trace.get('blocks', 0)+1
    trace['data_additions'] = trace.get('data_additions', 0)+160
    trace['quarter_shifts'] = trace.get('quarter_shifts', 0)+32
    return result


def fibers(axis):
    bits = [3*j+axis for j in range(4)]
    mask = sum(1 << bit for bit in bits)
    offsets = [sum(((j >> k) & 1) << bits[k] for k in range(4)) for j in range(16)]
    for base in range(4096):
        if base & mask == 0:
            yield [base | offset for offset in offsets]


def make_backend(tables):
    """Bind the authenticated certificate once; return the retained call API."""
    def call(values, f, axis, width, adjoint=False, trace=None):
        need(type(f) is int and f == 4 and type(axis) is int and axis in (0, 2)
             and len(values) == 4096 and type(adjoint) is bool, 'Four-axis dimensions')
        trace = trace if trace is not None else {}
        for indices in fibers(axis):
            result = checked_block([values[i] for i in indices], tables, width, adjoint, trace)
            for i, z in zip(indices, result):
                values[i] = z
        return values
    return call


def request_bits(P, kind, reverse):
    """Retain source q while using the new g=q+1 at exactly four axes."""
    need(type(P) is int and P >= 0 and type(kind) is int and kind in (2, 3)
         and type(reverse) is bool, 'Port precision format')
    q = P + ((4 if kind == 2 else 6) if reverse else (7 if kind == 2 else 9))
    return q+1


def signed_width(H, P, kind, reverse):
    need(type(H) is int and H >= 0, 'Port magnitude format')
    return H+request_bits(P, kind, reverse)+19
