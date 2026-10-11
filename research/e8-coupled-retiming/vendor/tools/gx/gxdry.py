"""gxdry.py: DRY RUN of a gcert/1 file: Python mirror of both checks, kernel sizes,
segment plan, expected exponents (whole-block and per-rank, 8 and 10 decimals) in the bridged word B_2.
usage: gxdry.py <gcert1.json[.gz]> [gseg=<gates per replay segment>] [batches=<scalar batches>] [tsplit=<j>] [norate] [digits]"""
import sys, time, json
import gxpaths
import gxcore as gc
import gxunit as gu


def main():
    path = sys.argv[1]
    opt = dict(a.split('=') for a in sys.argv[2:] if '=' in a)
    flags = [a for a in sys.argv[2:] if '=' not in a]
    t0 = time.time()
    D = gc.normal(gc.load(path))
    plan = gu.plan(D, opt)
    try:
        M = gc.mirror(D, gmax=plan['gseg'], batches=plan['batches'])
    except gc.Reject as e:
        print('REJECTED by the Python mirror:', e)
        sys.exit(2)
    nm = path.split('/')[-1]
    h, v, R = D['h'], D['v'], D['R']
    nadds = sum(len(g[3]) for g in D['A'] + D['B'])
    print('%s: MIRROR ACCEPTS (label side E0 E1 E2 E6, scalar side E3 E4 E5%s)  %.1f s'
          % (nm, ' E7' if D['ext'] else '', time.time() - t0))
    print('  h=%d v=%d R=%d N=%d cst=%d ext=%d  registers=%d frames=%d (masks %d)' % (
        h, v, R, D['N'], D['cst'], len(D['ext']), 2 * v + R, len(D['frames']), sum(M['dim'])))
    print('  gates A=%d B=%d single adds=%d  register visits=%d  blocks=%d  distinct pairs=%d (mask ops <= %d)  y-y pairs=%d'
          % (len(D['A']), len(D['B']), nadds, sum(M['visits']), sum(M['hist'].values()), len(M['pairs']),
             M['pair_work'], M['ysh']))
    S = M['scal']
    print('  scalar: entry updates=%d  entries after A=%d  batches=%d %s' % (S['updates'], S['afterA'], len(S['batches']),
          S['per_batch'] if len(S['per_batch']) <= 12 else ''))
    if 'digits' in flags:
        print('  scalar digits {class: (denominator, largest numerator)}:', gc.digits(D))
    print('  blocks of one invocation (rank: count):', M['hist'])
    print('  by class:', M['H'])
    L = M['lab']
    print('  PLAN: frame-table subtries=%d  replay segments=%d at gates %s (visits %s, blocks %s) + final climbs (%d gates, %d blocks)'
          % (2 ** plan['tsplit'], len(M['visits']), M['cuts'], M['visits'], [len(r) for r in L['rs']], len(L['fins']), len(L['rF'])))
    print('        scalar batches=%d + y check; most registers named by one gate=%d' % (len(S['batches']), L['most']))
    print('  kernel evaluations in all: %d  (+ %d rank counts on explicit lists)' % (
        2 ** plan['tsplit'] + len(M['visits']) + 1 + 2 + len(S['batches']) + 1, 3 * (h + 2)))
    if 'norate' not in flags and not D['ext']:
        u = gu.unit(M['hist'], h, v, R, D['cst'])
        print('  unit of B_2: m=%d W=%d D=%d tally=%d  block list %s' % (u['m'], u['W'], u['D'], u['W'] * u['m'] - u['D'],
                                                                         sorted(u['H'].items())))
        for B, s in ((8, 13), (10, 40)):
            r = gu.rates(u, B, s)
            print('  %d decimals, fill 1 - 2^-%d: whole-block %d (evaluated %d holds / %d fails); per-rank %d (evaluated %d / %d)'
                  % (B, s, r['A'], r['A_eval'], r['A_fails'], r['A_rank'], r['A_rank_eval'], r['A_rank_fails']), flush=True)
    elif D['ext']:
        print('  no rate: exterior gauges (rule 2) are not on the path; N is short of the unit tally by the ext dimensions')


if __name__ == '__main__':
    main()
