#!/usr/bin/env python3
"""CERTKIT builder: compile Nov15 modules in order with runlean.sh (3.5 GB RSS guard), one at a time.
usage: build.py [--skip-fresh] MOD [MOD ...]   or   build.py --chain TAG   or   build.py --cert NAME
Refuses to start a module while another `lean` process runs (no waiting loops: rerun later).  Appends to build.log."""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))   # package root (paths are package-relative)
LEAN = os.path.join(ROOT, 'lean')
RUNLEAN = os.path.join(LEAN, 'tools', 'runlean.sh')


def fresh(m):
    src = os.path.join(LEAN, 'Nov15', m + '.lean'); ol = os.path.join(LEAN, '.lake', 'build', 'lib', 'lean', 'Nov15', m + '.olean')
    return os.path.exists(ol) and os.path.getmtime(ol) > os.path.getmtime(src)


def build(mods, skip_fresh=True):
    tot = 0; log = open(os.path.join(HERE, 'build.log'), 'a')
    for m in mods:
        if skip_fresh and fresh(m):
            print(f'{m}: fresh'); continue
        if subprocess.run(['pgrep', '-x', 'lean'], capture_output=True, text=True).stdout.strip():
            print(f'{m}: another lean is running; stop here (rerun later)'); return False
        t = time.time()
        r = subprocess.run([RUNLEAN, os.path.join('Nov15', m + '.lean'),
                            os.path.join('.lake', 'build', 'lib', 'lean', 'Nov15', m + '.olean')],
                           capture_output=True, text=True, cwd=LEAN)
        dt = time.time() - t; tot += dt
        line = (r.stdout.strip().splitlines() or ['?'])[0]
        print(f'{m}: {line}'); log.write(f'{time.strftime("%H:%M")} {m}: {line}\n'); log.flush()
        if 'rc=0' not in line:
            print(r.stdout[-3000:]); return False
        ax = [l for l in open('/tmp/claude-501/lean_last.log').read().splitlines() if 'axioms' in l]
        for l in ax:
            print('   ', l)
            if 'sorryAx' in l or 'native' in l.lower():
                print('BAD AXIOMS'); return False
    print(f'total {tot:.0f}s')
    return True


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == '--chain':
        mods = json.load(open(os.path.join(HERE, f'chain_{a[1]}.json')))['modules']
    elif a[0] == '--cert':
        mods = json.load(open(os.path.join(HERE, f'cert_{a[1]}.json')))['modules']
    else:
        mods = a
    sys.exit(0 if build(mods) else 1)
