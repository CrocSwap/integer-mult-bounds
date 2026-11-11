# SPDX-License-Identifier: Apache-2.0
"""Exact four-root caller replay and source-bound finite tariffs."""

from collections import Counter
from fractions import Fraction as Q

from word import require

UNIT = 675 * 2**381
I_POWERS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def four_root(caller, root, mutation=None):
    """Evaluate only q; keep all body degrees and input coordinates formal.

    Distinct roots 1,i,-1,-i detect any nonzero coefficient of degree <4 in
    q. This proves equality modulo q^4-1 without interpolating body powers.
    """
    stages = caller["stages"]
    rows = [{(j, (0,)*stages): (UNIT, 0)} for j in range(caller["roles"])]
    touched_stages = []
    checked_divisions = 0
    peak_terms = 0
    mutated = False

    def add(out, source, multiplier=Q(1), q=0, i=0, bodies=()):
        nonlocal checked_divisions
        power = (root*q+i) % 4
        u, v = I_POWERS[power]
        a, b = multiplier.numerator, multiplier.denominator
        for (owner, degrees), (x, y) in source.items():
            rx, ry = u*x-v*y, v*x+u*y
            if b > 1:
                rx, dx = divmod(rx, b)
                ry, dy = divmod(ry, b)
                require(dx == dy == 0, "Exact Gaussian coefficient at each fourth root")
                checked_divisions += 1
            if bodies:
                degree = list(degrees)
                for s in bodies:
                    degree[s-1] += 1
                degrees = tuple(degree)
            key = owner, degrees
            ox, oy = out.get(key, (0, 0))
            new = ox+a*rx, oy+a*ry
            if new != (0, 0):
                out[key] = new
            else:
                out.pop(key, None)

    def mapped(source, **kwargs):
        out = {}
        add(out, source, **kwargs)
        return out

    for e in caller["events"]:
        if e[0] == "J":
            _, s, a_owners, b_owners = e
            if mutation == "alias_stage" and s == 2:
                a_owners = [1,0,18,18+s]
                mutated = True
            require(a_owners == [s,0,18,18+s] and b_owners == [36,37,"-1","1/2"],
                    "Exact caller stage ownership")
            touched_stages.append(s)
            u, v, x, y = a_owners
            add(rows[v], rows[u], q=-1)
            add(rows[x], rows[y], multiplier=Q(caller["types"]["A"]["alpha2"]), q=1)
            for owner in a_owners:
                rows[owner] = mapped(rows[owner], bodies=(s,))
            u, v, a, b = b_owners
            ru = mapped(rows[u], bodies=(s,))
            add(ru, rows[v], multiplier=Q(a), q=1, bodies=(s,))
            rv = mapped(rows[v], multiplier=Q(b), bodies=(s,))
            add(rv, rows[u], multiplier=Q(b), q=-1, bodies=(s,))
            rows[u], rows[v] = ru, rv
        else:
            ty, op, r, *args = e
            t = caller["types"][ty]
            allowed = range(t["offset"], t["offset"]+t["roles"])
            require(r in allowed, "Target belongs to its own caller type")
            if op in ("ADD","SWAP","QUERY"):
                s = args[0]
                require(s in allowed and s != r, "Distinct source belongs to its own caller type")
            if op == "ADD":
                add(rows[r], rows[s], multiplier=Q(args[1]))
            elif op == "SCALE":
                rows[r] = mapped(rows[r], multiplier=Q(args[0]))
            elif op == "SWAP":
                rows[r], rows[s] = rows[s], rows[r]
            elif op == "QUERY":
                q = args[1]
                if mutation == "reverse_query" and not mutated:
                    q = -q
                    mutated = True
                add(rows[r], rows[s], q=q)
            elif op == "LAMBDA":
                # (1+is + (1-is)*q^2)/2 is 1 at q=±1 and i*s at q=±i.
                # No interpretation as a separate lambda on each axis.
                sign, = args
                if mutation == "reverse_lambda" and not mutated:
                    sign = -sign
                    mutated = True
                if root % 2:
                    rows[r] = mapped(rows[r], i=sign)
            else:
                require(op in ("IDLE_ONE","IDLE_ODD"), "Exact caller alphabet")
                body = args[0]
                require(body and len(set(body)) == len(body) and all(1 <= b <= stages for b in body), "Idle body")
                sign = args[1] if op == "IDLE_ODD" else 0
                if op == "IDLE_ODD" and mutation == "reverse_odd_idle" and not mutated:
                    sign = -sign
                    mutated = True
                rows[r] = mapped(rows[r], q=sign, bodies=body)
        peak_terms = max(peak_terms, sum(len(row) for row in rows))
    require(touched_stages == list(range(1,stages+1)), "Each independent stage used exactly once by J")
    require(mutation is None or mutated, "Mutation reached the designated literal event")
    for t in caller["types"].values():
        for r,(q,spare,*body) in enumerate(t["diagonal"], t["offset"]):
            require(spare==0 and len(body)==stages and all(k in (0,1) for k in body), "Complete diagonal")
            u, v = I_POWERS[(root*q) % 4]
            require(rows[r] == {(r,tuple(body)):(UNIT*u,UNIT*v)}, f"Wrong signed diagonal for public role {r}")
    return dict(q_power_of_i=root, literal_events=len(caller["events"]), roles=len(rows), peak_terms=peak_terms,
                exact_divisions_at_root=checked_divisions)


def scalar_units(coefficient, addition):
    q = Q(coefficient)
    magnitude = abs(q.numerator)
    return 4*(magnitude.bit_length()+q.denominator.bit_length()+1+addition*magnitude.bit_count())


def finite_charges(word, native, caller, receipt):
    c = caller["types"]
    stages = caller["stages"]
    actual_axes = 9+8*stages
    require((stages,actual_axes)==(17,caller["ambient_rank"]) and actual_axes==145, "Exact ambient")
    ports_a = len(c["A"]["ports"])
    ports = sum(len(t["ports"]) for t in c.values())
    require(c["A"]["ports"]==word["hosted"]["Dports"] and
            sorted(c["A"]["ports"]+c["B"]["ports"])==list(range(104)), "Complete 96+8 ports")
    native_paid = Counter({int(r):n for r,n in native["paid"].items()})
    main_roles = set(word["live"]) | {r+112 for r in word["live"]} | set(word["hosted"]["X2"]+word["hosted"]["Y2"])
    helper_ranks = Counter(len(word["frames"][word["final"][r]])-len(word["frames"][word["initial"][r]])
                           for r in set(range(word["public"]))-main_roles)
    paid = Counter({r:stages*n for r,n in native_paid.items()})
    productive = Counter({r:stages*n for r,n in helper_ranks.items()})
    op_counts = Counter()
    native_route = sum(native_paid.values())+2*sum(helper_ranks.values())+6*(ports+ports_a)+4*native["lifetimes"]
    scalar = sum(scalar_units(e[-2],e[0]!="SCALE") for e in word["program"] if e[0] in ("ADD","COPY","SCALE"))
    ordinary_caller = {}
    caller_surcharges = 0

    def outside_canonical(axes):
        return sum(axis>=len(axes) for axis in axes)

    def stage_axes(stage):
        return range(9+8*(stage-1),9+8*stage)

    for ty,t in c.items():
        p = len(t["ports"])
        ops = [e for e in caller["events"] if e[0]==ty]
        events = Counter(e[1] for e in ops)
        for op,n in events.items():
            op_counts[op] += n*p
        output_routes = idle_routes = query_routes = 0
        for signed,spare,*bits in t["diagonal"]:
            require(signed==-1 and spare==0 and any(bits), "Nonempty signed root job")
            chosen = [s for s,bit in enumerate(bits,1) if bit]
            productive[1+8*len(chosen)] += p
            actual = [0]+[axis for s in chosen for axis in stage_axes(s)]
            output_routes += 1000*p*(2*outside_canonical(actual)+3)
        for e in ops:
            op = e[1]
            if op=="QUERY":
                paid[1] += p
                query_routes += 1000*p*(2+(e[-1]==-1))
            elif op in ("IDLE_ONE","IDLE_ODD"):
                paid[8*len(e[3])+(op=="IDLE_ODD")] += p
                if op=="IDLE_ONE":
                    actual = [axis for s in e[3] for axis in stage_axes(s)]
                    idle_routes += 2000*p*outside_canonical(actual)
            elif op in ("ADD","SCALE"):
                caller_surcharges += p*scalar_units(e[-1],op=="ADD")
        ordinary_caller[ty] = dict(
            envelope=32*t["roles"]*p*(stages+len(ops)),field_boundary=26*t["roles"]*p,
            fused_routes=36500*p*events["IDLE_ODD"],idle_routes=idle_routes,output_routes=output_routes,
            query_routes=query_routes,thin=16*p*events["QUERY"],
        )
    main = sum(len(t["ports"])*t["roles"] for t in c.values())
    raw = stages*(1000*native_route+scalar)+sum(sum(row.values()) for row in ordinary_caller.values())
    native_conversions = 104*stages*word["public"]
    lambda_second = 1000*op_counts["LAMBDA"]
    caller_scale = 675
    caller_odd_conversions = 2*main*4*(caller_scale.bit_length()+1+caller_scale.bit_count())
    ordinary = raw+native_conversions+lambda_second+caller_surcharges+caller_odd_conversions
    got = receipt["checks"]["ODD-ADMISSION-PARTIAL.json"]["ordinary"]
    require((raw,native_conversions,lambda_second,caller_surcharges,caller_odd_conversions,ordinary)==
            tuple(got[k] for k in ("raw_upper","per_input_conversion","lambda_second_charge",
                                   "all_caller_scalar_surcharge","charged_caller_odd_conversions","conservative_total"))
            and got["caller_items"]==ordinary_caller and got["scalar_upper"]==scalar
            and got["routing"]==1000*native_route and ordinary==782129100<10**9,
            "Exact 17-stage ordinary source tariff and all components")
    require({str(k):v for k,v in paid.items()} == receipt["price"]["after"]["P"] and
            {str(k):v for k,v in productive.items()} == receipt["price"]["after"]["T"], "Complete signed rank invoice")
    counts = receipt["checks"]["ODD-FIXED-TAPE-COUNTS.json"]
    contacts = 4*stages*(ports_a+ports)
    idles = op_counts["IDLE_ONE"]+op_counts["IDLE_ODD"]
    maps = 2*(sum(paid.values())+sum(productive.values()))+contacts+2*idles+op_counts["IDLE_ODD"]
    maps += 3*op_counts["QUERY"]+op_counts["LAMBDA"]
    services = 32*(stages*(len(word["program"])-sum(native_paid.values()))+sum(op_counts.values())+
                   2*(stages*word["public"]+main))
    records = maps*4*(actual_axes+1)**2
    require((maps,services,records,services*2**20,stages*native["owned"]) ==
            tuple(counts[k] for k in ("monomial_map_slots","scalar_services_upper","elementary_records_upper",
                                      "scalar_steps_coefficient","owned_banks_per_raw_occurrence")),
            "Reconstructed map, service, record and bank charges")
    surplus = sum(r*n for r,n in productive.items())-sum(r*n for r,n in paid.items())
    require(surplus==1424 and counts["context_c"]==2430, "Surplus and fixed context")
    return dict(paid=sum(paid.values()),productive=sum(productive.values()),surplus=surplus,
                raw_ordinary=raw,native_conversions=native_conversions,lambda_second_charge=lambda_second,
                caller_scalar_surcharge=caller_surcharges,caller_odd_conversions=caller_odd_conversions,
                complete_ordinary=ordinary,caller_ordinary_components=ordinary_caller,contacts=contacts,
                monomial_maps=maps,elementary_records=records,scalar_services=services,
                scalar_step_coefficient=services*2**20,ambient=actual_axes,stage_macros=op_counts,
                native_banks=stages*native["owned"],serial_bank=1,
                paid_histogram=dict(paid),productive_histogram=dict(productive))



def check(caller, word, dense, receipt, fixture):
    evaluations = [four_root(caller, r) for r in range(4)]
    controls = {}
    tests = (
        ("alias_stage", "Exact caller stage ownership"),
        ("reverse_query", "Wrong signed diagonal"),
        ("reverse_lambda", "Wrong signed diagonal"),
        ("reverse_odd_idle", "Wrong signed diagonal"),
    )
    for tag, expected in tests:
        try:
            four_root(caller, 1, tag)
        except ValueError as exc:
            require(str(exc).startswith(expected), f"Unexpected {tag} control: {exc}")
            controls[tag] = str(exc)
        else:
            raise ValueError(f"Surviving signed-caller control: {tag}")
    bill = finite_charges(word, dense, caller, receipt)
    ingredient = fixture["ordinary"]
    require(ingredient["conservative_total"] == 856124152
            and ingredient["per_input_conversion"] == 18 * word["public"] * 104
            and bill["native_conversions"] == 17 * word["public"] * 104,
            "Keep the 18-stage fixture distinct from the actual 17-stage bill")
    return dict(evaluations=evaluations, controls=controls, bill=bill,
                reference_18_stage_ordinary=ingredient["conservative_total"])
