#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact single and joint delivery checks; no full P104 schedule is claimed.

Each recorded chain starts with an independently supplied scalar query in H_b.
It replays one selected B word with monotone frame joins, the early cleanup
(tail), original full-frame cleanup, and explicit extra query cleanup. The
remaining six decoder terms, forming these queries, native transport recipes,
and global ownership are outside this certificate.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FULL = frozenset(range(512))


class VerificationError(ValueError):
    """A literal contract, endpoint, or source pin failed."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def span(basis):
    out = {0}
    for value in basis:
        require(type(value) is int and 0 < value < 512, "invalid frame vector")
        require(value not in out, "dependent frame basis")
        out |= {x ^ value for x in tuple(out)}
    return frozenset(out)


def join(left, right):
    out = set(left)
    for value in sorted(right):
        if value not in out:
            out |= {x ^ value for x in tuple(out)}
    return frozenset(out)


def dimension(frame):
    return len(frame).bit_length() - 1


def pairing(a, b):
    return (a & b).bit_count() % 2


def profile(values):
    return {str(k): v for k, v in sorted(values.items()) if v}


def difference(left, right):
    return Counter({k: left[k] - right[k] for k in set(left) | set(right)
                    if left[k] != right[k]})


def load_sources(data):
    for name, digest in data["source_sha256"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                "source hash mismatch: " + name)
    word = json.loads(gzip.decompress((ROOT / "research/complex-block-rank-optimum/inputs/selected.json.gz").read_bytes()))
    prototype = json.loads((ROOT / "research/frame-sa504/inputs/hamming/PROTOTYPE.json").read_text())
    fixture = json.loads((ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json").read_text())["section4_explicit_P104"]
    tau = lambda x: x ^ (43 if pairing(x, 43) else 0)
    root_index = {tuple(r): i for i, r in enumerate(prototype["root_lines"])}
    def convert(c):
        values = [sum(x * y for x, y in zip(c, r)) for r in fixture["F0"]]
        require(all(v % 4 == 0 for v in values), "nonintegral root conversion")
        return tuple(v // 4 for v in values)
    def canonical(r):
        return tuple(-x for x in r) if next(x for x in r if x) < 0 else r
    removed_labels = {tau(prototype["binary_ports"][root_index[canonical(convert(c))]])
                      for c in fixture["C"]}
    live = [i for i, label in enumerate(word["ports"]) if label not in removed_labels]
    require(len(live) == 104, "P104 puncture cardinality")
    root_by_label = {tau(q): r for q, r in zip(prototype["binary_ports"], prototype["root_lines"])}
    roots = [root_by_label[q] for q in word["ports"]]
    labels = [tau(q) for q in prototype["binary_ports"]]
    return word, prototype, live, roots, labels


def replay(word, prototype, live, roots, labels, chain=None):
    v = word["v"]
    n = 2 * v + word["R"]
    require((v, n, word["h"]) == (112, 704, 9), "selected word dimensions")
    frames = [span(f) for f in word["frames"]]
    live_outputs = {v + t for t in live}
    removed = [t for t in range(v) if t not in live]
    current = [frames[i] for i in word["start"]]
    terminal = [frames[i] for i in word["final"]]
    # The sixteen punctured port roles are retained as dirty helpers in both
    # the comparison baseline and the candidate, so this common cost cancels.
    for t in removed:
        current[t] = frozenset({0})
        terminal[v + t] = FULL
    baseline_terminal = list(terminal)
    coefficients = [Fraction(0)] * n
    paid = Counter()
    copy_paid = Counter()
    by_cut = defaultdict(list)
    query_frame = None
    copy_frame = None
    copy_label = None
    if chain is not None:
        ai, bi = chain["pair_hamming_root_indices"]
        require(0 <= ai < 120 and 0 <= bi < 120, "invalid root index")
        copy_label, query_label = labels[ai], labels[bi]
        query_frame = frozenset(x for x in range(512) if not pairing(x, query_label))
        require(copy_label in query_frame, "private endpoint outside query frame")
        copy_frame = query_frame
        for contact in chain["contacts"]:
            k, r = contact["before_B_event"], contact["register"]
            require(type(k) is int and 0 <= k < len(word["B"]), "invalid contact cut")
            require(type(r) is int and 0 <= r < n, "invalid contact role")
            by_cut[k].append(contact)
        for key, basis in chain["final_frame_overrides"].items():
            r = int(key)
            require(0 <= r < n and r not in live_outputs, "illegal terminal override")
            changed = span(basis)
            require(terminal[r] <= changed, "terminal override shrinks")
            terminal[r] = changed

    def climb(r, target, where):
        require(current[r] <= target, "nonmonotone public transport: " + str((where, r)))
        require(target <= terminal[r], "terminal frame exceeded: " + str((where, r)))
        rank = dimension(target) - dimension(current[r])
        if rank:
            paid[rank] += 1
        current[r] = target

    def event(e, where, promote=False):
        require(e[0] in {"add", "scale"}, "unknown scalar event")
        registers = e[1:3] if e[0] == "add" else e[1:2]
        require(all(type(r) is int and 0 <= r < n for r in registers), "invalid scalar role")
        if e[0] == "add":
            require(e[1] != e[2], "self addition")
        target = frames[e[-1]]
        if promote:
            for r in registers:
                target = join(target, current[r])
        for r in registers:
            climb(r, target, where)
        if e[0] == "add":
            coefficients[e[1]] += Fraction(e[3], e[4]) * coefficients[e[2]]
        else:
            coefficients[e[1]] *= Fraction(e[2], e[3])

    for k, e in enumerate(word["A"]):
        event(e, ("A", k))
    a_profile = paid.copy()
    paid.clear()
    for k, e in enumerate(word["B"]):
        for contact in by_cut[k]:
            target = span(contact["frame"])
            require(copy_label in target and target <= copy_frame,
                    "private copy does not descend to prescribed endpoint")
            rank = dimension(copy_frame) - dimension(target)
            if rank:
                copy_paid[rank] += 1
            copy_frame = target
            r = contact["register"]
            climb(r, target, ("query contact", k))
            coefficients[r] += Fraction(contact["coefficient"])
        event(e, ("B", k), chain is not None)
    if chain is not None:
        endpoint = frozenset({0, copy_label})
        require(endpoint <= copy_frame, "invalid private erasure frame")
        rank = dimension(copy_frame) - 1
        if rank:
            copy_paid[rank] += 1
        copy_frame = endpoint
        require(sum(k * m for k, m in copy_paid.items()) == 7, "private descent rank mass")
    for k, e in enumerate(word["tail"]):
        event(e, ("early cleanup", k), chain is not None)
    for r in range(n):
        climb(r, terminal[r], ("endpoint", r))
    for k, e in enumerate(word["cleanup"]):
        event(e, ("original full cleanup", k), chain is not None)
    if chain is not None:
        # The caller must also pay for the supplied query register's remaining
        # H_b -> FULL rank-one boundary. This is reported separately below.
        require(dimension(query_frame) == 8, "query entry rank")
        query_frame = FULL
        for c in chain["query_cleanup"]:
            r = c["register"]
            require(0 <= r < n and r not in live_outputs, "cleanup writes live output")
            require(current[r] == query_frame, "query cleanup is not in common FULL frame")
            coefficients[r] += Fraction(c["coefficient"])
        a = prototype["root_lines"][chain["pair_hamming_root_indices"][0]]
        wanted = {v + t: sum(x * y for x, y in zip(roots[t], a)) for t in live}
        require(all(coefficients[r] == wanted.get(r, 0) for r in range(n)),
                "query perturbation endpoint mismatch")
    else:
        require(not any(coefficients), "baseline query perturbation")
    residual = Counter(9 - dimension(terminal[r]) for r in range(2 * v, n)
                       if dimension(terminal[r]) < 9)
    changes = [{"register": r, "before_rank": dimension(baseline_terminal[r]),
                "after_rank": dimension(terminal[r])}
               for r in range(n) if terminal[r] != baseline_terminal[r]]
    return {"local_profile": paid, "A_profile": a_profile, "residual_width_profile": residual,
            "private_descent_profile": copy_paid, "terminal_changes": changes,
            "contact_count": len(chain["contacts"]) if chain else 0,
            "query_cleanup_count": len(chain["query_cleanup"]) if chain else 0,
            "removed_selected_positions": removed}


def verify_combined(sources, chains, baseline):
    """Replay both supplied queries together, including mutual frame effects."""
    word, prototype, live, roots, labels = sources
    v, n = word["v"], 2 * word["v"] + word["R"]
    frames = [span(f) for f in word["frames"]]
    current = [frames[i] for i in word["start"]]
    terminal = [frames[i] for i in word["final"]]
    for t in range(v):
        if t not in live:
            current[t] = frozenset({0})
            terminal[t + v] = FULL
    original_terminal = list(terminal)
    for chain in chains:
        for key, basis in chain["final_frame_overrides"].items():
            terminal[int(key)] = join(terminal[int(key)], span(basis))
    count = len(chains)
    rows = [[Fraction(0)] * count for _ in range(n)]
    paid = Counter()
    copies = []
    by_cut = defaultdict(list)
    for j, chain in enumerate(chains):
        ai, bi = chain["pair_hamming_root_indices"]
        copies.append(frozenset(x for x in range(512) if not pairing(x, labels[bi])))
        for contact in chain["contacts"]:
            by_cut[contact["before_B_event"]].append((j, contact))
    def climb(r, target):
        require(current[r] <= target <= terminal[r], "combined frame contract")
        rank = dimension(target) - dimension(current[r])
        if rank:
            paid[rank] += 1
        current[r] = target
    def event(e):
        registers = e[1:3] if e[0] == "add" else e[1:2]
        target = frames[e[-1]]
        for r in registers:
            target = join(target, current[r])
        for r in registers:
            climb(r, target)
        if e[0] == "add":
            rows[e[1]] = [x + Fraction(e[3], e[4]) * y for x, y in zip(rows[e[1]], rows[e[2]])]
        else:
            rows[e[1]] = [Fraction(e[2], e[3]) * x for x in rows[e[1]]]
    for e in word["A"]:
        event(e)
    paid.clear()
    for k, e in enumerate(word["B"]):
        for j, contact in by_cut[k]:
            target = span(contact["frame"])
            require(target <= copies[j], "combined private copy ascends")
            copies[j] = target
            r = contact["register"]
            climb(r, target)
            rows[r][j] += Fraction(contact["coefficient"])
        event(e)
    for e in word["tail"]:
        event(e)
    for r, target in enumerate(terminal):
        climb(r, target)
    for e in word["cleanup"]:
        event(e)
    for j, chain in enumerate(chains):
        for cleanup in chain["query_cleanup"]:
            r = cleanup["register"]
            require(current[r] == FULL, "combined cleanup outside FULL")
            rows[r][j] += Fraction(cleanup["coefficient"])
        a = prototype["root_lines"][chain["pair_hamming_root_indices"][0]]
        desired = {v + t: sum(x * y for x, y in zip(roots[t], a)) for t in live}
        require(all(rows[r][j] == desired.get(r, 0) for r in range(n)), "combined scalar endpoint")
    residual = Counter(9 - dimension(terminal[r]) for r in range(2 * v, n)
                       if dimension(terminal[r]) < 9)
    local_delta = difference(paid, baseline["local_profile"])
    residual_delta = difference(residual, baseline["residual_width_profile"])
    mass_delta = sum(k * m for k, m in local_delta.items()) + sum(k * m for k, m in residual_delta.items())
    require(mass_delta == 0, "combined public plus residual rank mass")
    return {"query_count": count, "all_query_coefficients_exact": True,
            "all_other_query_perturbations_zero": True,
            "local_B_tail_endpoint_cleanup_profile_delta": profile(local_delta),
            "residual_width_profile_delta": profile(residual_delta),
            "public_plus_residual_rank_mass_delta": mass_delta,
            "private_descent_mass": 7 * count,
            "private_copy_lifetimes": [{"copy": j, "initialized_before_B_event": 0,
                                         "discarded_after_B_contact": max(c["before_B_event"] for c in chain["contacts"])}
                                        for j, chain in enumerate(chains)],
            "peak_simultaneous_private_copies": count,
            "external_query_registers_required": count,
            "global_owner_hosting_verified": False,
            "supplied_query_remaining_boundary_profile": {"1": count},
            "changed_terminal_roles": [r for r in range(n) if terminal[r] != original_terminal[r]]}


def verify(data=None, controls=True):
    if data is None:
        data = json.loads((HERE / "CHAINS.json").read_text())
    require(data["schema"] == "p104-interleaved-delivery-v1", "unknown schema")
    sources = load_sources(data)
    baseline = replay(*sources)
    baseline_recount = baseline["A_profile"] + baseline["local_profile"] + Counter({8: 8})
    inherited = Counter({int(k): v for k, v in sources[0]["local_profile"].items()})
    require(baseline_recount == inherited + Counter({1: 16}),
            "retained sixteen-helper baseline differs from selected invoice")
    reports = []
    for chain in data["chains"]:
        out = replay(*sources, chain)
        local_delta = difference(out["local_profile"], baseline["local_profile"])
        residual_delta = difference(out["residual_width_profile"], baseline["residual_width_profile"])
        mass_delta = sum(k * m for k, m in local_delta.items()) + sum(k * m for k, m in residual_delta.items())
        require(mass_delta == 0, "public plus residual rank mass changed")
        reports.append({"pair_hamming_root_indices": chain["pair_hamming_root_indices"],
                        "contact_count": out["contact_count"],
                        "query_cleanup_count": out["query_cleanup_count"],
                        "private_descent_profile": profile(out["private_descent_profile"]),
                        "private_descent_mass": 7,
                        "supplied_query_remaining_boundary_profile": {"1": 1},
                        "local_B_tail_endpoint_cleanup_profile_delta": profile(local_delta),
                        "residual_width_profile_delta": profile(residual_delta),
                        "public_plus_residual_rank_mass_delta": mass_delta,
                        "terminal_changes": out["terminal_changes"],
                        "all_live_output_query_coefficients_exact": True,
                        "all_other_query_perturbations_zero": True})
    control_results = {}
    if controls:
        for name in ("corrupt_contact_coefficient", "drop_query_cleanup", "drop_terminal_frame_overrides"):
            altered = deepcopy(data["chains"][0])
            if name == "corrupt_contact_coefficient":
                altered["contacts"][0]["coefficient"] = str(Fraction(altered["contacts"][0]["coefficient"]) + 1)
            elif name == "drop_query_cleanup":
                altered["query_cleanup"].pop()
            else:
                altered["final_frame_overrides"] = {}
            try:
                replay(*sources, altered)
            except VerificationError as error:
                expected = "terminal frame exceeded" if name == "drop_terminal_frame_overrides" else "query perturbation endpoint mismatch"
                require(expected in str(error), "control failed for unrelated reason")
                control_results[name] = "rejected: " + str(error)
            else:
                raise VerificationError("negative control was accepted: " + name)
    return {"schema": "p104-single-query-delivery-report-v1", "source_sha256": data["source_sha256"],
            "scope": "One exact two-query delivery perturbation channel on a modified selected B schedule, with separate and joint invoices; no eight-query program or improved kappa.",
            "query_input_contract": "One independent exact scalar q already available in H_b; forming q, its dirty-input compensation, and its initial boundary are not included. Its remaining H_b-to-FULL boundary is one rank-one child per query.",
            "removed_selected_positions": baseline["removed_selected_positions"],
            "retained_role_baseline_profile_delta_from_selected": {"1": 16},
            "chains": reports, "combined_two_query_channel": verify_combined(sources, data["chains"], baseline), "negative_controls": control_results}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
