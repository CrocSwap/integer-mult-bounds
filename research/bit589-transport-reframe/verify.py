"""One-command replay of the transport-and-reframe search on PR589's bit word (standard library only).

Steps (each compared with EXPECTED.json):
  0. pins: SHA-256 of the two input words and the moment engine;
  1. depth one on PR589's word: every commuting relocation slot (within A, within B, across the scatter), exact frame
     optimum, no improvement;
  2. positive control on PR555's word: the same search finds PR589's hoist and sink;
  3. independent re-implementation: same class count from every insertion index, identical outcome multisets;
  4. exact rational moment certification of every distinct depth-one profile;
  5. explicit-word control: PR555 + hoist + sink, rebuilt with optimal frames, replayed by PR589's wlib and accepted by
     the unchanged xcheck_p.py interface audit, with PR589's exact local profile;
  6. negative controls: a non-commuting relocation changes the exact F2 map; a frame below its forced bound fails;
     and a seeded sample of interacting pairs (seed 14) on which the primary and independent optima must agree;
  6b. Steinberg 3 -> 2 rewrites of PR589's word (PR548's mechanism): every rewrite F2-checked, exact optimum from
     both implementations, none better; detection control on a word expanded by one inverse rewrite;
  7. (--pairs, about 35 min on 12 cores) the pair positive control on PR555's word (from the hoist, the best second
     move is PR589's sink, reaching PR589's profile), then depth two over interacting pairs on PR589's word; every
     distinct pair profile is certified exactly.
Usage: verify.py OUTDIR [--jobs N] [--pairs]
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
"""
import gzip
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PY = [sys.executable, '-B']
TUNED = ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
BASE555 = ROOT / 'research/e8-bit-p111-tuned/data/bitE8mut-p111.json.gz'
MOMENT = ROOT / 'research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/moment.py'
XCHECK = ROOT / 'research/e8-bit-p111-tuned/code/xcheck_p.py'
C589 = '1733427039589844234749/1000000000000000000000000'
C555 = '1733052823330162099157/1000000000000000000000000'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(args, out=None):
    r = subprocess.run(PY + [str(a) for a in args], capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        sys.stderr.write(r.stdout[-4000:] + r.stderr[-4000:])
        raise SystemExit('FAIL: ' + ' '.join(map(str, args)))
    return r.stdout


def check(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r expected %r' % (name, got, want))
    print('ok', name)


def f2_replay(w, A, B):
    """exact F2 map of D, A, scatter, B, C on symbolic columns (frames ignored); True iff the word's endpoint holds"""
    V = w['v']
    N = 2 * V + w['R']
    val = [1 << i for i in range(N)]
    for f, t, ss in w['D'] + A:
        for s in ss:
            val[t] ^= val[s]
    snap = [val[q] for q in w['ret']]
    for t, ks in enumerate(w['scatter']):
        for k in ks:
            val[V + t] ^= snap[k]
    full = max(range(len(w['frames'])), key=lambda f: len(w['frames'][f]))
    C = [[full, t, ss] for f, t, ss in reversed([g for g in A + B if g[1] < V or g[1] >= 2 * V])]
    for f, t, ss in B + C:
        for s in ss:
            val[t] ^= val[s]
    return all(val[r] == ((1 << r) ^ (1 << (r - V)) if V <= r < 2 * V else 1 << r) for r in range(N))


def negative_controls():
    sys.path.insert(0, str(HERE))
    import reframe as R
    w = json.load(gzip.open(TUNED, 'rt'))
    assert f2_replay(w, w['A'], w['B'])
    # (a) relocate an op across an adjacent gate that reads its destination (not commuting)
    A = w['A']
    k = next(k for k in range(1, len(A)) if len(A[k][2]) == 1 and A[k][1] in A[k - 1][2])
    bad = A[:k - 1] + [A[k], A[k - 1]] + A[k + 1:]
    commuting_ok = f2_replay(w, bad, w['B'])
    # (b) lower one forced (lo = hi) gate frame below its bound: nesting must fail
    word = R.Word(R.load(str(TUNED)))
    gates = list(word.A)
    j = next(j for j, (f, t, ss) in enumerate(gates) if R.Lattice.dim(word.lat, f) >= 2 and len(ss) == 1)
    f, t, ss = gates[j]
    lower = word.lat.close(f & -f)[0]  # a rank-one subframe
    gates[j] = (lower, t, ss)
    nesting = R.fixed_profile(word, gates, word.B)
    return dict(noncommuting_index=k, noncommuting_endpoint_holds=commuting_ok,
                lowered_gate=j, lowered_profile_legal=nesting is not None)


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    jobs = sys.argv[sys.argv.index('--jobs') + 1] if '--jobs' in sys.argv else str(os.cpu_count())
    E = json.load(open(HERE / 'EXPECTED.json'))
    check('pins', dict(tuned=sha(TUNED), base555=sha(BASE555), moment=sha(MOMENT), xcheck=sha(XCHECK)), E['pins'])

    run([HERE / 'search.py', TUNED, C589, '--jobs', jobs, '--detail', '--out', out / 'depth1.json'])
    d1 = json.load(open(out / 'depth1.json'))
    check('depth one', {k: d1[k] for k in E['depth1']}, E['depth1'])

    run([HERE / 'search.py', BASE555, C555, '--jobs', jobs, '--out', out / 'control555.json'])
    c5 = json.load(open(out / 'control555.json'))
    check('positive control', dict(improving=c5['improving'],
                                   top=[[b['move'], b['profile']] for b in c5['best'][:c5['improving']]]),
          E['control555'])

    ind = json.loads(run([HERE / 'independent_check.py', TUNED, out / 'depth1.json', '--jobs', jobs]))
    check('independent implementation', ind, E['independent'])

    json.dump([r['profile'] for r in d1['detail'] if r['profile'] is not None], open(out / 'depth1-profiles.json', 'w'))
    cert = json.loads(run([HERE / 'certify.py', out / 'depth1-profiles.json']))
    check('exact certification (depth one)', cert, E['certify_depth1'])

    ex = json.loads(run([HERE / 'export.py', BASE555, C555, out / 'control-hoist-sink.json.gz',
                         json.dumps(E['explicit_control']['moves'])]))
    check('explicit control profile', ex['profile'], E['explicit_control']['profile'])
    xc = run([XCHECK, out / 'control-hoist-sink.json.gz'])
    check('explicit control xcheck_p', xc.strip().splitlines()[-1], E['explicit_control']['xcheck_last_line'])

    check('negative controls', negative_controls(), E['negative_controls'])

    st = json.loads(run([HERE / 'steinberg.py', TUNED, C589, '--independent']))
    check('Steinberg 3->2 rewrites', st, E['steinberg'])
    sc = json.loads(run([HERE / 'steinberg.py', TUNED, C589, '--control']))
    check('Steinberg detection control', sc, E['steinberg_control'])

    ps = E['pair_sample']
    sample = json.loads(run([HERE / 'pair_sample_check.py', TUNED, C589, str(ps['pairs']), str(ps['seed']),
                             '--jobs', jobs]))
    check('seeded pair cross-check', sample, ps)

    if '--pairs' in sys.argv:
        pc = E['pair_control555']
        run([HERE / 'pairs.py', BASE555, C555, '--jobs', '1', '--first', json.dumps(pc['first']),
             '--out', out / 'pair-control555.json'])
        q = json.load(open(out / 'pair-control555.json'))
        check('pair positive control', dict(improving_pairs=q['improving_pairs'], best_m2=q['best'][0]['m2'],
                                            best_profile=q['best'][0]['profile']),
              {k: pc[k] for k in ('improving_pairs', 'best_m2', 'best_profile')})
        run([HERE / 'pairs.py', TUNED, C589, '--jobs', jobs, '--out', out / 'pairs.json'])
        p = json.load(open(out / 'pairs.json'))
        check('depth two', {k: p[k] for k in E['depth2']}, E['depth2'])
        json.dump([pr for pr, n in p['profiles']], open(out / 'pair-profiles.json', 'w'))
        cert2 = json.loads(run([HERE / 'certify.py', out / 'pair-profiles.json']))
        check('exact certification (depth two)', cert2, E['certify_depth2'])
    print('PASS_BIT589_TRANSPORT_REFRAME classes=%d legal=%d improving=0 control_rediscovered=2 '
          'independent_mismatches=0 certified=%d steinberg=%d pair_sample_agree=%d%s no_new_kappa' % (
              d1['candidates'], d1['legal'], cert['certified_below'], st['triples'], sample['agree'],
              ' pairs=%d' % E['depth2']['legal_pairs'] if '--pairs' in sys.argv else ''))


if __name__ == '__main__':
    main()
