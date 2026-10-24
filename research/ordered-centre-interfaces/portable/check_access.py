"""Check the actual 25-axis views and the cheaper common-frame gauge."""

from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parents[1] / 'frozen' / 'work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/matched-stage-review-20261018'
CHECKER_SHA = sha256(Path(__file__).read_bytes()).hexdigest()
LANES = HERE.parents[1]
ROOT = LANES.parents[2]
ACCESS = LANES / "bridge-access-20261017/matched-stage-access-20261018"
GAUGE = LANES / "independent-review-20261017/matched-full-gauge-20261018"
PINS = {
    "access_freeze":"0b3e4f09ea0eff1f6106a2611ac80cf0976638da96e7c0e5b289224b159ba96c",
    "gauge_freeze":"a83fad6b1fe12e1cad34989ad4226ab9d1d2fb268362b010845deaea2f42034d",
    "views_compressed":"1da2f6a6058661f19e971bb31f1823585f01c2494dca813e208af45aea7a582f",
    "matching":"e2443eee2a7081ce3b57b9b7afcf4f1b061b9d8ddf0fbbeb5f7b29ce0d148902",
    "native_decompressed":"95f11d2b13fc75cb0d07e79ea17afdf3f46b4aca294117ffe1a988779e99f025",
    "archive":"f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6",
    "data":"c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    "controller":"f66186f2f67ea00eb8ae6447ec9cbddbdf410f141e61149871b0915e599845d7",
}
E = [1 << j for j in range(25)]
MASK = (1 << 25)-1


def need(test, message):
    if not test:
        raise ValueError(message)


def pin(path, key, compressed=False):
    raw = path.read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == PINS[key], "Pinned source: " + key)
    return raw


def frozen(folder, key):
    manifest = json.loads(pin(folder/"FREEZE.json", key))
    for name, digest in manifest["files"].items():
        need(sha256((folder/name).read_bytes()).hexdigest() == digest, "Frozen artifact: " + name)


def act(columns, x):
    out = 0
    for j, value in enumerate(columns):
        if x >> j & 1:
            out ^= value
    return out


def phase(terms):
    """Use Z4 basis values and binary off-diagonal polar rows."""
    diagonal, polar = [0]*25, [0]*25
    for vector, exponent in terms:
        need(vector <= MASK, "The phase direction lies in dimension25")
        for j in range(25):
            if vector >> j & 1:
                diagonal[j] += exponent
                if exponent % 2:
                    polar[j] ^= vector ^ (1 << j)
    return tuple(x % 4 for x in diagonal), tuple(polar)


def translated(terms, rho, delta):
    return phase([(act(rho, v), a) for v, a in terms] + [(delta, 2)])


def matrix(rows):
    return [{int(j):F(a) for j, a in row.items()} for row in rows]


def product(a, b):
    out = []
    for row in a:
        values = defaultdict(F)
        for j, x in row.items():
            for k, y in b[j].items():
                values[k] += x*y
        out.append({k:v for k, v in values.items() if v})
    return out


def scalar_replay(events):
    rows = [{p:F(1)} for p in range(112)]
    price, peak = 0, F(1)
    counts = Counter()
    for event in events:
        op, target = event[:2]
        c = F(*event[-2:])
        numerator, denominator = abs(c.numerator), c.denominator
        need(numerator > 0 and denominator & (denominator-1) == 0, "Nonzero dyadic coefficient")
        if op == "scale":
            need(len(event) == 4 and numerator & (numerator-1) == 0, "Unit dyadic SCALE")
            rows[target] = {p:c*a for p, a in rows[target].items()}
            price += 2*(abs(numerator.bit_length()-denominator.bit_length()) + (c < 0))
        else:
            need(op == "add" and len(event) == 5 and target != event[2], "Plain in-place ADD")
            values = defaultdict(F, rows[target])
            for p, a in rows[event[2]].items():
                values[p] += c*a
            rows[target] = {p:a for p, a in values.items() if a}
            price += 2*(1+numerator.bit_length()+numerator.bit_count()+denominator.bit_length())
        counts[op] += 1
        peak = max(peak, sum(abs(a) for a in rows[target].values()))
    return rows, price, peak, counts


def reverse_columns(events):
    columns = [{p:F(1)} for p in range(112)]
    for event in reversed(events):
        c = F(*event[-2:])
        target = event[1]
        if event[0] == "scale":
            columns[target] = {p:c*a for p, a in columns[target].items()}
        else:
            source = event[2]
            values = defaultdict(F, columns[source])
            for p, a in columns[target].items():
                values[p] += c*a
            columns[source] = {p:a for p, a in values.items() if a}
    return columns


def main():
    frozen(ACCESS, "access_freeze")
    frozen(GAUGE, "gauge_freeze")
    packed = pin(LANES/"bridge-access-20261017/BRIDGE-PROGRAMS.json.gz", "views_compressed")
    original_views = json.loads(gzip.decompress(packed))["views"]
    views = {(v["stage"],v["port"],v["side"]):v for v in original_views}
    raw = (ROOT / "archive-members/DATA-PHASES.json").read_bytes()
    need(sha256(raw).hexdigest() == PINS["data"], "Actual DATA phase source")
    data = json.loads(raw)["recipes"]
    dimensions = json.loads((ACCESS/"DIMENSION25-VIEWS.json").read_text())
    entries = {(r["stage"],r["port"]):r for r in dimensions["entries"]}
    counts = Counter()
    cone = {}
    for p, row in enumerate(data):
        q = row["q"]
        for s in range(3):
            full_rho = [1 << j for j in range(73)] if s == 0 else views[s,p,"X"]["route_columns"]
            need(all(x <= MASK for x in full_rho[:25]) and full_rho[25:] == [1 << j for j in range(25,73)],
                 "No route uses a discarded coordinate")
            rho = full_rho[:25]
            need(all(((a&b).bit_count() % 2) == (i == j) for i,a in enumerate(rho) for j,b in enumerate(rho)),
                 "Exact O25 membership")
            need([act(rho, x) for x in rho] == E and act(rho,q) == q, "Route inverse and fixed intrinsic line")
            record = entries[s,p]
            align = row["stage_alignment"][s]
            need(record == {"port":p,"stage":s,"q":q,"route_columns":rho,"literal_stage_alignment":align},
                 "Every emitted dimension25 record equals actual source data")
            need(all(x <= MASK for x in align.values()), "Every entry and exit translation restricts")
            counts["orthogonal_routes"] += 1
            for side in ("X","Y"):
                before = ([(q,1)] if side == "X" else []) if s == 0 else [(x,1) for x in E[:9+8*(s-1)]]
                if s and side == "Y":
                    before += [(q,-1)]
                want = [(x,1) for x in E[9:9+8*s]] + ([(q,1)] if side == "X" else [])
                delta = act(rho,align["entry_"+side])
                need(translated(before,rho,delta) == phase(want), "Exact current entry with common exterior")
                counts["entry"] += 1
                counts["entry_omission_controls"] += translated(before,rho,0) != phase(want)
                after = [(x,1) for x in E[:9+8*s]] + ([(q,-1)] if side == "Y" else [])
                need(translated(after,rho,align["exit_"+side]) == phase(after), "Exact current exit")
                counts["exit"] += 1
                counts["exit_omission_controls"] += translated(after,rho,0) != phase(after)
            for level in range(s,3):
                full = [(x,1) for x in E[:9+8*level]]
                delta = 0 if s == 0 else views[s,p,"X"]["translation_after_route"]
                need(translated(full,rho,delta) == phase(full), "Every past-X view")
                counts["past_X"] += 1
                cone[s,level,"X",p] = True
            for level in range(s):
                hole = [(x,1) for x in E[:9+8*level]] + [(q,-1)]
                common = [(x,1) for x in E[9:9+8*level]+E[9+8*(s-1):9+8*s]]
                delta = views[s,p,"Y"]["translation_after_route"]
                need(translated(hole,rho,delta) == phase(common), "Every future-Y view")
                counts["future_Y"] += 1
                cone[s,level,"Y",p] = True
    cuts = [(0,0,"X"),(1,0,"Y"),(1,1,"X"),(2,1,"Y"),(1,2,"X")]
    controller = json.loads(pin(LANES/"encoded-controller/one-pair-current-codes-20261018/PROGRAM.json",
                                "controller"))
    need(controller["program"] == [
        ["forward",0],["code_X",0,1],["code_Y",1,1],
        ["backward",1],["code_X",1,1],["code_Y",2,1],
        ["forward",2],["code_X",1,-1]], "The pinned controller gives these five code cuts")
    need(all(cone[s,level,side,p] for s,level,side in cuts for p in range(112)), "All five actual one-pair code cuts")
    counts["one_pair_code_port_cuts"] = len(cuts)*112

    matching = json.loads(pin(LANES/"controller-followthrough-20261017/matched-involution-20261018/MATCHED-INVOLUTION-PROGRAM.json", "matching"))
    native = json.loads(pin(LANES/"oblique-native-20261017/matched-native-involution/MATCHED-NATIVE-PROGRAM.json.gz", "native_decompressed", True))
    response = matrix(native["response"])
    gauge = json.loads((GAUGE/"FULL-GAUGE.json").read_text())
    need(response == matrix(gauge["response"]) == matrix(json.loads((ACCESS/"FULL-GAUGE-PROGRAM.json").read_text())["response"]),
         "The cheaper gauge and stage packet use the actual same full response")
    need(product(response,response) == [{p:F(1)} for p in range(112)], "The actual response is an involution")
    need(all(p not in row for p,row in enumerate(response)), "No physical fixed point")
    need(Counter(map(len,response)) == {4:48,1:64}, "The actual dense48 and permutation64 supports")
    for provider in native["providers"].values():
        for word in provider.values():
            need(all(word["frames"][word["final"][p]] == word["frames"][1] for p in range(112)),
                 "All native X outputs have one common FULL frame")
            need(sorted(word["frames"][1]) == [1 << j for j in range(9)], "Actual local FULL frame")
    events = gauge["events"]
    result, price, peak, census = scalar_replay(events)
    need(result == response and reverse_columns(events) == response, "All rows and independent columns of the scalar word")
    need(scalar_replay(events+events)[0] == [{p:F(1)} for p in range(112)], "The literal word squared is identity")
    c = gauge["cuts"]
    parts = [events[:c["code_end"]],events[c["code_end"]:c["swap_end"]],
             events[c["swap_end"]:c["undo_end"]],events[c["undo_end"]:]]
    bills = [scalar_replay(part)[1] for part in parts]
    need(bills == [470,624,470,832] and price == 2396 and peak == 4, "Exact complete scalar price and prefix norm")
    need(scalar_replay(parts[0]+parts[1]+parts[3])[0] != response, "Omitting the pair undo must fail")
    need(all(gauge[name] == 0 for name in ("owned_fields","private_fields","native_children")), "No hidden scratch or native work")
    # Pair-code algebra uses arbitrary values, and never a zero target.
    for pair in matching["pair_codes"]:
        a,b = map(F,pair["matrix"][0])
        c0,d = map(F,pair["matrix"][1])
        need(all(abs(x) == 1 for x in (a,b,c0,d)) and d == -a*b*c0,
             "Every four-operation pair code has the stated exact matrix")
    need(sha256(Path(__file__).read_bytes()).hexdigest() == CHECKER_SHA, "Checker bytes stayed fixed")
    receipt = {
        "status":"PASS_INDEPENDENT_MATCHED_D25_ACCESS_AND_FULL_GAUGE",
        "source_pins":PINS,
        "checker_sha256":CHECKER_SHA,
        "counts":dict(sorted(counts.items())),
        "actual_one_pair_cuts":[{"stage":s,"completed_level":level,"bank":side} for s,level,side in cuts],
        "common_frame_scalar_primitives":price,
        "component_scalar_primitives":bills,
        "scalar_events":dict(census),
        "exact_prefix_row_one_norm":str(peak),
        "native_children_in_gauge":0,
        "owned_fields_in_gauge":0,
        "maximum_monomial_view_calls_per_gauge":224,
        "five_gauge_scalar_primitives":5*price,
        "scope":"Actual D25 stage views, five one-pair scalar access cuts, and complete2396-scalar common-frame gauge. No three-factor terminal, recursive host or supplier claim in this receipt.",
    }
    (HERE/"ACCESS-REVIEW.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
