"""Coordinator's actual pinned source invocation, not an independent model."""
from collections import Counter
from pathlib import Path


def inventories(case, raw_inventory):
    if case.get('inventory') == 'raw_p7':
        data = raw_inventory['strictification']
        return ({int(k): v for k, v in data['targets'].items()},
                {int(k): v for k, v in data['paid'].items()})
    return dict(case['targets']), dict(case['paid'])


def invoke(case, raw_inventory, source_text):
    namespace = {'__name__': '_authenticated_flow_under_test'}
    exec(compile(source_text, 'authenticated-canonical-flow.py', 'exec'), namespace)
    targets, paid = inventories(case, raw_inventory)
    actual = namespace['Flow'](targets, paid, case['n']).merged()
    mirror = Counter(actual['exits'])
    for rank, count in actual['sources'].items():
        mirror[case['n']-rank] += count
    actual['mirror'] = mirror
    for name in ('sources', 'exits', 'boundary_exits', 'mirror'):
        actual[name] = [[k, v] for k, v in sorted(actual[name].items()) if v]
    return actual


def build_cases(contract, raw_inventory):
    text = (Path(__file__).resolve().parent/'inputs/flow.py.txt').read_text()
    return {case['id']: invoke(case, raw_inventory, text) for case in contract['cases']}


# Shared coordinator-authored byte/CLI wrapper; not an independent math model.
def _run_cli():
    import argparse
    import hashlib
    import json
    from pathlib import Path
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description='Complete finite flow certificate')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--emit', type=Path)
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    contract_raw = (base / 'CONTRACT.json').read_bytes()
    if hashlib.sha256(contract_raw).hexdigest() != '4fc49527e728be80abaa4c5f7f0bd62da30afaea70b71be2c77b8457136da1f1':
        raise ValueError('contract byte drift')
    pins_raw = (base / 'SOURCE-PINS.json').read_bytes()
    if hashlib.sha256(pins_raw).hexdigest() != 'a533c5c9513470c2294c3b6217caf052eca63ce568a075d35e5f6c2251358812':
        raise ValueError('source manifest byte drift')
    for row in json.loads(pins_raw)['objects']:
        data = (base / row['local_path']).read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256'] or blob != row['git_blob']:
            raise ValueError('source byte drift: '+row['local_path'])
    # These fixed mathematical inputs cannot be replaced by changing pin metadata.
    if hashlib.sha256((base/'inputs/flow.py.txt').read_bytes()).hexdigest() != '460f0b0262d7b6880973f46240b3fff1e9f04601fa1d658dda18688b1e26575a':
        raise ValueError('canonical flow drift')
    raw = (base/'inputs/p7-RESULT.json.txt').read_bytes()
    if hashlib.sha256(raw).hexdigest() != '9b814be97e3b45fcc28eafa8a65694897a7387f71a14d44796c6aadf303d7fab':
        raise ValueError('raw inventory drift')
    contract, inventory = json.loads(contract_raw), json.loads(raw)
    if 'build_packet' in globals():
        packet = build_packet(contract, inventory)
    else:
        packet = {'schema': contract['schema'], 'cases': build_cases(contract, inventory)}
    encoded = json.dumps(packet, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')+b'\n'
    if args.emit is not None:
        if args.emit.exists():
            raise ValueError('refusing to replace first packet')
        args.emit.write_bytes(encoded)
    else:
        reference = base / globals().get('REFERENCE_FILE', 'FIRST.json')
        if encoded != reference.read_bytes():
            raise ValueError('complete packet mismatch')
    print('PASS_COMPLETE_FINITE_FLOW', hashlib.sha256(encoded).hexdigest(), len(encoded))


if __name__ == '__main__':
    try:
        _run_cli()
    except (ValueError, OSError) as error:
        import sys
        print('FAIL_COMPLETE_FINITE_FLOW', error, file=sys.stderr)
        raise SystemExit(1)
