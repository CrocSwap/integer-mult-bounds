"""Run the package pipeline through a stage of portable_bit.STAGES and dump records/frames/meta. Usage: dump_at.py PKG OUT STAGE
Chafik Boukhalfa (chafreaky), Anthropic Claude assistance; Apache-2.0."""
import sys, json, importlib.util, time
from pathlib import Path
PKG = Path(sys.argv[1]).resolve(); OUT = Path(sys.argv[2]).resolve(); OUT.mkdir(parents=True, exist_ok=True); sys.path.insert(0, str(PKG))
UPTO = sys.argv[3]  # last stage to run (inclusive), or 'none'
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); sys.modules[name] = m; s.loader.exec_module(m); return m
t0 = time.time()
ctx = load('portable527_prepare', PKG/'prepare.py').prepare()
raw = load('portable527_raw_ledger', PKG/'raw_ledger.py').run(ctx)
producer = load('portable527_physical', PKG/'code/physical527.py').run(dict(ctx), ctx['SOURCE_TEXT'], output_dir=None)
run = load('portable527_parity', PKG/'parity_transform.py').run(producer)
STAGES = load('portable527_bitstages', PKG/'portable_bit.py').STAGES
todo = [] if UPTO == 'none' else list(STAGES[:STAGES.index(UPTO)+1])
for st in todo:
    if st.startswith('reorder'):
        run = load('portable527_reorder', PKG/'reorder_transform.py').run(run, tag=st)
    else:
        run = load('portable527_'+st, PKG/(st.rstrip('0123456789')+'_transform.py') if not (PKG/(st+'_transform.py')).exists() else PKG/(st+'_transform.py')).run(run)
    print(st, time.time()-t0, flush=True)
W, C = run['W'], run['C']
rec = run['records']; (OUT/'records.bin').write_bytes(rec.tobytes())
init = run['initial_state']; regs = run['context']['regs']; v = W.v; n = 2*v+len(regs)
final = dict(run.get('final_state') or init)
if not run.get('final_state'):
    for k in range(0, len(rec), 6):
        if rec[k] == 0: final[rec[k+1]] = rec[k+3]
used = set(init.values()) | set(final.values())
for k in range(0, len(rec), 6):
    op,a,b,c,f,z = rec[k:k+6]
    if op==0: used.update((b,c))
    elif op==1: used.add(f)
    elif op==2: used.update((c,f))
for s,z in W.gauge.items(): used.add(z['frame'])
frames = {str(f): dict(B=C.B[f], A=C.A[f], dim=C.dimf[f]) for f in used}
meta = dict(n=n, v=v, R=len(regs), ZERO=run['ZERO'], FULL=run['FULL'], category_names=run['physical']['category_names'], stages=todo,
            regs=regs, gauge={str(2*v+j): dict(frame=W.gauge[r]['frame'], dim=W.gauge[r]['dim']) for j,r in enumerate(regs) if r in W.gauge},
            donor_streams=sorted(2*v+j for j,r in enumerate(regs) if r in W.donor), borrow_streams=sorted(2*v+j for j,r in enumerate(regs) if r in run['context']['borrow']),
            paid_histogram=run['physical']['paid_histogram'], paid_rank_mass=run['physical']['paid_rank_mass'],
            scalar_projection_sha256=run['physical']['scalar_projection_sha256'], raw_sha256=__import__('hashlib').sha256(rec.tobytes()).hexdigest())
(OUT/'initial.json').write_text(json.dumps({str(k):v for k,v in init.items()}))
(OUT/'final.json').write_text(json.dumps({str(k):v for k,v in final.items()}))
(OUT/'frames.json').write_text(json.dumps(frames))
(OUT/'meta.json').write_text(json.dumps(meta))
(OUT/'raw.json').write_text(json.dumps(raw, default=str))
print('dumped', len(rec)//6, 'records; n', n, 'v', v, 'frames', len(frames), time.time()-t0, flush=True)
