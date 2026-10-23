#!/usr/bin/env python3
"""Independent lead-2 full-word control; exact Gaussian integer tuples."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import random

COMMIT = '80a2ab05c58b6a7e2050567ce12aae67bcf334cd'
parser = argparse.ArgumentParser()
parser.add_argument('root', type=Path)
args = parser.parse_args()
root = args.root.resolve()

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, root / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Authenticate the retained input closure before executing predecessor helpers.
manifest = json.loads((root / 'research/three-kappa-leads/SOURCES.json').read_text())
dependencies = []
for item in manifest['files']:
    raw = (root / item['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['sha256'], item['path']
    dependencies.append({'path': item['path'], 'sha256': item['sha256']})

source = load('research/rank7-idle-star-stream-obstruction/source.py', 'source')
physical = load('research/idle-star-paired-axis-census/verify.py', 'physical')
context = source.load_context()
axes = [list(map(int, child['orthogonal_axes'])) for child in context['recipe']['idle_children']]
used = {i: set() for i in range(20)}
hosts = {}
for time, helper, owner, child, port, offset in context['rows']:
    stage, replica = context['order'][time]
    provider = context['dispatch'][stage, replica % 74]
    width = context['providers'][provider]['widths'][helper]
    used[child].update(range(offset, offset + width))
    stream = 2 * context['plan']['pairs'][str(child)] + context['plan']['sides'][str(child)]
    hosts.setdefault(time, []).append((stream, axes[child][offset:offset + width]))
context['hosts'] = hosts
residual = {i: [axis for j, axis in enumerate(basis) if j not in used[i]]
            for i, basis in enumerate(axes)}
changed_residual = {i: list(basis) for i, basis in residual.items()}
delta = 0
for axis in residual[12][:4]:
    delta ^= axis
changed_residual[12][:4] = [delta ^ axis for axis in residual[12][:4]]
assert len(residual[12]) == 48
assert residual[12][:4] == [1 << i for i in range(25, 29)]
blocks = physical.stage_blocks(context['template'])
original = physical.run_data_event
final_bridge = {'kind': 'bridge', 'src': 0, 'dst': 1, 'coefficient': 1}
assert sum(event == final_bridge for event in context['template']['execution_schedule']) == 1

def corrected_event(matrix, event, ctx, residual_axes, character):
    if event == final_bridge:
        physical.phase(matrix, 0, 2 * physical.parity(character, delta))
    original(matrix, event, ctx, residual_axes, character)

rng = random.Random(87)
characters = [sum(1 << (25 + i) for i in range(4) if mask >> i & 1) for mask in range(16)]
characters += [rng.getrandbits(73) for _ in range(32)]
cases = []
for character in characters:
    physical.run_data_event = original
    baseline = physical.replay(context, residual, character, blocks)
    uncorrected = physical.replay(context, changed_residual, character, blocks)
    physical.run_data_event = corrected_event
    corrected = physical.replay(context, changed_residual, character, blocks)
    assert corrected == baseline, character
    cases.append({'character': character, 'corrected_matches': corrected == baseline,
                  'unchanged_bridge_fails': uncorrected != baseline})
physical.run_data_event = original
failures = sum(case['unchanged_bridge_fails'] for case in cases)
assert failures == 18
print(json.dumps({
    'status': 'PASS', 'reviewed_commit': COMMIT,
    'scope': 'owner0/port0 complete eight-stream data word; finite controls, not all-character proof',
    'arithmetic': 'exact Gaussian integer pairs in predecessor physical interpreter',
    'construction': 'child12 complement-of-one four-frame; X0 translation immediately before final bridge',
    'seed': 87, 'cases_checked': len(cases), 'unchanged_bridge_failures': failures,
    'dependency_note': 'Uses retained source.load_context and census physical interpreter, not bridge_screen.py. Source helper additionally authenticates its retained closure and complete PR3148 fill digest.',
    'authenticated_manifest': 'research/three-kappa-leads/SOURCES.json',
    'dependencies': dependencies, 'cases': cases,
}, indent=2, sort_keys=True))
