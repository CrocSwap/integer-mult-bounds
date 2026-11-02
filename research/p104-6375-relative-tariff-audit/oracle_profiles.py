"""Independent literal frame-rank profile and fixed-caller invoice extractor.

The author constructor, checkers, result, peer verifier and earlier audit code
are not imported. Native rank tariffs and supplier/interface correctness remain
premises. This file makes no power-threshold or new-kappa calculation.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
PUBLIC, OWNED, PORTS = 770, 29, 104
PINS = {
    "sources/NEW-WORD.json.gz": ("9e31463a785c18a70f6ae6ef3d04a6560dbb965517109390fe820f9fac3371b3", "b1cfd03abe9128cf5a3908fbd82652e5e8a2e292"),
    "sources/OLD-WORD.json.gz": ("e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491", "0af79e58172f85c302c35b193205c0b185b09393"),
    "sources/CONTROLLER.json": ("6fd67eaabe659956d6694471d3fd7d2824c0a4a79cf3b8f22922f7189b11b91f", "1f2e375b24aba5fb25580dfea7fab7a2049f3eb8"),
    "sources/controller-source.py": ("8067ade84815b54d539cbaef9885db9fa4d7a23fdde2e683451d317038a8477c", "3b4bf82eba05d57ef4bb1fd934e8ca65780425c1"),
    "sources/LIFTS.json": ("38960b70a074888a2aeaf3b543629a7ae747c0c5d4f5c853371a6e7c483766c5", "2ee8cb78fd149f9aca8dd953c650b92495a56266"),
    "sources/constructor-source.py": ("fe7dc1d9aa55da393465388ee90faaa687b1e5be48dfa816a421069fa3d2de08", "c099995bef0e224cbb0ec61c06ed3d0b4d478b33"),
    "sources/upstream-PROOF.md": ("769e0f87e6b85c557b48135d2d898bb485cf77ce9925540e0a3740e6283f41af", "bd20fcaf2078691d914d6afbc5cb06a75f47770d"),
    "sources/NOTICE": ("91f24d68004688bc0a56303a48edcb5ddabd66bfc2326950603bf98dec245bbe", "638a187d1417bda8976e945a2aeaed116a090e37"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, lower, upper, label):
    require(type(value) is int and lower <= value < upper, label)
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def authenticate():
    manifest = json.loads((HERE / "SOURCE-PINS.json").read_bytes())
    require(manifest["schema"] == "source-pins/v1"
            and manifest["upstream_head"] == "247b5c319b9f58fe9ee61dbf80697f8a9a429831"
            and manifest["retained_baseline_head"] == "b556600ffe14be72406b03a47c661f3c7f1aff06",
            "Exact source/baseline provenance")
    rows = manifest["files"]
    require(type(rows) is list and len(rows) == len(PINS)
            and {r["file"]: (r["sha256"], r["git_blob"]) for r in rows} == PINS,
            "Eight independently pinned source files")
    data = {}
    for name, (digest, blob) in PINS.items():
        raw = (HERE / name).read_bytes()
        require(sha256(raw).hexdigest() == digest, "exact source sha256: " + name)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "Exact source Git blob: " + name)
        if name.endswith(".json.gz"):
            data[Path(name).name] = json.loads(gzip.decompress(raw))
        elif name.endswith(".json"):
            data[Path(name).name] = json.loads(raw)
    return data


def rank(vectors, independent=False):
    pivots = {}
    require(type(vectors) is list, "Binary vector list")
    for vector in vectors:
        integer(vector, 1, 512, "Nonzero GF(2)^9 vector")
        value = vector
        while value:
            bit = (value & -value).bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
        require(value != 0 or not independent, "Independent literal frame basis")
    return len(pivots)


def q(value):
    require(type(value) is str, "Rational scalar string")
    result = Fraction(value)
    require(result and str(result) == value and result.denominator & (result.denominator - 1) == 0,
            "Canonical nonzero dyadic scalar")
    return result


def encoded(counter):
    return {str(r): n for r, n in sorted(counter.items()) if n}


def decoded(value):
    return Counter({int(r): n for r, n in value.items()})


def mass(counter):
    return sum(r * n for r, n in counter.items())


def delta(after, before):
    result = Counter(after)
    result.subtract(before)
    return Counter({r: n for r, n in result.items() if n})


def first_difference(actual, expected):
    for r in sorted(actual.keys() | expected.keys()):
        if actual.get(r, 0) != expected.get(r, 0):
            return {"rank": r, "actual_count": actual.get(r, 0), "expected_count": expected.get(r, 0)}
    return None


def same_profile(actual, expected, label):
    require(first_difference(actual, expected) is None, label + ": " + canonical(first_difference(actual, expected)))


def local(word):
    require(type(word["public"]) is int and word["public"] == PUBLIC
            and type(word["owned_fields"]) is int and word["owned_fields"] == OWNED,
            "Fixed arbitrary public/owned inventories")
    frames = word["frames"]
    require(type(frames) is list, "Frame inventory")
    dimensions = [rank(frame, independent=True) for frame in frames]
    for key in ("initial", "final"):
        require(type(word[key]) is list and len(word[key]) == PUBLIC, "Complete public boundary")
        for frame in word[key]:
            integer(frame, 0, len(frames), "Boundary frame")
    live = word["live"]
    require(type(live) is list and len(live) == PORTS, "104 main pairs")
    for r in live:
        integer(r, 0, PUBLIC - 112, "Main source role")
    mains = set(live) | {r + 112 for r in live}
    require(len(mains) == 208 and type(word["ports"]) is list and len(word["ports"]) == PORTS,
            "Disjoint main role pairs and104 ports")
    active = dict(enumerate(word["initial"]))
    open_owned, lifetimes, peak = set(), 0, 0
    paid, counts, first = Counter(), Counter(), {}
    require(type(word["program"]) is list and len(word["program"]) < 26000, "Bounded literal word")
    for index, e in enumerate(word["program"]):
        require(type(e) is list and e, "Literal instruction")
        op = e[0]
        require(op in ("MOVE", "INIT", "CLEAR", "ADD", "COPY", "SCALE"), "Known local opcode")
        require(len(e) == {"MOVE": 5, "INIT": 3, "CLEAR": 3, "ADD": 5, "COPY": 5, "SCALE": 4}[op], "Local opcode arity")
        r = integer(e[1], 0, PUBLIC + OWNED, "Literal role")
        counts[op] += 1
        if op == "MOVE":
            a, b = integer(e[2], 0, len(frames), "MOVE source"), integer(e[3], 0, len(frames), "MOVE target")
            require(r in active and active[r] == a and type(e[4]) is bool and e[4] == (r in open_owned),
                    "Chronological MOVE source and owned flag")
            da, db = dimensions[a], dimensions[b]
            require(rank(frames[a] + frames[b]) == max(da, db), "Nested transport subspaces")
            require(db < da if e[4] else da < db, "Strict owned descent or public ascent")
            paid[abs(db - da)] += 1
            if a == 3:
                require(r not in first, "One first departure from ZERO")
                first[r] = {"index": index, "destination": b}
            active[r] = b
        elif op == "INIT":
            frame = integer(e[2], 0, len(frames), "INIT frame")
            require(r >= PUBLIC and r not in active, "INIT inactive owned label")
            active[r] = frame
            open_owned.add(r)
            lifetimes += 1
            peak = max(peak, len(open_owned))
        elif op == "CLEAR":
            frame = integer(e[2], 0, len(frames), "CLEAR frame")
            require(r in open_owned and active[r] == frame, "CLEAR active lifetime and frame")
            open_owned.remove(r)
            del active[r]
        else:
            frame = integer(e[-1], 0, len(frames), "Scalar common frame")
            require(r in active and active[r] == frame, "Active scalar destination")
            q(e[-2])
            if op != "SCALE":
                s = integer(e[2], 0, PUBLIC + OWNED, "Scalar source role")
                require(s != r and s in active and active[s] == frame, "Active distinct scalar source in common frame")
                if op == "COPY":
                    require(r in open_owned, "COPY owned destination; zero-value premise remains separate")
    require(not open_owned and active == dict(enumerate(word["final"])), "Complete public exits and owned retirement")
    helpers = Counter()
    for r in range(PUBLIC):
        if r in mains:
            continue
        a, b = word["initial"][r], word["final"][r]
        da, db = dimensions[a], dimensions[b]
        require(da < db and rank(frames[a] + frames[b]) == db, "Strictly productive nested helper boundary")
        helpers[db - da] += 1
    require(sum(helpers.values()) == 562, "Exactly562 independent public helper targets")
    increments = {dimensions[word["final"][r]] - dimensions[word["initial"][r]] for r in mains}
    require(increments == {8}, "Declared rank-eight main stage interface")
    return {"paid": encoded(paid), "targets": encoded(helpers), "events": len(word["program"]),
            "opcode_counts": dict(sorted(counts.items())), "owned_lifetimes": lifetimes, "peak_owned": peak,
            "paid_jobs": sum(paid.values()), "helper_fields": 562,
            "paid_rank_mass": mass(paid), "productive_rank_mass": mass(helpers)}, dimensions, first


def footprint(old, new, lifts, dimensions, first):
    require(set(old) == set(new), "Same word metadata keys")
    for key in old:
        if key not in ("program", "initial"):
            require(canonical(old[key]) == canonical(new[key]), "Unchanged interface/header field: " + key)
    expected_initial, removed, added, clusters = {}, Counter(), Counter(), []
    require(type(lifts["rounds"]) is list and len(lifts["rounds"]) == 2, "Two declared lift rounds")
    all_anchors, all_carriers = set(), set()
    for round_number, spec in enumerate(lifts["rounds"]):
        for cluster in spec["clusters"]:
            F = integer(cluster["F"], 0, len(dimensions), "Entrance frame")
            anchors = sorted(int(r) for r in cluster["anchors"])
            require(len(anchors) == 2 and len(cluster["carriers"]) == 1, "Two lifted helpers share one carrier")
            carrier = integer(cluster["carriers"][0], 0, PUBLIC, "Public carrier")
            require(carrier not in all_carriers and not (set(anchors) & all_anchors), "Distinct three clusters")
            all_carriers.add(carrier)
            all_anchors.update(anchors)
            require(dimensions[F] == 1, "Rank-one entrance")
            for anchor in anchors:
                integer(anchor, 0, PUBLIC, "Lifted public helper")
                require(old["initial"][anchor] == 3 and old["final"][anchor] == 127, "Old full helper boundary")
                expected_initial[str(anchor)] = [3, F]
                G = first[anchor]["destination"]
                removed[("MOVE", anchor, 3, G, False)] += 1
                added[("MOVE", anchor, F, G, False)] += 1
            Gc = first[carrier]["destination"]
            removed[("MOVE", carrier, 3, Gc, False)] += 1
            added[("MOVE", carrier, 3, F, False)] += 1
            added[("MOVE", carrier, F, Gc, False)] += 1
            clusters.append({"round": round_number + 1, "carrier": carrier, "entrance": F,
                             "anchors": anchors, "old_carrier_destination": Gc,
                             "old_carrier_rank": dimensions[Gc],
                             "anchor_destination_ranks": [dimensions[first[r]["destination"]] for r in anchors]})
    actual_initial = {str(r): [old["initial"][r], new["initial"][r]] for r in range(PUBLIC)
                      if old["initial"][r] != new["initial"][r]}
    require(actual_initial == expected_initial and all_anchors == {520, 655, 544, 671, 472, 624}
            and all_carriers == {171, 208, 130}, "Exactly six changed initial contracts and three carriers")
    old_moves = Counter(tuple(e) for e in old["program"] if e[0] == "MOVE")
    new_moves = Counter(tuple(e) for e in new["program"] if e[0] == "MOVE")
    require(old_moves - new_moves == removed and new_moves - old_moves == added,
            "Complete MOVE multiset delta equals all six lifts plus three two-leg detours")
    return {"changed_initial_frames": actual_initial, "clusters": clusters,
            "removed_MOVE_records": [[list(e), n] for e, n in sorted(removed.items())],
            "added_MOVE_records": [[list(e), n] for e, n in sorted(added.items())]}


def complete(local_profile, caller):
    require(type(caller["roles"]) is int and caller["roles"] == 34
            and type(caller["stages"]) is int and caller["stages"] == 19, "Fixed34-field19-stage caller")
    paid, targets, opcounts = Counter(), Counter(), Counter()
    stages, idle_sizes = [], []
    queries = []
    for index, e in enumerate(caller["events"]):
        op = e[0]
        require(op in ("ADD", "SCALE", "SWAP", "LOCAL", "QUERY", "Q_POWER", "IDLE"), "Known caller opcode")
        opcounts[op] += 1
        if op == "LOCAL":
            integer(e[1], 1, 20, "LOCAL stage")
            stages.append(e[1])
            paid.update(decoded(local_profile["paid"]))
            targets.update(decoded(local_profile["targets"]))
        elif op == "QUERY":
            require(type(e[3]) is int and e[3] in (-1, 1), "Unit thin-query exponent")
            paid[1] += PORTS
            queries.append(index)
        elif op == "IDLE":
            require(type(e[3]) is list and e[3] and len(e[3]) == len(set(e[3])), "Distinct idle stages")
            for stage in e[3]:
                integer(stage, 1, 20, "Idle stage")
            paid[8 * len(e[3])] += 2 * PORTS
            idle_sizes.append({"index": index, "size": len(e[3])})
    require(sorted(stages) == list(range(1, 20)) and len(queries) == len(idle_sizes) == 16,
            "Nineteen complete LOCAL bills and sixteen queries/idles")
    require(type(caller["diagonal"]) is list and len(caller["diagonal"]) == 34, "Declared34 main targets")
    for term in caller["diagonal"]:
        require(type(term) is list and len(term) == 21 and all(type(x) is int for x in term)
                and term[0] in (-1, 1) and term[1] == 0 and all(x in (0, 1) for x in term[2:]),
                "Declared signed central power and19 distinct stage bits")
        targets[1 + 8 * sum(term[2:])] += PORTS
    node_sizes = []
    def leaves(tree):
        if type(tree) is int:
            require(tree == 1, "Native leaf")
            return 1
        require(type(tree) is list and len(tree) == 2, "Binary caller subtree")
        size = leaves(tree[0]) + leaves(tree[1])
        node_sizes.append(size)
        return size
    require(type(caller["tree"]) is list and len(caller["tree"]) == 3, "Ternary root")
    total_leaves = sum(leaves(tree) for tree in caller["tree"])
    require(total_leaves == 19 and len(node_sizes) == 16, "Independent topology census")
    formula_paid = Counter({r: total_leaves * n for r, n in decoded(local_profile["paid"]).items()})
    formula_targets = Counter({r: total_leaves * n for r, n in decoded(local_profile["targets"]).items()})
    formula_paid[1] += PORTS * len(node_sizes)
    formula_targets[1 + 8 * total_leaves] += 2 * PORTS
    for size in node_sizes:
        formula_paid[8 * size] += 2 * PORTS
        formula_targets[1 + 8 * size] += 2 * PORTS
    same_profile(paid, formula_paid, "Literal versus topology paid invoice")
    same_profile(targets, formula_targets, "Declared diagonal versus topology productive invoice")
    return {"paid": encoded(paid), "targets": encoded(targets), "paid_jobs": sum(paid.values()),
            "productive_fields": sum(targets.values()), "paid_rank_mass": mass(paid),
            "productive_rank_mass": mass(targets), "rank_mass_surplus": mass(targets) - mass(paid)}, {
                "opcode_counts": dict(sorted(opcounts.items())), "topology_node_sizes": dict(sorted(Counter(node_sizes).items())),
                "queries": queries, "idles": idle_sizes}


def controls(new_word, new_local, whole, caller_info):
    paid, targets = decoded(whole["paid"]), decoded(whole["targets"])
    bad = []
    index, event = next((i, e) for i, e in enumerate(new_word["program"])
                        if e[:4] == ["MOVE", 171, 3, 106])
    wrong = Counter(paid)
    wrong[1] -= 19
    bad.append(("unpaid_carrier_first_leg_in_nineteen_calls", paid, wrong, {"event_index": index, "event": event, "copies": 19}))
    wrong = Counter(targets)
    wrong[8] -= 19
    wrong[9] += 19
    require(sum(wrong.values()) == sum(targets.values()), "Target substitution control preserves independent field count")
    bad.append(("old_rank9_target_retained_instead_of_new_rank8", targets, wrong,
                {"helper": 520, "copies": 19, "productive_fields": sum(wrong.values())}))
    wrong = Counter(paid)
    wrong[1] -= PORTS
    bad.append(("one_thin_query_unpaid", paid, wrong, {"caller_event_index": caller_info["queries"][0], "jobs": PORTS}))
    idle = caller_info["idles"][0]
    wrong = Counter(paid)
    wrong[8 * idle["size"]] -= PORTS
    bad.append(("one_paired_idle_member_unpaid", paid, wrong, {"caller_event_index": idle["index"], "jobs": PORTS}))
    wrong = Counter(paid)
    wrong.subtract(decoded(new_local["paid"]))
    bad.append(("one_full_LOCAL_bill_missing", paid, wrong, {"omitted_stage": 1}))
    result = []
    for label, expected, corrupted, detail in bad:
        witness = first_difference(corrupted, expected)
        require(witness is not None, "Counterfactual invoice has a concrete different coefficient")
        try:
            same_profile(corrupted, expected, label)
        except ValueError:
            result.append({"control": label, "kind": "counterfactual_invoice_counts",
                           "profile_mismatch": witness, "detail": detail})
        else:
            raise ValueError("Counterfactual invoice was accepted")
    return result


def run():
    data = authenticate()
    old_word, new_word = data["OLD-WORD.json.gz"], data["NEW-WORD.json.gz"]
    old, dimensions, first = local(old_word)
    new, new_dimensions, _ = local(new_word)
    require(dimensions == new_dimensions, "Identical frame dimensions")
    binding = footprint(old_word, new_word, data["LIFTS.json"], dimensions, first)
    old_whole, caller = complete(old, data["CONTROLLER.json"])
    new_whole, new_caller = complete(new, data["CONTROLLER.json"])
    require(canonical(caller) == canonical(new_caller), "Unchanged caller census")
    dp = delta(decoded(new["paid"]), decoded(old["paid"]))
    dt = delta(decoded(new["targets"]), decoded(old["targets"]))
    same_profile(dp, Counter({1: 6, 3: -3, 4: 3, 5: -3}), "Exact local paid change")
    same_profile(dt, Counter({8: 6, 9: -6}), "Exact six-target initial-boundary debit")
    same_profile(delta(decoded(new_whole["paid"]), decoded(old_whole["paid"])), Counter({r: 19 * n for r, n in dp.items()}), "All nineteen paid copies")
    same_profile(delta(decoded(new_whole["targets"]), decoded(old_whole["targets"])), Counter({r: 19 * n for r, n in dt.items()}), "All nineteen productive copies")
    signed = Counter(dt)
    signed.subtract(dp)
    return {"schema_version": 1, "status": "PASS_CONDITIONAL_PROFILES",
            "old_local": old, "new_local": new, "source_binding": binding, "caller": caller,
            "old_complete": old_whole, "new_complete": new_whole,
            "local_paid_delta": encoded(dp), "local_target_delta": encoded(dt),
            "local_signed_gain_coefficients": encoded(signed),
            "rank_mass_changes": {"paid": mass(dp), "productive": mass(dt), "signed": mass(signed)},
            "counterfactual_invoice_controls": controls(new_word, new, new_whole, caller),
            "limits": ["Paid frame-rank and productive tariffs are retained native/interface premises, not phase or realization proofs.",
                       "Scalar common frames and temporal ownership are checked; scalar values, restoration, COPY zeros and physical erasure are not admitted.",
                       "Main target billing assumes the frozen rank-eight LOCAL interface and declared caller diagonal.",
                       "MOVE multiset cancellation is billing evidence, not a claim that retimed events have identical chronology.",
                       "Controls corrupt invoice counts only; no valid cheaper modified source program is claimed.",
                       "This round does not compute a power threshold, raw kappa crossing, uniform compiler or supplier admission."]}


if __name__ == "__main__":
    require(sys.argv[1:] in ([], ["--emit"]), "Usage: oracle_profiles.py [--emit]")
    result = run()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    else:
        retained = json.loads((HERE / "ORACLE-PROFILES.json").read_bytes())
        require(canonical(result) == canonical(retained), "Exact typed retained ORACLE-PROFILES.json receipt")
        print("PASS independent conditional profiles and retained receipt")
