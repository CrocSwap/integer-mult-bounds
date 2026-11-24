"""Check the actual ordinary floor and fully charged occupied-edge calendar."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

RUNTIME=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(RUNTIME))
from upstream import install

install()
LOWER=4474


def ceil(x):
    return -(-x.numerator//x.denominator)


def all_size_stock(word, c, intervals, unit):
    """Discharge the parameterized TRANSFER.md hypotheses at the new floor."""
    t = 1-c
    targets, paid = Counter(word.targets), Counter(word.paid)
    assert max(targets) <= 134 and min(paid) >= 1
    assert all(5*r <= 4*k for r,k in word.cells)
    assert all(sum(p for (u,k),p in word.cells.items() if u==r)==1 for r in paid)
    # Check actual directed per-receiving-label funding and the whole raw margin.
    t_lower = {k: intervals(k,t)[0] for k in targets}
    p_upper = {r: intervals(r,t)[1] for r in paid}
    t_hi = sum(n*intervals(k,t)[1] for k,n in targets.items())
    p_lo = sum(n*intervals(r,t)[0] for r,n in paid.items())
    assert sum(targets[k]*v for k,v in t_lower.items())>sum(paid[r]*v for r,v in p_upper.items())
    assert 100*p_lo>99*t_hi
    for k,n in targets.items():
        load=sum(paid[r]*p*p_upper[r] for (r,s),p in word.cells.items() if s==k)
        assert 0<load<=n*t_lower[k]
    psi=sum(paid[r]*p*r*(Q(intervals(k,c)[0],intervals(r,c)[1])-1)/c
            for (r,k),p in word.cells.items())
    target_axes=sum(k*n for k,n in targets.items())
    assert target_axes == 286098 and target_axes < 2**25
    fringe=10*target_axes/(t*psi)
    assert 0<fringe<Q(186,25) and psi>1

    # Check the smallest admitted numerical scale; every margin below grows
    # with N. Actual binary native stages start no earlier than H=3000.
    H=1024
    N=1<<H
    V=N**6
    ambient=134
    U=2*(N//(2048*ambient))
    delta=Q(1,2**128)
    assert LOWER%2==0 and 8<LOWER and 24*(LOWER+2)<25*LOWER
    assert (LOWER-8,LOWER-6)==(4466,4468)
    assert max(Q(k,r) for r,k in word.cells)*LOWER<U
    assert max(Q(k,r) for r,k in word.cells)*(U+2)<N
    assert 4*max(targets)*(U-8)<N and U*ambient<=Q(N,1024)
    assert U*1024*ambient>=(1-delta)*N
    assert Q(6,5)**4>2 and Q(6,5)**73>2**19
    assert len(word.paid)<2**19
    assert 2**19*Q(1,1024*ambient*LOWER)**77+Q(1,N**77)<1
    lower_power=Q(intervals(LOWER,t)[0],unit)
    assert lower_power>1024 and Q(1,t*lower_power)+Q(2,N**5)<2
    # Endpoint inverse bases are >1/(512N) through all roots. The
    # original 61-stage envelope costs 397+30.5H bits per endpoint.
    assert c.denominator.bit_length()-1<=60 and Q(1,N)-Q(1,2**(64*(H+1)))>Q(1,512*N)
    grid_error_bits=397+31*H+6*H+3-64*(H+1)
    assert grid_error_bits<-132
    # Time and integer errors are already normalized conservatively without
    # the L**c*psi denominator, which is strictly greater than one.
    assert c>0 and 1<LOWER and U<=N
    suffix_birth_error=Q(20*U*target_axes,V)/psi
    integer_mass_error=Q(2**46,N**4)
    delay_end_error=Q(2**20,N**4)
    # At H=1024 each error is below 2^-132. The inverse powers of N
    # and the negative slope of the grid error extend this to all H>=1024.
    assert suffix_birth_error<Q(2**30,N**5)<Q(1,2**132)
    assert integer_mass_error<Q(1,2**132) and delay_end_error<Q(1,2**132)
    assert 4*Q(1,2**132)<delta
    assert 4096*2*len(word.targets)<N**2
    assert (1-Q(10,LOWER))*psi-Q(1,2**130)>1
    assert (1-Q(1,N))/Q(257,256)>Q(1,2)
    return {"fringe_upper_1e9":ceil(fringe*10**9),"psi_lower_floor":int(psi),
            "grid_absolute_error_exponent_at_H1024":grid_error_bits,
            "suffix_target_axes":target_axes,
            "suffix_birth_error_upper_at_H1024":"2^30/N^5",
            "normalized_error_allowance":"2^-128",
            "birth_bound":"2V","copy_group_bound":"3N^3","whole_field_width":"N^92",
            "first_two_columns":[LOWER-8,LOWER-6],"minimum_positive_scale_h_guard":1024}


def bound_recipe(old, lower):
    """Pass the proposed literal cutoff through the installed Recipe.open seam."""
    import transport

    assert old.level_floor==lower
    N=1<<old.rank_log
    expected=2*(N//(2048*old.ambient))

    def capture(n,targets,paid,cells,t,l,u,volume,ticks,rounds,**flags):
        assert n==N and (l,u)==(lower,expected) and t==1-old.trial
        assert targets is old.targets and paid is old.paid and cells is old.cells
        # Compare the dyadic arguments by exponent: at large heights a second
        # copy of N**82 or 2**(92H) would not fit in memory.
        def dyadic(x,e):
            return x.bit_count()==1 and x.bit_length()-1==e
        H=old.rank_log
        assert dyadic(volume,6*H) and dyadic(ticks,82*H) and dyadic(rounds,2*H)
        assert set(flags)=={"width","delay_base"} and dyadic(flags["width"],92*H) and flags["delay_base"]==1<<19
        return True

    real_plan=transport.Plan
    try:
        transport.Plan=capture
        assert old.open()
    finally:
        transport.Plan=real_plan
    return {"height":old.rank_log,"lower":lower,"ambient":old.ambient,
            "first_columns":lower-8,"plan_arguments_checked":True}


def finite_plan(word, c):
    """Replay all records of a two-port cut fixture on one occupied K7 edge."""
    from transport import Measure, Plan

    r,k=max(word.cells,key=lambda edge: Q(edge[0],edge[1]))
    hi=2*ceil(Q((LOWER+4)*k,2*r))+4
    n=1<<(4*k*hi-1).bit_length()
    volume=8*hi**2
    ticks,radix=5,4
    t=1-c
    plan=Plan(n,(k,k),(r,r),{(r,k):Q(1)},t,LOWER,hi,volume,ticks,n,delay_base=radix)
    assert plan.bands.start==LOWER and LOWER-2 not in plan.count
    mass=Measure(t,volume,64*n.bit_length())
    contacts=[]
    for d in (LOWER,LOWER+2):
        assert plan.count[d]==ceil(mass.mass(d,d+2)[1])
        grants=[]
        for i in range(2):
            assert plan.receive[d,i]
            for link in plan.receive[d,i]:
                e=link.band
                a,b=max(e,Q(d*k,r)),min(e+2,Q((d+2)*k,r))
                grant=mass.mass(a,b)[0]/2
                assert link.count==grant.numerator//grant.denominator
                assert 0<grant and 2*plan.delay[d]<plan.delay[e]
                assert 0<=r*(e-8)-k*(d-8)<10*k
                grants.append((i,link.port,e,link.count))
        contacts.append((d,plan.count[d],grants))

    live,pending,held={},{},Counter()
    axes=opens=closes=loans=0
    first_counts=Counter()
    for op,frame,*args in plan.events():
        if op==0:
            assert frame not in live
            columns,*bindings=args
            size=k*columns
            parents=[]
            cursor=iter(bindings)
            for kind in cursor:
                if kind==1:
                    sender,prefix=pending.pop(next(cursor))
                    assert sender in live and prefix==size
                    held[sender]+=1
                    parents.append(sender)
                    loans+=1
                    if columns in (LOWER-8,LOWER-6):
                        first_counts[columns]+=1
                elif kind==2:
                    _,width,period=next(cursor),next(cursor),next(cursor)
                    assert width==size and period%4==0
                else:
                    assert kind==0 and next(cursor)==size
            live[frame]=parents
            opens+=1
        elif op==1:
            serial,size,selected=args
            assert frame in live and held[frame]==0
            axes+=size-selected
            if selected:
                assert serial not in pending
                pending[serial]=(frame,selected)
        else:
            assert op==2 and held[frame]==0
            for sender in live.pop(frame):
                held[sender]-=1
                assert held[sender]>=0 and sender in live
            closes+=1
    assert not live and not pending and not any(held.values()) and opens==closes
    assert axes==plan.leaves_per_epoch and len(first_counts)==2
    return {"tested_occupied_K7_grade":[r,k],"lower":LOWER,"upper":hi,"carrier":n,
            "first_band_contacts":contacts,"native_opens":opens,"native_closes":closes,
            "returned_paid_prefixes":loans,"paid_singletons":axes,
            "lower_return_counts":dict(first_counts),"extent":"complete fixture event stream"}


def check():
    from band_product import prepare_native
    from installations import BINARY_C, ENTRY, TERMINAL
    from raw_binary_stage import binary_word
    from strict_moment import UNIT
    from unpowered_price import intervals

    stage=(RUNTIME/"raw_binary_stage.py").read_bytes()
    assert sha256(stage).hexdigest()=="8020d33828233e7016700849a507a8cee78db8a17a33b6063b737313ea05b07f"
    assert TERMINAL.rank_logs==(31808,502922,7951907,125730703,134217727) and TERMINAL.complex_log==208653
    word=binary_word()
    assert (len(word.targets),len(word.paid),len(word.cells))==(18906,104652,24)
    a,b=prepare_native()
    ordinary=(*a[:-1],*b[:-1])
    assert tuple(recipe.rank_log for recipe in ordinary)==(*ENTRY.rank_logs,*TERMINAL.rank_logs)
    assert (a[-1].rank_log,b[-1].rank_log)==(1024,208653)
    openings=[bound_recipe(recipe,LOWER) for recipe in ordinary]
    stock=all_size_stock(word,BINARY_C,intervals,UNIT)
    finite=finite_plan(word,BINARY_C)
    assert finite["tested_occupied_K7_grade"]==[49,64]
    assert finite["native_opens"]==76380 and finite["returned_paid_prefixes"]==456
    assert finite["paid_singletons"]==38003660528
    print("PASS_LITERAL_ORDINARY_FLOOR",json.dumps(
        {"new_binary_openings":openings,"binary_all_size":stock,"binary_integer_fixture":finite},
        sort_keys=True),flush=True)


if __name__=="__main__":
    check()
