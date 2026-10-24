#!/usr/bin/env python3
"""Exact bounded heterogeneous terminal decoder; no new kappa.

Chris R / Clear1nsight, substantial OpenAI Codex assistance. Apache-2.0.
The predecessor emitter and Clifford compiler are reused with attribution.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256, sha1
from pathlib import Path
import argparse
import itertools
import json
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT/'research/center-helper-normal-form'
CE = ROOT/'research/kappa-round8-owner-protocol-20261023/sources/research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'
N = 640


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    # Execute the authenticated source bytes, never a neighbouring pyc cache.
    out = types.ModuleType(name)
    out.__file__ = str(path)
    sys.modules[name] = out
    exec(compile(path.read_bytes(), str(path), 'exec'), out.__dict__)
    return out


def plus(dst, src, coefficient=Q(1)):
    for key, value in tuple(src.items()):
        value = dst.get(key, Q(0)) + coefficient*value
        if value:
            dst[key] = value
        else:
            dst.pop(key, None)


def identity():
    return [{i: Q(1)} for i in range(N)]


def mm(a, b):
    out = []
    for row in a:
        new = {}
        for j, value in row.items():
            plus(new, b[j], value)
        out.append(new)
    return out


def transpose(a):
    out = [{} for _ in a]
    for i, row in enumerate(a):
        for j, value in row.items():
            out[j][i] = value
    return out


def rank(rows):
    pivots = {}
    for x in rows:
        while x:
            k = x.bit_length()-1
            if k not in pivots:
                pivots[k] = x
                break
            x ^= pivots[k]
    return len(pivots)


def span(basis):
    need(rank(basis) == len(basis), 'independent chart basis')
    out = {0}
    for v in basis:
        out |= {x ^ v for x in tuple(out)}
    return out


def evaluate(events, starts, final, frames):
    """New sparse/free-word evaluator; does not call predecessor replay."""
    rows = [{(i, ()): Q(1)} for i in range(N)]
    charts = list(starts)
    spaces = list(map(span, frames))
    paid = Counter()
    for e in events:
        op, dst = e[:2]
        if op == 'add':
            _, _, src, q, f = e
            need(dst != src and charts[dst] == charts[src] == f, 'actual scalar common chart')
            plus(rows[dst], rows[src], q)
        elif op == 'scale':
            _, _, q, f = e
            need(charts[dst] == f and q != 0, 'invertible scale chart')
            rows[dst] = {k: q*v for k, v in rows[dst].items()}
        elif op == 'transport':
            _, _, a, b, width = e
            need(charts[dst] == a and (spaces[a] < spaces[b] or spaces[b] < spaces[a]), 'nested physical chart move')
            need(width == abs(len(frames[a])-len(frames[b])), 'derive recursive width')
            paid[width] += 1
            charts[dst] = b
        elif op == 'warp':
            _, _, letter, a, b = e
            need(charts[dst] == a, 'actual warp chart')
            new = {}
            for (i, word), value in rows[dst].items():
                word = word[1:] if word and word[0] == -letter else (letter,)+word
                plus(new, {(i, word): value})
            rows[dst] = new
            charts[dst] = b
        else:
            raise ValueError('unknown actual operation')
    need(charts == final, 'every endpoint chart restored')
    need(all(not word for row in rows for i, word in row), 'all source warp words cancel')
    return [{i: v for (i, word), v in row.items()} for row in rows], paid


def target(abi, observations, selected):
    out = identity()
    for i in range(112):
        out[112+i][i] = Q(1)
    for i, row in enumerate(abi['B_rows']):
        plus(out[i], {j: Q(v) for j, v in row if j-632 not in selected})
    for j, row in enumerate(observations):
        if j not in selected:
            plus(out[632+j], row)
    return out


def terminal(selected, abi, observations, final, frames, pivots):
    xs = sorted({i for j in selected for i, v in abi['R_rows'][j] if i < 224})
    ys = sorted({i for i, row in enumerate(abi['B_rows']) if any(k-632 in selected for k, v in row)})
    touched = sorted(xs+ys+[pivots[j] for j in selected])
    need(len(touched) == len(set(touched)), 'distinct physical owners')
    strip = [('transport', i, final[i], 0, len(frames[final[i]])) for i in touched]
    scalar = []
    for j in selected:
        scalar += [('add', 632+j, i, -v, 0) for i, v in sorted(observations[j].items())]
    for j in selected:
        for i, row in enumerate(abi['B_rows']):
            for k, v in row:
                if k == 632+j:
                    scalar.append(('add', i, 632+j, -Q(v), 0))
    restore = [('transport', i, 0, final[i], len(frames[final[i]])) for i in touched]
    info = dict(selected=list(selected), X=xs, Y=ys, pivots=[pivots[j] for j in selected],
                scalar_ADDs=len(scalar), extra_paid=dict(Counter(e[4] for e in strip+restore)))
    return strip+scalar+restore, info


def inverse(a):
    unit = identity()
    k = [dict(row) for row in a]
    for i in range(N):
        plus(k[i], unit[i], Q(-1))
    k2 = mm(k, k)
    need(not any(mm(k2, k)), 'cube-zero endpoint')
    inv = identity()
    for i in range(N):
        plus(inv[i], k[i], Q(-1))
        plus(inv[i], k2[i])
    need(mm(inv, a) == mm(a, inv) == unit, 'two-sided inverse')
    return inv


def raw_dual(events):
    out = []
    for e in events:
        if e[0] == 'add':
            out.append(('add', e[2], e[1], -e[3], e[4]))
        elif e[0] == 'scale':
            out.append(('scale', e[1], 1/e[2], e[3]))
        else:
            need(e[0] == 'transport', 'no extra warp hidden in terminal')
            out.append(e)  # The retained source convention dualizes each chart.
    return out


def rejected(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def conjugate_clifford(ce, op):
    """For a unitary, raw inverse transpose is its complex conjugate."""
    circuit = []
    for e in op.circuit:
        if e[0] == 'C':
            circuit.append(('C', e[1], -e[2]))
        elif e[0] == 'D':
            circuit.append(('D', e[1], tuple(-x % 4 for x in e[2])))
        elif e[0] == 'phase':
            circuit.append(('phase', -e[1] % 4))
        else:
            need(e[0] in ('P', 'X'), 'known real Clifford primitive')
            circuit.append(e)
    return ce.Op(op.n, tuple((x,z,-p % 4) for x,z,p in op.tab), circuit)


def scalar_tariff(events):
    """Retained ADD/SCALE tariff from PR4712; routing is a separate bill."""
    total = 0
    count = Counter()
    for e in events:
        if e[0] not in ('add', 'scale'):
            continue
        q = e[3] if e[0] == 'add' else e[2]
        n, d = abs(q.numerator), q.denominator
        need(n > 0 and not d & (d-1), 'nonzero dyadic scalar')
        if e[0] == 'add':
            total += 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
        else:
            need(not n & (n-1), 'dyadic-unit SCALE')
            total += 2*(abs(n.bit_length()-d.bit_length())+int(q < 0))
        count[e[0]] += 1
    return dict(gates=dict(count), real_scalar_tariff=total,
                route_and_precision_costs_included=False)


def norm_envelope(events):
    """Whole-field l2 triangle bound; Gaussian/warp primitives are unitary."""
    envelope = [Q(1)]*N
    maximum = Q(1)
    for e in events:
        if e[0] == 'add':
            envelope[e[1]] += abs(e[3])*envelope[e[2]]
        elif e[0] == 'scale':
            envelope[e[1]] *= abs(e[2])
        maximum = max(maximum, max(envelope))
    return str(maximum)


def validate_census(entries):
    need(len({r['input'] for r in entries}) == len(entries), 'no duplicate productive input')
    need(sum(r['input'] < 632 for r in entries) == 408, 'all inherited helpers exactly once')


def census(selected, pivots, helpers):
    selected_helpers = {pivots[j] for j in selected}
    entries = [dict(input=i, rank=r, sector='consumer-pivot-return' if i in selected_helpers else 'autonomous-helper')
               for i, r in helpers.items()]
    entries += [dict(input=632+j, rank=8, sector='independent-center-inverse') for j in selected]
    validate_census(entries)
    return entries


def authenticate():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'changed source '+row['path'])
    auth = json.loads((HERE/'SNAPSHOTS.json').read_text())
    for row in auth['files']:
        raw = (ROOT/row['consumed_frozen_path']).read_bytes()
        need(sha256(raw).hexdigest() == row['frozen']['sha256'], 'frozen snapshot pin')
        blob = sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        need(blob == row['frozen']['git_blob'], 'frozen source blob')
        live = (HERE/row['live']['retained_package_file']).read_bytes() if 'retained_package_file' in row['live'] else raw
        need(sha256(live).hexdigest() == row['live']['sha256'], 'live snapshot pin')
        need(sha1(b'blob '+str(len(live)).encode()+b'\0'+live).hexdigest() == row['live']['git_blob'], 'live source blob')
        need((raw == live) == row['byte_identical'], 'do not equate source trees')
    return pins


def run():
    pins = authenticate()
    normal = load(SRC/'verify.py', 'predecessor_normalizer')
    engine = load(SRC/'inputs/retained_verify.py', 'frozen_center_emitter')
    engine.HERE = SRC
    payload = engine.load()
    frames = payload['canonical']['frames']
    abi = json.loads((SRC/'inputs/ABI.json').read_text())
    r = [{i: Q(v) for i, v in row} for row in abi['R_rows']]
    cold = {i for i in range(224, 632) if payload['canonical']['start'][i] == 0 and payload['canonical']['final'][i] == 1}
    header, det, _ = normal.make_header(r, cold)
    footer = normal.inverse_header(header, 1)
    need(len(header) == len(footer) == 379 and det == 64, 'whole joint normalization charged')
    starts, centers, source = engine.emit(payload)
    live = load(HERE/'live-4694-verify.py', 'live_predecessor_reference')
    need(live.emit(payload) == (starts, centers, source), 'standard emitter unchanged despite cache addition')
    final = payload['canonical']['final']+[0]*8
    observations = [{i: v for i, v in r[j].items() if i < 224} | {normal.J[j]: Q(1)} for j in range(8)]
    word = header+source+footer
    original, old_paid = evaluate(word, starts, final, frames)
    need(original == target(abi, observations, set()), 'full normalized source ABI')
    need(old_paid == Counter(engine.PAID), 'source recursive profile')
    helpers = {i: len(frames[final[i]]) - len(frames[starts[i]]) for i in range(224, 632)}
    need(Counter(helpers.values()) == Counter({4:28, 7:7, 8:47, 9:326}), 'helper target census')
    screens = []
    groups = [(j,) for j in range(8)]+list(itertools.combinations(range(8), 2))+[tuple(range(8))]
    for selected in groups:
        tail, info = terminal(selected, abi, observations, final, frames, normal.J)
        cost = Counter(info['extra_paid']); reward = Counter({8:len(selected)})
        need(cost[8] > reward[8] and cost[9] > 0, 'uniform negative moment coefficients')
        debt = cost-reward
        info.update(extra_paid={str(k):v for k,v in sorted(cost.items())},
                    optimistic_extra_reward={'8':len(selected)},
                    moment_delta_coefficients={str(k):-v for k,v in sorted(debt.items())},
                    uniform_moment_delta_upper_bound=-sum(debt.values()), candidate_C_interval=['0','1'],
                    joint_normalization_gates=758, two_unshared_invocations_normalization_gates=1516)
        screens.append(info)
    selected = {0}
    tail, _ = terminal(selected, abi, observations, final, frames, normal.J)
    last_contacts = []
    for field in screens[0]['X']+screens[0]['Y']+screens[0]['pivots']:
        index = next(k for k in range(len(word)-1, -1, -1)
                     if word[k][1] == field or (word[k][0] == 'add' and word[k][2] == field))
        need(word[index][0] == 'add', 'no last-contact Gaussian available for unilateral cancellation')
        last_contacts.append(dict(field=field, source_event=index, event=word[index]))
    actual, paid = evaluate(word+tail, starts, final, frames)
    wanted = target(abi, observations, selected)
    need(actual == wanted, 'chosen terminal full 640-input endpoint')
    need(paid == old_paid+Counter({8:112, 9:114}), 'complete chosen terminal recursive bill')
    inv = inverse(wanted)
    _, _, dual_source = engine.emit(payload, dual=True)
    dual_word = normal.dual_header(header)+dual_source+normal.dual_header(footer)+raw_dual(tail)
    dual, dual_paid = evaluate(dual_word, starts, final, frames)
    need(dual == transpose(inv) and dual_paid == paid, 'gatewise actual raw inverse transpose')
    ownership = census(selected, normal.J, helpers)
    credited = {row['input']: row for row in ownership}
    inventory = []
    for i in range(N):
        history = [e for e in word+tail if e[1] == i or (e[0] == 'add' and e[2] == i)]
        if i in credited:
            status = credited[i]['sector']
        elif i < 224:
            status = 'retained-coupled-main-contract-no-new-credit'
        else:
            status = 'retained-coupled-center-no-credit'
        inventory.append(dict(input=i, initial_chart=starts[i], final_chart=final[i],
                              independent_input=True, status=status,
                              new_reward_rank=8 if i == 632 else None,
                              inherited_helper_rank=helpers.get(i),
                              chronological_contact_count=len(history),
                              chronological_history_sha256=sha256(json.dumps(history,default=str).encode()).hexdigest()))
    need([x['input'] for x in inventory] == list(range(N)), 'every arbitrary input has one ownership history')
    controls = []
    bad = list(tail);bad.pop(next(i for i,e in enumerate(bad) if e[0]=='add' and e[2]<112))
    need(evaluate(word+bad, starts, final, frames)[0] != wanted, 'omitted R_X term rejected');controls.append('missing data observation')
    bad = [e for e in tail if not (e[0]=='add' and e[1]<632)]
    need(evaluate(word+bad, starts, final, frames)[0] != wanted, 'missing Y correction rejected');controls.append('missing center-to-Y correction')
    bad = list(tail);e=bad[0];bad[0]=(*e[:4],e[4]-1)
    need(rejected(lambda:evaluate(word+bad, starts, final, frames)), 'unpaid recursive width rejected');controls.append('undercharged transport')
    need(rejected(lambda:evaluate(word+tail[1:], starts, final, frames)), 'missing chart conversion rejected');controls.append('missing chart conversion')
    duplicate = ownership+[dict(ownership[0])]
    need(rejected(lambda:validate_census(duplicate)), 'duplicate helper input rejected');controls.append('duplicate helper credit')
    wrong = normal.dual_header(header)+dual_source+normal.dual_header(footer)+tail
    need(evaluate(wrong, starts, final, frames)[0] != transpose(inv), 'wrong raw dual rejected');controls.append('forward tail used as dual')
    # One-column phase-aware lowering of every distinct newly needed frame.
    # Exact source compiler is reused; this is not independent full native replay.
    ce = load(CE, 'retained_exact_clifford')
    charts = sorted({final[i] for info in screens for i in info['X']+info['Y']+info['pivots']})
    lowerings = []
    for chart in charts:
        f = ce.canonical_frame(9, tuple(frames[chart]))
        strip = f.adjoint()
        for direction, op in [('strip',strip), ('restore',f),
                              ('strip_raw_dual',conjugate_clifford(ce,strip)),
                              ('restore_raw_dual',conjugate_clifford(ce,f))]:
            recipe, compiled = ce.lower_child(op)
            need(rank([x for x,z,p in op.tab[9:]]) == recipe['rank'] == len(frames[chart]), 'actual new Fourier rank')
            need(compiled.tab == op.tab and compiled.zero_state() == op.zero_state(), 'phase-aware literal lowering')
            lowerings.append(dict(chart=chart, direction=direction, rank=recipe['rank'], recipe=recipe))
        unit = f.then(f.adjoint())
        need(unit.tab == ce.ident(9).tab and unit.zero_state() == ce.ident(9).zero_state(), 'true inverse with phase')
    h = ce.canonical_frame(9, tuple(frames[1]))
    z = ce.canonical_frame(9, tuple(frames[centers[0]['input_frame']])).adjoint()
    support = [sum(v!=(0,0) for v in op.zero_state()[0]) for op in (h,z)]
    need(support == [512,256], 'unmodified diagonal blocks cannot be one common multiplier')
    query_inventory = []
    for j, center in enumerate(centers):
        q = ce.canonical_frame(9, tuple(frames[center['input_frame']])).adjoint()
        square = q.then(q)
        monomial, record = ce.monomial(square)
        fourth = square.then(square)
        need(monomial.tab == square.tab and monomial.zero_state() == square.zero_state(), 'actual available monomial square')
        need(fourth.tab == ce.ident(9).tab and fourth.zero_state() == ce.ident(9).zero_state(), 'actual order-four premise')
        qt = conjugate_clifford(ce, q.adjoint())
        query_inventory.append(dict(center=j, input_frame=center['input_frame'],
                                    physical_Q='inverse canonical rank-eight frame',
                                    square_monomial=record, fourth_power_identity=True,
                                    Q_is_symmetric=(qt.tab == q.tab and qt.zero_state() == q.zero_state()),
                                    common_transverse_multiplier_realized=False))
    zt = conjugate_clifford(ce, z.adjoint())
    col, col_den = z.zero_state()
    row, row_den = zt.zero_state()
    need((col[10], col_den, row[10], row_den) == ((1,0),4,(-1,0),4),
         'literal physical-Q transpose counterexample at addresses zero and ten')
    h_conj = conjugate_clifford(ce, h)
    need(h_conj.zero_state() != h.zero_state(), 'raw inverse transpose is not the forward Gaussian')
    controls.append('forward Gaussian substituted for raw inverse transpose')
    consumer = load(SRC/'consumer.py','retained_conditional_consumer').check()
    need(not consumer['native_provider_realized'], 'algebraic identity is not physical embedding')
    # Positive scalar envelopes are bounds on whole-field ADD/SCALE growth;
    # movement, child precision and Gaussian norm factors remain separate.
    return dict(status='PASS_SCOPED_HETEROGENEOUS_TERMINAL_LOSES',new_kappa=None,
                base_commit=pins['base_commit'],chosen=screens[0],screens=screens,
                source_paid=dict(sorted(old_paid.items())),final_paid=dict(sorted(paid.items())),
                source_word_sha256=sha256(json.dumps(word,default=str).encode()).hexdigest(),
                full_terminal=tail,target_census=ownership,all_640_primal_and_raw_dual=True,
                all_input_ownership_inventory=inventory,
                unilateral_cancellation_last_contacts=last_contacts,
                remaining_coupled_centers=list(range(1,8)),controls=controls,
                selected_center_job='independent inverse rank-eight Gaussian; positive ordinary credit is optimistic',
                heterogeneous_diagonal_column_support=support,new_lowerings=lowerings,
                physical_query_inventory=query_inventory,
                direct_center_Q_symmetry_witness=dict(center=0, row=10, column=0,
                    Q_row_column='1/16', Q_column_row='-1/16',
                    scope='actual center inverse used directly as candidate Q; other embeddings not excluded'),
                added_boundary_bill=scalar_tariff(header+footer),
                terminal_scalar_bill=scalar_tariff(tail),
                native_source_scalar_bill=scalar_tariff(source),
                full_scalar_bill=scalar_tariff(word+tail),
                terminal_whole_field_l2_envelope=norm_envelope(tail),
                full_whole_field_l2_envelope=norm_envelope(word+tail),
                extra_monomial_wrapper_invocations_upper_count=452,
                new_storage_owners=0,
                phase_scope='new one-column nested Gaussian requests only; all-width tensor uses inherited source contract',
                compiler_route='PR4610 fixed, no compiler or outer transfer attempted')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);args=ap.parse_args()
    value=json.loads(json.dumps(run(),default=str))
    if args.out:
        need(not args.out.exists(),'fresh output file required')
        args.out.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
    else:
        expected=json.loads((HERE/'RESULT.json').read_text())
        canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
        need(canonical(value)==canonical(expected),'exact scientific receipt')
    print('PASS_SCOPED_HETEROGENEOUS_TERMINAL_LOSES no_new_kappa')


if __name__=='__main__':
    main()
