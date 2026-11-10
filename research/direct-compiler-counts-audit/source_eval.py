#!/usr/bin/env python3
"""Execute only the pinned finite compile_counts consumer as the program under test.

ToikY with substantial OpenAI Codex assistance. Apache-2.0.
The source's verify/authenticate/finite_flows/native functions are not called.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PINS_SHA = 'f2031ec3b25d187bd924037b63e46943c4d19ece39175e2c58327d7a4f0e59ed'
CASES_SHA = 'ce0152497423d200f0e2c8b83b9efce992c95c92743e238cd5a060306bf329a0'
NAMES = ('widths', 'leaves', 'units', 'columns', 'slots')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode()


def authenticate():
    raw = (HERE / 'SOURCE-PINS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS_SHA, 'source manifest changed')
    records = json.loads(raw)['objects']
    need(len(records) == 6, 'six source objects required')
    for record in records:
        path = HERE / record['local_path']
        need(path.is_relative_to(HERE) and not path.is_symlink(), 'regular local source required')
        data = path.read_bytes()
        need(len(data) == record['bytes'] and hashlib.sha256(data).hexdigest() == record['sha256'],
             'source bytes changed: ' + record['local_path'])
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        need(blob == record['git_blob'], 'source Git blob changed')
    cases = (HERE / 'CASES.json').read_bytes()
    need(hashlib.sha256(cases).hexdigest() == CASES_SHA, 'case data changed')
    return json.loads(cases)['cases']


def load_source(compiler_text=None, flow_text=None):
    """Full module bodies, isolated file layout; main/verify are never invoked."""
    compiler_text = compiler_text if compiler_text is not None else (HERE / 'inputs/verify.py.txt').read_text()
    flow_text = flow_text if flow_text is not None else (HERE / 'inputs/flow.py.txt').read_text()
    with tempfile.TemporaryDirectory(prefix='direct-counts-source-') as directory:
        root = Path(directory)
        (root / 'flow.py').write_text(flow_text)
        namespace = {'__file__': str(root / 'verify.py'), '__name__': 'pinned_finite_consumer'}
        exec(compile(compiler_text, str(root / 'verify.py'), 'exec'), namespace)
    return namespace


def evaluate_case(namespace, case, force_unit_replication=False):
    targets, paid = dict(case['targets']), dict(case['paid'])
    summary, vectors = namespace['compile_counts'](
        targets, paid, case['maximum'], force_unit_replication=force_unit_replication)
    need(len(vectors) == 5, 'all five vectors required')
    result = {}
    for name, values in zip(NAMES, vectors):
        need(len(values) == case['maximum'] + 1
             and all(type(x) is int and x >= 0 for x in values), 'complete nonnegative exact vector')
        result[name] = [format(x, 'x') for x in values]
    return {'name': case['name'], 'maximum': case['maximum'], 'vectors': result, 'summary': summary}


def packet():
    cases = authenticate()
    namespace = load_source()
    return canonical({'schema': 'direct-compiler-counts-audit/1',
                      'cases': [evaluate_case(namespace, case) for case in cases]})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--emit', action='store_true', help='Emit the complete packet without reference validation.')
    group.add_argument('--reference', type=Path, help='Compare against exactly these complete canonical bytes.')
    args = parser.parse_args()
    raw = packet()
    if args.emit:
        sys.stdout.buffer.write(raw)
        return
    reference = args.reference if args.reference is not None else HERE / 'CERTIFICATE.json'
    need(reference.read_bytes() == raw, 'complete reference packet differs')
    print(json.dumps({'status': 'PASS_ACTUAL_DIRECT_COMPILER_COUNTS', 'bytes': len(raw),
                      'sha256': hashlib.sha256(raw).hexdigest(), 'cases': 4}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise SystemExit('FAIL_ACTUAL_DIRECT_COMPILER_COUNTS: ' + str(error))
