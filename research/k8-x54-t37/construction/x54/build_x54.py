#!/usr/bin/env python3
"""Rebuild the eight-slot k8 word (seven-slot k8 word + X54 slot) and its native locals.

Input: the seven-slot k8 word (content c2b29430..., research/gauge44-slots RECIPE-SLOTS-k8.json on #1005's db2c7cfb).
Steps (each checked): build_tri.py (NewBArch, unchanged) applies RECIPE-X54-k8.json (jeremykothe2's #1130 X54 recipe,
identical edits and frames, rebased onto the seven-slot word); run_controls.py (10 outcomes); independent audit_local;
PR635 native chain (native, ledgers, local-replay, wrappers, phases). Pins: X54-PINS.json.
"""
import argparse, gzip, hashlib, json, os, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
def csha(p): return hashlib.sha256(gzip.decompress(Path(p).read_bytes())).hexdigest()
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True); ap.add_argument('--pr635', type=Path, required=True)
    ap.add_argument('--seven-slot-word', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args(); out = a.out.resolve(); assert not out.exists(); out.mkdir(parents=True)
    pins = json.loads((HERE/'X54-PINS.json').read_text()); rec = HERE/'RECIPE-X54-k8.json'
    main = a.main.resolve(); src = main/'research/complex-k492-owner-repair/vendor/multicold'
    up = a.pr635.resolve()/'research/complex-571-cold14-st2'; base = src/'vendor/pr558'; par = base/'vendor/pr552'
    barch = main/'research/complex-t21-owners/vendor/pr870/construction/barch'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0', MULTICOLD_SOURCE=str(src), GAIN_PR564_SOURCE=str(src))
    def run(label, script, *args, portable=True):
        cmd = [sys.executable, '-B'] + ([str(src/'code/run_portable.py')] if portable else []) + [str(script), *map(str, args)]
        with (out/(label+'.log')).open('w') as f: rc = subprocess.call(cmd, env=env, stdout=f, stderr=subprocess.STDOUT)
        assert rc == 0, label; print('PASS', label, flush=True)
    assert csha(a.seven_slot_word) == pins['base_content_sha256'], 'seven-slot base word'
    word = out/'FULL-WORD.json.gz'
    run('x54', barch/'build_tri.py', a.seven_slot_word, rec, word, portable=False)
    assert csha(word) == pins['word_content_sha256']
    run('x54-controls', barch/'run_controls.py', a.seven_slot_word, rec, main/'research/complex-t21-owners/vendor/pr870/independent/audit_local.py', out/'controls', portable=False)
    res = json.loads((out/'controls/controls.json').read_text()); assert sorted(res) == sorted(pins['controls']) and all(x['ok'] for x in res.values())
    run('audit-local', main/'research/complex-t21-owners/vendor/pr870/independent/audit_local.py', '--word', word, '--main', main, '--output', out/'AUDIT-LOCAL.json', portable=False)
    local = out/'local'; routing = par/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    run('native', up/'code/hpe_audit_and_transport.py', '--raw', word, '--routing', routing, '--out', local)
    assert csha(local/'CANONICAL-WORD.json.gz') == pins['canonical_sha256']
    run('ledgers', up/'code/hpe_emit_local.py', local)
    run('local-replay', up/'code/hpe_audit_local.py', local)
    run('wrappers', up/'code/hpe_adapters_local.py', local/'CANONICAL-WORD.json.gz', local/'RESIDUAL-ADAPTERS.json', local/'WRAPPER-CHECKS.json')
    checks = json.loads((local/'LOCAL-CHECKS.json').read_text())
    assert {o: checks[o]['sha256'] for o in ('forward', 'backward')} == pins['program_sha256']
    run('phases', base/'code/phases_full.py', local, par/'complex-global/vendor531/vendor/clifford')
    assert hashlib.sha256((local/'CLIFFORD-RECIPES.json').read_bytes()).hexdigest() == pins['clifford_recipes_sha256']
    print('DONE', local, flush=True)
if __name__ == '__main__': main()
