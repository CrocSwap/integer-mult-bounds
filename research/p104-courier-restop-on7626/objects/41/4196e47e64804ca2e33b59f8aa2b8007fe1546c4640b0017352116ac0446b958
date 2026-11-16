"""Materialize authenticated certificate inputs; fresh replay is the next stage."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--gate', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    root, gate = a.root.resolve(), a.gate.resolve()
    need(gate == root / 'compose7624_completion/run/case', 'wrong completed first gate')
    result = json.loads((gate / 'RESULT.json').read_bytes())
    control = json.loads((root / 'compose7624_completion/control/RESULT.json').read_bytes())
    need(result['status'] == 'PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U' and
         control['differential_case_completed'] is True and control['group_empty'] is True and
         control['returncode'] == 0, 'first gate not operationally complete')
    required = ('certificates/source-certificates.json', 'certificates/candidate-certificates.json',
                'certificates/certificate.json', 'certificates/status.json')
    for rel in required:
        need(rel in result['receipt_hashes'] and sha(gate / rel) == result['receipt_hashes'][rel],
             'first-gate certificate digest ' + rel)
    a.out.mkdir()
    copies = {'source-certificate.json': 'certificates/source-certificates.json',
              'certificate.json': 'certificates/candidate-certificates.json',
              'FIRST-GATE-CERTIFICATE-REPORT.json': 'certificates/certificate.json'}
    hashes = {}
    for dest, rel in copies.items():
        shutil.copyfile(gate / rel, a.out / dest)
        need(sha(a.out / dest) == sha(gate / rel), 'prepared certificate copy mismatch')
        hashes[dest] = sha(a.out / dest)
    for name in ('source-certificate.json', 'certificate.json'):
        obj = json.loads((a.out / name).read_bytes())
        need(obj['summary']['clears'] == obj['summary']['certified'] == len(obj['clears']) == 204,
             'prepared certificate census')
    report = {'status': 'PREPARED_CERTIFICATES_NOT_REPLAYED_IN_FULL_JOB', 'hashes': hashes,
              'first_gate_result_sha256': sha(gate / 'RESULT.json'),
              'scope': 'Input custody only; fresh independent replay follows in certificate-verifier stage.'}
    (a.out / 'status.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(report, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
