"""Admission-ready evidence for the typed-window z4 typed-echo schedule (KB1c).

Runs the pinned PR1087 chain's own admission/consistency machinery against the
typed-window schedule of PR 2595 as far as non-invasive execution reaches:
the frozen strict T16 replay (restore-parent ... admission-controls,
bit-supplier-controls, independent-t16) on the retained local word, the
invoice/assembly boundary (code/assemble.py) on the frozen receipts and on
typed-window candidate declarations, both certified moment engines on the
schedule's priced ledgers, and the verify_t16-style binding checks. Records
the exact stage and error of the first hard blocker at each boundary and the
named maintainer decisions that remain. No frozen pin is modified: every run
writes to a fresh temporary directory.

Aaron Wang, with help from opencode (substantial AI assistance). Apache-2.0.
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import traceback
from fractions import Fraction
from pathlib import Path

assert __debug__, 'Assertions required'
sys.set_int_max_str_digits(0)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
CHAIN = ROOT / 'research/gauge44-slots-t16'
SOURCE = ROOT / 'research/complex-k492-owner-repair/vendor/multicold'
ARCHIVE = ROOT / 'research/community-frontier1042-audit/selected-replay.tar.gz'
PR2595 = PKG / 'inputs/PR2595-RESULT.json'
PR386 = ROOT / 'research/split-centres-global/proofs/PR386-BIT-GEOMETRY.txt'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
Q = Fraction

# The vendored predecessor receipt is pinned here, not merely listed: it is a
# PR-head artifact (PR 2595 is not on the base commit) copied byte-exactly.
PR2595_SHA256 = 'a740acb4727ca5141154617e47986de41a3c7cfbfdac2ec2c5885eace55552e7'
PR2595_HEAD = '533bb00517ad0e9206ec34d2026a3977a2dc9a16'
PR2464_HEAD = 'f364b97ff4700147fc06e622b79952b9fe6c4fa8'
M73, LIVE = 73, 14336
TINY = Q(1, 10 ** 24)

INPUT_FILES = [
    'certificates/selected-result.json',
    'docs/research/agent-task-catalog.json',
    'research/gauge44-slots-t16/verify_t16.py',
    'research/gauge44-slots-t16/code/assemble.py',
    'research/gauge44-slots-t16/code/assembly_controls.py',
    'research/gauge44-slots-t16/code/bit_supplier_controls.py',
    'research/gauge44-slots-t16/code/invoice_allcold.py',
    'research/gauge44-slots-t16/code/witness.py',
    'research/gauge44-slots-t16/data/SPEC.json',
    'research/complex-k492-owner-repair/vendor/multicold/engines/moment.py',
    'research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py',
    'research/complex-k492-owner-repair/vendor/multicold/engines/outer.py',
    'research/split-centres-global/proofs/PR386-BIT-GEOMETRY.txt',
    'research/community-frontier1042-audit/selected-replay.tar.gz',
]
ARCHIVE_MEMBERS = [
    't16/global/audit/OWNERS-AND-PROFILE.json',
    't16/global/audit/PREFIX-AND-INVOICE.json',
    't16/global/audit/ASYNC-AUDIT.json',
    't16/ADMISSION-CONTROLS.json',
    't16/BIT-SUPPLIER-CONTROLS.json',
    't16/INDEPENDENT-T16.json',
    't16/ASSEMBLY.json',
    't16/REPLAY.json',
]


def evidence_bundle():
    """Inputs hashed: every chain input, the frozen replay archive and its members."""
    files = {name: sha(ROOT / name) for name in INPUT_FILES}
    files['research/z4-typed-window-admission-kb1c/inputs/PR2595-RESULT.json'] = sha(PR2595)
    assert files['research/z4-typed-window-admission-kb1c/inputs/PR2595-RESULT.json'] == PR2595_SHA256, 'vendored PR2595 pin'
    members = {}
    with tarfile.open(ARCHIVE, 'r:gz') as tar:
        for name in ARCHIVE_MEMBERS:
            members[name] = hashlib.sha256(tar.extractfile(name).read()).hexdigest()
    return {'files': files, 'archive_members': members}


def certify_bisect(M, H, m, W, bad):
    """Drive the chain's own moment() oracle past certify()'s built-in ceiling.

    engines/moment.py certify() bisects only on [0, Decimal('.003')] (line 78);
    the widened-window ledger's root lies above that ceiling. The acceptance
    oracle is unchanged: the same exact moment() bounds decide every grid point.
    Returns the 1e-24 grid endpoint (accepted) and its successor (rejected).
    """
    accept = lambda q: M.moment(H, m, W, Fraction(q, 10 ** 24), bad)[1] < 1
    lo, hi = 3 * 10 ** 21, 4 * 10 ** 21  # the widened ledger root is about 0.0031852
    assert accept(lo) and not accept(hi), 'bracket does not contain the root'
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if accept(mid):
            lo = mid
        else:
            hi = mid
    return Fraction(lo, 10 ** 24), Fraction(hi, 10 ** 24)


def load_engines():
    engines = {}
    for name in ('moment', 'base_two_moment', 'outer'):
        spec = importlib.util.spec_from_file_location('chain_engine_' + name, SOURCE / 'engines' / (name + '.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        engines[name] = module
    return engines


def check_moment(M, B, side, h, m, W, lower, deficit, bad):
    """The chain's own check_moment predicate (code/assemble.py), unchanged logic."""
    assert m * W - sum(r * n for r, n in h.items()) == deficit, 'coverage identity: ' + side
    assert m * m > 2 * max(h) ** 2, 'halving guard: ' + side
    rows = []
    for z, accept in [(lower, True), (lower + TINY, False)]:
        lo, up = M.moment(h, m, W, z, bad)
        blo, bup = B.moment(m, W, list(h.items()), z)
        if bad:
            fl, fu = B.moment(m, W, [(1, 32 * m * m * sum(h.values()))], z)
            blo += fl / 10 ** 16
            bup += fu / 10 ** 16
        assert (up < 1 and bup < 1) if accept else (lo > 1 and blo > 1), 'moment acceptance: ' + side
        rows.append({'side': side, 'surcharge': bad, 'endpoint': str(z), 'accept': accept,
                     'mercator': [str(lo - 1), str(up - 1)], 'base_two': [str(blo - 1), str(bup - 1)]})
    return rows


def load_assemble(discover):
    """Import the chain's acceptance function; discover=True relaxes SPEC pins only."""
    os.environ['GAIN_PR564_SOURCE'] = str(SOURCE)
    os.environ['WITNESS_SPEC'] = str(CHAIN / 'data/SPEC.json')
    if discover:
        os.environ['WITNESS_DISCOVER'] = '1'
    else:
        os.environ.pop('WITNESS_DISCOVER', None)
    sys.path.insert(0, str(CHAIN / 'code'))
    for name in list(sys.modules):
        if name == 'witness' or name.startswith('chain_assemble'):
            del sys.modules[name]
    name = 'chain_assemble_discover' if discover else 'chain_assemble_strict'
    spec = importlib.util.spec_from_file_location(name, CHAIN / 'code' / 'assemble.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def probe(module, owner, invoice, label, mutation):
    """Run assemble() on a mutated receipt pair; record the exact first rejection."""
    import copy
    o, i = copy.deepcopy(owner), copy.deepcopy(invoice)
    mutation(o, i)
    digest = lambda x: hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    oh = digest(o)
    i['owner_audit_sha256'] = oh
    row = {'probe': label, 'rejected': False}
    try:
        module.assemble(o, i, oh, digest(i))
    except Exception as exc:  # noqa: BLE001 - the exact rejection is the evidence
        frames = [f for f in traceback.extract_tb(exc.__traceback__)
                  if any(n in Path(f.filename).name for n in ('assemble', 'witness', 'moment', 'outer'))]
        last = frames[-1] if frames else None
        row.update(rejected=True, exception=type(exc).__name__, message=str(exc)[:600],
                   reject_file=Path(last.filename).name if last else None,
                   reject_line=last.lineno if last else None,
                   reject_source=(last.line or '').strip()[:200] if last else None)
    return row


def locate(source_path, needle):
    """Exact source location of a boundary assertion; drift is a hard failure."""
    lines = Path(source_path).read_text(encoding='utf-8').splitlines()
    hits = [(n + 1, line.strip()) for n, line in enumerate(lines) if needle in line]
    assert hits, 'boundary assertion moved: ' + needle
    return [hits[0][0], hits[0][1]]


def run_replay(tmp):
    """The frozen chain's own stage machinery, unmodified, into a fresh directory."""
    with tarfile.open(ARCHIVE, 'r:gz') as tar:
        for member in tar.getmembers():
            if member.name.startswith('slots/local/'):
                tar.extract(member, tmp, filter='data')
    work = tmp / 't16fresh'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
        env.pop(key, None)
    run = subprocess.run([sys.executable, '-B', str(CHAIN / 'verify_t16.py'), '--main', str(ROOT),
                          '--local', str(tmp / 'slots/local'), '--work', str(work)],
                         env=env, cwd=ROOT, capture_output=True, text=True, timeout=480)
    assert run.returncode == 0, 'chain replay failed:\n' + run.stdout[-3000:] + run.stderr[-3000:]
    assert 'PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY' in run.stdout, 'unexpected replay verdict'
    return work, run.stdout.strip().splitlines()[-1]


def build():
    ev = evidence_bundle()
    engines = load_engines()
    M, B = engines['moment'], engines['base_two_moment']
    pr2595 = json.loads(PR2595.read_text(encoding='utf-8'))
    controls = []

    def ok(name, condition, detail=None):
        assert condition, 'control failed: ' + name + (' :: ' + str(detail) if detail else '')
        controls.append(name)

    # ---- Smallest falsifying instance: PR 2595's k=2 typed-window schedule. ----
    inv = pr2595['k2_pair']['invoices_ADD_NEG_total']
    for name, total in [('pr2464_k2_separate', 608), ('pr2464_k2_joint', 496),
                        ('legal_min_literal_pair', 384), ('legal_typed_pair', 304),
                        ('joint_typed_pair', 304), ('joint_min_literal_pair', 416)]:
        ok('schedule_invoice_' + name, inv[name][0] + inv[name][1] == inv[name][2] == total)
    saving = pr2595['k2_pair']['saving_vs_pr2464_priced_baseline']
    ok('legal_literal_saving_224', saving['legal_min_literal_pair']['primitives'] == 224)
    ok('legal_typed_saving_304', saving['legal_typed_pair']['primitives'] == 304)
    witness = pr2595['k2_pair']['witness_at_block2_entry_x_carrying_and_dirty_rows']
    ok('witness_rows_24_16_0', witness['pr2464_k2_joint'] == [24, 24] and
       witness['joint_typed_pair'] == [16, 24] and witness['legal_typed_pair'] == [0, 0])
    ok('basis_columns_56', pr2595['k2_pair']['basis_columns_checked'] == 56)
    typed_price = pr2595['k2_pair']['price']['legal_typed_pair']
    ok('typed_relabeling_zero_extra', pr2595['obstruction']['extension_priced'].startswith(
        'typed windows (COPY/ERASE source rows relabelled'))
    ok('per_call_delivery', pr2595['k2_pair']['per_call_totals_delivery'].startswith(
        "the state at call a's region end equals call a's complete echo map"))
    # One bounded pivot: the widened-window shared ledger and the adjacent
    # fixed-reader tariff qualification (PR 2626 / Discussion 2610).
    pivot = pr2595['pivot_k5k10']['price']
    ok('pivot_fixed_separate_1616', pivot['pivot_separate5_typed_fixed']['primitives'] == 1616)
    ok('pivot_phase_separate_1456', pivot['pivot_separate5_typed_phase']['primitives'] == 1456)
    ok('pivot_phase_joint_1408', pivot['pivot_joint10_typed_phase']['primitives'] == 1408)
    ok('pr2626_fixed_reader_qualification', 1616 + 56 == 1672 and 1456 - 48 == 1408)
    hosted = pr2595['hosted_ledgers']
    base_hist = {int(r): n for r, n in hosted['baseline_histogram'].items()}
    shared_hist = {int(r): n for r, n in hosted['shared_k2_histogram'].items()}
    ok('published_coverage_identity_5120', M73 * LIVE - sum(r * n for r, n in base_hist.items()) == 5120)
    ok('published_shared_coverage_identity_9728', M73 * LIVE - sum(r * n for r, n in shared_hist.items()) == 9728)
    ok('shared_n8_576', base_hist[8] == 1152 and shared_hist[8] == 576)

    # ---- The frozen chain's own stage machinery, run fresh. ----
    with tempfile.TemporaryDirectory(prefix='kb1c-replay-') as tmp:
        work, verdict = run_replay(Path(tmp))
        replay = json.loads((work / 'REPLAY.json').read_text(encoding='utf-8'))
        assembly = json.loads((work / 'ASSEMBLY.json').read_text(encoding='utf-8'))
        admission = json.loads((work / 'ADMISSION-CONTROLS.json').read_text(encoding='utf-8'))
        supplier = json.loads((work / 'BIT-SUPPLIER-CONTROLS.json').read_text(encoding='utf-8'))
        fresh_owner = json.loads((work / 'global/audit/OWNERS-AND-PROFILE.json').read_text(encoding='utf-8'))
        fresh_invoice = json.loads((work / 'global/audit/PREFIX-AND-INVOICE.json').read_text(encoding='utf-8'))
        owner_bytes = (work / 'global/audit/OWNERS-AND-PROFILE.json').read_bytes()
        invoice_bytes = (work / 'global/audit/PREFIX-AND-INVOICE.json').read_bytes()

        with tarfile.open(ARCHIVE, 'r:gz') as tar:
            arch = {name: tar.extractfile(name).read() for name in ARCHIVE_MEMBERS}
        ok('owner_receipt_byte_exact', hashlib.sha256(owner_bytes).hexdigest() ==
           hashlib.sha256(arch['t16/global/audit/OWNERS-AND-PROFILE.json']).hexdigest())
        ok('invoice_receipt_semantic_exact', json.loads(invoice_bytes) ==
           json.loads(arch['t16/global/audit/PREFIX-AND-INVOICE.json']))
        ok('fresh_vs_archived_admission_controls', all(
            admission[k] == json.loads(arch['t16/ADMISSION-CONTROLS.json'])[k]
            for k in admission if k != 'input_sha256'))
        ok('admission_controls_69', len(admission['rejected_controls']) == 69 and
           admission['discovery_accepted_controls'] == [])
        ok('supplier_controls_12', len(supplier['rejected_controls']) == 12 and
           supplier['derived_deficit'] == 10272)
        ok('replay_verdict', verdict == 'PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY ' + replay['kappa_decimal'])
        ok('replay_controls', replay['controls'] == {'admission': 69, 'bit_supplier': 12,
                                                     'independent_t16': 6, 'controller_mutations': 15})
        ok('binding_inventory', replay['roles'] == 69120 and replay['complete_invocations'] == 144 and
           replay['prefix_bits'] == 397 and replay['charged_prefix_bits'] == 512 and
           replay['physical_row_coefficient'] == 16469 < replay['retained_row_coefficient'] == 20161)
        ok('outer_margins_47', len(assembly['outer']) == 47 and
           all(Q(v) > 0 for v in assembly['outer'].values()))
        ok('kappa_reproduced', replay['kappa'] == '1672188119205421/1000000000000000000')

        # ---- Dirty-column counts at the receipt boundary. ----
        local = fresh_invoice['providers']['gauge44']['local']
        ok('dirty_columns_480_of_704', all(z['all_exact_columns'] == 704 and z['dirty_helper_columns'] == 480 and
                                           z['all_dirty_helper_columns_restored'] is True for z in local.values()))
        ok('hosted_residuals_144x480', fresh_owner['hosted_residuals'] == 144 * 480 == 69120)
        ok('owners_per_call_704', fresh_owner['owners_per_call'] == 2 * 112 + 480)
        ok('physical_stock_identity', fresh_invoice['physical_stock_identity'] ==
           {'data_and_owner_families': 14336, 'local_helpers': 480, 'private_centres': 8, 'coefficient_work': 2})

        # ---- Boundary contracts: exact enforcing locations in the pinned chain. ----
        contracts = {}
        contracts['immutable_windows'] = {'source': 'research/split-centres-global/proofs/PR386-BIT-GEOMETRY.txt',
                                          'sha256': sha(PR386), 'located': locate(PR386, 'COPY/ERASE windows remain sequential and immutable')}
        contracts['wrapper_binding'] = {'source': 'research/gauge44-slots-t16/code/assemble.py',
                                        'located': locate(CHAIN / 'code/assemble.py', "z['pre_wrappers']==z['post_wrappers']==p['entering_helpers']")}
        contracts['deficit_literal'] = {'source': 'research/gauge44-slots-t16/code/assemble.py',
                                        'located': locate(CHAIN / 'code/assemble.py', "owner['deficit']==5120")}
        contracts['profile_pin'] = {'source': 'research/gauge44-slots-t16/code/assemble.py',
                                    'located': locate(CHAIN / 'code/assemble.py', "pin('expected.global_profile'")}
        contracts['rank_mass_pin'] = {'source': 'research/gauge44-slots-t16/code/assemble.py',
                                      'located': locate(CHAIN / 'code/assemble.py', "pin('expected.rank_mass'")}
        contracts['local_profile_pin'] = {'source': 'research/gauge44-slots-t16/code/assemble.py',
                                          'located': locate(CHAIN / 'code/assemble.py', "pin(K+'expected_local.'+name")}
        contracts['wrapper_factor_charge'] = {'source': 'research/gauge44-slots-t16/code/assemble.py',
                                              'located': locate(CHAIN / 'code/assemble.py', "wrapper_elementary_factors_charged']==sum(c['pre_wrappers']+c['post_wrappers'] for c in calls)*144")}
        contracts['typed_window_extension'] = {'source': 'PR 2595 RESULT.json (vendored)',
                                               'located': pr2595['obstruction']['extension_priced']}
        receipt_fields = sorted(fresh_invoice['providers']['gauge44']['local']['forward'].keys())
        ok('no_typed_window_receipt_field', not any('typed' in k or 'relabel' in k for k in receipt_fields))

        # ---- Moment engines (the chain's own) on both priced ledgers. ----
        chain_hist = {int(r): n for r, n in fresh_owner['paid_profile'].items()}
        spec = json.loads((CHAIN / 'data/SPEC.json').read_text(encoding='utf-8'))
        chain_lower = Q(spec['expected']['complex_lower'])
        moments = []
        moments += check_moment(M, B, 'chain_receipt_baseline', chain_hist, M73, LIVE, chain_lower, 5120, False)
        pub_cert = Q(M.certify(base_hist, M73, LIVE, False)['lower'])
        moments += check_moment(M, B, 'published_baseline', base_hist, M73, LIVE, pub_cert, 5120, False)
        # The chain's certify() cannot reach the widened ledger's root: its search
        # bracket ends at Decimal('.003') (engines/moment.py line 78). Record that
        # exact stage and error as the scoped obstruction, then drive the chain's
        # own moment() oracle past the ceiling (same acceptance test).
        scoped_obstructions = []
        try:
            M.certify({**chain_hist, 8: 576}, M73, LIVE, False)
            raise AssertionError('expected certify ceiling obstruction did not occur')
        except AssertionError as exc:
            scoped_obstructions.append({
                'stage': 'moment certification (engines/moment.py certify, search bracket)',
                'error': type(exc).__name__ + ': ' + str(exc)[:300],
                'location': 'engines/moment.py line 78 (hi=Decimal(\'.003\')) -> assert at line 86',
                'object': 'chain shared widened-window ledger (n_8 = 576, D = 9728)',
                'meaning': "the chain's certified moment engine cannot certify any endpoint above 0.003; "
                           'the widened ledger root is about 0.0031852 (PR 2595 enclosures). The chain\'s '
                           'moment() acceptance oracle itself is not implicated (checked below).'})
        shared_endpoint_chain, shared_reject_chain = certify_bisect(M, {**chain_hist, 8: 576}, M73, LIVE, False)
        moments += check_moment(M, B, 'chain_shared_widened_window', {**chain_hist, 8: 576}, M73, LIVE,
                                shared_endpoint_chain, 9728, False)
        shared_endpoint_pub, shared_reject_pub = certify_bisect(M, shared_hist, M73, LIVE, False)
        moments += check_moment(M, B, 'published_shared_widened_window', shared_hist, M73, LIVE,
                                shared_endpoint_pub, 9728, False)
        screen_lo = Q(hosted['baseline']['D_over_E_lo'])
        ok('D_over_E_screen_not_acceptance', M.moment(base_hist, M73, LIVE, screen_lo, False)[0] > 1)

        # ---- Invoice/assembly boundary probes (the chain's acceptance function). ----
        def widen_owner_only(o, i):
            o['paid_profile']['8'] = 576
            o['rank_mass'] -= 4608
            o['deficit'] = 9728

        def widen_consistent(o, i):
            # Self-consistent widened-window declaration: re-derive every invoice
            # envelope field exactly as code/assemble.py does (same formulas).
            # The frozen chain files are not modified.
            widen_owner_only(o, i)
            for p in i['providers'].values():
                p['paid_profile']['8'] //= 2
                p['children'] = sum(p['paid_profile'].values())
                p['local_adapters'] = 16 * (max(z['macros'] for z in p['local'].values()) + p['children']
                                            + 2 * 112 + i['helpers'] + 8) + 64 * 73
                p['local_primitive_bound'] = max(z['real_component_primitives'] for z in p['local'].values()) \
                    + p['local_adapters'] * p['compiler']
            i['local_adapters'] = max(p['local_adapters'] for p in i['providers'].values())
            i['local_primitive_bound'] = max(p['local_primitive_bound'] for p in i['providers'].values())
            summed = {}
            for c in i['selected_calls']:
                prof = i['providers'][c['provider_id']]['paid_profile']
                for r, n in prof.items():
                    summed[r] = summed.get(r, 0) + n
            i['selected_local_paid_profile'] = {str(r): n for r, n in sorted(summed.items())}
            r = i['helpers']
            bridges, shifts = 2 * 112 * 144, 4 * 112 * 16
            moves = 2 * shifts
            parent_live, parent_physical, parent_idle = 23408, 23922, 32256
            parent_banks = (parent_live - 2 * 112 * 4 * 16) // 9
            nonlocal_items = (4 * 112 * 16 * 9 + 2 * 112 * 16 * 9 + 2 * 144 * r + parent_idle + 9 * parent_banks
                              + bridges + shifts + moves + parent_live + parent_physical
                              + i['wrapper_elementary_factors_charged'])
            outside = 8 * nonlocal_items + 64 * 73
            pervertex = (i['selected_real_component_primitives'] + bridges + shifts + moves + parent_live
                         + (144 * i['local_adapters'] + outside) * i['compiler'] + 64 * parent_physical)
            rebased = pervertex + 65 * (i['physical'] - parent_physical) + (i['live'] - parent_live)
            i['unhosted_pervertex'] = pervertex
            i['hosted_rebased_pervertex'] = rebased
            used = max(pervertex, rebased)
            prior = i['retained_prior_overcharge']
            if prior is not None:
                prior['added_complete_new_pervertex'] = pervertex
                used = max(used, prior['previous_pervertex_allowance'] + pervertex)
            i['conservative_pervertex_used'] = used
            group = 2 ** (36 * 36)
            for j in range(1, 37):
                group *= 2 ** (2 * j) - 1
            stock = group * i['physical']
            streamed_mass = group * o['rank_mass']
            logical = group * used + 64
            router = i['compiler'] * (logical + 1) * (stock + 1) ** 2
            literal = 2 * 2 ** 30000 * stock ** 2 + 8 * streamed_mass + 4 * stock + 4 + 32 * 73
            total_mass = streamed_mass + 2 ** 100000
            f = i['finite']
            f['physical_stock_bits'] = stock.bit_length()
            f['router_bits'] = router.bit_length()
            f['literal_bits'] = literal.bit_length()
            f['physical_row_coefficient'] = 2 * stock.bit_length() + 9909 + 252 + 1024
            f['required_C0_bits'] = (32 * 73 * total_mass * total_mass).bit_length()
            i['strict_checks'] = {'local_primitive_bound': i['local_primitive_bound'] < 2 ** 48,
                                  'logical': logical < 2 ** 6050, 'router': router < 2 ** 30000,
                                  'literal': literal < 2 ** 100000, 'mass': total_mass < 2 ** 100001,
                                  'precision': 32 * 73 * total_mass * total_mass < 2 ** 210000,
                                  'tape': 2 * total_mass + 18 < 2 ** 210000,
                                  'row': f['physical_row_coefficient'] < 20161,
                                  'halving': 73 * 73 > 2 * 48 * 48}

        def scalar_rewindow(o, i):
            z = i['providers']['gauge44']['local']['forward']
            z['real_component_primitives'] -= 1

        strict = load_assemble(discover=False)
        control_kappa = strict.assemble(fresh_owner, fresh_invoice, hashlib.sha256(owner_bytes).hexdigest(),
                                        hashlib.sha256(invoice_bytes).hexdigest())
        ok('assemble_control_passes', control_kappa['kappa'] == replay['kappa'])
        probe_widen_strict = probe(strict, fresh_owner, fresh_invoice,
                                   'widened_window_ledger_strict_owner_declaration', widen_owner_only)
        ok('widened_rejected_at_rank_mass_pin', probe_widen_strict['rejected'] and
           'expected.rank_mass' in probe_widen_strict['message'])
        probe_widen_full_strict = probe(strict, fresh_owner, fresh_invoice,
                                        'widened_window_consistent_declaration_strict', widen_consistent)
        ok('widened_consistent_rejected_at_profile_pin', probe_widen_full_strict['rejected'] and
           'SPEC MISMATCH' in probe_widen_full_strict['message'])
        probe_scalar = probe(strict, fresh_owner, fresh_invoice, 'scalar_rewindowed_local_profile',
                             scalar_rewindow)
        ok('scalar_rewindow_rejected_at_contract_pin', probe_scalar['rejected'] and
           'complete_contract' in probe_scalar['message'], str(probe_scalar))
        discover = load_assemble(discover=True)
        probe_widen_owner_discover = probe(discover, fresh_owner, fresh_invoice,
                                           'widened_window_owner_declaration_pins_relaxed', widen_owner_only)
        ok('owner_only_declaration_rejected_at_idle_consistency', probe_widen_owner_discover['rejected'] and
           'idle' in probe_widen_owner_discover['reject_source'], str(probe_widen_owner_discover))
        # With every SPEC pin relaxed the consistent declaration dies inside the
        # engine's certify() bracket (the scoped obstruction above). To reach the
        # next boundary, one probe replaces certify() with its oracle-equivalent
        # bisect (the frozen files on disk are untouched).
        probe_widen_discover = probe(discover, fresh_owner, fresh_invoice,
                                     'widened_window_consistent_declaration_pins_relaxed', widen_consistent)
        ok('widened_consistent_discover_blocked_at_certify_bracket',
           probe_widen_discover['rejected'] and 'moment.py' in probe_widen_discover['reject_file'],
           str(probe_widen_discover))
        discover_patched = load_assemble(discover=True)
        discover_patched.M.certify = (
            lambda h, m, w, bad=False: {'lower': str(certify_bisect(discover_patched.M, h, m, w, bad)[0])})
        probe_widen_patched = probe(discover_patched, fresh_owner, fresh_invoice,
                                    'widened_window_consistent_declaration_certify_bypassed', widen_consistent)
        ok('widened_hard_blocker_is_deficit_literal', probe_widen_patched['rejected'] and
           "owner['deficit']==5120" in probe_widen_patched['reject_source'], str(probe_widen_patched))
        scoped_obstructions.append({
            'stage': 'invoice/assembly boundary (code/assemble.py assemble, owner deficit literal)',
            'error': probe_widen_patched['exception'] + ': ' + probe_widen_patched['reject_source'],
            'location': 'code/assemble.py line ' + str(probe_widen_patched['reject_line']),
            'object': 'the widened-window shared ledger declared consistently (owner profile, rank mass, '
                      'deficit and per-call rank-8 children halved 8 -> 4), with the certify bracket '
                      'bypassed by its oracle-equivalent bisect',
            'meaning': 'with every SPEC pin relaxed the acceptance function still hard-codes the selected '
                       'deficit 5120; admitting the shared ledger needs this literal replaced by the '
                       'coverage identity m*W - sum(r*n) = deficit with deficit 9728.'})

    named_decisions = [
        {'id': 'MD-1', 'decision': 'widened-window/common-sink contract change (vs PR 2500)',
         'content': 'Admit one widened COPY/ERASE window with per-pair totals delivery (common sink) so the '
                    'shared ledger n_8 = 576 / D = 9728 can be declared. Declared as an owner-ledger change '
                    'only, the chain rejects it at the per-call profile/idle consistency (the rank-8 idle '
                    'remainder goes negative: 576 - 1152); declared consistently per call (rank-8 children '
                    '8 -> 4), the chain rejects it at the SPEC pins expected.rank_mass / expected.profile '
                    "and, with all pins relaxed, at assemble.py's literal owner deficit assertion. The "
                    'chain moment oracle accepts the shared ledger at its own grid endpoint, but the '
                    "chain's certify() search cannot reach it (bracket ceiling 0.003, engines/moment.py "
                    'line 78; scoped obstruction recorded). Both are part of this decision.',
         'blocked_by': 'the pinned PR386 sentence (windows sequential and immutable, per-call totals) and '
                       "assemble.py's deficit literal; PR 2500: the typed contract alone does not imply "
                       'fewer recursive children.'},
        {'id': 'MD-2', 'decision': 'supplier admission fields for typed windows',
         'content': 'Add declared fields for typed (frame-relabelled) window source rows, 8-row per-call '
                    'windows and per-call totals delivery to the provider local receipt schema, plus their '
                    'negative controls beside false_dirty_restoration in code/assembly_controls.py. Today no '
                    'receipt field names a typed relabeling and any scalar re-window is rejected at the '
                    'providers.<pid>.complete_contract pin (then the expected_local pins); a SPEC '
                    'regeneration via the chain discovery path is the admission route.',
         'blocked_by': 'the literal-window model (independent-t16: PASS_INDEPENDENT_T16_LITERAL_WINDOWS_'
                       'CHARTS_PREFIX_ROW) and the 13-field provider local receipt schema.'},
    ]
    return {'result': 'PASS_Z4_TYPED_WINDOW_ADMISSION_KB1C', 'schema_version': 1,
            'base_commit': '0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2',
            'inputs': ev,
            'predecessors': {'pr2464': PR2464_HEAD, 'pr2595': PR2595_HEAD,
                             'pr2595_RESULT_sha256': PR2595_SHA256},
            'schedule_k2': {'invoices_ADD_NEG_total': inv,
                            'saving_vs_priced_baseline_primitives': {'literal': 224, 'typed': 304},
                            'witness_rows_block2_entry': witness,
                            'basis_columns': 56, 'priced_typed_pair': typed_price},
            'chain_replay': {'status': replay['status'], 'kappa': replay['kappa'],
                             'kappa_decimal': replay['kappa_decimal'], 'controls': replay['controls'],
                             'roles': replay['roles'], 'complete_invocations': replay['complete_invocations'],
                             'prefix_bits': replay['prefix_bits'], 'charged_prefix_bits': replay['charged_prefix_bits'],
                             'physical_row_coefficient': replay['physical_row_coefficient'],
                             'retained_row_coefficient': replay['retained_row_coefficient'],
                             'outer_strict_margins': 47, 'owner_receipt_sha256': hashlib.sha256(owner_bytes).hexdigest(),
                             'invoice_receipt_semantic_equal_to_archive': True,
                             'invoice_receipt_byte_equal_to_archive': False,
                             'byte_diff_reason': 'JSON key order of one receipt and absolute input paths recorded '
                                                 'by independent-t16; all content semantically equal'},
            'dirty_columns': {'owners_per_call': 704, 'all_exact_columns': 704, 'dirty_helper_columns': 480,
                              'all_dirty_helper_columns_restored': True, 'hosted_residuals': 69120,
                              'schedule_basis_columns': 56,
                              'schedule_block2_witness_rows': {'fused': [24, 24], 'deferral': [16, 24], 'legal': [0, 0]}},
            'priced_ledger': {'width_m': 73, 'live_stock_W': 14336,
                              'chain_receipt_histogram': {str(r): n for r, n in sorted(chain_hist.items())},
                              'published_baseline_histogram': hosted['baseline_histogram'],
                              'baseline': {'D': 5120, 'D_over_E_lo': hosted['baseline']['D_over_E_lo'],
                                           'D_over_E_hi': hosted['baseline']['D_over_E_hi']},
                              'shared_widened_window': {'D': 9728, 'n8': 576,
                                                        'D_over_E_lo': hosted['shared_widened_window']['D_over_E_lo'],
                                                        'D_over_E_hi': hosted['shared_widened_window']['D_over_E_hi'],
                                                        'chain_oracle_endpoint': str(shared_endpoint_chain),
                                                        'chain_oracle_rejects_at': str(shared_reject_chain),
                                                        'published_oracle_endpoint': str(shared_endpoint_pub),
                                                        'published_oracle_rejects_at': str(shared_reject_pub)},
                              'published_baseline_certified_endpoint': str(pub_cert),
                              'chain_recorded_endpoint': str(chain_lower),
                              'moments': moments},
            'boundary_contracts': contracts,
            'probes': {'assemble_control': 'pass',
                       'widened_window_owner_declaration_strict': probe_widen_strict,
                       'widened_window_consistent_declaration_strict': probe_widen_full_strict,
                       'widened_window_owner_declaration_pins_relaxed': probe_widen_owner_discover,
                       'widened_window_consistent_declaration_pins_relaxed': probe_widen_discover,
                       'widened_window_consistent_declaration_certify_bypassed': probe_widen_patched,
                       'scalar_rewindowed_local_profile': probe_scalar},
            'scoped_obstructions': scoped_obstructions,
            'provider_local_receipt_fields': receipt_fields,
            'named_maintainer_decisions': named_decisions,
            'control_count': len(controls), 'controls': controls,
            'scope': 'Admission-stage evidence only. The typed echo is not placed on the selected 144-call '
                     'schedule (research/selected-centre-adjacent-pair-seed01fcb1 found no adjacent pair with '
                     'a shared owner); the run is the pinned PR1087 chain (PR1042 composition) against the '
                     "typed-window declarations. No frozen pin, selected record or frontier change; no new "
                     'kappa and no supplier admission.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    result = build()
    out = PKG / 'RESULT.json'
    if a.write:
        out.write_text(json.dumps(result, indent=1, sort_keys=True) + '\n', encoding='utf-8')
        print('WROTE', out)
    else:
        assert json.loads(out.read_text(encoding='utf-8')) == result, 'RESULT.json drift; rerun with --write'
        print('RESULT.json matches recomputation')
    print(result['result'], 'controls=%d' % result['control_count'],
          'admission=69 supplier=12', 'kappa=' + result['chain_replay']['kappa_decimal'],
          'D=5120/9728', 'no_new_kappa')


if __name__ == '__main__':
    main()
