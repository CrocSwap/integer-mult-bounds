#!/usr/bin/env python3
"""Mechanical re-pinning after a new bit word (new module data) is installed. Not part of the proof.

    python3 -B discovery/repin.py --output /new/scratch/dir            (dry run: prints the changed pins)
    python3 -B discovery/repin.py --output /new/scratch/dir --write    (writes word-pins.json and MANIFEST.json)

It runs verify.replay(), the exact stage sequence of verify.py, in this process with word_pins.RECORD switched on,
so every expect(name, value) records the value of the installed word instead of asserting it. Every structural
assertion, control and exact certificate still runs and must pass. verify.py itself always runs with
RECORD = None (it asserts so), so after --write the new pins are checked by a fresh, strict `verify.py` run.
See discovery/REPIN.md for the whole procedure. Prepared by DreamingOfClouds with Anthropic Claude assistance;
Apache-2.0.
"""
import argparse, hashlib, importlib.util, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True


def manifest(write):
    p = ROOT / 'MANIFEST.json'; old = json.loads(p.read_text()); files = {}
    for q in ROOT.rglob('*'):
        assert not q.is_symlink(), q
        if q.is_file() and q != p:
            assert '__pycache__' not in q.parts and q.suffix != '.pyc' and q.name != '.DS_Store', q
            files[q.relative_to(ROOT).as_posix()] = hashlib.sha256(q.read_bytes()).hexdigest()
    changed = sorted(k for k in set(files) | set(old['files']) if files.get(k) != old['files'].get(k))
    if write:
        p.write_text(json.dumps(dict(files=dict(sorted(files.items())), schema=old['schema']), indent=1, sort_keys=True) + '\n')
    return changed


def main():
    if not __debug__: raise SystemExit('assertions required')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True); ap.add_argument('--write', action='store_true')
    a = ap.parse_args(); out = a.output.resolve(); assert not out.exists() and not out.is_relative_to(ROOT); out.mkdir(parents=True)
    import word_pins
    assert Path(word_pins.__file__).resolve() == ROOT / 'word_pins.py'
    old = dict(word_pins.PINS); word_pins.RECORD = {}
    spec = importlib.util.spec_from_file_location('repin_verify', ROOT / 'verify.py'); verify = importlib.util.module_from_spec(spec); spec.loader.exec_module(verify)
    results, timings = {}, {}
    def save(name, value): (out / name).write_text(json.dumps(verify.serial(value), sort_keys=True, indent=2) + '\n')
    t = time.monotonic(); verify.replay(out, results, timings, save)
    new = dict(sorted(word_pins.RECORD.items()))
    for k in sorted(set(old) | set(new)):
        if old.get(k) != new.get(k):
            print('PIN', k, ':', json.dumps(old.get(k))[:160], '->', json.dumps(new.get(k))[:160])
    (out / 'word-pins.json').write_text(json.dumps(new, indent=1, sort_keys=True) + '\n')
    if a.write:
        (ROOT / 'word-pins.json').write_text(json.dumps(new, indent=1, sort_keys=True) + '\n')
        print('wrote word-pins.json; MANIFEST changes:', manifest(True))
    else:
        print('dry run; MANIFEST would change:', manifest(False))
    print('recorded %d pins in %.0fs; now run verify.py (strict) on a new output directory' % (len(new), time.monotonic() - t))


if __name__ == '__main__':
    main()
