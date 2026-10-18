#!/usr/bin/env python3
"""end7_controls.py BASE_WORD RECIPE AUDIT_LOCAL_PY NATIVE_AUDITOR PORTABLE_RUNNER ROUTING OUTDIR
Positive control (the recipe word passes both auditors) and three negative controls, each rejected by BOTH the independent
audit_local and the native hpe auditor with its pinned reason:
  end_restored   : one lowered helper end restored to its dimension-eight value (frames/accounting stay lowered)
  wrong_frame    : one required B lowering replaced by a different codimension-one subspace
  cone_violation : one helper end set to another dimension-seven subspace that misses its row cone
Writes OUTDIR/END7-CONTROLS.json. Standard library only (the auditors are the package's own)."""
import gzip, hashlib, json, os, subprocess, sys
from pathlib import Path

EXPECT = {
    'end_restored': dict(independent='paid profile mismatch', native='paid local profile differs from the reported local_profile'),
    'wrong_frame': dict(independent='frame not monotone', native="'nonmonotone'"),
    'cone_violation': dict(independent='frame not monotone', native='hpe cone pre-check (row / column)'),
}


def main():
    base, recipe, audit, native, runner, routing, out = map(Path, sys.argv[1:8])
    here = Path(__file__).resolve().parent; out = out.resolve(); out.mkdir(parents=True, exist_ok=True)
    rec = json.loads(recipe.read_text())
    assert sorted(rec['controls']) == sorted(EXPECT), 'control set'
    res = {}

    def check(name, word, expect):
        rows = {}
        a = subprocess.run([sys.executable, '-B', str(audit), '--word', str(word), '--output', str(out / (name + '.audit.json'))],
                           capture_output=True, text=True)
        n = subprocess.run([sys.executable, '-B', str(runner), str(native), '--raw', str(word), '--routing', str(routing),
                            '--out', str(out / (name + '.native'))], capture_output=True, text=True, cwd=str(out))
        for k, r in (('independent', a), ('native', n)):
            last = (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else ''
            ok = r.returncode == 0 if expect is None else (r.returncode != 0 and expect[k] in last)
            rows[k] = dict(ok=ok, exit=r.returncode, last=last[:240])
        res[name] = rows
        print(name, {k: v['ok'] for k, v in rows.items()}, flush=True)

    w = out / 'recipe.json.gz'
    subprocess.run([sys.executable, '-B', str(here / 'build_ends7.py'), str(base), str(recipe), str(w)], check=True, capture_output=True)
    check('recipe', w, None)
    for ctl, exp in EXPECT.items():
        cw = out / (ctl + '.json.gz')
        subprocess.run([sys.executable, '-B', str(here / 'build_ends7.py'), str(base), str(recipe), str(cw), '--control', ctl],
                       check=True, capture_output=True)
        check(ctl, cw, exp)
    ok = all(v['ok'] for r in res.values() for v in r.values())
    rep = dict(status='PASS_RANK7_END_CONTROLS' if ok else 'FAIL', recipe_sha256=hashlib.sha256(recipe.read_bytes()).hexdigest(),
               controls=res, rejections=sum(1 for n, r in res.items() if n != 'recipe' for v in r.values() if v['ok']))
    (out / 'END7-CONTROLS.json').write_text(json.dumps(rep, indent=1) + '\n')
    print(rep['status'], rep['rejections'], 'rejections', flush=True)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
