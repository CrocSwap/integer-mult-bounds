"""Check exact price certificates and the field-dependent tariff without an LP solver."""
from dataclasses import astuple
from itertools import combinations
from signatures import profiles, verdict


def dot(left, right):
    return sum(x*y for x,y in zip(left,right,strict=True))


def check_certificates(records):
    binary = {astuple(v) for v in profiles(6) if verdict(3,3,v,True) == "ok"}
    missing = {astuple(v) for v in profiles(6) if verdict(3,3,v) == "ok"} - binary
    seen = set()
    outside = 0
    for record in records:
        row = tuple(record["counts"])
        if row not in missing or row in seen:
            raise ValueError("price certificate profile")
        seen.add(row)
        if "prices" in record:
            prices = record["prices"]
            if not all(type(c) is int and c > 0 for c in prices):
                raise ValueError("positive integral tariff")
            if min(dot(prices,y) for y in binary) <= dot(prices,row):
                raise ValueError("price does not strictly separate")
            outside += 1
        else:
            mix = [(entry["weight"],tuple(entry["counts"])) for entry in record["mixture"]]
            if not mix or any(type(w) is not int or w < 1 or y not in binary for w,y in mix):
                raise ValueError("invalid binary price mixture")
            total = sum(w for w,_ in mix)
            if any(sum(w*y[i] for w,y in mix) != total*row[i] for i in range(7)):
                raise ValueError("convex combination differs from profile")
    if seen != missing:
        raise ValueError("incomplete price certificate list")
    return {"separated":outside, "in_binary_convex_hull":len(seen)-outside}


def parity_family():
    rows = []
    for d in range(2,9):
        regular, binary = 20*d, 20*d
        for v in profiles(2*d):
            if verdict(d,d,v) != "ok":
                continue
            price = dot(astuple(v), (3,3,3,1,2,2,2))
            regular = min(regular,price)
            if verdict(d,d,v,True) == "ok":
                binary = min(binary,price)
        if regular != 3*d+1 or binary != regular + (d % 2):
            raise ValueError("parity tariff minima")
        rows.append([d,regular,binary])
    return rows


def literal_prices(codes, binary_codes, p, n):
    """Exhaust all actual six-port signatures for label-dependent monotone fees."""
    receipts = []
    for seed in range(12):
        tariffs = []
        for j in range(n):
            # Nonnegative weights on source, reader and source-reader indicators.
            s_weights = [(3*j+seed+2)%11, (j*j+2*seed+1)%13]
            r_weights = [(2*j+3*seed+1)%7, (4*j+seed+4)%11]
            row = [0]*16
            for s in (1,2,3):
                for r in (1,2,3):
                    value = sum(s_weights[i] for i in range(2) if s & (1<<i))
                    value += sum(r_weights[i] for i in range(2) if r & (1<<i))
                    value += (j+seed)%5 * int(bool(s & 1) and bool(r & 2))
                    row[4*s+r] = value
            tariffs.append(row)
        baseline = sum(row[10] for row in tariffs)
        optimum = baseline + sum(sorted(row[5]-row[10] for row in tariffs)[:p])
        assignments = [sum(t[5] if j in choice else t[10] for j,t in enumerate(tariffs))
                       for choice in combinations(range(n),p)]
        best_any = best_binary = 10**9
        for code in codes:
            fee = sum(row[(code >> (4*j)) & 15] for j,row in enumerate(tariffs))
            best_any = min(best_any,fee)
            if code in binary_codes:
                best_binary = min(best_binary,fee)
        if not (optimum == min(assignments) == best_any == best_binary):
            raise ValueError("message-dependent monotone tariff")
        receipts.append(optimum)
    return receipts
