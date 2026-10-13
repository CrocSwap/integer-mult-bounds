# Apache-2.0.  Prepared with Claude Opus 5.5 (Anthropic) in omp; submitted by jeremykothe2.
"""Verify the Lean formalisation of the hyperplane-end generalization of Lemma A.

usage: python3 verify.py [--no-cache] [--instances RUN_DIR ...]
  1. the Lean sources (this package, ../e8-lemma-a-lean, ../e8-lemma-g-lean) contain no `sorry`, `admit`, `axiom`,
     `native_decide`, `implemented_by`, `extern`, `unsafe`, `opaque` and no `set_option` other than the heartbeat limits;
  2. `lake exe cache get` (Mathlib's pinned build, skipped with --no-cache) and `lake build` (builds LemmaA and LemmaG;
     HyperplaneEnd.Exact runs the kernel checks of (N) with `decide +kernel`, several minutes and several GB);
  3. `lake env lean PrintAxioms.lean`: every named result depends only on propext, Classical.choice, Quot.sound;
  4. with --instances RUN_DIR ... (HPE local runs holding CANONICAL-WORD.json.gz and WRAPPER-CHECKS.json):
     code/check_hpe_pairs.py --mutants on each run.
Python 3.9+, standard library only; `lake` from elan on PATH (the toolchain is pinned by lean-toolchain)."""
import re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
FORBIDDEN = re.compile(r'\b(sorry|admit|axiom|native_decide|implemented_by|extern|unsafe|opaque)\b|set_option\s+(?!maxHeartbeats|maxRecDepth)')


def fail(msg):
    print('FAIL', msg, flush=True); sys.exit(1)


def run(cmd, timeout):
    print('$', ' '.join(cmd), flush=True)
    p = subprocess.run(cmd, cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
    if p.returncode:
        print(p.stdout[-4000:]); fail(f'{cmd[0]} {cmd[1]} exited {p.returncode}')
    return p.stdout


def strip_comments(src):
    src = re.sub(r'/-.*?-/', ' ', src, flags=re.S)
    return re.sub(r'--[^\n]*', ' ', src)


def main():
    args = sys.argv[1:]
    A, G = HERE.parent / 'e8-lemma-a-lean', HERE.parent / 'e8-lemma-g-lean'
    lean_files = (sorted(HERE.glob('HyperplaneEnd/*.lean')) + [HERE / 'HyperplaneEnd.lean', HERE / 'PrintAxioms.lean'] +
                  sorted(A.glob('LemmaA/*.lean')) + [A / 'LemmaA.lean'] + sorted(G.glob('LemmaG/*.lean')) + [G / 'LemmaG.lean'])
    for p in lean_files:
        m = FORBIDDEN.search(strip_comments(p.read_text(encoding='utf-8')))
        if m: fail(f'forbidden token {m.group(0)!r} in {p.name}')
    print('sources: no sorry / admit / axiom / native_decide / unsafe / opaque / extern in %d files' % len(lean_files), flush=True)

    if '--no-cache' not in args:
        run(['lake', 'exe', 'cache', 'get'], 3600)
    out = run(['lake', 'build'], 3600)
    print('\n'.join(l for l in out.splitlines() if 'warning' in l or 'error' in l or 'Build completed' in l), flush=True)

    out = run(['lake', 'env', 'lean', 'PrintAxioms.lean'], 1200)
    wanted = [l.split()[2] for l in (HERE / 'PrintAxioms.lean').read_text().splitlines() if l.startswith('#print axioms')]
    seen = {}
    for m in re.finditer(r"'([\w.']+)' depends on axioms: \[([^\]]*)\]", out):
        seen[m.group(1)] = [a.strip() for a in m.group(2).split(',') if a.strip()]
    for m in re.finditer(r"'([\w.']+)' does not depend on any axioms", out):
        seen[m.group(1)] = []
    print(out.strip(), flush=True)
    for name in wanted:
        if name not in seen: fail(f'no axiom report for {name}')
        extra = set(seen[name]) - ALLOWED
        if extra: fail(f'{name} uses {sorted(extra)}')
    print(f'axioms: {len(wanted)} results, all within {sorted(ALLOWED)}')
    if '--instances' in args:
        for run_dir in args[args.index('--instances') + 1:]:
            print(run([sys.executable, str(HERE / 'code' / 'check_hpe_pairs.py'), run_dir, '--mutants'], 600).strip())
    print('PASS')


if __name__ == '__main__':
    main()
