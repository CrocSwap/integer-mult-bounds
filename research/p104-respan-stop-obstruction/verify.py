"""Certify fixed scalar contacts obstructing one P104 stop deletion.

New proof and implementation produced by Nick Petalas. Apache-2.0.
Input word and question: DreamingOfClouds PR6345 over Ali Romman's PR6167.
"""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import platform

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORD = "research/p104-frontier-symmetric-ladders/WORD.json.gz"
MAX_RAW = 16 * 1024 * 1024
STATUS = "PASS_P104_RESPAN_STOP_OBSTRUCTION"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def authenticated_word():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            need(digest(raw) == row["sha256"], "Source hash: " + row["path"])
    raw = (ROOT / WORD).read_bytes()
    need(len(raw) <= MAX_RAW, "Compressed input size")
    with gzip.GzipFile(fileobj=BytesIO(raw)) as stream:
        payload = stream.read(MAX_RAW + 1)
    need(len(payload) <= MAX_RAW, "Expanded input size")
    word = json.loads(payload)
    need(0 < len(word["program"]) <= 26000, "Event capacity")
    need(0 < len(word["initial"]) <= 1024, "Public capacity")
    need(len(word["initial"]) + word["owned_fields"] <= 1024, "Field capacity")
    need(0 < len(word["frames"]) <= 2048, "Frame capacity")
    need(word["public"] == len(word["initial"]), "Public declaration")
    return word, digest(raw), digest(payload)


def frame_spans(word):
    spans = []
    for basis in word["frames"]:
        need(len(basis) <= 9, "Ambient dimension")
        values = {0}
        for vector in basis:
            need(type(vector) is int and 0 < vector < 512, "Binary vector range")
            need(vector not in values, "Independent frame basis")
            values |= {x ^ vector for x in values}
        spans.append(frozenset(values))
    return spans


def free_helpers(word):
    moves = Counter(e[1] for e in word["program"] if e[0] == "MOVE")
    main = set(word["live"]) | {r + 112 for r in word["live"]}
    return {r for r in range(len(word["initial"]))
            if r not in main and moves[r] == 1}


def trace(word):
    """Index constant-frame epochs, keeping owned lives separate."""
    public = len(word["initial"])
    lives = Counter()
    chains = {(r, 0): [f] for r, f in enumerate(word["initial"])}
    active = {r: (r, 0, 0) for r in range(public)}
    contacts = []
    for index, event in enumerate(word["program"]):
        op, r = event[:2]
        if op == "INIT":
            need(r >= public and r not in active, "Fresh owned life")
            lives[r] += 1
            chains[r, lives[r]] = [event[2]]
            active[r] = (r, lives[r], 0)
            continue
        need(r in active, "Active destination")
        key = active[r]
        chain = chains[key[:2]]
        if op == "MOVE":
            need(chain[-1] == event[2], "MOVE source frame")
            need(event[4] == int(r >= public), "MOVE ownership")
            active[r] = (r, lives[r], len(chain))
            chain.append(event[3])
        elif op == "CLEAR":
            need(r >= public and chain[-1] == event[2], "Owned exit")
            del active[r]
        else:
            need(op in ("ADD", "COPY", "SCALE"), "Scalar opcode")
            need(chain[-1] == event[-1], "Scalar destination chart")
            if op in ("ADD", "COPY"):
                s = event[2]
                need(s != r and s in active, "Active scalar source")
                partner = active[s]
                need(chains[partner[:2]][-1] == event[-1], "Common scalar chart")
                contacts.append((index, key, partner))
    need(set(active) == set(range(public)), "Completed owned lives")
    need([chains[r, 0][-1] for r in range(public)] == word["final"],
         "Final frame declarations")
    return chains, contacts


def stop_domain(word, chains):
    spans = frame_spans(word)
    stops = set()
    for (r, life), chain in chains.items():
        for k in range(1, len(chain) - 1):
            before, middle, after = (spans[f] for f in chain[k - 1:k + 2])
            ordered = before < middle < after if r < len(word["initial"]) \
                else after < middle < before
            need(ordered, "Strict neighboring stop subspaces")
            stops.add((r, life, k))
    return stops


def certificate(word):
    chains, contacts = trace(word)
    stops = stop_domain(word, chains)
    free = free_helpers(word)
    anchors = {}
    for index, a, b in contacts:
        for stop, partner in ((a, b), (b, a)):
            if stop in stops and partner[0] not in free:
                anchors.setdefault(stop, (index, partner))
    need(set(anchors) == stops, "Unanchored intermediate stop")
    return [list(stop) + [anchors[stop][0]] + list(anchors[stop][1])
            for stop in sorted(stops)]


def check_certificate(word, records):
    """Separate streaming checker; no primary trace or domain is used."""
    public = len(word["initial"])
    totals = [0] * (public + word["owned_fields"])
    for event in word["program"]:
        if event[0] == "MOVE":
            totals[event[1]] += 1
    mains = set(word["live"] + [r + 112 for r in word["live"]])
    free = {r for r in range(public) if r not in mains and totals[r] == 1}
    requested, declared = {}, set()
    for row in records:
        need(len(row) == 7, "Witness arity")
        stop = tuple(row[:3])
        need(stop not in declared, "Duplicate stop witness")
        declared.add(stop)
        requested.setdefault(row[3], []).append(row)
    lives = [0] * len(totals)
    ordinal = [0] * len(totals)
    current = dict(enumerate(word["initial"]))
    candidates, checked = set(), set()
    for index, event in enumerate(word["program"]):
        op, r = event[:2]
        if op == "INIT":
            lives[r] += 1
            ordinal[r] = 0
            current[r] = event[2]
        elif op == "MOVE":
            if ordinal[r] > 0:
                candidates.add((r, lives[r], ordinal[r]))
            ordinal[r] += 1
            current[r] = event[3]
        elif op == "CLEAR":
            del current[r]
        for row in requested.get(index, []):
            need(op in ("ADD", "COPY"), "Witness must be a contact")
            s = event[2]
            ends = ((r, lives[r], ordinal[r]), (s, lives[s], ordinal[s]))
            stop, partner = tuple(row[:3]), tuple(row[4:])
            need((stop, partner) in (ends, ends[::-1]), "Actual contact epochs")
            need(partner[0] not in free, "Partner must be fixed")
            need(current[r] == current[s] == event[-1], "Actual common chart")
            checked.add(stop)
    need(declared == candidates == checked, "Complete exact stop coverage")
    return dict(stops=len(candidates),
                public_stops=sum(r < public for r, _, _ in candidates),
                owned_stops=sum(r >= public for r, _, _ in candidates),
                free_helpers=sorted(free))


def reject(call, *args):
    try:
        call(*args)
    except ValueError:
        return 1
    raise ValueError("Semantic control was accepted")


def toy(anchored):
    program = [["MOVE", 0, 0, 1, 0], ["ADD", 0, 1, "1", 1]]
    if anchored:
        program.append(["ADD", 0, 2, "1", 1])
    program += [["MOVE", 0, 1, 2, 0], ["MOVE", 1, 1, 2, 0]]
    return dict(frames=[[], [1], [1, 2]], initial=[0, 1, 1],
                final=[2, 2, 1], public=3, owned_fields=0, live=[],
                program=program)


def controls(word, records):
    checks = reject(check_certificate, word, records[:-1])
    checks += reject(check_certificate, word, records + [records[0]])
    for column, value in ((0, -1), (2, -1), (3, -1), (4, -1), (6, -1)):
        mutant = [list(row) for row in records]
        mutant[0][column] = value
        checks += reject(check_certificate, word, mutant)
    mutant = [list(row) for row in records]
    mutant[0][4:] = [min(free_helpers(word)), 0, 0]
    checks += reject(check_certificate, word, mutant)
    anchored = toy(True)
    need(check_certificate(anchored, certificate(anchored))["stops"] == 1,
         "Anchored toy positive control")
    checks += reject(certificate, toy(False))
    collapsed = toy(False)
    collapsed["initial"][1] = 0
    collapsed["program"] = [["ADD", 0, 1, "1", 0],
                            ["MOVE", 0, 0, 2, 0], ["MOVE", 1, 0, 2, 0]]
    need(check_certificate(collapsed, certificate(collapsed))["stops"] == 0,
         "Unanchored toy admits helper respanning and stop removal")
    blocked = toy(True)
    blocked["initial"][1] = 0
    blocked["program"] = collapsed["program"][:1] + \
        [["ADD", 0, 2, "1", 0]] + collapsed["program"][1:]
    checks += reject(trace, blocked)
    return checks


def run(receipt_path):
    word, compressed_hash, payload_hash = authenticated_word()
    records = certificate(word)
    result = check_certificate(word, records)
    need((result["stops"], result["public_stops"], result["owned_stops"],
          len(result["free_helpers"])) == (2660, 2654, 6, 42), "Frozen question domain")
    checks = controls(word, records)
    need(checks == 10, "Complete rejection control count")
    result.update(status=STATUS, claim_type="scoped proof with finite certificate",
                  semantic_rejections=checks, positive_toy_controls=2,
                  source_sha256=compressed_hash, payload_sha256=payload_hash,
                  events=len(word["program"]), python=platform.python_version(),
                  witness_sha256=digest(json.dumps(records).encode()))
    if receipt_path is not None:
        output = receipt_path.resolve()
        need(not output.is_relative_to(ROOT), "Receipt must be outside checkout")
        hashes = {p.name: digest(p.read_bytes()) for p in sorted(HERE.iterdir())
                  if p.is_file()}
        receipt = dict(result, package_sha256=hashes, anchors=records)
        output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    run(parser.parse_args().receipt)
