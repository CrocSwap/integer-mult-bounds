"""Offline reconstruction and fresh full admission of the rank-five expansion.

Prepared with OpenAI Codex assistance; Apache-2.0. No optimizer or network.
"""
import argparse, gzip, hashlib, json, os, subprocess, sys, time
from pathlib import Path

if not __debug__:
    raise SystemExit('Assertions must remain enabled.')
ROOT = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--work', type=Path, required=True)
a = ap.parse_args()
work = a.work.resolve()
assert not work.exists() and not work.is_relative_to(ROOT)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
manifest = read(ROOT / 'MANIFEST.json')
for path, digest in manifest.items():
    assert sha(ROOT / path) == digest, path
sources = read(ROOT / 'SOURCES.json')
for path, pin in sources['retained_files'].items():
    data = (ROOT / path).read_bytes()
    assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == pin['git_blob_sha1'], path
work.mkdir(parents=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0', PYTHONUTF8='1')
env.pop('PYTHONOPTIMIZE', None)
stages = []
def run(name, script, *args):
    start = time.monotonic()
    log = work / (name + '.log')
    print('RUN', name, flush=True)
    with log.open('w', encoding='utf-8') as f:
        proc = subprocess.run([sys.executable, '-B', str(ROOT / script), *map(str, args)], env=env, stdout=f, stderr=subprocess.STDOUT)
    stages.append(dict(name=name, exit_code=proc.returncode, seconds=time.monotonic()-start, log_sha256=sha(log)))
    (work / 'STAGES.json').write_text(json.dumps(stages, indent=2)+'\n')
    if proc.returncode:
        raise RuntimeError(name + ' failed\n' + log.read_text()[-6000:])
    print('PASS', name, flush=True)

run('local-construction-scalar-price', 'local/verify.py', '--work', work / 'local')
word = work / 'local/candidate/FULL-WORD.json.gz'
price = work / 'local/PRICE.json'
assert hashlib.sha256(gzip.decompress(word.read_bytes())).hexdigest() == '6a02824c7484b9fd768a39d87b9c65dbe5221a877032ed1f74d11afb2acdd7d8'
run('omitted-middle-shear-control', 'omit_control.py', '--candidate', word,
    '--auditor', ROOT / 'local/audit_scalar.py', '--selection', ROOT / 'local/inputs/STATIC44-SELECTION.json', '--out', work / 'omission')
plan = read(ROOT / 'physical/data/SAT534-PLAN.json')
plan['profile'] = read(price)['global_profile']
(work / 'PLAN.json').write_text(json.dumps(plan, indent=2)+'\n')
run('full-physical-admission', 'physical/replay.py', '--word', word, '--word-sha256', sha(word),
    '--expected-price', price, '--plan', work / 'PLAN.json', '--out', work / 'physical')
audit = work / 'physical/complex-audit'
run('exact-assembly', 'assemble.py', '--owner', audit / 'OWNERS-AND-PROFILE.json',
    '--invoice', audit / 'PREFIX-AND-INVOICE.json', '--out', work / 'ASSEMBLY.json')
run('assembly-admission-controls', 'assembly_controls.py', '--owner', audit / 'OWNERS-AND-PROFILE.json',
    '--invoice', audit / 'PREFIX-AND-INVOICE.json', '--out', work / 'ASSEMBLY-CONTROLS.json')
result = read(work / 'ASSEMBLY.json')
expected = read(ROOT / 'evidence/EXPECTED-ASSEMBLY.json')
# Elapsed phase-audit time is retained upstream and changes receipt digests.
# Bind those digests to THIS fresh run; compare every mathematical field and
# every immutable supplier/engine digest against the frozen expected result.
assert result['template_sha256'] == read(work / 'physical/RESULT.json')['template_sha256']
assert result['input_sha256']['owner_audit'] == sha(audit / 'OWNERS-AND-PROFILE.json')
assert result['input_sha256']['fresh_invoice'] == sha(audit / 'PREFIX-AND-INVOICE.json')
def cross_run_fields(obj):
    obj = dict(obj)
    obj.pop('template_sha256')
    obj['input_sha256'] = {key: value for key, value in obj['input_sha256'].items()
                           if key not in ('owner_audit', 'fresh_invoice')}
    return obj
assert cross_run_fields(result) == cross_run_fields(expected), 'fresh exact mathematical result differs'
receipt = dict(status='PASS_FRESH_COMPLEX_TRACE_RANK5_AND_EXACT_ASSEMBLY', kappa=result['kappa'],
    kappa_decimal=result['kappa_decimal'], source_manifest_sha256=sha(ROOT / 'MANIFEST.json'),
    physical_receipt_sha256=sha(work / 'physical/RECEIPT.json'), assembly_sha256=sha(work / 'ASSEMBLY.json'),
    admission_controls_sha256=sha(work / 'ASSEMBLY-CONTROLS.json'),
    stages=stages, python=sys.version,
    scope='Fresh complex supplier admission and exact assembly with cited unchanged PR543 bit supplier. Retained all-size, common-label/mutable-source, whole-call hosting, precision/tape and analytic-transfer contracts remain conditional.')
(work / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(receipt['status'], result['kappa_decimal'], flush=True)
