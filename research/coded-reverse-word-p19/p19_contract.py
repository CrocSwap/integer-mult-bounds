#!/usr/bin/env python3
"""Typed all-column contract for the existing p19 primitive word.

This is the finite-precompilation interface: it checks the chronological
primitive word, code-state transitions, owned recoding work, endpoint return,
and binds the universal operator/census receipts. It does not reinterpret the
opaque frozen 21,449-record payload.
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


def load(name):
    return json.loads((HERE / name).read_text())


def main():
    word = load("P19_WORD.json")
    lift = load("P19_LIFT.json")
    units = load("P19_UNITS.json")
    lowering = load("P19_LOWERING.json")
    diagonal = load("P19_DIAGCENSUS.json")
    claim = load("P19_CLAIM.json")
    state = load("P19_STATE_TRACE.json")
    gates = []
    # The emitted listing is regenerated from the source constructor, not copied.
    import sys
    sys.path.insert(0, str(HERE))
    import p19_word as W
    gates = W.native_chain(19, "I" * 9 + "T" * 9)

    coded = [False] * 38
    counts = Counter()
    chronology = []
    for index, gate in enumerate(gates):
        kind = gate[0]
        counts[kind] += 1
        roles = [x for x in gate[1:] if isinstance(x, int) and 0 <= x < 38]
        if kind == "GAUGE_LOAD":
            role = gate[1]
            need(role % 2 == 1 and not coded[role], f"load state at {index}")
            coded[role] = True
        elif kind == "GAUGE_UNLOAD":
            role = gate[1]
            need(role % 2 == 1 and coded[role], f"unload state at {index}")
            coded[role] = False
        elif kind == "FORWARD":
            x, y = gate[1:3]
            need(x % 2 == 0 and y == x + 1, f"forward pair at {index}")
            need(coded[x] is False and coded[y] is True, f"forward gauge state at {index}")
        elif kind == "REVERSE":
            x, y = gate[1:3]
            need(x % 2 == 0 and y == x + 1, f"reverse pair at {index}")
            need(coded[x] is False and coded[y] is True, f"reverse gauge state at {index}")
        elif kind == "LETTER":
            x, y = gate[1:3]
            need(x % 2 == 0 and y == x + 1, f"letter pair at {index}")
            need(coded[x] is False and coded[y] is True, f"letter gauge state at {index}")
        elif kind == "IDLE":
            x, y = gate[1:3]
            need(x % 2 == 0 and y == x + 1, f"idle pair at {index}")
            need(gate[3] > 0, f"idle exponent at {index}")
        elif kind == "BRIDGE":
            src, dst = gate[1:3]
            need(src != dst and 0 <= src < 38 and 0 <= dst < 38, f"bridge endpoints at {index}")
            need(abs(src - dst) in (2, 3), f"bridge adjacency at {index}")
            need(gate[3] in (-1, 1), f"bridge coefficient at {index}")
            need(coded[src] == coded[dst], f"bridge gauge state at {index}")
        elif kind == "SWAP":
            x, y = gate[1:3]
            need(x % 2 == 0 and y == x + 1 and gate[3] == -1, f"swap at {index}")
        else:
            raise ValueError(f"unknown gate {kind}")
        chronology.append({"index": index, "kind": kind, "roles": roles, "coded": tuple(coded)})

    need(all(not x for x in coded), "final code state")
    need(dict(counts) == word["gate_kinds"], "emitted gate counts")
    need(word["gate_records"] == len(gates) == 259, "emitted gate count")
    need(lowering["status"] == "PASS_PRIMITIVE_SPEC_BINDING", "primitive contract")
    need(lift["status"] == "PASS_LIFTING_LEMMA", "all-width operator lift")
    need(units["status"] == "PASS_UNIT_COMPOSITION_AND_ENDPOINT_TYPING", "endpoint contract")
    need(diagonal["cases"]["p19_IIIIIIIIITTTTTTTTT"]["census_equals_invoice"] is True,
         "diagonal target census")
    need(claim["field_level_bill"]["recodings"] == 77, "recoding bill")
    need(claim["field_level_bill"]["owned_clears"] == 1232, "owned clear bill")
    need(state["status"] == "PASS_P19_SYMBOLIC_DIRTY_STATE_TRACE", "symbolic state trace")
    need(state["final_code_state"] == "all uncoded", "state trace final code")
    need(state["owned_scratch"]["final"] == "blank", "state trace scratch")
    out = {
        "status": "PASS_P19_TYPED_PRIMITIVE_CONTRACT",
        "theorem": "research/direct-mixed-flow/vendor/FINITE-PRECOMPILATION.md",
        "new_p19_condition": True,
        "word": {"gates": len(gates), "ambient_rank": 153, "gate_kinds": dict(sorted(counts.items()))},
        "all_column_contract": {
            "operator": "P19_LIFT.json",
            "primitive": "P19_LOWERING.json",
            "arbitrary_input": "symbolic dirty-input rows",
            "owned_scratch": "symbolic lifetime trace",
            "owned_erasure": "symbolic final blank check",
            "chronological_links": len(chronology) - 1,
            "final_code_state": "all uncoded",
        },
        "endpoint": {"units": 19, "standard_denominators": [1], "coded_denominators": [1, 13], "swap_sign": -1},
        "paid_work": claim["field_level_bill"],
        "census": "P19_DIAGCENSUS.json equals inherited invoice",
        "source_contract": {
            "path": "research/coded-native-caller/PHYSICAL.md",
            "sha256": hashlib.sha256((ROOT / "research/coded-native-caller/PHYSICAL.md").read_bytes()).hexdigest(),
        },
        "scope": "typed primitive state contract with symbolic dirty-input trace; native event lowering remains inherited",
        "missing": [
            "producer event lowering or equivalent source theorem",
        ],
    }
    (HERE / "P19_CONTRACT.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("FINDING_P19_NATIVE_STATE_CONTRACT_MISSING")
    print(json.dumps({"status": out["status"], "new_p19_condition": out["new_p19_condition"]}, sort_keys=True))


if __name__ == "__main__":
    main()
