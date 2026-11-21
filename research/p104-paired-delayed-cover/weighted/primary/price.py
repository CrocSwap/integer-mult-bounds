"""Certify one fixed 768-factor high-tail / L128 triangle-inequality bound."""
from argparse import ArgumentParser
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import time

PINS = {
    'peer-application':'587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f',
    'peer-archive':'d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968',
    'R347-binary':'f4aad2d07449c864479f26cc3b3ed4bbd8321f0ca14e1efc8676b28b54c27ed4',
    'R348-price':'523d6dc93a7cd34bf6183a66d03b624ab2f0dfcf18b7e95032b7d0ab695fa24f',
    'R348-full':'9b00a17913efb76995b01c7b75f5b00aab394a0531e26490ab02a5940adcac3c',
    'R348-accept':'35481cf9a929a3dd137a9e63134b7e97ee7c5408d4e675a3e8ad67b16d9a7b71',
    'weighted-theorem':'28e0308f315a583282291fa01998d53a874b4b7e3073cacc3ddbb38c5a7f66c7',
    'R350-exclusion':'922f50e004b2844054c2be938df676412f7ce6c1963af96f9e231cc1fd016987'}
MEMBERS={'recipient/binary/finite.py':'c780cea060f4a9efef064b239636162a7e8e84e40369abc1a1c4679dfbeb3041',
         'source/research/paired-query-only-bit/retained/inputs/credited_trim.py':'fcff17fdd3108be68761fbde0fcbfe218be166cf518c99f7163e60d53ab785d9',
         'parent/binary/PROOF.md':'2bddffa4d670237ffc72514c3c5b4be4b9dabdd7696e0c4e0759f7fd7c10e575'}

def check(ok, why):
    if not ok:
        raise ValueError(why)

def save(path, result):
    with path.open('x') as f:
        json.dump(result,f,sort_keys=True,indent=2);f.write('\n')

def ceil_grid(x):
    scale=10**65
    return F(-(-scale*x//1),scale)

def positive_power(k,s):
    if k==1:
        return F(1),F(1)
    with localcontext() as c:
        c.prec=75
        log=Decimal(k).ln()
        return F((s*log.next_minus()).next_minus().exp().next_minus()),F((s*log.next_plus()).next_plus().exp().next_plus())

def four(covered, rational):
    previous=F('0.00385248');rho=F(1,250);rows=[]
    for _ in range(4):
        envelope=(1-rho)*covered+rho*previous
        admitted=F(int(envelope*10**15)-1,10**15)
        margin=min(rho-admitted,1-rho-admitted,envelope-admitted)
        check(admitted>previous and margin>0,'strict four-level service')
        rows.append({'previous':str(previous),'endpoint':str(envelope),'admitted':str(admitted),'charged_minimum_slack':str(margin)})
        previous=admitted
    claim=F(min(int(rational*10**14),int(previous*10**14))-8,10**14)
    return previous,claim,claim+F(7,10**14),rows

def dec(x,p):
    n=x*10**p;check(n.denominator==1,'exact decimal')
    return f'0.{int(n):0{p}d}'

def run(a):
    paths={k:getattr(a,k.lower().replace('-','_')) for k in PINS}
    for key,path in paths.items():
        check(sha256(path.read_bytes()).hexdigest()==PINS[key],key)
    load=lambda k:json.loads(paths[k].read_bytes())
    with tarfile.open(paths['peer-archive']) as tar:
        names=tar.getnames();check(len(names)==len(set(names)),'archive uniqueness')
        for key,expected in MEMBERS.items():
            check(sha256(tar.extractfile(key).read()).hexdigest()==expected,key)
    app=load('peer-application');old=load('R347-binary')['peer_finite'];prior=load('R348-price')
    signed=load('R348-full');accepted=load('R348-accept');negative=load('R350-exclusion')
    check(prior['claim']==signed['claim']==accepted['claim']=='0.00389011519729' and accepted['replay_sha256']==PINS['R348-full'],'signed comparable benchmark')
    check(negative['observed_direct_enclosure_failures']==list(range(11,18)) and negative['first_failed_j']==11,'old Bernoulli exclusion control')
    v,H,p,h=768,299610000000000,128,1024
    C=F('0.003890115276594');d=F(1,H*2**38)
    prev=F(signed['claim']);ceil_old=F(app['binary_raw'][1])-F(23731,H);guard=ceil_old+F(1,10**11)
    check(H+h<h*2**39 and C-F(4992,H)-F(2,10**13)>guard,'full optimistic price prior to source check')
    s=old['finite_separation'];native=app['binary_native'];comp=old['independent_directed_compiler']
    check((comp['product_exponent'],comp['cutoff'],comp['productive_floor'],comp['ambient_base'],comp['H'])==(v,15,16,134,H)
          and F(comp['trial'])==C and s['paid_tail_offset']=='1/5','native source')
    P={int(k):n for k,n in native['paid_all'].items()};T={int(k):n for k,n in native['productive_all'].items()}
    check(s['paid']==native['paid_all'] and s['targets']==native['productive_all'] and s['source_paid_calls']==sum(P.values()) and
          s['source_public_fields']==sum(T.values()) and s['source_paid_rank_mass']==sum(k*n for k,n in P.items()),'separate full paid and productive inventories')
    check(s['construction']=='chronological product; specialize low complete targets to owned zero; retain all original paid calls; split paid calls on disjoint axes'
          and s['owned_allocation_records_bound']==f'2*{sum(T.values())}^{v}' and s['specialized_initial_and_final']==0,'zero new recursive completion; paid backing retained')
    check(T[8]>0 and T[64]>0 and 8**512*64**256==16**v and 512+256==v,'attained productive floor')
    ratios=comp['ratio_intervals']
    alpha=F(ratios[0][0]);gamma=F(ratios[1][1]);base=gamma/alpha
    t=Decimal('0.996109884723406');u=Decimal('0.2')
    paid_lo=sum(n*positive_power(r,t)[0] for r,n in P.items())
    paid_high=sum(n*positive_power(r,t+u)[1] for r,n in P.items())
    direct_ratio=paid_high/(positive_power(15,u)[0]*paid_lo)
    check(0<direct_ratio<=base<1,'directly bound complete raw Chernoff slope')
    threshold=F(4,5);ell=F(9,10)
    # Frozen rational upper on 15^(1/25); exponent u(1-threshold)=1/25.
    root_upper=F(223,200)
    check(root_upper**25>15 and base*root_upper<1,'rational root and true decay')
    raw_tail=ceil_grid((base*root_upper)**v)
    extra=ceil_grid(2*base**v)
    prob=raw_tail+extra
    moment=threshold**p+prob
    check(0<prob<1 and moment<ell**p,'one completed label L128 gate')
    aa,bb,beta=F(7,20),F(21,10),F(51,50)
    check(2**(20*h)<=15**(7*v) and (2**h*134**v)**10>=15**(21*v) and 16**50>=15**51,'three logarithmic guards')
    check(2**7<134<2**8 and 7*v>h and 8*v*C<p,'all ranks in ordinary base')
    eta=F(old['uniform']['eta']['lower'])
    zero=((aa+ell)/bb)**p;infinity=(ell/beta)**p
    check(max(zero,infinity)<eta,'all heights via affine endpoint maximum')
    check((F(1)/beta)**p>=F(old['uniform']['eta']['upper']),'no distributional credit negative')
    check(F(old['finite_separation']['strict_normalized_gap']['lower'])>0 and old['cover_prime_condition']=='odd q > 2^45*N^5 avoiding the frozen finite catalogue witnesses'
          and F(prior['cover_loss'])==d and H*d/2==F(64,2**45),'whole-job budget and existing q-adic stock')
    den=h**p;num=(H+h)**p;J=(num//den).bit_length()
    check((den<<(J-1))<=num<(den<<J) and J*(H+h)>2*H*p,'adjacent minimal terminal and continuous tail')
    raw_left=F(app['rational_raw'][0]);covered=C-F(J,H)-d
    old_c,old_k,old_t,_=four(C-F(23731,H)-d,raw_left)
    check((old_c,old_k,old_t)==tuple(F(signed[k]) for k in ('cap','claim','tested')),'predecessor four stages and signed points')
    cap,claim,tested,rows=four(covered,raw_left)
    check(guard<claim<tested<cap and old_k==prev,'charged complete selection')
    rec={'result':'PASS_WHOLE_TUPLE_PRICE_SIGNED_REPLAY_REQUIRED','pins':PINS,'archive_member_pins':MEMBERS,
         'case':{'v':v,'p':p,'h':h,'H':H,'t':str(1-C),'top_cut':str(threshold),'Lp_bound':str(ell),'slab_base':15,'floor_base':16,'ambient_base':134},
         'alpha_lower':str(alpha),'gamma_upper':str(gamma),'direct_raw_ratio_upper':str(ceil_grid(direct_ratio)),
         'raw_tail_upper':str(raw_tail),'positive_split_uplift_upper':str(extra),'extra_recursive_completion_upper':'0','completed_tail_upper':str(prob),
         'one_label_moment_upper':str(moment),'one_label_moment_budget':str(ell**p),'endpoint_g0':str(zero),'endpoint_infinity':str(infinity),'eta_lower':str(eta),
         'L':J,'uniform_loss':str(F(J,H)),'cover_loss':str(d),'covered':str(covered),'stages':rows,
         'cap':dec(cap,15),'claim':dec(claim,14),'tested':dec(tested,14),'prior_claim':signed['claim'],'prior_cap':signed['cap'],
         'gain':str(claim-prev),'percent':str(100*(claim-prev)/prev),'peer_gain':str(claim-F(app['claim'])),'peer_percent':str(100*(claim-F(app['claim']))/F(app['claim'])),
         'relaxed_old_ceiling':str(ceil_old),'separation':str(claim-ceil_old),'headroom_above_extra_guard':str(claim-guard),
         'controls':['R348 complete good control','R350 finite Bernoulli bad control','no-tail-credit bad end','one lower terminal fails']}
    save(a.out,rec);print(rec['result'],J,rec['cap'],rec['claim'],rec['tested'],flush=True)
def main():
    cli=ArgumentParser()
    for k in PINS:cli.add_argument('--'+k.lower(),dest=k.lower().replace('-','_'),type=Path,required=True)
    cli.add_argument('--out',type=Path,required=True)
    cli.add_argument('--child',action='store_true',help='internal timed child')
    a=cli.parse_args();check(sys.version_info[:2]==(3,12) and __debug__,'CPython 3.12 with assertions')
    if a.child:
        run(a);return
    timing=a.out.with_suffix('.timing.json');check(not timing.exists() and not a.out.exists(),'fresh outputs')
    start=time.monotonic()
    try:code=subprocess.run([sys.executable,'-IB',__file__,*sys.argv[1:],'--child'],timeout=45).returncode
    except subprocess.TimeoutExpired:code=124
    save(timing,{'timeout_seconds':45,'returncode':code,'elapsed_seconds':round(time.monotonic()-start,6)})
    raise SystemExit(code)
if __name__=='__main__':
    main()
