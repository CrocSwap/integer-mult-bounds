"""PR210's 493-source helper (head 1331149) inside PR234's five-stage cover: fresh preparation, all-column
scalar proofs, physical telescope, global lowering, exact geometry, prime determinants and finite accounting.

The helper word, its preparation and its all-column replay are PR210's own code (eumemic, Dugongue, sennemmi;
OpenAI Codex assistance), executed unchanged from a pinned checkout. The five-stage lowering, geometry and
finite bill are PR234's code (hcg890; ChatGPT assistance) with only their helper-specific constants rebound
to freshly computed values. Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from array import array
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import contextlib, hashlib, importlib.util, io, json, shutil, sys, tempfile, time, types

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import telescope493

V8 = 'research/five-stage-source-bound-v8'
BASE = 'research/paired-cube-diagonal-bit-168'
PR210 = 'research/coordinated-crossover-pr200'
CATEGORIES = tuple(sorted(['agg_read', 'agg_restore', 'agg_setup', 'center', 'cleanup_gate', 'dirty_read', 'echelon_read',
                           'echelon_restore', 'echelon_setup', 'forward_gate', 'gauge_mix', 'inject', 'partner_cleanup',
                           'partner_delivery', 'partner_mix', 'rank_restore', 'rank_setup', 'side_root', 'terminal_post',
                           'terminal_pre', 'terminal_write', 'uninject']))
sha = lambda b: hashlib.sha256(b).hexdigest()


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s)
    sys.modules[name] = m; s.loader.exec_module(m); return m


def assemble_tree(P210, P234, tmp):
    """PR210's package next to PR234's pinned copy of the PR200 base package (PR210 ships it only as archives)."""
    tree = Path(tmp) / 'tree'
    shutil.copytree(Path(P210) / PR210, tree / PR210, ignore=shutil.ignore_patterns('baseline-pr202.part*', '__pycache__'))
    shutil.copytree(Path(P234) / V8 / 'loader/source_inputs/base_bit' / BASE, tree / BASE)
    # PR234's terminal_records derives the 34 PR166 terminal records from the pinned PR200 selectors, exactly as
    # PR234 rebinds them; PR210's newg preparation reads them from joint-replay.json, an output-only receipt.
    sys.path.insert(0, str(tree / BASE / 'bit'))
    joint = load('fs493_joint_word', tree / PR210 / 'joint/joint_word.py')
    loader = load('fs493_pr234_loader', Path(P234) / V8 / 'loader/source_loader.py')
    selectors = json.loads((tree / BASE / 'selected/bit/sinks.json').read_text())
    with contextlib.redirect_stdout(io.StringIO()):
        records = loader.terminal_records(joint.Candidate(), selectors)
    (tree / PR210 / 'joint/joint-replay.json').write_text(json.dumps(dict(selected=records)))
    return tree


def prepare(tree):
    with contextlib.redirect_stdout(io.StringIO()):
        setup = load('fs493_complete493_setup', tree / PR210 / 'targetagg/setup.py')
    m = setup.m; word = tree / PR210 / 'targetagg/word.py'
    exec(compile(word.read_text(), str(word), 'exec'), m.__dict__)
    m.__dict__['__word_text__'] = word.read_text()
    return m


def scalar_proofs(m):
    """PR210's own complete replay: F2 identity, literal majorant, both defining-integer signs, 17 controls."""
    out = dict(F2=m.replay())
    bound = m.replay('bound'); bits = 8 * ((bound.bit_length() + 2 + 7) // 8); assert 1 << bits > 2 * bound
    out['majorant'] = dict(residual_bound=bound, packing_bits=bits)
    out['integer'] = [m.replay('Z', d, bits) for d in (1, -1)]
    controls = {}
    for mutation in ['omit_echelon_setup', 'omit_echelon_inverse', 'flip_echelon_sign', 'omit_rank_setup', 'omit_rank_inverse',
                     'repeat_rank_read', 'omit_aggregation_setup', 'omit_aggregation_inverse', 'repeat_aggregation_read',
                     'omit_extra_mix', 'omit_extra_compensation', 'omit_early_mix', 'old_adjoint', 'undo_before_restore',
                     'omit_gauge_mix', 'omit_gauge_compensation', 'late_phase1_gauge']:
        try: m.replay('Z' if mutation == 'flip_echelon_sign' else 'F2', bits=bits, mutation=mutation)
        except AssertionError: controls[mutation] = 'REJECTED'
        else: raise AssertionError('corruption accepted: ' + mutation)
    out['controls'] = controls
    f = out['F2']; assert f['formal_columns'] == 2 * m.W.v + len(m.regs) and f['all_targets'] and f['all_source_and_dirty_restored']
    for z in out['integer']: assert z['all_targets'] and z['all_source_and_dirty_restored']
    return out


def projection(records, n, v, reverse=False):
    """Independent literal F2 replay of the telescope's scalar projection (PR234 scalar_check, constants rebound)."""
    def events():
        center = None
        for k in (range(len(records) - 6, -1, -6) if reverse else range(0, len(records), 6)):
            op, a, b, c, f, z = records[k:k + 6]
            if op == 1:
                if b == n: assert center is not None; b = center
                assert 0 <= a < n and 0 <= b < n and a != b
                yield a, b, -c if reverse else c
            elif op == (3 if reverse else 2): assert center is None and b == n; center = a
            elif op == (2 if reverse else 3): assert center == a and b == n; center = None
        assert center is None
    cols = [1 << i for i in range(n)]; norms = [1] * n; want = cols[:]
    for i in range(v): want[v + i] ^= 1 << i
    largest = 1; counts = Counter(); digest = hashlib.sha256(b'['); count = 0
    for a, b, c in events():
        if c & 1: cols[a] ^= cols[b]
        norms[a] += abs(c) * norms[b]; largest = max(largest, norms[a]); counts[abs(c)] += 1
        if count: digest.update(b',')
        digest.update(json.dumps([a, b, c], separators=(',', ':')).encode()); count += 1
    digest.update(b']')
    assert cols == want, 'independent literal all-column endpoint'
    return dict(all_formal_columns=n, event_sha256=digest.hexdigest(), weighted_additions=count,
                coefficient_counts={str(k): x for k, x in sorted(counts.items())},
                literal_unit_additions=sum(c * x for c, x in counts.items()), max_intermediate_row_l1=largest)


def lowering(P234, m, records, tele, raw):
    src = (Path(P234) / V8 / 'code/five_stage_bit_global_lowering_20261009.py').read_text()
    R = raw['physical_R']; five = raw['five_stage_profile']
    def rep(a, b):
        nonlocal src; assert src.count(a) == 1, a; src = src.replace(a, b)
    rep("V, R, H, M = 1760, 16643, 24, 120", f"V, R, H, M = 1760, {R}, 24, 120")
    rep("assert not copy_open and adds==2569626 and copies==erases==24", f"assert not copy_open and adds=={tele['events']} and copies==erases==24")
    rep("assert coefficient=={1:785130,2:1783176,3:1320}", "COEFFICIENTS.append(dict(sorted(coefficient.items())))")
    rep("physical=lower.ns['result']; raw=json.loads(RAW.read_text())", "physical=lower.ns['result']; raw=portable_raw")
    rep("assert paid==expected and sum(paid.values())==495304", f"assert paid==expected and sum(paid.values())=={five['calls']}")
    rep("assert sum(r*n for r,n in paid.items())==2837560 and", f"assert sum(r*n for r,n in paid.items())=={five['rank_mass']} and")
    mod = types.ModuleType('fs493_lowering'); mod.__file__ = 'five_stage_bit_global_lowering [493 rebinding]'
    mod.COEFFICIENTS = []; mod.portable_raw = raw
    exec(compile(src, mod.__file__, 'exec'), mod.__dict__)
    physical = dict(categories=tele['categories'], paid_histogram=raw['one_stage_helper_histogram_including_copies'],
                    tagged_scalar_sha256=tele['tagged_sha256'])
    ctx = dict(W=m.W, C=m.C, initial_state=tele['initial_state'], ZERO=m.W.register([]), FULL=m.W.w['full_frame'], result=physical)
    lower = mod.Lowerer(records, ctx)
    res = mod.verify(lower)
    res['stage_coefficients'] = mod.COEFFICIENTS[0]
    return mod, lower, res


def geometry(P234, mod, m):
    src = (Path(P234) / V8 / 'code/five_stage_bit_global_lowering_geometry_20261009.py').read_text()
    start = src.index("W,C=ctx['W'],ctx['C']"); stop = src.index("assert all(sha(BASE.parent/p)==h")
    body = src[start:stop]
    ns = dict(ctx=dict(W=m.W, C=m.C, regs=m.regs), L=mod, sp=__import__('sympy'), array=array, lru_cache=__import__('functools').lru_cache)
    exec(compile(body, 'five_stage_bit_global_lowering_geometry [493 context]', 'exec'), ns)
    return dict(checked_actual_ports=ns['checked'], checked_actual_entrances=ns['helpers'],
                distinct_entrances_noncommuting=bool(ns['sigma'][0] * ns['sigma'][1] != ns['sigma'][1] * ns['sigma'][0]))


def primes(P234, m, used):
    pw = load('fs493_prime_validator', Path(P234) / V8 / 'code/prime_witnesses.py')
    w, c = m.W, m.C
    allused = set(used) | set(w.opframe) | set(w.w['source_frame']) | set(w.w['root_frame']) | {w.w['full_frame'], w.register([])}
    allused.update(g['frame'] for g in w.gauge.values())
    for e in w.k['entries']: allused.update((e['mix_frame'], e['deliver_frame']))
    for t in range(w.v): allused.add(w.register(w.module.kernel([c.cov[t]], w.h)[0]))
    groups = {}
    for f in sorted(allused): groups.setdefault(sha(json.dumps(c.B[f], separators=(',', ':')).encode()), f)
    factors = set(); largest = 0
    for h_, f in sorted(groups.items()):
        B = c.B[f]
        if not B: continue
        s = list(map(sum, B))
        gram = [[9 * sum(a * b for a, b in zip(x, y)) - s[i] * s[k] for k, y in enumerate(B)] for i, x in enumerate(B)]
        det = pw.det(gram); assert det != 0
        powers, residual = pw.factor_witness(det)          # asserts residual < 2^80 and the factor identity
        factors.update(int(p) for p, e in powers.items() if e); largest = max(largest, abs(det).bit_length())
    return dict(unique_bases=len(groups), current_frame_ids=len(allused), prime_factors=sorted(factors),
                maximum_determinant_bits=largest, all_remaining_factors_below_2_power_80=True,
                basis_inventory_sha256=sha(json.dumps(sorted(groups), separators=(',', ':')).encode()))


def finite(raw, fwd, inv):
    """PR234's finite BIT bill, recomputed from fresh values (formulas unchanged)."""
    m = 120; v = raw['v']; R = raw['physical_R']; W = 4 * v + R; d = m * m
    H = {int(k): n for k, n in raw['five_stage_profile']['histogram'].items()}; E = sum(H.values())
    J = 20 * v + 10 * R + 4 * v; good = 8 * m * m + 8; high = 16 * (d + 1) ** 2; N = 2 * m
    unit = 5 * fwd['literal_unit_additions'] + 6 * v
    payload = 64 * fwd['max_intermediate_row_l1'] ** 3 * inv['max_intermediate_row_l1'] ** 2
    payload_bits = payload.bit_length(); assert payload_bits <= 128
    fallback = 6 * N * (N - 1) + 3 * N + 6 * (N - 1); assert fallback < 32 * m * m
    coefficient = unit + J * high + J * (W + 24) + E * good + E * (128 * N ** 3) + 16 * m ** 3 + 120 + E + 1
    assert coefficient < 2 ** 80
    return dict(m=m, W=W, positive_rank_children=E, unit_expanded_additions=unit, route_and_final_exchange_families=J,
                payload_prefix_upper=payload, payload_prefix_bits=payload_bits, q_power_coefficient=coefficient, fallback_children=32 * m * m,
                scope='PR234 finite_check formulas with fresh 493-helper values; same retained primitive/tape hypotheses.')


def build(P210, P234, progress=lambda s: None):
    with tempfile.TemporaryDirectory(prefix='fs493-') as tmp:
        tree = assemble_tree(P210, P234, tmp); progress('tree assembled')
        m = prepare(tree); progress('PR210 493 helper prepared')
        scalar = scalar_proofs(m); progress('F2, majorant, both integer signs and 17 controls passed')
        records = array('i')
        tele = telescope493.run(m, records, CATEGORIES); progress('physical telescope passed')
        v = m.W.v; h = m.W.h; R = len(m.regs); n = 2 * v + R
        fwd = projection(records, n, v); inv = projection(records, n, v, True)
        assert fwd['event_sha256'] == tele['scalar_sha256'] and fwd['weighted_additions'] == tele['events']
        progress('independent projection and inverse passed')
        H = tele['hist']
        ent = Counter(g['dim'] for s, g in m.W.gauge.items() if s not in m.W.donor and s not in m.borrow)
        assert dict(ent) == {20: 2200, 18: 13, 12: 18, 13: 48}
        assert sum(k * x for k, x in H.items()) == h * R + 2 * v * (h - 1) + 24 * 22 - sum(a * x for a, x in ent.items())
        five = Counter({k: 5 * x for k, x in H.items()}); five.update({k: 2 * v for k in (2 * h - 2, h - 1, 2 * h + 2, 4)})
        for a, x in ent.items(): five[5 * a] += x
        Wl = 4 * v + R; mass = sum(k * x for k, x in five.items())
        raw = dict(source_head='13311491eb74a3a9a443ba4e318c68c263f064f0', h=h, v=v, physical_R=R,
                   source_aliases=len(m.borrow), one_stage_helper_histogram_including_copies={str(k): x for k, x in sorted(H.items())},
                   auxiliary_entrance_rank_histogram={str(k): x for k, x in sorted(ent.items())},
                   five_stage_profile=dict(m=120, W=Wl, histogram={str(k): x for k, x in sorted(five.items())}, calls=sum(five.values()),
                                           rank_mass=mass, deficit=120 * Wl - mass, maxchild=max(five)))
        assert raw['five_stage_profile']['deficit'] == 4 * v - 5 * 24 * 22 == 4400
        mod, lower, glob = lowering(P234, m, records, tele, raw); progress('five-stage global lowering passed')
        geo = geometry(P234, mod, m); progress('exact geometry passed')
        prime = primes(P234, m, tele['used_frames']); progress('prime determinants passed')
        fin = finite(raw, fwd, inv)
        summary = dict(
            scalar=dict(F2=scalar['F2'], majorant=scalar['majorant'], integer_directions=[z['direction'] for z in scalar['integer']],
                        controls_rejected=sorted(scalar['controls'])),
            telescope=dict(events=tele['events'], categories=dict(sorted(tele['categories'].items())), scalar_sha256=tele['scalar_sha256'],
                           tagged_sha256=tele['tagged_sha256'], copies=tele['copies'], center_reads=tele['center_reads'],
                           physical_registers=tele['physical_registers'], local_records=len(records) // 6),
            projection=dict(forward=fwd, inverse=inv),
            lowering=dict(program_sha256=glob['program_sha256'], paid_calls=glob['paid_calls'], paid_rank_mass=glob['paid_rank_mass'],
                          deficit=glob['deficit'], opcode_counts={str(k): x for k, x in glob['opcode_counts'].items()},
                          stage_coefficients={str(k): x for k, x in glob['stage_coefficients'].items()},
                          bank_F2_endpoint_after_terminal_relabel=glob['bank_F2_endpoint_after_terminal_relabel'],
                          controls_rejected=glob['controls_rejected']),
            geometry=dict(ports=[z['port'] for z in geo['checked_actual_ports']], entrances=len(geo['checked_actual_entrances']),
                          distinct_entrances_noncommuting=geo['distinct_entrances_noncommuting']),
            primes=prime, finite=fin)
        return raw, summary
