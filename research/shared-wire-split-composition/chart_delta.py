import json,gzip,pathlib,sys,importlib.util,copy
if not __debug__:raise RuntimeError('Run without -O; assertions are proof checks.')
ROOT=pathlib.Path(__file__).resolve().parent;SRC=ROOT
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
C=load(SRC/'frozen/clifford_exact.py','split_compiler');V=load(SRC/'frozen/native_verify.py','split_native')
base=json.load(gzip.open(SRC/'data/main_6936.json.gz'));w=json.load(gzip.open(sys.argv[1]));assert w['frames']==base['frames']
def maps(z):
 ms={(e[2],e[3])for e in z['program']if e[0]=='MOVE'};main=set(z['live'])|{r+112 for r in z['live']}|set(z['hosted']['X2'])|set(z['hosted']['Y2'])
 ms|={(z['initial'][r],z['final'][r])for r in range(z['public'])if r not in main};return ms
old=maps(base);new=maps(w);charts={};payload=[]
def chart(f):
 if f not in charts:charts[f]=C.canonical_frame(9,tuple(w['frames'][f]))
 return charts[f]
for a,b in sorted(new-old):
 recipe,_=C.lower_child(chart(a).adjoint().then(chart(b)));expected=V.adjoint(V.frame(w['frames'][a],9))+V.frame(w['frames'][b],9)
 V.equal(V.recipe(recipe),expected,'new exact chart map plus global phase');assert recipe['rank']==abs(len(w['frames'][a])-len(w['frames'][b]));payload.append([a,b,recipe])
a,b,recipe=payload[0]
bad=copy.deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4
try:V.equal(V.recipe(bad),V.adjoint(V.frame(w['frames'][a],9))+V.frame(w['frames'][b],9),'wrong phase must fail')
except ValueError:pass
else:raise AssertionError('wrong phase accepted')
print('PASS_CHART_DELTA',len(old),'base maps',len(new),'new total',len(new-old),'introduced',len(old-new),'retired')
result={'word':'data/final.json.gz','base_maps':len(old),'total_maps':len(new),'introduced':sorted(new-old),'retired':sorted(old-new),'recipes':payload}
if '--write' in sys.argv:
 (ROOT/'chart_delta.json').write_text(json.dumps(result,indent=1))
else:
 assert json.loads((ROOT/'chart_delta.json').read_text())==json.loads(json.dumps(result)), 'Frozen chart receipt must replay exactly'
