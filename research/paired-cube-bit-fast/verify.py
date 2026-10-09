#!/usr/bin/env python3
"""Regenerate the p=12 bit word with the fast generator and require byte-identical outputs to the pinned original.

    python3 -B verify.py                       # fast generator only (about 12 s)
    python3 -B verify.py --original PATH       # also run the pinned original at PATH (about 2 min) and compare

SOURCE.json pins the original generator (sha256), the data files it reads and the sha256 of every p=12 output.
Standard library only. Run without -O.
"""
import argparse, gzip, hashlib, json, shutil, subprocess, sys, tempfile, time
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('run without -O')
HERE = Path(__file__).resolve().parent
SRC = json.loads((HERE / 'SOURCE.json').read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
OUTPUTS = ('graph_p12.json', 'profile_p12.json', 'word_p12.json', 'frames_p12.json', 'kchron_p12.json', 'word_p12.json.gz')


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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--original', type=Path, default=None, help='path to the pinned original paired_cube_bit_word.py')
    a = ap.parse_args()
    for name, want in SRC['data'].items():
        need(sha((HERE / 'data' / name).read_bytes()) == want, 'data file differs from SOURCE.json: ' + name)
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
