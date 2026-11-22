# Compare the outputs of replay_spanfacts.sh with the shipped logs (provenance/logs), fact by fact.
#   usage: replay_compare.py OUTDIR LOGSDIR LOGDIR WALL     (OUTDIR: <job>.out/.rc/.cpu of every job; LOGDIR: receives one merged replay log per fact)
import os, re, sys, glob
OUT, LOGS, LOGDIR, WALL = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
os.makedirs(LOGDIR, exist_ok=True)
def rd(p): return open(p).read() if os.path.exists(p) else ''
def norm(t): return t.replace('cards/DIRX/', '')
def job(n): return rd(os.path.join(OUT, n + '.out'))
def rc(n):
    try: return int(rd(os.path.join(OUT, n + '.rc')).strip())
    except ValueError: return -1
def cpu(n):
    try: u, s = rd(os.path.join(OUT, n + '.cpu')).split(); return float(u) + float(s)
    except ValueError: return 0.0
status = []; cpus = {}
def report(tag, ok, msg): status.append(ok); print(('PASS ' if ok else 'FAIL ') + tag + ': ' + msg)
def merge(fact, names):   # merged replay log of one fact, and its CPU time
    with open(os.path.join(LOGDIR, 'replay_' + fact + '.out'), 'w') as f:
        for n in names: f.write('==> %s (exit %d) <==\n%s' % (n, rc(n), norm(job(n))))
    cpus[fact] = cpus.get(fact, 0) + sum(cpu(n) for n in names)
    return all(rc(n) == 0 for n in names)
# ---------- s6-type logs (s66 / s6x): additive histograms and per-rep lines
OV6 = re.compile(r'max real rank (\d+), max #directions (\d+); rank histogram \(nonempty pairs\): (.*)')
def s6_summary(texts):
    mr = md = 0; hist = [0] * 9; reps = {}
    for t in texts:
        for m in OV6.finditer(t):
            mr = max(mr, int(m.group(1))); md = max(md, int(m.group(2)))
            for kv in m.group(3).split():
                k, v = kv.split(':'); hist[int(k)] += int(v)
        for m in re.finditer(r'^rep (\d+) lines (\d+) orbit (\d+) active (\d+) maxrank (\d+)', t, re.M): reps[int(m.group(1))] = m.groups()[1:]
    return mr, md, hist[1:], reps
def check_s6(fact, tag, names, shipped, bound, nreps):
    ok = merge(fact, names)
    a = s6_summary([job(n) for n in names]); b = s6_summary([rd(os.path.join(LOGS, shipped))])
    same = a == b and len(a[3]) == nreps and a[0] <= bound
    report(tag, ok and same, 'max real rank %d (bound %d), max #dirs %d, %d reps; rank histogram and per-rep lines %s the shipped log %s' % (a[0], bound, a[1], len(a[3]), 'equal' if a == b else 'DIFFER from', shipped))
    return a
# ---------- s3-type logs (s3f / s3x / s3y / s3z): additive pairs, survivors, max span
def s3_summary(texts):
    pairs = surv = leaves = ovf = 0; span = 0; crack = 0; nrep = 0; hits = 0
    for t in texts:
        for l in t.split('\n'):
            if l.startswith('OVERALL'):
                d = dict(re.findall(r'(pairs|surviving|leaves|overflow) (\d+)', l)); pairs += int(d['pairs']); surv += int(d['surviving']); leaves += int(d['leaves']); ovf += int(d['overflow'])
                span = max(span, int(re.search(r'max span (\d+)', l).group(1)))
            elif l.startswith('CRACK'): crack += 1
            elif l.startswith('HIT'): hits += 1
            elif l.startswith('rep '): nrep += 1
    return dict(pairs=pairs, surviving=surv, leaves=leaves, overflow=ovf, maxspan=span, cracks=crack, hits=hits, reps=nrep)
def shipped_chunks(pattern, n): return [rd(os.path.join(LOGS, pattern % r)) for r in range(n)]
def check_s3(fact, tag, prefix, shipped_pat, n, z_prefix=None, expect_reps=159):
    names = [prefix + '_%d' % r for r in range(n)]; ok = merge(fact, names)
    a = s3_summary([job(x) for x in names]); b = s3_summary(shipped_chunks(shipped_pat, n))
    ident = sum(norm(job(x)) == norm(t) for x, t in zip(names, shipped_chunks(shipped_pat, n)))
    msg = '%d chunks, %d of them byte-identical to the shipped chunk logs; pairs %d, surviving pairs %d, cracks %d, max span %d (shipped: pairs %d, max span %d)' % (n, ident, a['pairs'], a['surviving'], a['cracks'], a['maxspan'], b['pairs'], b['maxspan'])
    good = ok and a == b and a['reps'] == expect_reps and a['overflow'] == 0
    if z_prefix:
        zn = [z_prefix + '_%d' % r for r in range(n)]; zok = merge(fact + '_s3z', zn); z = s3_summary([job(x) for x in zn])
        msg += '; independent s3z: pairs %d, surviving %d, max span %d, %s' % (z['pairs'], z['surviving'], z['maxspan'], 'EQUAL to s3f' if z == a else 'DIFFERS from s3f')
        good = good and zok and z == a
    report(tag, good, msg); return a
print('replay of the eight span facts (wall %s s)' % WALL)
# fact 1
n1 = ['f1_s66_m1']; ok = merge('fact1_s66', n1)
same = norm(job('f1_s66_m1')).strip() == rd(os.path.join(LOGS, 'SIX/s66_m1.out')).strip()
report('fact 1 (6,6)+1 <= 3 [s66.c mode 1]', ok and same, 'output byte-identical to logs/SIX/s66_m1.out (max real rank 3, 0 rank-8 pairs)' if same else 'DIFFERS from logs/SIX/s66_m1.out')
nm = ['f1_indep_m1_c%d' % c for c in range(6)]; ok = merge('fact1_indep', nm); good = ok
mx = 0
for c in range(6):
    new = job(nm[c]); old = rd(os.path.join(LOGS, 'SIX/indep_m1_c%d.out' % c))
    pick = lambda t: sorted(l for l in t.split('\n') if l.startswith('INDEP OVERALL') or l.startswith('DONE REPS'))
    if pick(new) != pick(old) or not pick(new): good = False
    m = re.search(r'max real rank (\d+)', new); mx = max(mx, int(m.group(1))) if m else 99
report('fact 1 (6,6)+1 <= 3 [indep.py mode 1, independent Python]', good and mx == 3, '6 chunks cover all 159 reps; INDEP OVERALL and DONE REPS lines equal the shipped chunk logs; max real rank %d' % mx)
# facts 2, 3, 4, 5
check_s6('fact2', 'fact 2 (6,6)+2 <= 4 [s6x = s6y]', ['f2_y662_%d' % k for k in range(4)], 'SIX/y_662.out', 4, 159)
a = check_s6('fact3_y664', 'fact 3a (6,6)+4 lines relaxed, lim 80: span 8 on 6 pairs only [s6x]', ['f3_y664_%d' % k for k in range(8)], 'SIX/y_664.out', 8, 159)
r8 = sorted(k for k, v in a[3].items() if v[3] == '8')
ref = job('f3_r664'); refshipped = rd(os.path.join(LOGS, 'SIX/r_664.out'))
okr = merge('fact3_r664', ['f3_r664']) and ref.strip() == refshipped.strip() and re.search(r'REFINE max exact rank 4', ref) and r8 == [67, 68, 82]
report('fact 3b (6,6,3) s0 <= 4 [s6x exact third-flat refinement]', bool(okr), 'refinement of the relaxed-span-8 reps %s: REFINE max exact rank 4; output byte-identical to logs/SIX/r_664.out' % r8)
check_s6('fact4', 'fact 4 (7,4) s0 <= 4 [s6x]', ['f4_y740_%d' % k for k in range(4)], 'SIX/y_740.out', 4, 51)
check_s6('fact5', 'fact 5 (7,5) s0 <= 4 [s6x]', ['f5_y750_%d' % k for k in range(2)], 'MS3c/y_750.out', 4, 51)
nm = ['f5_p1y750_%d' % r for r in range(24)]; ok = merge('fact5_p1', nm); a = s3_summary([job(x) for x in nm]); b = s3_summary([rd(os.path.join(LOGS, 'DIRX/p1_y750.out'))])
report('fact 5 (7,5) s0 |Off|<=88 extension [s3x pass 1]', ok and a['pairs'] == b['pairs'] == 146195478 and a['surviving'] == 0 and a['hits'] == 0, '%d pairs, %d surviving pairs, %d qualifying new directions (shipped log: %d pairs, %d surviving)' % (a['pairs'], a['surviving'], a['hits'], b['pairs'], b['surviving']))
# fact 6
a = check_s3('fact6_s3f', 'fact 6 (6,6,4) s0 <= 5 [s3f |Off|<=80, target 8]', 'f6_s3f_a664s0', 'S3FLAT/out_a664s0_%d.out', 24, 'z6_s3z_a664s0')
t6 = check_s3('fact6_t6', 'fact 6 (6,6,4) s0 <= 5 [s3y |Off|<=88, target 6: no crack => span <= 5]', 'f6_s3y_t6', 'SPANCOVER/664s0t6_%d.out', 48, 'z6_s3z_t6')
c5 = job('f6_s3y_t5_34'); z5 = job('z6_s3z_t5_34'); sh5 = rd(os.path.join(LOGS, 'SPANCOVER/664s0t5_34.out'))
pat = 'CRACK? target 5 span 5 rep 82 V2idx 103676'
ok5 = merge('fact6_t5', ['f6_s3y_t5_34', 'z6_s3z_t5_34']) and pat in c5 and pat in z5 and norm(c5) == norm(sh5)
report('fact 6 (6,6,4) s0: span exactly 5 [s3y and s3z, |Off|<=88, target 5, chunk 34]', bool(ok5), 'crack at target 5 (rep 82, V2idx 103676) found by both; s3y output identical to logs/SPANCOVER/664s0t5_34.out')
nm = ['f6_p1a664_%d' % r for r in range(24)]; ok = merge('fact6_p1', nm); a = s3_summary([job(x) for x in nm])
report('fact 6 (6,6,4) s0 |Off|<=88 extension at target 8 [s3x pass 1; previously only in the DIRX card notes]', ok and a['pairs'] == 70064678 and a['surviving'] == 0 and a['hits'] == 0, '%d pairs, %d qualifying new directions' % (a['pairs'], a['hits']))
# facts 7, 8
check_s3('fact7', 'fact 7 (6,5,4)+1 <= 4 [s3f target 8]', 'f7_s3f_b654s1', 'S3FLAT/out_b654s1_%d.out', 24, 'z7_s3z_b654s1')
check_s3('fact8', 'fact 8 (6,4,4)+1 <= 4 [s3f target 8]', 'f8_s3f_b644s1', 'S3FLAT/out_b644s1_%d.out', 24, 'z8_s3z_b644s1')
tot = sum(cpus.values())
print('CPU time (user+sys, s): ' + ', '.join('%s %.0f' % (k, v) for k, v in sorted(cpus.items())) + '; total %.0f s = %.1f CPU-min' % (tot, tot / 60))
allok = all(status)
print(('PASS' if allok else 'FAIL') + ' %d of %d checks pass' % (sum(status), len(status)))
sys.exit(0 if allok else 1)
