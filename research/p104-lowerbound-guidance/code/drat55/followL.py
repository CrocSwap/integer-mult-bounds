"""follow LOOSE's AF2T.state.json; for every cube they closed UNSAT (base f55e), produce+check a DRAT proof with my own cube generator.
bounded by LOOSE's arun pid (exits when it is gone and everything is processed)."""
import json, os, subprocess, time, sys
os.chdir('code/drat55')
L = 'code/loose/'
pid = int(open(L + 'arunF2T.pid').read())
def alive():
    try: os.kill(pid, 0); return True
    except OSError: return False
def name(m, fx):
    b = f'Lf55e_{m}'
    if fx: b += '_' + ','.join(f'{z}:{a}' for z, a in fx).replace(':', 'x').replace(',', 'y')
    return b
while True:
    st = json.load(open(L + 'AF2T.state.json'))
    res = set(l.split('\t')[0] for l in open('results.tsv'))
    todo = [(m, fx) for m, fx, s in st['done'] if s == 'UNSATISFIABLE' and name(m, fx) not in res]
    for m, fx in todo:
        arg = ','.join(f'{z}:{a}' for z, a in fx)
        subprocess.run(['./prodL.sh', 'f55e', str(m), arg])
    if not todo and not alive(): break
    if not todo: time.sleep(120)
print('followL done', len(st['done']))
