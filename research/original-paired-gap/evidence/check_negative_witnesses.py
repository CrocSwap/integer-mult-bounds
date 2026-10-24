"""Find native character witnesses for the wrapper mutation controls.

This check uses only the declared cold package and its isolated Git data.
It evaluates formal differences with the actual native line eigenvalues.
"""

from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--package', type=Path, required=True)
parser.add_argument('--repo', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
package = args.package


def load(name):
    spec = importlib.util.spec_from_file_location(name, package / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source, pair_check = load('source_data'), load('verify_pair')
local = source.load_local(args.repo)
word = local['CANONICAL-WORD.json.gz']
original = local['LOCAL-PROGRAMS.json.gz']
cores = json.loads(gzip.decompress((package / 'data/FULL-MODE-PROGRAMS.json.gz').read_bytes()))
packet = json.loads(gzip.decompress((package / 'data/PAIRED-PROGRAMS.json.gz').read_bytes()))
boundary = source.replay(original['forward'], cut=original['forward'].index(['phase', 'centers']))
r = [{p: value for p, value in boundary[c].items() if p < 112} for c in word['centers']]
k = [{j: row[p] / 4 for j, row in enumerate(r) if p in row} for p in range(112)]
identity = [{(i, ()): Q(1)} for i in range(1408)]


def witness(actual, expected):
    differences = []
    for i, (left, right) in enumerate(zip(actual, expected)):
        diff = dict(left)
        pair_check.add(diff, right, -1)
        if diff:
            differences.append((i, diff))
    for character in range(512):
        for row, diff in differences:
            value = {}
            for (column, operators), coefficient in diff.items():
                power = sum(e * ((word['ports'][p] & character).bit_count() % 2)
                            for p, e in operators) % 4
                a, b = value.get(column, (Q(0), Q(0)))
                dr, di = ((1, 0), (0, 1), (-1, 0), (0, -1))[power]
                value[column] = a + coefficient * dr, b + coefficient * di
            for column, error in sorted(value.items()):
                if error != (0, 0):
                    return {'character': character, 'output_coordinate': row,
                            'input_coordinate': column, 'nonzero_error': [str(x) for x in error]}
    raise ValueError('No actual native character rejects this mutation')


reports = {}
for direction in ('forward', 'backward'):
    core_map = source.replay(cores[direction])[:704]
    parts = packet['programs'][direction]
    expected = pair_check.formula(identity, direction, r, k)
    controls = {'missing_input_graph': {'prefix': [], 'suffix': parts['suffix']},
                'missing_translations': {side: [e for e in parts[side]
                                               if e['kind'] != 'physical_translation']
                                         for side in ('prefix', 'suffix')}}
    if direction == 'backward':
        controls['mode_preload_before_old_mode_read'] = {
            'prefix': parts['prefix'][-896:] + parts['prefix'][:-896], 'suffix': parts['suffix']}
    else:
        controls['target_correction_before_mode_update'] = {
            'prefix': parts['prefix'], 'suffix': parts['suffix'][896:] + parts['suffix'][:896]}
    reports[direction] = {name: witness(pair_check.run_pair(mutant, core_map, identity, word), expected)
                          for name, mutant in controls.items()}

report = {'status': 'PASS_ACTUAL_NATIVE_NEGATIVE_WITNESSES', 'controls': reports,
          'native_eigenvalue': 'C_p has eigenvalue i^parity(character & port_label)',
          'arithmetic': 'Exact rational real and imaginary parts',
          'scope': 'Each wrapper mutation fails on an actual spatial Fourier character at tensor depth one',
          'inherited': 'Formal row generation uses the declared package; character evaluation is new review code'}
args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(json.dumps(report, indent=2, sort_keys=True))
