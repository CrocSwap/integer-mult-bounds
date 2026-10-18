#!/usr/bin/env python3
"""Independent literal composed-word nomination check; imports no nominator.

Derived from PR569 f20a68b4b126780419c292571411022bb1d006d6,
research/larger-gain/geometry/review_width7_nomination.py (Apache-2.0).
Prepared with OpenAI Codex assistance. Changes: explicit provider directories,
two composed-provider IDs, variable dispatch counts, and explicit runtime plan/owner
inputs. Complete provider artifact pins are required. Geometry checks unchanged.
Original source SHA256: 51f69958e1d4e965830c73c5d4666a9c2ac4329e0dcd3e92b81c22b1558cf72c.
"""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def review(base, plan_path, owners_path, nomination_receipt, provider_dirs):
    if not __debug__:
        raise RuntimeError('Assertions required for literal geometry verification')
    template_path = base / "split-centres/GLOBAL-TEMPLATE.json.gz"
    phase_path = base / "work/complex-nine-native/DATA-PHASES.json"
    parent, phase = read(template_path), read(phase_path)
    plan, roles, nominal = read(plan_path), read(owners_path), read(nomination_receipt)
    assert sha(owners_path) == nominal["owners_sha256"] == plan["assignment_sha256"]
    order = [tuple(row) for row in plan["order"]]
    assert len(order) == len(set(order)) == 72
    assert set(order) == {(stage, replica) for stage in range(9) for replica in range(8)}
    calls = {(call["stage"], call["replica"]): call for call in parent["calls"]}
    capacities = {child["child"]: child["rank"] for child in parent["idle_children"]}
    assert set(capacities) == set(range(18))

    # Project each whole invocation's actual event block onto its nominated
    # replica. No claimed window or family formula is used to create windows.
    blocks = {}
    stage = None
    for event in parent["execution_schedule"]:
        if event["kind"] in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue
        if event["kind"] == "local_cover_sweep":
            stage = event["stage"]
            blocks[stage] = []
        assert stage is not None
        blocks[stage].append(event)
    sequence = [(time, replica, event) for time, (stage, replica) in enumerate(order)
                for event in blocks[stage]]
    stage_pairs = {event["stage"]: event["pair"] for event in parent["recipe"]
                   if event["kind"] == "local"}
    last_touch, windows, positions, geometry = {}, {}, {}, {}
    per_replica = defaultdict(list)
    for position, (time, replica, event) in enumerate(sequence):
        per_replica[replica].append(event)
        if event["kind"] == "local_cover_sweep":
            stage = event["stage"]
            assert order[time] == (stage, replica)
            positions[time] = position
            last_touch[replica, stage_pairs[stage]] = position
        elif event["kind"] == "bridge":
            for pair in (event["src"], event["dst"]):
                last_touch[replica, pair] = position
        elif event["kind"] == "idle_cover_sweep":
            for side, child in enumerate(event["child_indices"]):
                if child not in capacities:
                    continue
                geometry[child] = event["pair"], side
                windows[replica, child] = last_touch.get((replica, event["pair"]), -1), position
    source_events = [event for event in parent["execution_schedule"]
                     if event["kind"] not in ("bank_padding_cover_sweep", "translate_every_live_family")]
    assert all(events == source_events for events in per_replica.values())
    assert len(windows) == 144
    for (replica, child), (left, right) in windows.items():
        times = [time for time, position in positions.items() if left < position < right]
        assert plan["windows"][f"{replica},{child}"] == [capacities[child], times]
        pair, side = geometry[child]
        assert plan["pairs"][str(child)] == pair and plan["sides"][str(child)] == side

    assert set(provider_dirs) == set(plan["provider_registry"]) == {"eightcold_eight", "width7_eight"}
    providers, source_hashes = {}, {}
    for pid, directory in provider_dirs.items():
        desc = plan["provider_registry"][pid]
        for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz", "LOCAL-CHECKS.json",
                     "INDEPENDENT-LOCAL-REPLAY.json", "CLIFFORD-RECIPES.json", "CLIFFORD-REVIEW.json",
                     "RESIDUAL-ADAPTERS.json"):
            actual_hash = sha(directory / name)
            assert actual_hash == desc["artifact_sha256"][name]
            source_hashes[str((directory / name).resolve())] = actual_hash
        word = read(directory / "CANONICAL-WORD.json.gz")
        programs = read(directory / "LOCAL-PROGRAMS.json.gz")
        checks = read(directory / "LOCAL-CHECKS.json")
        replay = read(directory / "INDEPENDENT-LOCAL-REPLAY.json")
        phase_review = read(directory / "CLIFFORD-REVIEW.json")
        widths = [9 - len(word["frames"][frame]) for frame in word["start"][224:]]
        assert (word["v"], word["h"], word["R"]) == (112, 9, 504)
        assert widths == desc["widths"] and len(widths) == 504
        p = 32 if pid == 'width7_eight' else 0
        assert Counter(widths) == Counter({4: 8, 5: 48, 7: p, 8: 160-p, 9: 288})
        assert all(widths[h] == 9 for h in (299,301,375,377))
        assert all(widths[h] == 8 for h in (270,271,282,283,294,295,306,307))
        assert word["ports"] == desc["ports"] and word["centers"] == desc["centers"]
        assert replay["status"] == "PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY"
        assert len(replay["negative_controls_rejected"]) == 11
        assert replay["canonical_word_sha256"] == sha(directory / "CANONICAL-WORD.json.gz")
        assert replay["local_programs_sha256"] == sha(directory / "LOCAL-PROGRAMS.json.gz")
        assert phase_review["status"] == "PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES"
        assert phase_review["canonical_word_sha256"] == replay["canonical_word_sha256"]
        assert phase_review["recipe_sha256"] == sha(directory / "CLIFFORD-RECIPES.json")
        assert phase_review["all_child_equalities_include_global_phase"] is True
        assert phase_review["endpoint_adapters"] == 224
        assert phase_review["directed_edges"] == (3004 if pid == "width7_eight" else 2928)
        for orientation in ("forward", "backward"):
            profile = Counter(event[-1] for event in programs[orientation] if event[0] in ("climb", "center"))
            assert dict(profile) == {1: 2320+p, 2: 420+5*p, 3: 464-4*p, 4: 192,
                                     5: 56, 6: 56, 8: 8}
            assert dict(profile) == {int(rank): count for rank, count in word["local_profile"].items()}
            assert checks[orientation]["paid_profile"] == replay["paid_profiles"][orientation] == desc["actual_paid_profile"]
            assert digest(programs[orientation]) == checks[orientation]["sha256"] == desc["orientation_program_sha256"][orientation]
        providers[pid] = dict(word=word, widths=widths, profile=profile, checks=checks)
    plain, promoted = (providers[pid]["word"] for pid in ("eightcold_eight", "width7_eight"))
    # Frame names change after interning, but every scalar operation remains.
    for phase_name in ("precondition", "A", "cut", "B", "compensation", "cleanup"):
        assert [row[:-1] for row in plain[phase_name]] == [row[:-1] for row in promoted[phase_name]]
    changed_widths = [helper for helper in range(504)
                      if providers["eightcold_eight"]["widths"][helper] != providers["width7_eight"]["widths"][helper]]
    assert len(changed_widths) == 32
    assert all(providers["eightcold_eight"]["widths"][helper] == 8
               and providers["width7_eight"]["widths"][helper] == 7 for helper in changed_widths)

    selected = {}
    paid, provider_counts = Counter(), Counter()
    for time, call in enumerate(plan["provider_calls"]):
        key = call["stage"], call["replica"]
        assert key == order[time] and call["time"] == time
        assert call["orientation"] == calls[key]["orientation"]
        pid = call["provider"]
        assert call["local_program_sha256"] == providers[pid]["checks"][call["orientation"]]["sha256"]
        selected[time] = pid
        provider_counts[pid] += 1
        paid.update(providers[pid]["profile"])
    assert dict(provider_counts) == nominal["dispatch"] and sum(provider_counts.values()) == 72
    assert len(plan["provider_calls"]) == len(plan["per_call_widths"]) == 72
    for time, row in enumerate(plan["per_call_widths"]):
        if isinstance(row, dict):
            assert (row["stage"], row["replica"]) == order[time]
            row = row["widths"]
        assert row == providers[selected[time]]["widths"]

    bases = []
    for port in plain["ports"]:
        pivot = next(index for index in range(9) if not (port >> index) & 1)
        even = port ^ (1 << pivot)
        axes = list(range(9))
        axes[0], axes[pivot] = axes[pivot], axes[0]
        basis = [(1 << index) ^ (even if (even >> index) & 1 else 0) for index in axes]
        basis += [1 << index for index in range(9, 73)]
        assert all((a & b).bit_count() % 2 == int(i == j)
                   for i, a in enumerate(basis) for j, b in enumerate(basis))
        bases.append(basis)
    seen_helpers, owners, occupied = defaultdict(set), defaultdict(set), defaultdict(set)
    sigmas, cross_replica, width7_roles = set(), 0, 0
    for row in roles:
        time, helper, family = row["time"], row["helper"], row["family"]
        stage, replica = order[time]
        assert (row["stage"], row["replica"]) == (stage, replica)
        assert 0 <= helper < 504 and helper not in seen_helpers[time]
        assert family not in owners[time] and 0 <= family < 7168
        seen_helpers[time].add(helper)
        owners[time].add(family)
        assert family not in {value[0] for value in calls[stage, replica]["owners"][:224]}
        owner_replica, remainder = divmod(family, 896)
        pair_side, port = divmod(remainder, 112)
        pair, side = divmod(pair_side, 2)
        child, offset, width = row["child"], row["offset"], row["width"]
        assert (pair, side) == geometry[child]
        assert (owner_replica, port) == (row["owner_replica"], row["port"])
        assert row["copy"] == owner_replica * 112 + port
        assert width == providers[selected[time]]["widths"][helper]
        left, right = windows[owner_replica, child]
        assert left < positions[time] < right
        assert 0 <= offset and offset + width <= capacities[child]
        cells = set(range(offset, offset + width))
        key = owner_replica, child, port
        assert not occupied[key] & cells
        occupied[key].update(cells)
        pending = list(map(int, phase["recipes"][port]["idle_children"][child]["orthogonal_axes"]))
        assert len(pending) == capacities[child]
        basis = bases[port]
        used = [basis.index(axis) for axis in pending[offset:offset + width]]
        spectators = [index for index in range(73) if index not in used][:9 - width]
        permutation = used + spectators + [index for index in range(73) if index not in used + spectators]
        assert len(used + spectators) == len(set(used + spectators)) == 9
        assert sorted(permutation) == list(range(73))
        sigma = [basis[index] for index in permutation]
        assert sigma[:width] == pending[offset:offset + width]
        sigmas.add(digest(sigma))
        cross_replica += owner_replica != replica
        width7_roles += width == 7
    assert len(roles) == 36288 and all(seen_helpers[time] == set(range(504)) for time in range(72))
    idle = Counter()
    for replica in range(8):
        for child, capacity in capacities.items():
            for port in range(112):
                cells = occupied[replica, child, port]
                assert cells == set(range(len(cells)))
                if capacity > len(cells):
                    idle[capacity - len(cells)] += 1
    paid.update(idle)
    assert dict(idle) == {int(rank): count for rank, count in nominal["idle"].items()}
    assert dict(paid) == {int(rank): count for rank, count in plan["profile"].items()}
    assert dict(paid) == {int(rank): count for rank, count in nominal["profile"].items()}
    assert 73 * 7168 - sum(rank * count for rank, count in paid.items()) == 2560
    assert 73 * 73 > 2 * max(paid) ** 2
    return dict(status="PASS_INDEPENDENT_WIDTH7_LITERAL_GEOMETRY_AND_PROFILE",
                source_sha256=dict(source_hashes, **{str(template_path): sha(template_path),
                                                       str(phase_path): sha(phase_path),
                                                       str(plan_path): sha(plan_path),
                                                       str(owners_path): sha(owners_path),
                                                       str(nomination_receipt): sha(nomination_receipt)}),
                provider_counts=dict(provider_counts), changed_helper_indices=changed_widths,
                unchanged_scalar_streams=True, whole_call_roles=len(roles), width7_roles=width7_roles,
                independent_pending_windows=len(windows), actual_73column_sigmas=len(sigmas),
                cross_replica_roles=cross_replica, idle_profile=dict(sorted(idle.items())),
                paid_profile=dict(sorted(paid.items())), mass=sum(rank * count for rank, count in paid.items()),
                reviewer_sha256=sha(Path(__file__)),
                registry_hashes_present=all("artifact_sha256" in d for d in plan["provider_registry"].values()),
                scope="Independent literal nomination checker, with windows reconstructed from actual inherited events. "
                      "Actual provider scalar and exact phase receipts are byte-bound in this receipt and inspected, not rerun. "
                      "All seven generated-artifact registry pins match the supplied actual provider files. "
                      "Complete emitted-template, invoice and outer assembly admission are separate.")


if __name__ == "__main__":
    assert __debug__, "Assertions required"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--owners", type=Path, required=True)
    parser.add_argument("--nomination-receipt", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--plain", type=Path, required=True)
    parser.add_argument("--width7", type=Path, required=True)
    arguments = parser.parse_args()
    result = review(arguments.base, arguments.plan, arguments.owners, arguments.nomination_receipt,
                    {"eightcold_eight": arguments.plain, "width7_eight": arguments.width7})
    arguments.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(result["status"], result["provider_counts"], result["paid_profile"])
