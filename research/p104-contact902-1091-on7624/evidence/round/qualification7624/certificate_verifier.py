"""Freshly replay both 204-lifetime words with the corrected strict checker."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--gate', type=Path, required=True)
    p.add_argument('--prepared', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    root, gate = a.root.resolve(), a.gate.resolve()
    need(gate == root / 'compose7624_completion/run/case', 'wrong first gate')
    a.out.mkdir()
    checker = root / 'compose7624_completion/certificates.py'
    need(sha(checker) == '10714b5e758ce2bd23432c7824dbcb719b9f81ae2444a32a2eb25d8d284d1411',
         'strict certificate checker source changed')
    prepared = json.loads((a.prepared / 'status.json').read_bytes())
    need(prepared['status'] == 'PREPARED_CERTIFICATES_NOT_REPLAYED_IN_FULL_JOB', 'certificate preparation missing')
    for name, pin in prepared['hashes'].items():
        need(sha(a.prepared / name) == pin, 'prepared certificate changed')
    argv = [sys.executable, '-I', '-B', '-X', 'pycache_prefix=' + str(a.out / 'pycache'),
            str(checker), '--root', str(root), '--built', str(gate / 'built'), '--out', str(a.out / 'fresh')]
    subprocess.run(argv, check=True, timeout=175)
    fresh = a.out / 'fresh'
    status = json.loads((fresh / 'status.json').read_bytes())
    report = json.loads((fresh / 'certificate.json').read_bytes())
    need(status['status'] == report['status'] == 'PASS_CERTIFICATES_204' and
         status['certificate_sha256'] == sha(fresh / 'certificate.json'), 'fresh certificate replay incomplete')
    pairs = [('source-certificate.json', 'source-certificates.json'),
             ('certificate.json', 'candidate-certificates.json')]
    for original, current in pairs:
        need((a.prepared / original).read_bytes() == (fresh / current).read_bytes(), 'fresh certificate input mismatch')
    for label in ('source', 'candidate'):
        obj = report[label]
        need(len(obj['records']) == 204 and obj['final_public_rank'] == 1501 and obj['zero_rows'] == 7 and
             obj['other_rank_definition'] == 'rank of all other live rows immediately before CLEAR', 'fresh rank/census')
    result = {'status': 'PASS_FRESH_204_CERTIFICATE_REPLAY', 'source_count': 204, 'candidate_count': 204,
              'checker_sha256': sha(checker), 'fresh_report_sha256': sha(fresh / 'certificate.json'),
              'prepared_status_sha256': sha(a.prepared / 'status.json'),
              'scope': 'Independent exact live-row/public-provider/remaining-live-rank checker; physical erasure and numerical U remain assumptions.'}
    (a.out / 'status.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
