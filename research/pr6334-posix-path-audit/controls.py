#!/usr/bin/env python3
"""Independent rejection controls for the scoped PR6334 POSIX audit.

Hao Yan (@FanPUYen), with substantial OpenAI Codex assistance. Apache-2.0.
These controls test the audit's acceptance boundary, not the theorem.
"""
import copy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reject(call, message):
    try:
        call()
    except ValueError as exc:
        require(str(exc) == message,
                'control failed for an unrelated reason: ' + str(exc))
    else:
        raise ValueError('invalid evidence was accepted: ' + message)


def main():
    path = HERE / 'verify.py'
    spec = importlib.util.spec_from_file_location('pr6334_audit_under_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    files = module.source_bytes()
    source_controls = []
    with tempfile.TemporaryDirectory(prefix='pr6334-rejection-') as directory:
        root = Path(directory)
        for name, raw in files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        require(module.source_bytes(root) == files, 'valid source export rejected')
        for name, raw in files.items():
            target = root / name
            target.write_bytes(raw + b'\n')
            reject(lambda: module.source_bytes(root), 'source hash mismatch: ' + name)
            source_controls.append(name)
            target.write_bytes(raw)

    # This report oracle is declared here, independently of the producer.
    head = 'a' * 40
    missing = ['research/line\r\nbreak/README.md',
               'research/line\rbreak/README.md']
    report = {'coverage': {'local': {
        'head': head, 'head_records': 5, 'records': 3,
        'unsearched_head_paths': missing, 'complete_head_inventory': False}},
        'matches_total': 3, 'matches': [{}],
        'warnings': ['local: 2 HEAD note paths were not searched']}
    module.check_report(report, head, missing, 3, 'pr6334')
    mutations = [
        ('head', 'b' * 40, 'HEAD binding changed'),
        ('head_records', 3, 'unexpected HEAD path count'),
        ('unsearched_head_paths', [], 'wrong missing paths'),
        ('complete_head_inventory', True, 'incorrect completeness flag'),
        ('records', 4, 'wrong searched record count'),
    ]
    report_controls = []
    for field, value, message in mutations:
        bad = copy.deepcopy(report)
        bad['coverage']['local'][field] = value
        reject(lambda: module.check_report(bad, head, missing, 3, 'pr6334'), message)
        report_controls.append(field)
    for field, value, message in [
        ('matches_total', 2, 'search lost a materialized note'),
        ('matches', [], '--limit did not limit displayed results'),
        ('warnings', [], 'missing coverage warning'),
    ]:
        bad = copy.deepcopy(report)
        bad[field] = value
        reject(lambda: module.check_report(bad, head, missing, 3, 'pr6334'), message)
        report_controls.append(field)
    print(json.dumps({
        'status': 'PASS_PR6334_AUDIT_REJECTION_CONTROLS',
        'optimized': bool(sys.flags.optimize),
        'verifier_sha256': sha256(path.read_bytes()).hexdigest(),
        'positive_controls': ['valid_source_export', 'valid_candidate_report'],
        'source_corruptions_rejected': source_controls,
        'report_corruptions_rejected': report_controls,
        'scope': 'Audit source-byte and report acceptance only; no mathematical proof.'
    }, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        print(json.dumps({'status': 'FAIL_PR6334_AUDIT_REJECTION_CONTROLS',
                          'error': str(exc)}), file=sys.stderr)
        raise SystemExit(1)
