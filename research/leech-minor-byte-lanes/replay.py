#!/usr/bin/env python3
"""Opt-in, source-pinned replay of all nine historical affine-vector screens."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from lanes import lane_rows, require

SOURCE = 'scripts/experiments/affine_vector_screens.py'
OLD = '''    packed=[];digest=sha256()
    for i in independent_rows:
        sparse=[(a,x) for a,x in enumerate(sample[i]) if x]
        row=sum(1<<j for j,v in enumerate(sample)
                if i==j or sum(x*v[a] for a,x in sparse)==shift)
        packed.append(row);digest.update(row.to_bytes((len(sample)+7)//8,'little'))
'''
NEW = '''    packed=lane_rows(sample, independent_rows, shift);digest=sha256()
    for row in packed:
        digest.update(row.to_bytes((len(sample)+7)//8,'little'))
'''


def check_pins(root=ROOT):
    pins = json.loads((HERE / 'PINS.json').read_text())
    require(pins['files'], 'Empty source pins')
    for name, expected in pins['files'].items():
        path = (root / name).resolve()
        require(path.is_relative_to(root.resolve()) and path.is_file(),
                'Missing or escaping pinned file: ' + name)
        require(sha256(path.read_bytes()).hexdigest() == expected,
                'Pinned file changed: ' + name)
    return pins


def load(mode):
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    require(mode in ('baseline', 'lanes'), 'Invalid replay mode')
    check_pins()
    sys.path.insert(0, str(ROOT / 'scripts'))
    import audit_affine_vectors as audit
    from experiments import affine_vector_screens as original
    source = (ROOT / SOURCE).read_text()
    require(source.count(OLD) == 1, 'Pinned row block is not unique')
    if mode == 'lanes':
        source = source.replace(OLD, NEW)
    # Separate globals/caches: only the pinned row block differs. All original
    # admission, inventory, rational span, binary rank and receipt code remains.
    namespace = dict(vars(original), lane_rows=lane_rows)
    exec(compile(source, str(ROOT / SOURCE), 'exec'), namespace)
    return audit, namespace, sha256(source.encode()).hexdigest()


def certificate(mode, observe=None):
    audit, namespace, adapted_sha = load(mode)
    if observe is not None:
        rank = namespace['rank_of_rows']

        def recording_rank(rows):
            observe(tuple(rows))
            return rank(rows)

        namespace['rank_of_rows'] = recording_rank
    before = audit.leech_minor
    try:
        audit.leech_minor = namespace['leech_minor']
        result = audit.certificate()
    finally:
        audit.leech_minor = before
    from prepare_layers import serializable
    payload = (json.dumps(serializable(result), indent=2, sort_keys=True) + '\n').encode()
    expected = (ROOT / 'certificates/affine-vector-screens.json').read_bytes()
    require(payload == expected, 'Complete historical certificate differs')
    return payload, adapted_sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('baseline', 'lanes'), default='lanes')
    parser.add_argument('--output', type=Path, required=True,
                        help='Fresh path for the complete original certificate')
    args = parser.parse_args()
    require(not args.output.exists(), 'Output already exists')
    payload, adapted_sha = certificate(args.mode)
    with args.output.open('xb') as out:
        out.write(payload)
    print(json.dumps({'status': 'PASS_AFFINE_VECTOR_REPLAY', 'mode': args.mode,
                      'certificate_sha256': sha256(payload).hexdigest(),
                      'executed_geometry_sha256': adapted_sha}, sort_keys=True))


if __name__ == '__main__':
    main()
