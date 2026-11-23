"""Replay separate repair, direct-role and mass follow-ups without changing landed evidence."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ArithmeticError(message)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    source = HERE / 'sources/pr8042'
    manifest = json.loads((HERE / 'SOURCE-BINDINGS.json').read_text())
    need(manifest['commit'] == 'dfd25d553a843a946ca0b94130a5ff8943e98fdd', 'wrong source head')
    for name, pin in manifest['files'].items():
        path = Path(name)
        need(not path.is_absolute() and '..' not in path.parts, 'invalid source path')
        data = (source / path).read_bytes()
        need(len(data) == pin['size'] and sha256(data).hexdigest() == pin['sha256'],
             'retained source changed: ' + name)
    frozen = json.loads((HERE / 'FROZEN-FOLLOWUPS.json').read_text())
    need(frozen['source_commit'] == manifest['commit'], 'follow-up source pin differs')
    for name, expected in frozen['files'].items():
        need(sha256((HERE / name).read_bytes()).hexdigest() == expected,
             'frozen follow-up changed: ' + name)
    accepted_owner = json.loads((HERE / 'mass-enclosure/review/OWNER-COROLLARY-ACCEPTANCE.json').read_text())
    for name, key in (('mass-enclosure/OWNER-COROLLARY.md', 'corollary_sha256'),
                      ('census/OWNER-CENSUS.md', 'census_proof_sha256'),
                      ('mass-enclosure/PROOF.md', 'mass_proof_sha256')):
        need(sha256((HERE / name).read_bytes()).hexdigest() == accepted_owner[key],
             'owner composition differs from accepted review: ' + name)
    spec = spec_from_file_location('followup_source_bootstrap', source / 'bootstrap.py')
    bootstrap = module_from_spec(spec)
    spec.loader.exec_module(bootstrap)
    receipts = []
    with TemporaryDirectory(prefix='retimed-followup-replay-') as temporary:
        runtime = Path(temporary)
        bootstrap.install(runtime)
        stock = runtime / 'mass-review-stock'
        jobs = [
            ('mass-stock', 'mass-enclosure/restore_stock.py',
             ['--runtime', str(runtime), '--output', str(stock)],
             stock / 'RESULT.json', 'PASS_AUTHENTICATED_MASS_REVIEW_STOCK'),
            ('repair', 'repair-bounds/review/check_review.py',
             ['--runtime', str(runtime), '--output', str(output / 'repair.json')],
             output / 'repair.json', 'PASS_INDEPENDENT_RETIMED_BYTES_REVIEW'),
            ('direct', 'direct-scale/check.py',
             ['--runtime', str(runtime), '--output', str(output / 'direct.json')],
             output / 'direct.json', 'PASS_DIRECT_SCALAR_AND_ROOT_BYTES'),
            ('direct-review', 'direct-scale/review/check_review.py',
             ['--source', str(HERE / 'direct-scale'), '--output', str(output / 'direct-review.json')],
             output / 'direct-review.json', 'PASS_INDEPENDENT_DIRECT_ROLE_ENVELOPE'),
            ('mass', 'mass-enclosure/check.py', ['--output', str(output / 'mass.json')],
             output / 'mass.json', 'PASS_DYADIC_MASS_ENCLOSURE'),
            ('mass-review', 'mass-enclosure/review/replay.py',
             ['--runtime', str(runtime), '--stock', str(stock),
              '--output', str(output / 'mass-review')],
             output / 'mass-review/RESULT.json', 'PASS_PORTABLE_MASS_ENCLOSURE_REVIEW'),
        ]
        for label, script, arguments, record_path, marker in jobs:
            command = [sys.executable, '-IB', str(HERE / script), *arguments]
            run = subprocess.run(command, capture_output=True, text=True, timeout=150)
            (output / (label + '.log')).write_text(run.stdout + run.stderr)
            run.check_returncode()
            record = json.loads(record_path.read_text())
            need(record['status'] == marker, 'unexpected result: ' + label)
            if label == 'direct-review':
                accepted = json.loads((HERE / 'direct-scale/review/EVIDENCE.json').read_text())
                need(record == accepted, 'direct review differs from accepted receipt')
            receipts.append({'label': label, 'status': marker,
                             'sha256': sha256(record_path.read_bytes()).hexdigest()})
            print(marker, flush=True)
    proofs = ('repair-bounds/PROOF.md', 'repair-bounds/review/SHARP-REPAIR.md',
              'repair-bounds/review/CROSS-REVIEW.md', 'direct-scale/PROOF.md',
              'direct-scale/review/REVIEW.md', 'mass-enclosure/PROOF.md',
              'mass-enclosure/review/CROSS-REVIEW.md', 'mass-enclosure/OWNER-COROLLARY.md')
    result = {'status': 'PASS_RETIMED_REPAIR_DIRECT_AND_MASS_FOLLOWUPS',
              'source_commit': manifest['commit'],
              'seconds': round(time.monotonic() - started, 3), 'receipts': receipts,
              'proof_sha256': {name: sha256((HERE / name).read_bytes()).hexdigest() for name in proofs},
              'production_repair': '<=6V* after role-wise historical maxima; actual header gives t<=a/2',
              'direct_scalar': '27521/3420 * V* <9V* for 22 fixed roles across differing calls',
              'ordinary_root': '<7V* for five fixed roles',
              'public_rectangle': '<18V_slab for two serial padded roles',
              'production_mass': 'Delta <2^24 N^-57 <=2^-33 <1/4 for installed callers',
              'owner_corollary': 'Retained Gaussian Arena.high <2B now derives its local mass premise from the literal loop',
              'scope': 'Local source-bound lemmas; all five canonical assumptions and selected kappa unchanged'}
    (output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
