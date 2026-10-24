#!/usr/bin/env python3
"""Bind explicit forward/dual warp recipes to emitted PR2339 programs.

Finite exact local check, not global hosting or an exponent certificate.
Uses PR2269's independently decoded Gaussian products; the child compiler is
not imported. Apache-2.0; prepared with substantial OpenAI Codex assistance.
"""
import copy
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

if not __debug__:
    raise RuntimeError("assertions must remain enabled")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "anticipatory-stage-evidence/interface/pr2269"))
import bw_gauss as g


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def conjugate(recipe):
    """Monomial inverse-transpose is conjugation; quadratic signs are mod 2."""
    out = copy.deepcopy(recipe)
    out["phase"] = (-out["phase"]) % 4
    out["linear_Z4"] = [(-x) % 4 for x in out["linear_Z4"]]
    return out


def main(local):
    c = read(local / "CANONICAL-WORD.json.gz")
    programs = read(local / "LOCAL-PROGRAMS.json.gz")
    compiled = read(local / "CLIFFORD-RECIPES.json")
    warps = {w["op"]: w for w in c["warps"]}
    recipes = {(w["sign"], w["op"], w["old"], w["new"]): w for w in compiled["warps"]}
    need(len(recipes) == 112, "four-alias warp class count changed")
    output = []; rejected = []
    for key, r in sorted(recipes.items()):
        sign, op, old, new = key
        need(r["rank"] == 0 and r["right"] is None, "paid warp")
        z = g.warp_product(warps[op]["G_columns"], c["frames"][old], c["frames"][new], sign * op, c["h"])
        for orientation in ("forward", "backward"):
            m = r["left"] if orientation == "forward" else conjugate(r["left"])
            expected = z if orientation == "forward" else (z[0], -z[1], z[2])
            need(g.equal_scaled(expected, g.recipe_matrix(m, c["h"])), f"wrong {orientation} recipe {key}")
            bad = copy.deepcopy(m); bad["phase"] = (bad["phase"] + 1) % 4
            need(not g.equal_scaled(expected, g.recipe_matrix(bad, c["h"])), "phase mutation accepted")
            rejected.append([orientation, *key])
            output.append(dict(orientation=orientation, sign=sign, op=op, old=old, new=new, rank=0, monomial=m))
    by = {}
    for orientation, events in programs.items():
        phase = None; counts = Counter(); used = set(); peak = 0; live = set()
        for e in events:
            if e[0] == "phase": phase = e[1]
            elif e[0] == "warp":
                key = (1 if e[2] > 0 else -1, abs(e[2]), e[3], e[4])
                need(key in recipes, "missing emitted recipe")
                counts[phase] += 1; used.add(key)
                if phase == "zero_frame_precondition":
                    need(e[3:] == [0, 0] and c["start"][e[1][1]] == 0, "compensation reads a nonzero entrance")
            elif e[0] == "zero_buffer":
                need(phase == "full_frame_cleanup", "zero buffer outside cleanup")
                if e[1] == "alloc":
                    need(e[2] not in live, "duplicate buffer"); live.add(e[2]); peak = max(peak, len(live))
                else:
                    need(e[2] in live, "unallocated buffer"); live.remove(e[2])
        need(not live and peak == 76, "buffer inventory changed")
        need(used == set(recipes), "warp recipe inventory mismatch")
        need(dict(counts) == {"A": 8, "B": 52, "full_frame_cleanup": 52}, "warp event count changed")
        by[orientation] = dict(warp_events_by_phase=dict(counts), warp_classes=len(used), peak_zero_buffers=peak)
    h = c["local_profile"]
    widths = Counter(len(c["frames"][c["final"][r]]) - len(c["frames"][c["start"][r]]) for r in range(2*c["v"], 2*c["v"]+c["R"]))
    need(widths == {4: 36, 5: 4, 7: 36, 8: 112, 9: 240}, "helper widths changed")
    need(sum(int(r)*n for r,n in h.items()) == 5328, "paid mass changed")
    need(sum(w*n for w,n in widths.items()) == 3472, "helper width sum changed")
    payload = json.dumps(output, sort_keys=True, separators=(",", ":")).encode()
    (local / "ORIENTED-WARP-RECIPES.json.gz").write_bytes(gzip.compress(payload, mtime=0))
    report = dict(status="PASS_EXPLICIT_FORWARD_DUAL_WARP_RECIPES", orientations=by,
                  recipe_records=len(output), columns_per_record=512,
                  wrong_global_phase_controls_rejected=len(rejected),
                  paid_profile=h, paid_mass=5328, helper_width_inventory=dict(sorted(widths.items())),
                  helper_width_sum=3472, helpers=428,
                  canonical_content_sha256=hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",", ":")).encode()).hexdigest(),
                  oriented_recipe_content_sha256=hashlib.sha256(payload).hexdigest(),
                  scope="Exact finite local monomial recipes for both orientations; inverse-transpose is entrywise conjugation for unitary monomials. Hosting, physical reserve, outer recurrence, source-access and all-size analytic transfer remain separate.")
    (local / "ORIENTATION-CONTRACT.json").write_text(json.dumps(report, indent=2)+"\n")
    print(report["status"], "224 recipes, 512 columns each, 224 phase mutations rejected")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
