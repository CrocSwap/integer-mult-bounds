"""Run #276's prepare -> physical527 -> parity_transform and dump the six-int transcript plus frame tables."""
import sys, json, importlib.util, time, gzip
from pathlib import Path
PKG = Path(sys.argv[1]).resolve(); OUT = Path(sys.argv[2]).resolve(); OUT.mkdir(parents=True, exist_ok=True)
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); sys.modules[name] = m; s.loader.exec_module(m); return m
t0 = time.time()
ctx = load('portable527_prepare', PKG/'prepare.py').prepare(); print('prepared', time.time()-t0, flush=True)
raw = load('portable527_raw_ledger', PKG/'raw_ledger.py').run(ctx); print('raw', time.time()-t0, flush=True)
phys = load('portable527_physical', PKG/'code/physical527.py')
producer = phys.run(dict(ctx), ctx['SOURCE_TEXT'], output_dir=OUT/'producer-bit'); print('physical', time.time()-t0, flush=True)
run = load('portable527_parity', PKG/'parity_transform.py').run(producer, output_dir=OUT/'parity'); print('parity', time.time()-t0, flush=True)
W, C = run['W'], run['C']
rec = run['records']; (OUT/'records.bin').write_bytes(rec.tobytes())
init = run['initial_state']
regs = run['context']['regs']; v = W.v; n = 2*v+len(regs)
used = set(init.values())
for k in range(0, len(rec), 6):
    op,a,b,c,f,z = rec[k:k+6]
    if op==0: used.update((b,c))
    elif op==1: used.add(f)
    elif op==2: used.update((c,f))
for s,z in W.gauge.items(): used.add(z['frame'])
frames = {str(f): dict(B=C.B[f], A=C.A[f], dim=C.dimf[f]) for f in used}
meta = dict(n=n, v=v, R=len(regs), ZERO=run['ZERO'], FULL=run['FULL'], category_names=run['physical']['category_names'],
            regs=regs, gauge={str(2*v+j): dict(frame=W.gauge[r]['frame'], dim=W.gauge[r]['dim'], targets=W.gauge[r]['targets']) for j,r in enumerate(regs) if r in W.gauge},
            donor_streams=sorted(2*v+j for j,r in enumerate(regs) if r in W.donor), borrow=list(run['context']['borrow']),
            paid_histogram=run['physical']['paid_histogram'], paid_rank_mass=run['physical']['paid_rank_mass'], weighted_scalar_events=run['physical']['weighted_scalar_events'],
            scalar_projection_sha256=run['physical']['scalar_projection_sha256'], initial_independent_entrances=run['physical']['initial_independent_entrances'],
            cov={str(t): C.cov[t] for t in range(v)})
(OUT/'initial.json').write_text(json.dumps({str(k):v for k,v in init.items()}))
(OUT/'frames.json').write_text(json.dumps(frames))
(OUT/'meta.json').write_text(json.dumps(meta))
(OUT/'raw.json').write_text(json.dumps(raw, default=str))
print('dumped', len(rec)//6, 'records; n', n, 'v', v, 'R', len(regs), 'frames', len(frames), time.time()-t0, flush=True)
