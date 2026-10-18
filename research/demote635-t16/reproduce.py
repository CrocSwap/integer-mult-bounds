"""Fresh finite replay of both words, the parent assembly, and the mixed assembly.

Python 3.12+, Git, standard library; network on first fetch. Apache-2.0.
Prepared for seslly with substantial OpenAI Codex assistance.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import threading
import time

from construct import build_word, nominate, read, sha

if not __debug__:
    raise RuntimeError('Assertions required; do not use -O')
HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--main', type=Path, default=HERE.parents[1], help='repository root (normally automatic)')
    args = ap.parse_args()
    root, out = args.main.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    pins = read(HERE/'SOURCES.json')
    stages, lock = [], threading.Lock()

    def extract(commit, package, label):
        repository = root
        if subprocess.run(['git', '-C', str(root), 'cat-file', '-e', commit],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
            repository = out/(label+'.git')
            subprocess.run(['git', 'init', '--bare', str(repository)], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(repository), 'fetch', '--depth=1', pins['repository'], commit], check=True)
        archive, destination = out/(label+'.tar'), out/label
        subprocess.run(['git', '-C', str(repository), 'archive', '--output', str(archive), commit, package], check=True)
        destination.mkdir()
        with tarfile.open(archive) as stream:
            stream.extractall(destination, filter='data')
        archive.unlink()
        return destination/package

    parent = extract(pins['parent_commit'], pins['parent_package'], 'parent-source')
    native = extract(pins['native_commit'], pins['native_package'], 'native-source')
    assert sha(parent/'MANIFEST.json') == pins['parent_manifest_sha256']
    actual = {p.relative_to(parent).as_posix(): sha(p) for p in parent.rglob('*')
              if p.is_file() and p != parent/'MANIFEST.json'}
    assert actual == read(parent/'MANIFEST.json'), 'complete parent source manifest'
    for name, digest in read(parent/'data/UPSTREAM-PINS.json').items():
        assert sha(root/name) == digest, 'main dependency: '+name
    source = root/'research/complex-k492-owner-repair/vendor/multicold'
    ancestor = source/'vendor/pr558'
    old = ancestor/'vendor/pr552'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(source), GAIN_PR564_SOURCE=str(source))
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC',
                'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET', 'PR635_CODE', 'SW4_PIN', 'LEC_REASON_PINS'):
        env.pop(key, None)

    def run(name, script, *arguments, environment=None):
        started, log = time.monotonic(), out/(name+'.log')
        command = [sys.executable, '-B', str(source/'code/run_portable.py'), str(script), *map(str, arguments)]
        with log.open('w') as stream:
            result = subprocess.run(command, env=environment or env, stdout=stream, stderr=subprocess.STDOUT)
        with lock:
            stages.append(dict(name=name, exit_code=result.returncode, seconds=time.monotonic()-started,
                               log_sha256=sha(log)))
            (out/'STEPS.json').write_text(json.dumps(stages, indent=2)+'\n')
        assert result.returncode == 0, name+':\n'+log.read_text()[-5000:]
        print('PASS', name, flush=True)

    baseline_word = HERE/'data/BASELINE-WORD.json.gz'
    new_word = out/'DEMOTE635-WORD.json.gz'
    build_word(new_word)
    slot_pins = read(parent/'construction/slots/SLOT-PINS-k8.json')
    assert hashlib.sha256(gzip.decompress(baseline_word.read_bytes())).hexdigest() == slot_pins['word_sha256'] == pins['baseline_payload_sha256']
    nomination = out/'nomination'
    nominate(parent, nomination)

    def local(job):
        label, word = job
        target = out/label
        run(label+'-native', native/'code/hpe_audit_and_transport.py', '--raw', word,
            '--routing', old/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz', '--out', target)
        run(label+'-ledgers', native/'code/hpe_emit_local.py', target)
        run(label+'-replay', native/'code/hpe_audit_local.py', target)
        run(label+'-wrappers', native/'code/hpe_adapters_local.py', target/'CANONICAL-WORD.json.gz',
            target/'RESIDUAL-ADAPTERS.json', target/'WRAPPER-CHECKS.json')
        run(label+'-phases', ancestor/'code/phases_full.py', target, old/'complex-global/vendor531/vendor/clifford')
        run(label+'-independent', parent/'independent/audit_local.py', '--word', word, '--main', root,
            '--output', out/(label+'-INDEPENDENT.json'))

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(local, [('baseline', baseline_word), ('demote635', new_word)]))
    checks = read(out/'baseline/LOCAL-CHECKS.json')
    assert {k: v['sha256'] for k, v in checks.items()} == slot_pins['program_sha256']
    assert sha(out/'baseline/CLIFFORD-RECIPES.json') == slot_pins['clifford_recipes_sha256']
    run('frame-controls', HERE/'controls.py', '--source', parent, '--word', new_word,
        '--recipe', HERE/'data/RECIPE.json', '--main', root, '--out', out/'frame-controls')
    run('parent-global', parent/'verify_t16.py', '--main', root, '--local', out/'baseline', '--work', out/'parent-global')
    baseline = read(out/'parent-global/ASSEMBLY.json')
    assert baseline['kappa_decimal'] == pins['comparison_kappa']
    mixed = dict(env, WITNESS_SPEC=str(nomination/'data/SPEC.json'))
    code, glob = parent/'code', out/'global'

    def global_run(name, script, *arguments):
        run(name, code/script, *arguments, environment=mixed)

    global_run('bind', 'bind_providers_portable.py', '--baseline', out/'parent-global/parent16',
               '--provider', 'gauge44='+str(out/'baseline'), '--provider', 'demote635='+str(out/'demote635'),
               '--plan', nomination/'data/PLAN.json', '--out', glob)
    global_run('emit', 'emit_allcold.py', '--base', glob/'base', '--owners', nomination/'data/OWNERS.json',
               '--plan', glob/'PLAN.json', '--out', glob/'hosted')
    global_run('audit', 'audit_allcold.py', glob/'base', glob/'hosted', glob/'audit/ASYNC-AUDIT.json', '--mutation-controls')
    global_run('invoice', 'invoice_allcold.py', '--base', glob/'base', '--hosted', glob/'hosted',
               '--audit', glob/'audit', '--out', glob/'audit',
               '--retained-invoice', old/'complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json')
    global_run('assembly', 'assemble.py', source, glob, out/'ASSEMBLY.json')
    for label, script in [('ADMISSION-CONTROLS', 'assembly_controls.py'), ('BIT-CONTROLS', 'bit_supplier_controls.py')]:
        global_run(label, script, '--source-package', source, '--owner', glob/'audit/OWNERS-AND-PROFILE.json',
                   '--invoice', glob/'audit/PREFIX-AND-INVOICE.json', '--out', out/(label+'.json'))
    spec = read(HERE/'data/SPEC.json')
    independent_env = dict(env, T16_EXPECTED_IDLE=json.dumps(spec['expected']['idle_remainder_profile']),
                           T16_EXPECTED_WIDTHS=json.dumps(spec['providers']['gauge44']['inventory']))
    run('independent-owners', HERE/'independent.py', '--baseline-parent',
        out/'parent-global/global8/base/split-centres/GLOBAL-TEMPLATE.json.gz',
        '--owners', nomination/'data/OWNERS.json', '--word', out/'baseline/CANONICAL-WORD.json.gz',
        '--second-word', out/'demote635/CANONICAL-WORD.json.gz', '--second-times', *read(HERE/'data/RECIPE.json')['calls'],
        '--out', out/'INDEPENDENT-OWNERS.json', environment=independent_env)
    result, independent = read(out/'ASSEMBLY.json'), read(out/'INDEPENDENT-OWNERS.json')
    owner, invoice = read(glob/'audit/OWNERS-AND-PROFILE.json'), read(glob/'audit/PREFIX-AND-INVOICE.json')
    audit = read(glob/'audit/ASYNC-AUDIT.json')
    assert result['kappa'] == spec['expected']['kappa'] and Fraction(result['kappa']) > Fraction(baseline['kappa'])
    assert independent['profile'] == result['complex_profile'] and independent['rank_mass'] == owner['rank_mass'] == 1041408
    assert independent['roles'] == owner['hosted_residuals'] == audit['complex_hosted_residuals'] == 69120
    assert independent['calls'] == audit['complete_invocations'] == invoice['complete_invocation_sweeps'] == 144
    assert independent['prefix_bits'] == invoice['global_prefix_bits'] < invoice['charged_prefix_bits'] == 512
    assert independent['physical_row_coefficient'] == invoice['finite']['physical_row_coefficient'] < 20161
    assert len(independent['controls_rejected']) == 6 and len(audit['mutations_rejected']) == 23
    assert len(read(out/'ADMISSION-CONTROLS.json')['rejected_controls']) == 114
    assert len(read(out/'BIT-CONTROLS.json')['rejected_controls']) == 12
    assert all(invoice['strict_checks'].values()) and len(result['outer']) == 47
    assert all(Fraction(v) > 0 for v in result['outer'].values())
    assert result['provider_counts'] == {'gauge44': 35, 'demote635': 109}
    receipt = dict(status='PASS_DEMOTE635_T16_COMPLETE_ADMISSION', kappa=result['kappa'],
                   kappa_decimal=result['kappa_decimal'], comparison=baseline['kappa_decimal'],
                   parent_commit=pins['parent_commit'], reused_native_receipts=False,
                   historical_generators_rerun=False, stages=stages,
                   scope='Exact finite words, phases, whole-owner geometry and invoices. PR589 bit circuit cited and repriced. '
                         'Inherited uniform/compiler, realization/hosting, precision/tape and analytic obligations remain conditional.')
    (out/'RESULT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(receipt['status'], result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
