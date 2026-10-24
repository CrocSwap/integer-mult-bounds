"""Restrict the literal DATA charts to two fresh stage blocks."""

from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def need(ok, label):
    if not ok:
        raise ValueError(label)


def main():
    path = HERE / "check_matched_access.py"
    spec = importlib.util.spec_from_file_location("matched_stage_source", path)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    base, ports, data = source.load()
    unit = [1 << j for j in range(25)]
    mask = (1 << 25) - 1
    entries = []
    counts = {"entry": 0, "exit": 0, "future_Y": 0, "past_X": 0,
              "orthogonal_routes": 0, "omitted_entry_translation": 0,
              "omitted_exit_translation": 0}
    views = {(v["stage"], v["port"], v["side"]): v for v in data["views"]["views"]}
    for p, recipe in enumerate(ports):
        q = recipe["q"]
        for s in range(3):
            full_rho = list(base.UNIT) if s == 0 else views[s, p, "X"]["route_columns"]
            need(all(v <= mask for v in full_rho[:25]) and full_rho[25:] == base.UNIT[25:],
                 "The literal route acts only on the 25-axis space")
            rho = full_rho[:25]
            need(all((a & b).bit_count() % 2 == int(i == j)
                     for i, a in enumerate(rho) for j, b in enumerate(rho)), "O(25,2) membership")
            need([base.act(rho, v) for v in rho] == unit and base.act(rho, q) == q,
                 "Route involution and intrinsic line")
            counts["orthogonal_routes"] += 1
            align = recipe["stage_alignment"][s]
            need(all(v <= mask for v in align.values()), "All literal translations restrict")
            record = {"port": p, "stage": s, "q": q, "route_columns": rho,
                      "literal_stage_alignment": align}
            for side in ("X", "Y"):
                before = ([(q, 1)] if side == "X" else []) if s == 0 else [(v, 1) for v in unit[:9 + 8 * (s - 1)]]
                if s and side == "Y":
                    before.append((q, -1))
                body = base.product([(base.act(rho, v), power) for v, power in before])
                delta = base.act(rho, align["entry_" + side])
                actual = base.add_phase(body, base.line(delta, 2))
                expected_terms = [(v, 1) for v in unit[9:9 + 8 * s]]
                if side == "X":
                    expected_terms.append((q, 1))
                expected = base.product(expected_terms)
                need(actual == expected, "Exact current native entry including exterior")
                counts["entry"] += 1
                counts["omitted_entry_translation"] += body != expected
                after = [(v, 1) for v in unit[:9 + 8 * s]]
                if side == "Y":
                    after.append((q, -1))
                body = base.product([(base.act(rho, v), power) for v, power in after])
                actual = base.add_phase(body, base.line(align["exit_" + side], 2))
                expected = base.product(after)
                need(actual == expected, "Exact declared output endpoint")
                counts["exit"] += 1
                counts["omitted_exit_translation"] += body != expected
            if s:
                for level in range(s):
                    terms = [(base.act(rho, v), 1) for v in unit[:9 + 8 * level]] + [(q, -1)]
                    actual = base.add_phase(base.product(terms), base.line(views[s, p, "Y"]["translation_after_route"], 2))
                    axes = unit[9:9 + 8 * level] + unit[9 + 8 * (s - 1):9 + 8 * s]
                    need(actual == base.product([(v, 1) for v in axes]), "Future-Y common exterior")
                    counts["future_Y"] += 1
            for level in range(s, 3):
                actual = base.product([(base.act(rho, v), 1) for v in unit[:9 + 8 * level]])
                delta = 0 if s == 0 else views[s, p, "X"]["translation_after_route"]
                actual = base.add_phase(actual, base.line(delta, 2))
                need(actual == base.product([(v, 1) for v in unit[:9 + 8 * level]]), "Past-X common exterior")
                counts["past_X"] += 1
            entries.append(record)
    need(counts["entry"] == counts["exit"] == 672, "All local boundary types")
    need(counts["future_Y"] == 336 and counts["past_X"] == 672, "All three-stage access cones")
    witness = json.loads((HERE / "CHECKS.json").read_bytes())["witness"]
    need(all(v <= mask for v in witness["route_columns"][:25])
         and witness["route_columns"][25:] == base.UNIT[25:], "Terminal witness restricts")
    need(max(witness["lines"]) <= mask and witness["FULL_translation"] <= mask,
         "The two-line phase witness has no discarded spectator")
    program = {"schema": "matched-dimension25-views-v1", "dimension": 25, "data_fields": 224,
               "stages": [0, 1, 2], "source_pins": source.PINS, "entries": entries,
               "owner_contract": "Use the regular O(25,2) cover. Complete each data-only local cover sweep before the next stage.",
               "native_word_claimed": False, "recursive_hosting_claimed": False}
    (HERE / "DIMENSION25-VIEWS.json").write_text(json.dumps(program, sort_keys=True, indent=2) + "\n")
    receipt = {"status": "PASS_LITERAL_DIMENSION25_STAGE_RESTRICTION", "source_pins": source.PINS,
               "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(), "checks": counts,
               "current_Y_at_B1": {"E2": "future scalar view admitted", "E0": "old mixed-line view; not admitted as a free scalar gauge"},
               "initial_all_I": "Every routed scalar matrix is a monomial-view scalar gauge",
               "terminal_upper_witness": {k: witness[k] for k in ("target", "middle", "source", "coefficient", "lines", "FULL_translation")},
               "scope": "Literal chart, endpoint, cover, and access restriction. Local native words and complete supplier admission are separate."}
    (HERE / "DIMENSION25-CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
