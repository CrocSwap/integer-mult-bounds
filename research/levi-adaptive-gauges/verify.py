"""Native source specialization, independent DP and symplectic pairing checks."""
from pathlib import Path
from fractions import Fraction as Q
import json,types,sys,random,copy
HERE=Path(__file__).resolve().parent

def load(name,file):
 m=types.ModuleType(name);m.__file__=str(HERE/file);sys.modules[name]=m
 exec(compile((HERE/file).read_bytes(),m.__file__,'exec'),m.__dict__);return m
B=load('levi_native_source','native_source.py');C=load('levi_adaptive_compiler','compiler.py');S=load('levi_suffix','suffix.py')

def rejects(action,label):
 try:action()
 except (ValueError,KeyError,IndexError,StopIteration):return
 raise ValueError('Invalid control accepted: '+label)

def price_program(program,price):return sum(price(e) for e in program)
def native(program,rule):
 def role(r):return ['L',(rule['source_roles'] if r[0]=='X' else rule['target_roles'])[r[1]]]
 out=[]
 for e in program:
  op=[e[0],role(e[1])]+([role(e[2])]+e[3:] if e[0]=='add' else e[2:]);out.append(['scalar',op,rule['frame']])
 return out

def apply(program,x,y):
 values={('X',i):Q(q) for i,q in enumerate(x)}|{('Y',i):Q(q) for i,q in enumerate(y)}
 for e in program:
  t=tuple(e[1])
  if e[0]=='add':values[t]+=Q(e[3],e[4])*values[tuple(e[2])]
  else:values[t]*=Q(e[2],e[3])
 return [values['X',i] for i in range(len(x))],[values['Y',j] for j in range(len(y))]
def symplectic_check(program,n,m,rng):
 # Cotangent coordinates are stored as (dual Y, dual X).
 vectors=[[Q(rng.randrange(-4,5),2) for _ in range(n+m)] for k in range(4)]
 x,y,a,b=vectors
 px=sum(apply(program,x[:n],x[n:]),[]);py=sum(apply(program,y[:n],y[n:]),[])
 dual=C.inverse_dual(program)
 ax,ay=apply(dual,a[n:],a[:n]);bx,by=apply(dual,b[n:],b[:n]);pa=ay+ax;pb=by+bx
 dot=lambda u,v:sum((q*r for q,r in zip(u,v)),Q(0))
 B.need(dot(pb,px)-dot(pa,py)==dot(b,x)-dot(a,y),'Exact hyperbolic symplectic pairing')

def dp_optimum(row,price):
 # Enumerate every edge order and gauge choice in [-2,2], independently of intervals.
 n=len(row);grid=range(-2,3);dp={(0,0):0}
 for mask in range(1<<n):
  for b in grid:
   if (mask,b) not in dp:continue
   for i,q in enumerate(row):
    if mask>>i&1:continue
    for t in grid:
     coeff=q*C.power(t);cost=dp[mask,b]+2*abs(t-b)+price(['add',['Y',0],['X',i],coeff.numerator,coeff.denominator]);key=(mask|1<<i,t)
     dp[key]=min(dp.get(key,cost),cost)
 return min(dp[(1<<n)-1,b]+2*abs(b) for b in grid if ((1<<n)-1,b) in dp)

def verify():
 inputs=B.authenticated();words,chart,v,n=B.sources(inputs)
 prior=json.loads(next(data for path,data in inputs.items() if path.endswith('/native-splice-replay/PATCHES.json')))
 borrow=B.extract(next(data for path,data in inputs.items() if path.endswith('/borrowed-rankone/compiler.py')),{'borrowed_candidates','valuation','add_cost','power'})
 patches=[];plans=[];rng=random.Random(20261022)
 for rule in [r for r in prior if r['direction']=='forward']:
  M=[[Q(q) for q in row] for row in rule['matrix']];p=C.compile_rows(M)
  options=[p]+borrow.borrowed_candidates(M);selected=min(options,key=lambda x:x['new']);program=selected['program']
  B.need(price_program(program,n.primitive_allowance)==selected['new'],'Fully charged adaptive/borrowed scalar bill')
  symplectic_check(program,len(M[0]),len(M),rng)
  back=next(r for r in prior if r['direction']=='backward' and r['source_indices']==rule['source_indices'])
  # Source indices happen to match here, but role/matrix semantics are checked independently.
  for rr,pp in [(rule,program),(back,C.inverse_dual(program))]:
   updated=copy.deepcopy(rr);updated['replacement']=native(pp,updated);patches.append(updated)
  plans.append({'source_indices':rule['source_indices'],'adaptive_cost':p['new'],'selected_cost':selected['new'],'selected_mechanism':selected.get('mechanism'),'row_intervals':[r['interval'] for r in p['rows']]})
 new,local=B.install(words,patches,n.primitive_allowance)
 B.need(new==B.read('NATIVE.json'),'Committed complete adaptive word')
 B.need(sum(r['new_cost'] for r in local if r['direction']=='forward')==616,'Four-window total')
 complete=B.check_whole(new,chart,v,n)
 for d,wanted in [('forward',157970),('backward',158018)]:B.need(complete[d]['prefix']['real_scalar_allowance']==wanted,'Whole native allowance')
 suffix={d:S.summarize(new[d],d=='backward') for d in ['forward','backward']}
 B.need(suffix['forward']['uniform_add_scale_bound']=='1328' and suffix['backward']['uniform_add_scale_bound']=='4871','Measured logical suffix bounds')
 for _ in range(30):
  row=[Q(rng.choice([-3,-1,1,3]))*C.power(rng.randrange(-2,3)) for i in range(rng.randrange(1,5))]
  p=C.row_plan(row,0);B.need(p['new']==dp_optimum(row,n.primitive_allowance),'Independent order-and-gauge dynamic program')
  symplectic_check(p['program'],len(row),1,rng)
 bad=copy.deepcopy(patches);r=next(r for r in bad if r['direction']=='backward' and len(r['matrix'])==38)
 r['replacement']=list(reversed(r['replacement']))
 rejects(lambda:B.install(words,bad,n.primitive_allowance),'wrong inverse-dual execution order')
 bad=copy.deepcopy(patches);r=next(r for r in bad if r['direction']=='forward' and len(r['matrix'][0])==38)
 scale=next(i for i,e in enumerate(r['replacement']) if e[1][0]=='scale');r['replacement'].pop(scale)
 rejects(lambda:B.install(words,bad,n.primitive_allowance),'missing adaptive gauge transition')
 return {'status':'PASS_LEVI_ADAPTIVE_NATIVE_GAUGES','plans':plans,'patches':patches,'whole_native_checks':complete,'suffix_checks':suffix,'local_cost_old':766,'local_cost_previous':666,'local_cost_new':616,'saving_over_previous_per_orientation':50,'saving_over_original_per_orientation':150,'additional_fields':0,'new_recursive_calls':0,'independent_order_gauge_dp_cases':30,'symplectic_pairing_checks':34,'new_kappa':False,'fresh_Lean_audit':False}

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();result=json.loads(json.dumps(verify()))
 if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
 else:B.need(result==B.read('RESULT.json'),'Deterministic semantic receipt')
 print(json.dumps({k:v for k,v in result.items() if k not in ['plans','patches','whole_native_checks','suffix_checks']},sort_keys=True))
