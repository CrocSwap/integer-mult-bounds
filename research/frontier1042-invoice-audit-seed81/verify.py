#!/usr/bin/env python3
"""Standalone re-check of the selected PR1042 finite invoice and outer admission.

Independent verification, assignment seed 81. Standard library only. Nothing
from the repository is imported or executed: the committed selected assembly,
the committed selected replay archive and the cited PR589 record are read as
data. Prepared by Wronskode (@Wronskode) with substantial AI assistance from Claude
(Anthropic) via Claude Code. Apache-2.0.

Scope: arithmetic from the frozen owner audit and invoice receipts to kappa.
The receipts' semantic content (words, owners, hosting, local replays) and the
moment endpoints themselves are taken as data; see README.md.
"""
import argparse
import copy
import hashlib
import json
import sys
import tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
AUDIT = 'research/community-frontier1042-audit'
# Selected certificate at base ba82555c; archive members are pinned by the assembly itself.
ASSEMBLY_SHA256 = '093f35445812ea96fe1bfe6a3af7d769cb7f274e08f4fb30f71a17ed1161e54e'
BIT_PATH = 'research/e8-bit-p111-tuned/tune/EXPECTED.json'
BIT_BLOB = 'e293ddc557742637f9f679f083a1a282d87b1b13'   # PR589 blob, cited in the assembly
OWNER_MEMBER = 't16/global/audit/OWNERS-AND-PROFILE.json'
INVOICE_MEMBER = 't16/global/audit/PREFIX-AND-INVOICE.json'
ASSEMBLY_MEMBER = 't16/ASSEMBLY.json'


class Fail(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise Fail(msg)


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def git_blob(b):
    return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()


def ceil(x):
    return -(-x.numerator // x.denominator)


# ---------------------------------------------------------------- group order
def sp_order_product(n, q=2):
    """|Sp(2n,q)| = q^(n^2) prod_{j<=n} (q^(2j)-1)."""
    out = q ** (n * n)
    for j in range(1, n + 1):
        out *= q ** (2 * j) - 1
    return out


def sp_order_orbit(n, q=2):
    """Orbit-stabilizer form: count hyperbolic pairs level by level.

    A hyperbolic pair (e,f) of a 2k-dimensional symplectic space has
    q^(2k)-1 choices of e and q^(2k-1) choices of f with B(e,f)=1.
    """
    out = 1
    for k in range(1, n + 1):
        out *= (q ** (2 * k) - 1) * q ** (2 * k - 1)
    return out


def orthogonal_odd_brute(n):
    """|O(Q)| for Q = x0^2 + sum x_{2i-1} x_{2i} on F_2^(2n+1), by backtracking.

    A linear map preserves Q iff it preserves Q on a basis and the polar form
    B(x,y)=Q(x+y)+Q(x)+Q(y) on basis pairs. Only invertible maps are counted.
    """
    d = 2 * n + 1

    def Q2(x):
        v = x & 1
        for i in range(n):
            v ^= ((x >> (2 * i + 1)) & 1) & ((x >> (2 * i + 2)) & 1)
        return v

    def B(x, y):
        return Q2(x ^ y) ^ Q2(x) ^ Q2(y)

    basis = [1 << i for i in range(d)]
    count = 0

    def rank_ok(cols):
        rows, piv = [], []
        for c in cols:
            for p, r in zip(piv, rows):
                if c >> p & 1:
                    c ^= r
            if c == 0:
                return False
            p = c.bit_length() - 1
            rows.append(c)
            piv.append(p)
        return True

    def go(cols):
        nonlocal count
        k = len(cols)
        if k == d:
            count += 1
            return
        for y in range(1, 1 << d):
            if Q2(y) != Q2(basis[k]):
                continue
            if any(B(cols[i], y) != B(basis[i], basis[k]) for i in range(k)):
                continue
            if rank_ok(cols + [y]):
                go(cols + [y])

    go([])
    return count


# ---------------------------------------------------------------- inputs
def load_inputs(root):
    sel = json.loads((root / 'certificates/selected-result.json').read_bytes())
    need(sel['certificate'] == AUDIT + '/ASSEMBLY.json', 'selected certificate path moved')
    asm_bytes = (root / AUDIT / 'ASSEMBLY.json').read_bytes()
    need(sha256(asm_bytes) == sel['certificate_sha256'] == ASSEMBLY_SHA256,
         'ASSEMBLY.json does not match the selected-record pin')
    asm = json.loads(asm_bytes)
    need(sel['kappa'] == asm['kappa'], 'selected kappa differs from assembly')
    members = {}
    with tarfile.open(root / AUDIT / 'selected-replay.tar.gz') as tar:
        for name in (OWNER_MEMBER, INVOICE_MEMBER, ASSEMBLY_MEMBER):
            members[name] = tar.extractfile(name).read()
    need(members[ASSEMBLY_MEMBER] == asm_bytes, 'archived t16 assembly differs from committed copy')
    need(sha256(members[OWNER_MEMBER]) == asm['input_sha256']['owner_audit'], 'owner audit pin')
    need(sha256(members[INVOICE_MEMBER]) == asm['input_sha256']['fresh_invoice'], 'invoice pin')
    bit_bytes = (root / BIT_PATH).read_bytes()
    need(git_blob(bit_bytes) == BIT_BLOB == asm['bit_supplier']['git_blob_sha1'], 'PR589 blob pin')
    return dict(asm=asm, owner=json.loads(members[OWNER_MEMBER]),
                invoice=json.loads(members[INVOICE_MEMBER]), bit=json.loads(bit_bytes))


# ---------------------------------------------------------------- A: profile
def check_profile(d, out):
    asm, own, inv = d['asm'], d['owner'], d['invoice']
    calls = inv['selected_calls']
    need(len(calls) == 144, 'call count')
    need(sorted((c['stage'], c['replica']) for c in calls) == [(s, r) for s in range(9) for r in range(16)],
         'calls are not exactly 9 stages x 16 replicas')
    for c in calls:
        need(c['orientation'] == ('forward', 'backward')[c['stage'] % 2], 'orientation alternation')
    paid = Counter()
    for c in calls:
        p = inv['providers'][c['provider_id']]
        need(c['program_sha256'] == p['program_hashes'][c['orientation']], 'call program hash')
        paid.update({int(r): n for r, n in p['paid_profile'].items()})
    need(dict(paid) == {int(r): n for r, n in inv['selected_local_paid_profile'].items()},
         'sum of per-call paid profiles')
    total = Counter({int(r): n for r, n in own['paid_profile'].items()})
    idle = Counter(total)
    idle.subtract(paid)
    need(all(v >= 0 for v in idle.values()), 'negative idle remainder')
    idle = +idle
    need(sum(idle.values()) == own['explicit_idle_remainder_children'], 'idle remainder count')
    need({int(r): n for r, n in asm['complex_profile'].items()} == dict(total), 'assembly profile')
    mass = sum(r * n for r, n in total.items())
    m, W = 73, own['live']
    need(mass == own['rank_mass'], 'rank mass')
    need(m * W - mass == own['deficit'] == 5120, 'deficit')
    need(m * m > 2 * max(total) ** 2, 'halving guard m^2 > 2 max^2')
    need(inv['finite']['halving_integer_inequality'] == [m * m, 2 * max(total) ** 2], 'halving record')
    out['profile'] = dict(calls=144, local=dict(sorted(paid.items())), idle=dict(sorted(idle.items())),
                          idle_children=sum(idle.values()), rank_mass=mass, live=W, deficit=m * W - mass,
                          halving=[m * m, 2 * max(total) ** 2])


# ---------------------------------------------------------------- B: envelope
def check_envelope(d, out):
    inv, own = d['invoice'], d['owner']
    calls = inv['selected_calls']
    R = inv['helpers']
    need(R == 480 and own['owners_per_call'] == 2 * 112 + R, 'helpers per call')
    for c in calls:
        z = inv['providers'][c['provider_id']]['local'][c['orientation']]
        for k in ('events', 'macros', 'real_component_primitives', 'coefficient_work_primitive_count',
                  'pre_wrappers', 'post_wrappers'):
            need(c[k] == z[k], 'call field %s differs from provider orientation' % k)
    prim = sum(c['real_component_primitives'] for c in calls)
    need(prim == inv['selected_real_component_primitives'], 'selected primitives')
    need(sum(c['coefficient_work_primitive_count'] for c in calls) ==
         inv['selected_coefficient_work_primitive_count'], 'coefficient work')
    need(sum(c['macros'] for c in calls) == inv['selected_scalar_macros'], 'macros')
    wrap = 144 * sum(c['pre_wrappers'] + c['post_wrappers'] for c in calls)
    need(wrap == inv['wrapper_elementary_factors_charged'], 'wrapper factors')
    compiler = 64 * 74 ** 3
    need(inv['compiler'] == compiler, 'compiler constant')
    for p in inv['providers'].values():
        macros = max(z['macros'] for z in p['local'].values())
        need(p['local_adapters'] == 16 * (macros + p['children'] + 2 * 112 + R + 8) + 64 * 73, 'adapters')
        need(p['children'] == sum(p['paid_profile'].values()), 'provider child count')
        need(p['local_primitive_bound'] == max(z['real_component_primitives'] for z in p['local'].values())
             + p['local_adapters'] * compiler, 'local primitive bound')
    adapters = max(p['local_adapters'] for p in inv['providers'].values())
    lpb = max(p['local_primitive_bound'] for p in inv['providers'].values())
    need(adapters == inv['local_adapters'] and lpb == inv['local_primitive_bound'], 'shared maxima')
    # Retained dedicated two-bank parent geometry (two groups of R0=504 helpers).
    parent_live, parent_physical, parent_idle = 23408, 23922, 32256
    banks, rem = divmod(parent_live - 2 * 112 * 4 * 16, 9)
    need(rem == 0 and parent_physical == parent_live + 504 + 8 + 2, 'parent geometry')
    need(own['source_idle_children_charged'] == parent_idle, 'parent idle children')
    stock_id = inv['physical_stock_identity']
    need(stock_id == dict(data_and_owner_families=14336, local_helpers=R, private_centres=8, coefficient_work=2)
         and sum(stock_id.values()) == inv['physical'] == own['physical'], 'physical stock identity')
    need(inv['live'] == own['live'] == 14336, 'live stock')
    bridges, shifts = 2 * 112 * 144, 4 * 112 * 16
    moves = 2 * shifts
    nonlocal_items = (4 * 112 * 16 * 9 + 2 * 112 * 16 * 9 + 2 * 144 * R + parent_idle + 9 * banks + bridges
                      + shifts + moves + parent_live + parent_physical + wrap)
    outside = 8 * nonlocal_items + 64 * 73
    pervertex = (prim + bridges + shifts + moves + parent_live + (144 * adapters + outside) * compiler
                 + 64 * parent_physical)
    rebased = pervertex + 65 * (inv['physical'] - parent_physical) + (inv['live'] - parent_live)
    need(pervertex == inv['unhosted_pervertex'], 'unhosted per-vertex')
    need(rebased == inv['hosted_rebased_pervertex'], 'hosted rebased per-vertex')
    prior = inv['retained_prior_overcharge']
    need(prior['added_complete_new_pervertex'] == pervertex, 'prior overcharge adds fresh recount')
    used = max(pervertex, rebased, prior['previous_pervertex_allowance'] + pervertex)
    need(used == inv['conservative_pervertex_used'], 'conservative per-vertex used')
    out['envelope'] = dict(selected_primitives=prim, wrapper_factors=wrap, compiler=compiler,
                           local_adapters=adapters, local_primitive_bound=lpb, nonlocal_items=nonlocal_items,
                           unhosted_pervertex=pervertex, hosted_rebased_pervertex=rebased, used=used,
                           local_primitive_bound_bits=lpb.bit_length())
    return used


# ---------------------------------------------------------------- C: guards
def check_guards(d, used, out, group_n=36):
    inv, own = d['invoice'], d['owner']
    group = sp_order_product(group_n)
    need(group == sp_order_orbit(group_n), 'group order formulas disagree')
    stock = group * inv['physical']
    streamed = group * own['rank_mass']
    logical = group * used + 64
    router = inv['compiler'] * (logical + 1) * (stock + 1) ** 2
    literal = 2 * 2 ** 30000 * stock ** 2 + 8 * streamed + 4 * stock + 4 + 32 * 73
    total_mass = streamed + 2 ** 100000
    c0_need = 32 * 73 * total_mass * total_mass
    row = 2 * stock.bit_length() + 9909 + 252 + 1024
    f = inv['finite']
    need(f['G_exponent'] == 30000 and f['E_exponent'] == 100000 and f['C0_exponent'] == 210000, 'exponents')
    need(f['physical_stock_bits'] == stock.bit_length(), 'stock bits')
    need(f['router_bits'] == router.bit_length(), 'router bits')
    need(f['literal_bits'] == literal.bit_length(), 'literal bits')
    need(f['required_C0_bits'] == c0_need.bit_length(), 'C0 bits')
    need(f['physical_row_coefficient'] == row, 'row coefficient')
    need(f['retained_row_coefficient'] == 20161, 'retained row coefficient')
    checks = dict(local_primitive_bound=inv['local_primitive_bound'] < 2 ** 48,
                  logical=logical < 2 ** 6050, router=router < 2 ** 30000, literal=literal < 2 ** 100000,
                  mass=total_mass < 2 ** 100001, precision=c0_need < 2 ** 210000,
                  tape=2 * total_mass + 18 < 2 ** 210000, row=row < 20161,
                  halving=73 * 73 > 2 * 48 * 48)
    need(all(checks.values()), 'failed guards: %s' % [k for k, v in checks.items() if not v])
    need(checks == inv['strict_checks'], 'recorded strict checks differ')
    prefix = max(z['prefix_bits'] for p in inv['providers'].values() for z in p['local'].values())
    need(inv['global_prefix_bits'] == prefix + 37 + 144 + 144 + 4, 'global prefix bits')
    need(0 < inv['global_prefix_bits'] <= inv['charged_prefix_bits'] == 512, 'prefix charge')
    need(inv['row_prefix_extra'] == 2 * inv['charged_prefix_bits'], 'row prefix reserve')
    bits = lambda x: x.bit_length()
    out['guards'] = dict(
        group='|Sp(72,2)| = |O(73,2)|', group_bits=bits(group), stock_bits=bits(stock),
        headroom_bits=dict(local_primitive_bound=48 - bits(inv['local_primitive_bound']),
                           logical=6050 - bits(logical), router=30000 - bits(router),
                           literal=100000 - bits(literal), streamed_mass_below_2E=100000 - bits(streamed),
                           precision=210000 - bits(c0_need), tape=210000 - bits(2 * total_mass + 18)),
        row=[row, 20161], halving=[73 * 73, 2 * 48 * 48],
        prefix=dict(local_max=prefix, global_bits=inv['global_prefix_bits'], charged=512))


# ---------------------------------------------------------------- D: outer
def assembly_slacks(a, b, kappa, eta, beta, literal_gap=Q(1), row_gap=Q(10 ** 6) - Q(51 * 20161, 25)):
    """The 47 retained strict constraints.

    a is the bootstrapped exponent and b the complex endpoint; the bit endpoint
    enters only through the bootstrap target s = min(c, (1-beta)b) - 10^-27.
    """
    tau, sigma = 1 - a, 1 - b
    q = a * (1 - 2 * eta)
    lp = 1 - q
    lam = (tau + lp) / 2
    c = q + eta / 4
    eps = (1 - eta) / (1 + q)
    g = eps * q
    r = (g + 1 - eps) / 2
    delta = eta / 8
    internal = tau + (1 - beta) * max(sigma - tau, Q(0))
    leaf = sigma + beta * (1 - sigma)
    margins = dict(balanced_prefix=1 - eps, coordinate_movement=a, compact_phase_layer=g, bulk_exposure=a,
                   Gaussian_arithmetic=min(1 - eps - delta, r - delta), scalar_work=1 - eps - delta,
                   dimension=eps)
    s = dict(bit_positive=a, complex_above_bit=b - a, complex_below_one_over32=Q(1, 32) - b,
             beta_positive=beta, beta_below_one=1 - beta, leaf_saving_above_bit=(1 - beta) * b - a,
             q_positive=q, q_below_internal=1 - internal - q, q_below_leaf=1 - leaf - q, c_positive=c,
             c_below_one=1 - c, q_below_reservations=c - q, lambda_above_tau=lam - tau,
             lambda_above_sigma=lam - sigma, lambda_above_internal=lam - internal,
             lambda_prime_above_lambda=lp - lam, compact_leaf=lp - leaf, compact_reservations=lp - (1 - c),
             lambda_prime_below_one=q, epsilon_positive=eps, epsilon_below_one=1 - eps, guard_width=1 - eps,
             K_geometry=1 - eps * (1 + c), K_dominates_log=eps * c, record_suffix=1 - eps,
             phase_local=1 - eps - delta, phase_boundary=r - delta, gamma_sublinear=1 - eps - r,
             cell_above_band=eps - (1 - r) / 2, prime_interval_packing=1 - eps, alpha_positive=r,
             alpha_below_one=1 - r, alpha_below_one_fourth=Q(1, 4) - r, delta_positive=delta,
             delta_below_one_eighth=Q(1, 8) - delta, short_record_fallback=eps - a,
             small_field_exposure=1 - eps - g, artificial_boundary=8 - eps + r - delta - g,
             literal_scalar_guard=literal_gap, row_product_gap=row_gap)
    for k, v in margins.items():
        s[k + '_above_kappa'] = v - kappa
    assert len(s) == 47
    return s, g


def bootstrap(b, c, eta, beta, levels=7, reserve=512):
    s = min(c, (1 - beta) * b) - Q(1, 10 ** 27)
    need(0 < s < c and s < (1 - beta) * b, 'bootstrap target')
    chain, cuts = [Q(384599, 10 ** 10)], []
    for _ in range(levels):
        old = chain[-1]
        a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
        need(old < a < s < 1 - a and gap > 0, 'bootstrap step order')
        quad, lin = ceil(36 / gap ** 2), ceil(2 * (4 + reserve) / gap)
        cut = max(quad, lin)
        cuts.append(dict(exponent=a, gap=gap, cutoff_log2=cut, quadratic_dominates=quad >= lin))
        chain.append(a)
    return chain[-1], cuts


def kappa_from(a, eta):
    q = a * (1 - 2 * eta)
    ticks = (1 - eta) * q / (1 + q) * 10 ** 18
    return Q((ticks.numerator - 1) // ticks.denominator, 10 ** 18)


def check_outer(asm, out, b, c, label, rec_cuts, rec_outer, rec_kappa, rec_controls):
    eta = beta = Q(1, 10 ** 24)
    a, cuts = bootstrap(b, c, eta, beta)
    need(len(rec_cuts) == 7, label + ' bootstrap length')
    for mine, rec in zip(cuts, rec_cuts):
        need(str(mine['exponent']) == rec['exponent'] and str(mine['gap']) == rec['gap']
             and str(mine['cutoff_log2']) == rec['cutoff_log2'], label + ' bootstrap record')
        need(mine['cutoff_log2'] * mine['gap'] ** 2 >= 36 and mine['cutoff_log2'] * mine['gap'] >= 2 * 516,
             label + ' cutoff covers both terms')
    k = kappa_from(a, eta)
    need(k == Q(rec_kappa), label + ' kappa')
    slacks, g = assembly_slacks(a, b, k, eta, beta)
    need(set(slacks) == set(rec_outer), label + ' constraint names')
    need(all(Q(rec_outer[n]) == v for n, v in slacks.items()), label + ' slack values')
    need(all(v > 0 for v in slacks.values()), label + ' strict slacks')
    # kappa is the largest 10^-18 grid point strictly below the absorption margin g.
    need(k < g <= k + Q(1, 10 ** 18), label + ' kappa is not the last grid point below g')
    controls = []
    for name, kk, ee, bb in [('next_grid', k + Q(1, 10 ** 18), eta, beta), ('zero_eta', k, Q(0), beta),
                             ('zero_beta', k, eta, Q(0)), ('unit_beta', k, eta, Q(1))]:
        sl, _ = assembly_slacks(a, b, kk, ee, bb)
        if min(sl.values()) <= 0:
            controls.append(name)
    need(controls == rec_controls == ['next_grid', 'zero_eta', 'zero_beta', 'unit_beta'], label + ' controls')
    # Reserve sensitivity: the quadratic term decides every cutoff while gap <= 18/(4+P).
    max_reserve = min((18 / cut['gap']).__floor__() - 4 for cut in cuts)
    smallest = sorted(slacks, key=lambda n: slacks[n])[:3]
    out[label] = dict(bootstrap_levels=7, final_exponent_decimal=float(a), kappa=str(k),
                      absorption_gap_over_kappa=str(g - k), slacks=47, all_quadratic=all(x['quadratic_dominates'] for x in cuts),
                      reserve_insensitive_up_to=max_reserve, min_slack_names=smallest, controls=controls)


def check_assembly(d, out):
    asm, bit = d['asm'], d['bit']
    c = Q(asm['bit_lower'])
    need(c == Q(bit['nine']['bit_lower']), 'bit endpoint differs from PR589 record')
    w = bit['word']
    deficit = 32 * (2 * 4 * w['v'] - 9 * w['decoder_constant'])
    need(w['decoder_constant'] == sum(w['copy_ranks']) and deficit == asm['bit_supplier']['derived_deficit'],
         'bit deficit T(2Kv-L*cst)')
    bitH = {int(r): n for r, n in bit['nine']['profile'].items()}
    need(64 * bit['nine']['bit']['live'] - sum(r * n for r, n in bitH.items()) == deficit, 'bit mass identity')
    b, cb = Q(asm['complex_lower']), Q(asm['conservative_complex_lower'])
    need(cb < b < c, 'endpoint order: conservative < native complex < bit')
    check_outer(asm, out, b, c, 'native', asm['bootstrap'], asm['outer'], asm['kappa'], asm['controls'])
    check_outer(asm, out, cb, c, 'conservative', asm['conservative_bootstrap'], asm['conservative_outer'],
                asm['conservative_kappa'], asm['conservative_controls'])
    need(Q(asm['kappa']) - Q(asm['conservative_kappa']) > 0, 'native correction is a gain')


def run_all(d):
    out = {}
    check_profile(d, out)
    used = check_envelope(d, out)
    check_guards(d, used, out)
    check_assembly(d, out)
    return out


# ---------------------------------------------------------------- controls
def mutate(d, fn):
    e = copy.deepcopy(d)
    fn(e)
    return e


def controls(d):
    """Each mutation must be rejected by run_all."""
    def extra_idle(e):
        e['owner']['paid_profile']['1'] += 1

    def call_primitives(e):
        e['invoice']['selected_calls'][7]['real_component_primitives'] -= 1

    def drop_call(e):
        e['invoice']['selected_calls'].pop()

    def swap_orientation(e):
        c = e['invoice']['selected_calls'][3]
        c['orientation'] = 'backward' if c['orientation'] == 'forward' else 'forward'

    def physical_plus(e):
        e['invoice']['physical'] += 1
        e['owner']['physical'] += 1
        e['invoice']['physical_stock_identity']['coefficient_work'] += 1

    def prior_dropped(e):
        e['invoice']['conservative_pervertex_used'] = e['invoice']['unhosted_pervertex']

    def router_bits(e):
        e['invoice']['finite']['router_bits'] -= 1

    def row_bound(e):
        e['invoice']['finite']['physical_row_coefficient'] = 20161

    def kappa_up(e):
        e['asm']['kappa'] = str(Q(e['asm']['kappa']) + Q(1, 10 ** 18))

    def slack_edit(e):
        e['asm']['outer']['K_geometry'] = str(Q(e['asm']['outer']['K_geometry']) + Q(1, 10 ** 40))

    def bootstrap_cut(e):
        e['asm']['bootstrap'][3]['cutoff_log2'] = str(int(e['asm']['bootstrap'][3]['cutoff_log2']) - 1)

    def bit_endpoint(e):
        e['asm']['bit_lower'] = str(Q(e['asm']['bit_lower']) - Q(1, 10 ** 24))

    def complex_endpoint(e):
        e['asm']['complex_lower'] = str(Q(e['asm']['complex_lower']) + Q(1, 10 ** 24))

    def max_rank(e):
        # Count- and mass-preserving idle edit (48->52, 3->1, 3->1), applied to
        # both records, so only the halving guard 73^2 > 2*max^2 can reject it.
        for p in (e['owner']['paid_profile'], e['asm']['complex_profile']):
            p['48'] -= 1
            p['52'] = 1
            p['3'] -= 2
            p['1'] += 2
    cases = [extra_idle, call_primitives, drop_call, swap_orientation, physical_plus, prior_dropped,
             router_bits, row_bound, kappa_up, slack_edit, bootstrap_cut, bit_endpoint, complex_endpoint,
             max_rank]
    results = {}
    for fn in cases:
        try:
            run_all(mutate(d, fn))
        except (Fail, KeyError, AssertionError) as exc:
            results[fn.__name__] = str(exc)
        else:
            raise Fail('control accepted: ' + fn.__name__)
    # Group-order control: one smaller symplectic rank changes the recorded bit lengths.
    e = mutate(d, lambda e: None)
    try:
        out = {}
        check_profile(e, out)
        check_guards(e, check_envelope(e, out), out, group_n=35)
    except Fail as exc:
        results['group_Sp70'] = str(exc)
    else:
        raise Fail('control accepted: group_Sp70')
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=ROOT)
    ap.add_argument('--write', action='store_true', help='rewrite RESULT.json instead of comparing')
    args = ap.parse_args()
    small = {str(2 * n + 1): orthogonal_odd_brute(n) for n in (1, 2)}
    need(small == {str(2 * n + 1): sp_order_product(n) for n in (1, 2)} == {'3': 6, '5': 720},
         'small odd orthogonal groups do not match |Sp(2n,2)|')
    d = load_inputs(args.root.resolve())
    out = run_all(d)
    out['group_identity_small_cases'] = small
    out['controls_rejected'] = controls(d)
    out['status'] = 'PASS_FRONTIER1042_INVOICE_OUTER_INDEPENDENT'
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    target = HERE / 'RESULT.json'
    if args.write:
        target.write_text(text)
    else:
        need(target.read_text() == text, 'RESULT.json differs from regenerated result')
    print(out['status'], '| guards', len(out['guards']['headroom_bits']) + 2,
          '| slacks 94 | bootstrap 14 | controls', len(out['controls_rejected']))


if __name__ == '__main__':
    try:
        main()
    except Fail as exc:
        print('FAIL', exc)
        sys.exit(1)
