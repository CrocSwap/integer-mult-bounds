"""lift16.py BASE8 PLAN8 OWNERS8 OWNERS16 OUT
Generic T16 lift (after #858 build_parent.py): direct-sum two-bank parent, actual
source-event windows, T16 PLAN with profile recomputed from the T16 owner map.
BASE8 = bound T8 global base (has split-centres/GLOBAL-TEMPLATE.json.gz)."""
import copy, gzip, hashlib, json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_parent import lift_parent, actual_windows, read, canonical, portable_gzip, sha, content_sha, require


def idle_profile(owners, windows):
    used = {}
    for r in owners:
        key = (r['owner_replica'], r['child'], r['port'])
        cells = used.setdefault(key, set())
        new = set(range(r['offset'], r['offset'] + r['width']))
        require(not cells & new, 'overlap')
        cells |= new
    idle = Counter()
    for key, (cap, _) in windows.items():
        rep, ch = map(int, key.split(','))
        for port in range(112):
            c = used.get((rep, ch, port), set())
            require(c == set(range(len(c))), 'non-prefix')
            if len(c) < cap:
                idle[cap - len(c)] += 1
    return idle


def interleave(order8):
    return [[s, r + 8 * g] for s, r in order8 for g in range(2)]


def lift_plan(source, parent, owners8, owners, plan_sha, owners8_sha, owners_sha):
    p = copy.deepcopy(source)
    require(source['T'] == 8 and len(source['order']) == 72, 'source plan dimensions')
    order = interleave(source['order'])
    windows, schedule = actual_windows(parent, order)
    idle8 = idle_profile(owners8, source['windows'])
    paid = Counter({int(k): v for k, v in source['profile'].items()})
    paid.subtract(idle8)
    require(all(v >= 0 for v in paid.values()), 'T8 idle not within profile')
    idle16 = idle_profile(owners, windows)
    prof = Counter({k: 2 * v for k, v in paid.items()})
    prof.update(idle16)
    prof = +prof
    p.update(status='FROZEN_EXPLICIT_T16_TWO_BANK_DIRECT_SUM_OWNER_NOMINATION',
             mode='gauge44-all144-t16-idle-concentration', T=16, live=14336, deficit=5120,
             profile={str(k): prof[k] for k in sorted(prof)}, order=order, windows=windows,
             solver_status='exact pattern-flow LNS on the T16 actual-window geometry', gap=None,
             source_plan_sha256=plan_sha, source_owners_sha256=owners8_sha,
             assignment_sha256=owners_sha, assignment_content_sha256=content_sha(owners))
    for field in ('provider_calls', 'per_call_widths'):
        p[field] = []
        for old in source[field]:
            for group in range(2):
                new = copy.deepcopy(old)
                new['replica'] += 8 * group
                if 'time' in new:
                    new['time'] = 2 * old['time'] + group
                p[field].append(new)
    at = {tuple(x): i for i, x in enumerate(order)}
    for field in ('provider_calls', 'per_call_widths'):
        p[field].sort(key=lambda c: at[c['stage'], c['replica']])
    p['replica_lift'] = dict(groups=2, source_replicas=8, replicas=16,
                             parent_template_content_sha256=content_sha(parent), owners_file_sha256=owners_sha,
                             window_semantics='strict physical source-event touch intervals, including bridges',
                             schedule_content_sha256=content_sha(schedule))
    require(len(owners) == 144 * len(source['provider_registry']['gauge44']['widths']), 'owner role count')
    for role in owners:
        require(role['time'] == at[role['stage'], role['replica']], 'role call time')
        require(role['time'] in windows[f"{role['owner_replica']},{role['child']}"][1], 'owner outside actual window')
    require(sum(int(k) * v for k, v in p['profile'].items()) == 73 * p['live'] - p['deficit'], 'rank mass')
    return p, schedule, idle8, idle16


def main(base, plan8p, own8p, own16p, out):
    base, out = Path(base), Path(out)
    require(not out.exists(), 'out exists')
    src_path = base / 'split-centres/GLOBAL-TEMPLATE.json.gz'
    source = read(src_path)
    plan8 = read(plan8p)
    require(lift_parent(source, 1) == source, 'T8 identity control')
    require(actual_windows(source, plan8['order'])[0] == plan8['windows'], 'T8 source-window replay')
    require(source['exact_data_phase_recipe_sha256'] == sha(base / 'work/complex-nine-native/DATA-PHASES.json'), 'data-phase binding')
    parent = lift_parent(source)
    owners8, owners = read(own8p), read(own16p)
    plan, schedule, idle8, idle16 = lift_plan(plan8, parent, owners8, owners, sha(plan8p), sha(own8p), sha(own16p))
    out.mkdir(parents=True)
    (out / 'GLOBAL-TEMPLATE.json.gz').write_bytes(portable_gzip(canonical(parent)))
    (out / 'PLAN.json').write_bytes((json.dumps(plan, indent=2) + '\n').encode())
    rec = dict(status='PASS_T16_DIRECT_SUM_PARENT_AND_LITERAL_SOURCE_WINDOWS', T8_identity_control=True,
               T8_source_window_identity=True, idle8=dict(sorted(idle8.items())), idle16=dict(sorted(idle16.items())),
               profile=plan['profile'], parent_live=parent['live'], parent_physical=parent['physical'],
               actual_window_membership_checked=len(owners), events=len(schedule))
    (out / 'PARENT-LIFT-RECEIPT.json').write_text(json.dumps(rec, indent=2) + '\n')
    print(json.dumps(rec))


if __name__ == '__main__':
    main(*sys.argv[1:6])
