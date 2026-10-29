#!/usr/bin/env python3
"""Independent stdlib audit of PR #2979's V45 lowering and final ledgers.

This script reads the frozen source archive as data. It imports no module from
that archive, does not run its registered verifier or owner engine, and does
not calculate a new kappa root.
"""
from collections import Counter, defaultdict
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "research/rank7-joint-endframes"
NORMS = (7, 42, 45)
LOCAL_REGISTERS = 704
HELPER_START = 224
HELPER_STOP = 704
PORT_COUNT = 112
GUARD_COUNT = 2


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text())


def read_gzip_json(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind_source_archive(pins):
    manifest_path = SOURCE / "MANIFEST.json"
    need(sha256(manifest_path) == pins["source_manifest_sha256"],
         "source package manifest hash differs from local pin")
    expected = read_json(manifest_path)
    actual = {}
    for path in SOURCE.rglob("*"):
        need(not path.is_symlink(), "source archive contains an unexpected symlink")
        if path.is_file() and path != manifest_path:
            actual[path.relative_to(SOURCE).as_posix()] = sha256(path)
    need(actual == expected, "source package file set or SHA-256 differs from manifest")
    allocation_pins = read_json(SOURCE / "ALLOCATION-PINS.json")
    for relative, digest in allocation_pins.items():
        need(sha256(SOURCE / relative) == digest,
             "source allocation pin differs: " + relative)
    return len(actual), len(allocation_pins)


def basis(vectors):
    """Return an echelon basis over F2 using highest-bit pivots."""
    pivots = {}
    for vector in vectors:
        value = int(vector)
        need(value >= 0, "negative F2 vector")
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def rank(vectors):
    return len(basis(vectors))


def contained(small, large):
    rows = basis(large)
    for raw in small:
        value = int(raw)
        for row in rows:
            pivot = row.bit_length() - 1
            if (value >> pivot) & 1:
                value ^= row
        if value:
            return False
    return True


def same_space(left, right):
    return contained(left, right) and contained(right, left)


def hyperplane(normal):
    need(0 < normal < 512, "normal outside F2^9")
    return basis(value for value in range(1, 512)
                 if (value & normal).bit_count() % 2 == 0)


def valid_v45_space(space):
    return (rank(space) == 7 and
            all((int(vector) & normal).bit_count() % 2 == 0
                for vector in space for normal in NORMS))


def frame_report(word):
    """Rebuild the local child-rank and width report from word events.

    The walk tracks each register's current subspace. An event that needs a
    larger frame pays one child at the dimension difference; terminal helper
    widths are counted from their start and end frames.
    """
    full = basis(1 << bit for bit in range(9))
    ports = word["ports"]
    endings = ([full] * PORT_COUNT +
               [hyperplane(port) for port in ports] +
               [full] * 480)
    for register, frame in word["helper_final"].items():
        endings[int(register)] = basis(frame)

    beginnings = [(port,) for port in ports] + [()] * (PORT_COUNT + 480)
    for register, frame in word["start_extra"].items():
        beginnings[int(register)] = basis(frame)

    current = [basis(frame) for frame in beginnings]
    paid = Counter()

    def climb(register, target):
        target_basis = basis(target)
        need(contained(current[register], target_basis),
             "nonmonotone frame at register " + str(register))
        delta = rank(target_basis) - rank(current[register])
        if delta:
            paid[delta] += 1
        current[register] = target_basis

    def event(gate):
        if gate[0] == "warp":
            need(same_space(current[gate[1]], gate[3]), "warp source frame mismatch")
            current[gate[1]] = basis(gate[4])
            return
        need(gate[0] in ("add", "scale"), "unknown word operation " + str(gate[0]))
        registers = gate[1:3] if gate[0] == "add" else gate[1:2]
        for register in registers:
            climb(register, gate[-1])

    for gate in word["A"]:
        event(gate)

    for register, centre_frame in zip(word["centers"], word["center_frames"]):
        need(same_space(current[register], centre_frame), "centre frame mismatch")
        targets = {
            basis(word["target_levels"].get(str(gate[1] - PORT_COUNT), []))
            for gate in word["cut"] if gate[2] == register
        }
        current_level = basis(centre_frame)
        for target in sorted(targets, key=lambda value: -len(value)):
            if not same_space(current_level, target):
                paid[len(current_level) - len(target)] += 1
            current_level = target

    warps_by_position = defaultdict(list)
    for warp in word["warps"]:
        warps_by_position[warp[0]].append(warp)
    for position in range(len(word["B"]) + 1):
        for warp in warps_by_position.get(position, []):
            need(same_space(current[warp[1]], warp[3]), "B warp source frame mismatch")
            current[warp[1]] = basis(warp[4])
        if position < len(word["B"]):
            event(word["B"][position])

    for gate in word["restore"]:
        event(gate)

    live = set(range(LOCAL_REGISTERS)) - set(word["removed"])
    for register in live:
        climb(register, endings[register])

    widths = Counter(rank(endings[register]) - rank(beginnings[register])
                     for register in live if register >= HELPER_START)
    profile = {str(key): paid[key] for key in sorted(paid) if paid[key]}
    inventory = {str(key): widths[key] for key in sorted(widths) if widths[key]}
    return profile, inventory


def gate_registers(signature):
    if signature[0] == "add":
        return signature[1:3]
    if signature[0] == "scale":
        return signature[1:2]
    return ()


def apply_stage_one(parent, record, lowered, *, omit=None, edited_record=None):
    """Apply the shared recorded gate refit and selected terminal lowerings."""
    row = record if edited_record is None else edited_record
    result = deepcopy(parent)
    seen = set()
    for edit in row["frame_edits"]:
        key = (edit["section"], edit["index"])
        need(key not in seen, "duplicate frame-edit address")
        seen.add(key)
        section, index = key
        gate = result[section][index]
        need(gate[:-1] == edit["gate"] and gate[-1] == edit["old_frame"],
             "gate signature/frame preimage mismatch at " + repr(key))
        need(contained(edit["new_frame"], edit["old_frame"]),
             "edited gate frame is not a subspace of its preimage")
        need(rank(edit["new_frame"]) == rank(edit["old_frame"]) - 1,
             "edited gate frame did not drop exactly one dimension")
        if omit != key:
            gate[-1] = list(edit["new_frame"])

    changes = record["helper_final_changes"]
    for helper in lowered:
        change = changes[str(helper)]
        need(parent["helper_final"].get(str(helper)) == change["old"],
             "helper endpoint preimage mismatch at " + str(helper))
        need(rank(change["new"]) == rank(change["old"]) - 1,
             "helper endpoint did not drop exactly one dimension")
        result["helper_final"][str(helper)] = list(change["new"])
    return result


def word_gate_fit(word, helpers, space):
    for section in ("A", "B", "restore"):
        for index, gate in enumerate(word[section]):
            if gate[0] in ("add", "scale") and set(gate_registers(gate)) & set(helpers):
                if not contained(gate[-1], space):
                    return False, (section, index)
    return True, None


def profile_cost(profile, weights):
    return sum(int(count) * weights[int(rank)] for rank, count in profile.items())


def rank_mass(profile):
    return sum(int(rank) * int(count) for rank, count in profile.items())


def widths_histogram(widths):
    return {str(width): count for width, count in sorted(Counter(widths).items())}


def derive_windows(template, order, replicas):
    rank_by_child = {int(row["child"]): int(row["rank"])
                     for row in template["idle_children"]}
    pair_by_stage = {int(row["stage"]): int(row["pair"])
                     for row in template["recipe"] if row["kind"] == "local"}
    blocks = {}
    stage = None
    ignored = {"bank_padding_cover_sweep", "translate_every_live_family"}
    for item in template["execution_schedule"]:
        if item["kind"] in ignored:
            continue
        if item["kind"] == "local_cover_sweep":
            stage = int(item["stage"])
            blocks[stage] = []
        need(stage is not None, "source event precedes first local stage")
        blocks[stage].append(item)
    need(set(blocks) == set(range(9)), "expected nine source stages")

    progress = [0] * replicas
    last_source = {}
    windows = {}
    for time, (raw_stage, raw_replica) in enumerate(order):
        current_stage, replica = int(raw_stage), int(raw_replica)
        need(0 <= replica < replicas and current_stage == progress[replica],
             "call order violates stage chronology")
        progress[replica] += 1
        for position, item in enumerate(blocks[current_stage]):
            kind = item["kind"]
            if kind == "local_cover_sweep":
                need(position == 0, "local sweep is not first in its stage")
                last_source[replica, pair_by_stage[current_stage]] = time
            elif kind == "bridge":
                last_source[replica, item["src"]] = time
                last_source[replica, item["dst"]] = time
            elif kind == "idle_cover_sweep":
                start = last_source.get((replica, item["pair"]), -1)
                for child in item["child_indices"]:
                    child = int(child)
                    if child in rank_by_child:
                        windows[replica, child] = (rank_by_child[child], start, time)
            elif kind in ("terminal_Y_translations", "terminal"):
                pass
            else:
                raise ValueError("unknown source-window event " + str(kind))
    need(progress == [9] * replicas, "replica chronology is incomplete")
    return windows, pair_by_stage


def check_fill(fill, order, dispatch_rows, plan, template, providers):
    dispatch = {}
    for stage, replica, provider in dispatch_rows:
        key = (int(stage), int(replica))
        need(key not in dispatch, "duplicate provider dispatch")
        need(provider in providers, "unknown provider dispatch")
        dispatch[key] = provider
    need(set(dispatch) == {tuple(map(int, row)) for row in order},
         "provider dispatch does not bind the complete order")

    replicas = len(order) // 9
    need(replicas * 9 == len(order), "call count is not nine stages per replica")
    windows, _ = derive_windows(template, order, replicas)
    need(fill["columns"] == ["time", "helper", "owner_replica", "child", "port", "offset"],
         "role column schema mismatch")
    rows = fill["rows"]
    need(len(rows) == len(order) * 408, "role count is not 408 per call")
    pair = plan["pairs"]
    side = plan["sides"]
    need(set(pair) == set(side), "bin pair/side keys differ")
    helper_masks = [0] * len(order)
    family_masks = [set() for _ in order]
    used_families = set()
    occupancy = {}
    provider_role_counts = Counter()
    for row in rows:
        need(len(row) == 6 and all(type(value) is int for value in row),
             "non-integer role row")
        time, helper, owner, child, port, offset = row
        need(0 <= time < len(order) and 0 <= helper < 408 and
             0 <= port < PORT_COUNT and offset >= 0, "role row outside declared domain")
        need((owner, child) in windows, "role has no source window")
        cap, lo, hi = windows[owner, child]
        need(lo < time <= hi, "role is outside its source window")
        helper_bit = 1 << helper
        need(not helper_masks[time] & helper_bit, "duplicate helper at a call")
        helper_masks[time] |= helper_bit

        stage, replica = map(int, order[time])
        provider = dispatch[stage, replica]
        provider_role_counts[provider] += 1
        width = int(providers[provider]["widths"][helper])
        need(offset + width <= cap, "role exceeds bin capacity")
        child_key = str(child)
        need(child_key in pair and child_key in side, "bin has no physical family map")
        family = (owner * 896 +
                  (2 * int(pair[child_key]) + int(side[child_key])) * PORT_COUNT + port)
        family_bitset = family_masks[time]
        need(family not in family_bitset, "two helpers use one family in a call")
        family_bitset.add(family)
        used_families.add(family)

        key = (owner, child, port)
        mask = ((1 << width) - 1) << offset
        need(not occupancy.get(key, 0) & mask, "two roles overlap within a family")
        occupancy[key] = occupancy.get(key, 0) | mask

    complete_helper_mask = (1 << 408) - 1
    need(all(mask == complete_helper_mask for mask in helper_masks),
         "one or more calls lack a helper role")
    expected_live = replicas * 896
    need(all(0 <= family < expected_live for family in used_families),
         "physical family ID exceeds the reserved live-family domain")
    need(len(used_families) <= expected_live, "more distinct assignments than live stock")
    return {
        "replicas": replicas,
        "calls": len(order),
        "roles": len(rows),
        "live_families": expected_live,
        "distinct_assigned_families": len(used_families),
        "roles_by_provider": dict(sorted(provider_role_counts.items())),
    }


def rejected(label, action):
    try:
        action()
    except (ValueError, KeyError, IndexError):
        return label
    raise ValueError("semantic failure control accepted: " + label)


def main():
    pins = read_json(HERE / "PINS.json")
    need(pins["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
         "unexpected research base")
    need(pins["source_pr"] == 2979 and
         pins["source_head"] == "be191346391661f4d35fc0d1508d0a6029572576",
         "unexpected PR #2979 source head")
    source_file_count, allocation_pin_count = bind_source_archive(pins)

    record = read_json(SOURCE / "data/STAGE1-FRAME-EDITS.json")
    price_data = read_json(SOURCE / "construction/STAGE-PRICES.json")
    groups = record["groups"]
    space, v45_helpers = groups["V45"]
    need(valid_v45_space(space), "V45 is not the claimed rank-seven intersection")
    need(rank(NORMS) == 2, "V45 normals do not impose exactly two independent conditions")
    need((7 ^ 42) == 45, "V45 circuit relation differs")

    parents = {kind: read_gzip_json(SOURCE / f"data/PARENT-{kind}.json.gz")
               for kind in ("base", "extra")}
    final_words = {kind: read_gzip_json(SOURCE / f"data/WORD-{kind}.json.gz")
                   for kind in ("base", "extra")}
    for kind, word in parents.items():
        profile, inventory = frame_report(word)
        need(profile == word["report"]["local_profile"],
             "independent parent child-rank report differs for " + kind)
        need(inventory == word["report"]["width_inventory"],
             "independent parent width report differs for " + kind)

    edits = record["frame_edits"]
    need(len(record["helper_final_changes"]) == 22 and len(edits) == 139,
         "stage-one declared edit counts changed")
    v45_edit_positions = {
        (edit["section"], edit["index"])
        for edit in edits if set(gate_registers(edit["gate"])) & set(v45_helpers)
    }
    need(len(v45_edit_positions) == 29, "V45 gate-edit count changed")

    old_end = parents["base"]["helper_final"]
    for helper in v45_helpers:
        change = record["helper_final_changes"][str(helper)]
        need(old_end[str(helper)] == change["old"], "V45 endpoint preimage mismatch")
        need(same_space(space, change["new"]), "V45 endpoint is not the shared space")
        need(rank(change["old"]) == 8 and rank(change["new"]) == 7 and
             contained(change["new"], change["old"]), "V45 endpoint is not a hyperplane lowering")

    for edit in edits:
        need(edit["section"] in ("A", "B", "restore"), "unexpected frame-edit section")
        need(rank(edit["old_frame"]) == rank(edit["new_frame"]) + 1 and
             contained(edit["new_frame"], edit["old_frame"]), "gate edit is not a one-rank subspace")

    all_stage1_profiles = {}
    stage1_words = {}
    for kind, word in parents.items():
        stage1 = apply_stage_one(word, record,
                                {int(helper) for helper in record["helper_final_changes"]})
        fit, failed_gate = word_gate_fit(stage1, v45_helpers, space)
        need(fit, "V45 partner gate falls outside W: " + repr(failed_gate))
        need(stage1["cleanup"] == word["cleanup"], "stage one changed cleanup data")
        for section in ("A", "B", "restore"):
            need(all(before[:-1] == after[:-1]
                     for before, after in zip(word[section], stage1[section])),
                 "stage one changed a gate/operator/scalar")
        profile, inventory = frame_report(stage1)
        need(profile == record["declared_local_profile"], "stage-one local profile mismatch")
        need(inventory == record["declared_width_inventory"], "stage-one width inventory mismatch")
        all_stage1_profiles[kind] = (profile, inventory)
        stage1_words[kind] = stage1

    weights = {int(rank): int(value) for rank, value in price_data["weights"]["c"].items()}
    break_even = int(price_data["weights"]["break_even"])
    base_profile = parents["base"]["report"]["local_profile"]
    all_profile = all_stage1_profiles["base"][0]
    all_delta = profile_cost(all_profile, weights) - profile_cost(base_profile, weights)
    need(all_delta == price_data["stage1"]["literal_price_units"],
         "complete stage-one price does not follow from independently rebuilt profiles")

    all_lowered = {int(helper) for helper in record["helper_final_changes"]}
    source_group_prices = {}
    for group_name, (_, helpers) in groups.items():
        source_group = next(row for row in price_data["stage1"]["groups"]
                            if row["group"] == group_name)
        need(source_group["joint_margin"] ==
             -source_group["joint_delta"] - len(helpers) * break_even,
             "joint margin arithmetic differs for group " + group_name)
        source_group_prices[group_name] = {
            "joint_delta_units": source_group["joint_delta"],
            "joint_margin_units": source_group["joint_margin"],
            "helpers": len(helpers),
        }
    need(sum(row["joint_delta_units"] for row in source_group_prices.values()) == all_delta,
         "five source group prices do not sum to the independently rebuilt stage-one profile cost")

    v45_joint = v45_source_group = next(row for row in price_data["stage1"]["groups"]
                                        if row["group"] == "V45")
    v45_joint_margin = int(v45_joint["joint_margin"])
    need(v45_joint["helpers"] == v45_helpers, "V45 helper inventory mismatch")
    no_v45_endpoints = deepcopy(stage1_words["base"])
    for helper in v45_helpers:
        no_v45_endpoints["helper_final"][str(helper)] = \
            parents["base"]["helper_final"][str(helper)]
    no_v45_profile, _ = frame_report(no_v45_endpoints)
    fixed_gate_delta = profile_cost(all_profile, weights) - profile_cost(no_v45_profile, weights)
    need(fixed_gate_delta == -len(v45_helpers) * weights[1],
         "fixed-gate V45 endpoint delta is not four rank-one child savings")
    partner_refit_overhead = int(v45_joint["joint_delta"]) - fixed_gate_delta

    subset_prices = []
    source_subsets = {tuple(row["helpers"]): row for row in v45_source_group["subsets"]}
    for mask in range(1, 1 << len(v45_helpers)):
        selected = {v45_helpers[index] for index in range(len(v45_helpers))
                    if (mask >> index) & 1}
        reverted = set(v45_helpers) - selected
        candidate = deepcopy(stage1_words["base"])
        for helper in reverted:
            candidate["helper_final"][str(helper)] = parents["base"]["helper_final"][str(helper)]
        fits, failed_gate = word_gate_fit(candidate, selected, space)
        need(fits, "V45 subset control has an unfitted partner gate: " + repr(failed_gate))
        profile, _ = frame_report(candidate)
        need(candidate["cleanup"] == stage1_words["base"]["cleanup"],
             "V45 endpoint-only control changed cleanup data")
        reverted_endpoint_cost = profile_cost(profile, weights) - profile_cost(all_profile, weights)
        expected_reversion_cost = len(reverted) * weights[1]
        need(reverted_endpoint_cost == expected_reversion_cost,
             "V45 terminal reversion cost differs from rank-one child tariff")
        endpoint_delta = profile_cost(profile, weights) - profile_cost(no_v45_profile, weights)
        need(endpoint_delta == -len(selected) * weights[1],
             "V45 endpoint-only delta differs from rank-one tariff")
        delta = endpoint_delta + partner_refit_overhead
        margin = -delta - len(selected) * break_even
        source = source_subsets[tuple(helper for helper in v45_helpers if helper in selected)]
        need(delta == source["delta"] and margin == source["margin"],
             "V45 subset price mismatch for " + repr(sorted(selected)))
        subset_prices.append((len(selected), delta, margin))
    need(all(margin < 0 for size, _, margin in subset_prices if size < len(v45_helpers)),
         "a proper V45 subset unexpectedly meets the joint margin")
    need(next(margin for size, _, margin in subset_prices if size == len(v45_helpers)) > 0,
         "joint V45 group no longer clears its reported margin")

    final_profiles = {}
    provider_registry = read_json(SOURCE / "allocation/PROVIDERS.json")
    for kind, word in final_words.items():
        profile, inventory = frame_report(word)
        provider = "gauge44" if kind == "base" else "extra"
        need(profile == {str(k): int(v) for k, v in
                         provider_registry[provider]["actual_paid_profile"].items()},
             "final provider paid profile mismatch for " + provider)
        need(inventory == widths_histogram(provider_registry[provider]["widths"]),
             "final provider width inventory mismatch for " + provider)
        need(len(word["helper_final"]) == 91 and len(word["centers"]) == 8,
             "final private buffer or centre count mismatch for " + provider)
        buffer_registers = set()
        for gate in word["cleanup"]:
            for register in gate_registers(gate):
                if register >= LOCAL_REGISTERS:
                    buffer_registers.add(register)
        need(len(buffer_registers) == 91, "cleanup does not expose 91 private buffers")
        final_profiles[kind] = profile
    need(final_profiles["base"] == final_profiles["extra"],
         "the two provider words have different local profiles")

    final_profile = final_profiles["base"]
    final_delta = profile_cost(final_profile, weights) - profile_cost(base_profile, weights)
    final_width_loss = rank_mass(base_profile) - rank_mass(final_profile)
    total = price_data["total"]
    need(final_delta == total["literal_price_units"], "full final child cost differs from the source ledger")
    need(final_width_loss == total["freed_width_units"], "full final rank-mass reduction differs")
    need(-final_delta - final_width_loss * break_even == total["margin"],
         "full final margin arithmetic differs")

    claim = read_json(SOURCE / "CLAIM.json")
    order = read_json(SOURCE / "allocation/ORDER.json")
    dispatch = read_json(SOURCE / "allocation/DISPATCH.json")
    fill = read_gzip_json(SOURCE / "allocation/FILL.json.gz")
    plan = read_gzip_json(SOURCE / "allocation/vendor/PLAN.json.gz")
    template = read_gzip_json(SOURCE / "allocation/vendor/TEMPLATE.json.gz")
    owner = read_json(SOURCE / "construction/allocation/T74-OWNER-CHECK.json")
    owner_summary = check_fill(fill, order, dispatch, plan, template, provider_registry)

    global_profile = {int(rank): int(count) for rank, count in
                      read_json(SOURCE / "allocation/PROFILE.json").items()}
    idle = {int(rank): int(count) for rank, count in
            read_json(SOURCE / "allocation/SEARCH.json")["idle_histogram"].items()}
    local = {int(rank): int(count) for rank, count in final_profile.items()}
    reconciled = {rank: local.get(rank, 0) * len(order) + idle.get(rank, 0)
                  for rank in set(local) | set(idle)}
    reconciled = {rank: count for rank, count in reconciled.items() if count}
    need(reconciled == global_profile, "local children plus idle widths do not equal full profile")
    total_rank_mass = sum(rank * count for rank, count in global_profile.items())
    need(total_rank_mass == owner["rank_mass"], "full child-rank mass mismatch")
    need(owner_summary["live_families"] == claim["live_families"] == 66304,
         "live physical family count mismatch")
    helpers = len(provider_registry["extra"]["widths"])
    centres = len(final_words["base"]["centers"])
    private = len(final_words["base"]["helper_final"])
    guards = int(owner["physical"]) - owner_summary["live_families"] - helpers - centres - private
    physical = owner_summary["live_families"] + helpers + centres + private + guards
    need(guards == GUARD_COUNT and physical == 66813 == owner["physical"] == claim["physical_families"],
         "complete physical family invoice mismatch")

    # Semantic failure controls: wrong shared space, omitted partner refit,
    # stale gate signature, duplicate helper row, and over-capacity offset.
    wrong_space = None
    for index in range(len(space)):
        for bit in range(9):
            candidate = list(space)
            candidate[index] ^= 1 << bit
            if rank(candidate) == 7 and not valid_v45_space(candidate):
                wrong_space = candidate
                break
        if wrong_space is not None:
            break
    need(wrong_space is not None, "failed to construct wrong-space control")
    controls = [rejected("wrong_v45_subspace", lambda: need(
        valid_v45_space(wrong_space), "wrong rank-seven space"))]

    omitted_edit = None
    for edit in edits:
        if ((edit["section"], edit["index"]) in v45_edit_positions and
                not contained(edit["old_frame"], space)):
            omitted_edit = edit
            break
    need(omitted_edit is not None, "no V45 gate refit available for omission control")
    omitted_word = apply_stage_one(
        parents["base"], record, all_lowered,
        omit=(omitted_edit["section"], omitted_edit["index"]))
    fits, _ = word_gate_fit(omitted_word, v45_helpers, space)
    controls.append(rejected("omitted_partner_gate_refit", lambda: need(
        fits, "a lowered helper has an unfitted partner gate")))

    mutated_record = deepcopy(record)
    mutated_record["frame_edits"][0]["gate"][3] *= -1
    controls.append(rejected("changed_gate_scalar_preimage", lambda: apply_stage_one(
        parents["base"], record, all_lowered, edited_record=mutated_record)))

    bad_rows = list(fill["rows"])
    bad_rows[1] = list(bad_rows[0])
    duplicate_fill = {**fill, "rows": bad_rows}
    controls.append(rejected("duplicate_helper_role", lambda: check_fill(
        duplicate_fill, order, dispatch, plan, template, provider_registry)))

    bad_rows = list(fill["rows"])
    bad_rows[0] = list(bad_rows[0])
    bad_rows[0][5] = 49
    overflow_fill = {**fill, "rows": bad_rows}
    controls.append(rejected("bin_capacity_overflow", lambda: check_fill(
        overflow_fill, order, dispatch, plan, template, provider_registry)))

    metrics = {
        "status": "PASS_INDEPENDENT_V45_FRAME_COST_AND_PHYSICAL_LEDGER",
        "base_commit": pins["base_commit"],
        "priority_revision": pins["priority_revision"],
        "source_pr": pins["source_pr"],
        "source_head": pins["source_head"],
        "source_files_hash_bound": source_file_count,
        "allocation_inputs_hash_bound": allocation_pin_count,
        "v45": {
            "normals": list(NORMS),
            "relation": "7 xor 42 = 45",
            "space_rank": rank(space),
            "helpers": list(v45_helpers),
            "edited_partner_gates": len(v45_edit_positions),
            "subset_count": len(subset_prices),
            "fixed_gate_endpoint_delta_units": fixed_gate_delta,
            "source_joint_delta_units": v45_joint["joint_delta"],
            "implied_shared_partner_refit_overhead_units": partner_refit_overhead,
            "subset_margins_by_cardinality": {
                str(size): sorted({margin for n, _, margin in subset_prices if n == size})
                for size in range(1, len(v45_helpers) + 1)
            },
            "single_lowering_margin": subset_prices[0][2],
            "joint_margin": next(margin for size, _, margin in subset_prices if size == 4),
        },
        "stage_one": {
            "lowered_endpoints": 22,
            "gate_frame_edits": 139,
            "local_profile": all_profile,
            "source_joint_group_delta_and_margin": source_group_prices,
            "literal_price_units": all_delta,
            "freed_width_units": 22,
            "margin": -all_delta - 22 * break_even,
        },
        "final": {
            "provider_profiles_equal": True,
            "provider_local_profile": final_profile,
            "provider_width_inventory": widths_histogram(provider_registry["extra"]["widths"]),
            "literal_price_units_from_parent": final_delta,
            "freed_width_units_from_parent": final_width_loss,
            "margin_from_parent": total["margin"],
        },
        "physical": {
            **owner_summary,
            "helpers": helpers,
            "centres": centres,
            "private_buffers": private,
            "guards_from_pinned_invoice_residual": guards,
            "physical_families": physical,
            "provider_calls": dict(sorted(Counter(
                provider for _, _, provider in dispatch).items())),
            "global_child_rank_mass": total_rank_mass,
            "global_rank_profile": {str(k): v for k, v in sorted(global_profile.items())},
            "idle_rank_profile": {str(k): v for k, v in sorted(idle.items())},
        },
        "controls_rejected": controls,
        "scope": "Exact finite source-bound ledger audit; no new kappa root, full native replay, independent algebra replay, outer theorem, or supplier admission.",
    }
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
