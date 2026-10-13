"""Check that declarative inputs and outputs exactly reconstruct the replay SPEC."""
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parents[1]
read = lambda name: json.loads((P / 'data' / name).read_bytes())

def need(value, message):
    if not value:
        raise ValueError(message)

def merge(a, b):
    need(all(a[k] == b[k] for k in a.keys() & b.keys()), 'conflicting declaration')
    return a | b

w, e, s, plan = map(read, ('WITNESS.json', 'EXPECTED.json', 'SPEC.json', 'PLAN.json'))
need((w['schema'], e['schema'], s['schema']) == ('witness/1', 'witness-expected/1', 'witness-spec/1'), 'schemas')
need(w['geometry'] == dict(v=112, h=9, helpers=504, centres=8, stages=9, replicas=8,
                           cold_helpers=[270, 282, 294, 306]), 'fixed native geometry')
need(hashlib.sha256((P / 'data/WITNESS.json').read_bytes()).hexdigest() == e['witness_sha256'], 'witness hash')
need(w['name'] == s['name'], 'name')
for key in ('data', 'call_order'):
    need(w[key] == s[key], key)
need(sorted(w['dispatch']) == s['dispatch'], 'canonical dispatch')
need(len({(stage, replica) for stage, replica, _ in w['dispatch']}) == len(w['dispatch']), 'unique dispatch keys')
need(w['dispatch'] == [[c['stage'], c['replica'], c['provider']] for c in plan['provider_calls']], 'literal dispatch')
need(w['call_order'] == plan['order'], 'literal chronology')
for name, filename in (('plan_sha256', 'PLAN.json'), ('owners_sha256', 'OWNERS.json.gz')):
    need(hashlib.sha256((P / 'data' / filename).read_bytes()).hexdigest() == w['data'][name], filename)
need(merge(e['global'], {'gain_baseline_kappa': w['gain_baseline_kappa']}) == s['expected'], 'global outputs')
need(e['providers'] == s['providers'], 'provider outputs')
build = dict(w['build'])
build['providers'] = {}
need(set(w['build']['providers']) == set(e['build']), 'build providers')
for pid, declaration in w['build']['providers'].items():
    a, b = dict(declaration), dict(e['build'][pid])
    left, right = a.pop('steps'), b.pop('steps')
    a['base'] = merge(a['base'], {'content_sha256': b.pop('base_content_sha256')})
    need(len(left) == len(right), 'construction step count')
    build['providers'][pid] = merge(a, b)
    build['providers'][pid]['steps'] = [merge(x, y) for x, y in zip(left, right)]
need(build == s['build'], 'complete typed build')
print('PASS declarative inputs and outputs reconstruct SPEC', flush=True)
