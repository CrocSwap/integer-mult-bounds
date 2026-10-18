# Adapted from Chi Zhao's PR636 declarative-input check; OpenAI Codex assisted.
"""Check that declarative inputs and outputs exactly reconstruct the replay SPEC."""
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parent
read = lambda name: json.loads((P / 'data' / name).read_bytes())

def need(value, message):
    if not value:
        raise ValueError(message)

def merge(a, b):
    need(all(a[k] == b[k] for k in a.keys() & b.keys()), 'conflicting declaration')
    return a | b

w, e, s, plan = map(read, ('WITNESS.json', 'EXPECTED.json', 'SPEC.json', 'PLAN.json'))
need((w['schema'], e['schema'], s['schema']) == ('witness/1', 'witness-expected/1', 'witness-spec/1'), 'schemas')
need(w['geometry'] == dict(v=112, h=9, helpers=480, centres=8, stages=9, replicas=8,
                           cold_helpers=[258, 270, 282, 294]), 'fixed native geometry')
need(hashlib.sha256((P / 'data/WITNESS.json').read_bytes()).hexdigest() == e['witness_sha256'], 'witness hash')
need(w['name'] == s['name'], 'name')
for key in ('data', 'call_order'):
    need(w[key] == s[key], key)
need(sorted(w['dispatch']) == sorted(s['dispatch']), 'same complete dispatch')
need(len({(stage, replica) for stage, replica, _ in w['dispatch']}) == len(w['dispatch']), 'unique dispatch keys')
need(w['dispatch'] == [[c['stage'], c['replica'], c['provider']] for c in plan['provider_calls']], 'literal dispatch')
need(w['call_order'] == plan['order'], 'literal chronology')
for name, filename in (('plan_sha256', 'PLAN.json'), ('owners_sha256', 'OWNERS.json.gz')):
    need(hashlib.sha256((P / 'data' / filename).read_bytes()).hexdigest() == w['data'][name], filename)
need(merge(e['global'], {'gain_baseline_kappa': w['gain_baseline_kappa']}) == s['expected'], 'global outputs')
provider_outputs = {}
for pid, declaration in e['providers'].items():
    declaration = dict(declaration)
    for group in ('artifacts', 'expected_local'):
        nested = declaration.pop(group)
        declaration = merge(declaration, {group + '.' + key: value for key, value in nested.items()})
    provider_outputs[pid] = declaration
need(provider_outputs == s['providers'], 'provider outputs with literal dotted receipt keys')
need(s['width_spot_helpers'] == w['geometry']['cold_helpers'], 'mapped width spot helpers')
build = dict(w['build'])
need(set(e['build']) == set(w['build']['providers']) | set(w['build']['shadows']), 'all provider and shadow outputs')
for group in ('providers', 'shadows'):
    build[group] = {}
    for pid, declaration in w['build'][group].items():
        a, b = dict(declaration), dict(e['build'][pid])
        left, right = a.pop('steps'), b.pop('steps')
        base_outputs = {'content_sha256': b.pop('base_content_sha256')}
        if 'helper_map_sha256' in b:
            base_outputs['helper_map_sha256'] = b.pop('helper_map_sha256')
        a['base'] = merge(a['base'], base_outputs)
        need(len(left) == len(right), 'construction step count')
        build[group][pid] = merge(a, b)
        build[group][pid]['steps'] = [merge(x, y) for x, y in zip(left, right)]
need(build == s['build'], 'complete typed build with shadows')
print('PASS declarative inputs and outputs reconstruct SPEC', flush=True)
