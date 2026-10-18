#!/usr/bin/env python3
"""Independent XOR-span reconstruction of #2979's staged profile arithmetic.

This rebuilds the profile-bearing word sections through stages 1-3 and checks
the pinned T74 aggregate numerically. It does not certify the extraction or
rewrite identities, compensation/cleanup semantics, owners, chronology, native
admission, or the exact outer release.
"""
from collections import Counter
from copy import deepcopy
from decimal import Decimal as D, localcontext
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "research" / "rank7-joint-endframes"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


@lru_cache(maxsize=100_000)
def _span(vectors):
    """Return an F2 span by explicit closure, independent of RREF implementations."""
    out = {0}
    for v in vectors:
        old = tuple(out)
        out.update(x ^ v for x in old)
    return frozenset(out)


def span(vectors):
    return _span(tuple(vectors))


def rank(vectors):
    n = len(span(vectors))
    need(n and n & (n - 1) == 0, "span cardinality is not a power of two")
    return n.bit_length() - 1


def inside(a, b):
    return span(a).issubset(span(b))


def dot_parity(a, b):
    return (a & b).bit_count() & 1


def profile(word):
    full = span([1 << i for i in range(9)])
    ends = [full] * 112
    ends += [span(z for z in range(1, 512) if not dot_parity(z, p)) for p in word["ports"]]
    ends += [full] * 480
    starts = [span([p]) for p in word["ports"]] + [frozenset()] * 592
    for r, rows in word["start_extra"].items():
        starts[int(r)] = span(rows)
    for r, rows in word["helper_final"].items():
        ends[int(r)] = span(rows)

    current = list(starts)
    paid = Counter()

    def climb(r, rows):
        rows = span(rows)
        need(inside(current[r], rows), f"nonmonotone register {r}")
        d = rank(rows) - rank(current[r])
        if d:
            paid[d] += 1
        current[r] = rows

    def step(gate):
        if gate[0] == "warp":
            need(current[gate[1]] == span(gate[3]), "warp entry frame")
            current[gate[1]] = span(gate[4])
        elif gate[0] == "add":
            climb(gate[1], gate[-1])
            climb(gate[2], gate[-1])
        elif gate[0] == "scale":
            climb(gate[1], gate[-1])
        else:
            raise AssertionError(("unknown gate", gate[0]))

    for gate in word["A"]:
        step(gate)
    for r, rows in zip(word["centers"], word["center_frames"]):
        need(current[r] == span(rows), f"center entry frame {r}")
        levels = []
        for cut in word["cut"]:
            if cut[2] == r:
                levels.append(span(word["target_levels"].get(str(cut[1] - 112), [])))
        rows = span(rows)
        for target in sorted(set(levels), key=len, reverse=True):
            if rows != target:
                paid[rank(rows) - rank(target)] += 1
            rows = target
    warps = {}
    for entry in word["warps"]:
        warps.setdefault(entry[0], []).append(entry)
    for pos in range(len(word["B"]) + 1):
        for entry in warps.get(pos, []):
            need(current[entry[1]] == span(entry[3]), "B warp entry frame")
            current[entry[1]] = span(entry[4])
        if pos < len(word["B"]):
            step(word["B"][pos])
    for gate in word["restore"]:
        step(gate)

    live = set(range(704)) - set(word["removed"])
    for r in live:
        climb(r, ends[r])
    inventory = Counter(rank(ends[r]) - rank(starts[r]) for r in live if r >= 224)
    return dict(sorted(paid.items())), dict(sorted(inventory.items()))


def roles(gate):
    return set(gate[1:3] if gate[0] == "add" else gate[1:2])


def apply_groups(parent, record, chosen):
    out = deepcopy(parent)
    changed = []
    for name in chosen:
        W, helpers = record["groups"][name]
        W = span(W)
        for h in helpers:
            row = record["helper_final_changes"][str(h)]
            need(parent["helper_final"][str(h)] == row["old"], "helper old-frame pin")
            need(span(row["new"]) == W and rank(row["new"]) == 7, "shared rank-7 helper endpoint")
            need(inside(row["new"], row["old"]), "helper endpoint containment")
            out["helper_final"][str(h)] = list(row["new"])
    for edit in record["frame_edits"]:
        owners = [name for name, (W, _) in record["groups"].items() if inside(edit["new_frame"], W)]
        need(len(owners) == 1, ("unique frame-edit owner", edit["section"], edit["index"], owners))
        name = owners[0]
        if name not in chosen:
            continue
        section, i = edit["section"], edit["index"]
        gate = out[section][i]
        need(gate[:-1] == edit["gate"] and span(gate[-1]) == span(edit["old_frame"]), "gate preimage pin")
        need(rank(edit["new_frame"]) == rank(edit["old_frame"]) - 1, "gate codimension one")
        need(inside(edit["new_frame"], edit["old_frame"]), "gate hyperplane containment")
        need(inside(edit["new_frame"], record["groups"][name][0]), "gate is inside shared W")
        gate[-1] = list(edit["new_frame"])
        changed.append((name, section, i))
    for name in chosen:
        W = record["groups"][name][0]
        for h in record["groups"][name][1]:
            for section in ("A", "B", "restore"):
                for i, gate in enumerate(out[section]):
                    if h in roles(gate):
                        need(inside(gate[-1], W), ("lowered-helper event outside W", name, h, section, i))
    return out, changed


def basis_by_closure(vectors):
    """Choose an independent basis by explicit XOR closure, without RREF."""
    accepted = []
    current = {0}
    for vector in sorted(set(vectors)):
        if vector not in current:
            accepted.append(vector)
            current.update(value ^ vector for value in tuple(current))
    need(span(accepted) == span(vectors), "closure-selected basis spans its input")
    return accepted


def apply_extraction(word, transform):
    """Rebuild the profile-bearing part of one paired extraction from literal gates."""
    x = deepcopy(word)
    helper = int(transform["helper"])
    need(str(helper) not in x["helper_final"] and str(helper) not in x["start_extra"], "new extraction helper")
    prelude = int(x["prelude_events"])
    protected = set(map(int, x["helper_final"])) | set(map(int, x["start_extra"]))
    protected |= {int(c["source"]) for c in x["initial_corrections"]}
    removed = set(map(int, x["removed"]))

    before = transform["before"]
    after = transform["after"]
    need(before and after, "nonempty paired extraction")
    for gate in before:
        need(gate[0] in ("add", "scale") and gate[-1] == [], "extraction inputs use zero frames")
        involved = gate[1:3] if gate[0] == "add" else gate[1:2]
        need(all(224 <= int(r) < 704 and int(r) not in protected and int(r) not in removed
                 for r in involved), "extraction inputs touch only live unprotected helpers")

    normal = int(transform["normal"])
    hyperplane = [v for v in range(1, 512) if not dot_parity(v, normal)]
    end_frame = basis_by_closure(hyperplane)
    need(rank(end_frame) == 8 and all(not dot_parity(v, normal) for v in end_frame),
         "extraction endpoint is the declared rank-8 hyperplane")
    need(all(g[0] in ("add", "scale") and inside(g[-1], end_frame) for g in after),
         "extraction outputs lie in the declared hyperplane")

    x["A"] = x["A"][:prelude] + deepcopy(before) + x["A"][prelude:]
    x["restore"] += deepcopy(after)
    x["helper_final"][str(helper)] = end_frame
    seen = set()
    for edit in transform["frame_changes"]:
        section, index = edit["section"], int(edit["index"])
        need(section in ("A", "B", "restore") and (section, index) not in seen,
             "unique extraction frame-change address")
        need(0 <= index < len(x[section]) and (section != "A" or index >= prelude),
             "extraction frame-change address is live")
        seen.add((section, index))
        gate = x[section][index]
        need(gate[:-1] == edit["gate"] and span(gate[-1]) == span(edit["old_frame"]),
             "extraction frame-change preimage")
        need(rank(edit["new_frame"]) == rank(edit["old_frame"]) - 1 and
             inside(edit["new_frame"], edit["old_frame"]), "extraction frame change lowers one dimension")
        gate[-1] = list(edit["new_frame"])
    return x


def apply_literal_rewrites(word, rewrites, shift_warps=True):
    """Apply declared stage-3 splices by exact old slices and source indices."""
    x = deepcopy(word)
    taken = {section: [] for section in ("A", "B", "restore")}
    edits = []
    for rewrite in rewrites:
        for edit in rewrite["edits"]:
            section, start, stop = edit["section"], int(edit["start"]), int(edit["stop"])
            need(section in taken and 0 <= start <= stop <= len(word[section]), "rewrite slice address")
            need(section != "A" or start >= int(word["prelude_events"]), "rewrites preserve prelude")
            need(word[section][start:stop] == edit["old"] and edit["old"] != edit["new"],
                 "rewrite old slice is exact and nonvacuous")
            for left, right in taken[section]:
                need(stop < left or right < start, "declared rewrite slices are disjoint and separated")
            taken[section].append((start, stop))
            edits.append((section, start, stop, edit["new"]))

    for section, start, stop, new in sorted(edits, key=lambda row: (row[0], -row[1], -row[2])):
        x[section][start:stop] = deepcopy(new)

    b_edits = [(start, stop, len(new) - (stop - start))
               for section, start, stop, new in edits if section == "B"]
    if shift_warps:
        for warp in x["warps"]:
            pos = int(warp[0])
            need(not any(start < pos < stop for start, stop, _ in b_edits), "warp outside edited B slices")
            warp[0] = pos + sum(delta for start, stop, delta in b_edits if stop <= pos and start < pos)
    return x


def profile_projection(word):
    """Fields sufficient to determine the complete paid local profile and inventory."""
    names = ("A", "B", "restore", "warps", "ports", "start_extra", "helper_final",
             "centers", "center_frames", "cut", "target_levels", "removed", "prelude_events")
    return {name: word[name] for name in names}


def replay_stages(parent, record, transforms, rewrites):
    """Bind stages 2/3 to source records and return their independently priced profiles."""
    stage1, _ = apply_groups(parent, record, list(record["groups"]))
    stage2 = stage1
    step_profiles = []
    for expected_step, transform in enumerate(transforms, 1):
        need(int(transform["step"]) == expected_step, "extraction order")
        stage2 = apply_extraction(stage2, transform)
        step_profiles.append(profile(stage2))
    after2 = profile(stage2)
    stage3 = apply_literal_rewrites(stage2, rewrites)
    after3 = profile(stage3)
    return stage1, stage2, stage3, {
        "stage2_step_profiles": step_profiles,
        "stage2_profile": after2[0],
        "stage2_inventory": after2[1],
        "stage3_profile": after3[0],
        "stage3_inventory": after3[1],
    }


def price(profile_, weights):
    return sum(weights[r] * n for r, n in profile_.items())


def dec_fraction(value):
    q = Q(value)
    return D(q.numerator) / D(q.denominator)


def decimal_root(profile_, replicas):
    """High-precision numerical cross-check; intentionally not an exact certificate."""
    with localcontext() as ctx:
        ctx.prec = 90
        denominator = D(73 * 896 * replicas)

        def moment(b):
            terms = []
            for r, n in profile_.items():
                base = D(73) / D(r)
                terms.append(D(n) * D(r) * (b * base.ln()).exp())
            return sum(terms, D(0)) / denominator

        low, high = D(0), D("0.01")
        need(moment(low) < 1 < moment(high), "T74 moment root bracket")
        for _ in range(320):
            mid = (low + high) / 2
            if moment(mid) < 1:
                low = mid
            else:
                high = mid
        root = (low + high) / 2
        return root, moment(root) - 1


def main():
    selected = read(ROOT / "certificates/selected-result.json")
    record = read(PKG / "data/STAGE1-FRAME-EDITS.json")
    prices = read(PKG / "construction/STAGE-PRICES.json")
    claim = read(PKG / "CLAIM.json")
    cap = read(PKG / "certificates/RELAX-CAP.json")
    allocation = {int(k): int(v) for k, v in read(PKG / "allocation/PROFILE.json").items()}
    weights = {int(k): int(v) for k, v in prices["weights"]["c"].items()}
    break_even = int(prices["weights"]["break_even"])

    rows = {}
    for variant in ("base", "extra"):
        parent = read(PKG / f"data/PARENT-{variant}.json.gz")
        parent_profile, parent_inventory = profile(parent)
        need(parent_profile == {int(k): v for k, v in parent["report"]["local_profile"].items()}, "independent parent profile")
        need(parent_inventory == {int(k): v for k, v in parent["report"]["width_inventory"].items()}, "independent parent inventory")

        stage1, edits = apply_groups(parent, record, list(record["groups"]))
        stage1_profile, stage1_inventory = profile(stage1)
        need(len(edits) == 139, "all five groups account for 139 frame edits")
        need(stage1_profile == {int(k): v for k, v in record["declared_local_profile"].items()}, "five-group local profile")
        need(stage1_inventory == {int(k): v for k, v in record["declared_width_inventory"].items()}, "five-group width inventory")

        v45, v45_edits = apply_groups(parent, record, ["V45"])
        joint_profile, joint_inventory = profile(v45)
        need(len(v45_edits) == 61, "V45 frame edit count")
        only_one = deepcopy(v45)
        v45_helpers = record["groups"]["V45"][1]
        for h in v45_helpers[1:]:
            only_one["helper_final"][str(h)] = deepcopy(parent["helper_final"][str(h)])
        one_profile, one_inventory = profile(only_one)
        delta = lambda newer: price(newer, weights) - price(parent_profile, weights)
        joint_delta, one_delta = delta(joint_profile), delta(one_profile)
        joint_margin = -joint_delta - len(v45_helpers) * break_even
        one_margin = -one_delta - break_even
        need((joint_delta, joint_margin) == (-8_388_172, 22_972), "V45 coordinated price and margin")
        need((one_delta, one_margin) == (-2_038_159, -53_141), "V45 losing single-helper control")
        rows[variant] = {
            "parent_profile": parent_profile,
            "stage1_profile": stage1_profile,
            "stage1_inventory": stage1_inventory,
            "v45_profile": joint_profile,
            "v45_inventory": joint_inventory,
            "v45_edit_count": len(v45_edits),
            "v45_delta_units": joint_delta,
            "v45_margin_units": joint_margin,
            "single_helper": v45_helpers[0],
            "single_delta_units": one_delta,
            "single_margin_units": one_margin,
            "single_inventory": one_inventory,
        }
    need(rows["base"] == rows["extra"], "provider profile agreement")

    final_rows = {}
    for variant in ("base", "extra"):
        final = read(PKG / f"data/WORD-{variant}.json.gz")
        final_profile, final_inventory = profile(final)
        need(final_profile == {int(k): v for k, v in final["report"]["local_profile"].items()}, "independent final-word profile")
        need(final_inventory == {int(k): v for k, v in final["report"]["width_inventory"].items()}, "independent final-word inventory")
        final_rows[variant] = (final_profile, final_inventory)
    need(final_rows["base"] == final_rows["extra"], "final provider profile agreement")
    final_profile, final_inventory = final_rows["base"]

    transforms = [read(PKG / f"data/TRANSFORM-{helper}.json")
                  for helper in (226, 228, 230, 363, 395)]
    rewrites = read(PKG / "data/REWRITES-2957.json")
    stage_replays = {}
    for variant in ("base", "extra"):
        parent = read(PKG / f"data/PARENT-{variant}.json.gz")
        stage1, stage2, stage3, ledger = replay_stages(parent, record, transforms, rewrites)
        final = read(PKG / f"data/WORD-{variant}.json.gz")
        for name, actual, expected in (("stage2", ledger["stage2_profile"], profile(stage2)[0]),
                                       ("stage3", ledger["stage3_profile"], profile(stage3)[0])):
            need(actual == expected, f"{name} replay ledger reports its derived profile")
        stage2_delta = price(profile(stage2)[0], weights) - price(profile(stage1)[0], weights)
        stage3_delta = price(profile(stage3)[0], weights) - price(profile(stage2)[0], weights)
        need(stage2_delta == int(prices["stage2"]["literal_price_units"]), "stage-2 source replay price")
        need(stage3_delta == int(prices["stage3"]["literal_price_units"]), "stage-3 source replay price")
        need(profile(stage3) == profile(final), "stage-2/3 replay reproduces both final local profile and inventory")
        for field in ("A", "B", "restore", "warps", "ports", "start_extra", "centers", "center_frames",
                      "cut", "target_levels", "removed", "prelude_events"):
            need(stage3[field] == final[field], f"stage-2/3 replay final {field} matches pinned word")
        need(set(stage3["helper_final"]) == set(final["helper_final"]), "stage-2/3 replay endpoint inventory")
        need(all(span(stage3["helper_final"][h]) == span(final["helper_final"][h])
                 for h in final["helper_final"]), "stage-2/3 replay endpoints match pinned spans")
        stage_replays[variant] = {
            "stage1_delta_units": price(profile(stage1)[0], weights) - price(profile(parent)[0], weights),
            "stage2_delta_units": stage2_delta,
            "stage3_delta_units": stage3_delta,
            "stage2_profile": profile(stage2)[0],
            "stage2_inventory": profile(stage2)[1],
            "final_profile": profile(stage3)[0],
            "final_inventory": profile(stage3)[1],
        }
    need(stage_replays["base"] == stage_replays["extra"], "base/extra source replay agrees across stages 2/3")
    need(stage_replays["base"]["stage1_delta_units"] == int(prices["stage1"]["literal_price_units"]),
         "stage-1 source replay price")

    # Semantic failure controls for the new source-bound stage-2/3 replayer.
    control_parent = read(PKG / "data/PARENT-base.json.gz")
    control_stage1, _ = apply_groups(control_parent, record, list(record["groups"]))
    omitted_frame = deepcopy(transforms)
    omitted_frame[1]["frame_changes"] = []
    wrong_stage2 = control_stage1
    for transform in omitted_frame:
        wrong_stage2 = apply_extraction(wrong_stage2, transform)
    wrong_stage3 = apply_literal_rewrites(wrong_stage2, rewrites)
    need(profile(wrong_stage3) != profile(read(PKG / "data/WORD-base.json.gz")),
         "omitting the declared stage-2 frame change is detected by the final paid profile")

    stale_rewrites = deepcopy(rewrites)
    stale_edit = next(edit for rewrite in stale_rewrites for edit in rewrite["edits"] if edit["old"])
    stale_edit["start"] += 1
    stale_edit["stop"] += 1
    try:
        apply_literal_rewrites(stage2, stale_rewrites)
    except AssertionError:
        stale_rewrite_rejected = True
    else:
        need(False, "stale stage-3 rewrite preimage must be rejected")
    unshifted_warps = apply_literal_rewrites(stage2, rewrites, shift_warps=False)
    try:
        profile(unshifted_warps)
    except AssertionError:
        unshifted_warp_rejected = True
    else:
        need(False, "unshifted B-phase warp must be rejected by the profile replay")

    total_delta = price(final_profile, weights) - price(rows["base"]["parent_profile"], weights)
    stage_delta_sum = sum(int(prices[f"stage{i}"]["literal_price_units"]) for i in (1, 2, 3))
    need(total_delta == stage_delta_sum == -56_726_747, "final frame-price delta equals three published stage deltas")
    need(final_inventory == {int(k): v for k, v in claim["width_inventory"].items()}, "claim width inventory matches independently profiled final word")
    need(final_profile == {int(k): v for k, v in claim["local_profile"].items()}, "claim local profile matches independently profiled final word")

    calls, replicas = int(claim["calls"]), int(claim["replicas"])
    idle = dict(allocation)
    for r, n in final_profile.items():
        idle[r] = idle.get(r, 0) - calls * n
    need(all(n >= 0 for n in idle.values()), "T74 profile pays all 666 complete local calls")
    idle = {r: n for r, n in sorted(idle.items()) if n}
    need(sum(r * n for r, n in allocation.items()) == replicas * 65_088, "complete T74 rank-mass identity")
    need(sum(r * n for r, n in final_profile.items()) * calls + sum(r * n for r, n in idle.items()) == replicas * 65_088,
         "local plus idle profile closes T74 rank mass")
    need(allocation == {int(k): v for k, v in claim["profile"].items()}, "T74 profile matches claim")

    root, root_residual = decimal_root(allocation, replicas)
    selected_kappa = Q(selected["kappa"])
    claimed_kappa = Q(claim["kappa"])
    cap_lower = dec_fraction(cap["cap_lower"])
    cap_upper = dec_fraction(cap["cap_upper"])
    need(claimed_kappa > selected_kappa, "claimed candidate kappa strictly exceeds selected kappa")
    need(root > dec_fraction(claim["complex_lower"]), "numerical T74 root exceeds claimed conservative complex lower bound")
    need(root < cap_lower < cap_upper, "numerical T74 root lies below the fixed-inventory cap bracket")
    need(D(0) < root - dec_fraction(claimed_kappa) < D("1e-24"), "claim is a conservative floor of the numerical T74 root")

    print(json.dumps({
        "status": "PASS_V45_INDEPENDENT_LOCAL_PROFILE_AND_T74_AGGREGATE_ARITHMETIC",
        "v45": rows["base"],
        "final_local_profile": final_profile,
        "final_width_inventory": final_inventory,
        "local_stage_delta_units": total_delta,
        "sum_of_stage_deltas_units": stage_delta_sum,
        "source_replayed_stages_1_to_3": stage_replays["base"],
        "stage_replay_controls": {
            "omitted_stage2_frame_change_detected": True,
            "stale_stage3_preimage_rejected": stale_rewrite_rejected,
            "unshifted_stage3_warp_rejected": unshifted_warp_rejected,
        },
        "t74_profile": allocation,
        "t74_idle_profile_after_666_calls": idle,
        "t74_rank_mass": sum(r * n for r, n in allocation.items()),
        "root_decimal_crosscheck_only": str(root),
        "root_moment_residual_decimal": str(root_residual),
        "claimed_kappa_minus_selected_exact": str(claimed_kappa - selected_kappa),
        "limitations": [
            "Stage-2/3 replay checks the profile-bearing word sections and prices, not compensation or cleanup semantics.",
            "The extracted operator identities and the fourteen rewrite identities are not independently certified here.",
            "T74 ownership chronology, physical admission, native admission, and outer release are not independently audited here.",
            "The Decimal root is a numeric cross-check, not an exact root certificate."
        ]
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
