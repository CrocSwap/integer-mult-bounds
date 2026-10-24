#!/usr/bin/env python3
"""Instantiate the retained finite-precompilation contract for p19.

The contract is compositional: each emitted gate consumes and returns the
inherited all-column primitive interface, and the finite word links those
interfaces chronologically.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(name):
    if name.endswith('.gz'):
        import gzip
        return json.loads(gzip.decompress((HERE / name).read_bytes()))
    return json.loads((HERE / name).read_text())


def main():
    word = read("P19_WORD.json")
    lift = read("P19_LIFT.json")
    units = read("P19_UNITS.json")
    low = read("P19_LOWERING.json")
    bridge = read("P19_BRIDGE.json")
    diag = read("P19_DIAGCENSUS.json")
    claim = read("P19_CLAIM.json")
    macro = read("P19_NATIVE_MACRO.json.gz")
    macro_replay = read("P19_NATIVE_MACRO_REPLAY.json")
    forward_program = read("P19_FORWARD_PROGRAM.json")
    reverse_program = read("P19_REVERSE_PROGRAM.json")
    macro_resources = read("P19_MACRO_RESOURCES.json")
    gates = Counter(word["gate_kinds"])
    p19 = units["cases"]["p19_IIIIIIIIITTTTTTTTT"]
    d19 = diag["cases"]["p19_IIIIIIIIITTTTTTTTT"]

    primitive_contract = {
        "all_column": "not established by this probe",
        "arbitrary_inputs": "symbolic inputs only",
        "owned_scratch": "not executed by the macro replay",
        "owned_erasure": "not executed by the macro replay",
        "fixed_precision_interface": "not established by this probe",
        "source": "research/coded-native-caller/PHYSICAL.md",
        "source_sha256": hashlib.sha256(
            (ROOT / "research/coded-native-caller/PHYSICAL.md").read_bytes()
        ).hexdigest(),
    }
    need(word["gate_records"] == 259, "p19 word gate count")
    need(word["p"] == 19 and word["stages"] == 39, "p19 dimensions")
    need(lift["status"] == "PASS_LIFTING_LEMMA", "operator lift")
    need(low["status"] == "PASS_PRIMITIVE_SPEC_BINDING", "primitive binding")
    need(units["status"] == "PASS_UNIT_COMPOSITION_AND_ENDPOINT_TYPING", "unit contract")
    need(bridge["status"] == "PASS_ADAPTERS_ARE_PART_OF_THE_INHERITED_UNIT", "adapter unit")
    need(p19["loads"] == p19["unloads"] == p19["swaps"] == 19, "terminal closure")
    need(p19["terminal"]["swap_sign"] == -1, "swap sign")
    need(p19["terminal"]["recursive_gaussian_children"] == 0, "recursive children")
    need(d19["census_equals_invoice"] is True, "diagonal census")
    need(claim["field_level_bill"]["recodings"] == 77, "recoding bill")
    need(claim["field_level_bill"]["recursive_gaussian_children"] == 0, "claim children")
    need(macro["status"] == "PASS_P19_TYPED_NATIVE_MACRO_EMISSION", "typed native macro emission")
    need(macro_replay["status"] == "PASS_P19_NATIVE_MACRO_REPLAY", "typed native macro replay")
    need(forward_program["status"] == "PASS_LITERAL_FORWARD_QUERY_PROGRAM", "literal forward program")
    need(reverse_program["status"] == "PASS_LITERAL_REVERSE_LETTER_PROGRAM", "literal reverse program")
    need(macro_resources["status"] == "PASS_P19_MACRO_RESOURCE_ACCOUNTING", "macro resources")
    need(macro["gate_records"] == macro["macro_records"] == 259, "macro cardinality")
    need(macro_replay["events"] == 259, "macro replay cardinality")
    need(macro["compiled_wrapper_contract"]["all_wrappers_gaussian_free"],
         "compiled normalizer wrappers")
    need(macro["compiled_wrapper_contract"]["ports"] == 112,
         "all inherited port wrappers")
    need(gates == Counter({
        "BRIDGE": 108,
        "FORWARD": 20,
        "GAUGE_LOAD": 19,
        "GAUGE_UNLOAD": 19,
        "IDLE": 36,
        "LETTER": 19,
        "REVERSE": 19,
        "SWAP": 19,
    }), "gate vocabulary/counts")

    out = {
        "status": "FINDING_PRECOMPILATION_CONTRACT_MISSING",
        "theorem": "research/direct-mixed-flow/vendor/FINITE-PRECOMPILATION.md",
        "theorem_scope": "finite chronological composition under inherited native hypotheses",
        "new_p19_condition": True,
        "primitive_contract": primitive_contract,
        "word": {
            "gates": word["gate_records"],
            "ambient_rank": 153,
            "gate_kinds": dict(sorted(gates.items())),
        },
        "chronology": {
            "initial_gauges": 19,
            "final_unloads": 19,
            "signed_swaps": 19,
            "bridges": gates["BRIDGE"],
            "idles": gates["IDLE"],
            "operator_link": "P19_LIFT.json",
            "primitive_link": "P19_LOWERING.json",
            "endpoint_link": "P19_UNITS.json",
        },
        "whole_job_adapters": {
            "per_direction": 448,
            "bracketed_middle_retained": True,
            "link": "P19_BRIDGE.json",
        },
        "paid_work": claim["field_level_bill"],
        "targets": {
            "source": "P19_DIAGCENSUS.json",
            "equals_invoice": d19["census_equals_invoice"],
        },
        "proof_boundary": {
            "native_event_encoding": "typed finite macro contract over inherited PHYSICAL.md primitives",
            "frozen_program_replay": "inherited base evidence",
            "p19_specific_event_encoder": "P19_NATIVE_MACRO.json.gz",
            "macro_replay": "P19_NATIVE_MACRO_REPLAY.json",
            "missing": [
                "the complete p19 macro still requires the inherited finite native interface",
                "literal forward/reverse programs are checked as formal owned-work macros, not serialized native records",
            ],
        },
    }
    (HERE / "P19_PRECOMPILATION.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(out["status"])
    print(json.dumps({"status": out["status"], "new_p19_condition": out["new_p19_condition"]}, sort_keys=True))


if __name__ == "__main__":
    main()
