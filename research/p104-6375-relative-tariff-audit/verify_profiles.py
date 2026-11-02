#!/usr/bin/env python3
"""Source-bound formal rank-profile extraction for the frozen PR6375 words.

All source files are authenticated data; no author or peer module is imported.
The paid-rank premise is the retained strict-nesting frame tariff, as used by
PR6359. This is bookkeeping, not native phase, endpoint or supplier admission.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PUBLIC, OWNED, PORTS = 770, 29, 104
PINNED = {
    "sources/NEW-WORD.json.gz": [
        "9e31463a785c18a70f6ae6ef3d04a6560dbb965517109390fe820f9fac3371b3",
        "b1cfd03abe9128cf5a3908fbd82652e5e8a2e292"
    ],
    "sources/OLD-WORD.json.gz": [
        "e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491",
        "0af79e58172f85c302c35b193205c0b185b09393"
    ],
    "sources/CONTROLLER.json": [
        "6fd67eaabe659956d6694471d3fd7d2824c0a4a79cf3b8f22922f7189b11b91f",
        "1f2e375b24aba5fb25580dfea7fab7a2049f3eb8"
    ],
    "sources/controller-source.py": [
        "8067ade84815b54d539cbaef9885db9fa4d7a23fdde2e683451d317038a8477c",
        "3b4bf82eba05d57ef4bb1fd934e8ca65780425c1"
    ],
    "sources/LIFTS.json": [
        "38960b70a074888a2aeaf3b543629a7ae747c0c5d4f5c853371a6e7c483766c5",
        "2ee8cb78fd149f9aca8dd953c650b92495a56266"
    ],
    "sources/constructor-source.py": [
        "fe7dc1d9aa55da393465388ee90faaa687b1e5be48dfa816a421069fa3d2de08",
        "c099995bef0e224cbb0ec61c06ed3d0b4d478b33"
    ],
    "sources/upstream-PROOF.md": [
        "769e0f87e6b85c557b48135d2d898bb485cf77ce9925540e0a3740e6283f41af",
        "bd20fcaf2078691d914d6afbc5cb06a75f47770d"
    ],
    "sources/NOTICE": [
        "91f24d68004688bc0a56303a48edcb5ddabd66bfc2326950603bf98dec245bbe",
        "638a187d1417bda8976e945a2aeaed116a090e37"
    ]
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def authenticate():
    manifest = json.loads((HERE / "SOURCE-PINS.json").read_bytes())
    require(manifest["schema"] == "source-pins/v1" and len(manifest["files"]) == 8 and
            {r["file"]: [r["sha256"], r["git_blob"]] for r in manifest["files"]} == PINNED,
            "eight independently fixed source pins")
    data = {}
    for name, (digest, blob) in PINNED.items():
        raw = (HERE / name).read_bytes()
        require(sha256(raw).hexdigest() == digest, "source SHA256: " + name)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "source Git blob: " + name)
        if name.endswith(".json.gz"):
            data[Path(name).name] = json.loads(gzip.decompress(raw))
        elif name.endswith(".json"):
            data[Path(name).name] = json.loads(raw)
    return data


def integer(value, lower, upper, label):
    require(type(value) is int and lower <= value < upper, label)


def rational(value):
    require(type(value) is str, "rational coefficient string")
    q = Fraction(value)
    require(q and str(q) == value and q.denominator & (q.denominator - 1) == 0,
            "canonical nonzero dyadic coefficient")
    return q


def frame_spaces(frames):
    result = []
    require(type(frames) is list and len(frames) == 1095, "fixed frame inventory")
    for basis in frames:
        require(type(basis) is list, "binary frame basis")
        space = {0}
        for vector in basis:
            integer(vector, 1, 512, "nonzero binary nine-axis vector")
            require(vector not in space, "independent frame basis")
            space |= {point ^ vector for point in tuple(space)}
        result.append(frozenset(space))
    return result


def dimension(space):
    return len(space).bit_length() - 1


def raw_local(word, spaces):
    paid = Counter()
    for event in word["program"]:
        if event[0] == "MOVE":
            paid[abs(dimension(spaces[event[3]]) - dimension(spaces[event[2]]))] += 1
    main = set(word["live"]) | {r + 112 for r in word["live"]}
    helpers = Counter(dimension(spaces[word["final"][r]]) - dimension(spaces[word["initial"][r]])
                      for r in range(PUBLIC) if r not in main)
    require(min(paid) > 0 and min(helpers) > 0, "positive literal paid and productive ranks")
    return paid, helpers


def validate_word(word, spaces):
    require(type(word["public"]) is int and word["public"] == PUBLIC and
            type(word["owned_fields"]) is int and word["owned_fields"] == OWNED, "fixed role inventory")
    require(len(word["initial"]) == len(word["final"]) == PUBLIC and
            len(word["live"]) == len(set(word["live"])) == len(word["ports"]) == PORTS, "public/main interface")
    main = set(word["live"]) | {r + 112 for r in word["live"]}
    require(len(main) == 208, "disjoint104 main pairs")
    for value in word["initial"] + word["final"]:
        integer(value, 0, len(spaces), "public frame label")
    current = dict(enumerate(word["initial"]))
    counts = Counter()
    lifetimes, active, peak = 0, set(), 0
    for event in word["program"]:
        op, r = event[:2]
        integer(r, 0, PUBLIC + OWNED, "literal role")
        counts[op] += 1
        if op == "MOVE":
            require(len(event) == 5, "MOVE arity")
            a, b, private = event[2:]
            integer(a, 0, len(spaces), "MOVE source frame")
            integer(b, 0, len(spaces), "MOVE destination frame")
            require(current.get(r) == a and type(private) is bool and private == (r in active),
                    "MOVE source frame and active ownership")
            require(spaces[b] < spaces[a] if private else spaces[a] < spaces[b],
                    "strict nested MOVE descent/ascent")
            current[r] = b
        elif op == "INIT":
            require(len(event) == 3 and r >= PUBLIC and r not in current, "inactive owned INIT")
            integer(event[2], 0, len(spaces), "INIT frame")
            current[r] = event[2]
            active.add(r)
            lifetimes += 1
            peak = max(peak, len(active))
        elif op == "CLEAR":
            require(len(event) == 3 and r in active and current[r] == event[2], "active owned CLEAR frame")
            integer(event[2], 0, len(spaces), "CLEAR frame")
            active.remove(r)
            del current[r]
        else:
            require(op in ("ADD", "SCALE") and len(event) == (5 if op == "ADD" else 4),
                    "actual pinned words contain only ADD/SCALE scalar updates, no COPY")
            integer(event[-1], 0, len(spaces), "scalar frame")
            require(current.get(r) == event[-1], "active common-frame scalar destination")
            q = rational(event[-2])
            if op == "ADD":
                s = event[2]
                integer(s, 0, PUBLIC + OWNED, "scalar source role")
                require(s != r and s in current and current[s] == event[-1], "active distinct common-frame source")
            else:
                require(abs(q.numerator) & (abs(q.numerator) - 1) == 0, "dyadic-unit SCALE")
    require(not active and current == dict(enumerate(word["final"])), "all public exits and owned lifetimes")
    require(all(dimension(spaces[word["final"][r]]) - dimension(spaces[word["initial"][r]]) == 8
                for r in main), "retained main-stage rank increment8")
    return {"events": len(word["program"]), "opcode_counts": dict(sorted(counts.items())),
            "owned_fields": OWNED, "owned_lifetimes": lifetimes, "peak_owned": peak,
            "COPY_events": counts["COPY"]}


def complete_from_events(local, caller, strict=True):
    paid, helpers = local
    full_paid, full_targets = Counter(), Counter()
    native_stages, queries, idles = [], [], []
    for event in caller["events"]:
        op = event[0]
        if op == "LOCAL":
            native_stages.append(event[1])
            full_paid.update(paid)
            full_targets.update(helpers)
        elif op == "QUERY":
            require(type(event[3]) is int and event[3] in (-1, 1), "unit central query exponent")
            full_paid[1] += PORTS
            queries.append(event)
        elif op == "IDLE":
            labels = event[3]
            require(type(labels) is list and labels and len(labels) == len(set(labels)) and
                    all(type(s) is int and 1 <= s <= 19 for s in labels),
                    "distinct idle stage labels")
            full_paid[8 * len(labels)] += 2 * PORTS
            idles.append(event)
        else:
            require(op in ("ADD", "SCALE", "SWAP", "Q_POWER"), "declared ordinary caller event")
    for row in caller["diagonal"]:
        require(type(row) is list and len(row) == 21 and type(row[0]) is int and row[0] in (-1, 1)
                and row[1] == 0 and all(type(s) is int and s in (0, 1) for s in row[2:]),
                "literal main target monomial")
        full_targets[abs(row[0]) + 8 * sum(row[2:])] += PORTS
    if strict:
        require(type(caller["stages"]) is int and caller["stages"] == 19 and
                sorted(native_stages) == list(range(1, 20)) and len(queries) == len(idles) == 16 and
                caller["roles"] == len(caller["diagonal"]) == 34, "fixed caller occurrence census")
    return full_paid, full_targets


def complete_from_forest(local, caller):
    node_sizes = Counter()
    def leaves(tree):
        if type(tree) is int:
            require(tree == 1, "unit native leaf")
            return 1
        require(type(tree) is list and len(tree) == 2, "binary caller subtree")
        count = leaves(tree[0]) + leaves(tree[1])
        node_sizes[count] += 1
        return count
    require([leaves(tree) for tree in caller["tree"]] == [4, 7, 8], "fixed three-root forest")
    require(node_sizes == Counter({2: 9, 3: 1, 4: 4, 7: 1, 8: 1}), "independent internal-node size census")
    paid, targets = [Counter({r: 19 * n for r, n in profile.items()}) for profile in local]
    paid[1] += PORTS * sum(node_sizes.values())
    targets[153] += 2 * PORTS
    for size, count in node_sizes.items():
        paid[8 * size] += 2 * PORTS * count
        targets[1 + 8 * size] += 2 * PORTS * count
    return paid, targets, dict(sorted(node_sizes.items()))


def profile(value):
    return {str(rank): count for rank, count in sorted(value.items()) if count}


def delta(after, before):
    result = Counter(after)
    result.subtract(before)
    return result


def first_departure(word, role):
    return next(event for event in word["program"] if event[0] == "MOVE" and event[1] == role)


def bind_changes(old, new, lifts, spaces):
    require(set(old) == set(new), "same local word schema")
    for key in old:
        if key not in ("initial", "program"):
            require(canonical(old[key]) == canonical(new[key]), "unchanged shared local interface: " + key)
    clusters = [cluster for round_ in lifts["rounds"] for cluster in round_["clusters"]]
    require(len(clusters) == 3, "three shared-carrier clusters")
    expected_initial, expected_removed, expected_added, carriers = {}, Counter(), Counter(), []
    for cluster in clusters:
        entrance = cluster["F"]
        integer(entrance, 0, len(spaces), "lift entrance label")
        require(dimension(spaces[entrance]) == 1 and len(cluster["carriers"]) == 1 and
                len(cluster["anchors"]) == 2, "one rank1 entrance and one carrier shared by two helpers")
        carrier = cluster["carriers"][0]
        old_event = first_departure(old, carrier)
        require(old_event[2] == 3 and dimension(spaces[old_event[3]]) == 2, "carrier old rank2 first destination")
        first = ("MOVE", carrier, 3, entrance, False)
        second = ("MOVE", carrier, entrance, old_event[3], False)
        old_role = Counter(tuple(e) for e in old["program"] if e[0] == "MOVE" and e[1] == carrier)
        new_role = Counter(tuple(e) for e in new["program"] if e[0] == "MOVE" and e[1] == carrier)
        require(old_role - new_role == Counter({tuple(old_event): 1}) and
                new_role - old_role == Counter({first: 1, second: 1}), "exact shared carrier detour")
        expected_removed.update([tuple(old_event)])
        expected_added.update([first, second])
        carriers.append({"carrier": carrier, "entrance_frame": entrance, "old_first_MOVE": old_event,
                         "new_first_MOVEs": [list(first), list(second)],
                         "old_rank": 2, "new_ranks": [1, 1]})
        for text_role in cluster["anchors"]:
            role = int(text_role)
            require(str(role) not in expected_initial and old["initial"][role] == 3, "distinct independent lifted input")
            expected_initial[str(role)] = [3, entrance]
            event = first_departure(old, role)
            require(event[2] == 3 and dimension(spaces[event[3]]) in (3, 5) and spaces[entrance] < spaces[event[3]],
                    "lift entrance nested in actual first destination")
            replacement = ("MOVE", role, entrance, event[3], False)
            expected_removed.update([tuple(event)])
            expected_added.update([replacement])
    initial = {str(r): [a, b] for r, (a, b) in enumerate(zip(old["initial"], new["initial"])) if a != b}
    require(initial == expected_initial and set(initial) == {"472", "520", "544", "624", "655", "671"},
            "exact six initial endpoint changes")
    old_moves = Counter(tuple(e) for e in old["program"] if e[0] == "MOVE")
    new_moves = Counter(tuple(e) for e in new["program"] if e[0] == "MOVE")
    require(old_moves - new_moves == expected_removed and new_moves - old_moves == expected_added,
            "all MOVE changes are the six entrances and three shared detours")
    return {"initial_frame_changes": initial, "final_frame_changes": {},
            "carrier_detours": carriers, "removed_MOVE_count": sum(expected_removed.values()),
            "added_MOVE_count": sum(expected_added.values()),
            "other_MOVE_records_cancel": True}


def rejection(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError("invalid mutated occurrence inventory accepted")


def controls(new, caller, local, complete, spaces, bindings):
    result = []
    baseline_paid, baseline_targets = complete
    for carrier in (171, 208, 130):
        changed = deepcopy(new)
        index = next(i for i, e in enumerate(changed["program"])
                     if e[0] == "MOVE" and e[1] == carrier and e[2] == 3)
        omitted = changed["program"].pop(index)
        counter_local = raw_local(changed, spaces)
        counter_paid, counter_targets = complete_from_events(counter_local, caller)
        require(delta(counter_paid, baseline_paid) == Counter({1: -19}) and counter_targets == baseline_targets,
                "omitted actual carrier trip loses nineteen charged H1 occurrences")
        result.append({"control": "omitted_carrier_trip", "carrier": carrier, "event_index": index,
                       "omitted_event": omitted, "complete_paid_delta": profile(delta(counter_paid, baseline_paid)),
                       "complete_target_delta": profile(delta(counter_targets, baseline_targets)),
                       "structural_rejection": rejection(lambda: validate_word(changed, spaces))})
    changed = deepcopy(new)
    changed["initial"][520] = 3
    counter_paid, counter_targets = complete_from_events(raw_local(changed, spaces), caller)
    require(delta(counter_targets, baseline_targets) == Counter({9: 19, 8: -19}) and counter_paid == baseline_paid,
            "reverted productive input omits exactly nineteen target debits")
    result.append({"control": "reverted_lifted_input_520", "complete_paid_delta": {},
                   "complete_target_delta": profile(delta(counter_targets, baseline_targets)),
                   "structural_rejection": rejection(lambda: validate_word(changed, spaces))})
    for opcode in ("IDLE", "QUERY", "LOCAL"):
        altered = deepcopy(caller)
        index = next(i for i, e in enumerate(altered["events"]) if e[0] == opcode)
        omitted = altered["events"].pop(index)
        paid, targets = complete_from_events(local, altered, strict=False)
        changed_paid, changed_targets = delta(paid, baseline_paid), delta(targets, baseline_targets)
        expected_paid = (Counter({8 * len(omitted[3]): -208}) if opcode == "IDLE" else
                         Counter({1: -104}) if opcode == "QUERY" else
                         Counter({rank: -count for rank, count in local[0].items()}))
        expected_targets = Counter({rank: -count for rank, count in local[1].items()}) if opcode == "LOCAL" else Counter()
        require(dict(profile(changed_paid)) == dict(profile(expected_paid)) and
                dict(profile(changed_targets)) == dict(profile(expected_targets)), "actual caller omission invoice")
        result.append({"control": "missing_" + opcode.lower(), "event_index": index, "omitted_event": omitted,
                       "complete_paid_delta": profile(changed_paid), "complete_target_delta": profile(changed_targets),
                       "structural_rejection": rejection(lambda: complete_from_events(local, altered))})
    return {"qualification": "These changed literal records give counterfactual invoice differences; structural guards reject them. They are not valid cheaper programs.",
            "cases": result}


def run():
    data = authenticate()
    old, new, caller = data["OLD-WORD.json.gz"], data["NEW-WORD.json.gz"], data["CONTROLLER.json"]
    require(canonical(old["frames"]) == canonical(new["frames"]), "unchanged native frame coordinates")
    spaces = frame_spaces(old["frames"])
    old_census, new_census = validate_word(old, spaces), validate_word(new, spaces)
    old_local, new_local = raw_local(old, spaces), raw_local(new, spaces)
    bindings = bind_changes(old, new, data["LIFTS.json"], spaces)
    old_complete, new_complete = complete_from_events(old_local, caller), complete_from_events(new_local, caller)
    for local, complete in ((old_local, old_complete), (new_local, new_complete)):
        paid, targets, node_sizes = complete_from_forest(local, caller)
        require((paid, targets) == complete, "independent emitted and forest-formula profiles")
    paid_delta, target_delta = delta(new_local[0], old_local[0]), delta(new_local[1], old_local[1])
    require(profile(paid_delta) == {"1": 6, "3": -3, "4": 3, "5": -3} and
            profile(target_delta) == {"8": 6, "9": -6}, "exact local signed changes")
    require(old_census["owned_lifetimes"] == new_census["owned_lifetimes"] == 43 and
            old_census["peak_owned"] == new_census["peak_owned"] == 13, "unchanged owned resource census")
    complete_records = {}
    for name, value in (("old", old_complete), ("new", new_complete)):
        paid, targets = value
        complete_records[name] = {"paid": profile(paid), "targets": profile(targets),
                                 "paid_jobs": sum(paid.values()), "productive_fields": sum(targets.values()),
                                 "rank_mass_surplus": sum(r*n for r,n in targets.items()) - sum(r*n for r,n in paid.items())}
    require(complete_records["old"]["paid_jobs"] == 70656 and complete_records["new"]["paid_jobs"] == 70713 and
            all(r["productive_fields"] == 14214 and r["rank_mass_surplus"] == 808 for r in complete_records.values()),
            "complete same-caller inventories")
    margin_delta = delta(target_delta, paid_delta)
    return {"schema_version": 1, "scope": "source-bound formal local and complete same-caller rank profiles only",
            "old_local": {"paid": profile(old_local[0]), "targets": profile(old_local[1]), "census": old_census},
            "new_local": {"paid": profile(new_local[0]), "targets": profile(new_local[1]), "census": new_census},
            "literal_changes": bindings, "forest_node_sizes": {str(k): v for k,v in node_sizes.items()},
            "complete": complete_records,
            "local_paid_delta": profile(paid_delta), "local_productive_delta": profile(target_delta),
            "local_margin_delta_coefficients": profile(margin_delta),
            "complete_paid_delta": profile(delta(new_complete[0], old_complete[0])),
            "complete_productive_delta": profile(delta(new_complete[1], old_complete[1])),
            "complete_margin_delta_coefficients": profile(Counter({r: 19*n for r,n in margin_delta.items()})),
            "controls": controls(new, caller, new_local, new_complete, spaces, bindings),
            "limits": ["Strict nested-frame ranks use the retained native/tariff premise; no native phase or all-width implementation proof is supplied.",
                       "Scalar common-frame and owned lifetime syntax is checked, not the public endpoint or shared response algebra.",
                       "The caller diagonal and primitive contracts are premises; no physical caller or ordinary-work funding is admitted.",
                       "No relative crossover, power evaluation, raw kappa root, new saving or supplier admission is computed."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit fresh canonical-profile receipt bytes")
    options = parser.parse_args()
    result = run()
    payload = (json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    if options.emit:
        sys.stdout.buffer.write(payload)
    else:
        retained = HERE / "PROFILES.json"
        require(retained.is_file(), "retained PROFILES.json receipt must exist")
        raw = retained.read_bytes()
        parsed = json.loads(raw)
        require(type(parsed) is dict and type(parsed.get("schema_version")) is int and parsed["schema_version"] == 1,
                "typed profile receipt schema")
        require(canonical(parsed) == canonical(result) and raw == payload, "exact typed byte PROFILES.json receipt")
        print("PASS exact source-bound rank profiles and retained receipt")
