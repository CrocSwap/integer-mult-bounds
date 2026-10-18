"""Exact conditional bank invoices, including encoder roles and pads.

No emitted scalar or frame word is asserted. The final two baselines are
PR606's documented proposals, priced at selected and discussion targets.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib
import json
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
BANK = ROOT / "research/niemeier-lattices/workbench/paid-controller/banked.py"
sys.path.insert(0, str(BANK.parent))
import banked as b

N, H = 30960, 17
TARGETS = {"selected_frontier1094": F(json.loads((ROOT / "certificates/selected-result.json").read_text())["kappa"]),
           "discussion_pr1424_title": F("0.001676855229071321886206381217337893")}
COMPENSATION_PATHS = {"full": [17], "coarse": [1, 16],
                      "h6_root_path": [1, 7, 8, 1], "units": [1] * 17}


def require(value, message):
    if not value:
        raise ValueError(message)


def ceiling_minus_one(value):
    return -((-value.numerator) // value.denominator) - 1


def add_group(row, count, profile):
    unit, q, pad = b.helper(row, profile)
    row["terms"].extend((count * mass, base) for mass, base in unit)
    row["stock"] += F(row["stages"] * count, q)


def make_row(name, stages):
    histogram = {17: 256, 15: 560} if name != "full_center_fallback" else {17: 816}
    row = b.base(N, H, histogram, stages, [16])
    if name == "conservative_encoder":
        # Use PR606 encoder_conservative.py's proposed [1,15] data profile.
        row = b.base(N, H, histogram, stages, [1, 15])
        groups = [(28800, [1, 8, 8]), (1920, [9, 8]),
                  (13440, [9, 6, 2]), (560, [15, 2]), (256, [17])]
        source, target = [1, 15], [1, 15]
    elif name == "full_center_fallback":
        # One width17 descent and one stock-bearing full center per center.
        row["terms"][0:1] = [(F(N * stages * 16), F(row["m"], 16))] + [
            (F(N * stages * a), F(row["m"], a)) for a in [1, 7, 8]]
        groups = [(816, [17])]
        source, target = [16], [1, 7, 8]
    else:
        groups = []
        source, target = [16], [16]
    for count, path in groups:
        add_group(row, count, path)
    require(sum(mass for mass, _ in row["terms"]) == row["m"] * row["stock"] - row["deficit"],
            "Complete bank rank mass, including groups and pads")
    require(all(row["m"] / base <= row["cap"] for _, base in row["terms"]), "Strict child cap")
    return row, source, target, groups


records = []
for name in ("h6_paper_screen", "conservative_encoder", "full_center_fallback"):
    for stages in (3, 5, 7):
        row, source, target, groups = make_row(name, stages)
        for target_name, k in TARGETS.items():
            alpha = k / (1-k)
            pl, ph = b.pressure(row, alpha)
            extras = {}
            for profile_name, profile in COMPENSATION_PATHS.items():
                unit, q, pad = b.helper(row, profile)
                ul, uh = b.pressure(dict(row, terms=unit), alpha)
                lower = ceiling_minus_one((row["deficit"]-ph)/uh)
                upper = ceiling_minus_one((row["deficit"]-pl)/ul)
                require(lower == upper, "Certified exact strict integer threshold")
                if lower >= 0:
                    require(row["deficit"] - ph - lower*uh > 0,
                            "The last allowed count has strictly positive slack")
                    require(row["deficit"] - pl - (lower+1)*ul <= 0,
                            "The next count cannot have strictly positive slack")
                # These omissions would contradict the complete bank identity.
                residual_mass = F(stages * H)
                full_mass = sum(mass for mass, _ in unit)
                require(full_mass == F(stages * row["m"], q), "Per-helper mass with pad")
                require(full_mass != residual_mass, "Omitted pad fails complete bank mass")
                require(full_mass != 0, "Added bank stock without residual work fails mass")
                extras[profile_name] = dict(path=profile, max_additional_helpers=max(lower, 0),
                    base_passes=lower >= 0, bank_slots=q, pad_rank=pad,
                    helper_pressure_interval_scaled_1e12=b.c.scaled(ul, uh, 10**12))
            records.append(dict(baseline=name, stages=stages, m=row["m"], source_path=source,
                target_path=target, encoder_groups=[dict(count=c, path=p) for c,p in groups],
                encoder_roles=sum(c for c,_ in groups), center_bill=sum(w*c for w,c in
                    ({17:256,15:560} if name != "full_center_fallback" else {17:816}).items()),
                stock=str(row["stock"]), deficit=row["deficit"],
                target_name=target_name, target_kappa=str(k),
                slack_interval_scaled_1e12=b.c.scaled(row["deficit"]-ph, row["deficit"]-pl, 10**12),
                compensation_capacity=extras))

result = dict(status="PASS_CONDITIONAL_COMPLETE_BANK_INVOICES",
    source_hashes={name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in (
        "research/niemeier-lattices/workbench/paid-controller/banked.py",
        "research/niemeier-lattices/workbench/paid-controller/portable.py",
        "research/niemeier-lattices/workbench/paid-controller/encoder_conservative.py",
        "research/niemeier-lattices/workbench/paid-controller/full_centers.py",
        "research/niemeier-lattices/code/costs.py",
        "research/leech-lattice/code/screen.py",
        "certificates/selected-result.json")},
    banked_source_sha256=hashlib.sha256(BANK.read_bytes()).hexdigest(),
    selected_record_sha256=hashlib.sha256((ROOT/"certificates/selected-result.json").read_bytes()).hexdigest(),
    scope="Necessary bank pressure screen only. It charges proposed encoder roles, their full ordinary paths, replication stock, pads, data profiles and existing center descents. It does not admit a Walsh DAG, price unlisted private descents or prove chronology, inverse-transpose dirt restoration, wrappers, compiler admission or bit-side envelope.",
    records=records)
destination = Path(__file__).with_name("CHARGED-SCREEN.json")
destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
for row in records:
    if row["stages"] == 5:
        print(row["baseline"], row["target_name"], "encoder", row["encoder_roles"],
              "extra_h6_path", row["compensation_capacity"]["h6_root_path"]["max_additional_helpers"],
              "extra_coarse", row["compensation_capacity"]["coarse"]["max_additional_helpers"])
