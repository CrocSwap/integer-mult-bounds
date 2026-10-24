"""Independent literal local census and positive-series exact price audit.

No primary price, tail, or interval implementation is imported. The numerical
engine uses base10 outward intervals,60-term atanh logs and90-term exponentials.
Native correctness is checked separately by the two emitted-word interpreters.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import ast,gzip,hashlib,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE));sys.dont_write_bytecode=True
import exact_series as X

def need(c,m):
    if not c:raise ValueError(m)

def census():
    sources=json.loads((HERE/'SOURCES.json').read_bytes())
    for item in sources['files']:
        if item['usage']=='input':
            data=(ROOT/item['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest()==item['sha256'],'Independent source authentication')
    base=ROOT/'research/kappa-rebuild/bit'
    frames=json.loads((base/'sources/pr589-regenerated/records/frames.json').read_bytes())['frames']
    word=json.loads(gzip.decompress((ROOT/'research/bit-compact-carrier-retirement/provider/inputs/WORD.json.gz').read_bytes()))
    need(len(word['start'])==len(word['final'])==658 and all(x==0 for x in word['start'][222:]),
         'Actual independent helper inputs')
    local=Counter()
    for op,d,s,c,f,tag in word['records']:
        if op==0:
            need(frames[str(c)]['dim']-frames[str(s)]['dim']==f,'Actual proper nested query rank')
            local[f]+=1
        elif op==2:local[frames[str(c)]['dim']]+=1
    helper=Counter(frames[str(f)]['dim']for f in word['final'][222:])
    need(helper=={4:4,8:432},'Partial jobs from actual exit frames')
    # Derive the old primitive from its pinned source literal, independently
    # of both primary invoice functions.
    nodes=ast.parse((base/'mixed_productive_bit.py').read_bytes()).body
    choices=[]
    for n in nodes:
        if not isinstance(n,ast.Assign)or not any(isinstance(t,ast.Name)and t.id=='LOCAL'for t in n.targets):continue
        v=n.value
        if isinstance(v,ast.Call):
            need(isinstance(v.func,ast.Name)and v.func.id=='Counter'and len(v.args)==1 and not v.keywords,
                 'Literal Counter wrapper only')
            v=v.args[0]
        choices.append(ast.literal_eval(v))
    need(len(choices)==1,'Unambiguous committed LOCAL source literal')
    old_local=choices[0]
    row=json.loads((ROOT/'research/query-thinned-controllers/BIT-CONTROLLER.json').read_bytes())['invoice']
    calls=row['thick_calls'];need(calls==18,'Actual full invocations')
    target=Counter({int(k):v for k,v in row['targets'].items()})
    paid=Counter({int(k):v for k,v in row['paid'].items()})
    target[8]-=calls*439
    for k,n in helper.items():target[k]+=calls*n
    for k,n in old_local.items():paid[k]-=calls*n
    for k,n in local.items():paid[k]+=calls*n
    return dict(target),dict(paid),dict(local),dict(helper),row

def check(target,paid,p):
    tested,uniform,gap,atom,b,old,ag=[F(p[k])for k in ('tested','uniform','cover_gap','atom','admitted','old_backend','alpha_gap')]
    t=1-tested;T=X.moment(target,t);P=X.moment(paid,t)
    alpha=X.div(P,T)
    gamma=X.div(X.moment(paid,t+F(1,5)),X.mul(X.power(17,F(1,5)),T))
    delta=X.div((F(sum(target.values())*18),)*2,X.mul(X.power(17,tested),T))
    need(alpha[1]<1-ag and gamma[1]<F(31,32)and delta[1]<F(19,20),'Complete charged tensor tails')
    need(F(31,32)**128<F(1,16)and F(19,20)**128<F(1,16),'Both geometric tail blocks')
    need(1/(1+1024*ag)+F(4,2**32)<1,'Strict total contraction, both tails paid')
    h=F(1,64);z=1-uniform;z0=(t+z)/2;d=z0-t
    H0=X.ceil((d*(5+8*h)*1024+1+8*1024*(1-z0))/(h*d))
    H1=X.floor(H0*(1-z0)/(z-z0))+1
    need(17**64<18**63 and max(target)<256,'Strict exit/source rank separation')
    need(H0>=8192 and H0*h*d>=d*(5+8*h)*1024+1+8*1024*(1-z0),'Integer compiler induction')
    need(H1*(z-z0)>H0*(1-z0),'Finite uniform dimension')
    c1=uniform-gap;a=(1-atom)*c1+atom*old
    need(tested>uniform>c1>0 and atom>a>b>0 and atom<1-a,'Ordinary adapter/mixed/stock exponents')
    need(F(p['prime_coefficient'])>256/gap,'Full delayed-cover fallback prime allowance')
    return {'alpha':alpha,'gamma':gamma,'delta':delta,'H0':H0,'H1':H1,'ordinary':a,'admitted':b}

def audit():
    target,paid,local,helper,old_invoice=census()
    result=json.loads((HERE/'RESULT.json').read_bytes())
    need({str(k):v for k,v in target.items()}==result['invoice']['targets']and
         {str(k):v for k,v in paid.items()}==result['invoice']['paid'],'Independent complete census')
    params=result['ordinary_BIT']['params'];calc=check(target,paid,params)
    need(calc['ordinary']==F(result['ordinary_BIT']['ordinary_exact'])and calc['admitted']==F('0.0034597'),
         'Exact admitted ordinary coefficient')
    need(calc['H0']==result['ordinary_BIT']['tail']['compiler_H0']and
         calc['H1']==result['ordinary_BIT']['tail']['uniform_H1'],'Independent compiler integers')
    for name in ('alpha','gamma','delta'):
        display=result['ordinary_BIT']['tail'][name]
        need(F(display['lower'])<=calc[name][0]<=calc[name][1]<=F(display['upper']),
             'Independent interval lies within primary displayed enclosure')
    controls={}
    for name,change in [('old_atom',{'atom':'0.0034'}),('closed_cover_gap',{'cover_gap':str(F(1,2**18))}),
                        ('overclaimed_admission',{'admitted':'0.00346'}),('unfunded_alpha_gap',{'alpha_gap':'1/10000000'})]:
        try:check(target,paid,dict(params,**change))
        except ValueError:controls[name]='REJECT'
        else:raise ValueError('Unrejected arithmetic mutation '+name)
    # Direct raw-root sign brackets, not more digits of an unchanged invoice.
    roots={}
    oldT={int(k):v for k,v in old_invoice['targets'].items()};oldP={int(k):v for k,v in old_invoice['paid'].items()}
    for name,T,P,lo,hi in [('old',oldT,oldP,'0.003464248972023961106948','0.003464248972023961106949'),
                          ('new',target,paid,'0.003475458064076428997514','0.003475458064076428997515')]:
        a,b=F(lo),F(hi)
        ta,pa=X.moment(T,1-a),X.moment(P,1-a)
        tb,pb=X.moment(T,1-b),X.moment(P,1-b)
        need(ta[0]>pa[1]and tb[1]<pb[0],'Independent strict raw root bracket')
        roots[name]={'lower':lo,'upper':hi}
    return {'status':'PASS_INDEPENDENT_LITERAL_CENSUS_AND_EXACT_SERIES',
            'paid_queries':sum(paid.values()),'original_fields':sum(target.values()),
            'local':local,'helpers':helper,'H0':calc['H0'],'H1':calc['H1'],
            'ordinary':str(calc['ordinary']),'admitted':str(calc['admitted']),
            'raw_roots':roots,'rejected_controls':controls,'new_whole_kappa':None}

if __name__=='__main__':print(json.dumps(audit(),indent=2,sort_keys=True))
