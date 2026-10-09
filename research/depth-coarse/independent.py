"""Independent selected grammar-profile/root/47-margin audit; no package imports."""
import sys
if sys.flags.optimize:
    raise ValueError("Assertions must remain enabled")
sys.dont_write_bytecode = True
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from math import comb,factorial
from hashlib import sha256
import json,itertools,argparse

SCALE=10**50
def outward(q,up=False):
    q*=SCALE
    return F(-(-q.numerator//q.denominator) if up else q.numerator//q.denominator,SCALE)
def small_log(x):
    z=(x-1)/(x+1)
    low=2*sum((z**(2*k+1)/F(2*k+1) for k in range(64)),F())
    return low,low+2*z**129/(129*(1-z*z))
LN2=small_log(F(2))
def log_bounds(x):
    assert x>=1
    k=0
    while x>2:x/=2;k+=1
    lo,hi=small_log(x)
    return outward(lo+k*LN2[0]),outward(hi+k*LN2[1],True)
def exp_bounds(x):
    assert 0<=x<1
    low=sum((x**k/F(factorial(k)) for k in range(14)),F())
    return low,low+x**14/F(factorial(14))/(1-x/15)
def bracket(p):
    denominator=10**22;low,high=1,10**18
    assert p['moment'](F(low,denominator))[1]<1<p['moment'](F(high,denominator))[0]
    while high-low>1:
        mid=(high+low)//2;l,h=p['moment'](F(mid,denominator))
        if h<1:low=mid
        elif l>1:high=mid
        else:raise ArithmeticError('Enclosure inconclusive')
    return F(low,denominator),F(high,denominator)
def string_data(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):string_data(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [string_data(v) for v in x]
    return x

PACKAGE=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
PINNED={}

def read(path):
    raw=path.read_bytes();PINNED[path.relative_to(PACKAGE).as_posix()]=sha256(raw).hexdigest()
    return json.loads(raw)

def make_profile(axes):
    m,N=575,comb(23,3)*comb(25,3)
    rows=Counter({1:19*N,21:2*N,17:2*N,481:2*N})
    W=2*N
    for h,x in zip((23,25),axes):
        p=x['profile'];R=p['R'];v=comb(h,3)
        assert p['h']==h and p['v']==v and R==x['compiled']['roles']==x['replay']['roles']
        assert p['crt_disagreements']==0 and p['blocks'][0]==p['blocks'][h]==0
        assert len(p['blocks'])==h+1 and all(type(n)is int and n>=0 for n in p['blocks'])
        assert sum(t*n for t,n in enumerate(p['blocks']))==h*R+h*(h-1)
        rep=N//v;bank=rep*R;W+=bank
        rows.update({t:rep*n for t,n in enumerate(p['blocks']) if t and n})
        rows.update({h:bank,m-2*h:bank})
        rows.update({1:2*N,h-2:2*N})
    mass=sum(t*n for t,n in rows.items())
    L=sum((N//comb(h,3))*h*(h-1) for h in (23,25))
    assert mass==m*W-N+L==m*W-1846900 and max(rows)==529
    logs={t:log_bounds(F(m,t)) for t in rows}
    def moment(a):
        lo,hi=F(),F()
        for t,n in rows.items():
            l,h=logs[t];weight=F(t*n,m*W)
            lo+=weight*exp_bounds(a*l)[0];hi+=weight*exp_bounds(a*h)[1]
        return outward(lo),outward(hi,True)
    return dict(m=m,W=W,rows=rows,mass=mass,moment=moment)

def half(m,r):
    n=1
    while m**n<=2*r**n:n+=1
    return n

def independent_assembly(cert,bridge):
    recorded=cert['assembly']['assembly'];p=recorded['parameters']
    a,b,h,beta,kappa=map(F,(cert['bit_saving'],'717/10000000','1/1000000000000','1/20',cert['kappa']))
    tau,sigma=1-a,1-b;q=a*(1-2*h);lp=1-q;c=q+h/4;eps=(1-h)/(1+q)
    lam=(tau+lp)/2;G=eps*q;r=(G+1-eps)/2;delta=h/8
    phase=bridge['complex'];mc,Wc,s,scalar=(phase[k] for k in ('m','W','s','scalar_group_upper'))
    E=64*(Wc+mc+scalar+1)**3;B=s+E;C0=32*mc*B*B
    literal=2*scalar*Wc**2+8*s+4*Wc+4+32*mc
    semantic=dict(E=E,B=B,C0=C0,C1=1,literal_charge=literal,strict_literal_gap=E-literal,
                  induction_gap=2*B*(mc-phase['maxchild'])-(s+E))
    assert all(F(bridge['semantic'][k])==v for k,v in semantic.items())
    assert E>literal and semantic['induction_gap']>=0 and C0>2*B+18
    bit=bridge['bit'];bit=dict(bit,W=cert['W'])
    coeff=0
    for data in (bit,phase):
        degree=half(data['m'],data['maxchild']);bits=data['W'].bit_length()
        assert data['halving_degree']==degree and data['wire_bits']==bits
        coeff+=degree*bits
    stock=bridge['rows'];gap=stock['degree']-F(51,25)*coeff
    assert coeff==stock['coefficient'] and gap==F(stock['degree_gap']) and gap>0
    assert stock['suffix_slope']==4*stock['degree']
    internal=tau+(1-beta)*max(sigma-tau,F());leaf=sigma+beta*(1-sigma)
    margins=dict(g1=1-eps,g2=a,g3=G,g4=a,g5=min(1-eps-delta,r-delta),g6=1-eps-delta,g7=eps)
    slacks=dict(a_positive=a,a_below_b=b-a,b_below_one_over32=F(1,32)-b,
       beta_positive=beta,beta_below_one=1-beta,phase_leaf_above_bit=(1-beta)*b-a,
       q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,c_positive=c,
       c_below_one=1-c,q_below_reservations=c-q,lambda_above_tau=lam-tau,
       lambda_above_sigma=lam-sigma,lambda_above_internal=lam-internal,
       lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,
       compact_reservations=lp-(1-c),lambda_prime_below_one=q,
       epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps,
       K_geometry=1-eps*(1+c),K_dominates_log=eps*c,record_suffix=1-eps,
       phase_local=1-eps-delta,phase_boundary=r-delta,gamma_sublinear=1-eps-r,
       cell_above_band=eps-(1-r)/2,prime_interval_packing=1-eps,alpha_positive=r,
       alpha_below_one=1-r,alpha_below_one_fourth=F(1,4)-r,
       delta_positive=delta,delta_below_one_eighth=F(1,8)-delta,
       short_record_fallback=eps-a,small_field_exposure=1-eps-G,
       artificial_boundary=8-eps+r-delta-G,literal_scalar_guard=E-literal,row_product_gap=gap)
    slacks.update({name+'_above_kappa':value-kappa for name,value in margins.items()})
    params=dict(a_bit=a,a_complex=b,tau=tau,sigma=sigma,beta=beta,h=h,q=q,c=c,
       epsilon=eps,lambda_=lam,lambda_prime=lp,alpha_squared_power=r,delta=delta,
       C0=C0,C1=1,kappa=kappa)
    assert len(slacks)==47 and all(value>0 for value in slacks.values())
    assert {k:F(v) for k,v in recorded['constraints'].items()}==slacks
    assert {k:F(v) for k,v in recorded['parameters'].items()}==params
    assert {k:F(v) for k,v in recorded['margins'].items()}==margins
    assert min(margins.values())==G and G-kappa==F(recorded['absorption_gap'])
    assert 1-eps-G==h and 1-eps-r==h/2 and 1-eps*(1+c)==h-eps*h/4
    assert G<=kappa+F(1,10**18) # next kappa grid genuinely fails g3.
    return dict(parameters=params,constraints=slacks,margins=margins,absorption_gap=G-kappa,
                next_kappa_rejected_by_g3=True,semantic_and_product_stock_recomputed=True)

def main():
    global PACKAGE,BASE
    cli=argparse.ArgumentParser()
    cli.add_argument('--package-root',type=Path,default=PACKAGE)
    cli.add_argument('--output',type=Path,help='Intentionally write a new independent receipt; default checks retained receipt')
    args=cli.parse_args();PACKAGE=args.package_root.resolve();BASE=PACKAGE/'research/depth-coarse'
    selection=read(BASE/'selection.json');cert=read(BASE/'certificate.json')
    ledger=read(BASE/'menu-ledger.json')
    assert ledger['selected']==selection and len(ledger['results'])==64
    axes=[read(BASE/f'axis-{h}.json') for h in (23,25)]
    for h,x in zip((23,25),axes):assert x['source']['choices']==selection[str(h)]
    p=make_profile(axes)
    assert p['W']==cert['W'] and p['mass']==cert['total_rank']
    assert p['rows']=={int(t):n for t,n in cert['child_multiplicities'].items()}
    a=F(cert['bit_saving']);next_a=a+F(1,10**18)
    accepted=p['moment'](a);rejected=p['moment'](next_a)
    assert accepted[1]<1<rejected[0]
    root_interval=bracket(p)
    old=read(BASE/'comparisons/pr71.json');old75=read(BASE/'comparisons/pr75.json')
    assembly=independent_assembly(cert,old['finite_bridge'])
    exclusions={}
    for name,oldcert in (('pr71',old),('pr75',old75)):
        bit=oldcert['bit'];total=F()
        for t,n in bit['child_multiplicities'].items():
            t=int(t);l,_=log_bounds(F(bit['m'],t))
            total+=F(t*n,bit['m']*bit['W'])*exp_bounds(a*l)[0]
        assert total>1 and F(cert['kappa'])>F(oldcert['kappa'])
        exclusions[name]=outward(total)
    menu_result=[]
    choices=[''.join(x) for x in itertools.product('cr',repeat=3)]
    for c23,c25 in itertools.product(choices,repeat=2):
        menu_axes=[read(BASE/f'menu/{c}-{h}.json') for h,c in ((23,c23),(25,c25))]
        trial=make_profile(menu_axes)
        lo,hi=trial['moment'](a)
        if (c23,c25)==(selection['23'],selection['25']):
            assert trial['W']==p['W'] and trial['rows']==p['rows'] and hi<1
        else:assert lo>1
        menu_result.append(dict(h23=c23,h25=c25,W=trial['W'],lower=lo,upper=hi))
    # Reject changing input bytes while the audit was running.
    for rel,digest in PINNED.items():assert sha256((PACKAGE/rel).read_bytes()).hexdigest()==digest
    ceiling=root_interval[1]/(1+root_interval[1])
    assert 0<ceiling-F(cert['kappa'])<F(1565,10**19)
    result=dict(status='PASS independent exact selected-profile mathematical audit',
        scope='Finite grammar lemma reviewed, complete profile reconstructed, independent rational root and 47 margins; all-size transfer conditional; no physical replay in this checker',
        source_hashes=PINNED,selection=selection,W=p['W'],total_rank=p['mass'],bit_saving=a,
        root_interval=list(root_interval),accepted_interval=list(accepted),rejected_interval=list(rejected),kappa=F(cert['kappa']),
        balanced_family_ceiling_upper=ceiling,remaining_parameter_headroom_upper=ceiling-F(cert['kappa']),
        comparisons_lower_at_selected=exclusions,assembly=assembly,menu_64_at_selected=menu_result,
        residual_proof_obligations=['Source/word closure and physical replay verified in separate checker.',
            'Ambient framed lift, all-size residual/row/remainder compiler and fixed-tape simulation inherited.',
            'Analytic/routing/prime/setup/precision/recovery multiplication interfaces inherited.',
            'Not global optimality, unconditional multiplication theorem or measured runtime gain.'])
    result=string_data(result)
    if args.output is not None:
        args.output.write_text(json.dumps(result,indent=2)+'\n')
    else:
        assert result==json.loads((BASE/'independent-receipt.json').read_text()), 'Independent receipt changed'
    print('PASS complete rank/list, independent exact root, 47 constraints, seven margins, PR71/75 exclusions and 64-profile separation')
    print('Selection',selection,'W',p['W'],'kappa',cert['kappa'])

if __name__=='__main__':main()
