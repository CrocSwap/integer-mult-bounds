"""Mutant coverage of the selected final stage's controller/owner audit.

Runs the pinned PR1087 `code/audit_allcold.py` (sha256 1467a2ac...) unchanged and in-process on the
selected #1094 hosted template archived in research/community-frontier1094-audit/selected-replay.tar.gz.
It then records, for every shipped mutation control and for new targeted mutants, the exception type and
the line of audit_allcold.py that rejects it, plus a one-field-at-a-time binding census of the template.

Stdlib only; Python 3.10.12+ (tarfile filter='data').  Usage:
  python3 -B research/t16-audit-mutant-coverage/verify.py            # compare with EXPECTED.json
  python3 -B research/t16-audit-mutant-coverage/verify.py --write    # regenerate EXPECTED.json
"""
import argparse, ast, contextlib, gzip, hashlib, io, json, marshal, os, runpy, sys, tarfile, tempfile, traceback
from collections import Counter, defaultdict
from pathlib import Path

assert __debug__, 'assertions must stay enabled'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STAGE = ROOT / 'research/complex-t16-rare-pattern-exchanges'
ARCHIVE = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
AUDIT_SHA = '1467a2acb654e62552c69fb9a7c4c85f70a02120881d222313865058ab71a6cc'
sha = lambda b: hashlib.sha256(b).hexdigest()


def fast_copy(x):
    # JSON data only (dict/list/str/int/bool/None); checked once against the original below.
    return marshal.loads(marshal.dumps(x))


def extract(tmp):
    pins = [f for f in json.loads((HERE / 'SOURCES.json').read_text())['files'] if f['usage'] == 'input']
    assert len(pins) == 5
    for f in pins:
        assert sha((ROOT / f['path']).read_bytes()) == f['sha256'], 'pinned input changed: ' + f['path']
    source = tmp / 'source'
    source.mkdir()
    with tarfile.open(STAGE / 'upstream1087.tar.gz') as t:
        t.extractall(source, filter='data')
    for name in ('OWNERS.json.gz', 'PLAN.json', 'SPEC.json'):  # the stage's three frozen overlays
        (source / 'data' / name).write_bytes((STAGE / 'data' / name).read_bytes())
    script = source / 'code/audit_allcold.py'
    assert sha(script.read_bytes()) == AUDIT_SHA, 'audit_allcold.py is not the pinned PR1087 file'
    g = tmp / 'g'
    prefix = 'candidate/strict/global/'
    with tarfile.open(ARCHIVE) as t:
        members = [m for m in t.getmembers() if m.name.startswith(prefix) and m.isfile()]
        for m in members:
            m.name = m.name[len(prefix):]
        t.extractall(g, members=members, filter='data')
    return source, script, g


def load_audit(source, script, g, tmp):
    os.environ.update(PYTHONINTMAXSTRDIGITS='0', WITNESS_SPEC=str(source / 'data/SPEC.json'))
    for k in ('WITNESS_DISCOVER', 'WITNESS_RECORD'):
        os.environ.pop(k, None)
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    hosted = tmp / 'hosted'
    hosted.mkdir()
    for f in (g / 'hosted').iterdir():
        (hosted / f.name).write_bytes(f.read_bytes())
    report = tmp / 'audit/ASYNC-AUDIT.json'
    sys.argv = [str(script), str(g / 'base'), str(hosted), str(report)]  # no --mutation-controls
    sys.path.insert(0, str(script.parent))
    with contextlib.redirect_stdout(io.StringIO()):
        G = runpy.run_path(str(script), run_name='__main__')
    archived = json.loads((g / 'audit/ASYNC-AUDIT.json').read_text())
    fresh = json.loads(report.read_text())
    assert fresh['mutation_controls_run'] is False and fresh['mutations_rejected'] == []
    same = {k: v for k, v in fresh.items() if k not in ('mutation_controls_run', 'mutations_rejected')}
    assert same == {k: v for k, v in archived.items() if k not in ('mutation_controls_run', 'mutations_rejected')}, \
        'in-process positive audit differs from the archived selected receipt'
    return G, archived


class Runner:
    def __init__(self, G, script):
        self.G, self.script = G, str(script)
        self.lines = Path(script).read_text().splitlines()
        self.base = G['ct']
        assert fast_copy(self.base) == self.base

    def outcome(self, mut):
        q = fast_copy(self.base)
        mut(q)
        if q == self.base:
            return dict(result='NO_OP_MUTANT')
        try:
            self.G['audit'](q)
        except Exception as ex:  # record any rejection, then classify it
            frames = [f for f in traceback.extract_tb(ex.__traceback__) if f.filename == self.script]
            line = frames[-1].lineno if frames else None
            caught = isinstance(ex, (AssertionError, KeyError, IndexError, ValueError, TypeError))
            return dict(result='REJECTED' if caught else 'REJECTED_UNCAUGHT_BY_SHIPPED_HARNESS',
                        exception=type(ex).__name__, line=line,
                        statement=self.lines[line - 1].strip()[:160] if line else None)
        return dict(result='ACCEPTED')


def shipped_controls(G, runner, script):
    text = Path(script).read_text()
    start = text.index('controls=[]\n')
    end = text.index('report=dict(')
    block = text[start:end]
    assert block.count('def reject(name,mut):') == 1
    block = block.replace('def reject(name,mut):', 'def _shipped_reject(name,mut):')
    out = {}

    def reject(name, mut):
        out[name] = runner.outcome(mut)

    G['reject'] = reject
    exec(compile(block, script, 'exec'), G)
    return out


def new_mutants(G):
    ct, V, R, N = G['ct'], G['V'], G['R'], G['N']
    prank, DATA = G['prank'], G['DATA']
    stagepair = {e['stage']: e['pair'] for e in G['parent']['recipe'] if e['kind'] == 'local'}
    es = ct['execution_schedule']
    # Recompute the idle windows and call positions from the literal schedule (same definition as the audit).
    last, windows, callpos, pairs, sides = {}, {}, {}, {}, {}
    for pos, e in enumerate(es):
        if 'replica' not in e:
            continue
        rep = e['replica']
        if e['kind'] == 'local_cover_sweep':
            callpos[e['stage'], rep] = pos
            last[rep, stagepair[e['stage']]] = pos
        elif e['kind'] == 'bridge':
            last[rep, e['src']] = last[rep, e['dst']] = pos
        elif e['kind'] == 'idle_cover_sweep':
            for side, i in enumerate(e['child_indices']):
                if i in prank:
                    pairs[i], sides[i] = e['pair'], side
                    windows[rep, i] = (last.get((rep, e['pair']), -1), pos)

    def helpers():
        for ci, c in enumerate(ct['calls']):
            for h, (fam, route) in enumerate(c['owners'][2 * V:]):
                ownerrep, sub = divmod(fam, 8 * V)
                yield ci, h, fam, route, ownerrep, callpos[c['stage'], c['replica']]

    fams = [{f for f, _ in c['owners']} for c in ct['calls']]

    def move_replica(before):
        for ci, h, fam, route, ownerrep, cp in helpers():
            i = route[1]
            for r2 in range(16):
                if r2 == ownerrep:
                    continue
                lo, hi = windows[r2, i]
                if (cp <= lo if before else cp >= hi):
                    f2 = fam + (r2 - ownerrep) * 8 * V
                    if f2 not in fams[ci]:
                        return ci, h, f2
        raise AssertionError('no window mutant found')

    def set_family(ci, h, f2):
        return lambda q: q['calls'][ci]['owners'][2 * V + h].__setitem__(0, f2)

    m = {}
    m['helper hosted before its idle window opens (owner replica changed only)'] = set_family(*move_replica(True))
    m['helper hosted after its idle child was swept (owner replica changed only)'] = set_family(*move_replica(False))
    # Two width-nine helpers on one idle child of one owner replica: give the later one the earlier offset.
    seen = {}
    pick = None
    for ci, h, fam, route, ownerrep, cp in helpers():
        if route[0] != 3:
            continue
        key = (route[1], ownerrep, fam % V)
        if key in seen and seen[key][2] != route[2]:
            pick = (ci, h, seen[key][2])
            break
        seen.setdefault(key, (ci, h, route[2]))
    assert pick
    m['two helpers overlap axis cells of one idle child'] = \
        lambda q, p=pick: q['calls'][p[0]]['owners'][2 * V + p[1]][1].__setitem__(2, p[2])
    w9 = next((ci, h, route) for ci, h, fam, route, ownerrep, cp in helpers() if route[0] == 3)
    m['width-nine helper runs past its idle child rank'] = \
        lambda q, p=w9: q['calls'][p[0]]['owners'][2 * V + p[1]][1].__setitem__(2, prank[p[2][1]] - 8)
    ent = next((ci, h) for ci, h, fam, route, ownerrep, cp in helpers() if route[0] == 4 and len(route[4]) > 1)
    m['entering helper spectators permuted'] = \
        lambda q, p=ent: q['calls'][p[0]]['owners'][2 * V + p[1]][1][4].reverse()
    flip = lambda fam: fam + (V if (fam // V) % 2 == 0 else -V)  # family = rep*8V + (2*pair+side)*V + port
    side = next((ci, h, flip(fam)) for ci, h, fam, route, ownerrep, cp in helpers() if flip(fam) not in fams[ci])
    m['helper on the other side of its idle pair'] = set_family(*side)
    m['data owner prefix permuted within a call'] = \
        lambda q: q['calls'][0]['owners'].__setitem__(slice(0, 2), [q['calls'][0]['owners'][1], q['calls'][0]['owners'][0]])
    m['call time off by one'] = lambda q: q['calls'][5].__setitem__('time', q['calls'][5]['time'] + 1)
    m['call stage relabelled'] = lambda q: q['calls'][0].__setitem__('stage', 1)
    m['pooled slot copy index changed'] = \
        lambda q: q['hosting']['pooled_slots'][0].__setitem__('copy', q['hosting']['pooled_slots'][0]['copy'] + 1)
    m['pooled slot duplicated over another'] = \
        lambda q: q['hosting']['pooled_slots'].__setitem__(1, dict(q['hosting']['pooled_slots'][0]))
    m['pooled slot time changed'] = \
        lambda q: q['hosting']['pooled_slots'][0].__setitem__('time', q['hosting']['pooled_slots'][0]['time'] + 1)
    m['idle remainder rank plus one'] = lambda q: q['idle_children'][0].__setitem__('rank', q['idle_children'][0]['rank'] + 1)
    m['idle remainder pending offset shifted'] = \
        lambda q: q['idle_children'][0].__setitem__('pending_offset', q['idle_children'][0]['pending_offset'] - 1)
    bridge = next(k for k, e in enumerate(es) if e['kind'] == 'bridge')
    m['bridge event dropped'] = lambda q, k=bridge: q['execution_schedule'].pop(k)
    idle = next(k for k, e in enumerate(es) if e['kind'] == 'idle_cover_sweep')
    m['idle sweep moved one position earlier'] = \
        lambda q, k=idle: q['execution_schedule'].insert(k - 1, q['execution_schedule'].pop(k))
    m['idle sweep levels changed'] = \
        lambda q, k=idle: q['execution_schedule'][k].__setitem__('to_level', q['execution_schedule'][k]['to_level'] + 1)
    m['bridge coefficient negated'] = \
        lambda q, k=bridge: q['execution_schedule'][k].__setitem__('coefficient', -q['execution_schedule'][k]['coefficient'])
    m['global translation charge changed'] = \
        lambda q: q['execution_schedule'][-1].__setitem__('charged_calls_per_cover', DATA - 1)
    m['global events swapped'] = lambda q: q['execution_schedule'].__setitem__(slice(-2, None), q['execution_schedule'][-2:][::-1])
    m['bank padding families restored'] = lambda q: q['bank_padding'].__setitem__('families', [DATA, DATA])
    m['private namespace overlaps live data'] = \
        lambda q: q['private_namespace'].__setitem__('centers', [DATA - 1, q['private_namespace']['centers'][1]])
    m['two helpers per physical family declared'] = lambda q: q['hosting'].__setitem__('max_helpers_per_physical_family_per_call', 2)
    m['one bank declared'] = lambda q: q['hosting']['banks'].__setitem__(0, 1)
    m['source schedule tampered'] = \
        lambda q: q['async_schedule']['source_schedule'][0].__setitem__('stage', 3)
    m['loop order sentence removed'] = lambda q: q.__setitem__('loop_order', 'Follow the schedule.')
    m['local providers gain an extra entry'] = \
        lambda q: q['local_providers'].__setitem__('extra', q['local_providers'][next(iter(q['local_providers']))])
    # Targeted at assertions no earlier mutant reaches.
    ends = {}
    for ci, h, fam, route, ownerrep, cp in helpers():
        key = (route[1], ownerrep, fam % V)
        w = 9 if route[0] == 3 else route[3]
        if key not in ends or route[2] > ends[key][2]:
            ends[key] = (ci, h, route[2], w, route[0])
    gap = next(v for k, v in sorted(ends.items()) if v[4] == 3 and v[2] + v[3] + 1 <= prank[k[0]])
    gc = ct['calls'][gap[0]]
    gslot = next(k for k, z in enumerate(ct['hosting']['pooled_slots'])
                 if (z['stage'], z['replica'], z['helper']) == (gc['stage'], gc['replica'], gap[1]))

    def leave_gap(q, p=gap, k=gslot):  # route and pooled slot move together, as one consistent emitter bug
        q['calls'][p[0]]['owners'][2 * V + p[1]][1][2] = p[2] + 1
        q['hosting']['pooled_slots'][k]['offset'] = p[2] + 1
    m['hosted cells leave a gap in the pending prefix'] = leave_gap
    order = [(c['stage'], c['replica']) for c in ct['calls']]

    def other_time(k):
        r = es[k]['replica']
        return next(t for t, (s, rr) in enumerate(order) if rr == r and t != es[k]['time'])
    loc = next(k for k, e in enumerate(es) if e['kind'] == 'local_cover_sweep')
    m['local sweep retimed to another invocation of its replica'] = \
        lambda q, k=loc, t=other_time(loc): q['execution_schedule'][k].__setitem__('time', t)
    m['bridge retimed to another invocation of its replica'] = \
        lambda q, k=bridge, t=other_time(bridge): q['execution_schedule'][k].__setitem__('time', t)
    m['pooled slot dropped'] = lambda q: q['hosting']['pooled_slots'].pop()
    m['pooled slot names a helper index past R'] = lambda q: q['hosting']['pooled_slots'][0].__setitem__('helper', R)
    m['retired top-level local_programs reintroduced'] = lambda q: q.__setitem__('local_programs', {})
    l0, l1 = [k for k, e in enumerate(es) if e['kind'] == 'local_cover_sweep'][:2]
    assert es[l0]['replica'] != es[l1]['replica']
    m['two local sweeps of different replicas swapped in list order'] = \
        lambda q, a=l0, b=l1: q['execution_schedule'].__setitem__(slice(a, b + 1), [q['execution_schedule'][b]] + q['execution_schedule'][a + 1:b] + [q['execution_schedule'][a]])
    m['bank padding global event moved to the front'] = \
        lambda q: q['execution_schedule'].insert(0, q['execution_schedule'].pop(-2))
    return m


def sentinel(v):
    if isinstance(v, bool):
        return not v
    if isinstance(v, int):
        return v + 1
    if isinstance(v, str):
        return v + ' (mutated)'
    if isinstance(v, list):
        return v + [None]
    if isinstance(v, dict):
        return dict(v, mutated=True)
    return 'mutated'


def census(G):
    ct = G['ct']
    paths = [(k,) for k in ct]
    paths += [('hosting', k) for k in ct['hosting'] if k != 'pooled_slots']
    paths += [('hosting', 'pooled_slots', 0, k) for k in ct['hosting']['pooled_slots'][0]]
    paths += [('async_schedule', k) for k in ct['async_schedule']]
    paths += [('calls', 0, k) for k in ct['calls'][0]]
    paths += [('idle_children', 0, k) for k in ct['idle_children'][0]]
    kinds = {}
    for k, e in enumerate(ct['execution_schedule']):
        kinds.setdefault(e['kind'], k)
    for kind, k in sorted(kinds.items()):
        paths += [('execution_schedule', k, f) for f in ct['execution_schedule'][k]]
    out = {}
    for p in paths:
        def mut(q, p=p):
            x = q
            for s in p[:-1]:
                x = x[s]
            x[p[-1]] = sentinel(x[p[-1]])
        label = '.'.join(str(s) for s in p)
        if p[0] == 'execution_schedule' and len(p) == 3:
            label += ' [' + ct['execution_schedule'][p[1]]['kind'] + ']'
        out[label] = mut
    return out


def assert_lines(script):
    tree = ast.parse(Path(script).read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'audit')
    return sorted({n.lineno for n in ast.walk(fn) if isinstance(n, ast.Assert)})


def downstream_mentions(source, key):
    hits = []
    for rel in ('code/invoice_allcold.py', 'code/assemble.py'):
        text = (source / rel).read_text()
        if "['%s']" % key in text or '"%s"' % key in text or "'%s'" % key in text:
            hits.append(rel)
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='regenerate EXPECTED.json instead of comparing with it')
    a = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='t16-mutant-coverage-') as d:
        tmp = Path(d)
        source, script, g = extract(tmp)
        G, archived = load_audit(source, script, g, tmp)
        runner = Runner(G, script)
        shipped = shipped_controls(G, runner, script)
        assert list(shipped) == archived['mutations_rejected'], 'shipped control names differ from the selected receipt'
        new = {k: runner.outcome(v) for k, v in new_mutants(G).items()}
        # Cross-stage binding that no selected stage checks: the audited template's pooled owner map must be the
        # frozen data/OWNERS.json.gz that lift16 and independent-t16 check, and owner_map_sha256 must name it.
        owners_gz = (STAGE / 'data/OWNERS.json.gz').read_bytes()
        frozen = json.loads(gzip.decompress(owners_gz))
        pooled = G['ct']['hosting']['pooled_slots']
        binding = dict(pooled_slots_equal_frozen_owners=pooled == frozen,
                       owner_map_sha256_names_frozen_gzip=G['ct']['hosting']['owner_map_sha256'] == sha(owners_gz),
                       roles=len(frozen))
        assert binding['pooled_slots_equal_frozen_owners'] and binding['owner_map_sha256_names_frozen_gzip']
        fields = {k: runner.outcome(v) for k, v in census(G).items()}
        lines = assert_lines(script)
        hit = defaultdict(list)
        for group, res in (('shipped', shipped), ('new', new), ('field', fields)):
            for name, o in res.items():
                if o.get('line'):
                    hit[o['line']].append(group + ': ' + name)
        text = Path(script).read_text().splitlines()
        coverage = {str(n): dict(statement=text[n - 1].strip()[:160],
                                 shipped=sum(x.startswith('shipped') for x in hit.get(n, [])),
                                 new=sum(x.startswith('new') for x in hit.get(n, [])),
                                 field=sum(x.startswith('field') for x in hit.get(n, [])))
                    for n in lines}
        accepted_fields = sorted(k for k, o in fields.items() if o['result'] == 'ACCEPTED')
        result = dict(
            status='PASS_T16_AUDIT_MUTANT_COVERAGE',
            audit_script_sha256=AUDIT_SHA,
            template_sha256=archived['template_sha256'],
            template_to_frozen_owners_binding=binding,
            shipped_controls=shipped,
            new_mutants=new,
            field_census=fields,
            assert_lines_in_audit=len(lines),
            assert_lines_reached_by_shipped=sorted(n for n in lines if coverage[str(n)]['shipped']),
            assert_lines_reached_by_any=sorted(n for n in lines if any(coverage[str(n)][k] for k in ('shipped', 'new', 'field'))),
            assert_lines_unreached=sorted(n for n in lines if not any(coverage[str(n)][k] for k in ('shipped', 'new', 'field'))),
            coverage=coverage,
            accepted_new_mutants=sorted(k for k, o in new.items() if o['result'] == 'ACCEPTED'),
            accepted_fields={k: downstream_mentions(source, k.split(' ')[0].split('.')[-1]) for k in accepted_fields},
            rejections_by_exception=dict(Counter(o.get('exception', o['result']) for r in (shipped, new, fields) for o in r.values())),
        )
    assert all(o['result'] == 'REJECTED' for o in shipped.values()), 'a shipped control is not rejected'
    out = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if a.write:
        (HERE / 'EXPECTED.json').write_text(out)
    else:
        expected = (HERE / 'EXPECTED.json').read_text()
        assert out == expected, 'result differs from EXPECTED.json'
    print('PASS_T16_AUDIT_MUTANT_COVERAGE shipped=%d new=%d fields=%d accepted_new=%d accepted_fields=%d unreached_asserts=%d' % (
        len(shipped), len(new), len(fields), len(result['accepted_new_mutants']), len(result['accepted_fields']),
        len(result['assert_lines_unreached'])))


if __name__ == '__main__':
    main()
