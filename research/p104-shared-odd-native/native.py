"""Exact native replay and signed physical maps.

Adapted from Ali Romman's independent-helper verifier; native compiler and
Gaussian interpreter retain their source credit. Inventory, COPY monitor and
retimed helper extension by @CubeJerry with substantial OpenAI assistance.
Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip, importlib.util, json, sys
HERE=Path(__file__).resolve().parent
def _sm(m):
    # odd-scalar change: 2,3,5-smooth test (alphabet A = Z[1/2,1/3,1/5]); replaces the power-of-two tests of the dyadic rule
    m=abs(m)
    for p_ in (2,3,5):
        while m%p_==0:m//=p_
    return m==1
def need(ok, why):
    if not ok:
        raise ValueError(why)

def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def add(dst, src, q):
    for k, v in tuple(src.items()):
        value = dst.get(k, 0) + q*v
        if value:
            dst[k] = value
        else:
            dst.pop(k, None)

def span(basis):
    out = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in out, 'Independent binary basis')
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)

def replay(w):
 n=w['public'];N=n+w['owned_fields'];frames=[span(x)for x in w['frames']]
 need(type(n) is int and len(w['initial'])==len(w['final'])==n, 'Public boundary size')
 need(len(w['live'])==len(w['ports'])==104, 'Main port inventory')
 rows=[{r:Q(1)}if r<n else{}for r in range(N)];current=w['initial']+[None]*w['owned_fields']
 owned=set();paid=Counter();erased=[];peak=0;lifetimes=0;scalar=0;copy=0
 for i,e in enumerate(w['program']):
  op,r=e[:2];need(0<=r<N,('role',i))
  if op=='MOVE':
   a,b,private=e[2:];need(current[r]==a and private==(r in owned),('move current',i,e,current[r]))
   need(frames[b]<frames[a]if private else frames[a]<frames[b],('move nesting',i,e))
   current[r]=b;paid[abs(len(w['frames'][b])-len(w['frames'][a]))]+=1
  elif op=='INIT':
   need(r>=n and r not in owned,('init',i));owned.add(r);peak=max(peak,len(owned));lifetimes+=1;rows[r]={};current[r]=e[2];scalar+=2
  elif op=='CLEAR':
   need(r in owned and current[r]==e[2],('clear',i));
   if rows[r]:erased.append(dict(event=i,role=r,frame=e[2]))
   rows[r]={};current[r]=None;owned.remove(r);scalar+=2
  else:
   q,f=Q(e[-2]),e[-1];need(q!=0 and current[r]==f,('scalar frame',i,e,current[r]));a,d=abs(q.numerator),q.denominator
   need(_sm(d) and abs(q)+1<2**16,('scalar alphabet',i))
   if op=='SCALE':
    need(_sm(a),('unit',i));rows[r]={k:v*q for k,v in rows[r].items()};scalar+=2*(abs(a.bit_length()-d.bit_length())+int(q<0))
   else:
    s=e[2];need(s!=r and 0<=s<N and current[s]==f,('scalar source',i,e,current[s]))
    if op=='COPY':need(r in owned and not rows[r],('COPY zero',i));copy+=1
    else:need(op=='ADD',('opcode',i))
    add(rows[r],rows[s],q);scalar+=2*(3+a.bit_length()-1+a.bit_count()+d.bit_length()-1)
 need(not owned and current[:n]==w['final'],'exits')
 for r,row in enumerate(rows):
  expected={r:Q(1)}if r<n else{}
  if r-112 in w['live']:expected[r-112]=Q(1)
  need(row==expected,('endpoint',r,row,expected))
 main=set(w['live'])|{r+112 for r in w['live']}
 helpers=Counter()
 for r in range(n):
  if r not in main:
   a,b=w['initial'][r],w['final'][r];need(frames[a]<frames[b],('target nesting',r));helpers[len(w['frames'][b])-len(w['frames'][a])]+=1
 return dict(public=n,owned_fields=w['owned_fields'],events=len(w['program']),public_inputs=n,owned_lifetimes=lifetimes,peak_owned_fields=peak,real_scalar_allowance=scalar,endpoint_coefficients=N*N,paid=dict(paid),helpers=dict(helpers),erased=erased,peak=peak,lifetimes=lifetimes,scalar=scalar,COPY=copy)

def native(w):
    n = w['public']
    C = load(HERE/'retained/native/clifford_exact.py', 'p104_productive_clifford')
    V = load(HERE/'retained/native/native_verify.py', 'p104_productive_gaussian')
    @lru_cache(None)
    def chart(i):
        return C.canonical_frame(9, tuple(w['frames'][i]))
    recipes = {}
    def check(a,b):
        if (a,b) not in recipes:
            recipe,_ = C.lower_child(chart(a).adjoint().then(chart(b)))
            expected = V.adjoint(V.frame(w['frames'][a],9)) + V.frame(w['frames'][b],9)
            V.equal(V.recipe(recipe),expected,'Native chart change and exact global phase')
            need(recipe['rank'] == abs(len(w['frames'][a])-len(w['frames'][b])), 'Native boundary rank')
            recipes[a,b] = recipe
        return recipes[a,b]
    for e in w['program']:
        if e[0] == 'MOVE':
            check(e[2],e[3])
    main = set(w['live']) | {r+112 for r in w['live']}
    helper_profile = Counter()
    for r in range(n):
        if r not in main:
            helper_profile[check(w['initial'][r],w['final'][r])['rank']] += 1
    adapters = []
    for r,q in zip(w['live'],w['ports']):
        need(w['frames'][w['initial'][r]] == [q], 'Literal central port')
        need(span(w['frames'][w['final'][r+112]]) == frozenset(x for x in range(512) if not (x&q).bit_count()%2), 'Literal output hyperplane')
        tests = [
            (C.cgate(9,q,1).adjoint().then(chart(w['initial'][r])), V.adjoint((('C',q,1),))+V.frame(w['frames'][w['initial'][r]],9)),
            (chart(w['final'][r+112]).adjoint().then(C.cgate(9,q,-1).then(C.fourier(9))), V.adjoint(V.frame(w['frames'][w['final'][r+112]],9))+(('C',q,-1),)+V.fourier(9))]
        for actual,expected in tests:
            recipe,_ = C.lower_child(actual)
            need(recipe['rank'] == 0, 'Free intrinsic main adapter')
            V.equal(V.recipe(recipe),expected,'Main endpoint phase')
            adapters.append(recipe)
    bad = json.loads(json.dumps(next(iter(recipes.values()))))
    bad['left']['phase'] = (bad['left']['phase']+1)%4
    a,b = next(iter(recipes))
    try:
        V.equal(V.recipe(bad),V.adjoint(V.frame(w['frames'][a],9))+V.frame(w['frames'][b],9),'Wrong phase control')
    except ValueError:
        pass
    else:
        raise ValueError('Wrong native phase accepted')
    payload = [[a,b,recipes[a,b]] for a,b in sorted(recipes)] + adapters
    return {'distinct_maps':len(recipes),'main_adapters':len(adapters),'helper_normalizers':2*sum(helper_profile.values()),
            'helpers':dict(helper_profile),'recipe_payload_sha256':sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'wrong_phase_rejected':True, 'proof':'Every signed Pauli image and exact global phase at tensor width 1, for every map listed here. Width 2 is not run on these recipes here: check_a6.py runs it (global phase i^(p f), f = 2) on the 23 owned-rise maps and on one rank-1 MOVE only; no other width, no other map.'}
