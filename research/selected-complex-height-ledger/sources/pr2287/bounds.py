"""Exact row, height and coarse-layer inequalities; no new root search."""
from fractions import Fraction as F
from importlib.util import spec_from_file_location,module_from_spec
from math import prod

from streams import need
from caller import depth


def scalar_charge(events):
    result=0;largest=0
    for event in events:
        if event[0]!="scalar":continue
        operation=event[1]
        if operation[0] not in ("add","scale"):continue
        c=F(operation[-2],operation[-1]);den=c.denominator
        need(den&(den-1)==0,"selected scalars are dyadic")
        cost=2*abs(c.numerator).bit_length()+den.bit_length()+3
        result+=cost;largest=max(largest,cost)
    return result,largest


def precision(data,profile):
    gamma=(1<<1296)*prod((1<<(2*i))-1 for i in range(1,37))
    need(1<<2627<gamma<1<<2628,"orthogonal cover cardinality")
    mass=sum(r*n for r,n in profile.items());need(mass==1041408,"selected unnormalized rank mass")
    s=gamma*mass;E=1<<100000;B=s+E;C0=1<<210000
    stock=14826*gamma
    literal=2*(1<<30000)*stock**2+8*s+4*stock+4+32*73
    need(literal<E and 32*73*B*B<C0 and 2*B+18<C0,"retained selected precision guard")
    need(2*B*(73-48)>=s+E,"completed-child height induction")
    charges={name:scalar_charge(events) for name,events in data["programs"].items()}
    local=sum(charges[c["orientation"]][0] for c in data["template"]["calls"])
    # Each bridge has one X and one Y ADD for each of 112 ports.
    actual=gamma*(local+144*224*8)+32*73
    need(actual<E,"new Horner implementation fits the node height allowance")
    # The explicit gather/work implementation uses extra copies, outside live rows.
    work_slots=14336+720;expanded=work_slots*gamma
    work_literal=2*(1<<30000)*expanded**2+8*s+4*expanded+4+32*73
    need(work_literal<E,"expanded fixed work inventory fits the same allowance")
    old=data["invoice"]["finite"]
    need((stock.bit_length(),literal.bit_length(),(32*73*B*B).bit_length())==
         (old["physical_stock_bits"],old["literal_bits"],old["required_C0_bits"]),
         "actual selected guard receipt binding")
    return {"cover_bits":gamma.bit_length(),"live_row_factor_bits":(14336*gamma).bit_length(),
            "paid_rank_mass":mass,"unnormalized_mass_bits":s.bit_length(),
            "E_exponent":100000,"C0_exponent":210000,"literal_bits":literal.bit_length(),
            "required_C0_bits":(32*73*B*B).bit_length(),
            "new_scalar_height_charge_bits":actual.bit_length(),
            "scalar_charges_per_call":charges,"caller_work_slots":work_slots,
            "expanded_literal_bits":work_literal.bit_length(),
            "height":"A(e)<=2*(Gamma*1041408+2^100000)*e; A_layer<C0*d",
            "grid":"2^-(p+ceil(C0*d)); no child-return rounding"}


def rows():
    tested=0
    for e in list(range(1000))+[10**i+j for i in range(3,61) for j in (0,1,72)]:
        d=depth(e)
        need(d<=2*(max(2,e)-1).bit_length(),"two-level halving depth")
        if e>=73:
            f=e//73
            for r in range(1,49):
                need(0<r*f<e and depth(r*f)<=d-1,"proper child and fresh-row divisor")
                tested+=1
    # A complete small row model, including arbitrary outer multiplicity.
    W,G,D,t=2,3,3,5;L=W*G;rows=t*L**D
    tuples=[(r//(G*(rows//L)),(r//(rows//L))%G,r%(rows//L)) for r in range(rows)]
    need(len(set(tuples))==rows and {x[2] for x in tuples}==set(range(rows//L)),"complete row decoding")
    for family in range(W):
        for cover in range(G):
            packet=[u for f,g,u in tuples if (f,g)==(family,cover)]
            need(packet==list(range(rows//L)) and len(packet)%(L**(D-1))==0,
                 "each owner packet retains complete unused stock")
    return {"proper_child_checks":tested,"halving_inequality":[73**2,2*48**2],
            "row_model_rows":rows,"row_model_owner_packet":rows//L,
            "live_factor":"14336*|O(73,2)|","stock":"live_factor^D(d)",
            "root_padding":"one padding to a multiple, factor below two",
            "packet_volume":"V/(14336*|O(73,2)|)"}


def parameters(root,profile):
    directory=root/"research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r740-replica32/code/engines"
    engines=[]
    for name in ("moment","base_two_moment"):
        spec=spec_from_file_location("retained_complex_"+name,directory/(name+".py"))
        engine=module_from_spec(spec);spec.loader.exec_module(engine);engines.append(engine)
    a=F(167,100000);sigma=1-a;tau=1-F(169711,10**8);beta=F(1,1000)
    spacing=F(1,500);lam=1-F(1668,10**6);lamp=F(599,600);epsilon=F(997,1000)
    first=engines[0].moment(profile,73,14336,a,False)
    second=engines[1].moment(73,14336,list(profile.items()),a)
    need(max(first[0],second[0])<=min(first[1],second[1]),"coarse interval intersection")
    gap=1-max(first[1],second[1]);need(gap>F(15999,10**9),"strict selected coarse moment")
    linear=F(sum(r*n for r,n in profile.items()),73*14336)
    need(linear==F(1017,1022),"linear moment")
    chi=tau+(1-beta)*max(sigma-tau,0);leaf=sigma+beta*(1-sigma)
    margins={"sigma-tau":sigma-tau,"lambda-tau":lam-tau,"lambda-sigma":lam-sigma,
             "lambda-chi":lam-chi,"lambda-leaf":lam-leaf,"lambdaPrime-lambda":lamp-lam,
             "lambdaPrime-leaf":lamp-leaf,"lambdaPrime-reservation":lamp-(1-spacing),
             "geometry":1-epsilon*(1+spacing),"precision":1-epsilon,"spacing_growth":epsilon*spacing}
    need(all(x>0 for x in margins.values()),"complete strict layer gaps")
    return {"tau":str(tau),"sigma":str(sigma),"beta":str(beta),"spacing":str(spacing),
            "lambda":str(lam),"lambdaPrime":str(lamp),"epsilon":str(epsilon),
            "internal_exponent":str(chi),"leaf_exponent":str(leaf),
            "linear_moment":str(linear),"coarse_moment_gap_lower":str(gap),
            "margins":{k:str(v) for k,v in margins.items()},"layer_saving":"1/600",
            "scope":"Fixed coarse point using retained interval engines; no new selected root or kappa."}


def run(root,data,profile):
    return {"precision":precision(data,profile),"rows":rows(),"parameters":parameters(root,profile)}
