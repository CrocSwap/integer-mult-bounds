#!/usr/bin/env python3
"""Compare the emitted PR5713 word with the credited temporal edit.

The predecessor word and witness are pinned inputs. This checker rebuilds the
edit and replays the scalar identity without importing the author constructor.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
"""

from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "p104-temporal-updates"
WIDTH = 9

NATIVE_KEYS = {
    "distinct_maps",
    "helper_normalizers",
    "helpers",
    "main_adapters",
    "proof",
    "recipe_payload_sha256",
    "wrong_phase_rejected",
}
CALLER_KEYS = {
    "central_square_columns",
    "full_calls",
    "main_targets",
    "new_paid_jobs",
    "physical_contacts",
    "ports",
    "route_payload_sha256",
    "tensor_rule",
    "whole_idle_jobs",
    "wrapper_sites",
}
EMITTED_RANKS = {1: 2184, 2: 459, 3: 495, 4: 92, 5: 159, 6: 22, 7: 15}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load_json(path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def add(dst, src, coefficient):
    for column, value in src.items():
        value = dst.get(column, Fraction(0)) + coefficient * value
        if value:
            dst[column] = value
        else:
            dst.pop(column, None)


def apply_scalar(rows, frames, event):
    """Decoded scalar step used by the predecessor word."""
    op, target = event[0], event[1]
    if op == "MOVE":
        frames[target] = event[3]
    elif op == "INIT":
        rows[target] = {}
        frames[target] = event[2]
    elif op == "CLEAR":
        rows[target] = {}
        frames[target] = None
    elif op == "SCALE":
        rows[target] = {j: Fraction(event[-2]) * value for j, value in rows[target].items()}
    elif op == "COPY":
        rows[target] = {j: Fraction(event[-2]) * value for j, value in rows[event[2]].items()}
    else:
        need(op == "ADD", "Known scalar instruction")
        add(rows[target], rows[event[2]], Fraction(event[-2]))


def scalar_identity(word, witness):
    role = witness["role"]
    start, stop = witness["start"], witness["stop"]
    removed = witness["removed_event"]
    program = word["program"]
    need(0 <= start <= removed < stop <= len(program), "Bounded witness interval")
    old = program[removed]
    need(old[0] == "ADD" and old[1] == role, "Removed event is one target ADD")
    width = word["public"] + word["owned_fields"]
    rows = [{i: Fraction(1)} for i in range(width)]
    frames = list(word["initial"]) + [None] * word["owned_fields"]
    need(len(frames) == width, "One frame register per public or owned field")
    terms = defaultdict(list)
    for term in witness["inserts"]:
        need(start <= term["cut"] <= stop and term["source"] != role, "Replacement cut and source")
        terms[term["cut"]].append(term)
    total, expected, observations = {}, {}, []
    target_reads = []
    for index in range(stop + 1):
        for term in terms.get(index, []):
            source, frame = term["source"], term["frame"]
            coefficient = Fraction(term["coefficient"])
            need(coefficient, "Nonzero replacement")
            need(frames[role] == frames[source] == frame, "Common frame at the replacement cut")
            add(total, rows[source], coefficient)
            observations.append([index, source, frame, len(rows[source])])
        if index == stop:
            break
        event = program[index]
        op, target = event[0], event[1]
        if start <= index < stop:
            if op in ("ADD", "COPY") and event[2] == role:
                target_reads.append(index)
            if target == role and op in ("SCALE", "COPY", "INIT", "CLEAR"):
                target_reads.append(index)
        if index == removed:
            add(expected, rows[event[2]], Fraction(event[-2]))
        apply_scalar(rows, frames, event)
    need(not target_reads, "No read or non-additive write of the changed target")
    need(total == expected and expected, "Exact distributed source functional")
    encoded = [[j, str(value)] for j, value in sorted(expected.items())]
    digest = sha256(json.dumps(encoded, separators=(",", ":")).encode()).hexdigest()
    return {
        "coefficients": len(expected),
        "sha256": digest,
        "observations": observations,
        "functional": {str(j): str(value) for j, value in sorted(expected.items())},
    }


def credited_program(source, witness):
    role = witness["role"]
    first = witness["removed_move"]
    removed = witness["removed_event"]
    last = witness["merged_move"]
    origin, middle, terminal = witness["old_frames"]
    program = source["program"]
    need(program[first] == ["MOVE", role, origin, middle, False], "Removed transport")
    need(program[removed][:3] == ["ADD", role, 747], "Removed centre read")
    need(program[last] == ["MOVE", role, middle, terminal, False], "Merged transport")
    need(first < removed < last, "Removed contact lies between the transports")
    inserts = defaultdict(list)
    for term in witness["inserts"]:
        inserts[term["cut"]].append(
            ["ADD", role, term["source"], term["coefficient"], term["frame"]]
        )
    edited = []
    for index, event in enumerate(program):
        edited.extend(inserts.get(index, []))
        if index in (first, removed):
            continue
        if index == last:
            edited.append(["MOVE", role, origin, terminal, False])
        else:
            edited.append(event)
    edited.extend(inserts.get(len(program), []))
    return edited


def move_ranks(word):
    dims = [len(frame) for frame in word["frames"]]
    ranks = Counter()
    for event in word["program"]:
        if event[0] == "MOVE":
            ranks[abs(dims[event[3]] - dims[event[2]])] += 1
    return dict(ranks)


def span_basis(masks):
    pivot = {}
    for mask in masks:
        value = mask
        for lead in sorted(pivot, reverse=True):
            if value & (1 << lead):
                value ^= pivot[lead]
        if not value:
            continue
        lead = value.bit_length() - 1
        for other in list(pivot):
            if pivot[other] & (1 << lead):
                pivot[other] ^= value
        pivot[lead] = value
    return pivot


def in_span(value, pivot):
    for lead in sorted(pivot, reverse=True):
        if value & (1 << lead):
            value ^= pivot[lead]
    return value == 0


def frame_chain(word):
    frames = word["frames"]
    empty, middle, terminal = frames[3], frames[598], frames[396]
    need(empty == [] and middle == [491] and terminal == [13, 70, 416], "Pinned frame supports")
    need(all(0 <= mask < (1 << WIDTH) for mask in middle + terminal), "Vectors lie in F_2^9")
    need(13 ^ 70 ^ 416 == 491, "491 is the sum of the terminal basis")
    basis = span_basis(terminal)
    need(len(basis) == 3 and in_span(491, basis) and in_span(0, basis), "Strict F_2^9 chain")
    dims = (len(empty), len(middle), len(terminal))
    need(dims == (0, 1, 3), "Dimensions 0 < 1 < 3")
    return {
        "dimensions": dims,
        "removed_ranks": (1, 2),
        "merged_rank": 3,
        "relation": "13 XOR 70 XOR 416 = 491",
    }


def archive_payloads(raw, depth=4):
    try:
        bundle = tarfile.open(fileobj=io.BytesIO(raw), mode="r:")
    except tarfile.TarError:
        return
    for member in bundle.getmembers():
        if not member.isfile():
            continue
        payload = bundle.extractfile(member).read()
        yield member.name, payload
        if depth and member.name.endswith(".tar"):
            yield from archive_payloads(payload, depth - 1)


def receipt_gap(result):
    native = result["native"]
    caller = result["physical_caller"]
    need(set(native) == NATIVE_KEYS, "Native receipt is the published summary")
    need(set(caller) == CALLER_KEYS, "Caller receipt is the published summary")
    need(isinstance(native["proof"], str) and len(native["proof"]) < 400, "Native proof is one sentence")
    need(len(json.dumps(native)) < 1000 and len(json.dumps(caller)) < 2000, "Receipts are not event traces")
    hashes = {
        "native_recipe": native["recipe_payload_sha256"],
        "caller_route": caller["route_payload_sha256"],
    }
    for name, digest in hashes.items():
        need(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), name)
    seen = {}
    for path in PACKAGE.rglob("*"):
        if path.is_file():
            seen[sha256(path.read_bytes()).hexdigest()] = str(path.relative_to(ROOT))
    archive = PACKAGE / "inputs" / "pr5678-source.tar"
    for name, payload in archive_payloads(archive.read_bytes()):
        seen[sha256(payload).hexdigest()] = "pr5678-source.tar:" + name
    missing = {name: digest for name, digest in hashes.items() if digest not in seen}
    need(set(missing) == set(hashes), "Neither payload is a retained file or archive member")
    return {
        "native_bytes": len(json.dumps(native)),
        "caller_bytes": len(json.dumps(caller)),
        "full_calls_recorded_not_rederived": caller["full_calls"],
        "missing_preimages": missing,
    }


def compare(source, emitted, witness, result):
    edited = credited_program(source, witness)
    need(emitted["program"] == edited, "Emitted program is the credited edit")
    for key, value in source.items():
        if key == "program":
            continue
        if key == "schema":
            need(emitted[key] == "p104-temporal-updates/1", "Successor schema")
        else:
            need(emitted[key] == value, "Unchanged geometry: " + key)
    identity = scalar_identity(source, witness)
    recorded = result["temporal_identity"]
    need(identity["coefficients"] == 105, "105 source coefficients")
    need(identity["sha256"] == recorded["source_sha256"], "Independent functional hash")
    need(identity["observations"] == recorded["observations"], "Replacement observations")
    need(len(emitted["program"]) == len(source["program"]) - 2 + 4 == 25453, "Instruction count")
    chain = frame_chain(source)
    before, after = move_ranks(source), move_ranks(emitted)
    delta = {rank: after.get(rank, 0) - before.get(rank, 0) for rank in set(before) | set(after)}
    delta = {rank: count for rank, count in delta.items() if count}
    need(delta == {1: -1, 2: -1, 3: 1}, "Local query change is one H1 and one H2 for one H3")
    need(after == EMITTED_RANKS, "Emitted local rank profile")
    gap = receipt_gap(result)
    return {
        "instructions": len(emitted["program"]),
        "identity_sha256": identity["sha256"],
        "coefficients": identity["coefficients"],
        "rank_delta": delta,
        "chain": chain,
        "receipt_gap": gap,
    }


def controls(source, emitted, witness, result):
    bad = json.loads(json.dumps(witness))
    bad["inserts"][0]["coefficient"] = "-1/4"
    try:
        scalar_identity(source, bad)
    except ValueError as error:
        need("Exact distributed source functional" in str(error), "Sign control reached the identity")
    else:
        raise ValueError("A wrong replacement sign was accepted")

    bad = json.loads(json.dumps(witness))
    bad["inserts"].pop()
    try:
        scalar_identity(source, bad)
    except ValueError as error:
        need("Exact distributed source functional" in str(error), "Omission control reached the identity")
    else:
        raise ValueError("A missing replacement was accepted")

    broken = json.loads(json.dumps(emitted))
    broken["program"] = [event for event in broken["program"] if event != ["MOVE", 715, 3, 396, False]]
    need(broken["program"] != emitted["program"], "Control actually changes the word")
    try:
        compare(source, broken, witness, result)
    except ValueError as error:
        need("Emitted program" in str(error), "A deleted transport must fail program equality")
    else:
        raise ValueError("A deleted transport was accepted")

    forged = json.loads(json.dumps(result))
    forged["native"]["events"] = [0]
    try:
        receipt_gap(forged)
    except ValueError as error:
        need("Native receipt" in str(error), "An event trace must leave the summary shape")
    else:
        raise ValueError("An expanded native receipt was treated as a summary")


def main():
    source = load_json(PACKAGE / "inputs" / "pr5684" / "WORD.json.gz")
    emitted = load_json(PACKAGE / "WORD.json.gz")
    witness = load_json(PACKAGE / "WITNESS.json")
    result = load_json(PACKAGE / "RESULT.json")
    report = compare(source, emitted, witness, result)
    controls(source, emitted, witness, result)
    print(
        "PASS_PR5713_EMITTED_EDIT_MATCHES instructions={instructions} "
        "coefficients={coefficients} identity_sha256={identity_sha256} "
        "rank_delta={rank_delta} chain={chain}".format(**report)
    )
    print(
        "PASS_PR5713_NATIVE_CALLER_RECEIPTS_ARE_SUMMARIES "
        "native_bytes={native_bytes} caller_bytes={caller_bytes} "
        "full_calls_recorded_not_rederived={full_calls_recorded_not_rederived}".format(
            **report["receipt_gap"]
        )
    )


if __name__ == "__main__":
    main()
