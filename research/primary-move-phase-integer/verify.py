#!/usr/bin/env python3
"""The #6030 primary stores a width-1 phase integer, not a joint phase.

The source claim is the inspection of local.native in the PR5827 archive.
The state claim is exhaustive for one rank-1 MOVE. See PROOF.md.
"""

from contextlib import ExitStack
from hashlib import sha256
import gzip
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORD = ROOT / "research/p104-helper470-twin-rung-removal/WORD.json.gz"
RESULT = ROOT / "research/p104-helper470-twin-rung-removal/RESULT.json"
OPENER = ROOT / "research/p104-helper470-twin-rung-removal/sources.py"
ARCHIVE = ROOT / "research/p104-helper470-twin-rung-removal/inputs/pr5827-source.tar"
CLIFFORD = ROOT / "research/p104-native-channel/vendor/clifford_exact.py"
NATIVE = ROOT / "research/p104-native-channel/vendor/native_verify.py"

WORD_SHA256 = "7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f"
RESULT_SHA256 = "84fcbe2a0b64307b5703c363408042bdd91555b0419509aa50daa43b3b1924ad"
ARCHIVE_SHA256 = "7af5908a4d83e83e28f59523fd7494841f669b7295311cfdbc3027fa65c5826d"
CLIFFORD_SHA256 = "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"
NATIVE_SHA256 = "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38"
LOCAL_SHA256 = "7201df8e32f5c99f7403150e8664042322037906088bc754c67293a241368597"
PROOF = (
    "Every signed Pauli image and exact global phase; "
    "frame induction at every positive tensor width"
)
EVENT = 9896
ROLE = 236
SOURCE = 3
DESTINATION = 7
PHASE = 1


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def span(basis):
    out = {0}
    for value in basis:
        need(type(value) is int and 0 < value < 512 and value not in out, "Independent frame vector")
        out |= {point ^ value for point in tuple(out)}
    return frozenset(out)


def walk(word):
    public = word["public"]
    owned = word["owned_fields"]
    need(word.get("schema") == "p104-accumulated-block-composition/2", "Selected word schema")
    need(public == 770 and owned == 29, "Selected inventory")
    frames = [span(row) for row in word["frames"]]
    current = list(word["initial"]) + [None] * owned
    live = set()
    moves = 0
    for event in word["program"]:
        op, role = event[0], event[1]
        need(op in ("MOVE", "INIT", "CLEAR", "ADD", "SCALE", "COPY"), "Opcode")
        if op == "MOVE":
            source, destination, private = event[2], event[3], event[4]
            need(current[role] == source, "MOVE leaves the recorded chart")
            need((role in live) is private, "MOVE ownership flag")
            if private:
                need(frames[destination] < frames[source], "Private transport shrinks the chart")
            else:
                need(frames[source] < frames[destination], "Public transport enlarges the chart")
            current[role] = destination
            moves += 1
        elif op == "INIT":
            need(role >= public and role not in live, "INIT")
            live.add(role)
            current[role] = event[2]
        elif op == "CLEAR":
            need(role in live and current[role] == event[2], "CLEAR")
            live.remove(role)
            current[role] = None
        else:
            need(current[role] == event[-1], "Scalar destination chart")
    need(not live and current[:public] == word["final"], "Public exit charts")
    need(moves == 3453, "Selected MOVE count")


def joint_factor(body):
    """True when native() builds a multiplicity-dependent phase outside its proof sentence."""
    rest = body.replace(PROOF, "", 1)
    markers = ("tensor", "multiplicity", "phase * f", "p*f", "p * f")
    return any(marker in rest for marker in markers) or rest.count(PROOF) != 0


def primary_bytes():
    opener = load(OPENER, "primary_phase_opener")
    with ExitStack() as contexts:
        parent = contexts.enter_context(opener.sources())
        cursor = contexts.enter_context(opener.load(parent / "sources.py", "base_source_top").sources())
        root = None
        for depth in range(7):
            module = opener.load(cursor / "sources.py", "base_source_" + str(depth))
            cursor, root = contexts.enter_context(module.sources())
        need(root is not None, "Depth-7 source root")
        vendor = root / "research/p104-native-channel/vendor"
        need(sha256((vendor / "clifford_exact.py").read_bytes()).hexdigest() == CLIFFORD_SHA256,
             "Primary Clifford bytes")
        need(sha256((vendor / "native_verify.py").read_bytes()).hexdigest() == NATIVE_SHA256,
             "Primary native-verify bytes")
        text = (parent / "local.py").read_bytes()
        need(sha256(text).hexdigest() == LOCAL_SHA256, "Primary local.py bytes")
        return text


def inspect(text):
    body = text.decode().split("def native(w):", 1)
    need(len(body) == 2, "native function")
    body = "def native(w):" + body[1]
    need(body.count(PROOF) == 1, "Proof sentence occurs once")
    need("lower_child" in body, "Recipes come from lower_child")
    need("recipes[a,b] = recipe" in body, "Stored recipe assignment")
    need(
        "payload = [[a,b,recipes[a,b]] for a,b in sorted(recipes)] + adapters" in body,
        "Payload is the width-1 records",
    )
    need(not joint_factor(body), "No joint phase factor")
    planted = body.replace("return {", "phase_scale = phase * f\n    return {", 1)
    need(planted != body and joint_factor(planted), "Planted joint factor is detected")
    return body


def multiply(left, right):
    a, b = left
    c, d = right
    return (a * c - b * d, a * d + b * c)


def tensor(left, right):
    values = {}
    for address, pair in left[0].items():
        for other, factor in right[0].items():
            values[(address, other)] = multiply(pair, factor)
    return values, left[1] + right[1]


def rotate(native, state, power):
    values, denominator = state
    return {key: native.rotate(pair, power) for key, pair in values.items()}, denominator


def witness(word):
    event = word["program"][EVENT]
    need(event == ["MOVE", ROLE, SOURCE, DESTINATION, False], "Pinned MOVE")
    first = next(
        index for index, item in enumerate(word["program"])
        if item[0] == "MOVE"
        and abs(len(word["frames"][item[2]]) - len(word["frames"][item[3]])) == 1
    )
    need(first == EVENT, "First rank-1 MOVE")
    clifford = load(CLIFFORD, "primary_phase_clifford")
    native = load(NATIVE, "primary_phase_native")
    start = clifford.canonical_frame(9, tuple(word["frames"][SOURCE]))
    stop = clifford.canonical_frame(9, tuple(word["frames"][DESTINATION]))
    record, _compiled = clifford.lower_child(start.adjoint().then(stop))
    recipe = native.recipe(record)
    gates = [gate[1] for gate in recipe if gate[0] == "phase"]
    phase = sum(gates) % 4
    right = record["right"]["phase"]
    need(record["rank"] == 1 and record["left"]["phase"] == 0 and right == phase == PHASE, "Phase integer")
    need("phase" in record["left"] and "f" not in record and "f" not in record["left"], "No multiplicity field")
    stripped = tuple(gate for gate in recipe if gate[0] != "phase")
    full = [native.state(recipe, basis) for basis in range(512)]
    free = [native.state(stripped, basis) for basis in range(512)]
    for basis in range(512):
        need(rotate(native, free[basis], PHASE) == full[basis], "Width-1 global phase")
        need(rotate(native, free[basis], PHASE + 1) != full[basis], "Off-by-one phase")
    for left in range(512):
        for right_basis in range(512):
            correct = tensor(full[left], full[right_basis])
            base = tensor(free[left], free[right_basis])
            need(correct == rotate(native, base, 2 * PHASE), "Tensor power uses p*f")
            need(correct != rotate(native, base, PHASE), "Copied width-1 integer disagrees")


def reject_source(word):
    trial = json.loads(json.dumps(word))
    trial["program"][EVENT][2] = (trial["program"][EVENT][2] + 1) % len(trial["frames"])
    try:
        walk(trial)
    except ValueError:
        return
    raise ValueError("Wrong source frame was accepted")


def main():
    need(digest(WORD) == WORD_SHA256, "Selected word bytes")
    need(digest(RESULT) == RESULT_SHA256, "Primary result bytes")
    need(digest(ARCHIVE) == ARCHIVE_SHA256, "PR5827 archive bytes")
    need(digest(CLIFFORD) == CLIFFORD_SHA256 and digest(NATIVE) == NATIVE_SHA256, "Vendor bytes")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    native_summary = result["native"]
    need(native_summary["proof"] == PROOF, "Registered proof sentence")
    need(native_summary["distinct_maps"] == 2922 and native_summary["main_adapters"] == 208,
         "Registered recipe census")
    need(native_summary["recipe_payload_sha256"] ==
         "e22642923d5437c49e2d1dc79dd6b795503499d6f33615a1df3568f0b96164c1",
         "Registered payload hash is recorded, not recomputed")
    inspect(primary_bytes())
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    walk(word)
    reject_source(word)
    witness(word)
    print(
        "PASS_PRIMARY_MOVE_PHASE_INTEGER"
        f" event={EVENT} frames={SOURCE}->{DESTINATION} phase={PHASE}"
        " bases=512 pairs=262144 joint_recipe=false"
    )


if __name__ == "__main__":
    main()
