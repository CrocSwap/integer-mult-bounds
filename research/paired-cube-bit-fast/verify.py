#!/usr/bin/env python3
"""Regenerate the p=12 bit word with the fast generator and require byte-identical outputs.

    python3 -B verify.py                       # against the outputs pinned in SOURCE.json (about 12 s)
    python3 -B verify.py --original PATH       # also run the pinned original at PATH (about 2 min) and compare
    python3 -B verify.py --against-main        # compare with the bit word main itself carries (about 1 min)

--against-main rebuilds main's PR181 source tree from research/coordinated-frames-and-entrance-banks/
baseline-pr181.part01..03 (hash-checked against that package's BASELINE.json), regenerates the word, requires it to
equal main's research/paired-cube-bit/out/ byte for byte, and runs that tree's independent check_paired_cube_bit.py
on the regenerated word. It does not reproduce main's frozen physical layer (references/paired-cube/bit-physical),
which comes from other tools; it only reports how that layer relates to the regenerated word.

Standard library only. Run without -O.
"""
import argparse, gzip, hashlib, io, json, shutil, subprocess, sys, tempfile, time, zipfile
from collections import Counter
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('run without -O')
HERE = Path(__file__).resolve().parent
SRC = json.loads((HERE / 'SOURCE.json').read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
OUTPUTS = ('graph_p12.json', 'profile_p12.json', 'word_p12.json', 'frames_p12.json', 'kchron_p12.json', 'word_p12.json.gz')
MAIN_PKG = 'research/coordinated-frames-and-entrance-banks'
MAIN_BIT = 'research/paired-cube-bit'
MAIN_PHYS = 'references/paired-cube/bit-physical'


def need(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def run(script, out):
    t0 = time.time()
    subprocess.run([sys.executable, '-B', str(script), '--p', '12', '--out', str(out)], check=True, capture_output=True)
    return time.time() - t0


def digests(out):
    got = {}
    for name in OUTPUTS:
        data = (out / name).read_bytes()
        if name.endswith('.gz'):          # gzip bytes depend on the zlib build: compare the content
            got['word_p12.json.gz (decompressed)'] = sha(gzip.decompress(data))
        else:
            got[name] = sha(data)
    return got


def main_archive(root):
    """main's PR181 source archive, rebuilt from its three parts and checked against BASELINE.json."""
    pkg = root / MAIN_PKG
    need((pkg / 'BASELINE.json').exists(), '%s/BASELINE.json not found; run from a checkout of main (or pass --repo)' % MAIN_PKG)
    pin = json.loads((pkg / 'BASELINE.json').read_text())
    blob = b''
    for part in pin['parts']:
        data = (pkg / part['file']).read_bytes()
        need(sha(data) == part['sha256'], 'archive part differs from BASELINE.json: ' + part['file'])
        blob += data
    need(sha(blob) == pin['archive_sha256'], 'archive differs from BASELINE.json')
    zf = zipfile.ZipFile(io.BytesIO(blob))
    need(all(not n.startswith('/') and '..' not in Path(n).parts for n in zf.namelist()), 'unsafe path in archive')
    return zf, pin


def against_main(root):
    zf, pin = main_archive(root)
    print('main archive: %d files, sha256 %s... matches %s/BASELINE.json (PR181 @ %s)' % (len(zf.namelist()), pin['archive_sha256'][:12], MAIN_PKG, pin['commit'][:7]))
    results = []

    def check(name, ok):
        results.append(ok)
        print('  %-4s %s' % ('PASS' if ok else 'FAIL', name))
    for name in SRC['data']:
        check('generator input data/%s equals main\'s %s/data/%s' % (name, MAIN_BIT, name), (HERE / 'data' / name).read_bytes() == zf.read('%s/data/%s' % (MAIN_BIT, name)))
    with tempfile.TemporaryDirectory(prefix='bit-fast-main-') as d:
        d = Path(d)
        fast = d / 'fast'
        fast.mkdir()
        t = run(HERE / 'paired_cube_bit_word.py', fast)
        print('fresh run of the generator: %.1f s' % t)
        for name in OUTPUTS:
            ref = zf.read('%s/out/%s' % (MAIN_BIT, name))
            mine = (fast / name).read_bytes()
            if name.endswith('.gz'):
                check('%s equals main\'s %s/out/%s (decompressed)' % (name, MAIN_BIT, name), gzip.decompress(mine) == gzip.decompress(ref))
            else:
                check('%s equals main\'s %s/out/%s byte for byte' % (name, MAIN_BIT, name), mine == ref)
        checker = d / 'check_paired_cube_bit.py'
        checker.write_bytes(zf.read('%s/check_paired_cube_bit.py' % MAIN_BIT))
        r = subprocess.run([sys.executable, '-B', str(checker), '--dir', str(fast), '--p', '12'], capture_output=True, text=True)
        check('main\'s independent check_paired_cube_bit.py passes on the regenerated word (%s)' % ((r.stdout.strip().splitlines() or [''])[-1][:70]), r.returncode == 0)
        # how main's frozen physical layer relates to the regenerated word (reported, not scored)
        pw = json.loads(gzip.decompress(zf.read('%s/word_p12.json.gz' % MAIN_PHYS)))
        mw = json.loads(gzip.decompress((fast / 'word_p12.json.gz').read_bytes()))['word']
        pf = json.loads(gzip.decompress(zf.read('%s/frames_p12.json.gz' % MAIN_PHYS)))['frames']
        mf = json.loads((fast / 'frames_p12.json').read_bytes())['frames']
        pset = {json.dumps(v, sort_keys=True) for v in pf.values()}
        have = sum(1 for v in mf.values() if json.dumps(v, sort_keys=True) in pset)
        moved = sum(1 for a, b in zip(mw['ops'], pw['ops']) if a != b)
        same_ops = Counter(o[2] for o in mw['ops']) == Counter(o[2] for o in pw['ops'])
        print('main\'s frozen physical layer (%s) is NOT reproduced by this generator; relation, for information:' % MAIN_PHYS)
        print('  same op count (%d) and op node multiset: %s; same sources: %s; ops reordered at %d positions; %.1f%% of the regenerated frame records appear in its frames (ids renumbered)'
              % (len(mw['ops']), same_ops, mw['sources'] == pw['sources'], moved, 100 * have / len(mf)))
    need(all(results), 'the regenerated word differs from the one main carries')
    print('PASS: the fast generator reproduces main\'s base bit word (%d/%d checks)' % (sum(results), len(results)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--original', type=Path, default=None, help='path to the pinned original paired_cube_bit_word.py')
    ap.add_argument('--against-main', action='store_true', help="compare with the bit word main's own PR181 archive carries")
    ap.add_argument('--repo', type=Path, default=HERE.parents[1], help='repository root holding main\'s files (default: this checkout)')
    a = ap.parse_args()
    for name, want in SRC['data'].items():
        need(sha((HERE / 'data' / name).read_bytes()) == want, 'data file differs from SOURCE.json: ' + name)
    if a.against_main:
        return against_main(a.repo.resolve())
    with tempfile.TemporaryDirectory(prefix='bit-fast-') as d:
        d = Path(d)
        fast = d / 'fast'
        t_fast = run(HERE / 'paired_cube_bit_word.py', fast.mkdir() or fast)
        got = digests(fast)
        need(got == SRC['p12_outputs'], 'fast generator outputs differ from the pinned outputs: ' +
             ', '.join(k for k in SRC['p12_outputs'] if got.get(k) != SRC['p12_outputs'][k]))
        print('PASS: fast generator reproduces all %d pinned p=12 outputs byte-for-byte in %.1f s' % (len(got), t_fast))
        if a.original:
            need(sha(a.original.read_bytes()) == SRC['original']['sha256'], 'original differs from the pin in SOURCE.json')
            orig = d / 'orig'
            (orig / 'data').mkdir(parents=True)
            shutil.copy(a.original, orig / 'paired_cube_bit_word.py')
            for name in SRC['data']:
                shutil.copy(HERE / 'data' / name, orig / 'data' / name)
            t_orig = run(orig / 'paired_cube_bit_word.py', (d / 'orig_out').mkdir() or d / 'orig_out')
            need(digests(d / 'orig_out') == got, 'original and fast outputs differ')
            print('PASS: pinned original gives identical outputs in %.1f s (%.1fx slower)' % (t_orig, t_orig / t_fast))


if __name__ == '__main__':
    main()
