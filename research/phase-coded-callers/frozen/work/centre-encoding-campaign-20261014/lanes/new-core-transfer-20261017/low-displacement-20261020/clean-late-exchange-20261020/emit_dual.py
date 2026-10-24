#!/usr/bin/env python3
"""Emit the inverse-adjoint clean word and its selected-role conjugate."""

import argparse
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PINS = {
    "producer": (HERE / "emit_clean_exchange.py",
                 "91ee4ce54a5774dfdec7ac0a83f78c5076ef14d0ee30f2dcc7ecf448b869ecbc"),
    "source": (HERE / "run-normal/CLEAN-LATE-EXCHANGE.json.gz",
               "b0432322c28ad3a03af8da550a0b7c7df048c7ff5a0664acc7f78efffcffd083"),
    "freeze": (HERE / "FREEZE.json",
               "96048355033e5f5bdd26dadddb869708faae6f8b0d9a61a1ae696e5a5c20c0bc"),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def read(name):
    path, pin = PINS[name]
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Pinned clean source " + name)
    return raw


read("producer")
spec = importlib.util.spec_from_file_location("clean_dual_base", PINS["producer"][0])
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
n = base.n


def conjugate(rows, permutation):
    result = [{} for _ in rows]
    for target, row in enumerate(rows):
        result[permutation[target]] = {permutation[source]: value
                                       for source, value in row.items()}
    return result


def expected_swap(code, response, selected):
    result = n.r.identity(640)
    for p in range(112):
        if p in selected:
            result[p] = {112 + j: value for j, value in code[p].items()}
            result[112 + p] = {p: F(-1)}
        else:
            n.r.add(result[p], {112 + p: F(-1)})
            for j in selected:
                value = response[p].get(j, F(0))
                if value:
                    n.r.add(result[p], {112 + j: value})
    return result


def lower(original, permutation):
    word = deepcopy(original)
    events = []
    for event in original["events"]:
        new = deepcopy(event)
        if event[0] == "native":
            new[1] = permutation[event[1]]
        else:
            need(event[0] == "scalar", "The complete source event grammar")
            op, target, source, raw = event[1]
            coefficient = F(raw)
            if op == "add":
                new[1] = [op, permutation[source], permutation[target], str(-coefficient)]
            else:
                need(op == "scale" and coefficient, "An invertible real scale")
                new[1] = [op, permutation[target], None, str(1 / coefficient)]
        events.append(new)
    word["events"] = events
    for key in ("start", "final"):
        word[key] = [original[key][permutation[p]] for p in range(640)]
        need(word[key] == original[key], "Selected endpoint frame symmetry")
    for record in word["input_views"]:
        record["field"] = permutation[record["field"]]
        record["role"] = "source" if record["field"] < 112 else "selected_target"
    word["input_views"].sort(key=lambda record: record["field"])
    input_by_field = {record["field"]: record for record in original["input_views"]}
    physical_keys = ("frame", "left", "right", "rank", "port")
    for record in word["input_views"]:
        old = input_by_field[record["field"]]
        need(all(record[key] == old[key] for key in physical_keys),
             "The complete same-port input adapter is invariant")
    for record in word["output_views"]:
        need(permutation[112 + record["port"]] == 112 + record["port"],
             "Every ordinary output adapter keeps its physical field")
    need(word["native_recipes"] == original["native_recipes"]
         and word["frames"] == original["frames"], "All native physical records are unchanged")
    word["wire_permutation"] = {str(p): q for p, q in enumerate(permutation) if p != q}
    word["scalar_rule"] = "Keep event order. Transpose each ADD and negate its coefficient. Invert each real SCALE."
    return word


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    read("freeze")
    source = json.loads(read("source"))
    for name in ("phase_review", "line_phase_review"):
        base.read(name)
    selected = set(source["selected_ports"])
    code, response = n.rows(source["code"]), n.rows(source["response"])
    direct = n.rows(source["content_map"])
    inverse = n.rows(source["inverse_content_map"])
    need(n.r.product(direct, inverse) == n.r.product(inverse, direct) == n.r.identity(224),
         "Both source content inverse orders")
    for p in range(112):
        if p in selected:
            need(code[p].get(p) == 1 and set(code[p]) & selected == {p},
                 "The exact normalized centre minor")
            continue
        row = {p: F(1)}
        for j in selected:
            d = response[p].get(j, F(0))
            need(d == -code[j].get(p, F(0)), "The actual D=-B transpose identity")
            n.r.add(row, code[j], d)
        need(row == response[p], "The actual ordinary response is u+D(a+Bu)")
    dual = n.r.transpose(inverse, 224)
    dual_inverse = n.r.transpose(direct, 224)
    need(n.r.product(dual, dual_inverse) == n.r.product(dual_inverse, dual) == n.r.identity(224),
         "Both inverse-adjoint content inverse orders")
    full_dual = dual + n.r.identity(640)[224:]
    identity_permutation = list(range(640))
    swap_permutation = list(identity_permutation)
    for p in selected:
        swap_permutation[p], swap_permutation[112 + p] = 112 + p, p
    swap = conjugate(full_dual, swap_permutation)
    need(swap == expected_swap(code, response, selected),
         "The direct Bswapclean block formula")
    swap_inverse = conjugate(dual_inverse, swap_permutation[:224])
    need(n.r.product(swap[:224], swap_inverse) == n.r.product(swap_inverse, swap[:224])
         == n.r.identity(224), "Both Bswapclean content inverse orders")
    providers, reports = {}, {}
    for provider, entries in source["providers"].items():
        original = entries["Q"]
        providers[provider], reports[provider] = {}, {}
        for name, permutation, expected in (
                ("inverse_adjoint", identity_permutation, full_dual),
                ("selected_swap_conjugate", swap_permutation, swap)):
            word = lower(original, permutation)
            report = base.verify(word, expected)
            need(report["real_scalar_primitives"] == 8600
                 and report["native_mass"] == 1792
                 and report["native_profile"] == {1: 1392, 2: 64, 3: 48, 8: 16},
                 "The full dual invoice")
            need(report["native_side_map_upper_bound"] == 3040
                 and report["explicit_input_monomial_views"] == 128
                 and report["explicit_output_monomial_views"] == 96,
                 "All actual adapter and wrapper counts")
            report["extra_boundary_swap_instructions"] = 0
            report["native_phase_records_unchanged"] = True
            report["selected_input_and_output_adapter_symmetry"] = True
            for stage in ("source_row_code", "signed_selected_exchanges"):
                bad = deepcopy(word)
                index = next(i for i in range(*word["stage_ranges"][stage])
                             if bad["events"][i][1][0] == "add")
                bad["events"][index][1][3] = str(-F(bad["events"][index][1][3]))
                try:
                    base.verify(bad, expected)
                except ValueError:
                    pass
                else:
                    raise ValueError("A wrong dual ADD sign was accepted")
            providers[provider][name], reports[provider][name] = word, report
    payload = {
        "schema": "clean-inverse-adjoint-selected-conjugate-v1",
        "source_pins": {name: {"path": str(path), "sha256": pin}
                        for name, (path, pin) in PINS.items()},
        "ports": source["ports"], "selected_ports": source["selected_ports"],
        "code": source["code"], "response": source["response"],
        "content_maps": {"inverse_adjoint": n.r.encoded(dual),
                         "selected_swap_conjugate": n.r.encoded(swap[:224])},
        "inverse_content_maps": {"inverse_adjoint": n.r.encoded(dual_inverse),
                                 "selected_swap_conjugate": n.r.encoded(swap_inverse)},
        "providers": providers,
        "physical_contract": {
            "input": "X=Q(a,u); Y_P=Q_P z; Y_U=v.",
            "inverse_adjoint_output_content": "X=(-z,u+D a-v); Y=(a+Bv,v).",
            "selected_swap_conjugate_output_content": "X=(z+Bv,u+D z-v); Y=(-a,v).",
            "output_frames": "All X and selected Y have F9; ordinary Y has F9 q_U.",
            "operators": "B is the normalized reader off-pivot block; D=-B^T, with actual real dyadic coefficients.",
            "scope": "Complete local physical inverse-adjoint and selected-role conjugate. A routed caller and its full supplier bill remain separate.",
        },
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for provider, words in saved["providers"].items():
        for name, word in words.items():
            expected = n.rows(saved["content_maps"][name]) + n.r.identity(640)[224:]
            report = base.verify(word, expected)
            need(all(value == reports[provider][name][key] for key, value in report.items()),
                 "The complete serialized dual replay")
    (args.out / "CLEAN-DUAL.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_EXACT_CLEAN_INVERSE_ADJOINT_AND_SELECTED_CONJUGATE",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "reports": reports, "all_content_inverse_orders": True,
        "actual_D_equals_negative_B_transpose": True,
        "negative_controls": "A wrong code or exchange ADD sign fails in all four words.",
        "native_phase_scope": "All native and endpoint spatial operators are unchanged unitary records from the reviewed Q-entry word. Each inverse-adjoint native operator equals itself.",
        "scope": payload["physical_contract"]["scope"],
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
