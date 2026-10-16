"""Verify the frozen owner improvement with unchanged PR1018 admission code.

Default: rebuild k8 and its slot layer. --native-from explicitly reuses a
completed, pinned rebuild (including all controls), and reruns global admission.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from prepare import P, ROOT, UP, read, sha, dump, prepare

CHAIN_STEPS = ['pivot-swap', 'cold44-exact', 'lec-p6n', 'promotion', 'promo-controls',
               'lec-promo', 'jx', 'jx-control-C0_identity', 'jx-control-C1_741_only',
               'jx-control-N3_plain_join_moved_reads', 'lec-jx', 'hybrids',
               'hybrid-controls', 'lec-hyb', 'frames', 'lec-frames', 'native',
               'ledgers', 'local-replay', 'wrappers', 'phases']
SLOT_STEPS = ['parent-manifest', 'slots', 'slot-controls', 'native', 'ledgers',
              'local-replay', 'wrappers', 'phases', 'audit-local', 'strict']


def payload(path):
    return hashlib.sha256(gzip.decompress(Path(path).read_bytes())).hexdigest()


def check_steps(path, expected):
    rows = read(path)
    assert [s['step'] for s in rows] == expected
    assert all(type(s['exit_code']) is int and s['exit_code'] == 0 for s in rows)


def check_native(native):
    """Rebind receipt references and proof-relevant identities, not just status strings."""
    leaver = ROOT / 'research/gauge44-leaver8/construction/leaver'
    cp = read(leaver / 'CHAIN-PINS-k8.json')
    sp = read(UP / 'construction/slots/SLOT-PINS-k8.json')
    check_steps(native / 'word/STEPS.json', ['gauge-forward', 'port0', 'port1', 'port2', 'port3', 'cold44'])
    check_steps(native / 'chain/STEPS.json', CHAIN_STEPS)
    check_steps(native / 'slots/STEPS.json', SLOT_STEPS)
    assert payload(native / 'chain/frames/FULL-WORD.json.gz') == sp['base_sha256']
    for label in ('lec-p6n', 'lec-promo', 'lec-jx', 'lec-hyb', 'lec-frames'):
        controls = read(native / 'chain' / label / 'COLD-END-CONTROLS.json')
        assert controls['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS'
        assert len(controls['rejected']) == cp[label] == 95
    controls = read(native / 'slots/slot-controls/controls.json')
    assert sorted(controls) == sorted(sp['slot_controls']) and all(v['ok'] for v in controls.values())
    for directory, pins in [(native / 'chain/local', cp), (native / 'slots/local', sp)]:
        assert payload(directory / 'CANONICAL-WORD.json.gz') == pins['canonical_sha256']
        checks = read(directory / 'LOCAL-CHECKS.json')
        programs = read(directory / 'LOCAL-PROGRAMS.json.gz')
        assert set(programs) == set(checks) == {'forward', 'backward'}
        for direction in programs:
            encoded = json.dumps(programs[direction], sort_keys=True, separators=(',', ':')).encode()
            assert hashlib.sha256(encoded).hexdigest() == checks[direction]['sha256'] == pins['program_sha256'][direction]
        assert sha(directory / 'CLIFFORD-RECIPES.json') == pins['clifford_recipes_sha256']
        phase = read(directory / 'CLIFFORD-REVIEW.json')
        assert phase['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES'
        assert phase['canonical_word_sha256'] == sha(directory / 'CANONICAL-WORD.json.gz')
        assert phase['recipe_sha256'] == sha(directory / 'CLIFFORD-RECIPES.json')
        assert phase['all_child_equalities_include_global_phase'] is True
    assert payload(native / 'slots/slots/FULL-WORD.json.gz') == sp['word_sha256']
    result = read(native / 'slots/RESULT.json')
    assert result['status'] == 'PASS_SLOTS_ON_CHECKED_K8_BASELINE'
    assert result['kappa_decimal'] == sp['kappa_decimal']
    old = read(native / 'slots/global/ASSEMBLY.json')
    assert old['kappa_decimal'] == sp['kappa_decimal']
    assert len(old['outer']) == 47 and len(old['conservative_outer']) == 47
    return dict(status='PASS_PINNED_COMPLETE_K8_AND_SLOT_REBUILD',
                native_directory=str(native), chain_steps=len(CHAIN_STEPS), slot_steps=len(SLOT_STEPS),
                cold_end_controls=5*95, slot_control_outcomes=len(controls),
                source_result_sha256=sha(native / 'slots/RESULT.json'),
                source_assembly_sha256=sha(native / 'slots/global/ASSEMBLY.json'),
                canonical_payload_sha256=sp['canonical_sha256'])


def main():
    assert __debug__, 'Assertions are required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--word-dir', type=Path, help='Completed, pinned PR741 gauge44 initial word directory')
    ap.add_argument('--native-from', type=Path, help='Completed word/, chain/, slots/ rebuild; explicitly rechecked')
    args = ap.parse_args()
    work = args.work.resolve()
    assert not work.exists() and not work.is_relative_to(ROOT)
    assert args.native_from or args.word_dir, 'Supply --word-dir for rebuild, or explicitly --native-from'
    work.mkdir(parents=True)
    for rel, digest in read(P / 'SOURCE-PINS.json').items():
        assert sha(ROOT / rel) == digest, 'Changed upstream dependency: ' + rel
    for name in ('OWNERS.json.gz', 'SPEC.json'):
        assert sha(P / name) == read(P / 'CLAIM.json')['files'][name], 'Changed frozen candidate'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    env.pop('PYTHONOPTIMIZE', None)
    env.pop('WITNESS_DISCOVER', None)
    env.pop('WITNESS_RECORD', None)
    steps = []

    def run(name, script, *arguments):
        log = work / (name + '.log'); start = time.monotonic()
        with log.open('w') as f:
            proc = subprocess.run([sys.executable, '-B', str(script), *map(str, arguments)],
                                  cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
        steps.append(dict(step=name, exit_code=proc.returncode, seconds=round(time.monotonic()-start, 3), log_sha256=sha(log)))
        dump(work / 'STEPS.json', steps)
        assert proc.returncode == 0, name + ':\n' + log.read_text()[-6000:]
        print('PASS', name, flush=True)

    for package in ('gauge44-leaver8', 'gauge44-slots'):
        run(package + '-manifest', ROOT / 'research' / package / 'verify_manifest.py')
    if args.native_from:
        native = args.native_from.resolve()
    else:
        native = work / 'native'
        pr635 = ROOT / 'research/complex-sw4-frame8/vendor/pr635'
        leaver = ROOT / 'research/gauge44-leaver8/construction/leaver'
        run('leaver-word', leaver / 'reproduce_leaver.py', '--main', ROOT, '--pr635', pr635,
            '--word-dir', args.word_dir.resolve(), '--out', native / 'word', '--id', 'k8', '--word-only')
        run('leaver-chain', leaver / 'reproduce_leaver_chain.py', '--main', ROOT, '--pr635', pr635,
            '--leaver-dir', native / 'word', '--hamming', args.word_dir.resolve() / 'hamming',
            '--out', native / 'chain', '--id', 'k8')
        run('slot-layer', UP / 'construction/slots/verify_slots.py', '--main', ROOT, '--pr635', pr635,
            '--baseline', native / 'chain', '--work', native / 'slots')
    binding = check_native(native)
    binding['reuse_explicitly_requested'] = bool(args.native_from)
    dump(work / 'NATIVE-BINDING.json', binding)
    preparation = prepare(work / 'runtime', P / 'OWNERS.json.gz', P / 'SPEC.json')
    dump(work / 'PREPARATION.json', preparation)
    run('strict-global', work / 'runtime/verify_global.py', '--main', ROOT,
        '--local', native / 'slots/local', '--work', work / 'global')
    result = read(work / 'global/ASSEMBLY.json')
    claim = read(P / 'CLAIM.json')
    assert result['kappa_decimal'] == claim['kappa_decimal']
    assert result['complex_profile'] == {str(k): v for k, v in preparation['global_profile'].items()}
    from fractions import Fraction as F
    assert F(result['kappa']) > F(claim['baseline_kappa'])
    assert len(result['outer']) == len(result['conservative_outer']) == 47
    assert all(F(v) > 0 for v in result['outer'].values())
    owner = read(work / 'global/global/audit/OWNERS-AND-PROFILE.json')
    invoice = read(work / 'global/global/audit/PREFIX-AND-INVOICE.json')
    controls = read(work / 'global/ADMISSION-CONTROLS.json')
    bit = read(work / 'global/BIT-SUPPLIER-CONTROLS.json')
    assert len(controls['rejected_controls']) == 69 and len(bit['rejected_controls']) == 12
    assert all(invoice['strict_checks'].values())
    receipt = dict(status='PASS_K8_COORDINATED_OWNERS_COMPLETE_ADMISSION',
                   kappa_decimal=result['kappa_decimal'], baseline_kappa=claim['baseline_kappa'],
                   gain_percent=str(float(100*(F(result['kappa'])/F(claim['baseline_kappa'])-1))),
                   complex_lower=result['complex_decimal'], bit_lower=result['bit_decimal'],
                   admission_controls=69, bit_supplier_controls=12, outer_strict_inequalities=47,
                   native=binding, scope=result['scope'], steps=steps,
                   source_pins_sha256=sha(P / 'SOURCE-PINS.json'),
                   assembly_sha256=sha(work / 'global/ASSEMBLY.json'),
                   owner_audit_sha256=sha(work / 'global/global/audit/OWNERS-AND-PROFILE.json'),
                   invoice_sha256=sha(work / 'global/global/audit/PREFIX-AND-INVOICE.json'))
    dump(work / 'RESULT.json', receipt)
    print(receipt['status'], result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
