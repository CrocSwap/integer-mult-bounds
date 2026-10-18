#!/usr/bin/env python3
"""Replay of the T74 side-condition coverage audit (pending PR #2044 head 322949a5).

Scope: an adversarial *coverage* audit of the asymptotic side conditions quoted in the
notes of research/capped-fusion-t74-k554/ (PR #2044).  It is NOT a proof of the T74
claim, NOT a re-certification of the supplier endpoint and NOT a multiplication theorem.
It checks a recorded classification against exact rational arithmetic:

  (a) rebuild the final parameter point from ONE irreducible input (the certified complex
      endpoint b_cert of LEDGER.json `complex_lower_pinned`) and closed-form definitions
      transcribed from outer/check_ledger.py; check SHA-256 fingerprints of the rebuilt
      rationals (recorded from LEDGER.json);
  (b) evaluate every canonical condition key at every point exactly (ast-whitelisted
      evaluator: Expression/BinOp(+,-,*,/,**int)/UnaryOp/Name/int Constant only) and
      require the recorded truth values;
  (c) require classification consistency;
  (d) recompute the 49 non-comparison LEDGER strict checks (and 7 rejecting-control rows)
      from formulas transcribed from check_ledger.py and require every COVERED mapping;
  (e) run negative controls that must be rejected;
  (f) optional --source-root DIR: re-hash every audited source file, re-locate every quote
      within +-2 lines, and compare the rebuilt point / checks / controls with LEDGER.json.

Standard library only; Python 3.10-3.14; run as `python3 -I -B verify.py`.  -O is refused.
"""
import sys

if sys.flags.optimize:
    sys.stderr.write('verify.py refuses to run under -O/-OO\n')
    sys.exit(2)

import argparse
import ast
import copy
import hashlib
import json
import time
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

HERE = Path(__file__).resolve().parent
PKG_REL = 'research/capped-fusion-t74-k554'
POINT_NAMES = ('final', 'pr1786', 'pr1673', 'pr1673mc')
CLASSES = ('COVERED', 'AUTO_TRUE', 'FALSE_AT_POINT', 'UNCOVERED_TRUE', 'STALE_TEXT_ONLY',
           'OBSOLETE', 'NON_EXPONENT', 'AMBIGUOUS')
FLAG_CLASSES = ('FALSE_AT_POINT', 'UNCOVERED_TRUE', 'AMBIGUOUS', 'STALE_TEXT_ONLY')
LIVE_CLASSES = ('COVERED', 'AUTO_TRUE', 'STALE_TEXT_ONLY', 'UNCOVERED_TRUE', 'AMBIGUOUS')
ENCODED_KINDS = ('ledger', 'implied', 'assert', 'control')
MAX_POW = 100000


class Fail(Exception):
    pass


class Unknown(Exception):
    """name outside the declared vocabulary (hard error)"""


class Undefined(Exception):
    """vocabulary name not defined at this point (truth value n/a)"""


class Forbidden(Exception):
    """expression uses a node outside the whitelist"""


def need(ok, msg):
    if not ok:
        raise Fail(msg)


# ---------------------------------------------------------------- safe exact evaluator
_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
_UNOPS = (ast.UAdd, ast.USub)


def parse(src):
    if not isinstance(src, str) or len(src) > 4000:
        raise Forbidden('expression must be a short string')
    try:
        tree = ast.parse(src, mode='eval')
    except SyntaxError as e:
        raise Forbidden(f'syntax: {e}') from None
    for node in ast.walk(tree):
        if isinstance(node, (ast.Expression, ast.Load, ast.Name) + _BINOPS + _UNOPS):
            continue
        if isinstance(node, ast.BinOp) and isinstance(node.op, _BINOPS):
            continue
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, _UNOPS):
            continue
        if isinstance(node, ast.Constant) and type(node.value) is int:
            continue
        raise Forbidden(f'{type(node).__name__} not allowed in {src!r}')
    return tree


def _ev(node, env, vocab):
    if isinstance(node, ast.Expression):
        return _ev(node.body, env, vocab)
    if isinstance(node, ast.Constant):
        return Fraction(node.value)
    if isinstance(node, ast.Name):
        if node.id not in vocab:
            raise Unknown(node.id)
        if node.id not in env:
            raise Undefined(node.id)
        return env[node.id]
    if isinstance(node, ast.UnaryOp):
        v = _ev(node.operand, env, vocab)
        return -v if isinstance(node.op, ast.USub) else v
    if isinstance(node, ast.BinOp):
        x = _ev(node.left, env, vocab)
        y = _ev(node.right, env, vocab)
        op = node.op
        if isinstance(op, ast.Add):
            return x + y
        if isinstance(op, ast.Sub):
            return x - y
        if isinstance(op, ast.Mult):
            return x * y
        if isinstance(op, ast.Div):
            if y == 0:
                raise Forbidden('division by zero')
            return x / y
        if isinstance(op, ast.Pow):
            if y.denominator != 1 or abs(y.numerator) > MAX_POW:
                raise Forbidden('** needs a bounded integer exponent')
            if x == 0 and y < 0:
                raise Forbidden('0 ** negative')
            return x ** int(y)
    raise Forbidden(type(node).__name__)


def seval(src, env, vocab):
    return Fraction(_ev(parse(src), env, vocab))


def exact_literal(s):
    """'123', '-1/7', '0.00173' -> Fraction (decimal/rational literal only)."""
    need(isinstance(s, str) and s and len(s) < 100000, 'bad exact literal')
    body = s[1:] if s[0] == '-' else s
    num, _, den = body.partition('/')
    ip, _, fp = num.partition('.')
    need(ip.isdigit() and (fp == '' or fp.isdigit()) and (den == '' or den.isdigit()), f'bad exact literal {s[:40]!r}')
    return Fraction(s)


def dec(x, prec=25):
    with localcontext() as cx:
        cx.prec = prec
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def frac_sha(x):
    return hashlib.sha256(str(Fraction(x)).encode()).hexdigest()


# ---------------------------------------------------------------- points
def build_point(pt, vocab, overrides=None):
    env = {}
    for name, val in pt['definitions']:
        need(name in vocab, f'definition of unknown variable {name}')
        need(name not in env, f'duplicate definition {name}')
        if overrides and name in overrides:
            env[name] = overrides[name]
            continue
        if isinstance(val, str):
            env[name] = seval(val, env, vocab)
        elif isinstance(val, dict) and set(val) == {'exact'}:
            env[name] = exact_literal(val['exact'])
        elif isinstance(val, dict) and set(val) == {'floor_grid', 'grid', 'minus'}:
            # floor(x * grid) / grid - minus   (check_ledger.py l.121: kappa)
            g = seval(val['grid'], env, vocab)
            need(g.denominator == 1 and g > 0, 'grid must be a positive integer')
            x = seval(val['floor_grid'], env, vocab)
            env[name] = Fraction((x * g).__floor__(), g.numerator) - seval(val['minus'], env, vocab)
        else:
            raise Fail(f'bad definition form for {name}')
    return env


# ---------------------------------------------------------------- ledger transcription
# Transcribed from PR #2044 outer/check_ledger.py ledger() (lines 110-196) at the final point.
# Only exact edits: Q(n,d) -> n/d, Q(x) -> x, tau_eff.numerator/denominator -> tau_num/tau_den.
# The 13 comparison-only checks (improvement_over_*) are kappa minus other packages' kappas;
# they are not side conditions and are only re-checked from LEDGER.json in --source-root mode.
LEDGER_VOCAB = {'eps', 'beta', 'q_', 'a', 'b', 'r', 'stop', 'slack', 'zeta', 'tau_eff', 'tau_num', 'tau_den',
                'THETA_POWER', 'halo_power', 'core_power', 'bit', 'c', 'xi', 'saving', 'kappa', 'tau', 'sigma',
                'internal', 'leaf', 'lam', 'key', 'sparse_union_movement'}
MARGINS = [  # check_ledger.py lines 128-136
    ('main_transform', 'saving'),
    ('global_coordinate_router', 'a'),
    ('fused_gaussian', '1-eps+q_*beta'),
    ('group_bit_router', '1-eps+a*beta'),
    ('group_scans', '1-eps+beta'),
    ('boundary_algebraic_matrix', 'c+xi-eps'),
    ('sparse_union_movement', 'xi+1/2-eps'),
    ('polynomial_products', 'eps'),
    ('microbox_face_corrections', '1-(eps+beta+halo_power-core_power+2)'),
]
CHECKS = [  # check_ledger.py lines 142-181 (comparison-only rows omitted)
    ('actual_bit_above_effective', 'bit-a'),
    ('complex_above_effective', 'b-a'),
    ('q_positive', 'q_'),
    ('complex_endpoint', 'b-q_'),
    ('q_below_effective', 'a-q_'),
    ('stop_positive', 'stop'),
    ('stop_below_one', '1-stop'),
    ('leaf_saving_above_effective', '(1-stop)*b-a'),
    ('q_below_internal', '1-internal-q_'),
    ('q_below_leaf', '1-leaf-q_'),
    ('lambda_above_tau', 'lam-tau'),
    ('lambda_above_sigma', 'lam-sigma'),
    ('lambda_above_internal', 'lam-internal'),
    ('lambda_prime_above_lambda', '1-q_-lam'),
    ('lambda_prime_above_leaf', '1-q_-leaf'),
    ('epsilon_positive', 'eps'),
    ('epsilon_below_one', '1-eps'),
    ('cap_above_band', 'xi-1/2'),
    ('cap_below_cell', 'eps-xi'),
    ('group_positive', 'beta'),
    ('group_below_dimension', 'eps-beta'),
    ('support_router_span', '1-beta'),
    ('group_gauge_power_slack', '1-(2*xi-THETA_POWER)-r-beta'),
    ('actual_logarithmic_group_guard', '1-(2*xi-THETA_POWER)-beta'),
    ('global_gamma_power_slack', '1-eps-r'),
    ('actual_logarithmic_gamma_guard', '1-eps'),
    ('alpha_logarithm_absorption', 'r'),
    ('group_key_fits_record', '1-key'),
    ('membership_arithmetic_fits_record', '1-beta-2*(1-eps)'),
    ('microbox_halo_volume', 'core_power-halo_power-beta'),
    ('positive_layout_slack', 'slack'),
    ('short_record_fallback', 'eps-a'),
    ('complex_below_one_over_32', '1/32-b'),
    ('strassen_integer_power_gap', '2**tau_num-7**tau_den'),
    ('theta_positive_polynomial_power', 'THETA_POWER'),
    ('cap_below_phase_cell_power', 'THETA_POWER-xi'),
    ('halo_covers_generic_inverse_radius', 'halo_power-43'),
    ('union_tag_work_per_visit_fits_record', '1-beta'),
    ('union_header_fits_record', '1-beta'),
    ('source_axis_superpolynomial', '1-eps'),
]
COMPARISON_CHECKS = ['improvement_over_online_final', 'improvement_over_previous_local_final',
                     'improvement_over_pr1786', 'improvement_over_pr1828', 'improvement_over_pr1839',
                     'improvement_over_pr1875', 'improvement_over_pr1876', 'improvement_over_pr1897',
                     'improvement_over_pr1758', 'improvement_over_pr1699', 'improvement_over_pr1712',
                     'improvement_over_previous_package', 'improvement_over_pkg_k2']
# rejecting-control rows that the ledger adds under a flag (check_ledger.py lines 137-139, 183-186)
CONTROL_ROWS = {
    'old_g_factor_union_row_above_kappa': ('old_g_factor_union_row', '(1-eps-beta-1/2+xi)-kappa'),
    'old_per_axis_scan_above_kappa': ('old_per_axis_scan', '(1-eps)-kappa'),
    'unnecessary_full_key_sort_above_kappa': ('full_key_sort', '(sparse_union_movement-key)-kappa'),
    'unrecentered_group_gauge': ('full_cell_gauge', '1-THETA_POWER-r-beta'),
    'old_theta_chirp_guard': ('old_theta_chirp_guard', '1-(2*xi-eps)-r-beta'),
    'old_linear_guard': ('old_linear_guard', '1-xi-r-beta'),
    'old_union_tag_2beta': ('old_union_tag_2beta', '1-2*beta'),
}


def ledger_recompute(P, floor_grid):
    """P: rebuilt final point. Returns (checks, margins, control_rows, kappa)."""
    V = LEDGER_VOCAB
    env = {'eps': P['eps'], 'beta': P['beta'], 'q_': P['q'], 'a': P['a'], 'b': P['b'], 'r': P['r'],
           'stop': P['stop'], 'slack': P['s'], 'zeta': P['zeta'], 'tau_eff': P['tau'],
           'tau_num': Fraction(P['tau'].numerator), 'tau_den': Fraction(P['tau'].denominator),
           'THETA_POWER': P['TH'], 'halo_power': P['halo'], 'core_power': P['core'], 'bit': P['bit']}
    env['c'] = seval('(3-tau_eff)/2', env, V)
    env['xi'] = seval('eps*(1+q_)-c+slack', env, V)
    env['saving'] = seval('eps*q_', env, V)
    env['kappa'] = Fraction((env['saving'] * floor_grid).__floor__(), floor_grid) - P['backoff']
    env['tau'] = seval('1-a', env, V)
    env['sigma'] = seval('1-b', env, V)
    env['internal'] = env['tau'] + (1 - env['stop']) * max(env['sigma'] - env['tau'], Fraction(0))
    env['leaf'] = seval('sigma+stop*(1-sigma)', env, V)
    env['lam'] = seval('1-(q_+a)/2', env, V)
    env['key'] = seval('beta+1-eps', env, V)
    margins = {n: seval(f, env, V) for n, f in MARGINS}
    env['sparse_union_movement'] = margins['sparse_union_movement']
    checks = {n: seval(f, env, V) for n, f in CHECKS}
    for n, v in margins.items():
        checks[n + '_above_kappa'] = v - env['kappa']
    need(margins['boundary_algebraic_matrix'] == env['saving'] + env['slack'], 'check_ledger l.195 identity')
    need(margins['sparse_union_movement'] == env['saving'] + env['slack'] + (env['tau_eff'] - 2) / 2,
         'check_ledger l.196 identity')
    ctrl = {n: seval(f, env, V) for n, (_, f) in CONTROL_ROWS.items()}
    return checks, margins, ctrl, env


# ---------------------------------------------------------------- key evaluation
def key_value(kd, env, vocab):
    exprs = kd['expr'] if isinstance(kd['expr'], list) else [kd['expr']]
    need(exprs, 'empty key expression')
    return min(seval(e, env, vocab) for e in exprs)


def truth(v, rel, tol):
    if rel == '>0':
        return v > 0
    if rel == '>=0':
        return v >= 0
    if rel == '==0':
        return v == 0 if tol is None else abs(v) < tol
    raise Fail(f'bad relation {rel}')


def truth_table(keys, envs, vocab, tols):
    out = {}
    for name, kd in keys.items():
        row = {}
        for pt in POINT_NAMES:
            try:
                row[pt] = truth(key_value(kd, envs[pt], vocab), kd['rel'], tols[pt])
            except Undefined:
                row[pt] = None
        out[name] = row
    return out


# ---------------------------------------------------------------- classification consistency
def consistency_errors(inv, tt, files):
    err = []
    keys = inv['keys']
    for c in inv['conditions']:
        cid, cls = c['id'], c['classification']
        if cls not in CLASSES:
            err.append(f'{cid}: unknown class {cls}')
            continue
        for k in c['keys'] + c.get('operative_keys', []):
            if k not in keys:
                err.append(f'{cid}: unknown key {k}')
        if any(k not in keys for k in c['keys'] + c.get('operative_keys', [])):
            continue
        fin = [tt[k]['final'] for k in c['keys']]
        if cls in LIVE_CLASSES and not all(v is True for v in fin):
            err.append(f'{cid}: {cls} but a condition key is not true at final')
        if cls == 'COVERED' and not any(keys[k]['kind'] in ENCODED_KINDS or keys[k]['kind'] == 'auto' for k in c['keys']):
            err.append(f'{cid}: COVERED without any key')
        if cls == 'COVERED' and any(keys[k]['kind'] == 'none' for k in c['keys']):
            err.append(f'{cid}: COVERED but uses an unencoded key')
        if cls == 'UNCOVERED_TRUE' and any(keys[k]['kind'] in ('ledger', 'implied') for k in c['keys']):
            err.append(f'{cid}: UNCOVERED_TRUE but a key is ledger-encoded')
        if cls == 'FALSE_AT_POINT':
            if not any(v is False for v in fin):
                err.append(f'{cid}: FALSE_AT_POINT without a failing key at final')
            if c.get('load_bearing') is not False:
                err.append(f'{cid}: FALSE_AT_POINT must record load_bearing=false with operative keys')
            if not c.get('operative_keys'):
                err.append(f'{cid}: FALSE_AT_POINT without operative keys')
        if cls in ('FALSE_AT_POINT', 'OBSOLETE'):
            for k in c.get('operative_keys', []):
                if tt[k]['final'] is not True:
                    err.append(f'{cid}: operative key {k} not true at final')
        if cls == 'OBSOLETE':
            sup = c.get('superseded_by') or []
            if not sup:
                err.append(f'{cid}: OBSOLETE without superseding citation')
            for s in sup:
                if s.get('file') not in files or not isinstance(s.get('line'), int) or not 1 <= s['line'] <= files[s['file']]['lines']:
                    err.append(f'{cid}: bad superseding citation {s}')
        if cls == 'NON_EXPONENT' and not c.get('reason'):
            err.append(f'{cid}: NON_EXPONENT without description')
        if c['file'] not in files or not 1 <= c['line'] <= files[c['file']]['lines']:
            err.append(f'{cid}: bad file/line')
    return err


def load_bearing_false(inv, tt):
    n = 0
    for c in inv['conditions']:
        if c['classification'] in LIVE_CLASSES and any(tt[k]['final'] is not True for k in c['keys']):
            n += 1
        if c['classification'] == 'FALSE_AT_POINT' and c.get('load_bearing') is not False:
            n += 1
    return n


# ---------------------------------------------------------------- source-root checks
def resolve_root(d):
    d = Path(d)
    if (d / PKG_REL / 'outer' / 'LEDGER.json').is_file():
        return d / PKG_REL
    if (d / 'outer' / 'LEDGER.json').is_file():
        return d
    raise Fail(f'--source-root {d}: no {PKG_REL}/outer/LEDGER.json')


def source_errors(root, srcs, inv):
    err = []
    texts = {}
    for rel, meta in srcs['files'].items():
        p = root / rel
        if not p.is_file():
            err.append(f'missing source {rel}')
            continue
        data = p.read_bytes()
        if hashlib.sha256(data).hexdigest() != meta['sha256']:
            err.append(f'sha256 mismatch {rel}')
        if hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() != meta['git_blob']:
            err.append(f'git blob mismatch {rel}')
        if rel.endswith('.md'):
            texts[rel] = data.decode('utf-8').split('\n')
    for c in inv['conditions']:
        lines = texts.get(c['file'])
        if lines is None:
            err.append(f"{c['id']}: file {c['file']} not hashed")
            continue
        L = c['line']
        if c['quote'] not in '\n'.join(lines[max(0, L - 3):L + 2]):
            err.append(f"{c['id']}: quote not within +-2 lines of {c['file']}:{L}")
    return err


def ledger_errors(root, P, points, checks, ctrl):
    err = []
    L = json.loads((root / 'outer' / 'LEDGER.json').read_bytes())
    row = L['rows']['struct_boundary_radix_union']
    R = lambda node: Fraction(node['rational'])  # noqa: E731
    stored = {'eps': row['epsilon'], 'xi': row['xi'], 'beta': row['beta'], 'q': row['q'], 'a': row['a'],
              'r': row['r0'], 'zeta': row['zeta'], 's': row['slack'], 'kappa': row['kappa'],
              'b': L['complex_lower_short'], 'b_cert': L['complex_lower_pinned']}
    for n, node in stored.items():
        if R(node) != P[n]:
            err.append(f'LEDGER {n} != rebuilt')
    g = L['geometry_changes']
    if (R(g['theta_power']), Fraction(g['halo_power']), Fraction(g['core_power']), R(g['matrix_exponent'])) != \
            (P['TH'], P['halo'], P['core'], P['tau']):
        err.append('LEDGER geometry != rebuilt')
    sc = row['strict_checks']
    if len(sc) != 62 or set(sc) != set(checks) | set(COMPARISON_CHECKS):
        err.append('LEDGER strict-check names differ from transcription + comparison list')
    for n, v in checks.items():
        if n not in sc or R(sc[n]) != v:
            err.append(f'LEDGER strict check {n} != recomputed')
    allv = [R(x) for x in sc.values()]
    if not all(v > 0 for v in allv):
        err.append('LEDGER has a non-positive strict check')
    if min(allv) != P['MINCHECK']:
        err.append('LEDGER min strict check != MINCHECK')
    for n in COMPARISON_CHECKS:
        if n in sc and R(sc[n]) <= P['MINCHECK']:
            err.append(f'comparison row {n} below MINCHECK')
    rc = L['rejecting_controls']['struct_boundary_radix_union']
    for n, (cname, _) in CONTROL_ROWS.items():
        if n not in rc.get(cname, {}) or R(rc[cname][n]) != ctrl[n]:
            err.append(f'LEDGER rejecting control {cname}.{n} != recomputed')
    return err


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-root', help='checkout/archive of PR #2044 head (contains research/capped-fusion-t74-k554)')
    args = ap.parse_args()
    t0 = time.time()
    POINTS = json.loads((HERE / 'POINTS.json').read_text())
    INV = json.loads((HERE / 'INVENTORY.json').read_text())
    SRC = json.loads((HERE / 'SOURCES-T74.json').read_text())
    vocab = set(POINTS['vocabulary'])
    files = SRC['files']

    # (a) final point + ledger recomputation
    fin = POINTS['points']['final']
    envs = {}
    P = build_point(fin, vocab)
    floor_grid = int(seval(fin['ledger_floor_grid'], {}, vocab))
    checks, margins, ctrl, lenv = ledger_recompute(P, floor_grid)
    need(lenv['kappa'] == P['kappa'] and lenv['xi'] == P['xi'] and lenv['c'] == P['c'], 'point vs ledger kappa/xi/c')
    need(len(checks) == 49, f'expected 49 non-comparison checks, got {len(checks)}')
    P['MINCHECK'] = min(checks.values())
    P['MIN_NONMAIN_MARGIN'] = min(v - P['kappa'] for k, v in margins.items() if k != 'main_transform')
    P['MIN_MARGIN_ABOVE_KAPPA'] = min(v - P['kappa'] for v in margins.values())
    for n, h in fin['fingerprints'].items():
        need(frac_sha(P[n]) == h, f'final fingerprint mismatch for {n}')
    envs['final'] = P
    tols = {'final': None}
    for pt in POINT_NAMES[1:]:
        envs[pt] = build_point(POINTS['points'][pt], vocab)
        tol = POINTS['points'][pt].get('eq_tolerance')
        tols[pt] = seval(tol, {}, vocab) if tol else None
    print(f'[a] final point rebuilt from b_cert ({len(str(P["b_cert"].numerator))}-digit numerator); '
          f'{len(fin["fingerprints"])} fingerprints match; kappa = {dec(P["kappa"], 30)}')

    # (b) truth table
    keys = INV['keys']
    need(len(keys) == INV['counts']['keys'], 'key count')
    tt = truth_table(keys, envs, vocab, tols)
    bad = [(k, pt) for k in keys for pt in POINT_NAMES if tt[k][pt] != keys[k]['truth'][pt]]
    need(not bad, f'recorded truth mismatch: {bad[:5]}')
    for k, kd in keys.items():
        need(dec(key_value(kd, P, vocab)) == kd['final_value'], f'final_value display mismatch for {k}')
    print(f'[b] {len(keys)} keys x {len(POINT_NAMES)} points: recorded truth values reproduced exactly')

    # (c) classification consistency
    conds = INV['conditions']
    err = consistency_errors(INV, tt, files)
    need(not err, f'consistency: {err[:5]}')
    counts = {c: sum(1 for x in conds if x['classification'] == c) for c in CLASSES}
    need(len(conds) == INV['counts']['conditions'] and all(counts[c] == INV['counts'][c] for c in CLASSES), 'class counts')
    need(len({x['id'] for x in conds}) == len(conds), 'duplicate condition ids')
    need(sorted(INV['flagged_ids']) == sorted(x['id'] for x in conds if x['classification'] in FLAG_CLASSES), 'flagged ids')
    lbf = load_bearing_false(INV, tt)
    print(f'[c] {len(conds)} conditions consistent with their classes; load-bearing false = {lbf}')

    # (d) ledger links
    needed = set()
    for c in conds:
        if c['classification'] == 'COVERED':
            for k in c['keys']:
                needed.update(keys[k]['ledger_checks'])
    C = {'C__' + n: v for n, v in checks.items()}
    cv = set(vocab) | set(C)
    for k, kd in keys.items():
        v = key_value(kd, P, vocab)
        for ch in kd['ledger_checks']:
            need(ch in checks, f'{k}: unknown ledger check {ch}')
        if kd['kind'] == 'ledger':
            if k == 'all_checks_pos':
                need(v == min(checks.values()), 'all_checks_pos')
            for ch in kd['ledger_checks']:
                need(checks[ch] == v, f'{k} != ledger {ch}')
        if kd.get('identity'):
            need(seval(kd['identity'], dict(P, **C), cv) == v, f'{k}: identity fails')
        if kd['kind'] == 'implied':
            need(kd.get('identity') and all(checks[ch] > 0 for ch in kd['ledger_checks']), f'{k}: implied link')
        if kd.get('rejecting_control'):
            need(ctrl[kd['rejecting_control']] == v and v <= 0, f'{k}: control value')
    need(needed <= set(checks) and all(checks[n] > 0 for n in needed), 'needed ledger check not positive')
    need(all(v > 0 for v in checks.values()), 'non-positive recomputed check')
    need(all(v <= 0 for v in ctrl.values()), 'rejecting control row does not fire')
    print(f'[d] 49 non-comparison LEDGER checks recomputed, all > 0 (min {dec(P["MINCHECK"], 4)}); '
          f'{len(needed)} used by COVERED keys; {len(ctrl)} control rows fire')

    # (e) negative controls
    rejected = []

    def expect_reject(label, fn, *exc):
        try:
            fn()
        except exc or (Fail,):
            rejected.append(label)
            return
        raise Fail(f'negative control not rejected: {label}')

    def flipped(cid, new):
        inv2 = copy.deepcopy(INV)
        for c in inv2['conditions']:
            if c['id'] == cid:
                c['classification'] = new
        e = consistency_errors(inv2, tt, files)
        need(not e, 'flipped')

    first_cov = next(c['id'] for c in conds if c['classification'] == 'COVERED' and c['keys'])
    first_false = next(c['id'] for c in conds if c['classification'] == 'FALSE_AT_POINT')
    first_obs = next(c['id'] for c in conds if c['classification'] == 'OBSOLETE' and
                     any(tt[k]['final'] is False for k in c['keys']))
    expect_reject(f'flip {first_cov} COVERED->FALSE_AT_POINT', lambda: flipped(first_cov, 'FALSE_AT_POINT'), Fail)
    expect_reject(f'flip {first_false} FALSE_AT_POINT->COVERED', lambda: flipped(first_false, 'COVERED'), Fail)
    expect_reject(f'flip {first_obs} OBSOLETE->COVERED', lambda: flipped(first_obs, 'COVERED'), Fail)

    def drop_citation():
        inv2 = copy.deepcopy(INV)
        next(c for c in inv2['conditions'] if c['classification'] == 'OBSOLETE')['superseded_by'] = []
        need(not consistency_errors(inv2, tt, files), 'citation')
    expect_reject('OBSOLETE without citation', drop_citation, Fail)

    flips = []

    def corrupt_beta():
        P2 = build_point(fin, vocab, overrides={'beta': Fraction(1, 2)})
        P2.update({k: P[k] for k in ('MINCHECK', 'MIN_NONMAIN_MARGIN', 'MIN_MARGIN_ABOVE_KAPPA')})
        tt2 = truth_table(keys, dict(envs, final=P2), vocab, tols)
        flips.extend(sorted(k for k in keys if tt2[k]['final'] != keys[k]['truth']['final']))
        need(not flips, 'beta corrupted')
    expect_reject('beta := 1/2 at final changes recorded truth', corrupt_beta, Fail)

    def fp_beta():
        P2 = build_point(fin, vocab, overrides={'beta': Fraction(1, 2)})
        need(frac_sha(P2['beta']) == fin['fingerprints']['beta'], 'fingerprint')
    expect_reject('beta := 1/2 fails the LEDGER fingerprint', fp_beta, Fail)

    def undefined_key():
        k2 = dict(keys, bogus={'expr': 'q-undefined_var', 'rel': '>0'})
        truth_table(k2, envs, vocab, tols)
    expect_reject('key with undefined variable', undefined_key, Unknown)
    for bad_expr in ('abs(q)', 'q.numerator', '[q][0]', '1.5*q', 'q if q else eps', '2**(1/2)'):
        expect_reject(f'forbidden expression {bad_expr!r}',
                      lambda e=bad_expr: key_value({'expr': e}, P, vocab), Forbidden)

    def bad_definition():
        fin2 = copy.deepcopy(fin)
        fin2['definitions'][0] = [fin2['definitions'][0][0], {'exact': '__import__("os")'}]
        build_point(fin2, vocab)
    expect_reject('non-literal exact input', bad_definition, Fail)
    print(f'[e] {len(rejected)} negative controls rejected; beta := 1/2 flips {len(flips)} final truth values: '
          + ', '.join(flips))

    # (f) optional source root
    src_note = 'not run (no --source-root)'
    if args.source_root:
        root = resolve_root(args.source_root)
        e = source_errors(root, SRC, INV)
        need(not e, f'sources: {e[:5]}')
        e = ledger_errors(root, P, POINTS, checks, ctrl)
        need(not e, f'ledger: {e[:5]}')
        n_neg = 0
        src2 = copy.deepcopy(SRC)
        rel0 = sorted(src2['files'])[0]
        h = src2['files'][rel0]['sha256']
        src2['files'][rel0]['sha256'] = ('0' if h[0] != '0' else '1') + h[1:]
        need(any('sha256 mismatch' in x for x in source_errors(root, src2, INV)), 'tampered sha256 accepted')
        n_neg += 1
        inv2 = copy.deepcopy(INV)
        inv2['conditions'][0]['line'] += 10
        need(any('quote not within' in x for x in source_errors(root, SRC, inv2)), 'moved quote accepted')
        n_neg += 1
        rejected += ['tampered SOURCES sha256', 'quote line moved by +10']
        src_note = (f'{len(SRC["files"])} files re-hashed (sha256 + git blob), {len(conds)} quotes located within +-2 lines, '
                    f'LEDGER.json params/49 checks/{len(ctrl)} controls equal; {n_neg} source negative controls rejected')
    print(f'[f] source root: {src_note}')

    vv = INV.get('verification_verdicts', [])
    ids = {c['id'] for c in conds}
    unknown = [v.get('id') for v in vv if v.get('id') not in ids]
    print(f'[report] verification_verdicts: {len(vv)} entries'
          + (f' (unknown ids: {unknown})' if unknown else '') + ' (reported, not enforced)')
    for v in vv:
        print(f"  {v.get('id')}: {v.get('verdict')} ({v.get('verifier', '?')})")

    need(lbf == 0, 'load-bearing false condition present')
    n = {c.lower(): counts[c] for c in CLASSES}
    print(f'runtime {time.time() - t0:.1f}s; python {sys.version.split()[0]}; mode '
          + ('source-root' if args.source_root else 'default'))
    print(f'PASS_T74_SIDE_CONDITION_COVERAGE conditions={len(conds)} keys={len(keys)} covered={n["covered"]} '
          f'auto_true={n["auto_true"]} obsolete={n["obsolete"]} stale_text_only={n["stale_text_only"]} '
          f'non_exponent={n["non_exponent"]} false_at_point={n["false_at_point"]} uncovered_true={n["uncovered_true"]} '
          f'ambiguous={n["ambiguous"]} load_bearing_false={lbf} negative_controls={len(rejected)} '
          f'source_root={"checked" if args.source_root else "skipped"}')


if __name__ == '__main__':
    try:
        main()
    except (Fail, Unknown, Undefined, Forbidden, KeyError, ValueError, OSError) as e:
        print(f'FAIL_T74_SIDE_CONDITION_COVERAGE: {type(e).__name__}: {e}')
        sys.exit(1)
