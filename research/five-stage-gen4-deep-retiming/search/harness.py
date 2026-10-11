"""Build the parity-fused gen4 word once and cache what frame experiments need."""
import sys, pickle, importlib.util, time
from pathlib import Path
PKG = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / 'cache.pkl'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m

def build():
    t = time.time()
    ctx = load('h_prepare', PKG/'prepare.py').prepare()
    phys = load('h_phys', PKG/'code/physical527.py')
    producer = phys.run(ctx, ctx['SOURCE_TEXT'])
    par = load('h_parity', PKG/'parity_transform.py').run(producer)
    W, C = par['W'], par['C']
    data = dict(records=par['records'].tobytes(), initial=par['initial_state'], ZERO=par['ZERO'], FULL=par['FULL'],
                v=W.v, n=len(par['initial_state']), B=dict(C.B), A=dict(C.A), dimf=dict(C.dimf),
                chi=list(C.chi), cov=list(C.cov), physical=par['physical'])
    OUT.write_bytes(pickle.dumps(data))
    print('cached', time.time()-t)

if __name__ == '__main__':
    build()
