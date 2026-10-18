"""Replay four explicit words and the exact global-budget obstruction (stdlib)."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'research/complex-k492-owner-repair/'
VENDOR = BASE + 'vendor/multicold/vendor/pr558/vendor/pr552/'
# Pairwise transport bytes; k492 code/hpe_audit_and_transport.py ships integer rows.
AUDITOR = 'research/complex-sw4-frame8/local/hpe_audit_and_transport.py'
ROUTING = VENDOR + 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
DATA = VENDOR + 'complex-global/vendor531/inputs/data-base/work/complex-nine-native/DATA-PHASES.json'
EXACT = runpy.run_path(str(HERE/'exact.py'))
require = EXACT['require']


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def integers(mapping):
    return {int(r): n for r, n in mapping.items()}


def difference(new, old):
    return {r: new.get(r, 0)-old.get(r, 0) for r in sorted(set(new) | set(old))
            if new.get(r, 0) != old.get(r, 0)}


def check_sources():
    pins = read(HERE/'SOURCE-PINS.json')
    require(set(pins['files']) == {AUDITOR, ROUTING, DATA, BASE+'data/SPEC.json',
                                  BASE+'data/PLAN.json'}, "source pin inventory")
    for path, digest in pins['files'].items():
        require(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest,
                f"source pin mismatch: {path}")
    require(hashlib.sha256((HERE/'CODED-CELL.json').read_bytes()).hexdigest()
            == pins['coded_cell_source']['sha256'], "coded-cell source pin")
    names = {f'{variant}-{pid}' for variant in ('positive', 'negative') for pid in ('ck', 'jp8')}
    require(set(pins['word_content_sha256']) == names, "candidate inventory")
    for name, digest in pins['word_content_sha256'].items():
        payload = gzip.decompress((HERE/'words'/f'{name}.json.gz').read_bytes())
        require(hashlib.sha256(payload).hexdigest() == digest, f"word content pin: {name}")
    require(set(read(HERE/'NATIVE-EXPECTED.json')) == names, "expected receipt inventory")
    return pins


def model_from_receipts(receipts):
    spec = read(ROOT/BASE/'data/SPEC.json')
    plan = read(ROOT/BASE/'data/PLAN.json')
    data = read(ROOT/DATA)
    expected = spec['expected']
    dispatch = spec['dispatch']
    counts = Counter(pid for _, _, pid in dispatch)
    require(counts == expected['provider_counts'] == {'ck': 8, 'jp8': 64}, "dispatch counts")
    require([[c['stage'], c['replica'], c['provider']] for c in plan['provider_calls']]
            == dispatch, "plan dispatch")
    require(plan['order'] == spec['call_order'] == [row[:2] for row in dispatch], "call order")
    require(plan['M'] == data['m'] == 73 and plan['T'] == 8 and plan['L'] == 9,
            "pinned geometry")
    require(len(dispatch) == plan['T']*plan['L'] and data['ports'] == 112,
            "call or port count")
    capacities = Counter()
    for rank, times in plan['windows'].values():
        capacities[rank] += data['ports']
    native_capacities = Counter()
    require(len(data['recipes']) == data['ports'], "data recipe count")
    for recipe in data['recipes']:
        for child in recipe['idle_children']:
            native_capacities[child['rank']] += plan['T']
    # The data recipe also records two empty children per port/replica.
    # They cannot host any positive-width helper and contribute zero moment.
    require(native_capacities.pop(0) == 2*data['ports']*plan['T'], "zero-capacity children")
    require(capacities == native_capacities == {8: 5376, 16: 3584, 32: 3584, 48: 3584},
            "window/data capacity inventories disagree")

    local, widths = Counter(), Counter()
    per_call = Counter(w for row in plan['per_call_widths'] for w in row['widths'])
    for pid, count in counts.items():
        source = spec['providers'][pid]
        profile, inventory = integers(source['expected_profile']), integers(source['inventory'])
        registry = plan['provider_registry'][pid]
        require(integers(registry['actual_paid_profile']) == profile, f"baseline profile: {pid}")
        require(Counter(registry['widths']) == inventory, f"baseline inventory: {pid}")
        local.update({r: n*count for r, n in profile.items()})
        widths.update({w: n*count for w, n in inventory.items()})
    require(widths == per_call, "per-call baseline helper inventory")
    global_profile = integers(expected['global_profile'])
    idle = integers(expected['idle_remainder_profile'])
    require(local + Counter(idle) == global_profile == integers(plan['profile']),
            "baseline local/global accounting")
    require(sum(c*n for c, n in capacities.items())-sum(w*n for w, n in widths.items())
            == sum(r*n for r, n in idle.items()), "baseline idle mass")

    profile_deltas, width_deltas = {}, {}
    for variant in ('positive', 'negative'):
        profiles, inventories = [], []
        for pid in sorted(counts):
            name = f'{variant}-{pid}'
            receipt = receipts[name]
            word = read(HERE/'words'/f'{name}.json.gz')
            profile = integers(receipt['local_profile'])
            inventory = dict(Counter(receipt['widths']))
            require(profile == integers(word['report']['local_profile']), f"paid profile: {name}")
            require(inventory == integers(word['report']['width_inventory']), f"paid widths: {name}")
            require(len(receipt['widths']) == receipt['helpers'] == word['report']['R'],
                    f"helper count: {name}")
            require(receipt['live_columns_each_orientation'] == 224 + receipt['helpers'],
                    f"all-column replay: {name}")
            baseline = spec['providers'][pid]
            profiles.append(difference(profile, integers(baseline['expected_profile'])))
            inventories.append(difference(inventory, integers(baseline['inventory'])))
        require(profiles[0] == profiles[1] and inventories[0] == inventories[1],
                f"provider-independent deltas: {variant}")
        profile_deltas[variant], width_deltas[variant] = profiles[0], inventories[0]
    require(plan['live'] == expected['live'] == 7168 and plan['deficit'] == expected['deficit'],
            "live/deficit budget")
    require(sum(r*n for r, n in global_profile.items()) == expected['rank_mass']
            == plan['live']*plan['M']-plan['deficit'], "baseline rank mass")
    return {'endpoint': expected['complex_lower'], 'm': plan['M'], 'live': plan['live'],
            'calls': len(dispatch), 'rank_mass': expected['rank_mass'],
            'capacities': dict(capacities), 'widths': dict(widths), 'local': dict(local),
            'global': global_profile, 'profile_deltas': profile_deltas, 'width_deltas': width_deltas}


def run(out):
    pins = check_sources()
    environment = os.environ.copy()
    environment.pop('PYTHONOPTIMIZE', None)
    subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8', str(HERE/'native_worker.py'),
                    str(HERE), str(ROOT/AUDITOR), str(ROOT/ROUTING), str(out)],
                   check=True, env=environment)
    native = read(out/'NATIVE-RESULT.json')
    require(native['assertions_enabled'] is True, "native worker assertions disabled")
    for name, receipt in native['receipts'].items():
        require(receipt['input_content_sha256'] == pins['word_content_sha256'][name],
                f"audited word identity: {name}")
    model = model_from_receipts(native['receipts'])
    certificate = read(HERE/'EXACT-CERTIFICATE.json')
    exact = EXACT['verify'](model, certificate)
    controls = EXACT['controls'](model, certificate)
    summary = {
        'status': 'PASS_SCOPED_INTEGER_PACKING_OBSTRUCTION',
        'native_words': len(native['receipts']), 'native_controls_rejected': len(native['controls_rejected']),
        'exact_controls_rejected': len(controls), 'recompression_control': native['recompression_control'],
        'patterns': exact['patterns'], 'potential_inequalities': exact['potential_inequalities'],
        'mixtures': exact['mixtures'], 'minimum_margin_greater_than': exact['minimum_margin_greater_than'],
        'minimum_at': exact['minimum_at'], 'scope': 'Four explicit native words; fixed #626 geometry and dispatch. No global candidate admission or new exponent.'}
    (out/'RESULT.json').write_text(json.dumps({'summary': summary, 'model': model,
                                             'exact_controls': controls}, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='retain receipts in a new directory')
    args = parser.parse_args()
    if args.out is not None:
        out = args.out.resolve()
        out.mkdir(parents=True, exist_ok=False)
        run(out)
    else:
        with tempfile.TemporaryDirectory(prefix='coded-helper-screen-') as directory:
            run(Path(directory))
