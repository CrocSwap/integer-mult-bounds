#!/usr/bin/env python3
"""Independent complete G20 census using per-cut active histograms.

Reuses only the authenticated, independently written frozen oracle kernel.
The primary census and predecessor executables are authenticated as data only.
No full-cut matrix archive is built. No price or typed-continuation claim is
inferred from the necessary normalized pairing conditions.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
FROZEN = {
    "SOURCE-PINS.json": "bb0272a4bc86649177ee229e6e6b9fc6ba37edc8cb240fda6cef4ade272f0b61",
    "verify_excess.py": "519029e6783bff1845e97f81c7cc92377b64a179f46021274ba6104a6163055f",
    "oracle_witness.py": "0a6c57687e5ef9e27db672793549f2253b0899b01ff179553bf52f8382071dee",
    "RESULT.json": "c28cd4c7d375ea551a294d364f5b4fcf784b9bbf504dc836e46e53a0fee4f8e1",
    "ORACLE.json": "b726e0c8e7350226a701c9eed4c53537e81d355a91e1b7904b37a5845e934248",
    "PROOF.md": "381a9736e234b8726b7f8fb389cab72a6b97f7d6838bc2f99597c20cf9b17be3",
    "sources/FRAMES.json": "0d99fc6b8f45c03dfba5252a03dd9e7fe23be3a7593dfe15368e34da6629a654",
    "sources/NOTICE.md": "a4fdb5e2dfeeb216f3f58417891fc0a084c218d9a75228fb977e3cb82973be72",
    "sources/PATHS.json": "f4dd58b78121040b1f054c0f7a626b25f6ef8d39f3de044d3456ea7dea8a6a5e",
    "sources/WORD.json.gz": "8dd441fdb9c8923df06eb5ebfda37d03e4539f2305763e688d8c7025d196c4b1",
    "sources/gap-PROOF.md": "121649b47271f45e18a1053ca5615c94e1cc81cc42136d8ccf3b2dca7d93f706",
    "sources/gap-source.py": "91e201fd3c96267c878863abba794a16025070c98145ae598ee0ed7383c7f9c6",
    "sources/prior-PROOF.md": "af88b44f1c61fb91d63ace7a2ece8d798bf6378864b2c4e1d44e01070fd485db",
    "sources/prior-source.py": "a9aea8b108ebbeae8041770cefecfdabdfaf91b72ba7b5cfa2ff13408f1d16dd",
    "sources/source-README.md": "e443b2fd7b988316953bfc7d21045690ea0d3ce9069ce1a06880f6ccfc7ec054",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def load_kernel():
    payloads = {}
    for name, sha in FROZEN.items():
        raw = (ROOT / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == sha, "Frozen scientific sha256 mismatch: " + name)
        if name == "oracle_witness.py":
            payloads[name] = raw
    namespace = {"__name__": "authenticated_independent_witness_kernel", "__file__": str(ROOT / "oracle_witness.py")}
    exec(compile(payloads["oracle_witness.py"], namespace["__file__"], "exec"), namespace)
    return namespace


def span_solver(rows):
    """Lowest-pivot row span with explicit source coefficients."""
    pivots = {}
    for index, source in enumerate(rows):
        value, coefficients = source, 1 << index
        while value:
            pivot = (value & -value).bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = (value, coefficients)
                break
            old, combination = pivots[pivot]
            value ^= old
            coefficients ^= combination
    return pivots


def solve(pivots, value):
    coefficients = 0
    while value:
        pivot = (value & -value).bit_length()-1
        if pivot not in pivots:
            return None
        old, combination = pivots[pivot]
        value ^= old
        coefficients ^= combination
    return coefficients


def format_profile(profile):
    return {"base": list(profile[:4]), "singleton": list(profile[4:8]),
            "augmented": list(profile[8:12]),
            "inherited_pivot_quotient": None if profile[12] < 0 else list(profile[12:14])}


class Census:
    def __init__(self, kernel):
        self.k = kernel
        data = kernel["source_inputs"]()
        self.word = data["WORD.json.gz"]
        self.spaces = kernel["frame_geometry"](data["FRAMES.json"])
        self.edges = kernel["route_edges"](data["PATHS.json"], self.spaces)
        self.start, self.final, self.owned, self.events = kernel["word_contract"](self.word, self.spaces)
        self.n = len(self.start)
        self.full = (1 << self.n)-1
        representatives = {}
        for frame, space in sorted(self.spaces.items()):
            representatives.setdefault(space, frame)
        self.shape = {frame: representatives[space] for frame, space in self.spaces.items()}
        self.shape[None] = None
        grouped = defaultdict(list)
        for role in range(222, self.n):
            if role not in self.owned:
                grouped[(self.spaces[self.start[role]], self.spaces[self.final[role]])].append(role)
        self.groups = sorted(grouped.values(), key=lambda members: tuple(members))
        self.gid = {role: g for g, members in enumerate(self.groups) for role in members}
        require(sum(map(len, self.groups)) == 415, "Complete public helper domain")
        self.outside = {g: self.full ^ sum(1 << h for h in members) for g, members in enumerate(self.groups)}
        self.legal = defaultdict(lambda: defaultdict(dict))
        self.incoming = defaultdict(list)
        for g, members in enumerate(self.groups):
            entrance, exit_space = self.spaces[self.start[members[0]]], self.spaces[self.final[members[0]]]
            for source, target, rank in sorted(self.edges):
                middle = self.spaces[target]
                if len(exit_space) < len(middle) < len(entrance) and kernel["contains"](entrance, middle) and kernel["contains"](middle, exit_space):
                    require(target not in self.legal[g][source], "Unique literal source/target edge")
                    self.legal[g][source][target] = rank
                    self.incoming[self.shape[target]].append((g, source, target, rank))
        self.rows = [1 << i for i in range(self.n)]
        self.columns = [1 << i for i in range(self.n)]
        self.erased = {}
        for index in reversed(range(len(self.events))):
            event = self.events[index]
            op, dest = event[:2]
            if op == "ADD":
                self.columns[event[2]] ^= self.columns[dest]
            elif op == "ERASE":
                self.erased[index] = self.columns[dest]
                self.columns[dest] = 0
        self.state = self.start[:]
        self.banks = defaultdict(set)
        for role, frame in enumerate(self.state):
            if frame is not None:
                self.banks[self.shape[frame]].add(role)
        self.members_at = defaultdict(lambda: defaultdict(set))
        for h, g in self.gid.items():
            self.members_at[g][self.state[h]].add(h)
        # Geometry-only source-frame multiplicities and occupied outgoing degree
        # provide an independent count of the domain at every cut.
        self.degree = defaultdict(int)
        for shape, incoming in self.incoming.items():
            if self.banks[shape]:
                for g, source, _target, _rank in incoming:
                    self.degree[g, source] += 1
        self.base_cache = {}
        self.active = {}
        self.keys_by_shape = defaultdict(set)
        self.keys_by_member = defaultdict(set)
        self.histogram = Counter()
        self.positive = Counter()
        self.weighted = Counter()
        self.weighted_positive = Counter()
        self.first_positive = {}
        self.coverage = hashlib.sha256()
        self.histogram_digest = hashlib.sha256()
        self.total_domain = 0
        self.peak_contexts = 0
        self.context_evaluations = 0
        self.base_evaluations = 0
        self.cut_count = 0
        self.direct_cuts = sorted({0, len(self.events), 7670} | {t for i, e in enumerate(self.events) if e[0] == "ERASE" for t in (i, i+1)})
        self.reference_prefix, self.reference_suffix, self.reference_headers = kernel["traces"](self.word, self.spaces, self.direct_cuts)

    def base(self, g, shape):
        key = (g, shape)
        if key in self.base_cache:
            return self.base_cache[key]
        self.base_evaluations += 1
        slots = sorted(self.banks[shape])
        p, s = [self.rows[h] for h in slots], [self.columns[h] for h in slots]
        mask = self.outside[g]
        pm, sm = [v & mask for v in p], [v & mask for v in s]
        left, right = self.k["kernels"](pm), self.k["kernels"](sm)
        inputs, outputs, boundary, internal = self.k["matrices"](left, right, p, s)
        base = {"slots": slots, "p": p, "s": s, "left": left, "right": right,
                "inputs": inputs, "outputs": outputs, "C": boundary, "D": internal,
                "C_rank": self.k["rank"](boundary), "D_rank": self.k["rank"](internal),
                "p_solver": span_solver(pm), "s_solver": span_solver(sm), "memo": {}}
        require(len(base["p_solver"])+len(left) == len(slots) and len(base["s_solver"])+len(right) == len(slots), "Independent bank span rank")
        self.base_cache[key] = base
        return base

    def extension_profile(self, g, shape, h):
        base = self.base(g, shape)
        p, s, mask = self.rows[h], self.columns[h], self.outside[g]
        memo_key = (p, s)
        if memo_key in base["memo"]:
            return base["memo"][memo_key]
        self.context_evaluations += 1
        pm, sm = p & mask, s & mask
        lp, rp = solve(base["p_solver"], pm), solve(base["s_solver"], sm)
        has_left, has_right = lp is not None, rp is not None
        combine, dot, rank = self.k["xor_combine"], self.k["dot"], self.k["rank"]
        c = p ^ combine(base["p"], lp) if has_left else 0
        d = s ^ combine(base["s"], rp) if has_right else 0
        require(not (c & mask) and not (d & mask), "Complete augmented image support")
        lcount, rcount = len(base["left"]), len(base["right"])
        boundary = list(base["C"])
        internal = list(base["D"])
        if has_right:
            for i in range(lcount):
                boundary[i] |= dot(base["inputs"][i], d) << rcount
                internal[i] |= dot(base["left"][i], rp) << rcount
        if has_left:
            crow = sum(dot(c, v) << j for j, v in enumerate(base["outputs"]))
            irow = sum(dot(lp, v) << j for j, v in enumerate(base["right"]))
            if has_right:
                crow |= dot(c, d) << rcount
                irow |= (dot(lp, rp) ^ 1) << rcount
            boundary.append(crow)
            internal.append(irow)
        cl, cr = int(pm == 0), int(sm == 0)
        singleton_C = dot(p, s) if cl and cr else 0
        singleton_D = int(bool(cl and cr))
        quotient_C = quotient_D = -1
        if singleton_C:
            # The selected extension vectors are e_h because solve(0)=0.
            # Thus clearing the singleton boundary pivot is exactly a rank-one
            # Schur update of BOTH actual forms; no internal identity is assumed.
            cross_left = [dot(v, s) for v in base["inputs"]]
            cross_right = sum(dot(p, v) << j for j, v in enumerate(base["outputs"]))
            qc = [v ^ (cross_right if cross_left[i] else 0) for i, v in enumerate(base["C"])]
            qd = [v ^ (cross_right if cross_left[i] else 0) for i, v in enumerate(base["D"])]
            quotient_C, quotient_D = rank(qc), rank(qd)
            require(quotient_C+1 == rank(boundary), "Inherited singleton boundary debit")
        profile = (lcount, rcount, base["C_rank"], base["D_rank"],
                   cl, cr, singleton_C, singleton_D,
                   lcount+int(has_left), rcount+int(has_right), rank(boundary), rank(internal), quotient_C, quotient_D)
        base["memo"][memo_key] = profile
        return profile

    def evaluate(self, key):
        g, h, target = key
        source = self.state[h]
        rank = self.legal[g].get(source, {}).get(target)
        shape = self.shape[target]
        if rank is None or not self.banks[shape] or h in self.banks[shape]:
            return None
        return self.extension_profile(g, shape, h), (source, target, rank)

    @staticmethod
    def excess(profile):
        return profile[10] > max(profile[2], profile[6])

    def positive_key(self, g, edge, profile):
        return (g,) + edge + profile

    def replace(self, key, t):
        g, h, target = key
        shape = self.shape[target]
        old = self.active.pop(key, None)
        if old is not None:
            profile, edge = old
            self.histogram[g, profile] -= 1
            if not self.histogram[g, profile]:
                del self.histogram[g, profile]
            if self.excess(profile):
                category = self.positive_key(g, edge, profile)
                self.positive[category] -= 1
                if not self.positive[category]:
                    del self.positive[category]
            self.keys_by_shape[shape].discard(key)
            self.keys_by_member[h].discard(key)
        current = self.evaluate(key)
        if current is None:
            return
        profile, edge = current
        self.active[key] = current
        self.histogram[g, profile] += 1
        self.keys_by_shape[shape].add(key)
        self.keys_by_member[h].add(key)
        if self.excess(profile):
            category = self.positive_key(g, edge, profile)
            self.positive[category] += 1
            if category not in self.first_positive:
                self.first_positive[category] = {"cut_t": t, "field": h, "bank": sorted(self.banks[shape])}

    def keys_for_shape(self, shape):
        for g, source, target, _rank in self.incoming[shape]:
            for h in self.members_at[g].get(source, ()):
                yield g, h, target

    def keys_for_member(self, h):
        g = self.gid[h]
        for target in self.legal[g].get(self.state[h], {}):
            if self.banks[self.shape[target]]:
                yield g, h, target

    def weight_cut(self, t):
        if t in self.reference_prefix:
            require(self.rows == self.reference_prefix[t] and self.columns == self.reference_suffix[t]
                    and self.state == self.reference_headers[t], "Direct full-map/header checkpoint mismatch at cut" + str(t))
        geometric_count = sum(len(members)*self.degree[g, source]
                              for g, by_source in self.members_at.items()
                              for source, members in by_source.items() if members)
        active_count = sum(self.histogram.values())
        require(active_count == len(self.active) == geometric_count, "Per-cut independent geometry/domain coverage")
        require(all(count > 0 for count in self.histogram.values()) and all(count > 0 for count in self.positive.values()), "Positive active histogram counts")
        self.total_domain += geometric_count
        self.peak_contexts = max(self.peak_contexts, active_count)
        self.weighted.update(self.histogram)
        self.weighted_positive.update(self.positive)
        self.coverage.update((str(t)+":"+str(geometric_count)+"\n").encode())
        self.histogram_digest.update((canonical([t, [[g, list(p), n] for (g, p), n in sorted(self.histogram.items())]])+"\n").encode())
        self.cut_count += 1

    def run(self):
        initial_keys = set()
        for shape, bank in self.banks.items():
            if bank:
                initial_keys.update(self.keys_for_shape(shape))
        for key in sorted(initial_keys):
            self.replace(key, 0)
        self.weight_cut(0)
        for index, event in enumerate(self.events):
            op, dest = event[:2]
            touched = {dest}
            if op == "ADD":
                touched.add(event[2])
            dirty_shapes = {self.shape[self.state[h]] for h in touched} - {None}
            affected = set()
            for shape in dirty_shapes:
                affected.update(self.keys_by_shape[shape])
            changed_members = touched & self.gid.keys()
            for h in changed_members:
                affected.update(self.keys_by_member[h])
            old_occupied = {shape: bool(self.banks[shape]) for shape in dirty_shapes}
            oldframe = self.state[dest]
            if op == "ADD":
                source, frame = event[2:]
                require(self.state[dest] == self.state[source] == frame, "Streamed ADD exact common frame")
                self.rows[dest] ^= self.rows[source]
                self.columns[source] ^= self.columns[dest]
            elif op == "ERASE":
                require(dest in self.owned, "Streamed owned erasure")
                self.rows[dest] = 0
                require(self.columns[dest] == 0, "Erasure suffix before projection")
                self.columns[dest] = self.erased[index]
                self.state[dest] = event[2]
            elif op == "INIT":
                require(dest in self.owned and self.rows[dest] == 0, "Streamed whole-zero owned INIT")
                self.state[dest] = event[2]
            else:
                source, target, rank = event[2:]
                require(self.state[dest] == source and (source, target, rank) in self.edges, "Streamed query route/source")
                if op == "ZERO_Q":
                    require(self.rows[dest] == 0, "Streamed whole-zero ZERO_Q")
                self.state[dest] = target
            newframe = self.state[dest]
            if oldframe != newframe:
                oldshape, newshape = self.shape[oldframe], self.shape[newframe]
                for shape in (oldshape, newshape):
                    if shape is not None:
                        old_occupied.setdefault(shape, bool(self.banks[shape]))
                        affected.update(self.keys_by_shape[shape])
                        dirty_shapes.add(shape)
                if oldshape is not None:
                    self.banks[oldshape].remove(dest)
                if newshape is not None:
                    self.banks[newshape].add(dest)
                if dest in self.gid:
                    g = self.gid[dest]
                    self.members_at[g][oldframe].remove(dest)
                    self.members_at[g][newframe].add(dest)
            for shape in dirty_shapes:
                change = int(bool(self.banks[shape]))-int(old_occupied[shape])
                if change:
                    for g, source, _target, _rank in self.incoming[shape]:
                        self.degree[g, source] += change
                for g in range(len(self.groups)):
                    self.base_cache.pop((g, shape), None)
                affected.update(self.keys_for_shape(shape))
            for h in changed_members:
                affected.update(self.keys_for_member(h))
            for key in sorted(affected):
                self.replace(key, index+1)
            self.weight_cut(index+1)
        require(self.state == self.final and self.columns == [1 << i for i in range(self.n)], "Streamed final headers/suffix identity")
        require(all(self.rows[h] == 0 for h in self.owned), "Streamed final owned normalized zero")
        require(self.cut_count == 14795 and self.total_domain == 386278548,
                "Complete frozen386278548-case domain")
        require(sum(self.weighted.values()) == self.total_domain, "Full weighted distribution closure")
        self.validate_positive_first_contexts()
        self.synthetic_algebra_control = self.validate_nonzero_schur_control()
        return self.receipt()

    def validate_nonzero_schur_control(self):
        # A synthetic two-coordinate example forces a NONZERO outer-product
        # correction in both forms. It is not a source census context.
        probe = Census.__new__(Census)
        probe.k, probe.rows, probe.columns = self.k, [1, 2], [2, 3]
        probe.outside, probe.banks = {0: 0}, {0: {0}}
        probe.base_cache = {}
        probe.base_evaluations = probe.context_evaluations = 0
        observed = probe.extension_profile(0, 0, 1)
        full = []
        for slots in ([0], [1], [0, 1]):
            view, left, right, p, s = self.k["bank_view"](probe.rows, probe.columns, slots, 0)
            full.extend(view[name] for name in ("left_kernel_dimension", "right_kernel_dimension", "boundary_rank", "internal_rank"))
        quotient = self.k["inherited_quotient"](left, right, p, s, [0, 1], 1, 0)
        require(quotient["available"], "Synthetic inherited pivot availability")
        full.extend((quotient["boundary_rank"], quotient["internal_rank_on_actual_changed_bases"]))
        expected = (1, 1, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 1, 0)
        require(observed == tuple(full) == expected, "Nonzero inherited Schur update versus full frozen kernel")
        return {"synthetic_not_source_case": True, "prefix_rows": [1, 2], "suffix_columns": [2, 3],
                "base_slots": [0], "added_role": 1, "outside_mask": 0,
                "checked_profile": format_profile(observed), "full_frozen_kernel_comparison": "PASS"}

    def validate_positive_first_contexts(self):
        cuts = sorted({spec["cut_t"] for spec in self.first_positive.values()})
        require(len(cuts) <= 1024, "Direct positive-class check snapshot resource bound")
        prefix, suffix, headers = self.k["traces"](self.word, self.spaces, cuts)
        digest = hashlib.sha256()
        for key, first in sorted(self.first_positive.items()):
            g, source, target, paid_rank, *items = key
            spec = dict(first, edge=[source, target, paid_rank])
            t = spec["cut_t"]
            view = self.k["checkpoint"](spec, self.word, self.spaces, self.edges, prefix[t], suffix[t], headers[t])
            require(view["group_members"] == self.groups[g], "Direct class actual-member group mapping")
            profile = []
            for name in ("base", "singleton", "augmented"):
                part = view[name]
                profile.extend(part[field] for field in ("left_kernel_dimension", "right_kernel_dimension", "boundary_rank", "internal_rank"))
            quotient = view["inherited_pivot_quotient"]
            profile.extend((quotient["boundary_rank"], quotient["internal_rank_on_actual_changed_bases"]) if quotient["available"] else (-1, -1))
            require(profile == items, "Direct complete augmented-kernel/form class check")
            require(view["boundary_excess_over_both"] > 0 and view["augmented"]["simultaneous_unit_pair"] is not None,
                    "Every positive class first context has direct simultaneous unit witness")
            digest.update((canonical([g, spec, profile])+"\n").encode())
        self.positive_direct_validation = {"class_context_count": len(self.first_positive),
            "direct_reconstruction_cut_t": cuts, "class_context_sha256": digest.hexdigest(),
            "method": "Independent frozen traces reconstruct full original prefix/suffix maps, then full bank_view kernels/forms and simultaneous unit witness via checkpoint(), for every positive edge/profile class first context."}

    def receipt(self):
        ranks = [{"group_index": g, "profile": format_profile(p), "weighted_cases": count}
                 for (g, p), count in sorted(self.weighted.items())]
        classes = []
        dimension_counts = Counter()
        for key, count in sorted(self.weighted_positive.items()):
            g, source, target, paid_rank, *items = key
            profile = tuple(items)
            source_dim, target_dim = len(self.spaces[source]), len(self.spaces[target])
            dimension_counts[g, source_dim, target_dim, paid_rank] += count
            classes.append({"group_index": g, "edge": [source, target, paid_rank],
                            "source_dimension": source_dim, "target_dimension": target_dim,
                            "profile": format_profile(profile), "weighted_cases": count,
                            "first_checkpoint": self.first_positive[key]})
        groups = [{"index": g, "members": members,
                   "entrance_dimension": len(self.spaces[self.start[members[0]]]),
                   "exit_dimension": len(self.spaces[self.final[members[0]]])}
                  for g, members in enumerate(self.groups)]
        return {"schema_version": 1, "status": "PASS_INDEPENDENT_COMPLETE_NORMALIZED_PAIRING_CENSUS",
                "frozen_scientific_sha256": FROZEN, "kernel_reuse": "Authenticated frozen independent oracle_witness.py; not a third unrelated engine",
                "coverage_method": "Subtract/add changed context categories in active histograms, then weight every full histogram at each cut; separate geometry multiplicities count each cut's domain.",
                "elimination_method": "Authenticated own-kernel lowest-pivot eligible kernels for current banks, with explicit coefficient-span bordering for augmented kernels; full direct kernels/forms cross-check every positive class first context.",
                "groups": groups, "cut_count": self.cut_count, "weighted_domain": self.total_domain,
                "per_cut_domain_sha256": self.coverage.hexdigest(), "per_cut_active_histogram_sha256": self.histogram_digest.hexdigest(),
                "peak_active_contexts": self.peak_contexts, "bank_state_evaluations": self.base_evaluations,
                "distinct_extension_evaluations": self.context_evaluations,
                "direct_checkpoint_validation": {"cut_t": self.direct_cuts, "count": len(self.direct_cuts),
                    "maps_and_headers_compared": "Every685 prefix row,685 suffix column and685 current header at opening,end,witness7670 and both sides of every96 ownedERASE records"},
                "positive_class_direct_validation": self.positive_direct_validation,
                "nonzero_inherited_schur_control": self.synthetic_algebra_control,
                "rank_profile_distribution": ranks,
                "positive_excess_weighted_cases": sum(self.weighted_positive.values()),
                "positive_edge_profile_classes": classes,
                "positive_dimension_classes": [{"group_index": key[0], "source_dimension": key[1], "target_dimension": key[2],
                    "paid_rank": key[3], "weighted_cases": count} for key, count in sorted(dimension_counts.items())],
                "limits": ["Complete only for the frozen published-one-edge member-to-entire-occupied-bank normalized domain; arbitrary new routes/word rewrites are not enumerated.",
                    "Boundary excess is rank(S+h)>max(rankS,rank{h}); internal pairing and inherited quotient ranks are reported separately.",
                    "A positive pairing gate supplies no additional productive target, typed continuation, native/physical erasure permission or profitable invoice.",
                    "No price theorem, ordinary/compiler/outer admission, newkappa or selected frontier change is supplied."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    kernel = load_kernel()
    result = Census(kernel).run()
    if args.emit:
        print(canonical(result))
    else:
        receipt = ROOT / "FULL-CENSUS.json"
        require(receipt.is_file(), "Retained receipt FULL-CENSUS.json required")
        require(canonical(kernel["decode"](receipt.read_bytes())) == canonical(result), "Retained full-census receipt mismatch")
        print("PASS independent complete normalized G20 census receipt")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        sys.exit(1)
