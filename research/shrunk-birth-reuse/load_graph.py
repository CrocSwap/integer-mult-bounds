"""Original exact reconstruction from PR117's passive operand/root witness."""
import sys,os
if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):raise RuntimeError('Assertions required')
from pathlib import Path
from itertools import combinations
import json,gzip,pickle,time,resource,hashlib
ROOT=Path(__file__).resolve().parent;REPO=Path(os.environ.get('BIRTH_REPO',ROOT.parents[1]));start=time.monotonic();(sys.platform=='darwin' or resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2)));resource.setrlimit(resource.RLIMIT_CPU,(30,30))
p=REPO/'research/shrunk-frames/inputs/complex-dag.json.gz';raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()=='3c034d0aae388ef567a454826f4f48b26fd8a94c71e8ffed4835271b349a783b';w=json.loads(gzip.decompress(raw));h=24;tr=list(combinations(range(h),3));v=len(tr);assert (w['h'],w['v'],w['central_disjoint'],w['center_denominator'])==(24,v,24,21)
args=[None]*(v+1);support=[0]+[1<<i for i in range(v)];core=[0]+[sum(1<<i for i in t)for t in tr];cover=core[:];rank=[0]+[1]*v;kind=[0]+[1]*v
assert len(w['args'])==2*91770
for a,b in zip(w['args'][::2],w['args'][1::2]):
 x=len(args);assert type(a)is int and type(b)is int and 0<a<x and 0<b<x and not(support[a]&support[b]);args.append((a,b));support.append(support[a]|support[b]);core.append(core[a]&core[b]);cover.append(cover[a]|cover[b]);ty=1 if core[x].bit_count()>=2 else 2;kind.append(ty);rank.append(support[x].bit_count()if ty==1 else cover[x].bit_count())
point=[sum(1<<j for j,t in enumerate(tr)if i in t)for i in range(h)];full=(1<<v)-1;roots=w['D']+w['P']+w['A'];targets=list(range(v));idx={t:i for i,t in enumerate(tr)}
assert (len(w['D']),len(w['P']),len(w['A']))==(2024,6072,24)
for t,x in zip(tr,w['D']):assert support[x]==full&~(point[t[0]]|point[t[1]]|point[t[2]])
stars=[(a,b,i)for a,b in combinations(range(h),2)for i in range(h)if i not in(a,b)]
for (a,b,i),x in zip(stars,w['P']):assert support[x]==point[a]&point[b]&~point[i];targets.append(idx[tuple(sorted((a,b,i)))])
for i,x in enumerate(w['A']):assert support[x]==full&~point[i]and rank[x]==23;targets.append(-1)
active=set(roots);todo=roots[:]
while todo:
 x=todo.pop()
 for y in args[x]or():
  if y not in active:active.add(y);todo.append(y)
assert sum(args[x]is not None for x in active)==91770
for x in active:
 for y in args[x]or():
  if kind[y]==kind[x]==1:assert not(core[x]&~core[y]or cover[y]&~cover[x])
  else:assert kind[x]==2 and not cover[y]&~cover[x]
g=dict(h=h,v=v,args=args,support=support,core=core,cover=cover,rank=rank,kind=kind,roots=roots,targets=targets,centers=w['A'],active=sorted(active));blob=pickle.dumps(g,protocol=4);(ROOT/'GRAPH.pkl').write_bytes(blob)
out=dict(status='PASS original full-source/frame reconstruction of pinned117 DAG for118',source_sha256=hashlib.sha256(raw).hexdigest(),graph_sha256=hashlib.sha256(blob).hexdigest(),additions=91770,roots=len(roots),root_order='pair stars ascending i',seconds=time.monotonic()-start,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(ROOT/'GRAPH_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
