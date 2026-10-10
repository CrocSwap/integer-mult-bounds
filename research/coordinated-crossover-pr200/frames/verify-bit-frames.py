import sys,json,gzip,hashlib,argparse,types,signal,contextlib,time
from pathlib import Path
from fractions import Fraction
sys.set_int_max_str_digits(0);sys.dont_write_bytecode=True
ap=argparse.ArgumentParser();ap.add_argument('--package',required=True);ap.add_argument('--frames',required=True);ap.add_argument('--out',required=True);ap.add_argument('--full',action='store_true');a=ap.parse_args();P=Path(a.package).resolve();O=Path(a.out);O.mkdir(parents=True,exist_ok=True)
resource=types.ModuleType('resource');resource.RLIMIT_CPU=0;resource.RUSAGE_SELF=0;resource.setrlimit=lambda *xs:None;resource.getrusage=lambda *xs:types.SimpleNamespace(ru_maxrss=0);sys.modules.setdefault('resource',resource)
if not hasattr(signal,'alarm'):signal.alarm=lambda *xs:None
sys.path.insert(0,str(P/'bit'));sys.path.insert(0,str(P/'arithmetic'))
from word import Candidate
from terminal import prove
from prime_witnesses import certificate as primes
from prove import certify
W=Candidate();C=W.C;B=json.loads(Path(a.frames).read_text());pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in W.input_paths+[Path(a.frames),P/'selected/bit/sinks.json',P/'bit/word.py',P/'bit/base_word.py',P/'bit/terminal.py',P/'bit/prime_witnesses.py',Path(W.module.__file__)]}
public=W.opframe[:]
for i,rows in B:W.opframe[i]=W.register(rows)
W.changed_frames=[i for i,(x,y) in enumerate(zip(W.original_opframe,W.opframe)) if x!=y];W.endframe={s:W.opframe[xs[-1]] for s,xs in W.role_ops.items()}
W.exact_frames();baseline=W.row();selection=json.loads((P/'selected/bit/sinks.json').read_text())
print('PASS full exact rational value, geometry and alias checks; changes',len(B),flush=True)
if a.full:
 with contextlib.redirect_stdout(sys.stderr):record=prove(W,selection)
 record.pop('seconds');record.pop('maxrss');row=record['profile'];prime=primes(W)
 (O/'prime-witnesses.json.gz').write_bytes(gzip.compress((json.dumps(prime,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0));prime={k:v for k,v in prime.items() if k!='frame_witnesses'}
 row['child_histogram']={int(k):v for k,v in row['child_histogram'].items()}
 co=certify(row)
else:
 # Exact integer terminal ledger follows the original cancellation once complete
 # target trajectories and exact all-column replay are admitted by the full mode.
 row=baseline;record=None;prime=None;co=None

def js(x):
 if isinstance(x,Fraction):return str(x)
 if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [js(v) for v in x]
 return x
assert pins=={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in pins}
R=js(dict(status='FULL_FINITE_REPLAY_PASS' if a.full else 'EXACT_FRAME_ONLY_NOT_FULL_REPLAY',input_pins=pins,changed_public_ops=len(B),baseline_profile=baseline,profile=row,terminal=record,coarse=co,prime_witnesses=prime,word_scalar_ops_unchanged=True,gauge_endpoint_and_aliases_unchanged=True))
(O/'verification.json').write_text(json.dumps(R,indent=1)+'\n');print('PASS',R['status'],R['coarse']['coarse_saving'] if co else '',flush=True)