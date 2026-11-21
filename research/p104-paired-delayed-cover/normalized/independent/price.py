"""One exact normalized paid-leaf bound on the frozen #8027 uniform job and R347 stock."""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import tarfile

PINS = {
    'peer_application':'587ece477179606eed6fd9a334ac6d6e27f0067f82c3d6281993736e0570a76f',
    'peer_archive':'d85d011ca74e8592c21c1e4db91a1a9021af26dcebc4dfdc2af7251f9c1bf968',
    'binary':'f4aad2d07449c864479f26cc3b3ed4bbd8321f0ca14e1efc8676b28b54c27ed4',
    'signed':'419d4bdfb95c4484d0ddc81f34c89ee45bdefc0955a85dd496c1043396260e37',
    'accepted':'babc9a23a60da353403b4d6f0a3a346c0523a42645618890a592929747fb019a',
    'ambient_proof':'95cc9e31bc030ec94b04decddcca2d28ee98cfec0ca7803b54666b2b76a5c9ab',
    'shift_proof':'04eba2e0a2a6cdd4ee512254142cbe45e647a73b66ad67b2c1c0a62e0883238a',
}
NAMES = {'peer_application':'APPLICATION.json','peer_archive':'APPLICATION-SOURCES.tar.gz','binary':'BINARY.json','signed':'REPLAY.json','accepted':'accept.json','ambient_proof':'AMBIENT.md','shift_proof':'SHIFTED-LOG.md'}

def check(ok, message):
    if not ok:
        raise ValueError(message)

def stage_grid(covered, rational_left):
    rho=F(1,250); old=F('0.00385248');rows=[]
    for _ in range(4):
        envelope=(1-rho)*covered+rho*old
        cap=F(int(10**15*envelope)-1,10**15)
        slack=min(rho-cap,1-rho-cap,envelope-cap)
        check(cap>old and slack>0,'strict complete stage')
        rows.append(dict(previous=str(old),cap=str(cap),bound=str(envelope),slack=str(slack)))
        old=cap
    grid=10**14
    claim=F(min(int(cap*grid),int(rational_left*grid))-8,grid)
    return cap,claim,claim+F(7,grid),rows

def decimal_text(q, digits):
    n=q*(10**digits)
    check(n.denominator==1,'finite decimal')
    return f'0.{int(n):0{digits}d}'

def main():
    parser=argparse.ArgumentParser()
    for k in PINS:
        parser.add_argument('--'+k.replace('_','-'),dest=k,type=Path,required=True)
    parser.add_argument('--out',required=True,type=Path)
    a=parser.parse_args()
    for k,expected in PINS.items():
        check(hashlib.sha256(getattr(a,k).read_bytes()).hexdigest()==expected,'source '+k)
    load=lambda k:json.loads(getattr(a,k).read_bytes())
    base=load('peer_application');prior_binary=load('binary');prior_signed=load('signed');prior_accept=load('accepted')
    old=prior_binary['peer_finite'];uni=old['uniform'];comp=old['independent_directed_compiler']
    with tarfile.open(a.peer_archive) as tar:
        member='source/research/paired-query-only-bit/retained/inputs/credited_trim.py'
        check(hashlib.sha256(tar.extractfile(member).read()).hexdigest()=='fcff17fdd3108be68761fbde0fcbfe218be166cf518c99f7163e60d53ab785d9','uniform compiler source')
    C=F(old['tested_saving']);t=1-C
    v,ambient,cut,floor=(comp[k] for k in ('product_exponent','ambient_base','cutoff','productive_floor'))
    H,p,h=uni['H'],uni['logarithm_power'],1024
    check((v,ambient,cut,floor,H,p)==(768,134,15,16,299610000000000,623),'one frozen profile')
    check(uni['N']==f'2^{H}' and F(uni['theta'])==F(42,43) and C==F('0.003890115276594'),'trial and fixed carrier')
    check(old['finite_separation']['targets']==base['binary_native']['productive_all'] and
          old['finite_separation']['paid']==base['binary_native']['paid_all'] and
          F(old['finite_separation']['strict_normalized_gap']['lower'])>0,'real complete t-moment')
    targets=old['finite_separation']['targets']
    check(min(targets['8'],targets['64'])>0 and 256+512==v and 64**256*8**512==floor**v,'attained minimum')
    check(cut**43<floor**42 and 2**h*cut**(43*v)<=ambient**(42*v),'exit scale and shift')
    # Independent directed reproduction: exp and ln round correctly to nearest. Only a
    # lower bound is required; use the upper logarithm when multiplied by the negative -v*C.
    with localcontext() as ctx:
        ctx.prec=70
        cc=Decimal('0.003890115276594')
        log_hi=Decimal(ambient).ln().next_plus()
        exp_lo=(-v*cc*log_hi).next_minus().exp().next_minus()
        eta_lo=((Decimal(1)-cc)*exp_lo).next_minus()
    ratio=F(42,43)**p
    check(ratio<F(eta_lo) and ratio<F(uni['eta']['lower']) and F(eta_lo)<F(uni['eta']['upper']),'complement and paid exits')
    check(2**7<ambient<2**8 and 7*v>h and (8*v)*C<p,'normalized base for all 0..A')
    numerator=(h+H)**p;denominator=h**p
    J=(numerator//denominator).bit_length()
    check(denominator<<(J-1)<=numerator<denominator<<J,'least strict numerator')
    check(J*(H+h)>2*H*p,'positive log tail derivative for all x >= H')
    d=F(1,H*(2**38))
    check(F(prior_binary['delayed_cover_debit'])==d and H*d/2==F(64,2**45) and
          old['cover_prime_condition']=='odd q > 2^45*N^5 avoiding the frozen finite catalogue witnesses','same positive charged cover')
    loss=F(J,H);old_loss=F(uni['gap']);left=F(base['rational_raw'][0])
    oc,ok,ot,ost=stage_grid(C-old_loss-d,left)
    check(oc==F(prior_signed['cap'])==F(prior_binary['admitted']) and ok==F(prior_accept['claim'])
          and ot==F(prior_signed['tested']) and prior_accept['outcome']=='PASS_COMPLETE_INDEPENDENT_SIGNED_ACCEPTANCE','complete predecessor control')
    cap,k,tested,rows=stage_grid(C-loss-d,left)
    ceiling=F(base['binary_raw'][1])-old_loss
    threshold=ceiling+F(1,10**11)
    check(ok<ceiling<threshold<k<tested<cap,'strong old ceiling and reserved headroom')
    check(floor**(4*v)==2**(16*v) and p>0,'positive parameters')
    check(F(p*39,H)>C-threshold and H>2**48,'smaller dyadic scale optimistic ceiling')
    out={'pins':{NAMES[k]:v for k,v in PINS.items()},'case':{'v':v,'h':h,'p':p,'H':H,'theta':'42/43','C':str(C),'J':J},
         'eta_lower':str(eta_lo),'lower_shift_ratio':str(ratio),'small_ranks':'0..134^768','uniform_loss':str(loss),'cover_loss':str(d),
         'terminal_lower_fails':True,'tail_derivative_positive':True,'old_stages':ost,'new_stages':rows,'old_cap':decimal_text(oc,15),
         'old_claim':decimal_text(ok,14),'covered':str(C-loss-d),'cap':decimal_text(cap,15),'claim':decimal_text(k,14),
         'tested':decimal_text(tested,14),'gap_vs_old':str(k-ok),'percent_vs_old':str(100*(k-ok)/ok),'old_relaxed_ceiling':str(ceiling),
         'separation':str(k-ceiling),'beyond_preregistered_guard':str(k-threshold),'status':'PASS uniform proof and complete price; fresh signed application required'}
    with a.out.open('x') as f:
        json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    print('PASS normalized price',J,out['cap'],out['claim'],out['tested'],out['gap_vs_old'])
if __name__=='__main__':
    main()
