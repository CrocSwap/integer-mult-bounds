#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact two-role whole-helper swap census on the selected PR1094 owner map.

Prepared by Aaron Wang with help from opencode.
Josie Elliston's pinned PR1091 audit supplies geometry and baseline admission;
the swap enumeration and exponent-uniform comparison are new here.
"""
import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_PACKAGE = "research/complex-t16-rare-pattern-exchanges/"
AUDITOR = "research/t16-owner-audit-seed67/verify.py"
CEILING = "research/complex-local-word-ceiling/ceiling.py"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def checked_sources(root, manifest):
    """Authenticate each byte snapshot before importing or decoding it."""
    raw = {}
    for item in manifest["files"]:
        if item["usage"] == "input":
            name = item["path"]
            path = root / name
            require(path.resolve().is_relative_to(root.resolve()), "external input")
            data = path.read_bytes()
            require(hashlib.sha256(data).hexdigest() == item["sha256"], "source drift: " + name)
            raw[name] = data
    return raw


def decode(raw, name):
    return json.loads(gzip.decompress(raw[name]) if name.endswith(".gz") else raw[name])


@dataclass
class Bin:
    capacity: int
    family: int
    used: int = 0

    @property
    def remainder(self):
        return self.capacity - self.used


def bin_key(role):
    return (role["owner_replica"], role["child"], role["port"])


class Model:
    """Owner-map geometry; reuses the pinned PR1091 audit's data conventions."""

    def __init__(self, roles, geo, windows, positions):
        self.roles, self.geo, self.windows, self.positions = roles, geo, windows, positions
        self.bins, self.families = {}, defaultdict(set)
        for owner, child in sorted(windows):
            pair, side = geo["place"][child]
            for port in range(112):
                self.bins[owner, child, port] = Bin(
                    geo["rank"][child], owner * 896 + (2 * pair + side) * 112 + port)
        for role in roles:
            self.bins[bin_key(role)].used += role["width"]
            self.families[role["time"]].add(role["family"])
        require(all(b.remainder >= 0 for b in self.bins.values()), "overfull bin")
        self.by_remainder = defaultdict(list)
        for key, b in self.bins.items():
            self.by_remainder[b.remainder].append(key)
        self.by_family = {b.family: key for key, b in self.bins.items()}

    def window_active_rejection(self, role, destination):
        """Strict source-event window and active-pair rules for one landing."""
        call = (role["stage"], role["replica"])
        lo, hi = self.windows[destination[:2]]
        if not lo < self.positions[call] < hi:
            return "outside_strict_source_event_window"
        pair = self.geo["place"][destination[1]][0]
        if (destination[0], pair) == (call[1], self.geo["stage_pair"][call[0]]):
            return "active_data_pair"
        return None


def family_collision(model, i, j):
    """Pair-aware per-call family uniqueness for swapping roles i and j."""
    ri, rj = model.roles[i], model.roles[j]
    fi, fj = model.bins[bin_key(ri)].family, model.bins[bin_key(rj)].family
    ti, tj = ri["time"], rj["time"]
    if ti == tj:
        return None  # the swap is a bijection inside one call
    if fj in model.families[ti] - {fi}:
        return "same_call_family_collision"
    if fi in model.families[tj] - {fj}:
        return "same_call_family_collision"
    return None


def swap_rejection(model, i, j):
    ri, rj = model.roles[i], model.roles[j]
    bi, bj = bin_key(ri), bin_key(rj)
    for role, dest in ((ri, bj), (rj, bi)):
        reason = model.window_active_rejection(role, dest)
        if reason is not None:
            return reason
    return family_collision(model, i, j)


def swap_sign(x1, w1, x2, w2):
    """Moment sign of swapping widths w1, w2 between remainders x1, x2.

    New remainders are (x1+d, x2-d) with d = w1-w2, sum preserved.  For
    p = 1-a in (0, 1) the cost x1^p + x2^p is strictly decreasing in the
    larger entry at fixed sum (strict concavity), so the sign is uniform for
    every real 0 < a < 1 and decided by exact integer comparison of the
    maxima.
    """
    d = w1 - w2
    if x1 + d < 0 or x2 - d < 0:
        return "capacity_infeasible"
    old_max = max(x1, x2)
    new_max = max(x1 + d, x2 - d)
    if new_max > old_max:
        return "strictly_improving"
    if new_max == old_max:
        return "neutral"
    return "strictly_worsening"


def group_roles(role_specs):
    """role_specs: iterable of (bin, remainder, width). Pure counting helper."""
    class_roles, class_bins = defaultdict(list), defaultdict(Counter)
    for index, (b, x, w) in enumerate(role_specs):
        class_roles[x, w].append(index)
        class_bins[x, w][b] += 1
    return class_roles, class_bins


def tabulate(class_roles, class_bins):
    """Class-pair table and distinct-bin pair classification; no pair materialized."""
    classes = sorted(class_roles)
    rows, classification = [], Counter()
    same_bin = 0
    for pos, ka in enumerate(classes):
        for kb in classes[pos:]:
            A, B = class_roles[ka], class_roles[kb]
            if ka == kb:
                total = len(A) * (len(A) - 1) // 2
                shared = sum(n * (n - 1) // 2 for n in class_bins[ka].values())
            else:
                total = len(A) * len(B)
                shared = sum(class_bins[ka][b] * class_bins[kb][b]
                             for b in set(class_bins[ka]) & set(class_bins[kb]))
            same_bin += shared
            distinct = total - shared
            if not distinct:
                continue
            sign = swap_sign(ka[0], ka[1], kb[0], kb[1])
            rows.append(dict(class_a=[ka[0], ka[1]], class_b=[kb[0], kb[1]],
                             class_a_roles=len(A), class_b_roles=len(B),
                             same_bin_pairs=shared, distinct_bin_pairs=distinct,
                             moment_sign=sign))
            classification[sign] += distinct
    return rows, classification, same_bin


def census(model):
    """Complete unordered-pair classification; materialize only improving pairs."""
    roles = model.roles
    specs = [(bin_key(r), model.bins[bin_key(r)].remainder, r["width"]) for r in roles]
    class_roles, class_bins = group_roles(specs)
    rows, classification, same_bin = tabulate(class_roles, class_bins)
    candidates = []
    for row in rows:
        if row["moment_sign"] != "strictly_improving":
            continue
        ka, kb = tuple(row["class_a"]), tuple(row["class_b"])
        x1, w1 = ka
        x2, w2 = kb
        d = w1 - w2
        for i in class_roles[ka]:
            ri = roles[i]
            bi = bin_key(ri)
            for j in class_roles[kb]:
                rj = roles[j]
                bj = bin_key(rj)
                if bi == bj:
                    continue
                candidates.append(dict(
                    role_index_a=i, role_index_b=j,
                    role_a=[ri["stage"], ri["replica"], ri["helper"]],
                    role_b=[rj["stage"], rj["replica"], rj["helper"]],
                    position_a=model.positions[ri["stage"], ri["replica"]],
                    position_b=model.positions[rj["stage"], rj["replica"]],
                    bin_a=list(bi), bin_b=list(bj),
                    widths=[w1, w2], old_remainders=[x1, x2],
                    new_remainders=[x1 + d, x2 - d],
                    window_for_a=list(model.windows[bj[:2]]),
                    window_for_b=list(model.windows[bi[:2]]),
                    rejection=swap_rejection(model, i, j)))
    require(len(candidates) == classification["strictly_improving"],
            "incomplete improving census")
    candidates.sort(key=lambda c: (c["role_index_a"], c["role_index_b"]))
    total_pairs = len(roles) * (len(roles) - 1) // 2
    require(same_bin + sum(classification.values()) == total_pairs, "pair accounting")
    bins = model.bins
    return dict(
        roles=len(roles), bins=len(bins),
        total_unordered_role_pairs=total_pairs,
        same_bin_noop=same_bin,
        bin_remainders=dict(sorted((r, len(keys)) for r, keys in model.by_remainder.items())),
        moment_classes=rows,
        pair_classification=dict(sorted(classification.items())),
        improving_candidates=candidates,
        rejection_counts=dict(sorted(Counter(
            c["rejection"] for c in candidates if c["rejection"] is not None).items())),
        legal_strict_improvements=sum(c["rejection"] is None for c in candidates))


def _eligible_groups(model):
    """(owner, child) groups whose strict window and active-pair rule allow each call."""
    out = {}
    for call, pos in model.positions.items():
        keep = set()
        for (owner, child), (lo, hi) in model.windows.items():
            if not lo < pos < hi:
                continue
            pair = model.geo["place"][child][0]
            if (owner, pair) == (call[1], model.geo["stage_pair"][call[0]]):
                continue
            keep.add((owner, child))
        out[call] = keep
    return out


def find_legal_swap(model, want_sign, budget=4_000_000):
    """First legal distinct-bin pair with the requested moment sign, or None.

    Bounded search used only for the positive control; the census itself is
    analytic and does not depend on this finder.
    """
    roles = model.roles
    specs = [(bin_key(r), model.bins[bin_key(r)].remainder, r["width"]) for r in roles]
    class_roles, _ = group_roles(specs)
    eligible = _eligible_groups(model)
    by_group = defaultdict(lambda: defaultdict(list))
    for key, indices in class_roles.items():
        for i in indices:
            owner, child, _port = bin_key(roles[i])
            by_group[key][owner, child].append(i)
    pairs = []
    classes = sorted(class_roles)
    for pos, ka in enumerate(classes):
        for kb in classes[pos:]:
            if swap_sign(ka[0], ka[1], kb[0], kb[1]) != want_sign:
                continue
            pairs.append((len(class_roles[ka]) * len(class_roles[kb]), ka, kb))
    checks = 0
    for _size, ka, kb in sorted(pairs):
        for i in class_roles[ka]:
            ri = roles[i]
            bi = bin_key(ri)
            call = (ri["stage"], ri["replica"])
            for group in eligible[call]:
                for j in by_group[kb].get(group, ()):
                    if bin_key(roles[j]) == bi:
                        continue
                    checks += 1
                    if swap_rejection(model, i, j) is None:
                        return i, j, checks
                    if checks >= budget:
                        return None
    return None


def swap_roles(model, i, j):
    """Control only: exchange two whole roles and compact both slice prefixes."""
    roles = [dict(z) for z in model.roles]
    bi, bj = bin_key(roles[i]), bin_key(roles[j])
    for index, dest in ((i, bj), (j, bi)):
        owner, child, port = dest
        roles[index].update(owner_replica=owner, child=child, port=port,
                            family=model.bins[dest].family, copy=owner * 112 + port, offset=0)
    for key in (bi, bj):
        offset = 0
        indices = sorted((k for k, z in enumerate(roles) if bin_key(z) == key),
                         key=lambda k: (roles[k]["offset"], k))
        for k in indices:
            roles[k]["offset"] = offset
            offset += roles[k]["width"]
    return Model(roles, model.geo, model.windows, model.positions)


def positive_control(f):
    """A legal worsening swap must expose itself as a legal improving inverse."""
    model = f["model"]
    found = find_legal_swap(model, "strictly_worsening")
    if found is None:
        # Relaxed control: mute the landing rules so a capacity-worsening swap
        # is legal by fiat; the moment-sign machinery must still flip.
        relaxed = Model(model.roles, model.geo,
                        {k: (-10 ** 9, 10 ** 9) for k in model.windows}, model.positions)
        found = find_legal_swap(relaxed, "strictly_worsening", budget=200_000)
        require(found is not None, "no worsening swap even under muted landing rules")
        mode = "muted_landing_rules_synthetic_control"
    else:
        mode = "natural_legal_worsening_swap"
    i, j, checks = found
    changed = swap_roles(model, i, j)
    idle = Counter({r: len(keys) for r, keys in changed.by_remainder.items() if r})
    f["audit"].audit(model.geo, f["widths"], f["local"], changed.roles, f["plan"], idle, 16)
    result = census(changed)
    inverse = [c for c in result["improving_candidates"]
               if (c["role_index_a"], c["role_index_b"]) in ((i, j), (j, i))]
    require(len(inverse) == 1 and inverse[0]["rejection"] is None, "missed improving inverse")
    restored = swap_roles(changed, i, j)
    expected = Counter({int(r): n for r, n in f["baseline"]["idle"].items()})
    f["audit"].audit(model.geo, f["widths"], f["local"], restored.roles, f["plan"], expected, 16)
    require({key: b.remainder for key, b in restored.bins.items()}
            == {key: b.remainder for key, b in model.bins.items()}, "inverse changed remainders")
    return dict(mode=mode, pair_checks=checks,
                role_index_a=i, role_index_b=j,
                role_a=[model.roles[i]["stage"], model.roles[i]["replica"], model.roles[i]["helper"]],
                role_b=[model.roles[j]["stage"], model.roles[j]["replica"], model.roles[j]["helper"]],
                old_remainders=[model.bins[bin_key(model.roles[i])].remainder,
                                model.bins[bin_key(model.roles[j])].remainder],
                improving_inverse_detected=True, rejection_of_inverse=None,
                independent_owner_audit="passes_after_swap_and_inverse")


def packing_cap(f, raw):
    """The selected word's packing ceiling from the pinned ceiling calculator."""
    mod = types.ModuleType("packing_ceiling")
    mod.__file__ = str(ROOT / CEILING)
    exec(compile(raw[CEILING], mod.__file__, "exec"), mod.__dict__)
    lo, hi = mod.ceiling(f["local"], 73, 896, 9, 64)
    kap = hi / (1 + hi)
    return dict(source=CEILING, parameters=dict(m=73, families=896, stages=9, centre=64),
                local_profile={str(k): v for k, v in sorted(f["local"].items())},
                a_ceiling_bracket=[str(lo.numerator) + "/" + str(lo.denominator),
                                   str(hi.numerator) + "/" + str(hi.denominator)],
                a_ceiling_decimal=float(hi), kappa_cap_decimal=float(kap))


def fixture(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    raw = checked_sources(root, manifest)
    audit = types.ModuleType("pinned_owner_audit")
    audit.__file__ = str(root / AUDITOR)
    exec(compile(raw[AUDITOR], audit.__file__, "exec"), audit.__dict__)
    geo = audit.geometry(decode(raw, audit.TEMPLATE), decode(raw, audit.PHASES))
    word = decode(raw, audit.WORD.relative_to(root).as_posix())
    widths = audit.word_widths(word)
    roles = decode(raw, SOURCE_PACKAGE + "data/OWNERS.json.gz")
    plan = decode(raw, SOURCE_PACKAGE + "data/PLAN.json")
    spec = decode(raw, SOURCE_PACKAGE + "data/SPEC.json")
    local = audit.as_profile(word["report"]["local_profile"])
    provider = spec["providers"]["gauge44"]
    require(local == audit.as_profile(provider["expected_profile"]), "local profile mismatch")
    require(Counter(widths) == audit.as_profile(provider["inventory"]), "helper inventory mismatch")
    expected_idle = audit.as_profile(spec["expected"]["idle_remainder_profile"])
    baseline = audit.audit(geo, widths, local, roles, plan, expected_idle, 16)
    require(audit.as_profile(baseline["profile"]) == audit.as_profile(plan["profile"])
            == audit.as_profile(decode(raw, SOURCE_PACKAGE + "PROFILE.json")), "global profile mismatch")
    controls = audit.controls(geo, widths, local, roles, plan, expected_idle, 16)
    require(len(controls) == 11, "inherited owner controls incomplete")
    windows, positions = audit.windows(geo, [tuple(x) for x in plan["order"]])
    model = Model(roles, geo, windows, positions)
    return dict(model=model, audit=audit, widths=widths, local=local, plan=plan,
                baseline=baseline, owner_controls=controls, manifest=manifest, raw=raw)


def build(root=ROOT):
    f = fixture(root)
    result = census(f["model"])
    cap = packing_cap(f, f["raw"])
    legal = result["legal_strict_improvements"]
    status = ("PASS_PR1094_SWAP_CENSUS_OBSTRUCTION" if legal == 0
              else "PASS_PR1094_SWAP_CENSUS_GAIN")
    return dict(status=status,
                domain="unordered_two_role_whole_helper_swaps_fixed_calls_and_windows",
                exponent_domain="0<a<1",
                baseline_owner_audit=f["baseline"], census=result,
                packing_ceiling=cap,
                fraction_of_packing_cap_realized=(0.0 if legal == 0 else None),
                positive_control=positive_control(f),
                inherited_owner_controls=f["owner_controls"],
                input_sha256={r["path"]: r["sha256"] for r in f["manifest"]["files"]
                              if r["usage"] == "input"})


def check_certificate(result, data):
    require(canonical(result) == data, "certificate differs from complete regenerated census")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a regenerated certificate to a new path")
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    try:
        result = build()
        if args.write:
            with args.write.open("xb") as out:
                out.write(canonical(result))
        else:
            check_certificate(result, args.certificate.read_bytes())
        c = result["census"]
        print(result["status"], "pairs=" + str(c["total_unordered_role_pairs"]),
              "possible_gains=" + str(c["pair_classification"]["strictly_improving"]),
              "legal_gains=" + str(c["legal_strict_improvements"]),
              "positive_control=" + result["positive_control"]["mode"], "no_new_kappa")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
