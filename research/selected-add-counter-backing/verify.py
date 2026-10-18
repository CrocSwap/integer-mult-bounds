#!/usr/bin/env python3
"""Exact backing census of unchanged native ADD Counter allocations."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import weakref

ROOT = Path(__file__).resolve().parent
MANIFEST = '95f3af10592a39278b0f397102a070df9688129f693449527242e7a60cda6c60'
MODULES = ('words', 'records', 'stream', 'cardinality', 'counts')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(root=ROOT):
    raw = (root / 'SOURCES.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == MANIFEST, 'source manifest digest')
    entries = json.loads(raw)['exports']
    require(len(entries) == len(MODULES), 'complete source inventory')
    code = []
    for name, entry in zip(MODULES, entries):
        require(entry['export'] == f'sources/{name}.py', 'source export order')
        data = (root / entry['export']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == entry['sha256'], 'source digest')
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == entry['git_blob'], 'source Git blob')
        code.append((name, str(root / entry['export']), data))
    return code


def load_source(root=ROOT):
    code = authenticate(root)
    require(not set(MODULES).intersection(sys.modules), 'source module already loaded')
    for name, filename, data in code:
        module = ModuleType(name)
        module.__file__ = filename
        sys.modules[name] = module
        exec(compile(data, module.__file__, 'exec'), module.__dict__)
    return SimpleNamespace(**{name: sys.modules[name] for name in MODULES})


def bound(before, middle, suffix, modulus, bits):
    for value in (before, middle, suffix, modulus, bits):
        require(type(value) is int, 'integer domain excluding bool')
    require(min(before, middle, suffix) >= 1 and modulus >= 2, 'positive ADD domain')
    require(bits == modulus.bit_length()+1 and bits <= 64, 'sufficient bounded residue width')
    p, m, s = (value.bit_length() + 3 for value in (before, middle, suffix))
    r = bits + 2
    C = p + r + m + max(m, r + (2*s if suffix > 1 else 0))
    return dict(p=p, r=r, m=m, s=s, intrinsic=C)


class Census:
    """Weak roots record actual constructor overlap without retaining Counters."""
    def __init__(self, original):
        self.original = original
        self.refs = []
        self.peak = self.allocations = self.peak_count = self.callback_peak = 0
        self.witness = []
        self.callback = False

    def sample(self):
        alive = [(ref, tag, size) for ref, tag, size in self.refs if ref() is not None]
        require(len(alive) <= 8, 'bounded native/callback counter inventory')
        self.refs = alive
        total, witness = 0, []
        for ref, tag, size in alive:
            counter = ref()
            require(len(counter.tape.cells) == size, 'Counter backing never grows')
            total += size
            witness.append([tag, size])
        if total > self.peak:
            self.peak, self.witness = total, sorted(witness)
        self.peak_count = max(self.peak_count, len(alive))
        if self.callback:
            self.callback_peak = max(self.callback_peak, total)

    def construct(self, counter, source):
        self.original(counter, source)
        size = len(counter.tape.cells)
        tag = 'callback' if self.callback else sys._getframe(2).f_code.co_name
        self.refs.append((weakref.ref(counter), tag, size))
        self.allocations += 1
        self.sample()


def fixture(rt, before, middle, suffix, modulus, bits, coefficient, callback_size=0, escape=False):
    bill = bound(before, middle, suffix, modulus, bits)
    require(0 <= coefficient < modulus, 'canonical coefficient')
    F = before*modulus*modulus*middle*suffix
    require(F <= 40000 and 0 <= callback_size <= 60, 'bounded fixture resources')
    arena = rt.words.Arena(bits)
    mod = arena.input(modulus)
    ring = rt.words.Ring(mod)
    entry_live = set(arena.live)
    extents = []
    for value in (before, middle, suffix):
        count = rt.counts.Count.literal(value)
        extents.append(count.marginal())
        count.close()
    source = rt.records.Tape()
    payload = bytes(((i*7+i//3) ^ (i//5)) & 1 for i in range(F))
    source.cells.extend(payload)
    original = rt.stream.Counter.__init__
    census = Census(original)
    calls, escaped = [], []

    def constructor(counter, word):
        census.construct(counter, word)

    def prepare():
        calls.append(len(calls))
        if callback_size:
            census.callback = True
            # A fixed padded fixture word creates exactly callback_size backing cells.
            callback_arena = rt.words.Arena(callback_size-2)
            word = callback_arena.input(1)
            private = rt.stream.Counter(word)
            require(len(private.tape.cells) == callback_size, 'callback fixture width')
            private.close()
            if escape:
                escaped.append(private)
            callback_arena.free(word)
            census.callback = False
        return arena.input(coefficient)

    rt.stream.Counter.__init__ = constructor
    try:
        output, traffic = rt.stream.add_pass(source, ring, *extents, prepare)
    finally:
        rt.stream.Counter.__init__ = original
    require(len(calls) == 2 and traffic['output']['writes'] == F, 'two complete traversals')
    verify_endpoint(source, output, payload, before, middle, suffix, modulus, coefficient)
    H = (2 if escape else 1)*callback_size
    expected_peak = bill['intrinsic']+H if escape else max(bill['intrinsic'], H)
    require(census.peak == expected_peak, 'exact Counter backing peak')
    require(census.callback_peak == H, 'callback phase has no intrinsic counters')
    census.sample()
    require(len(census.refs) == (2 if escape else 0), 'weak census does not retain counters')
    require(arena.live == entry_live, 'numerical scratch restored')
    for extent in extents:
        extent.close()
    arena.free(mod)
    return dict(parameters=[before,middle,suffix,modulus,bits,coefficient,callback_size],
                **bill, measured=census.peak, allocations=census.allocations,
                peak_count=census.peak_count, witness=census.witness, payload=F)


def verify_endpoint(source, output, payload, before, middle, suffix, modulus, coefficient):
    expected = oracle(payload, before, middle, suffix, modulus, coefficient)
    require(bytes(output.cells[1:]) == expected, 'complete native ADD endpoint')
    require(bytes(source.cells[1:]) == payload and source.head == 1, 'borrowed source restored')


def oracle(payload, before, middle, suffix, modulus, coefficient):
    result = bytearray()
    for b in range(before):
        for x in range(modulus):
            for g in range(middle):
                for y in range(modulus):
                    old_y = (y - coefficient*x) % modulus
                    offset = (((b*modulus+x)*middle+g)*modulus+old_y)*suffix
                    result.extend(payload[offset:offset+suffix])
    return bytes(result)


def cases():
    result = []
    for modulus in (2, 3, 5):
        for before, middle, suffix in ((1,1,1),(1,4,1),(2,3,2),(1,1,3),(3,2,1),(1,2,2),(2,1,1),(1,8,1),(1,2,3),(2,2,2)):
            for coefficient in (0, modulus-1):
                result.append((before,middle,suffix,modulus,modulus.bit_length()+1,coefficient,0))
    result.extend([(1,4096,2,2,3,0,0), (1,1,1,3,3,1,32), (1,1,2,3,3,1,6)])
    require(len(result) == 63, 'fixed fixture inventory')
    return result


def controls(rt, records):
    count = 0
    for args in ((0,1,1,3,2), (1,1,1,1,2), (1,1,1,3,1), (True,1,1,3,2)):
        try:
            bound(*args)
        except ValueError:
            count += 1
        else:
            raise ValueError('invalid domain accepted')
    a = next(x for x in records if x['parameters'][:5] == [1,1,3,3,3])
    require(a['measured'] > a['p']+2*a['r']+a['m']+a['s'], 'missing pending bits rejected')
    b = next(x for x in records if x['parameters'][:5] == [1,8,1,2,3])
    require(b['measured'] > b['p']+2*b['r']+b['m'], 'missing pending mid rejected')
    require(b['measured'] > b['peak_count'], 'LEFT-only cleared backing rejected')
    count += 3
    try:
        load_source()
    except ValueError as error:
        require('already loaded' in str(error), 'preload control reason')
        count += 1
    else:
        raise ValueError('preloaded source accepted')
    return count


def check_receipt(expected, actual):
    require(json.dumps(expected, sort_keys=True) == json.dumps(actual, sort_keys=True),
            'typed deterministic receipt')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    rt = load_source()
    records = [fixture(rt, *values) for values in cases()]
    result = dict(status='PASS_SELECTED_ADD_COUNTER_BACKING', cases=len(records),
                  controls=controls(rt, records), records=records)
    escaped = fixture(rt,1,1,1,3,3,1,32,escape=True)
    require(escaped['measured'] > max(escaped['intrinsic'],64), 'callback escape violates phase max')
    result['callback_escape_counterexample'] = escaped
    result['controls'] += 1
    data = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.write:
        with args.write.open('x') as destination:
            require(destination.write(data) == len(data), 'complete receipt write')
    else:
        check_receipt(json.loads((ROOT/'RESULT.json').read_text()), result)
    print(json.dumps({key: value for key,value in result.items() if key != 'records'}, sort_keys=True))


if __name__ == '__main__':
    main()
