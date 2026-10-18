#!/usr/bin/env python3
"""Mutation coverage of the selected finite invoice (frozen PR1087 invoice_allcold.run()).

Adversarial audit of one named current condition of the selected #1094 chain.
Object: code/invoice_allcold.py in research/complex-t16-rare-pattern-exchanges/
upstream1087.tar.gz (SHA-256 pinned below), run on the archived selected fixture
research/community-frontier1094-audit/selected-replay.tar.gz. The invoice stage
carries the finite inequalities (prefix required < 512 payload, row < 20161,
halving, mass, router, literal, precision, tape, local-primitive) and has no
mutation-control block of its own. This harness applies one-field semantic
mutants of its inputs, records the first rejecting assertion or acceptance, and
probes whether the downstream receipt admission (assemble(), the layer the 69
admission controls exercise) rejects the mutants the invoice accepts.

Scope: the invoice stage's acceptance boundary only. No kappa, certificate,
supplier or frontier change; not a cold replay. Open question 3 of
research/t16-audit-mutant-coverage/README.md (PR1959, Josie Elliston).

Aaron Wang, with help from opencode. Apache-2.0. Stdlib only; CPython 3.10+.
"""
import argparse
import contextlib
import gzip
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
ARCHIVE = ROOT / 'research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz'
FIXTURE = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
RETAINED = ROOT / ('research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/'
                   'vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json')
MULTICOLD = ROOT / 'research/complex-k492-owner-repair/vendor/multicold'
EXPECT = PKG / 'EXPECTED.json'

PINS = {
    'upstream1087.tar.gz': 'd4acf04daef85d4514f80ec5fcd2492d0c60e5d6c49fa71b3e6523f8db2dea86',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_bytes())


def read_gz_json(path):
    return json.loads(gzip.decompress(Path(path).read_bytes()))


def dumps(value):
    return json.dumps(value, indent=2).encode()


def contenthash_bytes(raw):
    return hashlib.sha256(gzip.decompress(raw)).hexdigest()


# --------------------------------------------------------------------------
# Environment and module loading (mirrors verify_t16.py's stage environment).


def prepare(work):
    """Extract the pinned PR1087 source and the archived selected fixture."""
    work = work.resolve()
    src = work / 'src1087'
    src.mkdir()
    with tarfile.open(ARCHIVE) as t:
        for m in t.getmembers():
            assert m.isfile() and (src / m.name).resolve().is_relative_to(src), 'unsafe archive member'
        t.extractall(src, filter='data')
    assert sha(ARCHIVE) == PINS['upstream1087.tar.gz'], 'PR1087 archive pin'
    manifest = read_json(src / 'MANIFEST.json')
    for name, digest in manifest.items():
        if name.startswith('code/') or name.startswith('data/'):
            assert sha(src / name) == digest, 'archive member pin: ' + name
    # The pipeline copies the pinned package data over the source data/ (verify.py).
    package = ROOT / 'research/complex-t16-rare-pattern-exchanges'
    for name in ('OWNERS.json.gz', 'PLAN.json', 'SPEC.json'):
        shutil.copyfile(package / 'data' / name, src / 'data' / name)

    fixture = work / 'fixture'
    fixture.mkdir()
    with tarfile.open(FIXTURE) as t:
        for m in t.getmembers():
            assert m.isfile() and (fixture / m.name).resolve().is_relative_to(fixture), 'unsafe fixture member'
        t.extractall(fixture, filter='data')
    global_dir = fixture / 'candidate/strict/global'
    return src, global_dir


def load_invoice(src):
    os.environ['WITNESS_SPEC'] = str(src / 'data/SPEC.json')
    os.environ['GAIN_PR564_SOURCE'] = str(MULTICOLD)
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        os.environ.pop(key, None)
    sys.path.insert(0, str(src / 'code'))
    assert __debug__, 'Assertions must remain enabled'
    mod = importlib.import_module('invoice_allcold')
    return mod


# --------------------------------------------------------------------------
# Input tree: pristine bytes, mutation, restoration. Inputs are mutated in
# place and restored from an in-memory pristine copy after every run.


INPUT_FILES = (
    'hosted/GLOBAL-TEMPLATE.json.gz',
    'hosted/HOSTED.json',
    'audit/OWNERS-AND-PROFILE.json',
    'audit/ASYNC-AUDIT.json',
    'base/split-centres/GLOBAL-TEMPLATE.json.gz',
    'base/providers/gauge44/LOCAL-CHECKS.json',
    'base/providers/gauge44/RESIDUAL-ADAPTERS.json',
    'base/providers/gauge44/INDEPENDENT-LOCAL-REPLAY.json',
    'base/providers/gauge44/CLIFFORD-REVIEW.json',
)


class InputTree:
    def __init__(self, base):
        self.base = base
        self.pristine = {name: (base / name).read_bytes() for name in INPUT_FILES}

    def restore(self):
        for name, raw in self.pristine.items():
            (self.base / name).write_bytes(raw)

    def load(self, name):
        raw = (self.base / name).read_bytes()
        if name.endswith('.gz'):
            return json.loads(gzip.decompress(raw))
        return json.loads(raw)

    def store(self, name, value):
        raw = dumps(value)
        if name.endswith('.gz'):
            raw = gzip.compress(raw)
        (self.base / name).write_bytes(raw)
        return raw


def sync_template_hashes(tree, template_raw, targets):
    """Class B: make the stored template hashes agree with mutated content."""
    digest = contenthash_bytes(template_raw)
    for name, key in targets:
        value = tree.load(name)
        value[key] = digest
        tree.store(name, value)
    return digest


# --------------------------------------------------------------------------
# Mutant catalogue. Each entry: name, class, function(tree) -> applied.


def mutants():
    out = []

    def add(name, cls, fn):
        out.append((name, cls, fn))

    # Class A: raw template content mutation; stored hashes untouched.
    def a1(tree):
        t = tree.load('hosted/GLOBAL-TEMPLATE.json.gz')
        t['live'] += 1
        tree.store('hosted/GLOBAL-TEMPLATE.json.gz', t)
    add('A1_raw_template_live', 'A', a1)

    def a2(tree):
        t = tree.load('hosted/GLOBAL-TEMPLATE.json.gz')
        t['bank_padding']['families'] = ['x']
        tree.store('hosted/GLOBAL-TEMPLATE.json.gz', t)
    add('A2_raw_template_bank_padding', 'A', a2)

    # Class B: template content mutation with the three stored hashes resynced.
    hash_targets = (('audit/ASYNC-AUDIT.json', 'complex_template_sha256'),
                    ('audit/OWNERS-AND-PROFILE.json', 'template_sha256'),
                    ('hosted/HOSTED.json', 'template_sha256'))

    def class_b(name, edit):
        def fn(tree):
            t = tree.load('hosted/GLOBAL-TEMPLATE.json.gz')
            edit(t)
            raw = tree.store('hosted/GLOBAL-TEMPLATE.json.gz', t)
            sync_template_hashes(tree, raw, hash_targets)
        add(name, 'B', fn)

    class_b('B1_template_live_plus1', lambda t: t.__setitem__('live', t['live'] + 1))

    def b2(t):
        t['live'] += 1
        t['physical'] += 1
    class_b('B2_template_live_physical_plus1', b2)

    class_b('B3_template_bank_padding_family',
            lambda t: t['bank_padding']['families'].append('x'))

    def b4(t):
        t['calls'].pop()
    class_b('B4_template_drop_call', b4)

    def b5(t):
        for e in t['execution_schedule']:
            if e['kind'] == 'local_cover_sweep':
                e['provider_id'] = '__wrong__'
                break
    class_b('B5_template_wrong_sweep_provider', b5)

    def b6(t):
        first = t['calls'][0]['owners'][0]
        if isinstance(first, list):
            first[0] = (first[0] + 1) % 20000
        else:
            t['calls'][0]['owners'][0] = (first + 1) % 20000
    class_b('B6_template_call_owner_changed', b6)

    def b7(t):
        t['calls'][0]['orientation'] = 'backward' if t['calls'][0]['orientation'] == 'forward' else 'forward'
    class_b('B7_template_call_orientation_changed', b7)

    def b8(t):
        t['recipe'][0] = dict(t['recipe'][0], kind='__wrong__')
    class_b('B8_template_recipe_changed', b8)

    def b9(t):
        t['calls'][0]['local_program_sha256'] = '0' * 64
    class_b('B9_template_call_program_hash', b9)

    def b10(t):
        pid = sorted(t['local_providers'])[0]
        t['local_providers'][pid]['local_program_checks'] = {}
    class_b('B10_template_registry_checks_cleared', b10)

    def b11(t):
        pid = sorted(t['local_providers'])[0]
        t['local_providers'][pid]['v'] = 113
    class_b('B11_template_registry_v_changed', b11)

    # Class C: audit receipt mutations (their file hashes are recorded, not pinned).
    def c1(tree):
        o = tree.load('audit/OWNERS-AND-PROFILE.json')
        o['deficit'] = 5119
        tree.store('audit/OWNERS-AND-PROFILE.json', o)
    add('C1_owner_deficit_5119', 'C', c1)

    def c2(tree):
        o = tree.load('audit/OWNERS-AND-PROFILE.json')
        o['rank_mass'] += 73
        tree.store('audit/OWNERS-AND-PROFILE.json', o)
    add('C2_owner_rank_mass_off_profile', 'C', c2)

    def c3(tree):
        # Same rank mass, but max child rank 52 must break the halving guard.
        o = tree.load('audit/OWNERS-AND-PROFILE.json')
        p = dict(o['paid_profile'])
        donor = next((r for r in (1, 2, 4, 13, 26) if int(p.get(str(r), 0)) >= 52 // r), None)
        assert donor is not None, 'C3 needs a donor rank dividing 52'
        p[str(donor)] = int(p[str(donor)]) - 52 // donor
        p['52'] = int(p.get('52', 0)) + 1
        o['paid_profile'] = p
        tree.store('audit/OWNERS-AND-PROFILE.json', o)
    add('C3_owner_profile_halving_guard', 'C', c3)

    def c3b(tree):
        # Same rank mass and same max child rank: run() alone must accept this
        # profile change; the downstream probe records what assemble() does.
        o = tree.load('audit/OWNERS-AND-PROFILE.json')
        p = dict(o['paid_profile'])
        assert int(p.get('2', 0)) >= 1
        p['2'] = int(p['2']) - 1
        p['1'] = int(p.get('1', 0)) + 2
        o['paid_profile'] = p
        tree.store('audit/OWNERS-AND-PROFILE.json', o)
    add('C3b_owner_profile_same_mass_same_max', 'C', c3b)

    def c4(tree):
        o = tree.load('audit/OWNERS-AND-PROFILE.json')
        o['explicit_idle_remainder_children'] += 1
        tree.store('audit/OWNERS-AND-PROFILE.json', o)
    add('C4_owner_explicit_idle_remainders', 'C', c4)

    def c5(tree):
        o = tree.load('audit/OWNERS-AND-PROFILE.json')
        o['template_sha256'] = '0' * 64
        tree.store('audit/OWNERS-AND-PROFILE.json', o)
    add('C5_owner_template_sha_raw', 'C', c5)

    def c6(tree):
        o = tree.load('audit/OWNERS-AND-PROFILE.json')
        o['actual_73column_sigmas'] += 1
        tree.store('audit/OWNERS-AND-PROFILE.json', o)
    add('C6_owner_actual_73column_sigmas', 'C', c6)

    def c7(tree):
        o = tree.load('audit/OWNERS-AND-PROFILE.json')
        key = sorted(o['source_artifacts'])[0]
        o['source_artifacts'][key] = '0' * 64
        tree.store('audit/OWNERS-AND-PROFILE.json', o)
    add('C7_owner_source_artifact_hash', 'C', c7)

    def c8(tree):
        c = tree.load('audit/ASYNC-AUDIT.json')
        c['complete_invocations'] = 143
        tree.store('audit/ASYNC-AUDIT.json', c)
    add('C8_control_complete_invocations', 'C', c8)

    def c9(tree):
        c = tree.load('audit/ASYNC-AUDIT.json')
        c['one_owner_per_complete_invocation'] = False
        tree.store('audit/ASYNC-AUDIT.json', c)
    add('C9_control_one_owner_flag', 'C', c9)

    def c10(tree):
        c = tree.load('audit/ASYNC-AUDIT.json')
        c['mutations_rejected'] = []
        c['mutation_controls_run'] = False
        tree.store('audit/ASYNC-AUDIT.json', c)
    add('C10_control_mutation_claims_cleared', 'C', c10)

    def c11(tree):
        c = tree.load('audit/ASYNC-AUDIT.json')
        c['complex_template_sha256'] = '0' * 64
        tree.store('audit/ASYNC-AUDIT.json', c)
    add('C11_control_template_sha_raw', 'C', c11)

    def c12(tree):
        s = tree.load('hosted/HOSTED.json')
        s['template_sha256'] = '0' * 64
        tree.store('hosted/HOSTED.json', s)
    add('C12_summary_template_sha_raw', 'C', c12)

    def c13(tree):
        s = tree.load('hosted/HOSTED.json')
        key = sorted(s['source_artifacts'])[0]
        s['source_artifacts'][key] = '0' * 64
        tree.store('hosted/HOSTED.json', s)
    add('C13_summary_source_artifact_hash', 'C', c13)

    # Class D: provider inputs.
    def d1(tree):
        c = tree.load('base/providers/gauge44/LOCAL-CHECKS.json')
        c['forward']['paid_profile']['1'] = str(int(c['forward']['paid_profile']['1']) + 1)
        tree.store('base/providers/gauge44/LOCAL-CHECKS.json', c)
    add('D1_provider_checks_paid_profile', 'D', d1)

    def d2(tree):
        r = tree.load('base/providers/gauge44/RESIDUAL-ADAPTERS.json')
        recipe = next(iter(r['recipes'].values()))
        recipe['rank'] = 8
        tree.store('base/providers/gauge44/RESIDUAL-ADAPTERS.json', r)
    add('D2_provider_residual_adapter_rank', 'D', d2)

    def d3(tree):
        r = tree.load('base/providers/gauge44/INDEPENDENT-LOCAL-REPLAY.json')
        r['status'] = 'FAIL'
        tree.store('base/providers/gauge44/INDEPENDENT-LOCAL-REPLAY.json', r)
    add('D3_provider_replay_status', 'D', d3)

    def d4(tree):
        r = tree.load('base/providers/gauge44/CLIFFORD-REVIEW.json')
        r['seconds'] = 0
        tree.store('base/providers/gauge44/CLIFFORD-REVIEW.json', r)
    add('D4_provider_phase_review_semantics', 'D', d4)

    # Class F: fully hash-consistent multi-file stock inflation. Every run()
    # arithmetic identity is preserved (deficit literal included); only the
    # finite inequality guards see the inflated stock. With payload 512 the
    # guard reads row = 2*stock_bits + 11185 < 20161, i.e. stock_bits < 4488.
    # F1 lands exactly on the failing side (stock bit length 4488, row == 20161),
    # F2 one bit below it: the smallest falsifying pair for the row obligation.
    def class_f(name, target_stock_bits):
        def fn(tree):
            invoice = read_json(tree.base / 'audit/PREFIX-AND-INVOICE.json')
            helpers, centres = invoice['helpers'], invoice['centres']
            parent = read_gz_json(tree.base / 'base/split-centres/GLOBAL-TEMPLATE.json.gz')
            parent_r = read_gz_json(tree.base / 'base/split-centres/CANONICAL-WORD.json.gz')['R']
            half = 73 // 2
            group = 2 ** (half * half)
            for i in range(1, half + 1):
                group *= 2 ** (2 * i) - 1
            n = None
            for cand_bits in range(target_stock_bits - group.bit_length() - 2,
                                   target_stock_bits - group.bit_length() + 8):
                cand = 2 ** cand_bits
                cand += (63 - cand % 73) % 73  # make (cand + 5120) divisible by m = 73
                physical = (cand + 5120) // 73 + helpers + centres + 2
                if (group * physical).bit_length() == target_stock_bits:
                    n = cand
                    break
            assert n is not None, 'no exact stock-width candidate'
            live = (n + 5120) // 73
            physical = live + helpers + centres + 2
            o = tree.load('audit/OWNERS-AND-PROFILE.json')
            o['live'], o['physical'] = live, physical
            o['rank_mass'] = n
            o['paid_profile'] = {'1': n}
            tree.store('audit/OWNERS-AND-PROFILE.json', o)
            t = tree.load('hosted/GLOBAL-TEMPLATE.json.gz')
            t['live'], t['physical'] = live, physical
            raw = tree.store('hosted/GLOBAL-TEMPLATE.json.gz', t)
            sync_template_hashes(tree, raw, hash_targets)
            parent_live = live + max(0, helpers - parent_r)
            parent_live += (8 - parent_live % 9) % 9  # (parent_live - data_stock) divisible by 9
            parent['live'] = parent_live
            parent['physical'] = parent_live + parent_r + centres + 2
            tree.store('base/split-centres/GLOBAL-TEMPLATE.json.gz', parent)
        add(name, 'F', fn)

    class_f('F1_consistent_stock_inflation_row_threshold', 4488)
    class_f('F2_consistent_stock_inflation_row_subthreshold', 4487)

    return out


# --------------------------------------------------------------------------
# Retained-invoice mutants run on a scratch copy, never on the pinned file.


def retained_mutants():
    def edit(name, fn):
        return (name, fn)

    def e1(v):
        v['charged_prefix_bits'] = 511
    def e2(v):
        v['conservative_pervertex_used'] = 0
    def e3(v):
        v['conservative_pervertex_used'] = 2 ** 6050
    def e4(v):
        v['compiler'] = 1
    return [edit('E1_retained_charged_prefix_bits', e1),
            edit('E2_retained_previous_bound_zero', e2),
            edit('E3_retained_previous_bound_inflated', e3),
            edit('E4_retained_compiler', e4)]


# --------------------------------------------------------------------------
# Execution.


def run_invoice(mod, base, out_dir, retained):
    out_dir.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        receipt = mod.run(base / 'base', base / 'hosted', base / 'audit', out_dir, retained)
    return receipt, buf.getvalue()


def probe_assemble(owner_path, invoice_path):
    """Downstream admission layer: does assemble() reject the emitted pair?"""
    os.environ['GAIN_PR564_SOURCE'] = str(MULTICOLD)
    assemble_mod = importlib.import_module('assemble')
    owner = read_json(owner_path)
    invoice = read_json(invoice_path)
    try:
        assemble_mod.assemble(owner, invoice, sha(owner_path), sha(invoice_path))
    except (AssertionError, KeyError, ValueError) as exc:
        tb = traceback.extract_tb(exc.__traceback__)
        frame = next((f for f in reversed(tb) if f.filename.endswith('assemble.py')), None)
        where = 'line %s: %s' % (frame.lineno, (frame.line or '').strip()) if frame else 'unknown'
        return 'assemble_rejected: %s | %s' % (where, str(exc)[:70] or '<assert>')
    return 'assemble_accepted'


def failure(mod, base, out_dir, retained):
    try:
        _, summary = run_invoice(mod, base, out_dir, retained)
    except AssertionError as exc:
        tb = traceback.extract_tb(exc.__traceback__)
        frame = next((f for f in reversed(tb) if f.filename.endswith('invoice_allcold.py')), None)
        where = 'line %s: %s' % (frame.lineno, (frame.line or '').strip()) if frame else 'unknown'
        return 'rejected', '%s | %s' % (where, str(exc)[:70] or '<assert>'), None
    except Exception as exc:  # incidental type errors still reject the input
        return 'rejected', 'exception %s: %s' % (type(exc).__name__, str(exc)[:60]), None
    return 'accepted', '', json.loads(summary)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true', help='regenerate EXPECTED.json')
    ap.add_argument('--expect', type=Path, default=EXPECT, help='receipt to compare against')
    ap.add_argument('--json', type=Path, help='also dump the full result here')
    a = ap.parse_args()
    assert __debug__, 'Assertions must remain enabled'

    with tempfile.TemporaryDirectory(prefix='invoice-mutant-coverage.') as tmp:
        work = Path(tmp)
        src, global_dir = prepare(work)
        tree = InputTree(global_dir)
        mod = load_invoice(src)

        # Positive control: reproduce the archived selected invoice exactly.
        out = work / 'out-positive'
        run_invoice(mod, global_dir, out, RETAINED)
        archived_invoice = read_json(global_dir / 'audit/PREFIX-AND-INVOICE.json')
        archived_prefix = read_json(global_dir / 'audit/GLOBAL-PREFIX.json')
        assert read_json(out / 'PREFIX-AND-INVOICE.json') == archived_invoice, \
            'positive control: PREFIX-AND-INVOICE differs'
        assert read_json(out / 'GLOBAL-PREFIX.json') == archived_prefix, 'positive control: GLOBAL-PREFIX differs'
        positive = dict(status='PASS_POSITIVE_CONTROL_REPRODUCES_ARCHIVED_INVOICE',
                        invoice_sha256=sha(global_dir / 'audit/PREFIX-AND-INVOICE.json'))

        records = []
        for name, cls, edit in mutants():
            tree.restore()
            edit(tree)
            verdict, detail, summary = failure(mod, global_dir, work / ('out-' + name), RETAINED)
            record = dict(name=name, mutant_class=cls, verdict=verdict, detail=detail,
                          summary=summary, downstream=None)
            if verdict == 'accepted':
                record['downstream'] = probe_assemble(global_dir / 'audit/OWNERS-AND-PROFILE.json',
                                                      work / ('out-' + name) / 'PREFIX-AND-INVOICE.json')
            records.append(record)
        tree.restore()

        # Retained-invoice mutants use a scratch copy of the pinned file.
        pristine_retained = RETAINED.read_bytes()
        scratch_retained = work / 'retained-invoice.json'
        for name, edit in retained_mutants():
            value = json.loads(pristine_retained)
            edit(value)
            scratch_retained.write_bytes(dumps(value))
            verdict, detail, summary = failure(mod, global_dir, work / ('out-' + name), scratch_retained)
            record = dict(name=name, mutant_class='E', verdict=verdict, detail=detail,
                          summary=summary, downstream=None)
            if verdict == 'accepted':
                record['downstream'] = probe_assemble(global_dir / 'audit/OWNERS-AND-PROFILE.json',
                                                      work / ('out-' + name) / 'PREFIX-AND-INVOICE.json')
            records.append(record)
        assert sha(RETAINED) == hashlib.sha256(pristine_retained).hexdigest(), 'retained invoice unchanged'

        result = dict(status='PASS_INVOICE_MUTANT_COVERAGE',
                      checked_mutants=len(records),
                      rejected=sum(1 for r in records if r['verdict'] == 'rejected'),
                      accepted=sum(1 for r in records if r['verdict'] == 'accepted'),
                      positive=positive,
                      pins=dict(upstream1087=PINS['upstream1087.tar.gz'],
                                selected_replay=sha(FIXTURE),
                                invoice_allcold_py=sha(src / 'code/invoice_allcold.py'),
                                retained_invoice=sha(RETAINED)),
                      records=records)

    if a.json:
        Path(a.json).write_text(json.dumps(result, indent=2) + '\n')
    if a.write:
        EXPECT.write_text(json.dumps(result, indent=2) + '\n')
        print('WROTE', EXPECT)
    else:
        expected = read_json(a.expect)
        assert expected == result, ('mutant census differs from receipt; rerun with --write only after '
                                    'reviewing the change: ' + a.expect.name)
    print(result['status'], '%d mutants: %d rejected, %d accepted' %
          (result['checked_mutants'], result['rejected'], result['accepted']))
    for r in result['records']:
        if r['verdict'] == 'accepted':
            print('  ACCEPTED', r['name'], '->', r['downstream'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
