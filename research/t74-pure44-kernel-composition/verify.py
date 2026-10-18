#!/usr/bin/env python3
"""Bounded local rebuild, source/receipt bindings and fixed-profile cap.
Full cold admission: supplier/verify_package.py.
Marius-Paul Dumitrean, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from fractions import Fraction as Q

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
S = P / 'supplier'
LOCAL = {1: 2341, 2: 505, 3: 420, 4: 124, 5: 42, 8: 8}
GLOBAL = {1: 1582416, 2: 336330, 3: 288393, 4: 82584, 5: 29451,
          7: 148, 8: 5328, 14: 1, 48: 24479}
MANIFEST = 'e1bcf65a27e52767e2f7f4c28b284ff21b4e4f991ba2a1a803617abe49ef3a9a'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def profile(p):
    return {int(k): v for k, v in p.items()}


def check_cut(word):
    # Additive guard from PR2478 (mdumitrean, Claude-assisted). The retained
    # scalar auditor alone does not price arbitrary non-centre cut operations.
    centres = set(word['centers'])
    v = word['report']['v']
    need(len(centres) == 8, 'eight distinct centres')
    need(all(g[0] == 'add' and v <= g[1] < 2 * v and g[2] in centres
             for g in word['cut']), 'cut must contain centre-to-target ADDs')


def cut_controls(word):
    check_cut(word)
    for field, value in ((1, 0), (2, 0)):
        mutant = dict(word, cut=[list(g) for g in word['cut']])
        mutant['cut'][0][field] = value
        try:
            check_cut(mutant)
        except ValueError:
            continue
        raise ValueError('invalid cut operation accepted')


def source_bindings():
    need(sha(S / 'MANIFEST.json') == MANIFEST, 'frozen source manifest')
    expected = read(S / 'MANIFEST.json')
    actual = {f.relative_to(S).as_posix(): sha(f) for f in S.rglob('*') if f.is_file()}
    need(set(actual) == set(expected) | {'MANIFEST.json'}, 'source inventory')
    need(all(actual[k] == v for k, v in expected.items()), 'frozen source bytes')
    for item in read(P / 'SOURCES.json')['comparison_sources']:
        raw = (P / item['path']).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(hashlib.sha256(raw).hexdigest() == item['sha256'], 'comparison SHA256')
        need(blob == item['git_blob'], 'comparison Git blob')
    return actual


def compare_latest():
    """Structural comparison, not complete admission of the comparison branch."""
    rows = []
    for case in ('base', 'extra'):
        latest = P / 'comparison/pr2474/new/borrow'
        word = read(latest / 'words' / f'BORROW-WORD-43{case}.json.gz')
        ours = read(S / 'new/borrow-extension/words' / f'BORROW-WORD-44{case}.json.gz')
        cut_controls(ours)
        kernel = read(latest / 'inputs' / f'kernel_43{case}.json')
        original = read(S / 'new/composition/inputs' / f'kernel_43{case}.json')
        need(kernel['declared_gate_edit'] == original['declared_gate_edit'], 'same kernels')
        bkeys = [g[:-1] for g in word['B']]
        for kind, _, gate in kernel['declared_gate_edit']:
            need((gate in bkeys) == (kind == 'insert'), 'kernel edit in actual latest word')
        handoff = read(latest / 'inputs' / f'handoff_43{case}.json')
        need(handoff['derived_removed_diff'] == [619, 621, 622, 623], 'handoff delta')
        need(619 in handoff['fields']['removed'] and 619 in word['removed'], '619 already removed')
        need('619' not in word['start_extra'] and '619' not in word['helper_final'], 'no remaining helper619')
        need(not any(619 in g[1:3] for g in word['B']), 'no remaining B use of helper619')
        witness = read(latest / 'inputs' / f'witness_43_{case}.json')
        loan = [x for x in witness['pairs'] if x['borrow_from'] == 530]
        need(len(loan) == 1 and loan[0]['register'] == 651, '530 already lends to651')
        need(len([x for x in word['warps'] if x[1] == 530]) == 1, 'latest530 warp')
        need(len([x for x in word['warps'] if x[1] == 1]) == 1, 'retired-source1 handoff')
        need(619 in ours['removed'] and profile(ours['report']['local_profile']) == LOCAL, 'our distinct word')
        rows.append({'case': case, 'same_kernel_edits': True,
                     'latest_already_removes_619': True, 'latest_530_lends_to': 651,
                     'our_helpers': 480 - len(ours['removed']),
                     'latest_helpers': 480 - len(word['removed'])})
    return rows


def receipt_bindings():
    for name, digest in read(P / 'evidence/MANIFEST.json').items():
        need(sha(P / 'evidence' / name) == digest, 'evidence hash: ' + name)
    grand = read(P / 'evidence/RESULT.json')
    release = read(P / 'evidence/RELEASE-RECEIPT.json')
    supplier = read(P / 'evidence/SUPPLIER-RESULT.json')
    assembly = read(P / 'evidence/ASSEMBLY.json')
    invoice = read(P / 'evidence/PREFIX-AND-INVOICE.json')
    owners = read(P / 'evidence/HOSTED-OWNERS-BINDING.json')
    need(grand['status'] == 'PASS_COMPLETE_NEW_CONDITIONAL_KAPPA_PACKAGE', 'grand status')
    need(release['status'] == 'PASS_RELEASE', 'release status')
    need(supplier['status'] == 'PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION', 'supplier status')
    need(assembly['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY', 'assembly status')
    need(grand['source_manifest_sha256'] == release['manifest_sha256'] ==
         supplier['manifest_sha256'] == MANIFEST, 'receipt source bindings')
    need(grand['source_unchanged'] and grand['hosted_owner_binding'], 'full replay coverage')
    need(owners['status'] == 'PASS_HOSTED_OWNERS_CROSS_STAGE_BINDING' and
         len(owners['mutations_rejected']) == 2, 'owner binding controls')
    need(profile(assembly['complex_profile']) == GLOBAL, 'admitted global profile')
    need(sum(r * n for r, n in GLOBAL.items()) == 4816512, 'global mass')
    need(grand['roles'] == supplier['roles'] == 290376 and invoice['live'] == 66304, 'owner roles')
    need(invoice['physical'] == grand['physical'] == 66826, 'private stock included')
    need(grand['ordinary_bootstrap_levels'] == 12, 'ordinary bootstrap')
    claim = read(S / 'outer/OUTER-CLAIM.json')
    kappa = Q(claim['kappa'])
    need(kappa == Q(claim['kappa_rational']) == Q(grand['kappa_decimal']) ==
         Q(release['kappa_decimal']), 'modern kappa bindings')
    need(kappa < Q(assembly['complex_lower']), 'modern outer below native saving')
    latest = Q(read(P / 'comparison/pr2474/outer/OUTER-CLAIM.json')['kappa'])
    need(kappa < latest, 'explicitly superseded claim')
    need(all(s['exit_code'] == 0 for s in supplier['stages']), 'supplier stages')
    return kappa


def packing_cap(kappa):
    source = ROOT / 'research/complex-local-word-ceiling/ceiling.py'
    evidence = read(P / 'evidence/PACKING-CAP.json')
    need(sha(source) == evidence['ceiling_source']['sha256'], 'cap engine binding')
    spec = importlib.util.spec_from_file_location('packing_ceiling', source)
    cap = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cap)
    lo, hi = cap.ceiling(LOCAL, 73, 66304, 666, 64)
    need((lo, hi) == (Q(evidence['a_lower']), Q(evidence['a_upper'])), 'exact cap bracket')
    need(cap.relax(LOCAL, 73, 66304, 666, 64, lo)[1] < 1 <
         cap.relax(LOCAL, 73, 66304, 666, 64, hi)[0], 'directed cap inequalities')
    need(Q(evidence['kappa_cap']) == hi and kappa / hi == Q(evidence['realized_fraction']),
         'modern outer uses kappa<a, not historical balanced conversion')
    need(72 * 66304 + 64 * 666 == sum(r * n for r, n in GLOBAL.items()), 'coverage law')
    try:
        cap.model(LOCAL, 73, 66304, 666, 64, R=52)
    except ValueError:
        pass
    else:
        raise ValueError('invalid rank52 cap accepted')
    return str(hi)


def main():
    need(not sys.flags.optimize, 'assertions required by retained producer')
    sys.dont_write_bytecode = True
    before = source_bindings()
    comparison = compare_latest()
    kappa = receipt_bindings()
    cap = packing_cap(kappa)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    with tempfile.TemporaryDirectory(prefix='pure44-composition-') as temporary:
        output = Path(temporary) / 'rebuild'
        subprocess.run([sys.executable, '-B', str(S / 'new/composition/produce.py'),
                        '--out', str(output), '--controls', '--expected-dir',
                        str(S / 'new/borrow-extension/words')], check=True, env=env)
        rebuilt = read(output / 'RESULT.json')
        need(rebuilt['status'] == 'PASS_PORTABLE_COMPOSED_BORROW_WORDS', 'fresh rebuild')
        need(len(rebuilt['results']) == 2, 'both orientations')
        for row in rebuilt['results']:
            need(profile(row['profile']) == LOCAL and row['targeted_mutants_rejected'] == 4,
                 'actual profile and kernel/warp failure controls')
    need(source_bindings() == before, 'source unchanged during bounded replay')
    print(json.dumps({'status': 'PASS_LOCAL_COMPOSITION_AND_PUBLICATION_BINDINGS',
                      'modern_kappa': str(kappa), 'modern_packing_cap': cap,
                      'comparison': comparison,
                      'scope': 'Fresh local rebuild and controls, retained complete cold receipts; '
                               'full admission is a separate documented command.'}, indent=2))


if __name__ == '__main__':
    main()
