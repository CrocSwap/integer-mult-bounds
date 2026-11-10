#!/usr/bin/env python3
"""The one-weight proof admits no second after-cover equal to the PR5679 component.

Authenticate the controller's single writer and the retained bridge's separate
C1 assignment before any Fraction arithmetic. The selected ordinary formula is
then shown to miss that component on every cover the positive-gap hypothesis
allows. This does not search for a prime, run the outer ledger, or change kappa.
"""
from fractions import Fraction
import ast
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Q = Fraction

CONTROLLER_RESULT = "research/query-thinned-controllers/RESULT.json"
CONTROLLER_VERIFY = "research/query-thinned-controllers/verify.py"
CONTROLLER_PROOF = "research/query-thinned-controllers/PROOF.md"
CONTROLLER_SOURCES = "research/query-thinned-controllers/SOURCES.json"
CONTROLLER_CODE = "research/query-thinned-controllers/controller.py"
PRICING = "research/p104-helper470-twin-rung-removal/pricing.py"
COMPONENT = "research/g20-helper-split/ORDINARY-RESULT.json"
BRIDGE_JSON = "research/kappa-rebuild/bit/BIT-ALLSIZE-PARAMETERS.json"
BRIDGE_PROSE = "research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md"
BRIDGE_WRITER = "research/kappa-rebuild/bit/bit_allsize_parameters.py"
CLAIM = "certificates/frontier6030/CLAIM.json"
SELECTED = "certificates/selected-result.json"

ONE_WEIGHT = "Keep one external cover weight throughout the entire finite BIT compilation"
C1_SENTENCE = "Use C0=0.003459 before covering and C1=0.00345"
GAP_PHRASE = "exceeds 256/(C0-C1)*N^5"
WRITER = "before, after, atom, old = Q('.003459'), Q('.00345'), Q('.004'), Q('.0000384599')"
GAP_NEED = "need(before > after and atom > ordinary > admitted and atom < 1-ordinary, 'Complete ordinary BIT conversion')"
PRIME_NEED = "need(Q('.003') < ordinary and 2**26 > 256/(before-after), 'Old atom rejected and finite prime bound')"
FORMULA = "ordinary=(1-atom)*Q(bit['after_cover'])+atom*Q('.0000384599')"
READER = "bit = L.read(L.ROOT/'research/query-thinned-controllers/RESULT.json')['ordinary_BIT']"
ATOM_LINE = "atom = Q(bit['atom'])"
ADMITTED_LINE = "admitted=Q(bit['admitted'])"
BRIDGE_ASSIGNMENT = "before,after=Q(69,25000),Q(11,4000)"
BRIDGE_GAP = "B.need(gap==Q(1,100000) and before>after>0,'Strict precompile-to-cover gap')"
BRIDGE_SENTENCE = "C1=11/4000=0.00275"
EMITTED_SPELLING = '"after_cover": "69/20000"'
RETAINED_BRIDGE_INPUTS = (BRIDGE_JSON, BRIDGE_PROSE)


def need(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


class Authenticated:
    """Spellings checked against pinned bytes. Arithmetic must receive this."""

    def __init__(self, spellings):
        self.authenticated = True
        self.spellings = spellings


def git_blob_sha1(raw):
    header = b"blob " + str(len(raw)).encode("ascii") + b"\0"
    return hashlib.sha1(header + raw).hexdigest()


def bind_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    files = {}
    seen = []
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = row["path"]
        raw = (ROOT / path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "sha256 pin " + path)
        need(git_blob_sha1(raw) == row["git_blob"], "git blob pin " + path)
        need(b"\0" not in raw, "source is text " + path)
        files[path] = raw.decode("utf-8")
        seen.append(path)
    need(len(seen) == len(set(seen)), "duplicate source pin")
    required = {
        CONTROLLER_RESULT, CONTROLLER_VERIFY, CONTROLLER_PROOF, CONTROLLER_SOURCES,
        CONTROLLER_CODE, PRICING, COMPONENT, BRIDGE_JSON, BRIDGE_PROSE, BRIDGE_WRITER,
        CLAIM, SELECTED,
    }
    need(required <= set(seen), "missing second-cover input")
    return files


def walk_keys(value, key, prefix="$"):
    found = []
    if isinstance(value, dict):
        for name, child in value.items():
            path = prefix + "." + name
            if name == key:
                found.append((path, child))
            found.extend(walk_keys(child, key, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(walk_keys(child, key, prefix + "[" + str(index) + "]"))
    return found


def tuple_assignments(source, names):
    tree = ast.parse(source)
    matches = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Tuple):
            continue
        if not all(isinstance(item, ast.Name) for item in target.elts):
            continue
        got = [item.id for item in target.elts]
        if got == names:
            matches.append(ast.get_source_segment(source, node))
    return matches


def name_assignments(source, name):
    tree = ast.parse(source)
    matches = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == name:
            matches.append(ast.get_source_segment(source, node))
    return matches


def authenticate(files):
    """Name both source assignments. No rational arithmetic in this function."""
    proof = files[CONTROLLER_PROOF]
    verify = files[CONTROLLER_VERIFY]
    result = files[CONTROLLER_RESULT]
    code = files[CONTROLLER_CODE]
    pricing = files[PRICING]
    bridge_json_text = files[BRIDGE_JSON]
    bridge_prose = files[BRIDGE_PROSE]
    bridge_writer = files[BRIDGE_WRITER]
    component_text = files[COMPONENT]
    claim_text = files[CLAIM]
    selected_text = files[SELECTED]
    controller_sources = json.loads(files[CONTROLLER_SOURCES])

    need(proof.count(ONE_WEIGHT) == 1, "one external cover-weight sentence")
    need(proof.count(C1_SENTENCE) == 1, "one controller C1 sentence")
    need(proof.count("C1=") == 1, "one C1 literal in the controller proof")
    need(proof.count(GAP_PHRASE) == 1, "one positive-gap prime comparison")
    need("11/4000" not in proof and BRIDGE_SENTENCE not in proof,
         "the bridge weight is not copied into the controller C1 sentence")

    writers = tuple_assignments(verify, ["before", "after", "atom", "old"])
    need(writers == [WRITER], "one controller cover assignment")
    need(verify.count(WRITER) == 1, "writer text occurs once")
    need(verify.count("'after_cover'") == 1, "controller writes one after_cover key")
    need(verify.count(GAP_NEED) == 1, "one strict before-after gate")
    need(verify.count(PRIME_NEED) == 1, "one numerical prime-coefficient comparison")
    need("11/4000" not in verify, "controller verifier does not assign the bridge weight")

    need(result.count(EMITTED_SPELLING) == 1, "one raw after_cover spelling")
    need(result.count('"after_cover"') == 1, "one after_cover key in the controller receipt")
    receipt = json.loads(result)
    found = walk_keys(receipt, "after_cover")
    need(len(found) == 1 and found[0] == ("$.ordinary_BIT.after_cover", "69/20000"),
         "parsed controller after_cover")
    bit = receipt["ordinary_BIT"]
    need(bit["before_cover"] == "3459/1000000", "controller before-cover spelling")
    need(bit["atom"] == "1/250", "controller atom spelling")
    need(bit["admitted"] == "17/5000", "controller admitted spelling")
    need("odd q > 2^26*N^5" in bit["prime_rule"], "prime rule is recorded, not evaluated")
    need("after_cover" not in code and "11/4000" not in code and ".00345" not in code,
         "controller.py does not assign a cover weight")

    retained = {row["path"]: row["usage"] for row in controller_sources["files"]}
    for path in RETAINED_BRIDGE_INPUTS:
        need(retained.get(path) == "input", "controller package retains " + path)
    need(BRIDGE_WRITER not in retained, "controller pins the bridge receipt, not its writer script")

    need(bridge_prose.count(BRIDGE_SENTENCE) == 1, "one bridge C1 sentence")
    need('"after_cover"' not in bridge_prose and "'after_cover'" not in bridge_prose,
         "bridge prose does not name the formula key")
    bridge_writers = tuple_assignments(bridge_writer, ["before", "after"])
    need(bridge_writers == [BRIDGE_ASSIGNMENT], "one bridge after-cover assignment")
    need(bridge_writer.count(BRIDGE_ASSIGNMENT) == 1, "bridge assignment text occurs once")
    need(bridge_writer.count(BRIDGE_GAP) == 1, "bridge gap predicate")
    need(bridge_writer.count("'C1_after_cover'") == 2, "bridge stores and prints C1_after_cover")
    need("'after_cover'" not in bridge_writer and '"after_cover"' not in bridge_writer,
         "bridge writer does not store the formula key")
    bridge = json.loads(bridge_json_text)
    need(walk_keys(bridge, "after_cover") == [], "bridge receipt has no after_cover key")
    bridge_covers = walk_keys(bridge, "C1_after_cover")
    need(bridge_covers == [("$." + "C1_after_cover", "11/4000")], "bridge C1_after_cover spelling")
    need(bridge["C0_before_cover"] == "69/25000", "bridge before-cover is not the controller C0")
    need(bridge["C0_minus_C1"] == "1/100000", "bridge's own gap spelling")
    need(bridge_json_text.count('"after_cover"') == 0, "bridge receipt text has no after_cover key")
    need(bridge_json_text.count('"C1_after_cover"') == 1, "one bridge C1_after_cover key")

    need(pricing.count(FORMULA) == 1, "one selected ordinary formula")
    need(pricing.count(READER) == 1, "formula reads the thinned-controller receipt")
    need(pricing.count(ATOM_LINE) == 1 and pricing.count(ADMITTED_LINE) == 1, "atom and admitted reads")
    need(name_assignments(pricing, "ordinary") == [FORMULA], "formula AST")
    need(name_assignments(pricing, "admitted") == [ADMITTED_LINE], "admitted is not ordinary")
    need(pricing.count("'bit_saving':admitted") == 1, "bit_saving is the name admitted")
    need("ordinary_saving" not in pricing and "C1_after_cover" not in pricing,
         "pricing does not read a stored ordinary or the bridge weight")
    need("kappa-rebuild/bit" not in pricing, "pricing does not read the bridge")

    component = json.loads(component_text)
    claim = json.loads(claim_text)
    selected = json.loads(selected_text)
    need(component["admitted"] == "3507410738409/1000000000000000", "recorded PR5679 component spelling")
    need(component["whole_kappa"] is None, "component receipt claims no whole kappa")
    need(claim["kappa"] == selected["kappa"] == "781451/250000000", "selected kappa spelling")
    need(selected["decimal"] == "0.003125804", "selected decimal spelling")
    need(claim["ordinary_BIT_saving"] == "8590884599/2500000000000", "selected ordinary spelling")

    return Authenticated({
        "emitted": bit["after_cover"],
        "before": bit["before_cover"],
        "atom": bit["atom"],
        "admitted": bit["admitted"],
        "bridge": bridge["C1_after_cover"],
        "bridge_before": bridge["C0_before_cover"],
        "component": component["admitted"],
        "claim_ordinary": claim["ordinary_BIT_saving"],
        "kappa": claim["kappa"],
        "texts": files,
    })


def ordinary(atom, cover, epsilon):
    return (1 - atom) * cover + atom * epsilon


def absent_token(text, token):
    return re.search(r"(?<![0-9])" + re.escape(token) + r"(?![0-9])", text) is None


def arithmetic(bound):
    need(isinstance(bound, Authenticated) and bound.authenticated is True,
         "source binding is required before arithmetic")
    spell = bound.spellings
    atom = Q(spell["atom"])
    epsilon = Q("0.0000384599")
    emitted = Q(spell["emitted"])
    before = Q(spell["before"])
    bridge = Q(spell["bridge"])
    bridge_before = Q(spell["bridge_before"])
    recorded = Q(spell["component"])
    need(atom == Q(1, 250) and epsilon == Q(384599, 10000000000), "atom and epsilon")
    need(emitted == Q("0.00345") == Q(69, 20000), "emitted cover agrees with the writer literal")
    need(before == Q("0.003459") == Q(3459, 1000000), "controller C0")
    need(bridge == Q(11, 4000) == Q("0.00275"), "bridge assignment agrees with its receipt")
    need(bridge_before == Q(69, 25000) and bridge_before != before, "bridge C0 is a different weight")
    need(before > emitted > bridge > 0, "both named covers sit strictly below controller C0")
    need(before - emitted == Q(9, 1000000), "controller gap")

    slope = 1 - atom
    need(slope == Q(249, 250) and slope > 0, "ordinary is strictly increasing in the cover")
    at_emitted = ordinary(atom, emitted, epsilon)
    at_before = ordinary(atom, before, epsilon)
    at_bridge = ordinary(atom, bridge, epsilon)
    need(at_emitted == Q(spell["claim_ordinary"]) == Q(8590884599, 2500000000000),
         "ordinary at the emitted cover reproduces the selected claim")
    need(at_before == Q(8613294599, 2500000000000), "ordinary at controller C0")
    need(at_bridge == Q(6847884599, 2500000000000), "ordinary at the bridge weight")
    need(at_bridge < at_emitted < at_before, "the two named covers sit below the C0 image")

    preimage = (recorded - atom * epsilon) / slope
    need(preimage == Q(3507256898809, 996000000000000), "reduced preimage")
    need(ordinary(atom, preimage, epsilon) == recorded, "preimage reproduces the component")
    need(preimage > before, "the preimage is not strictly below C0")
    need(before - preimage == Q(-62092898809, 996000000000000), "negative gap at the preimage")
    need(recorded - at_before == slope * (preimage - before) == Q(62092898809, 1000000000000000),
         "component stays above ordinary at C0")
    need(recorded - at_emitted == slope * (preimage - emitted) == Q(71056898809, 1000000000000000),
         "component stays above ordinary at the emitted cover")
    need(at_before < recorded and at_emitted < recorded and at_bridge < recorded,
         "C0, the emitted cover, and the bridge weight all miss the component")

    def misses(cover):
        need(cover < before, "gap-feasible covers are strictly below C0")
        image = ordinary(atom, cover, epsilon)
        need(image < at_before < recorded, "a gap-feasible cover stays strictly below the component")
        return image

    need(misses(emitted) == at_emitted and misses(bridge) == at_bridge,
         "both named assignments are gap-feasible and miss the component")
    try:
        misses(preimage)
    except SystemExit as exc:
        need(str(exc) == "FAIL: gap-feasible covers are strictly below C0",
             "the preimage is rejected by the gap hypothesis")
    else:
        need(False, "the preimage was treated as gap-feasible")
    need(2**26 > 256 / (before - emitted), "kept positive gap meets the recorded coefficient comparison")
    need(before - preimage < 0, "the same comparison has no positive denominator at the preimage")

    preimage_token = str(preimage.numerator)
    for path, body in spell["texts"].items():
        need(absent_token(body, preimage_token), "preimage numerator is not a source constant in " + path)
        need(str(preimage) not in body, "preimage fraction is not written in " + path)

    return {
        "status": "PASS_G20_SECOND_AFTER_COVER_OBSTRUCTION",
        "claim_type": "scoped-proof",
        "kappa": spell["kappa"],
        "kappa_changed": False,
        "ledger_executed": False,
        "controller_replayed": False,
        "prime_searched": False,
        "odd_prime_avoidance_executed": False,
        "admission_verdict": "not claimed",
        "bit_saving_expression": "admitted",
        "admitted_BIT": spell["admitted"],
        "hypotheses": [
            "one external cover-weight sentence",
            "one controller C1 sentence C1=0.00345",
            "one writer of after_cover from that C1",
            "before > after, so every kept cover is strictly below 3459/1000000",
        ],
        "controller_after_cover": str(emitted),
        "bridge_C1_after_cover": str(bridge),
        "bridge_key_is_after_cover": False,
        "second_after_cover_assignment_named": "research/kappa-rebuild/bit/bit_allsize_parameters.py",
        "controller_C0": str(before),
        "slope": str(slope),
        "ordinary_at_emitted_cover": str(at_emitted),
        "ordinary_at_controller_C0": str(at_before),
        "ordinary_at_bridge_weight": str(at_bridge),
        "pr5679_component": str(recorded),
        "component_minus_ordinary_at_C0": str(recorded - at_before),
        "unique_preimage": str(preimage),
        "preimage_below_C0": False,
        "positive_gap_at_preimage": False,
        "every_gap_feasible_cover_misses_component": True,
        "domain": "all rationals strictly below the controller C0; proved by a positive slope, not enumerated",
    }


def reject(label, callback):
    try:
        callback()
    except SystemExit as exc:
        need(str(exc).startswith("FAIL:"), label + " did not fail closed")
        return
    need(False, label + " returned")


def controls(files):
    reject("unbound arithmetic", lambda: arithmetic(object()))

    second_key = dict(files)
    second_key[CONTROLLER_RESULT] = files[CONTROLLER_RESULT].replace(
        EMITTED_SPELLING,
        EMITTED_SPELLING + ', "nested": {"after_cover": "11/4000"}',
        1,
    )
    need(second_key[CONTROLLER_RESULT] != files[CONTROLLER_RESULT], "second-key mutation")
    reject("second after_cover key", lambda: authenticate(second_key))

    renamed = dict(files)
    renamed[BRIDGE_JSON] = files[BRIDGE_JSON].replace('"C1_after_cover"', '"after_cover"', 1)
    need('"after_cover"' in renamed[BRIDGE_JSON], "renamed bridge key")
    reject("bridge weight stored as after_cover", lambda: authenticate(renamed))

    duplicated = dict(files)
    duplicated[CONTROLLER_PROOF] = files[CONTROLLER_PROOF].replace(
        C1_SENTENCE, C1_SENTENCE + "\n" + C1_SENTENCE, 1)
    reject("second C1 sentence", lambda: authenticate(duplicated))

    second_writer = dict(files)
    second_writer[CONTROLLER_VERIFY] = files[CONTROLLER_VERIFY].replace(
        WRITER, WRITER + "\n    " + WRITER, 1)
    reject("second controller writer", lambda: authenticate(second_writer))


def main():
    files = bind_sources()
    controls(files)
    bound = authenticate(files)
    receipt = arithmetic(bound)
    print("PASS_G20_SECOND_AFTER_COVER_OBSTRUCTION")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
