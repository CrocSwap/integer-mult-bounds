#!/usr/bin/env python3
"""Bounded finite grid and positive-envelope audit; no physical admission.

Runs only after separate authorization. Uses pinned attributed engines, with
explicit, counted adaptations; see README.md. Does not mutate source inputs.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
import resource
import signal
import sys
import time
from fractions import Fraction
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
V = HERE / 'vendor'
PINS = {
    'derive_grid.py': 'ceb7a44ef19d72a16db7b43c65c85910d965499d1715436011de32af5d39dbb0',
    'independent_bounds.py': '198521def614fe78fa728f1dde2b7fb820c0c0e0ac3ad0c9224dccbf51eac0d5',
    'envelopes.py': '783da6b5b450fc07434946cb9ec86070dfee01df6b5fa1c385cb024def2c9a9f',
    'source_binding.py': '624c459311c58f3847b7713b818bfd340153abf42919f02ac9aa8892ed52a2bd',
    'ODD-TYPE-AB-CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'ODD-CALLER-EXACT-GRID.json': '87d25d9fa3778bf4784e3a9e17f32ce5ba372663c6e97392cc62b87e6719042c',
}
WORD_COMPRESSED = 'de43ed04f58133eaef8f8d12a9dae1e6e8aa7f9721044200cc839673d86fd7c1'
WORD_RAW = '6a472688bdf2a1b293df0f4f77427a04a1f87c92fedb5b5a6921cc850c272b4f'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def module(name, path, replacements=()):
    text = path.read_text()
    edits = []
    for old, new, count in replacements:
        if text.count(old) != count:
            raise ValueError('adapter occurrence mismatch: ' + old)
        text = text.replace(old, new)
        edits.append({'old': old, 'new': new, 'count': count})
    obj = ModuleType(name)
    obj.__file__ = str(path)
    sys.modules[name] = obj
    exec(compile(text, str(path), 'exec'), obj.__dict__)
    return obj, {'source_sha256': digest(path.read_bytes()), 'adapted_sha256': digest(text.encode()), 'edits': edits}

def main():
    if not __debug__:
        raise RuntimeError('assertions required')
    ap = argparse.ArgumentParser()
    ap.add_argument('--word', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--cpu-seconds', type=int, default=1800)
    ap.add_argument('--wall-seconds', type=int, default=2100)
    args = ap.parse_args()
    if not 1 <= args.cpu_seconds <= 1800 or not 1 <= args.wall_seconds <= 2100:
        raise ValueError('requested limits exceed frozen scope')
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (args.cpu_seconds, args.cpu_seconds + 1))
    signal.alarm(args.wall_seconds)
    for name, pin in PINS.items():
        if digest((V / name).read_bytes()) != pin:
            raise ValueError('source pin mismatch: ' + name)
    compressed = args.word.read_bytes()
    if digest(compressed) != WORD_COMPRESSED:
        raise ValueError('only pinned #7641 word is authorized')
    raw = gzip.decompress(compressed)
    if digest(raw) != WORD_RAW:
        raise ValueError('decompressed source mismatch')
    w = json.loads(raw)
    canonical = digest(json.dumps(w, sort_keys=True, separators=(',', ':')).encode())
    caller_bytes = (V / 'ODD-TYPE-AB-CALLER.json').read_bytes()
    c = json.loads(caller_bytes)
    cg = json.loads((V / 'ODD-CALLER-EXACT-GRID.json').read_bytes())
    if cg['caller_sha256'] != digest(caller_bytes):
        raise ValueError('caller grid is not bound to this caller')
    start = time.monotonic()
    rational, rational_pin = module('resource_rational_grid', V / 'derive_grid.py')
    derived, rows = rational.derive(w)
    del rows
    integer, int_pin = module('resource_integer_grid', V / 'independent_bounds.py')
    wg = integer.word_run(w, scale=derived['odd_scale'], frac=derived['fractional_bits'])
    if (wg['odd_scale_lcm'], wg['dyadic_height'], Fraction(wg['maximum_scaled_mass'])) != (
        derived['odd_scale'], derived['fractional_bits'], Fraction(derived['scaled_maximum_mass'])):
        raise ValueError('independent rational/integer grids disagree')
    binding, binding_pin = module('source_binding', V / 'source_binding.py')
    changes = [
        ('elif op in ("LAMBDA", "IDLE_ONE"):', 'elif op in ("LAMBDA", "IDLE_ONE", "IDLE_ODD"):', 2),
        ('all(0 <= r < 38 for r in ar) and all(38 <= r < 76 for r in br[:2])', 'all(caller["types"]["A"]["offset"] <= r < caller["types"]["A"]["offset"] + caller["types"]["A"]["roles"] for r in ar) and all(caller["types"]["B"]["offset"] <= r < caller["types"]["B"]["offset"] + caller["types"]["B"]["roles"] for r in br[:2])', 1),
        ('all(1 <= k <= 18 for k in e[3])', 'all(1 <= k <= caller["stages"] for k in e[3])', 1),
        ('need(j_order == list(range(1, 19)), "exact eighteen native calls")', 'need(j_order == list(range(1, caller["stages"] + 1)), "all chronological native calls")', 1),
        ('word["public"] - len(mains) == 1061', 'word["public"] - len(mains) == expected_helper_count', 1),
        ('physical_main_inputs=3952, fresh_arbitrary_helpers=18 * 1061,', 'physical_main_inputs=sum(t["roles"] * len(t["ports"]) for t in caller["types"].values()), fresh_arbitrary_helpers=caller["stages"] * expected_helper_count,', 1),
        ('need(len(e[3]) == len(set(e[3]))', 'need(op != "IDLE_ODD" or (len(e[3]) == 1 and e[4] == -1), "signed child signature")\n                    need(len(e[3]) == len(set(e[3]))', 1),
        ('(life, peak, owned_count) == (54, 43, 51)', '(life, peak, owned_count) == (234, 50, 68)', 1),
    ]
    # The only lifecycle change is an explicit literal source contract; no
    # coefficient, copy, chart, rounding or backward-witness guard is relaxed.
    env, env_pin = module('resource_envelopes', V / 'envelopes.py', changes)
    mains = set(w['live']) | {r + 112 for r in w['live']} | set(w['hosted']['X2']) | set(w['hosted']['Y2'])
    env.expected_helper_count = w['public'] - len(mains)
    wp, wr = env.native_envelope(w)
    cp, cr = env.caller_envelope(c, wp, w)
    height = cg['grid_exponents'][0] + wg['dyadic_height']
    mass = binding.strict_power(cp['M_context'][0]) + cg['caller_odd_scale_bits'] + derived['odd_scale'].bit_length()
    context = 2 * max(height, mass)
    result = {'status': 'FINITE_GRID_AND_ENVELOPE_ONLY', 'compressed_word_sha256': digest(compressed),
        'decompressed_sha256': digest(raw), 'canonical_word_sha256': canonical,
        'caller_sha256': digest(caller_bytes), 'source_pins': PINS,
        'engines': {'rational': rational_pin, 'integer': int_pin, 'binding': binding_pin, 'envelope': env_pin},
        'rational_grid': derived, 'integer_grid': wg, 'native_envelope': wr,
        'caller_envelope': cr, 'caller_grid_carried_from_matching_caller': cg,
        'context_height': height, 'context_mass_bits': mass, 'context_c': context,
        'context_le_4096': context <= 4096, 'prior_7637_context': 2458,
        'elapsed_seconds': time.monotonic() - start,
        'scope': 'Conditional positive rounded envelopes and fixed scalar grid; no physical supplier, full signed application, ordinary or fixed-tape qualification.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as f:
        json.dump(result, f, indent=2, default=str)
        f.write('\n')
    print(json.dumps({'status': result['status'], 'context_c': context, 'le_4096': context <= 4096}))

if __name__ == '__main__':
    main()
