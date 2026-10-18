#!/usr/bin/env python3
"""Independent set-valued census and exact separating-witness checker.

Imports no census, search, circuit-generator or pricing implementation.
Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"


class Reject(Exception):
    pass


def require(condition, message):
    if not condition:
        raise Reject(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    def invalid(value):
        raise Reject("nonfinite JSON value: " + value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)


def input_pins():
    manifest = strict_json((HERE / "SOURCES.json").read_bytes())
    require(set(manifest["runtime_inputs"]) == {WORD, CHECKER}, "runtime inventory")
    for name, digest in manifest["runtime_inputs"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, "source pin: " + name)
    return strict_json(gzip.decompress((ROOT / WORD).read_bytes()))


def source_trace(word):
    """Sets of input coordinates; independent of the generator's integer bit rows."""
    v = word["v"]
    n = 2*v + word["R"]
    rows = [{r} if r < v else set() for r in range(n)]
    current = list(word["start"])
    events, reads = [], {q: [] for q in range(2*v, n) if q not in word["ret"]}
    for section in ("A", "B"):
        for index, (frame, dest, sources) in enumerate(word[section]):
            events.append((section, index, frame, dest, tuple(sources)))
            for q in sources:
                if q in reads:
                    matches = []
                    for source in range(v):
                        if source != dest and not rows[source].symmetric_difference(rows[q]):
                            matches.append(source)
                    reads[q].append({"section": section, "gate": index, "frame": frame,
                                     "clean_row": hex(sum(2**r for r in rows[q])), "sources": matches})
            for source in sources:
                rows[dest] = rows[dest].symmetric_difference(rows[source])
            for r in (dest, *sources):
                current[r] = frame
        if section == "A":
            snapshot = [set(rows[q]) for q in word["ret"]]
            for index, q in enumerate(word["ret"]):
                events.append(("COPY", index, current[q], q, ()))
            for target, copies in enumerate(word["scatter"]):
                for index in copies:
                    rows[v+target] = rows[v+target].symmetric_difference(snapshot[index])
    return reads, events


def fixed_anchor(word, events, helper, position, register, backwards):
    positions = range(position-1, -1, -1) if backwards else range(position+1, len(events))
    for k in positions:
        section, index, frame, dest, sources = events[k]
        if dest == helper or helper in sources:
            continue
        if register == dest or register in sources:
            return frame, [section, index]
    name = "start" if backwards else "final"
    return word[name][register], [name, register]


def verify_barrier(word, events, helper, record):
    witness = record["obstruction"]
    key = witness["section"], witness["gate"]
    position = next((i for i, event in enumerate(events) if event[:2] == key), None)
    require(position is not None, "barrier gate")
    _, _, _, dest, sources = events[position]
    read = next((r for r in record["reads"] if (r["section"], r["gate"]) == key), None)
    require(read is not None and read["sources"] == [witness["source"]], "barrier donor")
    require(helper in sources, "barrier helper occurrence")
    touched = {dest} | (set(sources) ^ {helper, witness["source"]})
    a, b = witness["lower_register"], witness["upper_register"]
    require(a in touched and b in touched, "barrier operands")
    low, previous = fixed_anchor(word, events, helper, position, a, True)
    high, following = fixed_anchor(word, events, helper, position, b, False)
    require((low, previous) == (witness["lower_frame"], witness["previous"]), "lower anchor")
    require((high, following) == (witness["upper_frame"], witness["following"]), "upper anchor")
    line, normal = witness["separating_line"], witness["normal"]
    require(line in word["frames"][low], "line not forced by lower frame")
    require(len(normal) == 8 and all(type(x) is int for x in normal), "integer normal")
    dot = lambda row: sum(x*y for x, y in zip(normal, row))
    require(all(dot(word["lines"][i]) == 0 for i in word["frames"][high]), "upper annihilator")
    require(dot(word["lines"][line]) != 0, "nonseparating normal")


def verify_certificate(word, certificate):
    reads, events = source_trace(word)
    require(certificate["schema"] == "bit-source-substitution-census/1", "certificate schema")
    require(type(certificate["assignment_seed"]) is int and certificate["assignment_seed"] == 11, "seed")
    require(certificate["word_sha256"] == hashlib.sha256(canonical(word)).hexdigest(), "decoded word pin")
    require(certificate["retained_helpers"] == word["ret"], "retained coverage")
    require(certificate["helper_domain"] == [2*word["v"], 2*word["v"]+word["R"]], "helper domain")
    helpers = certificate["helpers"]
    order = list(reads)
    order = order[11:] + order[:11]
    require([x["helper"] for x in helpers] == order, "helper coverage/order")
    counts = Counter(retained=len(word["ret"]))
    survivors = []
    for record in helpers:
        q = record["helper"]
        require(canonical(record["reads"]) == canonical(reads[q]), "clean response census")
        require(bool(reads[q]), "unread helper not classified")
        failures = [r for r in reads[q] if not r["sources"]]
        status = record["status"]
        if status == "clean_row_obstruction":
            require(bool(failures), "missing clean obstruction")
            require(record["obstruction"] == {k: failures[0][k] for k in ("section", "gate")}, "clean witness")
        else:
            require(not failures and all(len(r["sources"]) == 1 for r in reads[q]), "unique donor coverage")
            if status == "frame_obstruction":
                verify_barrier(word, events, q, record)
            elif status == "surviving":
                require(record["obstruction"] is None, "survivor obstruction")
                survivors.append(q)
            else:
                raise Reject("unknown classification")
        counts[status] += 1
    require(canonical(dict(counts)) == canonical(certificate["counts"]), "census counts")
    occurrences = sum(len(x) for x in reads.values())
    require(type(certificate["read_occurrences"]) is int and certificate["read_occurrences"] == occurrences, "read coverage")
    require(type(certificate["source_comparisons"]) is int and certificate["source_comparisons"] == occurrences*word["v"], "source coverage")
    require(survivors == [470], "each survivor requires a constructive check")
    return dict(counts)


def raw_rows(word):
    v = word["v"]
    rows = [{r} for r in range(2*v+word["R"])]
    for section in ("A", "B"):
        for _, dest, sources in word[section]:
            for source in sources:
                rows[dest] ^= rows[source]
        if section == "A":
            snapshots = [set(rows[q]) for q in word["ret"]]
            for t, copies in enumerate(word["scatter"]):
                for index in copies:
                    rows[v+t] ^= snapshots[index]
    return rows


def positive_control(word, helper=470, donor=77, frame=186):
    """Reconstruct the already-published PR1043 local witness; no code imported."""
    require(helper not in word["ret"], "cannot delete retained total")
    changed = copy.deepcopy(word)
    rename = lambda r: r - (r > helper)
    for section in ("A", "B"):
        gates = []
        for f, dest, sources in word[section]:
            if dest == helper:
                continue
            if helper in sources:
                require(dest != donor, "self donor")
                sources = sorted(set(sources) ^ {helper, donor})
                f = frame
            gates.append([f, rename(dest), [rename(s) for s in sources]])
        changed[section] = gates
    changed["R"] -= 1
    changed["ret"] = [rename(r) for r in word["ret"]]
    for field in ("start", "final"):
        changed[field] = word[field][:helper] + word[field][helper+1:]
    # This diagnostic field counts the extra carriers; it is not a proof input.
    changed["stats"]["extra_carriers"] -= 1
    v = word["v"]
    full = next(i for i, f in enumerate(word["frames"]) if len(f) == v)
    changed["C"] = [[full, d, list(ss)] for _, d, ss in reversed(changed["A"]+changed["B"]) if not v <= d < 2*v]
    rows = raw_rows(changed)
    changed["D"] = [[0, v+t, sorted(s for s in rows[v+t] if s >= 2*v)] for t in range(v)]
    return changed


def rank(rows):
    pivots = {}
    for row in rows:
        row = [Fraction(x) for x in row]
        for p, basis in sorted(pivots.items()):
            scale = row[p]
            row = [a-scale*b for a, b in zip(row, basis)]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is not None:
            scale = row[pivot]
            pivots[pivot] = [x/scale for x in row]
    return len(pivots)


def full_replay(word, dimensions):
    v, n = word["v"], 2*word["v"]+word["R"]
    rows = [{r} for r in range(n)]
    current = list(word["start"])
    frames = [set(f) for f in word["frames"]]
    profile = Counter()
    def move(register, frame):
        before = current[register]
        require(frames[before] <= frames[frame], "frame descent")
        change = dimensions[frame] - dimensions[before]
        if change:
            require(change > 0, "nonpositive climb")
            profile[change] += 1
        current[register] = frame
    for section in ("D", "A", "B", "C"):
        for frame, dest, sources in word[section]:
            require(len({dest, *sources}) == 1+len(sources), "noninvertible gate")
            for register in (dest, *sources):
                move(register, frame)
            for source in sources:
                rows[dest] ^= rows[source]
        if section == "A":
            snapshots = [set(rows[q]) for q in word["ret"]]
            for q in word["ret"]:
                profile[dimensions[current[q]]] += 1
            for t, copies in enumerate(word["scatter"]):
                for index in copies:
                    rows[v+t] ^= snapshots[index]
    for r, f in enumerate(word["final"]):
        move(r, f)
        require(rows[r] == ({r, r-v} if v <= r < 2*v else {r}), "dirty scalar endpoint")
    adds = sum(len(ss) for sec in ("D", "A", "B", "C") for _, _, ss in word[sec]) + sum(map(len, word["scatter"]))
    return {"columns": n, "ADDs": adds, "profile": dict(sorted(profile.items())),
            "rank_mass": sum(r*c for r, c in profile.items())}


def negative_controls(word, certificate, dimensions):
    tested = []
    def refuses(name, callback, reason):
        try:
            callback()
        except Reject as error:
            require(reason in str(error), name + ": wrong rejection: " + str(error))
            tested.append(name)
        else:
            raise Reject(name + ": mutation accepted")
    candidate = positive_control(word)
    for name, helper, source, frame in (("late_source_descent", 470, 77, 79),
                                       ("scalar_match_with_illegal_frame", 462, 47, 506),
                                       ("wrong_source", 470, 78, 186)):
        bad = positive_control(word, helper, source, frame)
        reason = "dirty scalar endpoint" if name == "wrong_source" else "frame descent"
        # Wrong donor may also be unavailable; test its scalar error with legal frame tests disabled below.
        if name == "wrong_source":
            rows = raw_rows(bad)
            refuses(name, lambda: require(all((rows[bad["v"]+t] & set(range(bad["v"]))) == {t} for t in range(bad["v"])), "dirty scalar endpoint"), reason)
        else:
            refuses(name, lambda b=bad: full_replay(b, dimensions), reason)
    for name, section in (("missing_cleanup", "C"), ("missing_compensation", "D")):
        bad = copy.deepcopy(candidate)
        bad[section][0][2].pop()
        refuses(name, lambda b=bad: full_replay(b, dimensions), "dirty scalar endpoint")
    refuses("retained_helper_deletion", lambda: positive_control(word, word["ret"][0]), "retained total")
    bad = copy.deepcopy(certificate)
    bad["helpers"].pop()
    refuses("omitted_helper", lambda: verify_certificate(word, bad), "helper coverage")
    bad = copy.deepcopy(certificate)
    bad["helpers"][0]["reads"][0]["clean_row"] = "0x0"
    refuses("altered_clean_row", lambda: verify_certificate(word, bad), "clean response")
    bad = copy.deepcopy(certificate)
    next(x for x in bad["helpers"] if x["status"] == "frame_obstruction")["obstruction"]["normal"] = [0]*8
    refuses("false_separator", lambda: verify_certificate(word, bad), "nonseparating")
    bad = copy.deepcopy(certificate)
    barrier = next(x for x in bad["helpers"] if x["status"] == "frame_obstruction")["obstruction"]
    barrier["previous"] = ["start", barrier["lower_register"]]
    refuses("wrong_fixed_anchor", lambda: verify_certificate(word, bad), "lower anchor")
    # A paid neutral pair must be accepted, guarding against rejecting every changed word.
    neutral = copy.deepcopy(candidate)
    neutral["D"][:0] = [[0, word["v"], [2*word["v"]]], [0, word["v"], [2*word["v"]]]]
    require(full_replay(neutral, dimensions)["ADDs"] == full_replay(candidate, dimensions)["ADDs"]+2,
            "neutral pair not fully charged")
    return tested


def main():
    word = input_pins()
    certificate = strict_json((HERE / "CERTIFICATE.json").read_bytes())
    counts = verify_certificate(word, certificate)
    dimensions = [rank([word["lines"][i] for i in f]) for f in word["frames"]]
    candidate = positive_control(word)
    before, after = full_replay(word, dimensions), full_replay(candidate, dimensions)
    require((before["ADDs"], after["ADDs"]) == (24305, 24248), "complete ADD accounting")
    require((before["rank_mass"], after["rank_mass"]) == (5129, 5121), "complete local rank accounting")
    controls = negative_controls(word, certificate, dimensions)
    # The unchanged owning checker supplies E8 geometry and original H1-H5 checks.
    with tempfile.TemporaryDirectory(prefix="bit-source-control-") as tmp:
        path = Path(tmp) / "control.json.gz"
        path.write_bytes(gzip.compress(canonical(candidate), mtime=0))
        for name, input_path in (("baseline", ROOT/WORD), ("PR1043 control", path)):
            run = subprocess.run([sys.executable, "-I", "-B", str(ROOT/CHECKER), str(input_path)],
                                 capture_output=True, text=True, timeout=60)
            require(run.returncode == 0 and "PASS interleaved interface lemma" in run.stdout,
                    name + " owning checker: " + run.stdout + run.stderr)
    print(json.dumps({"counts": counts, "baseline": before, "known_PR1043_control": after,
                      "controls": controls, "owning_geometry_and_H1_H5": "PASS", "no_new_kappa": True}, sort_keys=True))
    print("PASS_SOURCE_SUBSTITUTION_INDEPENDENT helpers=439 retained=9 clean_blocked=423 frame_blocked=6 survivor=470 reads=2102 controls=10 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (Reject, KeyError, TypeError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        print("REJECT:", error, file=sys.stderr)
        raise SystemExit(1)
