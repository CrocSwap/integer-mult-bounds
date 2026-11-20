#!/usr/bin/env python3
"""Regenerate the large DATA modules of the Lean closure (not stored in the package) and check them against REGEN.json.

  python3 tools/regen.py [--only t7669|w_s4] [--check-only]

Writes into lean/Nov15/ (standard library only, one process):
  t7669 : unigen/gen_inhabit.py   data/t7669.json.gz -> UniInhabitEvs/Tabs/Tabs2            (~1 s)
          unigen/gen_rowsp.py     -> UniRowsA{Par,Segs,Ck0..61,Seg0..60,assembly}  (143 files, ~80 s)
  w_s4  : gen_chain.data_files    data/w_s4.json.gz  -> UniInhabitWs4Evs/Tabs/Tabs2 (128-bit slots, ~3 s)
          unigen/gen_rowsp.py     -> UniRowsWs4A{...}                                (191 files, ~330 s)
Every written file must match the sha256 pinned in REGEN.json (340 files); prints PASS_REGEN on success.
"""
import argparse, hashlib, json, os, subprocess, sys, tempfile
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
NOV = os.path.join(PKG, 'lean', 'Nov15')
UG = os.path.join(HERE, 'unigen')
DATA = os.path.join(PKG, 'data')

# exact generator settings of the shipped certificates
ROWS = {
    't7669': dict(Pre='UniRowsA', Ns='UniRows.A', EvNs='UniInhabit.Evs', evs='UniInhabitEvs', tabs='UniInhabitTabs',
                  env=dict(SEEDS='all', D='2764800', CAP='2500')),
    'w_s4': dict(Pre='UniRowsWs4A', Ns='UniRowsWs4.A', EvNs='UniInhabitWs4.Evs', evs='UniInhabitWs4Evs', tabs='UniInhabitWs4Tabs',
                 env=dict(NSI='UniInhabitWs4', SEEDS='all', SLOT='128', CAP='2500', W='80', KB='47', D='88473600', NREG='1697',
                          MODEL='MWs4', TR='trWs4', EVS='evsWs4', LST='LWs4', SOUND='soundWs4', MOK='MWs4_ok',
                          WIMP='Nov15.UniInhabitWs4Word', REGMOD='Nov15.UniInhabitWs4Reg', TABSMOD='Nov15.UniInhabitWs4Tabs',
                          CKEND='Tabs.ck26', OPENS='UniFold7113')),
}


def run(argv, env=None):
    e = dict(os.environ, OMP_NUM_THREADS='1', **(env or {}))
    r = subprocess.run([sys.executable, '-B'] + argv, capture_output=True, text=True, env=e, cwd=NOV)
    if r.returncode:
        print(r.stdout[-1000:], r.stderr[-2000:]); raise SystemExit('FAIL: generator ' + os.path.basename(argv[0]))
    return r.stdout


def regen_t7669():
    print(run([os.path.join(UG, 'gen_inhabit.py'), os.path.join(DATA, 't7669.json.gz'), NOV]).strip())


def regen_w_s4():
    sys.path.insert(0, HERE)
    import gen_chain
    with tempfile.TemporaryDirectory() as td:
        gen_chain.data_files(os.path.join(DATA, 'w_s4.json.gz'), 'Ws4', td)
        for f in ['UniInhabitEvs', 'UniInhabitTabs', 'UniInhabitTabs2']:
            txt = open(os.path.join(td, f + '.lean'), encoding='utf-8').read().replace('UniInhabit', 'UniInhabitWs4')
            with open(os.path.join(NOV, f.replace('UniInhabit', 'UniInhabitWs4') + '.lean'), 'w', encoding='utf-8') as fo:
                fo.write(txt)


def rows(tag):
    R = ROWS[tag]
    env = dict(R['env'], WORD=os.path.join(DATA, tag + '.json.gz'))
    out = run([os.path.join(UG, 'gen_rowsp.py'), os.path.join(NOV, R['evs'] + '.lean'), os.path.join(NOV, R['tabs'] + '.lean'),
               NOV, R['Pre'], R['Ns'], R['EvNs']], env)
    print(out.strip().splitlines()[0])


def check(pins, tags):
    bad, n = [], 0
    for m, rec in pins.items():
        if rec['word'] not in tags:
            continue
        p = os.path.join(NOV, m + '.lean'); n += 1
        if not os.path.exists(p) or hashlib.sha256(open(p, 'rb').read()).hexdigest() != rec['sha256']:
            bad.append(m)
    return n, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', choices=sorted(ROWS)); ap.add_argument('--check-only', action='store_true')
    a = ap.parse_args()
    pins = json.load(open(os.path.join(PKG, 'REGEN.json'), encoding='utf-8'))['modules']
    tags = [a.only] if a.only else ['t7669', 'w_s4']
    if not a.check_only:
        for t in tags:
            (regen_t7669 if t == 't7669' else regen_w_s4)()
            rows(t)
    n, bad = check(pins, tags)
    if bad:
        raise SystemExit('FAIL: %d of %d regenerated modules differ from REGEN.json: %s' % (len(bad), n, bad[:8]))
    print('PASS_REGEN %d modules byte-identical (%s)' % (n, ', '.join(tags)))


if __name__ == '__main__':
    main()
