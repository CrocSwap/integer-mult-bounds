#!/usr/bin/env python3
"""The in-repo HPE checkers do not read the pre-wrapper recipe.

Synthetic word only. This does not rerun Lean, the external HPE replay, or a supplier.
"""
import copy
import importlib.util
import inspect
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BIND_PATH = ROOT / "scripts/verify_hpe_lean_binding.py"
INST_PATH = ROOT / "research/hyperplane-end-lean/code/check_hpe_pairs.py"
LABELS = ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Labels.lean"
EXACT = ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Exact.lean"

LEMMA = (
    "Let (N) hold for a certified pair (E, U): "
    "T_U T_E^{-1} = L (C_7 ⊗ id) R, with C_7 invertible. "
    "If the pre-wrapper that ran executed R'^{-1}, then "
    "L^{-1} T_U T_E^{-1} R'^{-1} = C_7 ⊗ id if and only if R' = R. "
    "A FULL recipe fails this equality when it differs from R."
)


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture(pairs):
    keys = list(pairs)
    require(len(keys) == 3, "expected the three Lean pairs")
    frames = [list(rows) for key in keys for rows in key]
    slots = ((0, 1), (2, 3), (4, 5))
    counts = (24, 8, 6)
    start = [0] * 200
    final = [0] * 200
    tail = []
    recipes = {}
    recorded = []
    pre = []
    helper = 0
    for count, (entrance, terminal), key in zip(counts, slots, keys, strict=True):
        recipes[f"{entrance}:{terminal}"] = {
            "rank": 7,
            "left": pairs[key]["left"],
            "right": pairs[key]["right"],
        }
        recorded.append({"frame": entrance, "terminal": terminal, "residual_width": 7})
        for _ in range(count):
            start[helper] = entrance
            final[helper] = terminal
            tail.append(["add", helper, 100 + helper, -1, 1, terminal])
            pre.append({"helper": helper, "recipe": f"{entrance}:FULL"})
            helper += 1
    word = {
        "frames": frames,
        "start": start,
        "final": final,
        "tail": tail,
        "cleanup": [],
        "pre_wrappers": pre,
    }
    wrap = {
        "status": "PASS_RESIDUAL_WRAPPERS_ARE_EXACT",
        "hyperplane_end_pairs": recorded,
    }
    return word, {"recipes": recipes}, wrap


def main():
    labels = LABELS.read_text(encoding="utf-8")
    exact = EXACT.read_text(encoding="utf-8")
    require("pre wrapper decoded against the FULL recipe" in labels, "factor_iff_pre text moved")
    require("theorem factor_iff_pre" in labels, "missing factor_iff_pre")
    require("(hrec : RecipesExact (Text T ent term Lw Rw) rec" in exact, "hpe_word_exact lost hrec")
    require("The exact factorization is no longer a hypothesis" in exact, "hpe_word_exact text moved")
    readme = (PACKAGE / "README.md").read_text(encoding="utf-8")
    require(LEMMA in readme, "README dropped the boundary lemma")

    bind = load(BIND_PATH, "hpe_bind")
    inst = load(INST_PATH, "hpe_inst")
    require("pre_wrappers" not in inspect.getsource(bind.check), "binding checker now reads pre_wrappers")
    require("pre_wrappers" not in inspect.getsource(inst.check), "instance checker now reads pre_wrappers")
    pairs = bind.literal_pairs()
    require(set(pairs) == inst.LEAN_PAIRS, "the two checkers disagree on the Lean pairs")

    word, adapters, wrap = fixture(pairs)
    require({row["recipe"] for row in word["pre_wrappers"]} == {"0:FULL", "2:FULL", "4:FULL"},
            "fixture did not name FULL recipes")
    violations, helpers, found = inst.check(word, wrap)
    require(violations == [] and len(helpers) == 38 and len(found) == 3, "instance checker saw the FULL names")
    bind.check(word, adapters, pairs)

    omitted = copy.deepcopy(word)
    del omitted["pre_wrappers"]
    violations, _, _ = inst.check(omitted, wrap)
    require(violations == [], "instance checker requires a pre-wrapper record")
    bind.check(omitted, adapters, pairs)

    phased = copy.deepcopy(adapters)
    phased["recipes"]["0:1"]["left"]["phase"] ^= 1
    try:
        bind.check(word, phased, pairs)
    except ValueError as exc:
        require("Emitted recipe differs from Lean: left" in str(exc), "unexpected phase failure")
    else:
        raise SystemExit("phase mutation accepted")

    flipped = copy.deepcopy(word)
    flipped["tail"][0][3] = 1
    violations, _, _ = inst.check(flipped, wrap)
    require(violations, "instance checker accepted h += p")
    try:
        bind.check(flipped, adapters, pairs)
    except ValueError as exc:
        require("Tail is not h -= p" in str(exc), "unexpected coefficient failure")
    else:
        raise SystemExit("binding checker accepted h += p")

    print("PASS_HPE_PREWRAPPER_BINDING full_recipe_accepted=true "
          "record_optional=true phase_rejected=true coefficient_rejected=true pairs=3")


if __name__ == "__main__":
    main()
