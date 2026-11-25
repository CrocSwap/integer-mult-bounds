"""Run audit_allcold.py with the same checks and byte-identical outputs, faster.

1. copy.deepcopy -> pickle round-trip (equal, independent copies with the same aliasing for the plain
   dict/list/tuple/int/str data the audit copies; the mutation controls deep-copy the whole template per control).
2. The mutation controls (independent of each other: each is deepcopy -> mutate -> audit -> must be rejected) are sharded
   over AUDIT_FAST_SHARDS processes. Every control still runs and must be rejected; shard 0 merges the control names in
   their original order and writes the report exactly as the unmodified script does.
Usage: audit_fast.py AUDIT_SCRIPT BASE HOSTED REPORT [--mutation-controls]   (run via run_portable.py like the original)
"""
import copy, json, os, pickle, subprocess, sys, time
from pathlib import Path

_real = copy.deepcopy


def _fast(x, memo=None):
    if memo is not None:
        return _real(x, memo)
    return pickle.loads(pickle.dumps(x, pickle.HIGHEST_PROTOCOL))


copy.deepcopy = _fast
script = Path(sys.argv[1]).resolve()
shards = int(os.environ.get('AUDIT_FAST_SHARDS', '1'))
shard = int(os.environ.get('AUDIT_FAST_SHARD', '0'))
src = script.read_text(encoding='utf-8')
if shards > 1 and '--mutation-controls' in sys.argv[2:]:
    old_reject = """def reject(name,mut):
 if '--mutation-controls' not in sys.argv[4:]:return
 q=copy.deepcopy(ct);mut(q)
 try:audit(q)
 except(AssertionError,KeyError,IndexError,ValueError,TypeError):controls.append(name)
 else:raise AssertionError('ACCEPTED '+name)
"""
    new_reject = """_idx=[0];_own=[]
def reject(name,mut):
 if '--mutation-controls' not in sys.argv[4:]:return
 i=_idx[0];_idx[0]+=1
 if i%_AF_SHARDS!=_AF_SHARD:return
 q=copy.deepcopy(ct);mut(q)
 try:audit(q)
 except(AssertionError,KeyError,IndexError,ValueError,TypeError):controls.append(name);_own.append((i,name))
 else:raise AssertionError('ACCEPTED '+name)
"""
    marker = "\nreport=dict(status='PASS_INDEPENDENT_ASYNC_WHOLE_OWNER_CONTROLLER_PHASES_AND_SPECTATORS'"
    assert src.count(old_reject) == 1 and src.count(marker) == 1, 'audit script layout changed'
    merge = """
import json as _j,sys as _s,time as _t
_part=Path(os.environ['AUDIT_FAST_PARTIAL'])
if _AF_SHARD!=0:
 _part.with_suffix('.tmp').write_text(_j.dumps([_idx[0],_own]));_part.with_suffix('.tmp').replace(_part.with_name(_part.name+'.%d'%_AF_SHARD));_s.exit(0)
_all=list(_own);_total=_idx[0]
for _k in range(1,_AF_SHARDS):
 _f=_part.with_name(_part.name+'.%d'%_k)
 while not _f.exists():
  _t.sleep(0.2)
  assert all(_p.poll() in (None,0) for _p in _AF_PROCS),'a mutation-control shard failed'
 _n,_o=_j.loads(_f.read_text());_f.unlink();assert _n==_total,'shards disagree on control count';_all+=[tuple(x) for x in _o]
assert sorted(i for i,_ in _all)==list(range(_total)),'every control must run exactly once and be rejected'
controls[:]=[n for i,n in sorted(_all)]
for _p in _AF_PROCS:assert _p.wait()==0
"""
    src = src.replace(old_reject, new_reject).replace(marker, merge + marker)
    if shard == 0:
        part = Path(sys.argv[4]).parent / '.audit-fast-partial'
        env0 = dict(os.environ, AUDIT_FAST_PARTIAL=str(part))
        os.environ['AUDIT_FAST_PARTIAL'] = str(part)
        rp = Path(os.environ['MULTICOLD_SOURCE']) / 'code/run_portable.py'
        procs = []
        part.parent.mkdir(parents=True, exist_ok=True)
        for old in part.parent.glob(part.name + '.*'):
            old.unlink()
        for k in range(1, shards):
            e = dict(os.environ, AUDIT_FAST_SHARD=str(k))
            procs.append(subprocess.Popen([sys.executable, '-B', str(rp), str(Path(__file__).resolve()), str(script)] + sys.argv[2:],
                                           env=e, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)))
        g = {'_AF_SHARDS': shards, '_AF_SHARD': 0, '_AF_PROCS': procs}
    else:
        os.environ.setdefault('AUDIT_FAST_PARTIAL', str(Path(sys.argv[4]).parent / '.audit-fast-partial'))
        g = {'_AF_SHARDS': shards, '_AF_SHARD': shard, '_AF_PROCS': []}
else:
    g = {}
g.update({'__file__': str(script), '__name__': '__main__'})
sys.argv = sys.argv[1:]
sys.path.insert(0, str(script.parent))
exec(compile(src, str(script), 'exec'), g)
