"""One fixed degree-40 raw coordinate moment with complete paid splitting on #8027."""
from argparse import ArgumentParser
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tarfile
import time

PINS={'peer-application':'587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f',
      'peer-archive':'d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968',
      'r347-binary':'f4aad2d07449c864479f26cc3b3ed4bbd8321f0ca14e1efc8676b28b54c27ed4',
      'r350-mean':'922f50e004b2844054c2be938df676412f7ce6c1963af96f9e231cc1fd016987',
      'r351-helper':'dd1790feeed03c6dd6b3df5c32f60416f814fe67cc2b6cac75d301c2c3702a5a',
      'r351-price':'4acbb38393550df5b046f125328a67bc344fe592a107556145ac315acf083a34',
      'r351-audit':'0f43bebea0a8a4a258e14ea7495ed9d2bdbfe8f952dafd423d7e1651b4807332',
      'r351-full':'65473eba091d40551586a3e078bb6c4155813ba64e7207e0698765a2e738da0d',
      'r351-accept':'32d40619c37fdcf91f63930e3ebdf1ec0e19210f91e4f1a74617fcc1b3ada10c',
      'weighted-theorem':'28e0308f315a583282291fa01998d53a874b4b7e3073cacc3ddbb38c5a7f66c7'}

def check(condition,label):
    if not condition:
        raise ValueError(label)

def save(path,obj):
    with path.open('x') as f:
        json.dump(obj,f,sort_keys=True,indent=2);f.write('\n')

def log_bounds(k):
    if k==1:return F(0),F(0)
    with localcontext() as ctx:
        ctx.prec=75
        x=Decimal(k).ln()
        return F(x.next_minus()),F(x.next_plus())

def run(a):
    paths={k:getattr(a,k.replace('-','_')) for k in PINS}
    for k,path in paths.items():
        check(sha256(path.read_bytes()).hexdigest()==PINS[k],k)
    load=lambda k:json.loads(paths[k].read_bytes())
    prev=load('r351-price');peer=load('peer-application');old=load('r347-binary')['peer_finite'];actual=load('r351-full')
    accepted=load('r351-accept');mean_control=load('r350-mean');other=load('r351-audit')
    helper=runpy.run_path(str(paths['r351-helper']))
    with tarfile.open(paths['peer-archive']) as tar:
        for n,hsh in helper['MEMBERS'].items():
            check(sha256(tar.extractfile(n).read()).hexdigest()==hsh,n)
    check(actual['claim']==accepted['claim']==prev['claim']=='0.00389011526022' and accepted['replay_sha256']==PINS['r351-full'],'complete signed control')
    check(F(other['cap'])==F(prev['cap'])==F(accepted['cap']),'independent precursor cap')
    v,p,h,H=768,40,1024,299610000000000
    C=F('0.003890115276594');t=Decimal('0.996109884723406');u=Decimal('0.2');d=F(1,H*2**38);lam=F(7,10)
    ceiling=F(peer['binary_raw'][1])-F(4876,H)
    check(H+h<h*2**39 and C-F(1560,H)-F(2,10**13)>ceiling>=F(actual['claim']),'whole candidate paid ceiling')
    bi=old['independent_directed_compiler'];sep=old['finite_separation'];nat=peer['binary_native']
    check(bi['product_exponent']==v and bi['cutoff']==15 and bi['productive_floor']==16 and bi['ambient_base']==134 and bi['H']==H and F(bi['trial'])==C,'source')
    P={int(k):n for k,n in nat['paid_all'].items()};T={int(k):n for k,n in nat['productive_all'].items()}
    check(sep['paid']==nat['paid_all'] and sep['targets']==nat['productive_all'] and sep['source_paid_calls']==sum(P.values())
          and sep['source_paid_rank_mass']==sum(k*n for k,n in P.items()) and sep['source_public_fields']==sum(T.values()),'separate one-letter laws')
    check(max(P)==56 and 56**2<15**3 and T[8]>0 and T[64]>0 and 8**512*64**256==16**768,'support and actual attained floor')
    check(sep['construction']=='chronological product; specialize low complete targets to owned zero; retain all original paid calls; split paid calls on disjoint axes' and
          sep['owned_allocation_records_bound']==f'2*{sum(T.values())}^{v}' and sep['specialized_initial_and_final']==0,'zero recursive completion; all ordinary specialized work retained')
    check(2**(20*h)<=15**(7*v) and (2**h*134**v)**10>=15**(21*v) and 16**50>=15**51 and 7*v>h and 8*v*C<p,'shift, floor and all bases')
    a0,b0,beta=F(7,20),F(21,10),F(51,50)
    eta=F(old['uniform']['eta']['lower'])
    end0=((a0+lam)/b0)**p;endinf=(lam/beta)**p
    check(max(end0,endinf)<eta,'prospective all-height budget')
    pden=pnum=F(0)
    for r,n in P.items():
        lo,hi=helper['positive_power'](r,t)
        pnum+=n*hi*log_bounds(r)[1];pden+=n*lo
    mean=pnum/(pden*log_bounds(15)[0]);mean_bound=F(67,100);letter_max=F(3,2);q=mean_bound/letter_max
    check(mean<=mean_bound and F(mean_control['completed_mean_upper'])<mean_bound and q==F(67,150),'tilted native letter mean and chord')
    alpha,gamma,_=bi['ratio_intervals'];slope=F(gamma[1])/F(alpha[0])
    phigh=sum(n*helper['positive_power'](r,t+u)[1] for r,n in P.items());plow=helper['positive_power'](15,u)[0]*pden
    check(phigh/plow<=slope<1,'separate positive raw split surcharge')
    split=helper['ceil_grid'](2*slope**v)
    check(F(prev['positive_split_uplift_upper'])==split and F(prev['case']['t'])==1-C and F(prev['cover_loss'])==d,'R351 controls')
    progress=a.out.with_suffix('.progress.jsonl')
    with progress.open('x') as events:
        events.write('{"stage":"all-input-guards"}\n');events.flush()
        stirling=[1]+[0]*p
        for i in range(1,p+1):
            stirling=[0]+[j*stirling[j]+stirling[j-1] for j in range(1,p+1)]
        check(stirling[0]==0 and stirling[1]==stirling[p]==1 and stirling[p-1]==p*(p-1)//2,'moment normalization and upper orders')
        terms=[];fall=1
        for j in range(p+1):
            if j:fall*=v-j+1
            terms.append(stirling[j]*fall*q**j)
            events.write(json.dumps({'stage':'term','j':j})+'\n');events.flush()
    check(F(v)*q==F(8576,25) and sum(terms)>0,'binomial mean and positive moment')
    raw=(letter_max/v)**p*sum(terms);completed=raw+split
    rec={'case':{'p':p,'v':v,'H':H,'h':h,'q_letter':str(q),'raw_support':'3/2','norm_limit':str(lam)},'pins':PINS,
         'raw_mean_upper':str(helper['ceil_grid'](mean)),'stirling_terms_0_through_40':[str(x) for x in terms],
         'raw_moment_upper':str(raw),'positive_split_uplift_upper':str(split),'extra_recursive_completion':'0','complete_moment_upper':str(completed),
         'moment_budget':str(lam**p),'eta_lower':str(eta),'endpoint_zero':str(end0),'endpoint_infinity':str(endinf)}
    if completed>=lam**p:
        rec['result']='EXCLUDED_FROZEN_NORM_CERTIFICATE';save(a.out,rec);print(rec['result'],flush=True);return
    inc=(H+h)**p;den=h**p;L=(inc//den).bit_length()
    check((den<<(L-1))<=inc<(den<<L) and L*(H+h)>2*H*p,'minimal terminal and increasing all-size tail')
    check(F(64,2**45)==H*d/2 and old['cover_prime_condition']=='odd q > 2^45*N^5 avoiding the frozen finite catalogue witnesses','full delayed cover')
    old_cap,old_claim,old_tested,_=helper['four'](C-F(4876,H)-d,F(peer['rational_raw'][0]))
    check((old_cap,old_claim,old_tested)==tuple(map(F,(actual['cap'],actual['claim'],actual['tested']))),'R351 four exact stages positive control')
    covered=C-F(L,H)-d
    cap,claim,tested,stages=helper['four'](covered,F(peer['rational_raw'][0]))
    check(claim>ceiling and claim>old_claim and claim<tested<cap,'directed complete separation')
    check((F(1)/beta)**p>=F(old['uniform']['eta']['upper']),'unpriced norm control')
    rec.update(result='PASS_FULL_PRICED_MOMENT_SIGNED_REQUIRED',L=L,uniform_loss=str(F(L,H)),cover_loss=str(d),covered=str(covered),stages=stages,
               cap=helper['dec'](cap,15),claim=helper['dec'](claim,14),tested=helper['dec'](tested,14),
               prior_cap=actual['cap'],prior_claim=actual['claim'],gain=str(claim-old_claim),percent=str(100*(claim-old_claim)/old_claim),
               peer_gain=str(claim-F(peer['claim'])),peer_percent=str(100*(claim-F(peer['claim']))/F(peer['claim'])),
               relaxed_old_ceiling=str(ceiling),separation=str(claim-ceiling),controls=['R351 positive signed control','lower terminal insufficient','uncertified unit norm fails'])
    save(a.out,rec);print(rec['result'],L,rec['cap'],rec['claim'],rec['tested'],flush=True)

def main():
    parser=ArgumentParser()
    for key in PINS:parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--child',action='store_true')
    a=parser.parse_args();check(sys.implementation.name=='cpython' and sys.version_info[:2]==(3,12) and __debug__,'CPython 3.12')
    if a.child:run(a);return
    clock=a.out.with_suffix('.timing.json')
    check(not any(f.exists() for f in (a.out,clock,a.out.with_suffix('.progress.jsonl'))),'fresh output paths')
    start=time.monotonic()
    try:code=subprocess.run([sys.executable,'-IB',__file__,*sys.argv[1:],'--child'],timeout=45).returncode
    except subprocess.TimeoutExpired:code=124
    save(clock,{'exit_code':code,'limit_seconds':45,'elapsed_seconds':round(time.monotonic()-start,6)});raise SystemExit(code)
if __name__=='__main__':
    main()
