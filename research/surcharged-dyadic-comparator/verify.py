#!/usr/bin/env python3
"""Source-bound exact certificates, original arithmetic, and rejecting controls."""
from pathlib import Path
import copy,hashlib,itertools,json,os,subprocess,sys
from fractions import Fraction as Q
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sources import HERE,pins
import compare as primary
import independent
import fixtures


def need(ok,why):
    if not ok: raise ValueError(why)


def encode(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True)


def run():
    source_pins=pins()
    cases=[];controls=[]
    def checked(a,b,m,W):
        cert=primary.compare(a,b,m,W)
        need(independent.check(a,b,m,W,cert)==cert['order'],'independent verdict')
        return cert
    def reject(name,action):
        try: action()
        except (ValueError,TypeError) as error: controls.append({'name':name,'reason':str(error)})
        else: raise ValueError('control accepted: '+name)
    for quadratic in (False,True):
        a,b,m,W,s=fixtures.tie(quadratic)
        cert=checked(a,b,m,W)
        need(cert['order']==0 and len(cert['gcd'])==(3 if quadratic else 2),'exact tie degree')
        need(sum(a.values())!=sum(b.values()) and s**10<2,'unequal count and original exponent domain')
        cases.append({'name':'quadratic tie' if quadratic else 'rational tie','a':a,'b':b,'m':m,'W':W,'certificate':cert})
    (a,b),m,W=fixtures.negative_factor()
    cert=checked(a,b,m,W)
    need(cert['gcd']==['3','1'] and cert['order']!=0,'negative-only common factor')
    cases.append({'name':'shared negative root is not equality','a':a,'b':b,'m':m,'W':W,'certificate':cert})
    false_equal={'status':'EXACT_EQUAL','order':0,'gcd':['3','1'],
                 'quotients':[list(map(str,primary.divide(primary.polynomial(p,m,W),[3,1])[0])) for p in (a,b)]}
    reject('nonconstant gcd alone is insufficient',lambda:independent.check(a,b,m,W,false_equal))
    N=64*1000*10**200;a={1:N};b={1:N+1};m=64;W=1001*10**200
    cert=checked(a,b,m,W)
    need(cert['order']==1 and cert['steps']>512 and cert['gcd']==['1'],'constant gcd and deep separation')
    cases.append({'name':'unequal roots need more than 512 refinements','a':a,'b':b,'m':m,'W':W,'certificate':cert})
    budgeted=primary.compare(a,b,m,W,max_steps=0)
    need(budgeted['status']=='UNRESOLVED' and budgeted['order'] is None,'explicit budget does not claim a tie')
    reject('unresolved cannot be certified as equal',lambda:independent.check(a,b,m,W,budgeted))
    bad=copy.deepcopy(cert);bad['order']=-cert['order']
    reject('reversed order',lambda:independent.check(a,b,m,W,bad))
    a={1:64,4:4};b={1:56,2:10,4:1};m=8;W=30
    cert=checked(a,b,m,W)
    need(cert['order']!=0,'the predecessor unsurcharged tie is broken by the actual fee')
    cases.append({'name':'old unsurcharged tie breaks under surcharge','a':a,'b':b,'m':m,'W':W,'certificate':cert})
    # Full-rank calls still have positive derivative through the actual surcharge.
    a={64:1};b={64:1,1:0};cert=checked(a,b,64,2)
    need(cert['order']==0 and len(primary.polynomial(a,64,2))==7,'zero terms and full-rank degree')
    cases.append({'name':'full-rank profile and dropped zero terms','a':a,'b':b,'m':64,'W':2,'certificate':cert})
    for name,a,m,W in [
        ('non-dyadic rank',{3:1},64,2),('boolean count',{1:True},64,2),
        ('negative count',{1:-1},64,2),('zero count',{1:0},64,2),
        ('non-dyadic dimension',{1:1},73,2),('zero stock',{1:1},64,0),
        ('nonpositive root domain',{64:64},64,1)]:
        reject(name,lambda a=a,m=m,W=W:primary.polynomial(a,m,W))
    reject('negative refinement budget',lambda:primary.compare({1:1},{1:2},64,2,max_steps=-1))
    a,b,m,W,s=fixtures.tie(True);cert=checked(a,b,m,W)
    bad=copy.deepcopy(cert);bad['quotients'][0][0]=str(Q(bad['quotients'][0][0])+1)
    reject('changed factor quotient',lambda:independent.check(a,b,m,W,bad))
    bad=copy.deepcopy(cert);bad['gcd']=[str(-Q(x)) for x in bad['gcd']]
    reject('changed factor normalization',lambda:independent.check(a,b,m,W,bad))
    for name,fee in [('omitted surcharge',lambda p:Q(0)),
                     ('rank mass instead of call count',lambda p:Q(32*m*m,10**16)*sum(r*n for r,n in p.items())),
                     ('dimension instead of dimension squared',lambda p:Q(32*m,10**16)*sum(p.values()))]:
        altered=[]
        for p in (a,b):
            poly=primary.polynomial(p,m,W)
            poly[-1]+=fee(p)-Q(32*m*m,10**16)*sum(p.values());altered.append(poly)
        need(primary.value(primary.gcd(*altered),1)>=0,'fault must destroy the exact tie: '+name)
        def fault(altered=altered):
            for p,poly in zip((a,b),altered):
                for t in range(1,m.bit_length()+1):
                    need(primary.value(poly,Q(t))==independent.residual(p,m,W,Q(t)),'direct source equation rejects altered fee')
        reject(name,fault)
    digest=hashlib.sha256();pairs=equal=max_steps=0;profile_counts=[]
    for W in range(1,6):
        profiles=[]
        for counts in itertools.product(range(3),repeat=4):
            p=dict(zip((1,2,4,8),counts))
            try: primary.polynomial(p,8,W)
            except ValueError: continue
            profiles.append(p)
        profile_counts.append(len(profiles))
        for a,b in itertools.combinations_with_replacement(profiles,2):
            cert=checked(a,b,8,W);reverse=checked(b,a,8,W)
            need(reverse['order']==-cert['order'],'antisymmetry')
            digest.update(encode([W,a,b,cert]).encode());pairs+=1
            equal+=cert['order']==0;max_steps=max(max_steps,cert['steps'])
    environment=os.environ.copy();environment.pop('PYTHONOPTIMIZE',None)
    child=subprocess.run([sys.executable,'-I','-B',str(HERE/'source_probe.py')],
                         text=True,capture_output=True,env=environment,timeout=120)
    need(child.returncode==0,'assertion-enabled source probe: '+child.stderr)
    source_probe=json.loads(child.stdout)
    need(source_probe['status']=='PASS_PINNED_SURCHARGE_PROBE','source probe marker')
    return {'status':'PASS_SURCHARGED_DYADIC_COMPARATOR','sources':source_pins,'cases':cases,
            'small_census':{'m':8,'W':list(range(1,6)),'counts':list(range(3)),
                            'valid_profiles':profile_counts,'pairs':pairs,'equal':equal,
                            'max_steps':max_steps,'sha256':digest.hexdigest()},
            'controls':controls,'source_probe':source_probe}


def main():
    need(sys.argv[1:] in ([],['--write']),'usage: verify.py [--write]')
    receipt=HERE/'RESULT.json';writing=sys.argv[1:]==['--write']
    if writing: need(not receipt.exists(),'refuse to overwrite committed receipt')
    else: need(receipt.is_file(),'missing committed receipt')
    result=run()
    if writing:
        with receipt.open('x',encoding='utf-8') as out: json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
    else: need(encode(result)==encode(json.loads(receipt.read_text(encoding='utf-8'))),'typed receipt mismatch')
    print(result['status'],'pairs',result['small_census']['pairs'],'controls',len(result['controls']))


if __name__=='__main__':main()
