"""One fixed contact-only qualification gate; all work stays in one cgroup."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def bindings(out):
    need(read(out / 'CONTROLS.json')['status'] == 'PASS_SOURCE_FREE_CONTROLS', 'controls missing')
    built = read(out / 'built/edit-manifest.json')
    need(sha(out / 'built/candidate-word.json.gz') == built['candidate_gzip_sha256'], 'built candidate gzip mismatch')
    exact = read(out / 'exact/status.json')
    need(exact['status'] == 'U_CONDITIONAL_LITERAL_EXACT_ONLY', 'exact missing')
    need(exact['exact_gzip_sha256'] == sha(out / 'exact/EXACT.json.gz'), 'exact gzip changed')
    proof = read(out / 'proof/proof.json')
    proof_status = read(out / 'proof/status.json')
    need(proof_status['status'] == proof['status'] == 'ZERO_NORMALIZED_STREAM_ONLY_UNQUALIFIED', 'zero proof missing')
    need(proof_status['proof_sha256'] == sha(out / 'proof/proof.json'), 'proof digest mismatch')
    need(proof['exact_gzip_sha256'] == exact['exact_gzip_sha256'] and
         proof['exact_sha256'] == exact['exact_sha256'] and
         proof['exact_status_sha256'] == sha(out / 'exact/status.json'), 'proof/exact mismatch')
    cert = read(out / 'certificates/certificate.json')
    certificate_status = read(out / 'certificates/status.json')
    need(certificate_status['status'] == cert['status'] == 'PASS_CERTIFICATES_204', 'certificates missing')
    need(certificate_status['certificate_sha256'] == sha(out / 'certificates/certificate.json'), 'certificate digest mismatch')
    need(cert['manifest_sha256'] == sha(out / 'built/edit-manifest.json'), 'certificate manifest mismatch')
    physical = read(out / 'physical/PHYSICAL.json')
    need(read(out / 'physical/status.json')['status'] == physical['status'] == 'CHANGED_ROUTE_PHYSICAL_DIFFERENTIAL_PASS_UNQUALIFIED', 'physical missing')
    price = read(out / 'price/PRICE.json')
    need(price['status'] == 'PROVISIONAL_UNDER_COMMON_U', 'price missing')
    for obj, key in ((proof, 'candidate_canonical_sha256'), (cert, 'candidate_canonical_sha256'),
                     (physical, 'candidate_word_canonical_sha256'), (price['bindings'], 'candidate_canonical_sha256')):
        need(obj[key] == built['candidate_canonical_sha256'], 'candidate identity mismatch')
    need(price['bindings']['exact_gzip_sha256'] == exact['exact_gzip_sha256'] and
         price['bindings']['manifest_sha256'] == sha(out / 'built/edit-manifest.json'), 'price exact binding')
    paths = ['CONTROLS.json', 'built/candidate-word.json.gz', 'built/edit-manifest.json', 'built/status.json',
             'exact/EXACT.json.gz', 'exact/status.json', 'proof/proof.json', 'proof/status.json',
             'certificates/certificate.json', 'certificates/source-certificates.json',
             'certificates/candidate-certificates.json', 'certificates/status.json',
             'physical/PHYSICAL.json', 'physical/status.json', 'price/PRICE.json',
             'price/invoice-source-normalized.json', 'price/invoice-new.json']
    return {rel: sha(out / rel) for rel in paths}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir()
    start = time.monotonic()
    deadline = start + 580
    rows = []
    report = {'status': 'INCOMPLETE', 'stages': rows, 'qualified_kappa': False,
              'scope': 'Fixed zero-row/contact-phase/certificate/provisional-invoice gate. Fresh complete native/signed/common-U resources are still required.'}
    stages = [('controls', 'controls.py', 30, []), ('built', 'build.py', 10, []),
              ('exact', 'exact.py', 150, ['--built', str(args.out / 'built')]),
              ('proof', 'proof.py', 30, ['--built', str(args.out / 'built'), '--exact', str(args.out / 'exact')]),
              ('certificates', 'certificates.py', 210, ['--built', str(args.out / 'built')]),
              ('physical', 'physical.py', 75, ['--built', str(args.out / 'built'), '--exact', str(args.out / 'exact')]),
              ('price', 'price.py', 70, ['--built', str(args.out / 'built'), '--exact', str(args.out / 'exact')])]
    try:
        need(__debug__ and sys.version_info[:2] == (3, 12), 'Python3.12 assertions enabled required')
        for name, script, cap, extra in stages:
            left = deadline - time.monotonic()
            need(left > 0, 'whole 580-second deadline')
            cache = args.out / 'stage-pycache' / name
            argv = [sys.executable, '-I', '-B', '-X', 'pycache_prefix=' + str(cache), str(HERE / script)]
            if name == 'controls':
                argv += ['--out', str(args.out / 'CONTROLS.json')]
            else:
                argv += ['--root', str(args.root), '--out', str(args.out / name), *extra]
            begin = time.monotonic()
            with (args.out / (name + '.stdout')).open('x') as stdout, (args.out / (name + '.stderr')).open('x') as stderr:
                done = subprocess.run(argv, stdout=stdout, stderr=stderr, check=False,
                                      timeout=min(cap, left), env=dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1'))
            row = {'name': name, 'argv': argv, 'exit_code': done.returncode,
                   'wall_seconds': time.monotonic() - begin, 'stage_cap_seconds': cap}
            rows.append(row)
            write(args.out / 'PARTIAL.json', report)
            print(json.dumps(row, sort_keys=True), flush=True)
            need(done.returncode == 0, 'failed stage ' + name)
        report['receipt_hashes'] = bindings(args.out)
        need(time.monotonic() < deadline, 'whole 580-second deadline after receipt binding')
        report['status'] = 'PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U'
    except BaseException as error:
        report.update(error_type=type(error).__name__, error=str(error))
    report['wall_seconds'] = time.monotonic() - start
    write(args.out / 'RESULT.json', report)
    print(json.dumps({'status': report['status'], 'wall_seconds': report['wall_seconds']}, sort_keys=True), flush=True)
    return 0 if report['status'] == 'PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U' else 1


if __name__ == '__main__':
    raise SystemExit(main())
