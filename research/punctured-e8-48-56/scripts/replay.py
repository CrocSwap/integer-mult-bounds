"""Replay of recorded leaves of the Lemma-G-failure orbit trees (sat/middrv.py semantics).
usage: replay.py TYPE P K OPTSDIR WORKDIR NMD5 NSOLVE      (FULL=1: every leaf, md5 and solve)
For leaves of data/states/T{TYPE}_P{P}_k{K}.json it (1) regenerates the leaf CNF from (T, live) with middrv.leafcnf and compares the md5 of the
file with the md5 recorded when the original run solved it; (2) for a spread sample, runs kissat 4.0.4 (--no-binary) and drat-trim against that CNF
and requires UNSAT + VERIFIED.  COUNT leaves are re-checked by |T| > P for ALL of them.  Prints PASS / FAIL / SKIP lines."""
import os, sys, json, hashlib, subprocess, time, shutil
typ, P, k = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); optsdir, work = sys.argv[4], sys.argv[5]
NMD5, NSOLVE = int(sys.argv[6]), int(sys.argv[7]); FULL = os.environ.get('FULL') == '1'
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE)
tag = f'T{typ} P{P} k{k}'
os.makedirs(work + '/st', exist_ok=True); os.makedirs(work + '/red', exist_ok=True)
shutil.copy(f'{optsdir}/opts56_{typ}.npz', f'{work}/opts56_{typ}.npz')
os.environ.update(MIDLIB='1', MIDWORK=work, MIDSKIPINV='1')
sys.argv = ['middrv.py', str(typ), str(P), str(k), '60']
t0 = time.time(); cwd0 = os.getcwd()
exec(compile(open(f'{PKG}/sat/middrv.py').read(), 'middrv.py', 'exec'))     # defines leafcnf, qcnt, OPT, ... (MIDLIB: no tree run)
os.chdir(cwd0)
state = json.load(open(f'{PKG}/data/states/T{typ}_P{P}_k{k}.json'))      # the recorded run (middrv's own empty state is overwritten)
fails = 0
def rep(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg, flush=True); fails += (not ok)
cnt = {n: v for n, v in state.items() if v.get('res') == 'COUNT'}
rep(all(len(v['T']) > P for v in cnt.values()), f'{tag}: all {len(cnt)} counting leaves have |T| > {P}')
leaves = sorted(n for n, v in state.items() if v.get('res') == 'UNSAT-VERIFIED' and not v.get('split') and 'md5' in v)
rep(all(v.get('res') in ('UNSAT-VERIFIED', 'COUNT') for v in state.values()), f'{tag}: no SAT / TIMEOUT / UNVERIFIED entry in the state ({len(state)} entries, {len(leaves)} solved leaves, '
    f'{sum(1 for v in state.values() if v.get("split"))} split nodes)')
def spread(lst, n): return lst if FULL or n >= len(lst) else [lst[int(i * len(lst) / n)] for i in range(n)]
def build(name):
    v = state[name]; nv, cls, nopt = leafcnf(set(v['T']), v['live'], None)
    fn = f'{work}/red/{name}.cnf'
    with open(fn, 'w') as f:
        f.write(f'p cnf {nv} {len(cls)}\n')
        for c in cls: f.write(' '.join(map(str, c)) + ' 0\n')
    return fn, v
bad = 0; shas = []
md5s = spread(leaves, NMD5)
for name in md5s:
    fn, v = build(name)
    ok = hashlib.md5(open(fn, 'rb').read()).hexdigest() == v['md5']
    bad += (not ok); shas.append((name, hashlib.sha256(open(fn, 'rb').read()).hexdigest()))
    if not ok: print('   md5 mismatch', name)
    if not FULL: os.remove(fn)
rep(bad == 0, f'{tag}: {len(md5s)} regenerated leaf CNFs match the recorded md5')
easy = [n for n in leaves if state[n].get('kissat_s', 99) <= 6 and state[n].get('s', 99) <= 40]
sol = spread(easy, NSOLVE); bad = 0; t1 = time.time()
KS = os.environ.get('KISSAT', 'kissat'); DT = os.environ.get('DRAT_TRIM', 'drat-trim')
for name in sol:
    fn, v = build(name); pr = fn[:-4] + '.drat'
    r = subprocess.run([KS, '-q', '--no-binary', fn, pr], capture_output=True, text=True, timeout=1200).stdout
    ok = 's UNSATISFIABLE' in r
    if ok: ok = 's VERIFIED' in subprocess.run([DT, fn, pr, '-t', '540'], capture_output=True, text=True).stdout
    bad += (not ok)
    if not ok: print('   not verified', name)
    for f in (fn, pr):
        if os.path.exists(f): os.remove(f)
rep(bad == 0, f'{tag}: {len(sol)} sampled leaves re-solved: kissat UNSAT + drat-trim VERIFIED ({time.time()-t1:.0f}s)')

# shipped proofs: evidence/proofs/index.tsv lines "tag<TAB>leaf<TAB>sha256(drat)<TAB>sha256(cnf)"; verify.  MAKEPROOFS=N (author): write N proofs for this tag first.
import lzma
PD = f'{PKG}/evidence/proofs'; IDX = f'{PD}/index.tsv'
if os.environ.get('MAKEPROOFS'):
    os.makedirs(PD, exist_ok=True); small = sorted(easy, key=lambda n: (state[n].get('kissat_s', 99), state[n]['clauses']))
    for name in small[:int(os.environ['MAKEPROOFS'])]:
        fn, v = build(name); pr = fn[:-4] + '.drat'
        subprocess.run([KS, '-q', '--no-binary', fn, pr], capture_output=True, text=True, timeout=1200)
        raw = open(pr, 'rb').read(); xz = lzma.compress(raw, preset=9)
        open(f'{PD}/{tag.replace(" ", "")}_{name}.drat.xz', 'wb').write(xz)
        open(IDX, 'a').write(f'{tag}\t{name}\t{hashlib.sha256(raw).hexdigest()}\t{hashlib.sha256(open(fn, "rb").read()).hexdigest()}\n')
shipped = [l.split('\t') for l in open(IDX).read().splitlines() if l.split('\t')[0] == tag] if os.path.exists(IDX) else []
bad = 0
for _, name, hp, hc in shipped:
    fn, v = build(name); pr = fn[:-4] + '.drat'
    raw = lzma.decompress(open(f'{PD}/{tag.replace(" ", "")}_{name}.drat.xz', 'rb').read()); open(pr, 'wb').write(raw)
    ok = hashlib.sha256(raw).hexdigest() == hp and hashlib.sha256(open(fn, 'rb').read()).hexdigest() == hc
    ok = ok and 's VERIFIED' in subprocess.run([DT, fn, pr, '-t', '540'], capture_output=True, text=True).stdout
    bad += (not ok)
    for f in (fn, pr): os.remove(f)
if shipped: rep(bad == 0, f'{tag}: {len(shipped)} SHIPPED DRAT proofs (evidence/proofs) drat-trim VERIFIED against the regenerated CNFs')
if os.environ.get('SHAOUT'): open(os.environ['SHAOUT'], 'a').write(''.join(f'{tag}\t{n}\t{h}\n' for n, h in sorted(set(shas))))
sys.exit(1 if fails else 0)
