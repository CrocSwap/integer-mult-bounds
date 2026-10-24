"""Check the terminal kernels, ordered endpoint, and data-only role stock."""

from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
ROOT = LANES.parents[2]
SELF_PIN = sha256(Path(__file__).read_bytes()).hexdigest()
UNIT = [1 << j for j in range(25)]
PINS = {
    "access": "13df3e89b983936bd2126c67204d229fc25d1f9f011fc77505c3376476fbd499",
    "triple": "0a20fdae1f2497088e0e62e72960d81c44c48805b5685b08710ceed898bc22ce",
    "admission": "0c27631267119efca1a416f0f299a2ce398a87fea313611341133b7c3736d8ed",
    "admission_proof": "799eab4224c40ec980712593cb1bcd8e62522f1fb1b5ebe79d0f3569d10111de",
    "admission_sources": "49cce325ea25508f7ff22f3ec48e8ef01297104bc76a9080d482a4f9ba929f46",
    "native_review": "952019e4611494972f67bf76b3636886260e425ecca2a67ceb512b144808587b",
    "native_review_receipt": "5411f46eb4050b85fa53b5a285ae96933fbb764c8e65cdb35f68d002b49f3788",
    "native_review_freeze": "8d0ac5e7890b55d871c4133a1027d2ee97690bfcf2d80206cbb7784a3bde3845",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pinned(path, key):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == PINS[key], "Source pin: " + key)
    return raw


def freeze(path, key=None):
    raw = pinned(path, key) if key else path.read_bytes()
    manifest = json.loads(raw)
    for name, digest in manifest["files"].items():
        need(sha256((path.parent/name).read_bytes()).hexdigest() == digest, "Frozen bytes: " + name)
    return sha256(raw).hexdigest()


def act(columns, value):
    result = 0
    while value:
        low = value & -value
        result ^= columns[low.bit_length()-1]
        value ^= low
    return result


def compose(left, right):
    return tuple(act(left, v) for v in right)


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            top = value.bit_length()-1
            if top in pivots:
                value ^= pivots[top]
            else:
                pivots[top] = value
                break
    return len(pivots)


def add_to(target, source, coefficient=F(1)):
    for key, value in source.items():
        target[key] = target.get(key, F(0)) + coefficient*value
        if not target[key]:
            del target[key]


def scalar_price(event):
    value = F(*event[-2:])
    n, d = abs(value.numerator), value.denominator
    need(n > 0 and d & (d-1) == 0, "Dyadic event")
    if event[0] == "scale":
        need(n & (n-1) == 0, "Dyadic unit scale")
        return 2*(abs(n.bit_length()-d.bit_length())+(value < 0))
    return 2*(1+n.bit_length()+n.bit_count()+d.bit_length())


def local_stock(word, response, direction):
    current = list(word["start"])
    need(len(current) == 632 and current[224:] == word["final"][224:], "Unused helper frames")
    widths, profile, price = [0]*224, Counter(), 0
    frames = word["frames"]
    for event in word["events"]:
        if event[0] == "native":
            _, target, old, new, width, key = event
            need(0 <= target < 224 and current[target] == old, "Native data role")
            need(rank(frames[old]+frames[new]) == len(frames[new]), "Nested frames")
            need(width == len(frames[new])-len(frames[old]) == word["native_recipes"][key]["rank"],
                 "Native rank")
            current[target] = new
            widths[target] += width
            profile[width] += 1
        else:
            need(event[0] == "scalar", "No hidden event type")
            op, frame = event[1:]
            target = op[1]
            need(0 <= target < 224 and current[target] == frame, "Scalar data role")
            if op[0] == "add":
                need(0 <= op[2] < 224 and op[2] != target and current[op[2]] == frame,
                     "Distinct equal-frame data operands")
            else:
                need(op[0] == "scale", "Scalar grammar")
            price += scalar_price(op)
    need(current == word["final"] and widths == [8]*224, "Complete data progress and untouched helper frames")
    # Propagate output columns backwards. This does not use the producer's row replay.
    columns = [{p:F(1)} for p in range(224)]
    for event in reversed(word["events"]):
        if event[0] != "scalar":
            continue
        op = event[1]
        coefficient = F(*op[-2:])
        if op[0] == "scale":
            columns[op[1]] = {p:coefficient*v for p,v in columns[op[1]].items()}
        else:
            add_to(columns[op[2]], columns[op[1]], coefficient)
    expected = [{p:F(1)} for p in range(224)]
    for p, row in enumerate(response):
        for r, value in row.items():
            if direction == "forward":
                expected[r][112+p] = value
            else:
                expected[112+p][r] = -value
    need(columns == expected, "Independent reverse replay of all224 columns")
    need(profile == {1:160,2:48,5:48,7:112,8:64} and price == 3032, "Local profile and scalar price")
    need(len(word["endpoint_adapters"]) == 224 and
         {(r["role"],r["port"]) for r in word["endpoint_adapters"]} ==
         {(role,p) for role in ("source","target") for p in range(112)}, "Complete data endpoint inventory")
    return {"columns":224,"native_profile":dict(profile),"rank_mass":sum(widths),
            "scalar_primitives":price,"omitted_helper_ranks":dict(Counter(len(frames[f]) for f in current[224:]))}


def reduce_letters(word):
    out = []
    for letter in word:
        if out and out[-1] == -letter:
            out.pop()
        else:
            out.append(letter)
    return tuple(out)


def ring_product(a, b):
    result = defaultdict(F)
    for x, u in a.items():
        for y, v in b.items():
            result[reduce_letters(x+y)] += u*v
    return {w:v for w,v in result.items() if v}


def block_product(a, b):
    result = [[{} for _ in range(2)] for _ in range(2)]
    for i in range(2):
        for j in range(2):
            for k in range(2):
                add_to(result[i][j], ring_product(a[i][k],b[k][j]))
    return result


def diagonal(a, b):
    return [[a,{}],[{},b]]


def ordered_controller(program):
    one, minus = {():F(1)}, {():F(-1)}
    identity = diagonal(one,one)
    result = identity
    for kind, stage, *power in program:
        symbol = stage+1
        value = {(symbol if not power else symbol*power[0],):F(1)}
        if kind == "forward":
            event = [[one,{}],[value,one]]
        elif kind == "backward":
            event = [[one,{(-symbol,):F(-1)}],[{},one]]
        elif kind == "code_X":
            event = diagonal(value,one)
        else:
            need(kind == "code_Y", "Controller event")
            event = diagonal(one,value)
        result = block_product(event,result)
    need(result == [[{},minus],[{(3,2,1):F(1)},{}]], "Ordered controller endpoint")
    q, qi = {(4,):F(1)}, {(-4,):F(1)}
    old = [[{},{(4,4):F(1)}],[minus,{}]]
    physical = block_product(old,block_product(diagonal(one,qi),block_product(result,diagonal(qi,one))))
    need(physical == diagonal({(4,3,2,1,-4):F(1)},one), "Raw input and raw terminal endpoint")
    decoder = diagonal({(4,-1,-2,-3,-4):F(1)},one)
    need(block_product(decoder,physical) == identity, "Complete ordered endpoint")
    wrong = diagonal({(4,-3,-2,-1,-4):F(1)},one)
    need(block_product(wrong,physical) != identity, "Wrong chronological inverse order fails")
    missing_line = diagonal({(-1,-2,-3,-4):F(1)},one)
    need(block_product(missing_line,physical) != identity, "Missing final original-input line fails")
    return {"preterminal":["-y","E2 E1 E0 x"],"raw_first_bank":"Q E2 E1 E0 Q^-1",
            "decoder":"Q E0^-1 E1^-1 E2^-1 Q^-1","free_noncommuting_identity":True}


def gaussian_mul(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


ALPHA, BETA = (F(1,2),F(1,2)), (F(1,2),F(-1,2))


def line_kernel(vector, power):
    need(power in (-1,1), "Line sign")
    return {0:ALPHA if power == 1 else BETA, vector:BETA if power == 1 else ALPHA}


def kernel_product(a, b):
    result = {}
    for u, c in a.items():
        for v, d in b.items():
            value = gaussian_mul(c,d)
            old = result.get(u^v,(F(0),F(0)))
            result[u^v] = (old[0]+value[0],old[1]+value[1])
    return {v:c for v,c in result.items() if c != (0,0)}


def shifted(kernel, delta, sign=1):
    return {v^delta:(sign*c[0],sign*c[1]) for v,c in kernel.items()}


def native_kernel(record):
    g, gi = record["child_basis_columns"], record["child_basis_inverse_columns"]
    need(compose(g,gi) == compose(gi,g) == tuple(UNIT), "Both native basis inverse orders")
    need(all((u&v).bit_count()%2 == (i==j) for i,u in enumerate(g) for j,v in enumerate(g)),
         "Native basis is orthogonal")
    columns = list(UNIT)
    for v in record["basis_transvections_in_time_order"]:
        need(v and v.bit_count()%2 == 0, "Orthogonal transvection")
        columns = [x^(v if (x&v).bit_count()%2 else 0) for x in columns]
    need(columns == g, "Literal basis transvection program")
    result = {0:(F(1),F(0))}
    for j in range(record["rank"]):
        result = kernel_product(result,line_kernel(g[j],1))
    return shifted(result,record["output_translation"],record["sign"])


def phase_value(packed, eta):
    odd, even, cross = packed
    result = (odd&eta).bit_count()+2*(even&eta).bit_count()
    for j in range(25):
        if eta >> j & 1:
            result += 2*((cross >> (j*(j-1)//2)) & eta & ((1<<j)-1)).bit_count()
    return result%4


def main():
    freeze(HERE/"ACCESS-FREEZE.json","access")
    spec = importlib.util.spec_from_file_location("independent_access",HERE/"check_access.py")
    access = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(access)
    triple_dir = LANES/"bridge-access-20261017/matched-stage-access-20261018"
    freeze(triple_dir/"TRIPLE25-FREEZE.json","triple")
    admission = LANES/"history-encoding/one-pair-admission-20261018"
    admission_freeze = freeze(admission/"FREEZE.json","admission")
    pinned(admission/"ONE-PAIR-ADMISSION.md","admission_proof")
    sources = json.loads(pinned(admission/"SOURCE-PINS.json","admission_sources"))
    loaded = {}
    for name, item in sources.items():
        raw = (ROOT/item["path"]).read_bytes()
        if item["kind"] == "gzip":
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == item["sha256"], "Admission premise: "+name)
        if item["kind"] != "text":
            loaded[name] = json.loads(raw)
    native_review = LANES/"independent-review-20261017/matched-native-review-20261018"
    freeze(native_review/"FREEZE.json","native_review_freeze")
    pinned(native_review/"REVIEW.md","native_review")
    pinned(native_review/"CHECKS.json","native_review_receipt")
    native = loaded["local_payload"]
    response = access.matrix(native["response"])
    for name in ("scalar_word","inverse_scalar_word"):
        events = []
        for op,p,r,c in loaded["gauge"][name]:
            value = F(c)
            events.append([op,p,r,value.numerator,value.denominator] if op=="add" else
                          [op,p,value.numerator,value.denominator])
        result, price, peak, _ = access.scalar_replay(events)
        need(result == response and price == 2668 and peak == 4,
             "The old admission scalar word and its complete inverse")
    stock = {provider:{direction:local_stock(word,response,direction) for direction,word in words.items()}
             for provider,words in native["providers"].items()}
    endpoint = ordered_controller(loaded["current_controller"]["program"])
    group = 1
    for j in range(1,13):
        group *= ((1 << (2*j))-1)*(1 << (2*j-1))
    producer_receipt = json.loads((admission/"CHECKS.json").read_bytes())
    need(group == int(producer_receipt["cover_order"]) and group.bit_length() == 300 and
         (224*group).bit_length() == 308, "Independent symplectic-basis cover count")
    dim = loaded["dimension_views"]
    rho = {(v["stage"],v["port"]):tuple(v["route_columns"]) for v in dim["entries"]}
    q = {v["port"]:v["q"] for v in dim["entries"] if v["stage"] == 0}
    terminal_chart_checks = 0
    for record in producer_receipt["terminal_line_charts"]:
        p, g = record["port"], record["chart_columns"]
        need(g[0] == q[p] and rank(g) == 25, "Safe line basis on the full payload")
        need(shifted(line_kernel(q[p],1),q[p]) == line_kernel(q[p],-1), "Safe inverse line has exact phase")
        terminal_chart_checks += 1
    triple_raw = gzip.decompress((triple_dir/"TRIPLE25-PROGRAMS.json.gz").read_bytes())
    triple = json.loads(triple_raw)
    need(triple["preferred_response"] == native["response"], "Triple uses the actual native response")
    dense = {p for p,row in enumerate(response) if len(row) == 4}
    small = set(range(112))-dense
    need(len(dense)==48 and len(small)==64 and
         all(set(response[p]) <= dense for p in dense) and
         all(set(response[p]) <= small for p in small), "Two invariant port sets")
    phase_arguments = [0]+UNIT+[UNIT[i]^UNIT[j] for i in range(25) for j in range(i)]
    reports, full_paths = {}, {}
    for direction, stages in (("T",(2,1,0)),("T_inverse",(0,1,2))):
        inventory = {(r["target"],tuple(r["middle"]),r["source"]):r for r in triple["path_records"][direction]}
        need(len(inventory) == len(triple["path_records"][direction]) == 3136, "Complete distinct path records")
        seen = set()
        phase_checks = 0
        for p,row in enumerate(response):
            for j,c1 in row.items():
                first = compose(rho[stages[0],p],rho[stages[0],j])
                for k,c2 in response[j].items():
                    second = compose(rho[stages[1],j],rho[stages[1],k])
                    for r,c3 in response[k].items():
                        third = compose(rho[stages[2],k],rho[stages[2],r])
                        route = compose(compose(first,second),third)
                        record = inventory[p,(j,k),r]
                        need(tuple(record["route_columns"]) == route and F(record["coefficient"]) == c1*c2*c3,
                             "Ordered stage operator product")
                        need((p,r,route) not in seen, "Distinct independent cover input for every path")
                        seen.add((p,r,route))
                        a,b = q[p],act(route,q[r])
                        need(record["lines"] == [a,b] and a != b and (a&b).bit_count()%2 == 0,
                             "Actual distinct orthogonal line directions")
                        delta = record["FULL_translation"]
                        for eta in phase_arguments:
                            desired = (eta.bit_count()-sum((eta&v).bit_count()%2 for v in route))%4
                            need(desired == 2*((eta&delta).bit_count()%2), "FULL conjugation including even phase")
                            raw_phase = desired+(a&eta).bit_count()%2-(b&eta).bit_count()%2
                            need(phase_value(record["phase"],eta) == raw_phase%4, "Complete serialized path phase")
                            phase_checks += 1
        need(len(seen) == 3136, "No omitted path")
        full_paths[direction] = {(p,r,route):inventory[p,m,r]["coefficient"]
                                 for p,m,r in inventory for route in [tuple(inventory[p,m,r]["route_columns"])]}
        reports[direction] = {"paths":len(seen),"phase_coefficients":phase_checks,
                              "dense_paths":sum(p in dense for p,_,_ in seen),"small_paths":sum(p in small for p,_,_ in seen)}
    need(full_paths["T"] != full_paths["T_inverse"], "The actual triple is not replaced by its reverse")
    mixed = triple["mixed_native_decoder"]
    inverse_by_target = {r["target"]:r for r in triple["path_records"]["T_inverse"] if r["target"] in small}
    branch_checks = 0
    small_sources = set()
    for record in mixed["small64_children"]:
        path = inverse_by_target[record["target"]]
        need(record["source"] == path["source"] and record["rank"] == 2 and record["sign"] == -1 and
             record["cover_route_columns"] == path["route_columns"], "Small native field and owner route")
        a,b = path["lines"]
        expected = shifted(kernel_product(line_kernel(a,1),line_kernel(b,-1)),path["FULL_translation"],-1)
        actual = native_kernel(record)
        need(actual == expected and len(actual)==4, "All four exact Gaussian kernel branches")
        need(shifted(expected,0,-1) != actual, "Dropping the small-path sign fails")
        small_sources.add(record["source"])
        branch_checks += len(actual)
    need(len(mixed["small64_children"]) == 64 and small_sources == small, "Complete small-port permutation")
    dense_records = mixed["dense48_line_children"]
    need(len(dense_records)==96, "Complete two-pass dense line inventory")
    for i,record in enumerate(dense_records):
        power = -1 if i < 48 else 1
        p = record["target"]
        need(p in dense and p == record["source"] and record["rank"] == 1 and
             record["cover_route_columns"] == UNIT, "Dense line has no owner transfer")
        need(native_kernel(record) == line_kernel(q[p],power), "Both Gaussian coefficients of a dense line")
        branch_checks += 2
    need({r["target"] for r in dense_records[:48]} == {r["target"] for r in dense_records[48:]} == dense,
         "Every dense field in both line passes")
    events = []
    for op,p,r,c in mixed["dense48_scalar_inverse_events"]:
        value = F(c)
        events.append([op,p,r,value.numerator,value.denominator] if op=="add" else
                      [op,p,value.numerator,value.denominator])
    target = [response[p] if p in dense else {p:F(1)} for p in range(112)]
    rows, price, peak, census = access.scalar_replay(events)
    need(rows == target and access.reverse_columns(events) == target and price==1564 and peak==4,
         "Complete restricted scalar inverse and its price")
    need(mixed["dense48_scalar_code_stages_in_time_order"] == [2,1,0], "Dense inverse stage order")
    safe_profile = {1:704,2:144,5:144,7:336,8:192}
    mixed_profile = {1:576,2:208,5:144,7:336,8:192}
    need(sum(r*n for r,n in safe_profile.items()) == sum(r*n for r,n in mixed_profile.items()) == 5600,
         "Both complete rank masses")
    need(sum(safe_profile.values())==1520 and sum(mixed_profile.values())==1456 and max(mixed_profile)<25,
         "Complete child counts and strict positive-moment comparison")
    need(mixed["map_inventory"] == {"dense48_code_views":288,"dense48_child_wrappers":192,"small64_child_wrappers":128},
         "Complete terminal map call inventory")
    need(mixed["dense48_code_real_scalar_primitives"] == 3*price and
         mixed["small64_sign_real_scalar_primitives"] == 128, "Complete terminal scalar invoice")
    need(sha256(Path(__file__).read_bytes()).hexdigest() == SELF_PIN, "Checker stayed fixed")
    receipt = {
        "status":"PASS_INDEPENDENT_TRIPLE_TERMINAL_AND_ONE_PAIR_HOSTING",
        "checker_sha256":SELF_PIN,"source_pins":PINS,"admission_freeze_sha256":admission_freeze,
        "triple_payload_decompressed_sha256":sha256(triple_raw).hexdigest(),
        "local_words":stock,"ordered_controller":endpoint,
        "cover_order":str(group),"productive_roles":str(224*group),
        "safe_terminal_charts":terminal_chart_checks,"triple_paths":reports,
        "exact_native_kernel_branches":branch_checks,"mixed_terminal_profile":{"1":96,"2":64},
        "mixed_terminal_scalar_primitives":3*price+128,"mixed_terminal_map_calls":608,
        "old_admission_local_and_eight_code_subtotal":3*3032+8*2668,
        "improved_safe_local_and_eight_code_subtotal":3*3032+8*2396,
        "improved_mixed_local_and_code_subtotal":3*3032+5*2396+3*price+128,
        "dense_inverse_scalar_primitives_per_stage":price,
        "safe_full_native_profile":safe_profile,"mixed_full_native_profile":mixed_profile,
        "full_rank_mass_per_cover":5600,"productive_dimension_product":224*25,
        "strict_positive_native_moment_failure":True,
        "phase_dependency":"The previously independent native review supplies full local phase verification; this review rechecks the terminal kernels directly.",
        "hosting_scope":"Data stock, exact owner bijections, and row/LIFO layout under the admitted all-size child contract. No all-size grouping, finite precision, or complete finite supplier invoice is established here.",
    }
    (HERE/"TERMINAL-HOSTING-REVIEW.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
