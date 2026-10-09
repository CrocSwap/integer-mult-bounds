"""Generate Lean kernel checks from the selected whole-rank bit and complex profiles.

Only exact finite arithmetic is kernel checked. Analytic enclosure theorems,
source histograms, and all-size semantic transfers remain external.
"""
import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from math import factorial
from pathlib import Path

HERE=Path(__file__).resolve().parent
BIT_DEFAULT=HERE/'inputs/bit.json'
CX_DEFAULT=HERE/'inputs/complex.json'
RECEIPT_DEFAULT=HERE/'inputs/assembly.json'
SCALE=10**30

def pair(x): return [x.numerator,x.denominator]
def fmt(pairs): return '['+', '.join(f'({a}, {b})' for a,b in pairs)+']'
def atanh(z,n):
    assert 0<=z<=F(1,3)
    low=2*sum((z**(2*j+1)/F(2*j+1) for j in range(n)),F())
    return low,low+2*z**(2*n+1)/F(2*n+1)/(1-z*z)
def logb(x,n):
    assert x>=1
    k=0
    while x>2:x/=2;k+=1
    l2,u2=atanh(F(1,3),n)
    l,u=atanh((x-1)/(x+1),n)
    return k*l2+l,k*u2+u
def expb(x,n):
    assert 0<=x<n+1
    low=sum((x**j/F(factorial(j)) for j in range(n)),F())
    return low,low+x**n/F(factorial(n))/(1-x/F(n+1))
def ceilgrid(x):return -(-x.numerator*SCALE//x.denominator)
def grid(hist,m,w,a):
    logs=[];exps=[]
    for width,num in hist:
        lg=ceilgrid(logb(F(m,width),24)[1]);eg=ceilgrid(expb(a*F(lg,SCALE),8)[1])
        logs.append((width,lg));exps.append((width,eg))
    total=sum(width*num*e for (width,num),(_,e) in zip(hist,exps))
    cap=m*w*SCALE
    assert total<cap, (cap-total,m,w,a)
    return logs,exps,cap-total,cap

BASE = r'''

set_option maxRecDepth 100000
set_option maxHeartbeats 0

/-!
Exact rational arithmetic certificate for selected supplied histograms.
The analytic assertions that `lnUp` bounds real logarithm and `expUp`
bounds real exponential are assumptions when interpreting this arithmetic
certificate. The file checks their numerical instances and the final weighted
sum, but does not prove those assertions or the source schedule's correctness.
-/
abbrev Q := Nat × Nat
def norm (a : Q) : Q := let g := Nat.gcd a.1 a.2; if g = 0 then a else (a.1 / g, a.2 / g)
def qadd (a b : Q) : Q := norm (a.1 * b.2 + b.1 * a.2, a.2 * b.2)
def qmul (a b : Q) : Q := norm (a.1 * b.1, a.2 * b.2)
def qdiv (a b : Q) : Q := norm (a.1 * b.2, a.2 * b.1)
def qsub (a b : Q) : Q := norm (a.1 * b.2 - b.1 * a.2, a.2 * b.2)
def qlt (a b : Q) : Bool := a.1 * b.2 < b.1 * a.2
def qpow (a : Q) : Nat → Q
  | 0 => (1, 1)
  | k + 1 => qmul a (qpow a k)
def atanhSum (z : Q) : Nat → Q
  | 0 => (0, 1)
  | j + 1 => qadd (atanhSum z j) (qdiv (qpow z (2 * j + 1)) (2 * j + 1, 1))
def twoAtanhUp (z : Q) (n : Nat) : Q :=
  qmul (2, 1) (qadd (atanhSum z n)
    (qdiv (qpow z (2 * n + 1))
      (qmul (2 * n + 1, 1) (qsub (1, 1) (qmul z z)))))
def halve (x : Q) (k : Nat) : Nat → Q × Nat
  | 0 => (x, k)
  | f + 1 => if qlt (2, 1) x then halve (norm (x.1, 2 * x.2)) (k + 1) f else (x, k)
def lnUp (x : Q) : Q :=
  let p := halve x 0 64
  let y := p.1
  let base := qmul (p.2, 1) (twoAtanhUp (1, 3) 24)
  if qlt (1, 1) y then
    qadd base (twoAtanhUp (qdiv (qsub y (1, 1)) (qadd y (1, 1))) 24)
  else base
def fact : Nat → Nat
  | 0 => 1
  | j + 1 => (j + 1) * fact j
def expSum (x : Q) : Nat → Q
  | 0 => (0, 1)
  | j + 1 => qadd (expSum x j) (qdiv (qpow x j) (fact j, 1))
def expUp (x : Q) : Q :=
  qadd (expSum x 8)
    (qdiv (qdiv (qpow x 8) (40320, 1))
      (qsub (1, 1) (qdiv x (9, 1))))

def rankSum (h : List (Nat × Nat)) : Nat := h.foldl (fun s p => s + p.1 * p.2) 0

'''

def read_profile(path, key):
    d=json.loads(Path(path).read_text())
    hist=d[key]
    hist=sorted((int(k),int(v)) for k,v in (hist.items() if isinstance(hist,dict) else hist))
    h,m,W,N=(int(d[k]) for k in ('h','m','W','N'))
    assert h*h==m and len(hist)==len(set(k for k,v in hist))
    assert all(0<k<m and v>0 for k,v in hist)
    s=sum(k*v for k,v in hist)
    assert W*m-s==int(d['deficit']) and N>0 and W>0
    return d,h,m,W,N,s,hist

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--bit-profile',type=Path,default=BIT_DEFAULT)
    p.add_argument('--complex-profile',type=Path,default=CX_DEFAULT)
    p.add_argument('--assembly-receipt',type=Path,default=RECEIPT_DEFAULT)
    p.add_argument('--complex-saving',default=None)
    p.add_argument('--kappa',default=None)
    p.add_argument('--literal-gap',default=None)
    p.add_argument('--row-degree-gap',default=None)
    args=p.parse_args()
    bit,bh,bm,bw,bN,bs,bhist=read_profile(args.bit_profile,'histogram')
    cx,ch,cm,cw,cN,cs,chist=read_profile(args.complex_profile,'hist')
    assert bh==23 and len(bhist)==46 and bm==529 and bw==108516254
    assert bs==int(bit['rank_sum']) and F(*bit['atom_saving_certified'])==F(15513,125000000)
    assert cs==int(cx.get('rank_sum',cs)) and cm*cw-cs==int(cx['deficit'])
    # The assembly receipt supplies the bridge gaps associated with this
    # complex profile; overrides remain available for a later audited schedule.
    receipt=json.loads(args.assembly_receipt.read_text())
    for path in (args.bit_profile,args.complex_profile):
        pin=receipt.get('source_sha256',{}).get('inputs/'+path.name)
        if pin is not None:
            assert hashlib.sha256(path.read_bytes()).hexdigest()==pin, path
    ac=F(args.complex_saving) if args.complex_saving else F(*cx['saving'])
    kap=F(args.kappa) if args.kappa else F(receipt['kappa'])
    assert ac>0 and kap>0
    atom=F(1,1000); old=F(384599,10**10)
    bitord=(1-atom)*F(15513,125000000)+atom*old
    assert bitord==F(*bit['ordinary_saving'])
    beta=F(1,10**6); leafgap=F(1,10**10); eta=F(1,10**8)
    a=min(bitord,(1-beta)*ac-leafgap)
    assert a>0
    bl,be,bd,bc=grid(bhist,bm,bw,F(15513,125000000))
    cl,ce,cd,cc=grid(chist,cm,cw,ac)
    literal=F(args.literal_gap) if args.literal_gap else F(receipt['assembly']['strict_constraints']['literal_scalar_guard'])
    rowgap=F(args.row_degree_gap) if args.row_degree_gap else F(receipt['assembly']['strict_constraints']['row_product_gap'])
    assert literal>0 and rowgap>0
    assert F(receipt['complex']['saving'])==ac
    assert receipt['complex']['profile']['m']==cm and receipt['complex']['profile']['W']==cw
    assert receipt['complex']['profile']['total_rank']==cs
    assert len(receipt['assembly']['strict_constraints'])==47 and len(receipt['assembly']['margins'])==7
    tau,sigma=1-a,1-ac
    q=a*(1-2*eta); lp=1-q; lam=(tau+lp)/2
    c=q*(1+eta); eps=(1-eta)/(1+c+q)
    minimum=eps*q; r=(minimum+1-eps)/2; delta=eta/8
    internal=tau+(1-beta)*max(sigma-tau,F(0)); leaf=sigma+beta*(1-sigma)
    margins=dict(original_prefix=1-eps*(1+c),coordinate_movement=a,
        compact_phase_layer=minimum,bulk_exposure=a,
        Gaussian_arithmetic=min(1-eps-delta,r-delta),
        scalar_work=1-eps-delta,dimension=eps)
    slacks=dict(bit_positive=a,complex_above_bit=ac-a,
        complex_below_one_over32=F(1,32)-ac,beta_positive=beta,
        beta_below_one=1-beta,leaf_saving_above_bit=(1-beta)*ac-a,
        q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,
        c_positive=c,c_below_one=1-c,q_below_reservations=c-q,
        lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf,compact_reservations=lp-(1-c),
        lambda_prime_below_one=q,epsilon_positive=eps,epsilon_below_one=1-eps,
        guard_width=1-eps,K_geometry=1-eps*(1+c),K_dominates_log=eps*c,
        record_suffix=1-eps,phase_local=1-eps-delta,phase_boundary=r-delta,
        gamma_sublinear=1-eps-r,cell_above_band=eps-(1-r)/2,
        prime_interval_packing=1-eps,alpha_positive=r,alpha_below_one=1-r,
        alpha_below_one_fourth=F(1,4)-r,delta_positive=delta,
        delta_below_one_eighth=F(1,8)-delta,short_record_fallback=eps-a,
        small_field_exposure=1-eps-minimum,
        artificial_boundary=8-eps+r-delta-minimum,
        literal_scalar_guard=literal,row_product_gap=rowgap)
    slacks.update({name+'_above_kappa':val-kap for name,val in margins.items()})
    assert set(slacks)==set(receipt['assembly']['strict_constraints'])
    assert all(F(v)==slacks[k] for k,v in receipt['assembly']['strict_constraints'].items())
    assert all(F(v)==margins[k] for k,v in receipt['assembly']['margins'].items())
    assert all(v>0 for v in slacks.values()) and min(margins.values())>kap
    lean=BASE+f'''
-- Input histograms are selected by the generator's two profile paths.
def bitHist : List (Nat × Nat) := {fmt(bhist)}
def cxHist : List (Nat × Nat) := {fmt(chist)}
def bitLogGrid : List (Nat × Nat) := {fmt(bl)}
def bitExpGrid : List (Nat × Nat) := {fmt(be)}
def cxLogGrid : List (Nat × Nat) := {fmt(cl)}
def cxExpGrid : List (Nat × Nat) := {fmt(ce)}
def bitAtom : Q := (15513, 125000000)
def complexSaving : Q := ({ac.numerator}, {ac.denominator})
def scale : Nat := {SCALE}

-- The Nat-subtraction and series remainder guards are checked per bin.
def logDomain (x : Q) : Bool :=
  let y := (halve x 0 64).1
  !qlt y (1,1) && !qlt (2,1) y

def gridOK (hist logs exps : List (Nat × Nat)) (a : Q) (m W s : Nat) : Bool :=
  hist.length == logs.length && hist.length == exps.length &&
  rankSum hist == s && hist.all (fun p => 0 < p.1 && p.1 < m && 0 < p.2) &&
  logs.all (fun p => 0 < p.1 && p.1 < m && logDomain (m,p.1) &&
    qlt (lnUp (m,p.1)) (p.2,scale)) &&
  (logs.zip exps).all (fun p => p.1.1 == p.2.1 &&
    qlt (qmul a (p.1.2,scale)) (9,1) &&
    qlt (expUp (qmul a (p.1.2,scale))) (p.2.2,scale)) &&
  (hist.zip exps).all (fun p => p.1.1 == p.2.1) &&
  (hist.zip exps).foldl (fun acc p => acc + p.1.1 * p.1.2 * p.2.2) 0 < m * W * scale

theorem bit_grid : gridOK bitHist bitLogGrid bitExpGrid bitAtom {bm} {bw} {bs} = true := by decide +kernel
theorem cx_grid : gridOK cxHist cxLogGrid cxExpGrid complexSaving {cm} {cw} {cs} = true := by decide +kernel

-- Signed rational expressions prevent subtraction from saturating at zero.
abbrev SQ := Int × Nat
def snorm (a : SQ) : SQ :=
  let g := Nat.gcd a.1.natAbs a.2
  if g = 0 then a else (a.1 / (g : Int), a.2 / g)
def sf (n : Int) (d : Nat) : SQ := snorm (n,d)
def sadd (a b : SQ) : SQ := snorm (a.1 * (b.2 : Int) + b.1 * (a.2 : Int), a.2 * b.2)
def ssub (a b : SQ) : SQ := snorm (a.1 * (b.2 : Int) - b.1 * (a.2 : Int), a.2 * b.2)
def smul (a b : SQ) : SQ := snorm (a.1 * b.1, a.2 * b.2)
def sdiv (a b : SQ) : SQ := snorm (a.1 * (b.2 : Int), a.2 * b.1.natAbs)
def slt (a b : SQ) : Bool := a.1 * (b.2 : Int) < b.1 * (a.2 : Int)
def seq (a b : SQ) : Bool := a.1 * (b.2 : Int) == b.1 * (a.2 : Int)
def smin (a b : SQ) : SQ := if slt a b then a else b
def smax (a b : SQ) : SQ := if slt a b then b else a

def assemblyOK : Bool := Id.run do
  let z := sf 0 1
  let one := sf 1 1
  let two := sf 2 1
  let eight := sf 8 1
  let atom := sf 1 1000
  let old := sf 384599 10000000000
  let bAtom := sf 15513 125000000
  let bOrd := sadd (smul (ssub one atom) bAtom) (smul atom old)
  let b := sf {ac.numerator} {ac.denominator}
  let beta := sf 1 1000000
  let eta := sf 1 100000000
  let leafGap := sf 1 10000000000
  let a := smin bOrd (ssub (smul (ssub one beta) b) leafGap)
  let kap := sf {kap.numerator} {kap.denominator}
  let tau := ssub one a
  let sigma := ssub one b
  let q := smul a (ssub one (smul two eta))
  let c := smul q (sadd one eta)
  let denom := sadd (sadd one c) q
  let eps := sdiv (ssub one eta) denom
  let minimum := smul eps q
  let r := sdiv (sadd minimum (ssub one eps)) two
  let delta := sdiv eta eight
  let internal := sadd tau (smul (ssub one beta) (smax (ssub sigma tau) z))
  let leaf := sadd sigma (smul beta (ssub one sigma))
  let lp := ssub one q
  let lam := sdiv (sadd tau lp) two
  let margins : List SQ := [ssub one (smul eps (sadd one c)), a,
    minimum, a, smin (ssub (ssub one eps) delta) (ssub r delta),
    ssub (ssub one eps) delta, eps]
  let constraints : List SQ := [a, ssub b a, ssub (sf 1 32) b,
    beta, ssub one beta, ssub (smul (ssub one beta) b) a,
    q, ssub (ssub one internal) q, ssub (ssub one leaf) q,
    c, ssub one c, ssub c q,
    ssub lam tau, ssub lam sigma, ssub lam internal,
    ssub lp lam, ssub lp leaf, ssub lp (ssub one c),
    q, eps, ssub one eps, ssub one eps,
    ssub one (smul eps (sadd one c)), smul eps c,
    ssub one eps, ssub (ssub one eps) delta, ssub r delta,
    ssub (ssub one eps) r, ssub eps (sdiv (ssub one r) two),
    ssub one eps, r, ssub one r, ssub (sf 1 4) r,
    delta, ssub (sf 1 8) delta, ssub eps a,
    ssub (ssub one eps) minimum,
    ssub (sadd (ssub eight eps) (ssub r delta)) minimum,
    sf {literal.numerator} {literal.denominator},
    sf {rowgap.numerator} {rowgap.denominator}]
  return seq bOrd (sf {bitord.numerator} {bitord.denominator}) &&
    slt z denom && constraints.length == 40 &&
    constraints.all (fun t => slt z t) &&
    margins.length == 7 && margins.all (fun t => slt kap t) &&
    seq (smin (margins.foldl smin one) one) minimum &&
    slt kap minimum

theorem signed_assembly : assemblyOK = true := by decide +kernel
#print axioms bit_grid
#print axioms cx_grid
#print axioms signed_assembly
'''
    (HERE/'KernelNew.lean').write_text(lean)
    def shown(path):
        try: return str(path.resolve().relative_to(HERE))
        except ValueError: return str(path)
    result={'scope':'finite exact numeric inequalities only; analytic enclosure, profile semantics, all-size transfers external',
            'bit_source':shown(args.bit_profile),'complex_source':shown(args.complex_profile),
            'bit_sha256':hashlib.sha256(args.bit_profile.read_bytes()).hexdigest(),
            'complex_sha256':hashlib.sha256(args.complex_profile.read_bytes()).hexdigest(),
            'assembly_receipt_source':shown(args.assembly_receipt),
            'assembly_receipt_sha256':hashlib.sha256(args.assembly_receipt.read_bytes()).hexdigest(),
            'bit':{'m':bm,'W':bw,'s':bs,'bins':len(bhist),'saving':pair(F(15513,125000000)),'grid_deficit':bd},
            'complex':{'m':cm,'W':cw,'s':cs,'bins':len(chist),'saving':pair(ac),'grid_deficit':cd},
            'assembly':{'bit_ordinary':pair(bitord),'bit_weakened':pair(a),'kappa':pair(kap),
                        'literal_gap_input':pair(literal),'row_degree_gap_input':pair(rowgap)}}
    (HERE/'certificate.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('bit grid deficit',bd,'complex grid deficit',cd,'kappa',kap)

if __name__=='__main__':
    if sys.flags.optimize:
        raise RuntimeError('Run without -O: assertions must remain enabled')
    main()
