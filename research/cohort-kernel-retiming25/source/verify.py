#!/usr/bin/env python3
"""Offline source-bound reproduction. No stored PASS result is accepted without execution."""
from pathlib import Path, PurePosixPath
import argparse, concurrent.futures, gzip, hashlib, json, os, subprocess, sys, time, zipfile
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
        return {k: normalize(v) for k, v in x.items() if k not in ('seconds', 'local_scalar_stream')}
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
    for part in ('logs', 'bin', 'lead', 'compiler', 'review', 'temporal/CURRENT249-EXPORT', 'upstream'):
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
    sources = sorted((HERE / 'code').glob('*.cpp'))
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
    need(digest(lead / 'COHORT249-RECORDS.bin') == result['parent_record_sha256'], 'parent physical transcript hash mismatch')
    run('02b-extra-retiming', [sys.executable, '-B', HERE / 'code/extra-retiming.py', out])
    need(digest(lead / 'COHORT249-RECORDS.bin') == result['new_record_sha256'], 'retimed physical transcript hash mismatch')
    need(result['parent_record_sha256'] != result['new_record_sha256'], 'vacuous omitted retiming control')
    run('03-independent-legality', [exe('cohort-legality-independent'), X, lead, review / 'INDEPENDENT-LEGALITY.json'])
    run('04-independent-prefix', [exe('cohort-prefix-independent'), X, lead, review / 'INDEPENDENT-PREFIX.json'])
    run('05-bank-charts-and-assignment', [exe('cohort-bank-review'), out, compiler])
    run('06-five-stage-columns', [exe('cohort-five-stage-columns'), lead / 'COHORT249-RECORDS.bin', temporal / 'COHORT-FIVE-STAGE-COLUMNS.json'])
    run('07-exact-price', [exe('cohort-price'), lead / 'COHORT249-REPLAY.json', lead / 'COHORT-EXACT-PRICE.json'])
    run('08-finite-invoice', [exe('cohort-finite-invoice'), lead / 'COHORT249-RECORDS.bin', lead / 'COHORT-EXACT-PRICE.json', compiler / 'COHORT-BANK-REVIEW.json', temporal / 'COHORT-FIVE-STAGE-COLUMNS.json', temporal / 'COHORT-FINITE-INVOICE.json'])
    receipts = {}
    for expected in sorted((HERE / 'expected').glob('*.json')):
        matches = [p / expected.name for p in (lead, compiler, temporal, review) if (p / expected.name).is_file()]
        need(len(matches) == 1, 'missing or ambiguous receipt: ' + expected.name)
        got = normalize(load(matches[0])); wanted = load(expected)
        need(got == wanted, 'fresh receipt differs: ' + expected.name)
        receipts[expected.name] = got
    need(load(lead / 'COHORT-EXACT-PRICE.json')['cohort_candidate']['kappa'] == result['kappa'], 'assembled result binding')
    need({p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and p.name != 'MANIFEST.json'} == set(manifest), 'package membership changed during replay')
    for name, expected in manifest.items():
        need(digest(HERE / name) == expected, 'package changed during replay: ' + name)
    cert = dict(status='PASS_IMMUTABLE_PR254_PLUS25_ALL_NATIVE_CHECKERS_EXACT_RETIMING_AND_PINNED_RECEIPTS',
                kappa=result['kappa'], kappa_decimal=result['kappa_decimal'],
                baseline_regenerated_from_source=not args.snapshots_only,
                new_record_sha256=result['new_record_sha256'],
                package_manifest_sha256=digest(HERE / 'MANIFEST.json'),
                retained_public_all_size_interfaces=True, lean_certificate=False,
                package_inputs_unchanged=True, post_retiming_checked=True,
                public_eight_stage_python_replay_claimed=False,
                inherited_parent_kappa=result['parent_kappa'],
                unchanged_scalar_and_copy_sequence=True,
                elapsed_seconds=time.monotonic()-start, receipts=receipts)
    (out / 'CERTIFICATE.json').write_text(json.dumps(cert, indent=2)+'\n', encoding='utf-8')
    print('PASS: kappa = ' + result['kappa_decimal'], flush=True)
    print('Certificate: ' + str(out / 'CERTIFICATE.json'), flush=True)

if __name__ == '__main__':
    main()
