#!/usr/bin/env python3
"""CERTKIT chain generator: a kernel-replayed Lean trace for ANY 7113-caller word (lane CERTKIT, Nov 19).
usage: gen_chain.py WORD.json[.gz] TAG        (pure Python, 1 proc; writes Nov15/UniInhabit<TAG>*.lean + UniWCData<TAG>.lean)

It instantiates the UNI-INHABIT chain (t7669, Nov15/UniInhabit*.lean, all kernel-only) for another word:
 * data files (Evs/Tabs/Tabs2) from Nov15/unigen/gen_inhabit.py, patched: COPY = SCALE 0 + ADD (the genwc/um3 shim),
   owned lifetimes of any count, segment size chosen so the trace has exactly 26 checkpointed segments;
 * fold tables UniWCData<TAG> (namespace T<TAG>Data) from Nov15/unigen/genwc.py;
 * the hand-written proof files with the word's sizes substituted (registers, lifetimes, frames, MOVEs, events),
   histogram counts recomputed, the t7669-table-specific D/R section of Fold dropped (not needed for the invoice);
 * UniInhabit<TAG>Main: paid7_hist / cred7_hist = the trace's MOVE-price and helper-climb histograms (fold_paid).
Every substituted fact is re-proved by the kernel when the files build; a wrong substitution can only fail the build.
"""
import gzip, json, math, os, re, subprocess, sys, tempfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))   # package root (paths are package-relative)
NOV = os.path.join(ROOT, 'lean', 'Nov15')
UG = os.path.join(HERE, 'unigen')

HAND = ['Defs', 'Sound', 'Seg', 'Frames'] + [f'Fr{i}' for i in range(8)] + ['Facts', 'Reg', 'Ports', 'Word', 'Hist', 'Nest', 'Fold']
PER_SEG = 2
SEGPARTS = []
ORDER = ['Defs', 'Evs', 'Tabs', 'Tabs2', 'WCDATA', 'Seg', 'Sound', 'Frames'] + [f'Fr{i}' for i in range(8)] + \
        ['Facts', 'Reg', 'Ports', 'Word', 'Hist', 'Nest', 'Fold', 'Main']


def load(p):
    return json.load(gzip.open(p) if p.endswith('.gz') else open(p))


def stats(W):
    n = W['public']; prog = W['program']
    NO = sum(1 for e in prog if e[0] == 'INIT')
    ncopy = sum(1 for e in prog if e[0] == 'COPY')
    NEV = n + len(prog) + ncopy
    dim = [len(f) for f in W['frames']]
    mv = [abs(dim[e[3]] - dim[e[2]]) for e in prog if e[0] == 'MOVE']
    live = set(W['live']); H = W['hosted']
    main = live | {r + 112 for r in live} | set(H['X2']) | set(H['Y2'])
    clm = [dim[W['final'][r]] - dim[W['initial'][r]] for r in range(n) if r not in main]
    return dict(n=n, NO=NO, NR=n + NO + 16, NF=len(W['frames']), NMV=len(mv), NEV=NEV, P=Counter(mv), C=Counter(clm),
                nh=len(clm))


def data_files(word, tag, outdir):
    """run gen_inhabit.py (patched copy) -> Evs/Tabs/Tabs2 in outdir; returns NSEG."""
    src = open(os.path.join(UG, 'gen_inhabit.py')).read()
    src = src.replace("if e[0] == 'ADD' and e[2] >= n: e[2] = life[e[2]]",
                      "if e[0] in ('ADD', 'COPY') and e[2] >= n: e[2] = life[e[2]]")
    src = src.replace("NR = n + NO + 16; assert len(kind) == NR == 1752, (NR, len(kind))",
                      "NR = n + NO + 16; assert len(kind) == NR, (NR, len(kind))")
    src = src.replace("    elif op == 'CLEAR': evs.append(slot(5, e[1], c=e[2]))",
                      "    elif op == 'CLEAR': evs.append(slot(5, e[1], c=e[2]))\n"
                      "    elif op == 'COPY': evs.append(slot(3, e[1], c=e[-1], co=Q(0))); evs.append(slot(2, e[1], a=e[2], c=e[-1], co=Q(e[3])))")
    src = src.replace("from GEN/STACK/t7669.json.gz", "from ' + os.path.basename(sys.argv[1]) + ' (CERTKIT gen_chain)")
    assert src.count("'COPY'") == 2
    # 128-bit slots: num 48-87, den 88-127 (40 bits each; t7669's 96-bit slots had 24-bit num/den)
    for a, b in [("nu < 1 << 24 and de < 1 << 24", "nu < 1 << 40 and de < 1 << 40"),
                 ("nu << 48 | de << 72", "nu << 48 | de << 88"), ("packl(c, 96)", "packl(c, 128)")]:
        assert src.count(a) == 1, a; src = src.replace(a, b)
    W = load(word)
    nev = W['public'] + len(W['program']) + sum(1 for e in W['program'] if e[0] == 'COPY')
    nch = math.ceil(nev / 250)
    seg = math.ceil(nch / 26)
    assert math.ceil(nch / seg) == 26, (nch, seg)
    p = os.path.join(outdir, 'gi.py'); open(p, 'w').write(src)
    env = dict(os.environ, SEG=str(seg), OMP_NUM_THREADS='1')
    r = subprocess.run([sys.executable, p, word, outdir], capture_output=True, text=True, env=env)
    print(r.stdout.strip()); assert r.returncode == 0, r.stderr[-2000:]
    return seg


def subst(txt, tag, S):
    txt = txt.replace('UniInhabit', 'UniInhabit' + tag).replace('UniWCData', 'UniWCData' + tag).replace('7669', tag)
    for a, b in [(1752, S['NR']), (1751, S['NR'] - 1), (1736, S['n'] + S['NO']), (1735, S['n'] + S['NO'] - 1),
                 (235, S['NO']), (1097, S['NF']), (6157, S['NMV']), (152023, S['NEV'])]:
        txt = re.sub(r'(?<![0-9])%d(?![0-9])' % a, str(b), txt)
    return txt


def fix_hist(txt, S):
    for r in range(10):
        txt = re.sub(r'(theorem prc_%d : .*?\.length = )\d+' % r, lambda m: m.group(1) + str(S['P'].get(r, 0)), txt)
        txt = re.sub(r'(theorem clm_%d : .*?\.length = )\d+' % r, lambda m: m.group(1) + str(S['C'].get(r, 0)), txt)
    return txt


def poly(cnt):
    return f'{cnt.get(1, 0)} + ' + ' + '.join(f'{cnt.get(r, 0)} * ({r}:ℝ) ^ σ' for r in range(2, 10))


def main_lite(tag, S):
    src = open(os.path.join(NOV, 'UniInhabitMain.lean')).read()
    body = src.split('/-! ## Valid at κ7669 -/')[0]
    body = re.sub(r'^/-.*?-/\n', '', body, count=1, flags=re.S)
    body = body.replace('import Nov15.UniInhabitNum\n', '')
    # the two histogram statements
    body = re.sub(r'(theorem paid7_hist .*?wordPaid caller7113 \(exec tr7669\) specPrice σ =\n    )(.*?)(:= by)',
                  lambda m: m.group(1) + poly(S['P']) + ' ' + m.group(3), body, flags=re.S)
    body = re.sub(r'(theorem cred7_hist .*?gc σ \(hcred \(exec tr7669\) r\) =\n    )(.*?)(:= by)',
                  lambda m: m.group(1) + poly(S['C']) + ' ' + m.group(3), body, flags=re.S)
    hdr = (f'/-\nUniInhabit{tag}Main (GENERATED by toolkit/certkit/gen_chain.py from UniInhabitMain, lane CERTKIT).\n'
           f'The concrete {tag} trace: MOVE-price histogram (wordPaid = Σ over the {S["NMV"]} MOVEs, fold_paid) and helper-climb\n'
           f'histogram (Σ over the {S["nh"]} helpers, path ends).  Kernel only.\n-/\n')
    return hdr + subst(body, tag, S) + 'end UniInhabit\n'.replace('UniInhabit', 'UniInhabit' + tag) + \
        f'\n#print axioms UniInhabit{tag}.paid7_hist\n#print axioms UniInhabit{tag}.cred7_hist\n'


def main():
    word, tag = sys.argv[1], sys.argv[2]
    W = load(word); S = stats(W)
    assert S['nh'] == 1101 and W['public'] == 1501 and W['owned_fields'] == 68
    assert all(r < 10 for r in S['P']) and all(0 <= r < 10 for r in S['C'])
    print('stats', {k: v for k, v in S.items() if k not in 'PC'}, 'P', sorted(S['P'].items()), 'C', sorted(S['C'].items()))
    with tempfile.TemporaryDirectory() as td:
        data_files(word, tag, td)
        for f in ['UniInhabitEvs', 'UniInhabitTabs', 'UniInhabitTabs2']:
            txt = open(os.path.join(td, f + '.lean')).read()
            txt = txt.replace('UniInhabit', 'UniInhabit' + tag)
            open(os.path.join(NOV, f.replace('UniInhabit', 'UniInhabit' + tag) + '.lean'), 'w').write(txt)
    r = subprocess.run([sys.executable, os.path.join(UG, 'genwc.py'), word, 'T' + tag, os.path.join(NOV, f'UniWCData{tag}.lean')],
                       capture_output=True, text=True, env=dict(os.environ, OMP_NUM_THREADS='1'))
    print(r.stdout.strip()); assert r.returncode == 0, r.stderr[-2000:]
    for h in HAND:
        txt = open(os.path.join(NOV, f'UniInhabit{h}.lean')).read()
        if h == 'Defs':
            for a, b in [('x / 281474976710656 % 16777216, x / 4722366482869645213696 % 16777216',
                          'x / 281474976710656 % 1099511627776, x / 309485009821345068724781056 % 1099511627776'),
                         ('79228162514264337593543950336', '340282366920938463463374607431768211456'),
                         ('slots of 96 bits', 'slots of 128 bits'),
                         ('Event slot (96 bits): op 0-2 | r 3-13 | a 14-24 | c 25-35 | d 36-46 | sign 47 | num 48-71 | den 72-95',
                          'Event slot (128 bits, CERTKIT): op 0-2 | r 3-13 | a 14-24 | c 25-35 | d 36-46 | sign 47 | num 48-87 | den 88-127')]:
                assert a in txt, a; txt = txt.replace(a, b)
        if h == 'Hist':
            txt = fix_hist(txt, S)
        if h == 'Fold':
            txt = re.sub(r'/-! ## generic: tables on the fold of ANY 7113 word.*?end Gen\n', '', txt, flags=re.S)
            txt = txt.replace('#print axioms UniInhabit.foldsGen\n', '')
        txt = subst(txt, tag, S)
        if h == 'Seg':  # one file per PER_SEG decides: kernel memory grows with every decide in a file
            lines = txt.splitlines(); th = [l for l in lines if l.startswith('theorem')]
            parts = []
            for k in range(0, len(th), PER_SEG):
                m = f'UniInhabit{tag}Seg{k // PER_SEG}'; parts.append(m)
                open(os.path.join(NOV, m + '.lean'), 'w').write('\n'.join(lines[:3]) + '\n' + '\n'.join(th[k:k + PER_SEG]) +
                                                               f'\nend UniInhabit{tag}.Tabs\n')
            txt = lines[0] + '\n' + '\n'.join(f'import Nov15.{m}' for m in parts) + '\n'
            SEGPARTS[:] = parts
        open(os.path.join(NOV, f'UniInhabit{tag}{h}.lean'), 'w').write(txt)
    open(os.path.join(NOV, f'UniInhabit{tag}Main.lean'), 'w').write(main_lite(tag, S))
    mods = []
    for m in ORDER:
        if m == 'Seg': mods += SEGPARTS
        mods.append(f'UniWCData{tag}' if m == 'WCDATA' else f'UniInhabit{tag}{m}')
    json.dump(dict(word=word, tag=tag, modules=mods, stats={k: v for k, v in S.items() if k not in 'PC'}),
              open(os.path.join(HERE, f'chain_{tag}.json'), 'w'), indent=1)
    print('modules (build order):', ' '.join(mods))


if __name__ == '__main__':
    main()
