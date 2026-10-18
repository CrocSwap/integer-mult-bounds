#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact one-role relocation census on the selected PR1094 owner map.

Prepared for @Arham-Tahir64 with substantial OpenAI Codex assistance.
Josie Elliston's pinned PR1091 audit supplies geometry and baseline admission;
the relocation enumeration and exponent-uniform comparison are new here.
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
                baseline=baseline, owner_controls=controls, manifest=manifest)


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

    def rejection(self, role, destination):
        """The moving role releases its old family in this invocation."""
        call = (role["stage"], role["replica"])
        lo, hi = self.windows[destination[:2]]
        if not lo < self.positions[call] < hi:
            return "outside_strict_source_event_window"
        pair = self.geo["place"][destination[1]][0]
        if (destination[0], pair) == (call[1], self.geo["stage_pair"][call[0]]):
            return "active_data_pair"
        occupied = self.families[role["time"]] - {role["family"]}
        if self.bins[destination].family in occupied:
            return "same_call_family_collision"
        return None


def compare(source_remainder, destination_remainder, width):
    """Sign of new minus old sum of r**(1-a), uniformly for 0<a<1."""
    require(all(type(x) is int for x in (source_remainder, destination_remainder, width)),
            "integer ranks required")
    require(source_remainder >= 0 and width > 0 and destination_remainder >= width,
            "capacity-infeasible transition")
    gap = source_remainder + width - destination_remainder
    return -1 if gap > 0 else (0 if gap == 0 else 1)


def census(model):
    """Count every capacity-feasible pair; materialize only possible gains."""
    source_classes = defaultdict(list)
    for index, role in enumerate(model.roles):
        source_classes[model.bins[bin_key(role)].remainder, role["width"]].append(index)
    classes, candidates = [], []
    for (rs, width), indices in sorted(source_classes.items()):
        for rd, destinations in sorted(model.by_remainder.items()):
            if rd < width:
                continue
            # If rs == rd, each role's own bin is present once and is excluded.
            pairs = len(indices) * (len(destinations) - int(rs == rd))
            if not pairs:
                continue
            sign = compare(rs, rd, width)
            classes.append(dict(source_remainder=rs, destination_remainder=rd, width=width,
                                source_roles=len(indices), destination_bins=len(destinations),
                                distinct_bin_pairs=pairs, moment_sign=sign))
            if sign >= 0:
                continue
            for index in indices:
                role = model.roles[index]
                source = bin_key(role)
                for destination in destinations:
                    if destination == source:
                        continue
                    lo, hi = model.windows[destination[:2]]
                    candidates.append(dict(
                        role_index=index, role=[role["stage"], role["replica"], role["helper"]],
                        call_time=role["time"], source=list(source), destination=list(destination),
                        width=width, old_remainders=[rs, rd], new_remainders=[rs + width, rd - width],
                        call_source_event_position=model.positions[role["stage"], role["replica"]],
                        destination_window=[lo, hi], rejection=model.rejection(role, destination)))
    totals = {name: sum(c["distinct_bin_pairs"] for c in classes if c["moment_sign"] == sign)
              for name, sign in (("strictly_improving", -1), ("neutral", 0), ("strictly_worsening", 1))}
    require(totals["strictly_improving"] == len(candidates), "incomplete improving census")
    return dict(roles=len(model.roles), bins=len(model.bins),
                bin_remainders=dict(sorted((r, len(keys)) for r, keys in model.by_remainder.items())),
                capacity_feasible_distinct_bin_pairs=sum(totals.values()), moment_classes=classes,
                pair_classification=totals, improving_candidates=candidates,
                rejection_counts=dict(sorted(Counter(c["rejection"] for c in candidates
                                                    if c["rejection"] is not None).items())),
                legal_strict_improvements=sum(c["rejection"] is None for c in candidates))


def relocate(model, index, destination):
    """Control only: move a whole role and compact the two slice prefixes."""
    role = model.roles[index]
    source = bin_key(role)
    require(destination != source, "same-bin move")
    require(model.bins[destination].remainder >= role["width"], "destination capacity")
    require(model.rejection(role, destination) is None, "illegal relocation")
    roles = [dict(z) for z in model.roles]
    owner, child, port = destination
    roles[index].update(owner_replica=owner, child=child, port=port,
                        family=model.bins[destination].family, copy=owner * 112 + port,
                        offset=model.bins[destination].used)
    for key in (source, destination):
        offset = 0
        indices = sorted((i for i, z in enumerate(roles) if bin_key(z) == key),
                         key=lambda i: (roles[i]["offset"], i))
        for i in indices:
            roles[i]["offset"] = offset
            offset += roles[i]["width"]
    return Model(roles, model.geo, model.windows, model.positions)


def positive_control(f):
    """A legal worsening move must expose its legal, improving inverse."""
    model = f["model"]
    selected = None
    for index, role in enumerate(model.roles):
        if model.bins[bin_key(role)].remainder != 0:
            continue
        for destination in model.by_remainder[48]:
            if model.rejection(role, destination) is None:
                selected = index, destination
                break
        if selected is not None:
            break
    require(selected is not None, "no real positive fixture found")
    index, destination = selected
    original = model.roles[index]
    source = bin_key(original)
    changed = relocate(model, index, destination)
    idle = Counter({r: len(keys) for r, keys in changed.by_remainder.items() if r})
    f["audit"].audit(model.geo, f["widths"], f["local"], changed.roles, f["plan"], idle, 16)
    result = census(changed)
    inverse = [c for c in result["improving_candidates"]
               if c["role_index"] == index and tuple(c["destination"]) == source]
    require(len(inverse) == 1 and inverse[0]["rejection"] is None, "missed improving inverse")
    restored = relocate(changed, index, source)
    expected = Counter({int(r): n for r, n in f["baseline"]["idle"].items()})
    f["audit"].audit(model.geo, f["widths"], f["local"], restored.roles, f["plan"], expected, 16)
    require({key: b.remainder for key, b in restored.bins.items()}
            == {key: b.remainder for key, b in model.bins.items()}, "inverse changed remainders")
    return dict(role_index=index, role=[original["stage"], original["replica"], original["helper"]],
                original_source=list(source), temporary_destination=list(destination),
                inverse=inverse[0], legal_improvements_detected=result["legal_strict_improvements"],
                independent_owner_audit="passes_after_move_and_inverse")


def build(root=ROOT):
    f = fixture(root)
    result = census(f["model"])
    require(result["legal_strict_improvements"] == 0, "selected map has a legal strict improvement")
    return dict(status="PASS_PR1094_SINGLE_RELOCATION_OBSTRUCTION", domain="one_whole_role_fixed_bins_and_windows",
                exponent_domain="0<a<1", baseline_owner_audit=f["baseline"], census=result,
                positive_control=positive_control(f), inherited_owner_controls=f["owner_controls"],
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
        print(result["status"], "capacity_pairs=" + str(c["capacity_feasible_distinct_bin_pairs"]),
              "possible_gains=" + str(c["pair_classification"]["strictly_improving"]),
              "legal_gains=0", "positive_inverse=PASS", "no_new_kappa")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
