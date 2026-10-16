"""Reproduce the unchanged-auditor acceptance and native domain protection."""
import argparse
import contextlib
import copy
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from binding import HERE, ROOT, AUDITOR, NATIVE, ROUTING, CLIFFORD, authenticate, load, need
from guard import violations
from native_witness import witness, full_column

FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]


def payload(word):
    return json.dumps(word, sort_keys=True, separators=(',', ':')).encode()


def mutant(word, target):
    changed = copy.deepcopy(word)
    n = 2*word['report']['v'] + word['report']['R']
    changed['helper_final'][str(target-n)] = FULL
    changed['report']['local_profile']['1'] += 1
    return changed


def audit(module, word, directory):
    path, out = directory/'word.json.gz', directory/'audit.json'
    path.write_bytes(gzip.compress(payload(word), mtime=0))
    with contextlib.redirect_stdout(io.StringIO()):
        module.run(path, out, ROOT)
    result = json.loads(out.read_text())
    keys = ('status', 'local_profile', 'width_inventory', 'checked_columns',
            'compensation_gates', 'entering', 'lowends', 'coldends')
    return {key: result[key] for key in keys}


def native_run(word, directory, success):
    path = directory/'native-word.json.gz'
    path.write_bytes(gzip.compress(payload(word), mtime=0))
    destination = directory/('native-positive' if success else 'native-negative')
    # The pinned native auditor uses assertions. Always execute it unoptimized.
    env = os.environ.copy()
    env.pop('PYTHONOPTIMIZE', None)
    result = subprocess.run([sys.executable, '-I', '-B', str(ROOT/NATIVE),
                             '--raw', str(path), '--routing', str(ROOT/ROUTING),
                             '--out', str(destination)], env=env, text=True,
                            capture_output=True, timeout=120)
    if success:
        need(result.returncode == 0 and 'PASS_CHANGED_WORD_ALL_COLUMNS_AND_NATIVE_FRAMES'
             in result.stdout, 'native positive: '+result.stderr)
        report = json.loads((destination/'SCALAR-FRAME-AUDIT.json').read_text())
        return {key: report[key] for key in ('status', 'live_columns_each_orientation',
                                             'local_profile', 'local_rank_mass')}
    need(result.returncode != 0 and 'assert all(2*v <= r < n for r in helper_final)'
         in result.stderr and 'AssertionError' in result.stderr, 'native exact rejection')
    need(not destination.exists(), 'rejected native word produced an output')
    return 'REJECT_HELPER_INDEX_BEFORE_NATIVE_OUTPUT'


def result():
    authenticate()
    auditor = load(ROOT/AUDITOR, 'retained_independent_auditor')
    cut = load(HERE/'source/cut_guard.py', 'retained_cut_guard')
    clifford = load(ROOT/CLIFFORD, 'retained_clifford')
    base = json.loads(gzip.decompress((HERE/'inputs/BASE-WORD.json.gz').read_bytes()))
    v, n = base['report']['v'], 2*base['report']['v']+base['report']['R']
    need((v, n) == (112, 704), 'source extent')
    need(not violations(base) and not cut.violations(base), 'positive guards')
    positive_words = []
    for row in json.loads((HERE/'inputs/GENUINE-WORDS.json').read_text())['words']:
        path = (ROOT if row['path'].startswith('research/') else HERE)/row['path']
        word = json.loads(gzip.decompress(path.read_bytes()))
        need(not violations(word), 'genuine endpoint indices: '+row['path'])
        positive_words.append(row['path'])
    full, full_den = clifford.canonical_frame(9, FULL).zero_state()
    independent = full_column()
    need(all((a*512, b*512) == (c*(1 << full_den), d*(1 << full_den))
             for (a, b), (c, d) in zip(full, independent)), 'independent full frame column')
    with tempfile.TemporaryDirectory(prefix='endpoint-index-') as directory:
        directory = Path(directory)
        baseline = audit(auditor, base, directory)
        native_positive = native_run(base, directory, True)
        accepted, native_witnesses = [], []
        for t in range(v, 2*v):
            changed = mutant(base, t)
            need(not cut.violations(changed), 'distinct from the cut guard')
            bad = violations(changed)
            need(len(bad) == 1 and bad[0]['key'] == str(t-n), 'new guard rejects actual alias')
            receipt = audit(auditor, changed, directory)
            need(receipt['local_profile']['1'] == baseline['local_profile']['1']+1
                 and receipt['width_inventory'] == baseline['width_inventory']
                 and receipt['checked_columns'] == n, 'exact accepted profile delta')
            port = base['ports'][t-v]
            hp = auditor.basis([x for x in range(1, 512) if (x & port).bit_count() % 2 == 0])
            actual, den = clifford.canonical_frame(9, hp).zero_state()
            proof = witness(port)
            need(actual[proof['row']] == (0, 0) and full[proof['row']] != (0, 0)
                 and sum(x != (0, 0) for x in actual) == 256, 'retained native support witness')
            accepted.append({'target': t, 'key': str(t-n),
                             'word_content_sha256': hashlib.sha256(payload(changed)).hexdigest()})
            native_witnesses.append({'target': t, **proof})
        representative = mutant(base, v)
        native_rejection = native_run(representative, directory, False)
        positive_key = copy.deepcopy(representative)
        positive_key['helper_final'][str(v)] = positive_key['helper_final'].pop(str(v-n))
        try:
            audit(auditor, positive_key, directory)
        except RuntimeError as error:
            need(str(error) == 'pre-wrapper touch of residual helper', 'positive-key rejection site')
        else:
            raise ValueError('positive target key accepted')
        no_price = mutant(base, v)
        no_price['report']['local_profile']['1'] -= 1
        try:
            audit(auditor, no_price, directory)
        except RuntimeError as error:
            need(str(error) == 'paid profile mismatch', 'invoice control rejection site')
        else:
            raise ValueError('missing invoice change accepted')
    valid = next(iter(base['helper_final']))
    cases = [str(-n-1), str(n), str(n+100), '0', str(v), '0'+valid, '+'+valid, ' '+valid]
    for key in cases:
        changed = copy.deepcopy(base)
        changed['helper_final'][key] = FULL
        need(bool(violations(changed)), 'index guard control: '+key)
    need(not violations({'report': {'v': v, 'R': n-2*v}}), 'absent optional map')
    return {'schema_version': 1, 'status': 'CONFIRMED_INDEPENDENT_AUDITOR_DOMAIN_GAP',
            'base': baseline, 'genuine_words': len(positive_words),
            'genuine_path_digest': hashlib.sha256('\n'.join(positive_words).encode()).hexdigest(),
            'accepted_target_aliases': accepted, 'target_alias_count': len(accepted),
            'cut_guard_accepts_all_aliases': True, 'native_positive': native_positive,
            'native_rejection': native_rejection, 'native_frame_witnesses': native_witnesses,
            'positive_target_key_old_rejection': 'pre-wrapper touch of residual helper',
            'missing_invoice_old_rejection': 'paid profile mismatch',
            'additional_index_controls': cases,
            'scope': 'Helper endpoint index domain only; native auditor already rejects; no selected-source bug or kappa change.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', type=Path)
    args = ap.parse_args()
    actual = result()
    if args.write:
        with args.write.open('x', encoding='utf-8', newline='\n') as output:
            output.write(json.dumps(actual, indent=2, sort_keys=True)+'\n')
    else:
        need(json.dumps(actual, sort_keys=True) ==
             json.dumps(json.loads((HERE/'RESULT.json').read_text()), sort_keys=True), 'receipt mismatch')
    print('PASS_HELPER_ENDPOINT_INDICES aliases=112 genuine=146 native_reject=1')


if __name__ == '__main__':
    main()
