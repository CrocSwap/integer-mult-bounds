#!/usr/bin/env python3
"""Offline source-bound reproduction. No stored PASS result is accepted without execution."""
from pathlib import Path, PurePosixPath
import argparse, concurrent.futures, gzip, hashlib, json, os, shutil, struct, subprocess, sys, time, zipfile
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent

def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def need(condition, message):
    if not condition:
        raise RuntimeError(message)

def normalize(x):
    if isinstance(x, dict):
        return {k: normalize(v) for k, v in x.items() if k not in ('seconds', 'local_scalar_stream', 'containment_pairs_checked')}  # the last: a memo-cache miss counter, compiler-dependent (this package)
    if isinstance(x, list):
        return [normalize(v) for v in x]
    return x

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--cxx', default='g++')
    ap.add_argument('--boost-include', type=Path)
    ap.add_argument('--snapshots-only', action='store_true')
    args = ap.parse_args()
    need(sys.version_info >= (3, 11), 'Python 3.11+ required')
    need(sys.byteorder == 'little', 'native six-int transcript requires little-endian host')
    out = args.output.resolve()
    need(out != HERE and HERE not in out.parents, 'output must be outside package')
    need(not out.exists(), 'choose a fresh output directory')
    manifest = load(HERE / 'MANIFEST.json')['files']
    actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and p.name != 'MANIFEST.json'}
    # Upstream manifest resides inside the archive, so there is only one outer manifest.
    need(actual == set(manifest), 'unexpected or missing package file')
    for name, expected in manifest.items():
        need(digest(HERE / name) == expected, 'package hash mismatch: ' + name)
    out.mkdir(parents=True)
    for part in ('logs', 'bin', 'lead', 'compiler', 'review', 'temporal/CURRENT249-EXPORT', 'upstream'):  # plateau/ is created by the 02c stage
        (out / part).mkdir(parents=True)
    start = time.monotonic()
    def run(label, cmd):
        print(label, flush=True)
        with (out / 'logs' / (label + '.log')).open('w', encoding='utf-8') as log:
            result = subprocess.run([str(s) for s in cmd], cwd=out, stdout=log, stderr=subprocess.STDOUT)
        need(result.returncode == 0, label + ' failed; inspect logs/' + label + '.log')
    members = load(HERE / 'vendor/PR249-SOURCE-MANIFEST.json')['files']
    with zipfile.ZipFile(HERE / 'vendor/pr249-source.zip') as z:
        need(len(z.namelist()) == len(members) and set(z.namelist()) == set(members), 'source archive membership')
        for info in z.infolist():
            name = PurePosixPath(info.filename)
            need(not name.is_absolute() and '..' not in name.parts and '\\' not in info.filename and ':' not in info.filename, 'unsafe source archive path')
            data = z.read(info)
            need(hashlib.sha256(data).hexdigest() == members[info.filename], 'upstream hash: ' + info.filename)
            target = out / 'upstream' / info.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    upstream_manifest = load(out / 'upstream/MANIFEST.json')['files']
    for name, h in upstream_manifest.items():
        need(members.get(name) == h, 'upstream own manifest mismatch: ' + name)
    X = out / 'temporal/CURRENT249-EXPORT'
    snapshots = load(HERE / 'inputs/SNAPSHOTS.json')
    for name, h in snapshots.items():
        data = gzip.decompress((HERE / 'inputs' / (name + '.gz')).read_bytes())
        need(hashlib.sha256(data).hexdigest() == h, 'snapshot hash: ' + name)
        (X / name).write_bytes(data)
    candidates = out / 'candidates.json'
    candidates.write_bytes(gzip.decompress((HERE / 'inputs/candidates.json.gz').read_bytes()))
    if not args.snapshots_only:
        generated = out / 'regenerated'
        run('01-regenerate-upstream', [sys.executable, HERE / 'code/export249.py', out / 'upstream', generated])
        need(digest(generated / '249-records.bin') == snapshots['249-records.bin'], 'fresh baseline word mismatch')
        for name in ('249-states.json', 'frames.json'):
            need(normalize(load(generated / name)) == normalize(load(X / name)), 'fresh baseline structural mismatch: ' + name)
        need(load(generated / 'REGENERATED-DONORS.json')['donor_keys'] == sorted(load(X / '249-DONOR-OWNERSHIP.json')['donor_keys']), 'fresh donor ownership mismatch')
    sources = sorted((HERE / 'code').glob('*.cpp'))  # code/sandwich/ holds the price wrapper, compiled separately
    need(len(sources) == 7, 'seven native checkers required')
    extension = '.exe' if os.name == 'nt' else ''
    def exe(name):
        return out / 'bin' / (name + extension)
    def compile_source(p):
        cmd = [args.cxx, '-std=c++17', '-O2', '-I', HERE / 'vendor']
        if args.boost_include:
            cmd.extend(['-I', args.boost_include.resolve()])
        cmd.extend([p, '-o', exe(p.stem)])
        run('compile-' + p.stem, cmd)
    # At most two compiler processes, with distinct output files.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(compile_source, sources))
    lead = out / 'lead'; compiler = out / 'compiler'; temporal = out / 'temporal'; review = out / 'review'
    run('02-transform', [exe('cohort-transform'), X, candidates, lead])
    result = load(HERE / 'RESULT.json')
    need(digest(lead / 'COHORT249-RECORDS.bin') == result['cohort_record_sha256'], 'cohort physical transcript hash mismatch')
    # 02b: concave-descent frame retiming of 25 ADD gates (rohanarun, PR263 stage), selection pre-bound by full
    # scalar-core alignment to this package's cohort transcript; the stage self-checks and every native checker reruns.
    (lead / 'DESCENT-REBIND-EVIDENCE.json').write_text(json.dumps(dict(status='SELECTION_PREBOUND_TO_COMMITTED_COHORT_TRANSCRIPT', cohort_record_sha256=result['cohort_record_sha256'], binding='full unchanged scalar-core event alignment (rebind_descent.py of PR270) from the shared-donor package cohort transcript d073aeb4a8054ee6e23366ac7a42554624d52d3a822e03de9831a12530287395 (itself bound from PR259 transcript 1ae06b18c7c23e0f96f9309fcfc4a64a59b670c21d99207192d93440021e4897); the plateau witness is bound likewise (rebind_plateaus.py) from its descent transcript 43a73a445f7eefa76f227d31e8195899a4c537ff8a561867f4a87c56fe8f0da6'), indent=2) + '\n', encoding='utf-8')
    shutil.copy(HERE / 'inputs/descent-selection.json', lead / 'descent-selection.json')
    run('02b-descent-retiming', [sys.executable, '-B', HERE / 'code/descent_retiming.py', X, lead, lead / 'descent-selection.json'])
    need(digest(lead / 'COHORT249-PRE-DESCENT-RECORDS.bin') == result['cohort_record_sha256'], 'retained cohort transcript changed')
    need(digest(lead / 'COHORT249-RECORDS.bin') == result['descent_record_sha256'], 'descent transcript hash mismatch')
    # 02c-02e: connected-block plateau retiming of 29 blocks / 57 ADDs (PR270 stage), witness pre-bound to the descent transcript.
    plateau = out / 'plateau'
    run('02c-plateau-retiming', [sys.executable, '-B', HERE / 'code/plateau_retiming.py', X, lead, HERE / 'inputs/plateau-selection.json', plateau])
    lead = plateau
    run('02d-plateau-source-spans', [sys.executable, '-B', HERE / 'code/verify_plateau_spans.py', X, lead, lead / 'PLATEAU-RETIMING.json'])
    run('02e-frame-tables', [sys.executable, '-B', HERE / 'code/verify_frame_tables.py', X, lead, '--output', lead / 'FRAME-TABLE-AUDIT.json'])
    need(digest(lead / 'COHORT249-RECORDS.bin') == result['plateau_record_sha256'], 'plateau transcript hash mismatch')
    # 02f: exact F2 target-prefix compression (eumemic's PR268 mechanism, rohanarun's native PR273 stage): 209 square
    # groups whose dependent target's frame-20 prefix response is the F2 sum of three retained square-mates. The
    # selection is bound to this package's plateau transcript (post-cut scalar event alignment from PR273's word);
    # the stage recomputes every literal dependency from the actual transcript, rebuilds every MOVE, and runs both
    # all-column replays with a negative control before anything is emitted. The seven native checkers follow.
    shutil.copy(HERE / 'inputs/target-selection.json', lead / 'target-selection.json')
    run('02f-target-prefix', [sys.executable, '-B', HERE / 'code/target_prefix.py', X, lead, lead / 'target-selection.json'])
    need(digest(lead / 'COHORT249-PRE-TARGET-RECORDS.bin') == result['plateau_record_sha256'], 'retained plateau transcript changed')
    need(digest(lead / 'COHORT249-RECORDS.bin') == result['new_record_sha256'], 'new physical transcript hash mismatch')
    run('03-independent-legality', [exe('cohort-legality-independent'), X, lead, review / 'INDEPENDENT-LEGALITY.json'])
    run('04-independent-prefix', [exe('cohort-prefix-independent'), X, lead, review / 'INDEPENDENT-PREFIX.json'])
    run('05-bank-charts-and-assignment', [exe('cohort-bank-review'), X, lead / 'COHORT249-INITIAL.json', lead / 'COHORT249-FRAMES.json', compiler, 'actual_multicut'])
    (compiler / 'BANK-REVIEW.json').rename(compiler / 'COHORT-BANK-REVIEW.json')
    run('06-five-stage-columns', [exe('cohort-five-stage-columns'), lead / 'COHORT249-RECORDS.bin', temporal / 'COHORT-FIVE-STAGE-COLUMNS.json'])
    run('07-exact-price', [exe('cohort-price'), lead / 'COHORT249-REPLAY.json', lead / 'COHORT-EXACT-PRICE.json'])
    run('08-finite-invoice', [exe('cohort-finite-invoice'), lead / 'COHORT249-RECORDS.bin', lead / 'COHORT-EXACT-PRICE.json', compiler / 'COHORT-BANK-REVIEW.json', temporal / 'COHORT-FIVE-STAGE-COLUMNS.json', temporal / 'COHORT-FINITE-INVOICE.json'])
    need(load(lead / 'COHORT-EXACT-PRICE.json')['cohort_candidate']['kappa'] == result['kappa_native_seven_checkers'], 'native kappa mismatch')
    # 09: cleanup-sandwich cancellation (evmckinney9's PR271 mechanism) of the 45 helpers whose only gates after the
    # first kernel cut are t += a; a += b; t += a. Each stops at a nondegenerate four-dimensional frame instead of
    # climbing to the full frame. The native bank review and the REPLAY-driven native pricer assume helpers end at
    # the full frame (hard-coded census, stock from the entrance rank), so this part is certified as PR271 does:
    # native legality (final frames from the stage's export), native own-cut prefix and five-stage columns on the
    # new word, exact SymPy endpoint charts and bank re-tiling, the unchanged price engine through a histogram
    # wrapper (which first reproduces the native price above), and the native finite invoice.
    sand = out / 'sandwich'
    run('09-cleanup-sandwich', [sys.executable, '-B', HERE / 'code/cleanup_sandwich.py', X, lead, HERE / 'inputs/sandwich-selection.json', sand])
    need(digest(sand / 'COHORT249-PRE-SANDWICH-RECORDS.bin') == result['new_record_sha256'], 'retained native transcript changed')
    need(digest(sand / 'COHORT249-RECORDS.bin') == result['sandwich_record_sha256'], 'sandwich transcript hash mismatch')
    srev = out / 'sandwich-review'; srev.mkdir()
    run('10-sandwich-legality', [exe('cohort-legality-independent'), sand / 'export', sand, srev / 'INDEPENDENT-LEGALITY.json'])
    run('11-sandwich-prefix', [exe('cohort-prefix-independent'), sand / 'export', sand, srev / 'INDEPENDENT-PREFIX.json'])
    run('12-sandwich-five-stage-columns', [exe('cohort-five-stage-columns'), sand / 'COHORT249-RECORDS.bin', srev / 'COHORT-FIVE-STAGE-COLUMNS.json'])
    run('13-sandwich-endpoints-and-banks', [sys.executable, '-B', HERE / 'code/sandwich_endpoints.py', X, sand, compiler / 'COHORT-BANK-REVIEW.json', srev])
    cmd = [args.cxx, '-std=c++17', '-O2', '-I', HERE / 'vendor']
    if args.boost_include:
        cmd.extend(['-I', args.boost_include.resolve()])
    run('14-compile-price-wrapper', cmd + ['-DPR254_PRICE_SOURCE="%s"' % (HERE / 'code/cohort-price.cpp'), HERE / 'code/sandwich/price-histogram.cpp', '-o', exe('price-histogram')])
    def histogram(path):
        h = {}
        for op, a, b, c, f, z in struct.iter_unpack('<6i', Path(path).read_bytes()):
            if op == 0 and f: h[f] = h.get(f, 0) + 1
            elif op == 2: h[z] = h.get(z, 0) + 1
        return {'histogram': {str(r): c for r, c in sorted(h.items())}}
    (srev / 'base-histogram.json').write_text(json.dumps(histogram(sand / 'COHORT249-PRE-SANDWICH-RECORDS.bin')), encoding='utf-8')
    (srev / 'new-histogram.json').write_text(json.dumps(histogram(sand / 'COHORT249-RECORDS.bin')), encoding='utf-8')
    run('15-price-control', [exe('price-histogram'), srev / 'base-histogram.json', compiler / 'COHORT-BANK-REVIEW.json', srev / 'base-price.json'])
    need(load(srev / 'base-price.json')['candidate'] == load(lead / 'COHORT-EXACT-PRICE.json')['cohort_candidate'], 'price wrapper does not reproduce the native price')
    run('16-price-sandwich', [exe('price-histogram'), srev / 'new-histogram.json', srev / 'SANDWICH-BANK-INVOICE.json', srev / 'new-price.json'])
    price = load(srev / 'new-price.json')['candidate']
    need(price['positive_constraints'] == 47 and price['next_kappa_rejected'] > 0, 'sandwich price assembly')
    (srev / 'COHORT-EXACT-PRICE.json').write_text(json.dumps({'status': 'PASS_SANDWICH_PRICE_SAME_ENGINE_STOCK_FROM_RETILED_BANKS', 'pre_sandwich_reproduced': load(srev / 'base-price.json')['candidate'], 'cohort_candidate': price}, indent=2) + '\n', encoding='utf-8')
    run('17-sandwich-finite-invoice', [exe('cohort-finite-invoice'), sand / 'COHORT249-RECORDS.bin', srev / 'COHORT-EXACT-PRICE.json', srev / 'SANDWICH-BANK-INVOICE.json', srev / 'COHORT-FIVE-STAGE-COLUMNS.json', srev / 'COHORT-FINITE-INVOICE.json'])
    need(price['kappa'] == result['kappa'], 'sandwich kappa mismatch')
    for expected in sorted((HERE / 'expected-sandwich').glob('*.json')):
        source = sand if expected.name in ('CLEANUP-SANDWICH.json', 'COHORT249-REPLAY.json') else srev
        need(normalize(load(source / expected.name)) == normalize(load(expected)), 'fresh sandwich receipt differs: ' + expected.name)
    receipts = {}
    for expected in sorted((HERE / 'expected').glob('*.json')):
        matches = [p / expected.name for p in (lead, compiler, temporal, review) if (p / expected.name).is_file()]
        need(len(matches) == 1, 'missing or ambiguous receipt: ' + expected.name)
        got = normalize(load(matches[0])); wanted = normalize(load(expected))  # both sides normalized (this package)
        need(got == wanted, 'fresh receipt differs: ' + expected.name)
        receipts[expected.name] = got
    cert = dict(status='PASS_ALL_SEVEN_NATIVE_CHECKERS_AND_PINNED_RECEIPTS_PLUS_SANDWICH_STAGE',
                kappa=result['kappa'], kappa_decimal=result['kappa_decimal'],
                kappa_native_seven_checkers=result['kappa_native_seven_checkers'], kappa_native_decimal=result['kappa_native_decimal'],
                sandwich_record_sha256=result['sandwich_record_sha256'], native_bank_review_applicable_to_sandwich=False,
                baseline_regenerated_from_source=not args.snapshots_only,
                new_record_sha256=result['new_record_sha256'],
                package_manifest_sha256=digest(HERE / 'MANIFEST.json'),
                retained_public_all_size_interfaces=True, lean_certificate=False,
                elapsed_seconds=time.monotonic()-start, receipts=receipts)
    (out / 'CERTIFICATE.json').write_text(json.dumps(cert, indent=2)+'\n', encoding='utf-8')
    print('PASS: kappa = ' + result['kappa_decimal'] + ' (seven native checkers alone, before the sandwich stage: ' + result['kappa_native_decimal'] + ')', flush=True)
    print('Certificate: ' + str(out / 'CERTIFICATE.json'), flush=True)

if __name__ == '__main__':
    main()
