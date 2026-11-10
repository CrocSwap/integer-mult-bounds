#!/usr/bin/env python3
"""Census the thinned controller's after-cover against the selected ordinary formula.

Authenticate the pinned bytes first. Only then evaluate

    ordinary = (1 - atom) * after_cover + atom * epsilon

on the covers the controller actually emits. The recorded PR5679 component is
the target value. This does not run the outer ledger, admit that component as
BIT, or change kappa.
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
CONTROLLER_WORD = "research/query-thinned-controllers/BIT-CONTROLLER.json"
CONTROLLER_CODE = "research/query-thinned-controllers/controller.py"
PRICING = "research/p104-helper470-twin-rung-removal/pricing.py"
COMPONENT = "research/g20-helper-split/ORDINARY-RESULT.json"
COMPONENT_SOURCE = "research/g20-helper-split/ordinary.py"
LATER = "research/g20-conjugation-admission/ORDINARY-RESULT.json"
CLAIM = "certificates/frontier6030/CLAIM.json"
SELECTED = "certificates/selected-result.json"

EMITTED_SPELLING = '"after_cover": "69/20000"'
WRITER = "before, after, atom, old = Q('.003459'), Q('.00345'), Q('.004'), Q('.0000384599')"
FORMULA = "ordinary=(1-atom)*Q(bit['after_cover'])+atom*Q('.0000384599')"
ONE_WEIGHT = "Keep one external cover weight throughout the entire finite BIT compilation"
C1_SENTENCE = "Use C0=0.003459 before covering and C1=0.00345"
READER = "bit = L.read(L.ROOT/'research/query-thinned-controllers/RESULT.json')['ordinary_BIT']"
ATOM_LINE = "atom = Q(bit['atom'])"
ADMITTED_LINE = "admitted=Q(bit['admitted'])"
GATE_LINE = "L.need(atom > ordinary > admitted > TESTED and atom < 1-ordinary, 'Retained BIT admission and stock')"
FOREIGN_LITERALS = (
    "tested=F('.00350741073843');uniform=F('.00350741073842');"
    "cover_gap=F(1,10**14);rho=F(1,100);"
)


def need(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


class SourceBound:
    """Bytes authenticated against SOURCES.json. Arithmetic must receive this."""

    def __init__(self, files):
        self.authenticated = True
        self.files = files


def git_blob_sha1(raw):
    header = b"blob " + str(len(raw)).encode("ascii") + b"\0"
    return hashlib.sha1(header + raw).hexdigest()


def bind_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    files = {}
    seen = []
    for row in manifest["files"]:
        path = row["path"]
        raw = (ROOT / path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "sha256 pin " + path)
        need(git_blob_sha1(raw) == row["git_blob"], "git blob pin " + path)
        need(b"\0" not in raw, "source is text " + path)
        files[path] = raw.decode("utf-8")
        seen.append(path)
    need(len(seen) == len(set(seen)), "duplicate source pin")
    required = {
        CONTROLLER_RESULT, CONTROLLER_VERIFY, CONTROLLER_PROOF, CONTROLLER_WORD,
        CONTROLLER_CODE, PRICING, COMPONENT, COMPONENT_SOURCE, LATER, CLAIM, SELECTED,
    }
    need(required <= set(seen), "missing cover-census input")
    return SourceBound(files)


def text_of(bound, path):
    need(isinstance(bound, SourceBound) and bound.authenticated is True,
         "source binding is required before arithmetic")
    return bound.files[path]


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


def require_emitted_singleton(result_text):
    need(result_text.count(EMITTED_SPELLING) == 1, "one raw after_cover spelling")
    need(result_text.count('"after_cover"') == 1, "one after_cover key in the receipt text")
    receipt = json.loads(result_text)
    found = walk_keys(receipt, "after_cover")
    need(len(found) == 1 and found[0][0] == "$.ordinary_BIT.after_cover",
         "parsed after_cover is the ordinary_BIT field")
    need(found[0][1] == "69/20000", "emitted after_cover spelling")
    return receipt


def selected_ordinary(atom, after_cover, epsilon):
    return (1 - atom) * after_cover + atom * epsilon


def assignment_segment(source, names):
    tree = ast.parse(source)
    matches = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Tuple):
            continue
        got = [item.id for item in target.elts if isinstance(item, ast.Name)]
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
            matches.append((node, ast.get_source_segment(source, node)))
    return matches


def bit_saving_name(pricing):
    tree = ast.parse(pricing)
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
            continue
        for key, value in zip(node.value.keys, node.value.values):
            if isinstance(key, ast.Constant) and key.value == "bit_saving":
                found.append(value)
    need(len(found) == 1 and isinstance(found[0], ast.Name) and found[0].id == "admitted",
         "pricing bit_saving is the name admitted")
    need(pricing.count("'bit_saving':admitted") == 1, "one bit_saving admitted entry")
    need(pricing.count("bit_saving=Q('.0027')") == 1, "insufficient-BIT literal is a different call")


def absent_token(text, token):
    return re.search(r"(?<![0-9])" + re.escape(token) + r"(?![0-9])", text) is None


def census_and_arithmetic(bound):
    result_text = text_of(bound, CONTROLLER_RESULT)
    verify_text = text_of(bound, CONTROLLER_VERIFY)
    proof_text = text_of(bound, CONTROLLER_PROOF)
    word_text = text_of(bound, CONTROLLER_WORD)
    code_text = text_of(bound, CONTROLLER_CODE)
    pricing = text_of(bound, PRICING)
    component_text = text_of(bound, COMPONENT)
    foreign_text = text_of(bound, COMPONENT_SOURCE)
    later_text = text_of(bound, LATER)
    claim_text = text_of(bound, CLAIM)
    selected_text = text_of(bound, SELECTED)

    receipt = require_emitted_singleton(result_text)
    bit = receipt["ordinary_BIT"]
    need(bit["atom"] == "1/250", "one atom field")
    need(bit["before_cover"] == "3459/1000000", "one before-cover field")
    need(bit["admitted"] == "17/5000", "recorded admitted BIT")
    need(bit["ordinary_saving"] == "8590884599/2500000000000", "recorded controller ordinary")
    need(result_text.count('"before_cover"') == 1, "one before_cover key")
    need("odd q > 2^26*N^5" in bit["prime_rule"], "prime rule is recorded, not evaluated here")

    writers = assignment_segment(verify_text, ["before", "after", "atom", "old"])
    need(writers == [WRITER], "one controller cover assignment")
    need(verify_text.count(WRITER) == 1, "writer text occurs once")
    need(verify_text.count("'after_cover'") == 1, "controller writes one after_cover key")
    ordinary_writer = assignment_segment(verify_text, ["ordinary", "admitted"])
    need(ordinary_writer == ["ordinary, admitted = (1-atom)*after+atom*old, Q('.0034')"],
         "controller ordinary uses the assigned after value")

    need(proof_text.count(ONE_WEIGHT) == 1, "one external cover-weight sentence")
    need(proof_text.count(C1_SENTENCE) == 1, "one C1 sentence")
    need("C1=0.00346" not in proof_text and proof_text.count("C1=") == 1, "no second C1 literal")

    need("after_cover" not in code_text and "69/20000" not in code_text and ".00345" not in code_text,
         "controller.py does not emit a cover weight")
    word = json.loads(word_text)
    need(word["kind"] == "bit", "physical controller is the BIT word")
    need(walk_keys(word, "after_cover") == [] and walk_keys(word, "before_cover") == [],
         "physical word has no cover field")
    need("69/20000" not in word_text and ".00345" not in word_text, "physical word has no cover literal")

    need(pricing.count(FORMULA) == 1, "one selected ordinary formula")
    need(pricing.count(READER) == 1, "formula reads the thinned-controller receipt")
    need(pricing.count(ATOM_LINE) == 1 and pricing.count(ADMITTED_LINE) == 1, "atom and admitted reads")
    need(pricing.count(GATE_LINE) == 1, "stock gate reads the recomputed ordinary")
    need("ordinary_saving" not in pricing, "pricing does not read the stored ordinary_saving")
    need("g20-helper-split" not in pricing and "g20-conjugation-admission" not in pricing,
         "component sources are not formula inputs")
    formula_nodes = name_assignments(pricing, "ordinary")
    need(len(formula_nodes) == 1 and formula_nodes[0][1] == FORMULA, "formula AST")
    admitted_nodes = name_assignments(pricing, "admitted")
    need(len(admitted_nodes) == 1 and admitted_nodes[0][1] == ADMITTED_LINE,
         "admitted is not assigned from ordinary")
    bit_saving_name(pricing)

    claim = json.loads(claim_text)
    selected = json.loads(selected_text)
    need(claim["kappa"] == selected["kappa"] == "781451/250000000", "selected kappa pin")
    need(selected["decimal"] == "0.003125804", "selected decimal pin")
    families = {row["family"]: row["saving"] for row in claim["uniform_templates"]}
    need(families == {"complex": "10940329/3500000000", "BIT before cover": "3459/1000000"},
         "claim templates are complex and the before-cover only")

    component = json.loads(component_text)
    later = json.loads(later_text)
    need(component["status"] == "PASS_CONDITIONAL_G20_HELPER_SPLIT_ORDINARY_FIVE_FINITE_LEVELS",
         "PR5679 ordinary status")
    need(later["status"] == "PASS_CONDITIONAL_G20_CONJUGATION_ORDINARY_FIVE_FINITE_LEVELS",
         "PR5708 ordinary status")
    need(component["whole_kappa"] is None and later["whole_kappa"] is None,
         "neither component receipt claims a whole kappa")
    need(component["admitted"] == component["finite_backend_levels"][-1]["admitted"]
         == "3507410738409/1000000000000000", "recorded PR5679 component")
    need(later["admitted"] == later["finite_backend_levels"][-1]["admitted"]
         == "3507719059749/1000000000000000", "recorded PR5708 component")
    need(FOREIGN_LITERALS in foreign_text and foreign_text.count("C1=uniform-cover_gap") == 1,
         "PR5679 source cover literals")
    need(foreign_text.count("a=(1-rho)*C1+rho*backend") == 1, "PR5679 uses rho, not the selected atom")

    atom = Q(bit["atom"])
    epsilon = Q(".0000384599")
    emitted = Q(bit["after_cover"])
    before = Q(bit["before_cover"])
    need(atom == Q(1, 250) and epsilon == Q(384599, 10000000000), "pinned atom and epsilon")
    need(emitted == Q(".00345") == Q(69, 20000), "emitted cover agrees with the writer literal")
    need(before == Q(".003459") == Q(3459, 1000000), "before-cover agrees with C0")
    slope = 1 - atom
    need(slope == Q(249, 250) and slope > 0, "ordinary is strictly increasing in the cover")

    ordinary = selected_ordinary(atom, emitted, epsilon)
    need(ordinary == Q(claim["ordinary_BIT_saving"]) == Q(bit["ordinary_saving"]),
         "recomputed ordinary matches the claim and the controller receipt")
    recorded = Q(component["admitted"])
    preimage = (recorded - atom * epsilon) / slope
    need(selected_ordinary(atom, preimage, epsilon) == recorded, "preimage reproduces the component")
    need(preimage == Q(3507256898809, 996000000000000), "reduced preimage")
    need(preimage != emitted, "emitted cover is not the preimage")
    need(selected_ordinary(atom, emitted, epsilon) != recorded, "emitted cover misses the component")
    gap = recorded - ordinary
    need(gap == slope * (preimage - emitted) == Q(71056898809, 1000000000000000) and gap > 0,
         "exact gap between the component and ordinary at the emitted cover")

    domain = {emitted}
    need(preimage not in domain, "no emitted cover has ordinary equal to the component")
    need(all(selected_ordinary(atom, cover, epsilon) != recorded for cover in domain),
         "singleton image misses the component")

    before_image = selected_ordinary(atom, before, epsilon)
    need(before != emitted and before != preimage and before_image != recorded and before_image != ordinary,
         "the before-cover weight is not an after-cover and misses the component")
    need(selected_ordinary(atom, emitted, Q(0)) != ordinary, "dropping epsilon changes ordinary")
    neighbor = preimage + Q(1, preimage.denominator)
    need(selected_ordinary(atom, neighbor, epsilon) != recorded, "a different cover misses the component")

    foreign = Q("0.00350741073842") - Q(1, 10**14)
    need(foreign == Q(component["C1"]) == Q(350741073841, 100000000000000), "PR5679 receipt C1")
    later_cover = Q(later["C1"])
    later_component = Q(later["admitted"])
    later_preimage = (later_component - atom * epsilon) / slope
    need(later_preimage == Q(3507565220149, 996000000000000), "PR5708 preimage")
    for outside in (foreign, later_cover, later_preimage):
        need(outside != emitted and outside != preimage, "outside cover is not emitted and is not this preimage")
        need(selected_ordinary(atom, outside, epsilon) != recorded,
             "substituting an outside cover does not make ordinary equal the PR5679 component")
    need(later_component != recorded and later_preimage != preimage, "the two components do not share a preimage")

    preimage_token = str(preimage.numerator)
    fraction_token = str(preimage)
    for path in (CONTROLLER_RESULT, CONTROLLER_VERIFY, CONTROLLER_PROOF, CONTROLLER_WORD,
                 CONTROLLER_CODE, PRICING, CLAIM, SELECTED, COMPONENT, COMPONENT_SOURCE, LATER):
        body = text_of(bound, path)
        need(absent_token(body, preimage_token), "preimage numerator is not a source constant in " + path)
        need(fraction_token not in body, "preimage fraction is not written in " + path)

    return {
        "status": "PASS_G20_SOURCE_BOUND_COVER_CENSUS",
        "claim_type": "exhaustive-finite-census",
        "kappa": claim["kappa"],
        "kappa_changed": False,
        "ledger_executed": False,
        "admission_verdict": "not claimed",
        "bit_saving_expression": "admitted",
        "admitted_BIT": bit["admitted"],
        "atom": str(atom),
        "epsilon": str(epsilon),
        "emitted_after_covers": [str(emitted)],
        "census_size": 1,
        "selected_ordinary": str(ordinary),
        "pr5679_component": str(recorded),
        "component_minus_ordinary": str(gap),
        "unique_preimage": str(preimage),
        "preimage_emitted": False,
        "before_cover_is_after_cover": False,
        "pr5679_source_C1": str(foreign),
        "pr5708_source_C1": str(later_cover),
        "pr5708_preimage": str(later_preimage),
        "outside_covers_in_census": False,
        "prime_rule_evaluated_at_preimage": False,
    }


def reject(label, callback):
    try:
        callback()
    except SystemExit as exc:
        need(str(exc).startswith("FAIL:"), label + " did not fail closed")
        return
    need(False, label + " returned")


def controls(bound):
    reject("unbound arithmetic", lambda: census_and_arithmetic(object()))

    original = text_of(bound, CONTROLLER_RESULT)
    nested = original.replace(
        EMITTED_SPELLING,
        EMITTED_SPELLING + ', "nested": {"after_cover": "1/2"}',
        1,
    )
    need(nested != original, "nested mutation changes the receipt")
    reject("second nested after_cover", lambda: require_emitted_singleton(nested))

    duplicate = original.replace(
        EMITTED_SPELLING,
        '"after_cover": "1/3", ' + EMITTED_SPELLING,
        1,
    )
    need(duplicate.count('"after_cover"') == 2, "duplicate-key mutation")
    reject("duplicate after_cover key", lambda: require_emitted_singleton(duplicate))


def main():
    bound = bind_sources()
    controls(bound)
    receipt = census_and_arithmetic(bound)
    print("PASS_G20_SOURCE_BOUND_COVER_CENSUS")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
