"""Bind PR2297's literal port dimensions to its conditional coverage screen."""
import argparse
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from model import coverage, dimensions, endpoint_witness, need, require_uniform

PRODUCER = 'research/five-plane-port-p112-seed1f7fdfe4'
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
TEMPLATE = 'candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz'
ENGINE = 'research/complex-local-word-ceiling/ceiling.py'


def authenticate():
    for manifest, base in [('SOURCES.json', ROOT), ('VENDOR.json', HERE)]:
        for row in json.loads((HERE/manifest).read_text(encoding='utf-8'))['files']:
            if row.get('usage', 'input') != 'input':
                continue
            raw = (base/row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source hash: '+row['path'])
            need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                 == row['git_blob'], 'source blob: '+row['path'])


def producer_replay():
    # The original source runs at its original relative path, with unmodified
    # bytes and root inputs, in a Git-free export. No code/global patching.
    with tempfile.TemporaryDirectory(prefix='mixed-port-original-') as tmp:
        root = Path(tmp)
        package = root/PRODUCER
        shutil.copytree(HERE/'predecessor', package)
        manifest = json.loads((package/'SOURCES.json').read_text(encoding='utf-8'))
        for row in manifest['files']:
            if row['usage'] == 'input':
                dest = root/row['path']
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/row['path'], dest)
        cp = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py')],
                            cwd=root, text=True, encoding='utf-8', capture_output=True, timeout=180)
        need(cp.returncode == 0 and 'PASS_P112_FIVE_PLANE_PORT_DECODER' in cp.stdout,
             'original replay: '+cp.stdout+cp.stderr)
        return cp.stdout.strip()


def load_engine():
    spec = importlib.util.spec_from_file_location('retained_ceiling', ROOT/ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def price(engine, profile, centre, unpaid):
    moment = engine.relax(profile, 73, 896, 9, centre, Q(1, 99), unpaid=unpaid)
    cap = engine.ceiling(profile, 73, 896, 9, centre, unpaid=unpaid)
    lo, hi = 0, 1000
    while hi-lo > 1:
        extra = (lo+hi)//2
        trial = profile.copy()
        trial[1] += extra
        a, b = engine.relax(trial, 73, 896, 9, centre+extra, Q(1, 99), unpaid=unpaid)
        if b < 1:
            lo = extra
        else:
            need(a > 1, 'overhead enclosure inconclusive')
            hi = extra
    thresholds = []
    for extra in (lo, hi):
        trial = profile.copy()
        trial[1] += extra
        interval = engine.relax(trial, 73, 896, 9, centre+extra, Q(1, 99), unpaid=unpaid)
        need(interval[1] < 1 if extra == lo else interval[0] > 1, 'sharp overhead threshold')
        thresholds.append({'extra_rank_one_units': extra, 'total_charge': centre+extra,
                           'moment': list(map(str, interval))})
    return {'unpaid': str(unpaid), 'model': {k: str(v) for k, v in
            engine.model(profile, 73, 896, 9, centre, unpaid=unpaid).items()},
            'moment': list(map(str, moment)), 'ceiling': list(map(str, cap)),
            'overhead': thresholds}


def compute():
    authenticate()
    original = producer_replay()
    with tarfile.open(ROOT/ARCHIVE, 'r:gz') as tf:
        raw = tf.extractfile(MEMBER).read()
        template_raw = tf.extractfile(TEMPLATE).read()
    source = json.loads(raw)
    template_payload = gzip.decompress(template_raw)
    template = json.loads(template_payload)
    need(source['m'] == template['m'] == 73 and source['ports'] == 112, 'source dimensions')
    replicas = template['replica_lift']['replicas']
    recipe = template['recipe']
    local_stages = [x['stage'] for x in recipe if x['kind'] == 'local']
    need(replicas == 16 and local_stages == list(range(9))
         and recipe[-1] == {'kind': 'terminal', 'pairs': 4}, 'selected normalization')
    need(sorted((c['replica'], c['stage']) for c in template['calls']) ==
         [(replica, stage) for replica in range(16) for stage in range(9)]
         and template['live'] == 16*896, 'actual call and family counts')
    recipes = sorted(source['recipes'], key=lambda r: r['port'])
    need([r['port'] for r in recipes] == list(range(112)), 'selected port order')
    labels = [r['q'] for r in recipes]
    record = json.loads((HERE/'predecessor/CANDIDATE.json').read_text(encoding='utf-8'))
    candidate = record['candidate']
    blocks = candidate['groups']+[candidate['residual']]
    need(candidate['blocks'] == blocks, 'same blocks in cover and decoder')
    dims = dimensions(blocks, labels)
    ledger = coverage(dims)
    need(dims.count(5) == 110 and dims.count(2) == 2 and sum(dims) == 554,
         'actual mixed dimensions')
    need(ledger['weighted_unpaid'] == Q(277, 56) and ledger['families'] == 896,
         'weighted coverage')
    uniform = coverage([5]*112)
    delta = ledger['pending_per_call']-uniform['pending_per_call']
    need(delta == Q(16, 3), 'missing paid mass')
    engine = load_engine()
    profile = {int(k): v for k, v in candidate['local_profile'].items()}
    centre = candidate['copy_charge']
    need(centre == 118 and sum(k*v for k,v in profile.items()) == 5640, 'retained profile')
    before = price(engine, profile, centre, Q(5))
    after = price(engine, profile, centre, ledger['weighted_unpaid'])
    stored = candidate['moment_screen_u5']
    need(before['moment'] == [stored['moment_lower'], stored['moment_upper']]
         and before['ceiling'] == [stored['ceiling_lower'], stored['ceiling_upper']],
         'original exact interval equality')
    need(before['overhead'][0]['extra_rank_one_units'] == 157
         and after['overhead'][0]['extra_rank_one_units'] == 152, 'allowance correction')
    need(Q(after['moment'][1]) < 1, 'mixed target still passes')
    child_lo, child_hi = engine.child_cost(51, 73, Q(1, 99))
    uplift = (delta/51*child_lo/Q(896,9), delta/51*child_hi/Q(896,9))
    need(Q(after['moment'][0]) <= Q(before['moment'][1])+uplift[1]
         and Q(before['moment'][0])+uplift[0] <= Q(after['moment'][1])
         and Q(after['moment'][0])-Q(before['moment'][1]) > 0, 'positive idle correction')
    native = endpoint_witness(candidate['residual'], labels)
    controls = []
    def rejects(name, action):
        try:
            action()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('accepted control: '+name)
    rejects('uniform-five-from-literal-planes', lambda: require_uniform(dims, 5))
    require_uniform([5]*112, 5)  # Honest homogeneous input, not a realization.
    omitted = copy.deepcopy(blocks[:-1])
    rejects('omit-residual-ports', lambda: dimensions(omitted, labels))
    repeated = copy.deepcopy(blocks)
    repeated[-1][0] = repeated[0][0]
    rejects('duplicate-port-incidence', lambda: dimensions(repeated, labels))
    wrong = copy.deepcopy(blocks)
    i,j = next((i,j) for i in range(112) for j in range(i+1,112)
               if (labels[i]&labels[j]).bit_count()%2)
    wrong_labels = labels.copy()
    wrong_labels[wrong[0][0]], wrong_labels[wrong[0][1]] = labels[i], labels[j]
    rejects('nonorthogonal-declared-block', lambda: dimensions(wrong, wrong_labels))
    old_allowance = profile.copy()
    old_allowance[1] += 157
    need(engine.relax(old_allowance,73,896,9,275,Q(1,99),unpaid=ledger['weighted_unpaid'])[0] > 1,
         'old extra allowance must fail under mixed contract')
    controls.append('old-157-unit-allowance-rejected')
    controls.append('literal-native-endpoint-not-uniform-five')
    return {'status': 'UNIFORM_FIVE_PREMISE_NOT_SUPPLIED_BY_LITERAL_PORTS',
            'original_verifier': original, 'selected_member_sha256': hashlib.sha256(raw).hexdigest(),
            'selected_template_member_sha256': hashlib.sha256(template_raw).hexdigest(),
            'selected_template_payload_sha256': hashlib.sha256(template_payload).hexdigest(),
            'selected_normalization': {'replicas': replicas, 'calls': len(template['calls']),
                                       'live_families': template['live'], 'pairs': 4, 'stages': 9},
            'port_dimensions': dims, 'port_dimension_sum': sum(dims),
            'coverage': {k:str(v) for k,v in ledger.items()},
            'uniform_pending_per_call': str(uniform['pending_per_call']),
            'missing_paid_mass_per_call': str(delta), 'original_uniform_screen': before,
            'moment_uplift_interval': list(map(str, uplift)),
            'literal_mixed_screen': after, 'native_endpoint_witness': native,
            'provisional_translation_count': 23,
            'remaining_after_provisional_translations': 129,
            'negative_controls': controls,
            'scope': 'Conditional mixed-port planning law; not a native supplier admission or disproof of a separately completed uniform-five contract.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', type=Path)
    args = ap.parse_args()
    observed = compute()
    if args.write:
        with args.write.open('x', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(observed, indent=2, sort_keys=True)+'\n')
    else:
        expected = json.loads((HERE/'RESULT.json').read_text(encoding='utf-8'))
        need(json.dumps(observed, sort_keys=True) == json.dumps(expected, sort_keys=True),
             'typed complete receipt mismatch')
    print('PASS_MIXED_PORT_COVERAGE ports=112 unpaid=277/56 idle_delta=16/3 allowance=152 controls=6')


if __name__ == '__main__':
    main()
