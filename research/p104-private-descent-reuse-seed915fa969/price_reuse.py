#!/usr/bin/env python3
"""Price the reused-helper word under the pinned selected-result screen."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(os.environ.get("P104_REPLAY_ROOT", Path(__file__).resolve().parents[2])).resolve()


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location("p104_private_reuse_" + name, path)
    if spec is None or spec.loader is None:
        raise ValueError("cannot load " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    fanout = load("fanout", ROOT / "research/p104-interleaved-search/fanout.py")
    budget = load("budget", ROOT / "research/p104-interleaved-search/budget.py")
    natural = load("natural_budget", ROOT / "research/p104-interleaved-search/natural_budget.py")
    report = fanout.construct(reuse_helper=7)["report"]
    engine, _, _, stock = budget.load_inputs()
    public = natural.integers(report["candidate_public_profile"])
    private = natural.integers(report["private_COPY_profile"])
    require(private == {1: 2, 2: 1, 3: 1, 7: 7}, "reused private path invoice")
    profile = budget.changed(public, private)
    expected = {1: 2611, 2: 513, 3: 378, 4: 132, 5: 81, 6: 15, 7: 13}
    require(profile == expected, "combined profile differs from scalar replay")
    require(budget.mass(profile) == 5885, "combined local rank mass")
    width = budget.Q(budget.FAMILIES, budget.STAGES)
    coverage_mass = (budget.M - 1) * width + budget.CENTRE
    model = engine.model(profile, budget.M, budget.FAMILIES, budget.STAGES, budget.CENTRE)
    require(model["local_mass"] + model["idle_mass"] == coverage_mass,
            "complete local and idle coverage mass")
    zero = engine.relax(profile, budget.M, budget.FAMILIES, budget.STAGES,
                        budget.CENTRE, budget.Q(0))
    require(zero[0] <= coverage_mass / (budget.M * width) <= zero[1],
            "zero-saving coverage moment")
    root = engine.ceiling(profile, budget.M, budget.FAMILIES,
                          budget.STAGES, budget.CENTRE)
    require(engine.relax(profile, budget.M, budget.FAMILIES, budget.STAGES,
                         budget.CENTRE, root[0])[1] < 1,
            "lower saving-root bracket")
    require(engine.relax(profile, budget.M, budget.FAMILIES, budget.STAGES,
                         budget.CENTRE, root[1])[0] > 1,
            "upper saving-root bracket")
    selected_a = budget.SELECTED_KAPPA / (1 - budget.SELECTED_KAPPA)
    selected_moment = engine.relax(profile, budget.M, budget.FAMILIES,
                                    budget.STAGES, budget.CENTRE, selected_a)
    require(selected_moment[0] > 1, "selected threshold remains excluded")
    complex_cap = root[1] / (1 + root[1])
    bit_cap = budget.BIT_LOWER / (1 + budget.BIT_LOWER)
    cap = min(complex_cap, bit_cap)
    require(cap < budget.SELECTED_KAPPA, "screen no longer rejects selected kappa")

    inputs = {
        name: {"path": path, "sha256": digest}
        for name, (path, digest) in budget.INPUTS.items()
    }
    result = {
        "status": "SCOPED_LOCAL_COST_REDUCTION_SELECTED_KAPPA_STILL_EXCLUDED",
        "predecessor_commit": "05f7aad0f08992ee48ec2dd93e896d9a4567847d",
        "fanout_variant_sha256": hashlib.sha256(
            (ROOT / "research/p104-interleaved-search/fanout.py").read_bytes()
        ).hexdigest(),
        "selected_kappa": str(budget.SELECTED_KAPPA),
        "selected_complex_saving_threshold": str(selected_a),
        "public_profile": budget.profile_json(public),
        "private_COPY_profile": budget.profile_json(private),
        "combined_profile": budget.profile_json(profile),
        "combined_rank_mass": budget.mass(profile),
        "combined_rank_mass_before": 5894,
        "rank_mass_saved": 9,
        "model": {key: str(value) for key, value in model.items()},
        "saving_root_interval": budget.interval(root),
        "complex_kappa_cap": str(complex_cap),
        "fixed_bit_kappa_cap": str(bit_cap),
        "selected_threshold_moment": budget.interval(selected_moment),
        "selected_threshold_excluded": True,
        "fractional_rank_51_residual_relaxation": True,
        "selected_private_centre_stock": stock,
        "inputs": inputs,
        "new_kappa_gain_certified": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
