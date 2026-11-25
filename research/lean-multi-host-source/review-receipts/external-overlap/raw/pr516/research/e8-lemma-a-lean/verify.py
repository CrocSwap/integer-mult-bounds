# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
"""Verify the Lean formalisation of Lemma A.

usage: python3 verify.py [--no-cache] [--instances BASE] [--async T.json.gz]
  1. every file listed in MANIFEST.json has its recorded sha256 and no unlisted file sits in LemmaA/ or code/; the files of
     the Lemma G package (path dependency) and of PR #484 that are used have their recorded sha256 ("external_files");
  2. the Lean sources contain no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by`, `extern`, `unsafe`, `opaque`
     and no `set_option` other than the heartbeat limits (Lemma G's sources are scanned too);
  3. `lake exe cache get` (Mathlib's pinned build, skipped with --no-cache) and `lake build` (builds LemmaG as well);
  4. `lake env lean PrintAxioms.lean`: each main theorem depends only on propext, Classical.choice, Quot.sound;
  5. with --instances BASE (BASE = the output directory of PR #484's verify.py; --all there adds gauge80 and kernel79), on
     every word present (the headline is required; the anchor is checked where present):
       a. #484's own results on inputs equal to EXPECTED.json: LEMMA-A.json (required for every wrapped word),
          HOSTING-AUDIT.json (strict one-helper audit, where present), LEMMA-G-CHECK.json (I-helper count = EXPECTED,
          scalar replay);
       b. the Lemma G package's code/check_extended_labels.py --mutants: (F) is read in Lemma G's extended labels;
       c. code/check_owners.py --mutants: one owner per stream (disjoint footprints on shared families), centre copies;
       d. code/check_windows.py --mutants: every hosted block inside its pending child's open window, blocks disjoint;
  6. with --async T.json.gz (an asynchronous hosted template, e.g. the one PR #505's verify.py emits): c. and d. on it.
Python 3.9+, standard library only; `lake` from elan on PATH (the toolchain is pinned by lean-toolchain)."""
import hashlib, json, os, re, subprocess, sys
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
    src = re.sub(r'/-.*?-/', ' ', src, flags=re.S)          # block and doc comments (not nested in these sources)
    return re.sub(r'--[^\n]*', ' ', src)


def main():
    args = sys.argv[1:]
    man = json.loads((HERE / 'MANIFEST.json').read_text())
    for rel, sha in man['files'].items():
        got = hashlib.sha256((HERE / rel).read_bytes()).hexdigest()
        if got != sha: fail(f'sha256 of {rel}')
    for d in ('LemmaA', 'code'):
        for p in (HERE / d).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and str(p.relative_to(HERE)) not in man['files']:
                fail(f'unlisted file {p.relative_to(HERE)}')
    for rel, sha in man['external_files'].items():
        if hashlib.sha256((HERE / rel).read_bytes()).hexdigest() != sha: fail(f'sha256 of {rel}')
    print('manifest: %d files and %d external files (Lemma G package, #484) OK' % (len(man['files']), len(man['external_files'])), flush=True)

    G = HERE.parent / 'e8-lemma-g-lean'
    lean_files = (sorted(HERE.glob('LemmaA/*.lean')) + [HERE / 'LemmaA.lean', HERE / 'PrintAxioms.lean'] +
                  sorted(G.glob('LemmaG/*.lean')) + [G / 'LemmaG.lean'])
    for p in lean_files:
        m = FORBIDDEN.search(strip_comments(p.read_text()))
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
        if not set(seen[name]) <= ALLOWED: fail(f'{name} depends on {seen[name]}')
    print('axioms: %d theorems, only %s' % (len(wanted), sorted(ALLOWED)), flush=True)

    if '--instances' in args:
        base = Path(args[args.index('--instances') + 1])
        words = [w for w in ('gauge80-kernel42', 'gauge80', 'kernel79', 'anchor') if (base / w / 'hosted').is_dir()]
        if 'gauge80-kernel42' not in words: fail(f'{base} lacks the headline word')
        E = json.loads((HERE.parent / 'e8-complex-gauge-kernel' / 'EXPECTED.json').read_text())
        for w in words:
            L = json.loads((base / 'lemmaG' / w / 'LEMMA-G-CHECK.json').read_text())
            if L['inputs'] != E['lemma_G_independent_checks'][w]['inputs']: fail(f'{w}: emitted inputs differ from #484 EXPECTED.json')
            if any(L['labels'][o]['n_label_violations'] or L['labels'][o]['scalar_violations'] for o in ('forward', 'backward')):
                fail(f'{w}: #484 label/scalar check')
            if w == 'anchor':
                print('instances: anchor: #484 label and scalar checks PASS (no wrappers)', flush=True); continue
            la = base / w / 'LEMMA-A.json'
            if not la.exists(): fail(f'{w}: #484 LEMMA-A.json missing')
            A = json.loads(la.read_text())
            if A['status'] != 'PASS_RESIDUAL_WRAPPERS_ARE_EXACT': fail(f'{w}: #484 LEMMA-A.json')
            if w == 'gauge80-kernel42' and A['frames'] != E['wrapper_check']['frames']: fail('headline: #484 LEMMA-A frames')
            ha = base / w / 'HOSTING-AUDIT.json'
            if ha.exists():
                H = json.loads(ha.read_text())
                if not (H['status'].startswith('PASS') and H['one_helper_per_family']): fail(f'{w}: #484 hosting audit')
            if L['instances']['I-helper']['failures']: fail(f'{w}: #484 I-helper')
            if L['instances']['I-helper']['entering_helpers'] != E['lemma_G_independent_checks'][w]['instances']['I-helper']['entering_helpers']:
                fail(f'{w}: I-helper count differs from EXPECTED.json')
            print('instances: %s: #484 Lemma A exact part (%d frames), %shosting audit, I-helper %d helpers, scalar replay: PASS'
                  % (w, A['frames'], 'strict ' if ha.exists() else 'no ', L['instances']['I-helper']['entering_helpers']), flush=True)
        out = run([sys.executable, '-B', str(HERE.parent / 'e8-lemma-g-lean' / 'code' / 'check_extended_labels.py'), str(base), *words, '--mutants'], 3600)
        print('\n'.join(l for l in out.splitlines() if re.match(r'^\S+ (forward|backward) violations', l) or 'mutants (' in l
                        or 'extended labels' in l), flush=True)
        print(run([sys.executable, '-B', 'code/check_owners.py', str(base), *words, '--mutants'], 3600).strip(), flush=True)
        print(run([sys.executable, '-B', 'code/check_windows.py', *[str(base / w / 'hosted' / 'GLOBAL-TEMPLATE.json.gz') for w in words], '--mutants'], 3600).strip(), flush=True)
    if '--async' in args:
        tpl = args[args.index('--async') + 1]
        print(run([sys.executable, '-B', 'code/check_owners.py', '--template', tpl, '16', '--mutants'], 3600).strip(), flush=True)
        print(run([sys.executable, '-B', 'code/check_windows.py', tpl, '--mutants'], 3600).strip(), flush=True)
    print('PASS Lemma A Lean verification', flush=True)


if __name__ == '__main__':
    main()
