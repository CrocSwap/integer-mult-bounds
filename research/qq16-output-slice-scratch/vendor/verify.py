#!/usr/bin/env python3
"""Exact conditional rewrite of ywz65's PR2540 QQ16 decoder.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor code imported. Formal operators do not reprove native admission.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(value):
    # Distinguish JSON true, 1 and 1.0, which Python == does not.
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    raw = {}
    for item in manifest["pending_predecessor"]["files"]:
        data = (HERE / item["path"]).read_bytes()
        require(sha(data) == item["sha256"], "predecessor source hash: " + item["path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == item["git_blob"], "predecessor Git blob: " + item["path"])
        raw[item["path"]] = data
    for item in manifest["files"]:
        if item["usage"] == "input":
            require(sha((ROOT / item["path"]).read_bytes()) == item["sha256"], "live source hash: " + item["path"])
    return json.loads(raw["predecessor/WORD.json"]), json.loads(raw["predecessor/RESULT.json"])


def transform(old):
    """Require the precise capture/copy/retire layout, not a generic deletion."""
    require([i for i, e in enumerate(old) if e["op"] == "history_boundary"] == [32], "one temporal cut")
    selected, new, deleted = [], [], []
    for i in range(0, 32, 2):
        clear, add = old[i:i+2]
        require(clear["op"] == "clear" and clear["frame"] == "old", "capture clear")
        bank = clear["field"]
        require(bank.startswith("R") and bank[1:].isdigit(), "early bank")
        p = int(bank[1:])
        require(0 <= p < 112 and p not in selected, "distinct selected port")
        require(add == {"op": "add", "src": f"X{p}", "dst": bank, "coefficient": "1"}, "capture add")
        selected.append(p)
        new.extend([{"op": "clear", "field": f"Z{p}", "frame": "old"},
                    {"op": "add", "src": f"X{p}", "dst": f"Z{p}", "coefficient": "1"}])
    new.append({"op": "history_boundary", "name": "complete_B1_with_retained_Z_untouched"})
    for j, p in enumerate(selected):
        i = 33 + 3*j
        require(old[i:i+3] == [{"op": "clear", "field": f"Z{p}", "frame": "old"},
                {"op": "add", "dst": f"Z{p}", "src": f"R{p}", "coefficient": "1"},
                {"op": "stage", "field": f"Z{p}", "rank": 8, "sign": 1}], "copy/upgrade block")
        new.append(deepcopy(old[i+2])); deleted.extend([i, i+1])
    suffix = deepcopy(old[81:-16])
    require(all(not (isinstance(e.get(k), str) and e[k].startswith("R"))
                for e in suffix for k in ("field", "src", "dst")), "no suffix R access")
    require(old[-16:] == [{"op": "clear", "field": f"R{p}", "frame": "old"} for p in selected], "retirement")
    new.extend(suffix); deleted.extend(range(len(old)-16, len(old)))
    return new, selected, deleted


def atom(name):
    return {(name, ()): Q(1)}


def add_rows(a, b, q):
    out = dict(a)
    for key, v in b.items():
        out[key] = out.get(key, Q(0)) + q*v
        if not out[key]:
            del out[key]
    return out


def operate(row, letter, sign):
    # Application order is left-to-right in this stored list. Only adjacent
    # inverse pairs cancel. Different letters never commute.
    out = {}
    for (name, word), q in row.items():
        tail = word[:-1] if word and word[-1] == (letter, -sign) else word + ((letter, sign),)
        key = (name, tail)
        out[key] = out.get(key, Q(0)) + q
    return {key: q for key, q in out.items() if q}


def digest_rows(rows):
    data = [[bank, [[name, list(word), str(q)] for (name, word), q in sorted(row.items())]]
            for bank, row in sorted(rows.items())]
    return sha(canonical(data).encode())


def replay(word, selected, retained):
    """Independent physical-operator replay over 240 temporal input symbols.

    Coarse frame transitions use PR2540's contract. The current-map phase
    identity and actual native lowering remain predecessor obligations.
    """
    outputs = {f"{side}{p}" for side in ("Z", "W") for p in range(112)}
    early = {f"R{p}" for p in selected} if retained == "R" else set()
    owned = outputs | early
    rows = {name: atom("dirt:" + name) for name in owned}
    frames = {name: "identity" for name in owned}
    for p in selected:
        rows[f"X{p}"], frames[f"X{p}"] = atom(f"E{p}"), "old"
    active, boundary, peak, checkpoints = set(), False, 0, {}
    for i, e in enumerate(word):
        op = e["op"]
        if op == "history_boundary":
            require(not boundary and not active, "one history boundary")
            for p in selected:
                name = retained + str(p)
                require(rows[name] == rows[f"X{p}"] == atom(f"E{p}"), "early value at B1")
                require(frames[name] == "old", "early frame at B1")
            # B1 acts only on its inherited namespace; retention is a premise.
            for p in range(112):
                for side in ("X", "Y"):
                    name = f"{side}{p}"
                    rows[name] = atom(name)
                    frames[name] = "current" if side == "X" else ("Y-minus", p)
            boundary = True
        elif op == "private_begin":
            require(boundary and not active, "nonoverlapping private bodies")
            active = set(e["fields"])
            require(active.isdisjoint(owned | set(rows)), "private/output alias")
            peak = max(peak, len(active))
            for name in active:
                rows[name], frames[name] = atom("dirt:" + name), "identity"
        elif op == "private_end":
            require(active == set(e["fields"]), "private body names")
            require(all(not rows[n] and frames[n] == "identity" for n in active), "private cleanup")
            for name in active:
                del rows[name], frames[name]
            active = set()
        elif op == "clear":
            name = e["field"]
            require(name in owned | active, "clear only owned storage")
            require(e["frame"] in ("old", "current", "identity"), "clear frame")
            rows[name], frames[name] = {}, e["frame"]
        elif op == "add":
            src, dst = e["src"], e["dst"]
            require(src in rows and dst in owned | active and src != dst, "live distinct ADD roles")
            require(frames[src] == frames[dst], "ADD frames at " + str(i))
            rows[dst] = add_rows(rows[dst], rows[src], Q(e["coefficient"]))
        elif op == "stage":
            name = e["field"]
            require(boundary and not active and name in outputs, "stage ownership/time")
            require(e["rank"] == 8 and e["sign"] == 1 and frames[name] == "old", "old-to-current stage")
            frames[name] = "current"
            rows[name] = operate(rows[name], "stage8", 1)
        elif op == "line":
            name, p, sign = e["field"], e["port"], e["sign"]
            require(boundary and name == f"Y{p}" and sign in (-1, 1), "borrowed line role")
            before, after = (("Y-minus", p), "current") if sign == 1 else ("current", ("Y-minus", p))
            require(frames[name] == before, "line frame")
            frames[name] = after
            rows[name] = operate(rows[name], f"line{p}", sign)
        elif op == "current_map":
            name = e["field"]
            require(boundary and not active and name in outputs and frames[name] == "current", "map frame/sweep")
            require(type(e["inverse"]) is bool, "map orientation type")
            rows[name] = operate(rows[name], "map" + str(e["port"]), -1 if e["inverse"] else 1)
        elif op == "checkpoint":
            require(not active and all(frames[f"Z{p}"] == "current" for p in range(112)), "checkpoint frames")
            checkpoints[e["name"]] = digest_rows({f"Z{p}": rows[f"Z{p}"] for p in range(112)})
        else:
            raise ValueError("unknown operation: " + op)
    require(boundary and not active, "completed word")
    require(all(frames[n] == "current" for n in outputs), "final output frames")
    require(all(not n.startswith("dirt:") for bank in outputs for n, _ in rows[bank]), "output dirt independence")
    for p in range(112):
        for side in ("X", "Y"):
            name = f"{side}{p}"
            require(rows[name] == atom(name), "borrowed source restoration")
            require(frames[name] == ("current" if side == "X" else ("Y-minus", p)), "borrowed source frames")
    require(all(not rows[n] and frames[n] == "old" for n in early), "R retirement")
    return {n: rows[n] for n in outputs}, checkpoints, peak


def invoice(word):
    counts = Counter(e["op"] for e in word)
    adds = Counter(str(abs(Q(e["coefficient"]))) for e in word if e["op"] == "add")
    require(set(adds) == {"1", "1/4"}, "scalar alphabet")
    names = {e[k] for e in word for k in ("field", "src", "dst") if k in e}
    banks = {n for n in names if n[0] in "RZW" and n[1:].isdigit()}
    return {"events": len(word), "owned_full_cover_bank_identities": len(banks),
            "unit_ADDs": adds["1"], "quarter_ADDs": adds["1/4"],
            "CLEARs": counts["clear"], "scalar_primitives": 8*adds["1"]+12*adds["1/4"]+2*counts["clear"],
            "rank_one_children": counts["line"], "rank_eight_children": counts["stage"],
            "native_rank_mass": counts["line"]+8*counts["stage"],
            "native_wrappers": 2*(counts["line"]+counts["stage"]), "full_cover_maps": counts["current_map"]}


def controls(word, selected, expected, expected_cuts):
    passed = []
    def reject(label, mutation):
        bad = deepcopy(word); mutation(bad)
        try:
            rows, cuts, _ = replay(bad, selected, "Z")
            require(rows == expected and cuts == expected_cuts, "changed formal operator")
        except (ValueError, KeyError):
            passed.append(label)
        else:
            raise ValueError("ineffective control: " + label)
    def at(w, op, **fields):
        return next(e for e in w if e["op"] == op and all(e.get(k) == v for k, v in fields.items()))
    reject("capture_after_B1", lambda w: w.insert(0, w.pop(32)))
    reject("wrong_capture_source", lambda w: w[1].update(src="X7"))
    reject("wrong_capture_sign", lambda w: w[1].update(coefficient="-1"))
    reject("capture_without_clear", lambda w: w.pop(0))
    reject("borrowed_input_alias", lambda w: w[0].update(field="X0"))
    reject("wrong_capture_frame", lambda w: w[0].update(frame="current"))
    reject("upgrade_missing", lambda w: w.remove(at(w, "stage")))
    reject("clear_retained_after_B1", lambda w: w.insert(33, {"op": "clear", "field": "Z0", "frame": "old"}))
    reject("retirement_destroys_output", lambda w: w.append({"op": "clear", "field": "Z0", "frame": "old"}))
    reject("wrong_native_map", lambda w: at(w, "current_map").update(port=2))
    reject("wrong_map_inverse", lambda w: at(w, "current_map", inverse=True).update(inverse=False))
    reject("borrowed_Y_not_restored", lambda w: w.remove(at(w, "line", sign=-1)))
    reject("wrong_F0_inverse_sign", lambda w: at(w, "add", dst="F0", src="G0").update(coefficient="1"))
    reject("uncleared_Y_output", lambda w: w.remove(at(w, "clear", field="W0")))
    reject("private_scratch_not_cleaned", lambda w: w.remove(at(w, "clear", field="G7", frame="identity")))
    return passed


def calculate():
    old, source_result = load_inputs()
    new, selected, deleted = transform(old)
    a, a_cuts, a_peak = replay(old, selected, "R")
    b, b_cuts, b_peak = replay(new, selected, "Z")
    require(a == b and a_cuts == b_cuts, "all outputs/checkpoints agree")
    require(a_peak == b_peak == 16, "local scratch peak")
    old_bill, new_bill = invoice(old), invoice(new)
    recorded = source_result["invoice"]
    require(old_bill["scalar_primitives"] == recorded["scalar_real_primitive_allowance"] == 17472, "old scalar bill")
    require(old_bill["unit_ADDs"] == recorded["absolute_ADD_coefficients"]["1"] == 856, "old unit ADDs")
    require(old_bill["quarter_ADDs"] == recorded["absolute_ADD_coefficients"]["1/4"] == 832, "old quarter ADDs")
    for k in ("CLEARs", "native_rank_mass", "native_wrappers", "rank_one_children", "rank_eight_children", "full_cover_maps"):
        require(old_bill[k] == recorded[k], "old invoice " + k)
    require((new_bill["unit_ADDs"], new_bill["CLEARs"], new_bill["scalar_primitives"]) == (840, 288, 17280), "new bill")
    native = lambda w: [e for e in w if e["op"] in ("stage", "line", "current_map")]
    require(native(old) == native(new), "literal native events unchanged")
    require(new[49:] == old[81:-16], "literal common suffix unchanged")
    passed = controls(new, selected, a, a_cuts)
    receipt = {"status": "PASS_QQ16_OUTPUT_BANK_RETENTION",
        "predecessor_head": "630d557af5088f66b45c447969cee9576600e50b",
        "selected_ports": selected, "old_invoice": old_bill, "new_invoice": new_bill,
        "deleted_predecessor_event_indices": deleted,
        "unchanged_native_events": len(native(new)), "identical_common_suffix_events": len(new[49:]),
        "owned_full_cover_banks": {"predecessor": old_bill["owned_full_cover_bank_identities"],
                                  "coalesced": new_bill["owned_full_cover_bank_identities"]},
        "retained_values_across_B1": 16, "peak_local_owned_scratch_arrays": b_peak,
        "output_arrays_compared": len(b), "restored_borrowed_arrays": 224,
        "temporal_source_symbols": 240, "formal_output_operator_sha256": digest_rows(b),
        "formal_checkpoint_sha256": b_cuts, "semantic_controls": passed,
        "scope": "Conditional rewrite; native realization and original-input inverse inherited from PR2540. No hosting, minimum storage theorem, supplier or kappa claim."}
    return new, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="create absent receipt only")
    args = parser.parse_args()
    word, result = calculate()
    require(canonical(json.loads((HERE / "WORD.json").read_text())) == canonical(word), "candidate WORD differs")
    path = HERE / "RESULT.json"
    if args.write:
        with path.open("x") as out:
            out.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(canonical(json.loads(path.read_text())) == canonical(result), "complete typed RESULT differs")
    print(result["status"], "banks=240->224 scalar=17472->17280 native_mass=352",
          "outputs=224 borrowed=224 controls=" + str(len(result["semantic_controls"])), "no_new_kappa")


if __name__ == "__main__":
    main()
