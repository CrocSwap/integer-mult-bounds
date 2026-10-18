"""Source-bound identity-loop witness on the selected PR589 local bit word.

Both variants have legal frame paths and unchanged paid children. The variant
with projected cleanup is deliberately invalid and must fail dirty restoration.
"""
import collections
import ast
import copy
import importlib.util
from pathlib import Path
import struct
import subprocess
import sys
import common as C
import independent as I


def guard_binding():
    """Bind the scalar envelope formulas without importing the predecessor suite."""
    tree = ast.parse((C.ROOT/C.GUARDS).read_text())
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    returned = next(n.value for n in ast.walk(functions['literal_bounds']) if isinstance(n, ast.Return))
    C.need(isinstance(returned, ast.Call) and isinstance(returned.func, ast.Name) and returned.func.id == 'dict',
           'retained envelope return shape')
    fields = {n.arg: n.value for n in returned.keywords}
    for key, expression in [('local_bits', '(64 * F**3 * B**2).bit_length()'),
                            ('nine_stage_bits', '((1 << 18) * F**5 * B**4).bit_length()')]:
        C.need(ast.dump(fields[key]) == ast.dump(ast.parse(expression, mode='eval').body), 'retained envelope formula')
    comparisons = [ast.dump(n) for n in ast.walk(functions['guard']) if isinstance(n, ast.Compare)]
    wanted = [ast.dump(ast.parse(x, mode='eval').body) for x in
              ("bill['local_bits'] <= 104", "bill['nine_stage_bits'] <= 192")]
    C.need(comparisons == wanted, 'retained scalar guard thresholds')
    return dict(local='64 F^3 B^2 < 2^104', nine_stage='2^18 F^5 B^4 < 2^192', source=C.GUARDS)


def variants(old):
    C.need((old['v'], old['R']) == (111, 439), 'wrong selected local word')
    d, s, t, zero, full = 222, 223, 111, 0, 1
    loop = [[zero, d, [t]], [zero, t, [s]], [zero, d, [t]],
            [zero, t, [s]], [zero, d, [s]]]
    good = copy.deepcopy(old)
    good['A'] = loop+good['A']
    bad = copy.deepcopy(good)
    bad['C'].append([full, d, [s]])
    return good, bad, loop


def stream(w, raw=False, reverse=False):
    ops = []
    for sec in (('A',) if raw else ('D', 'A')):
        ops.extend(('add', d, s) for _, d, srcs in w[sec] for s in srcs)
    temp = 2*w['v']+w['R']
    for j, helper in enumerate(w['ret']):
        ops.append(('copy', temp, helper))
        ops.extend(('add', w['v']+i, temp) for i, srcs in enumerate(w['scatter']) if j in srcs)
        ops.append(('erase', temp, helper))
    for sec in (('B',) if raw else ('B', 'C')):
        ops.extend(('add', d, s) for _, d, srcs in w[sec] for s in srcs)
    if reverse:
        flip = {'add': 'add', 'copy': 'erase', 'erase': 'copy'}
        ops = [(flip[k], d, s) for k, d, s in reversed(ops)]
    return ops


def row_replay(n, ops):
    rows = [1 << i for i in range(n)]+[0]
    for kind, dst, src in ops:
        if kind == 'add':
            rows[dst] ^= rows[src]
        elif kind == 'copy':
            C.need(rows[dst] == 0, 'copy target not clean')
            rows[dst] = rows[src]
        else:
            C.need(kind == 'erase' and rows[dst] == rows[src], 'invalid erasure')
            rows[dst] = 0
    C.need(rows[-1] == 0, 'copy temporary not erased')
    return rows[:-1]


def projected(w):
    n, v = 2*w['v']+w['R'], w['v']
    rows = [1 << i for i in range(n)]
    for sec in ('A', 'B'):
        for _, d, srcs in w[sec]:
            if not v <= d < 2*v:
                for s in srcs:
                    rows[d] ^= rows[s]
    return rows


def cleanup_rows(w, rows):
    result = list(rows)
    for _, d, srcs in w['C']:
        for s in srcs:
            result[d] ^= result[s]
    return result


def export(w, out):
    out.mkdir()
    path = out/'word.json'
    path.write_bytes(C.canonical(w))
    r = subprocess.run([sys.executable, '-I', '-B', str(C.ROOT/C.EXPORTER), str(path), str(out/'records')],
                       cwd=out, text=True, capture_output=True, timeout=120)
    C.need(r.returncode == 0, 'pinned exporter failed: '+r.stderr[-1000:])
    data = (out/'records/249-records.bin').read_bytes()
    C.need(len(data) % 24 == 0, 'record alignment')
    records = list(struct.iter_unpack('<6i', data))
    n = 2*w['v']+w['R']
    paid = collections.Counter()
    paths = [[x] for x in w['start']]
    for op, a, b, c, f, rank in records:
        if op == 0:
            C.need(paths[a][-1] == b and f > 0, 'MOVE source/rank')
            paths[a].append(c)
            paid[f] += 1
        elif op == 2:
            paid[rank] += 1
    C.need([x[-1] for x in paths] == w['final'], 'final frame paths')
    peaks = []
    for reverse in (False, True):
        values, peak, live = [1]*n+[0], 1, False
        for op, a, b, c, f, rank in (reversed(records) if reverse else records):
            if reverse and op in (2, 3):
                op = 5-op
            if op == 1:
                values[a] += abs(c)*values[b]
                peak = max(peak, values[a])
            elif op == 2:
                C.need(not live, 'nested exporter copy')
                values[b], live = values[a], True
            elif op == 3:
                C.need(live, 'unmatched exporter erase')
                values[b], live = 0, False
            else:
                C.need(op == 0, 'unknown exporter opcode')
        C.need(not live, 'unclosed exporter copy')
        peaks.append(peak)
    forward, reverse = peaks
    local = 64*forward**3*reverse**2
    nine = (1 << 18)*forward**5*reverse**4
    return dict(operations=dict(sorted(collections.Counter(r[0] for r in records).items())),
                records=len(records), profile=dict(sorted(paid.items())), mass=sum(r*c for r, c in paid.items()),
                frame_paths_sha256=C.digest(paths), records_sha256=C.sha(out/'records/249-records.bin'),
                forward=forward, reverse=reverse, local_envelope_bits=local.bit_length(),
                nine_stage_envelope_bits=nine.bit_length(), local_guard=local < 1 << 104,
                nine_stage_guard=nine < 1 << 192), records


def report(work):
    bound = guard_binding()
    old = C.read(C.ROOT/C.WORD)
    good, bad, loop = variants(old)
    n = 2*old['v']+old['R']
    spec = importlib.util.spec_from_file_location('retained_xcheck_p', C.ROOT/C.CHECKER)
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    original = owner.Word(old)
    labels = original.labels()
    original.full()
    baseline_h, baseline_c, _ = original.interface()
    C.need(all(baseline_h.values()) and all(baseline_c.values()), 'baseline interface failure')
    raw = row_replay(n, stream(old, raw=True))
    goal = row_replay(n, stream(old))
    C.need(goal == [((1 << i) | (1 << (i-old['v']))) if old['v'] <= i < 2*old['v'] else 1 << i
                    for i in range(n)], 'baseline full boundary')
    reports = {}
    for name, word in (('baseline', old), ('neutral_loop', good), ('projected_cleanup', bad)):
        engine = original if name == 'baseline' else owner.Word(word)
        # Replays include all gates and check every actual operand climb.
        replay, _, _ = engine.replay()
        C.need(row_replay(n, stream(word, raw=True)) == raw, 'raw endpoint changed')
        full = row_replay(n, stream(word))
        C.need(replay == full, 'owning checker / independent row disagreement')
        directions = []
        for reverse in (False, True):
            ops = stream(word, reverse=reverse)
            rows = row_replay(n, ops)
            columns = I.source_columns(n, ops)
            C.need(rows == I.transpose_columns(columns), 'literal columns / rows disagree')
            C.need(rows == full, 'unexpected inverse endpoint')
            directions.append(C.digest(columns))
        h, c, _ = engine.interface()
        p = projected(word)
        projected_cleanup_identity = cleanup_rows(word, p) == [1 << i for i in range(n)]
        full_ok = True
        rejection = None
        try:
            engine.full()
        except owner.Reject as error:
            full_ok, rejection = False, str(error)
        C.need(full_ok == (name != 'projected_cleanup'), 'owning full-check verdict')
        differing = [[i, goal[i], full[i]] for i in range(n) if goal[i] != full[i]]
        if name == 'projected_cleanup':
            C.need(differing == [[222, 1 << 222, (1 << 222) | (1 << 223)]], 'dirty witness changed')
            C.need(projected_cleanup_identity, 'compiled cleanup is not projected inverse')
        if name == 'neutral_loop':
            C.need(not projected_cleanup_identity and full == goal, 'neutral positive control')
        bill, records = export(word, work/name)
        if reports:
            base_bill = reports['baseline']['bill']
            for key in ('profile', 'mass', 'frame_paths_sha256'):
                C.need(bill[key] == base_bill[key], 'paid path change: '+key)
            C.need(bill['operations'][1]-base_bill['operations'][1] == (5 if name == 'neutral_loop' else 6),
                   'complete added cost')
        # Independent literal stream and actual exported opcode sequence agree.
        literal = stream(word)
        decoded = [('add', a, b) if op == 1 else ('copy', b, a) if op == 2 else ('erase', b, a)
                   for op, a, b, _, _, _ in records if op != 0]
        C.need(decoded == literal, 'exporter/literal stream mismatch')
        reports[name] = dict(full_boundary=full_ok, owner_rejection=rejection,
                            hypotheses=h, conclusions=c, raw_sha256=C.digest(raw),
                            full_sha256=C.digest(full), projected_sha256=C.digest(p),
                            cleanup_is_projected_inverse=projected_cleanup_identity,
                            differences=differing, column_sha256=directions, bill=bill)
    # A zero-helper-only test misses exactly the exhibited dirty corruption.
    helper_mask = ((1 << old['R'])-1) << (2*old['v'])
    a, b = row_replay(n, stream(old)), row_replay(n, stream(bad))
    C.need([r & ~helper_mask for r in a] == [r & ~helper_mask for r in b], 'zero-helper control')
    return dict(status='PASS_SELECTED_PR589_PROJECTED_CLEANUP_COUNTEREXAMPLE', columns=n,
                directions=2, literal_column_runs=6, input_loop=loop,
                compressed_cleanup_gate=[1, 222, [223]], labels=labels, variants=reports, guard_source=bound,
                clean_helper_inputs_miss_error=True, admitted=False,
                scope='Source frame legality and exact scalar/copy replay; no native supplier or physical adoption')
