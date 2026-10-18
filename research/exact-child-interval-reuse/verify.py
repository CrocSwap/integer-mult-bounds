"""Exact replay/guard checks for the opt-in child-interval session.

No persisted proof-result cache. Gareth Davidson / OpenAI Codex, Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from session import Session, canonical, freeze, need


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def reject(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(Path(path).read_bytes(), object_pairs_hook=pairs, parse_constant=reject)


def paths_and_pins(root=ROOT):
    files = [x for x in read(HERE / 'SOURCES.json')['files'] if x['usage'] == 'input']
    need({x['path'] for x in files} == {'research/complex-local-word-ceiling/ceiling.py',
                                      'research/complex-local-word-ceiling/levers.py'}, 'complete input roles')
    by_role = {('engine' if x['path'].endswith('/ceiling.py') else 'fixture'): x for x in files}
    paths = [root / by_role[k]['path'] for k in ('engine', 'fixture')]
    return paths, {k: v['sha256'] for k, v in by_role.items()}


def equivalent(reference, optimized, name, *args, **kwargs):
    def run(session):
        try:
            value = session.invoke(name, *args, **kwargs)
            return {'value': freeze(value)}
        except (ValueError, AttributeError, TypeError) as error:
            return {'error': [type(error).__name__, str(error)]}
    a, b = run(reference), run(optimized)
    need(canonical(a) == canonical(b), 'changed operation result: ' + name)
    need(canonical(reference.events) == canonical(optimized.events), 'changed complete operation trace: ' + name)
    return a, dict(optimized.counts)


def functional():
    paths, pins = paths_and_pins()
    reference = Session(*paths, pins, reuse=False)
    cached = Session(*paths, pins, reuse=True)
    stdout = reference.fixture();events = list(reference.events);baseline = reference.evidence(stdout)
    out = cached.fixture();fill = cached.evidence(out)
    need(canonical(cached.events) == canonical(events) and out == stdout, 'initial-fill complete trace')
    out = cached.fixture();warm = cached.evidence(out)
    need(canonical(cached.events) == canonical(events) and out == stdout, 'warm complete trace')
    need(warm['cache_counts'].get('misses', 0) == 0 and warm['cache_counts']['hits'] ==
         baseline['event_counts']['child_cost'], 'every repeated interval reused')
    expected_counts = {'ceiling': 7, 'child_cost': 1238, 'model': 263, 'relax': 263}
    need(baseline['event_counts'] == expected_counts, 'unchanged seven-lever coverage')
    controls = []
    ordinary = Session(*paths, pins, reuse=False)
    guarded = Session(*paths, pins, reuse=True, max_entries=2)
    keys = [(1, 73, Q(1, 1000)), (2, 73, Q(1, 1000)),
            (1, 74, Q(1, 1000)), (1, 73, Q(1, 999))]
    for args in keys:
        result, stats = equivalent(ordinary, guarded, 'child_cost', *args)
        need('value' in result and stats.get('misses') == 1, 'new exact key recomputed')
    controls.append('rank, modulus and exact exponent separate keys')
    result, stats = equivalent(ordinary, guarded, 'child_cost', *keys[-1])
    need(stats.get('hits') == 1, 'repeat key should hit')
    result, stats = equivalent(ordinary, guarded, 'child_cost', *keys[0])
    need(stats.get('misses') == 1 and stats.get('evictions') == 1, 'bounded LRU eviction')
    controls.append('bounded eviction recomputes the displaced interval')
    # Fraction(0) and float(0) compare equal in Python but have different behavior.
    equivalent(ordinary, guarded, 'child_cost', 1, 73, Q(0))
    result, stats = equivalent(ordinary, guarded, 'child_cost', 1, 73, 0.0)
    need('error' in result and not stats.get('hits'), 'numeric type alias bypass')
    controls.append('equal-valued float cannot reuse a Fraction result')
    result, stats = equivalent(ordinary, guarded, 'child_cost', r=1, m=73, a=Q(1, 1000))
    need('value' in result and stats.get('uncached') == 1, 'keyword fallback retains original behavior')
    controls.append('unsupported key forms use the original operation')
    word = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    # The original model/guards run again even when all relevant weights were warm.
    for label, local, extra in [
        ('changed local profile recomputes its ceiling', {**word, 1: 2413}, {}),
        ('invalid halving cap rejected after warming', word, {'R': 52}),
        ('excess local mass rejected after warming', {72: 1000}, {}),
        ('negative count rejected after warming', {1: -1}, {}),
    ]:
        result, stats = equivalent(reference, cached, 'ceiling', local, 73, 896, 9, 64,
                                   grid=Q(1, 10**12), **extra)
        need(('error' in result) == label.startswith(('invalid', 'excess', 'negative')), 'expected model boundary')
        controls.append(label)
    # Source checks use full bytes, not path, length or timestamp.
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        copied = [folder / p.name for p in paths]
        for a, b in zip(paths, copied):shutil.copyfile(a, b)
        altered = Session(*copied, pins)
        altered.invoke('child_cost', *keys[0])
        for index, old_token, new_token in [(0, b'Packing-independent', b'packing-independent'),
                                           (1, b'Ideal one-at-a-time', b'ideal one-at-a-time')]:
            path = copied[index];raw = path.read_bytes();st = path.stat()
            need(raw.count(old_token) == 1 and len(old_token) == len(new_token), 'mutation site')
            path.write_bytes(raw.replace(old_token, new_token));os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))
            try:
                altered.invoke('child_cost', *keys[0])
            except ValueError as error:
                need(str(error) == 'source changed: ' + ('engine' if index == 0 else 'fixture'), 'correct source rejection')
                need(not altered._weights, 'changed source clears memoized values')
            else:
                raise ValueError('same-size same-mtime source change accepted')
            path.write_bytes(raw);os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))
            altered.invoke('child_cost', *keys[0])
            need(altered.counts.get('misses') == 1, 'restored source recomputes')
        controls.append('engine and fixture changes reject despite equal size and mtime')
    guarded.invoke('child_cost', *keys[0]);guarded._module.PREC -= 1
    try:
        guarded.invoke('child_cost', *keys[0])
    except ValueError as error:
        need(str(error) == 'precision context changed' and not guarded._weights, 'precision guard')
    else:
        raise ValueError('precision mutation accepted')
    guarded._module.PREC += 1
    equivalent(ordinary, guarded, 'child_cost', *keys[0])
    need(guarded.counts.get('misses') == 1, 'precision restoration recomputes')
    controls.append('precision changes reject and clear prior intervals')
    original = guarded._module.exp
    guarded._module.exp = lambda lo, hi: (Q(0), Q(0))
    try:
        guarded.invoke('child_cost', *keys[0])
    except ValueError as error:
        need(str(error) == 'engine binding changed' and not guarded._weights, 'function dependency guard')
    else:
        raise ValueError('function replacement accepted')
    guarded._module.exp = original
    equivalent(ordinary, guarded, 'child_cost', *keys[0])
    controls.append('function dependency replacement rejects before a hit')
    # Explicitly test isolation from an existing import sentinel, including None.
    marker = object();saved = sys.modules.get('ceiling', marker);old_path = list(sys.path)
    try:
        sys.modules['ceiling'] = None
        cached.fixture()
        need('ceiling' in sys.modules and sys.modules['ceiling'] is None and sys.path == old_path,
             'import context restored')
    finally:
        if saved is marker:sys.modules.pop('ceiling', None)
        else:sys.modules['ceiling'] = saved
    controls.append('fixture restores its import alias and search path')
    result = {'schema': 'exact-child-interval-reuse/1', 'status': 'PASS_EXACT_CHILD_INTERVAL_REUSE',
              'source_sha256': pins, 'precision': 256, 'baseline': baseline,
              'initial_fill': fill, 'warm': warm, 'controls': controls,
              'persistent_cache': False, 'model_and_bisection_replayed': True,
              'selected_full_replay_speed_claim': False, 'new_kappa_claim': False}
    return result, events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit-result', type=Path)
    args = parser.parse_args()
    need(args.emit_result is None or not args.emit_result.exists(), 'output already exists')
    result, _ = functional()
    if args.emit_result:
        with args.emit_result.open('x') as f:json.dump(result, f, indent=2, sort_keys=True);f.write('\n')
    else:
        need(canonical(result) == canonical(read(HERE / 'RESULT.json')), 'complete typed receipt differs')
    print(result['status'], 'child_calls=1238', 'model_checks=263', 'ceilings=7',
          'controls=' + str(len(result['controls'])), 'no_new_kappa')


if __name__ == '__main__':
    main()
