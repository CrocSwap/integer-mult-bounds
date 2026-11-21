"""Price one rational grid law on the frozen 451-factor word. Requires CPython 3.12."""
import argparse
from contextlib import contextmanager
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
import json
from math import comb, factorial
from pathlib import Path
import signal
import sys
import tarfile
from time import monotonic

PIN = "538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749"
A, B, SLOPE = F(7, 6), F(319, 100), F(23, 20)
H_SHIFT, FACTORS, GRID, MASS = 1804, 451, 16, 2**16
PREVIOUS_CLAIM = F("0.00387992804505")
PREVIOUS_LOSS = 1218
CASE_CAP, HEIGHT_CAP, SECONDS = 6, 1024, 60

def source(path):
    if path.suffix == ".json":
        data = path.read_bytes()
    else:
        with tarfile.open(path, "r:*") as archive:
            with archive.extractfile("package-sanitized/BIT-451.json") as stream:
                data = stream.read()
    if sha256(data).hexdigest() != PIN:
        raise ValueError("wrong BIT-451.json bytes")
    return json.loads(data)

def grid(data):
    paid = data["native"]["paid"]
    if len(paid) != 14 or sum(paid.values()) != 107460 or max(map(int, paid)) != 56:
        raise ValueError("unexpected paid profile")
    t = 1 - F(data["separation"]["trial"])
    if t != 1 - F("0.003879928046148"):
        raise ValueError("wrong paid tilt")
    mass_lo = mass_hi = first_lo = first_hi = second_hi = F(0)
    with localcontext() as ctx:
        ctx.prec = 80
        base = Decimal(11).ln()
        for label, count in paid.items():
            rank = int(label)
            if rank == 1:
                mass_lo += count
                mass_hi += count
                continue
            log_r = Decimal(rank).ln()
            low, high = log_r.next_minus(), log_r.next_plus()
            exp_lo = ((low * t.numerator).next_minus() / t.denominator).next_minus()
            exp_hi = ((high * t.numerator).next_plus() / t.denominator).next_plus()
            w_lo = count * F(exp_lo.exp().next_minus())
            w_hi = count * F(exp_hi.exp().next_plus())
            y_lo, y_hi = F(low)/F(base.next_plus()), F(high)/F(base.next_minus())
            mass_lo += w_lo
            mass_hi += w_hi
            first_lo += w_lo*y_lo
            first_hi += w_hi*y_hi
            second_hi += w_hi*y_hi**2
    low, high = first_lo/mass_hi, first_hi/mass_lo
    variance = (second_hi/mass_lo-low**2)/FACTORS
    sep = data["separation"]
    raw_lo = F(sep["three_engine_intervals"]["source_1"]["alpha"][0])**FACTORS
    exact_eps = F(sep["paid_uplift_upper"][1])/raw_lo
    epsilon = F(-(-exact_eps*2**48 // 1), 2**48)
    if not (0 <= low <= high < 1 and variance >= 0 and epsilon >= exact_eps >= 0):
        raise ValueError("invalid moment interval")
    cdf = [0]
    for cut in range(1, GRID):
        z = F(cut, GRID)
        raw_tail = F(1) if z <= high else variance/(variance+(z-high)**2)
        final_tail = (raw_tail+epsilon)/(1+epsilon)
        cdf.append(max(cdf[-1], (1-final_tail)*MASS//1))
    cdf.append(MASS)
    weights = [r-l for l, r in zip(cdf, cdf[1:])]
    if len(weights) != GRID or min(weights) < 0 or sum(weights) != MASS:
        raise ValueError("invalid rational grid law")
    return weights, {"cuts": list(range(1, GRID)), "cut_denominator": GRID,
                     "strict_tail": "Pr(X>z)", "mass_denominator": MASS, "weights": weights,
                     "cdf_floor_units": cdf, "full_excess_upper": str(epsilon),
                     "mean_lower": str(low), "mean_upper": str(high), "variance_upper": str(variance)}

def coefficients(p, weights):
    mu = [sum(n*i**k for i, n in enumerate(weights, 1))*F(1, MASS*GRID**k)
          for k in range(p+1)]
    shift = [sum(comb(i,k)*A**(i-k)*mu[k] for k in range(i+1)) for i in range(p+1)]
    bell = [[F(0)]*(p+1) for _ in range(p+1)]
    stir = [[0]*(p+1) for _ in range(p+1)]
    bell[0][0] = stir[0][0] = 1
    for n in range(1, p+1):
        for j in range(1, n+1):
            bell[n][j] = sum(comb(n-1,i-1)*mu[i]*bell[n-i][j-1] for i in range(1,n-j+2))
            stir[n][j] = j*stir[n-1][j]+stir[n-1][j-1]
    numer, denom = [], []
    for j in range(p+1):
        numer.append(factorial(j)*sum(comb(p,i)*shift[p-i]*bell[i][j] for i in range(j,p+1)))
        denom.append(factorial(j)*sum(comb(p,i)*B**(p-i)*SLOPE**i*stir[i][j] for i in range(j,p+1)))
    return numer, denom

def loss_at(p, horizon):
    return (((horizon+H_SHIFT)**p)//(H_SHIFT**p)).bit_length()

def price(data, p):
    horizon = data["uniform"]["H"]
    loss = loss_at(p, horizon)
    if F(loss,horizon)*(horizon+H_SHIFT) <= 2*p:
        return {"status":"terminal conversion unresolved", "loss":loss}
    cover = F(data["separation"]["trial"])-F(loss,horizon)-F(1,horizon*2**44)
    stock = data["cover_and_stock"]
    rate, rho = F(stock["seed"]), F(stock["rho"])
    for _ in range(7):
        bound = (1-rho)*cover+rho*rate
        step = F(int(bound*10**24)-1,10**24)
        if not (rate < step < bound < cover and step < min(rho,1-rho)):
            return {"status":"stage price unresolved", "loss":loss}
        rate = step
    tick = F(1,10**14)
    cap = F(int(rate*10**17),10**17)
    claim = (cap//tick-8)*tick
    old_ceiling = F(data["raw_crossing"][1])-F(PREVIOUS_LOSS,horizon)-7*tick
    return {"status":"priced comparison only", "loss":loss,"ordinary_cap":str(cap),
            "candidate_grid_claim":str(claim), "old_relaxed_ceiling":str(old_ceiling),
            "directed_separation":str(claim-old_ceiling), "claim_minus_predecessor":str(claim-PREVIOUS_CLAIM)}

@contextmanager
def checkpoint_update():
    mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, mask)

def record_decision(state, ok, reason, facts, visited_height=False):
    with checkpoint_update():
        state["pending_decision"] = [ok, reason, facts]
        if visited_height:
            state["heights_used"] += 1
    return state["pending_decision"]

def decide(data, p, weights, state):
    eta = F(data["uniform"]["eta"][0])
    mean = F(sum(i*n for i,n in enumerate(weights,1)),GRID*MASS)
    if F(H_SHIFT+(134**451).bit_length()-1,H_SHIFT)**p <= F(data["uniform"]["ambient_power"][1]):
        return record_decision(state,False,"fixed conservative base guard",{})
    limit = (mean/SLOPE)**p
    if limit >= eta:
        return record_decision(state,False,"fixed-law limit reaches directed eta lower threshold",{"limit":str(limit)})
    numer, denom = coefficients(p, weights)
    start = state["next_height"]
    for g in range(HEIGHT_CAP):
        if g >= start:
            if state["heights_used"] >= HEIGHT_CAP:
                raise TimeoutError("cumulative height limit")
            ratio = numer[0]/denom[0]
            if ratio >= eta:
                return record_decision(state,False,"fixed-law ratio reaches directed eta lower threshold",
                                       {"height":g,"ratio":str(ratio)},visited_height=True)
            if all(n <= eta*d for n,d in zip(numer,denom)):
                return record_decision(state,True,"shifted differences, strict value and strict limit",
                                       {"height":g,"ratio":str(ratio),"limit":str(limit)},visited_height=True)
            with checkpoint_update():
                state["heights_used"] += 1
                state["next_height"] = g+1
        numer = [x+y for x,y in zip(numer,numer[1:]+[0])]
        denom = [x+y for x,y in zip(denom,denom[1:]+[0])]
    raise TimeoutError("cumulative height limit")

def screening(data, state):
    horizon = data["uniform"]["H"]
    tick = F(1,10**14)
    # Necessary floor for this fixed conservative base guard. Directed logs avoid
    # spending any of the six candidate decisions on a separate guard-only search.
    base = F(H_SHIFT+(134**FACTORS).bit_length()-1,H_SHIFT)
    ambient = F(data["uniform"]["ambient_power"][1])
    with localcontext() as ctx:
        ctx.prec = 80
        ambient_down = (Decimal(ambient.numerator)/ambient.denominator).next_minus()
        base_up = (Decimal(base.numerator)/base.denominator).next_plus()
        lower_log_ratio = F(ambient_down.ln().next_minus())/F(base_up.ln().next_plus())
    min_power = max(1, lower_log_ratio//1+1)
    min_loss = loss_at(min_power,horizon)
    cover = F(data["separation"]["trial"])-F(min_loss,horizon)-F(1,horizon*2**44)
    stock = data["cover_and_stock"]
    rate, rho = F(stock["seed"]), F(stock["rho"])
    for _ in range(7):
        rate = (1-rho)*cover+rho*rate
    upper = rate-7*tick
    old_ceiling = F(data["raw_crossing"][1])-F(PREVIOUS_LOSS,horizon)-7*tick
    state["optimistic_preprice"] = {"necessary_power_floor":min_power,"minimum_loss_units":min_loss,
                                   "seven_unrounded_stages_less_consumer_reserve":str(upper),
                                   "old_claim":str(PREVIOUS_CLAIM),"old_relaxed_ceiling":str(old_ceiling),
                                   "headroom_over_old_ceiling":str(upper-old_ceiling)}
    if min_power>30:
        return "fixed base guard excludes the entire candidate range"
    if upper <= old_ceiling:
        return "optimistic fully charged bound cannot clear the required predecessor ceiling"
    weights, moments = grid(data)
    state["grid"] = moments
    while state["high"]-state["low"] > 1:
        if state["current_power"] is None:
            if len(state["history"]) >= CASE_CAP:
                raise TimeoutError("six distinct powers")
            p = 30 if not state["history"] else (state["high"]+state["low"])//2
            with checkpoint_update():
                state["current_power"] = p
                state["next_height"] = 0
        p = state["current_power"]
        ok, kind, facts = state.get("pending_decision") or decide(data,p,weights,state)
        entry = {"power":p,"pass":ok,"reason":kind,**facts}
        if ok:
            entry["price"] = price(data,p)
        with checkpoint_update():
            state["history"].append(entry)
            if ok:
                state["high"] = p
            else:
                state["low"] = p
            state["current_power"] = None
            state["pending_decision"] = None
            state["next_height"] = 0
    if state["high"] == 31:
        return "all powers 1 through 30 fail the frozen sufficient comparison tests"
    return "minimum admissible integer in this grid law; independent proof and consumer outstanding"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bit-source",type=Path,required=True,help="pinned BIT-451.json or source7863.tar.gz")
    parser.add_argument("--out",type=Path,required=True,help="new, writable receipt path")
    parser.add_argument("--resume",type=Path,help="previous capped receipt; another allocation must be authorized")
    args = parser.parse_args()
    if sys.version_info[:2] != (3,12) or sys.implementation.name != "cpython":
        parser.error("requires CPython 3.12")
    if args.out.exists():
        parser.error("output already exists; choose a new path")
    data = source(args.bit_source)
    key = {"source_sha256":PIN,"script_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
           "h":H_SHIFT,"seconds_per_allocation":SECONDS,"power_cap":CASE_CAP,"height_cap":HEIGHT_CAP}
    state = dict(identity=key,low=0,high=31,history=[],heights_used=0,current_power=None,next_height=0)
    if args.resume:
        previous=args.resume.read_bytes()
        state=json.loads(previous)
        if state["identity"]!=key or state["status"]!="CAPPED" or (state["heights_used"] >= HEIGHT_CAP and not state.get("pending_decision")):
            parser.error("resume requires a matching wall-clock capped receipt with remaining height budget")
        if len(state["history"]) >= CASE_CAP and state["current_power"] is None:
            parser.error("power scope exhausted")
        state["resumed_from_sha256"] = sha256(previous).hexdigest()
    def deadline(*_):
        raise TimeoutError("60-second allocation expired")
    signal.signal(signal.SIGALRM,deadline)
    signal.alarm(SECONDS)
    start=monotonic()
    try:
        state["decision"]=screening(data,state)
        state["status"]="SCREEN_COMPLETE"
    except TimeoutError as exc:
        state.update(status="CAPPED",decision=str(exc))
    finally:
        signal.alarm(0)
    state["elapsed_seconds_this_allocation"]=monotonic()-start
    state["negative_scope"]="Frozen upper base requirement, lower eta threshold, and dominating grid law only. Physical supplier and exact eta remain open."
    with args.out.open("x") as out:
        json.dump(state,out,indent=2)
        out.write("\n")
    print(state["status"],state["decision"],"see",args.out)
    return 2 if state["status"]=="CAPPED" else 0

if __name__ == "__main__":
    raise SystemExit(main())
