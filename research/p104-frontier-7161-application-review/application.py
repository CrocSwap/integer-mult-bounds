# SPDX-License-Identifier: Apache-2.0
"""Literal witness, exact scalar service, and directed application checks."""

from collections import Counter
from fractions import Fraction as Q
import runpy

from moments import derivative_upper, enclose, log, moment, power
from word import require


def expect_failure(fn, description):
    try:
        fn()
    except ValueError as err:
        return str(err)
    raise ValueError('Mutation survived: ' + description)


def signed_difference(left, right):
    return {k:left.get(k,0)-right.get(k,0) for k in left.keys()|right.keys() if left.get(k,0)!=right.get(k,0)}


def check_price(paid, target, previous, native, gate, early):
    claim, C, bit = (Q(gate[k]) for k in ('claim','tested','BIT_pin'))
    gap = (C-claim)/7
    require(gap == Q(1,10**17), 'Exact compiler funding gap')
    raw_lo, raw_hi = map(Q,early['price']['independent_raw_bracket'])
    signed = signed_difference(target, paid)
    tested, predecessor_upper = moment(signed,C)[0], moment(previous,claim)[1]
    require(0 < claim < C < raw_lo < raw_hi < bit and tested > 0
            and moment(signed,raw_lo)[0] > 0 > moment(signed,raw_hi)[1] and predecessor_upper < 0
            and derivative_upper(signed,bit) < 0, 'Separate rational crossing and predecessor rejection')
    lower = moment(target,C)[0]
    alpha = moment(paid,C)[1]/lower
    gamma = moment(paid,C-Q(1,7))[1]/(11/power(11,Q(1,7))[1]*lower)
    delta = sum(target.values())*12*power(11,C)[1]/(11*lower)
    reserve, decay, v = Q(1,10**27), Q(31,32), 1920
    require(alpha < 1-reserve and gamma < decay and delta < decay
            and 1/(1+v*reserve)+4*decay**v < 1, 'Funded ceiling, target floor and tail separation')
    require(11**64 < 12**63 and 2*(11**v)**64 <= (153**v)**63, 'Completion geometry')
    a,b = (bound/153 for bound in power(153,C))
    H, ell = int(gate['H']), gate['written_log_power']
    require((1-C)*b**v <= Q(63,64)**(ell-2) and (1-C)*a**v > Q(63,64)**(ell-1)
            and a**(-v) < 2**ell, 'Certified minimum/written logarithmic power')
    h = H*gap
    require(h.denominator == 1 and (H+1)**ell < 2**h.numerator
            and (H-gap.denominator+1)**ell >= 2**(h.numerator-1), 'Exact carrier with preceding grid control')
    lift = {7:1,3:1,5:1,9:-1,4:-1,1:-2}
    slope = sum(co*r*log(r)[int(co>0)] for r,co in lift.items())
    curvature = sum(abs(co)*r*log(r)[1]**2 for r,co in lift.items())
    require(sum(co*r for r,co in lift.items()) == 0 and slope+bit*curvature < 0
            and min(moment(lift,s)[0] for s in (claim,C)) > 0, 'Full required lift interval')
    native_paid = Counter({r:17*n for r,n in native['paid'].items()})
    remainder = signed_difference(paid,native_paid)
    require(all(n>=0 and r<=145 for r,n in remainder.items()), 'Ambient-valid paid remainder')
    mass = sum(r*n for r,n in remainder.items())
    require(mass == 109088, 'Fixed packing mass')
    relaxed = signed_difference(target,native_paid)
    relaxed[145] = relaxed.get(145,0)-Q(mass,145)
    cap_lo,cap_hi = Q('.0058056997054336'),Q('.0058056997058885')
    require(moment(relaxed,cap_lo)[0] > 0 > moment(relaxed,cap_hi)[1]
            and derivative_upper(relaxed,Q(1,32))<0, 'Independent fixed mixed-profile upper relaxation')
    return dict(tested_margin_lower=tested, prior_at_new_upper=predecessor_upper, bracket=[raw_lo,raw_hi],
                alpha_upper=enclose(alpha,alpha)[1], gamma_upper=enclose(gamma,gamma)[1],
                delta_upper=enclose(delta,delta)[1], H=H, log_power=ell, packing_bracket=[cap_lo,cap_hi],
                paid_remainder_rank_mass=mass, fraction_of_ceiling=[claim/cap_hi,claim/cap_lo])


def scalar_checks(word, caller, scalar_path):
    rational = runpy.run_path(str(scalar_path))['rational']
    coefficients = {Q(e[-2]) for e in word['program'] if e[0] in ('ADD','COPY','SCALE')}
    coefficients |= {Q(e[-1]) for e in caller['events'] if e[0]!='J' and e[1] in ('ADD','SCALE')}
    for e in caller['events']:
        if e[0] == 'J':
            coefficients |= {Q(e[3][2]),Q(e[3][3])}
        elif e[1] == 'LAMBDA':
            coefficients |= {Q(1,2),Q(e[-1],2),Q(-e[-1],2)}
    coefficients |= {Q(1125),Q(1,1125),Q(675),Q(1,675),Q(-1),Q(1)}
    num = max(abs(q.numerator).bit_length() for q in coefficients)
    div = max(q.denominator.bit_length() for q in coefficients)
    wide = Q(-97039,655360)
    require((num,div) == (24,20) and wide in coefficients, 'Literal numerator and divisor envelope')
    index = next(i for i,e in enumerate(word['program']) if e[0] in ('ADD','COPY','SCALE') and Q(e[-2]) == wide)
    valid = invalid = 0
    for q in sorted(coefficients):
        b = q.denominator
        for w in (1,7,25,65):
            limit = (2**w-1)//b
            for m in {0,min(1,limit),limit//2,limit,-limit}:
                x = m*b
                require(rational(x,q,w) == x*q and abs(x*q.numerator) < 2**(w+24), 'Exact padded scalar')
                valid += 1
        if b > 1:
            require(expect_failure(lambda:rational(1,q,b.bit_length()),'Inexact division') ==
                    'nonzero exact-division remainder','Exact rejection for each fixed divisor')
            invalid += 1
    return dict(distinct=len(coefficients), exact_cases=valid, remainder_controls=invalid,
                numerator_bits=num, divisor_bits=div, wide_divisor=[index,wide])


def boundary_check(word,witness):
    pivot=witness['pivot']
    new=word['public']-1
    cut=76298
    op=word['program']
    left,right=op[:50],op[cut+1:]
    require(op[cut]==['MOVE',133,591,127,False] and len(right)==50,'Exact new MOVE precedes exit basis')
    require(all(e[0]=='ADD' and e[-1]==3 for e in left)
         and all(e[0]=='ADD' and e[-1]==127 for e in right),'Literal common-frame basis operations')

    def role(r):
        return pivot if r==new else r

    def unpack(events):
        return [(role(r),role(s),Q(a)) for _,r,s,a,_ in events]

    inv,forward=unpack(left),unpack(right)
    require([(r,s,-q) for r,s,q in reversed(inv)]==forward,'Emitted inverse of the exit basis')
    require(all(a.denominator in (1,2,4,8,16) for _,_,a in inv+forward),'Bounded dyadic basis')
    group=set(r for r,s,_ in inv) | set(s for r,s,_ in inv)
    c,d=({int(r):Q(v) for r,v in witness[k].items()} for k in ('c','d'))
    require(set(c)|set(d)<=group,'All witness coordinates are covered by the literal basis')
    before=word['initial']
    after=word['final']
    require(all(before[r]==3 and after[new if r==pivot else r]==127 for r in group),
         'The entire original helper group uses the correct entrance and exit frames')

    def apply(state,events):
        state=state.copy()
        for r,s,a in events:
            state[r]=state.get(r,0)+a*state.get(s,0)
        return {r:x for r,x in state.items() if x}

    require(apply(d,forward)=={pivot:1},'Literal G sends d to the pivot')
    require(all(apply({r:1},forward).get(pivot,0)==c.get(r,0) and
             apply(apply({r:1},inv),forward)=={r:1} for r in group),'Literal pivot row and inverse on all basis columns')
    return dict(basis_adds=50,inverse_adds=50,largest_dyadic_denominator=16,
                pivot=pivot,group_coordinates=len(group),exit_event=cut)


def timed_witness(old, new, witness, paths):
    from word import frame_spaces, timed_vector

    def touches(e, role):
        return e[1] == role or e[0] in ("ADD", "COPY") and e[2] == role

    c = timed_vector(old, witness, suffix=False)
    d = timed_vector(old, witness, suffix=True)
    expected = [{int(r): Q(x) for r, x in witness[key].items()} for key in ("c", "d")]
    overlap = c.keys() & d.keys()
    require([c, d] == expected and overlap == {133, 445, 1242, 1336}
            and sum(c[r]*d[r] for r in overlap) == 1, "Exact timed vectors and unit pairing")
    x = witness["extension"]
    role, a, b, t = (x[key] for key in ("role", "old", "new", "cut"))
    f, pivot = witness["frame"], witness["pivot"]
    spans = frame_spaces(old)
    start = old["initial"][pivot]
    require((role, a, b, t) == (133, 591, 127, len(old["program"]))
            and old["final"][role] == a and new["final"][role] == b
            and old["initial"][role] == new["initial"][role] == start
            and spans[a] < spans[b] and spans[start] < spans[f] < spans[b],
            "Extended public boundary and nested productive split")
    require(len(old["frames"][b])-len(old["frames"][a]) == 1
            and [len(old["frames"][v])-len(old["frames"][u]) for u, v in ((start, f), (f, b))]
            == witness["ranks"] == [5, 4] and witness["paid_delta"] == {},
            "Only the appended rank-one exit changes the paid profile")
    group = c.keys() | d.keys()
    main = set(old["live"]) | {r+112 for r in old["live"]} | set(old["hosted"]["X2"]+old["hosted"]["Y2"])
    require(not group & main and all(old["initial"][r] == start and
            (b if r == role else old["final"][r]) == b for r in group),
            "All timed support belongs to the one extended helper group")
    program = old["program"]
    seen = set()
    for path in paths:
        r, lo, hi = (path[key] for key in ("role", "lo", "hi"))
        require(0 <= lo < hi <= len(program), "Retiming range")
        hits = [i for i in range(lo, hi) if touches(program[i], r)]
        require(hits == path["moves"] and hits and not seen.intersection(hits),
                "Every contact is on its exact retiming and there is no overlap")
        seen.update(hits)
        events = [program[i] for i in hits]
        require(all(e[0] == "MOVE" for e in events)
                and [events[0][2], *(e[3] for e in events)] == path["frames"]
                and [e[2] for e in events] == path["frames"][:-1] and f in path["frames"],
                "The neutral path is continuous and reaches its declared frame")
    stationary = []
    for obs in witness["gathers"] + witness["injections"]:
        r, t = obs["role"], obs["cut"]
        if "path" in obs:
            p = paths[obs["path"]]
            require(p["role"] == r and p["lo"] <= t <= p["hi"], "Observation on its literal retiming")
        else:
            first = next(i for i, e in enumerate(program) if touches(e, r))
            require(t == 0 and old["initial"][r] == f and obs["stationary_interval"] == [0, first],
                    "Stationary cut before the first literal contact")
            stationary.append([r, 0, first])
    require(stationary == [[1362, 0, 35561], [1386, 0, 35607]] and len(paths) == 15
            and len(witness["gathers"]) == 12 and len(witness["injections"]) == 5,
            "Complete stationary, gather, injection and retiming inventory")
    return dict(pairing=1, c_support=len(c), d_support=len(d), stationary=stationary,
                neutral_paths=len(paths), gathers=12, injections=5, retirement_cut=witness["cut"])


def check_precision(receipt, native_hash, caller_hash, H):
    checks = receipt["checks"]
    p = checks["ODD-PRECISION.json"]
    fixed = checks["ODD-FIXED-TAPE-COUNTS.json"]
    require((p["native_sha256"], p["caller_sha256"]) == (native_hash, caller_hash)
            == (fixed["native_sha256"], fixed["caller_sha256"]), "Precision belongs to this exact supplier/caller")
    require(p["caller_grid"]["grid_exponents"] == [381, 3, 2]
            and p["caller_grid"]["caller_odd_scale"] == "675"
            and p["native_grid"]["dyadic_height"] == 25
            and p["native_grid"]["odd_scale_lcm"] == 1125,
            "The exact common native and caller grids")
    height = p["caller_grid"]["grid_exponents"][0] + p["native_grid"]["dyadic_height"]
    context = 2 * max(height, p["context_mass_bits"])
    require(height == p["context_height"] == 406 and p["context_mass_bits"] == 1215
            and context == fixed["context_c"] == p["context_c"] == 2430 and fixed["H"] == H,
            "Exact changed exterior precision context")
    for component in ("rounded_caller", "rounded_native"):
        require(all(Q(v["exact"]) < 2**v["strict_power_of_two"] and v["strict_power_of_two"] < H
                    for v in p[component]["bounds"].values()), "Literal precision envelope " + component)
    K = 1920 * 153**1920 * (H+1)**2
    require(context < 4096 and K.bit_length() == fixed["Kstar_bits"] and (4096*K).bit_length() < H,
            "Precision depth fits the funded carrier")
    require(fixed["common_grid"] == dict(fractional="p+D", signed_width="p+h+2D+3", temp_padding=26),
            "One complete root, common field and padded format")
    return dict(height=height, mass_bits=p["context_mass_bits"], context=context,
                native_odd_scale=1125, native_fractional_depth=25, caller_odd_scale=675,
                Kstar_bits=K.bit_length(), funded_context=True)


def check_outer(receipt, selected, price, outer_path, proposed):
    g0 = receipt["price"]["gate"]
    k, C = Q(g0["claim"]), Q(g0["tested"])
    g = (C-k)/7
    require(g == Q(1, 10**17) and k-Q(selected["kappa"]) == Q(".000014831897940"),
            "Exact frontier and funding comparison")
    bit = Q(selected["complex_BIT_premise"])
    require(Q(selected["admitted_BIT_saving"]) > bit > C, "Retained admitted BIT above the premise")
    model = runpy.run_path(str(outer_path))
    params = model["parameters"](k, C) | {"bit_saving": bit}
    check = model["evaluate"](params)
    guards, functional = check["strict_checks"], check["functional_checks"]
    require(check["all_positive"] and len(guards) == 54 and len(functional) == 4
            and min(*guards.values(), *functional.values()) == Q(1, 10**18), "Every actual outer guard")
    epsilon, beta = 1-g, 1-3*g
    a, q = k+4*g, k+3*g
    xi = epsilon*(1+q)-Q(3, 32)+g
    independently = {
        "main_transform": epsilon*q, "global_coordinate_router": a,
        "fused_gaussian": 1-epsilon+q*beta, "group_bit_router": 1-epsilon+a*beta,
        "group_scans": 1-epsilon+beta, "boundary_algebraic_matrix": Q(3,32)+xi-epsilon,
        "sparse_union_movement": xi+Q(1,2)-epsilon, "polynomial_products": epsilon,
        "microbox_face_corrections": 1-(epsilon+beta+48-128+2),
    }
    require(independently == check["margins"] and min(independently, key=independently.get) == "main_transform",
            "Nine independent saving formulas agree")
    lowest = min(independently.values())
    slack = lowest-k
    require(slack == 299635510993205997*Q(1, 10**34) > 0, "Exact limiting slack")
    controls = []
    for b in (a, a-Q(1, 10**12)):
        broken = model["evaluate"](params | {"bit_saving": b})
        gap = broken["strict_checks"]["actual_bit_above_effective"]
        require(not broken["all_positive"] and gap == b-a <= 0, "Actual BIT mutation fails")
        controls.append(dict(bit_saving=b, margin=gap, accepted=False))
    deficit = 1-price["alpha_upper"]
    require(deficit > Q("7.18e-18"), "Positive rational funding deficit hidden by float display")
    expected = selected | {
        "kappa": str(k),
        "source_result": "research/p104-rank8-exit-funded-split/RESULT.json",
        "uniform_templates": [
            dict(family="complex", rank_encoding="2^"+str(price["H"]), saving=str(k+6*g), ambient=153),
            selected["uniform_templates"][1],
        ],
        "nine_outer_savings": {key: str(s) for key, s in independently.items()},
        "outer_formula_source": "research/final4610-independent-admission/checks/outer.py",
        "limiting_outer_saving": str(lowest),
        "strict_limiting_slack": str(slack),
        "scope": "Conditional application of the exact #7161 funded-exit supplier and retained #7113 signed caller. "
                 "Maintainer selection, a materialized multiplier and formal-kernel acceptance are outside this proposal.",
    }
    require(expected == proposed, "Every proposed claim field, including the five assumptions")
    return dict(kappa=k, delta_over_selected=k-Q(selected["kappa"]),
                delta_over_predecessor=k-Q(".003644407895539"), funded_price=C, gap=g,
                alpha_deficit_lower=deficit, strict_guards=len(guards), functional_guards=len(functional),
                minimum_guard=min(*guards.values(), *functional.values()), bit_controls=controls,
                limiting_component="main_transform", limiting_slack=slack, nine_savings=independently)
