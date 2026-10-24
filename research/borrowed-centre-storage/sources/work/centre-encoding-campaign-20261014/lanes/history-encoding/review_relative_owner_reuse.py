"""Review the selected dirty-cache paths from the original owner records."""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import gzip
import json
import tarfile


LANE = Path(__file__).resolve().parent
CAMPAIGN = LANE.parents[1]
REPO = CAMPAIGN.parents[1]
SOURCE = CAMPAIGN / "lanes/source-domain/carried-owner-reuse"
ARCHIVE = REPO / "worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz"
PORTS = [21, 37, 47, 76, 81, 87, 92, 110]
PINS = {
    "RELATIVE-REUSE.json": "1d6d6c598022c7e83920a00575aeb5b3866b1ed1327718d389f659b057659acb",
    "RELATIVE-REUSE.md": "4ecbde9c53fd9888e5d0f2c90ef38dc006ff48ff7f9efb6b8339e87b03c6c3aa",
    "check_relative_reuse.py": "723d2d11abadcbfb569b1291fd3dc01a385e57ceecfa26124fdadec93726f204",
}
MEMBERS = {
    "template": ("candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz", "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760"),
    "word": ("candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz", "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"),
    "phases": ("candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json", "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"),
}
DEPENDENCIES = {
    "lanes/residual-syndrome/physical-algebra/CARRIED-QUERY-ALIAS.json": "42fb664f2273bacdc04603c548961de4a75ec04d752974794f0f0b311ca18bd2",
    "lanes/residual-syndrome/physical-algebra/review-gauss/graph-cache/carried-alias/REVIEW.json": "e5823787516ad6abbc1e2b0a6b2c3d53422ac56bca462dcfeb6abd6b25569ac3",
    "root/BORROWED-CENTRES-REVIEW.json": "04cffe488bce2b3f8c58a3e3428921052375bdcf1e0206c20de8e568a63d9b1f",
}


def require(value, message):
    if not value:
        raise ValueError(message)


def pinned(path, pin):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == pin, "Source pin: " + str(path))
    return raw


def family(replica, pair, side, port):
    return 896 * replica + 224 * pair + 112 * side + port


def mask(indices):
    require(len(indices) == len(set(indices)), "Repeated native axis")
    return sum(1 << i for i in indices)


def apply(columns, value):
    result = 0
    for i, column in enumerate(columns):
        if value >> i & 1:
            result ^= column
    return result


def phase_polynomial(vectors, translation=0):
    # Parity(v.z) is sum(v_i z_i)-2 sum(v_i v_j z_i z_j) modulo four.
    linear = [2 * ((translation >> i) & 1) for i in range(73)]
    quadratic = [[0] * i for i in range(73)]
    for vector in vectors:
        support = [i for i in range(73) if vector >> i & 1]
        for i in support:
            linear[i] = (linear[i] + 1) % 4
            for j in support:
                if j < i:
                    quadratic[i][j] = (quadratic[i][j] - 2) % 4
    return linear, quadratic


def reject(operation, label):
    try:
        operation()
    except ValueError:
        return label
    raise ValueError("Negative control did not fail: " + label)


def main():
    sources = {name: pinned(SOURCE / name, pin) for name, pin in PINS.items()}
    receipt = json.loads(sources["RELATIVE-REUSE.json"])
    premises = {name: json.loads(pinned(CAMPAIGN / name, pin)) for name, pin in DEPENDENCIES.items()}
    alias = premises["lanes/residual-syndrome/physical-algebra/CARRIED-QUERY-ALIAS.json"]
    alias_review = premises["lanes/residual-syndrome/physical-algebra/review-gauss/graph-cache/carried-alias/REVIEW.json"]
    helper_review = premises["root/BORROWED-CENTRES-REVIEW.json"]
    require(alias_review["status"] == "PASS_INDEPENDENT_CARRIED_QUERY_ALIAS", "Exact alias review")
    require(alias_review["pins"]["producer_receipt"] == DEPENDENCIES["lanes/residual-syndrome/physical-algebra/CARRIED-QUERY-ALIAS.json"], "Alias review pin")
    require(all(v["arbitrary_helpers_restored"] == 480 and v["input_columns"] == 712
                for v in helper_review["checks"].values()), "Arbitrary-helper output independence premise")
    digest = sha256()
    with ARCHIVE.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    require(digest.hexdigest() == "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6", "Selected archive pin")
    original = {}
    with tarfile.open(ARCHIVE) as archive:
        for key, (name, pin) in MEMBERS.items():
            raw = archive.extractfile(name).read()
            require(sha256(raw).hexdigest() == pin, "Selected member pin")
            original[key] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    template, word, recipes = original["template"], original["word"], original["phases"]["recipes"]
    require(template["cover"] == "all matrices d in O(73,2), in lexicographic row order", "Full orthogonal cover")
    require(template["live"] == 14336 and template["physical"] == 14826, "Original stocks")
    selected = receipt["selected"]
    require([row["role"] for row in selected] == list(range(512)), "All query roles exactly once")
    owners = {row["owner_family"] for row in selected}
    require(len(owners) == 512 and max(owners) < 14336, "Distinct old live owners")

    bases, pending = {}, {}
    for p, recipe in enumerate(recipes):
        basis = [recipe["q"]] + recipe["idle_children"][0]["orthogonal_axes"][:8] + [1 << i for i in range(9, 73)]
        require(len(basis) == 73 and all((a & b).bit_count() % 2 == int(i == j)
                for i, a in enumerate(basis) for j, b in enumerate(basis)), "Actual orthonormal owner chart")
        bases[p] = basis
        for c, child in enumerate(recipe["idle_children"]):
            pending[p, c] = [basis.index(v) for v in child["orthogonal_axes"]]
            require(len(pending[p, c]) == child["rank"], "Pending child rank")

    calls, events = template["calls"], template["execution_schedule"]
    require(len(calls) == 144 and len(events) == 482, "Complete selected schedule")
    places = {e["time"]: pos for pos, e in enumerate(events) if e["kind"] == "local_cover_sweep"}
    stages = {(c["replica"], c["stage"]): c for c in calls}
    child_places, child_roles = {}, {}
    for pos, event in enumerate(events):
        if event["kind"] == "idle_cover_sweep":
            for side, child in enumerate(event["child_indices"]):
                role = event["pair"], side
                require(child not in child_roles or child_roles[child] == role, "Stable idle child role")
                child_roles[child] = role
                child_places[event["replica"], child] = pos

    jobs, scalar_uses = defaultdict(list), defaultdict(list)
    used_slots = set()
    for index, slot in enumerate(template["hosting"]["pooled_slots"]):
        p, c, width = slot["port"], slot["child"], slot["width"]
        f, time, reg = slot["family"], slot["time"], 224 + slot["helper"]
        axes = pending[p, c][slot["offset"]:slot["offset"]+width]
        spectators = [i for i in range(73) if i not in axes][:9-width]
        route = [3, c, slot["offset"]] if width == 9 else [4, c, slot["offset"], width, spectators]
        require(f == family(slot["owner_replica"], *child_roles[c], p), "Actual helper family")
        require(calls[time]["owners"][reg] == [f, route], "Literal helper route and spectator list")
        require(width == len(axes) == len(word["frames"][word["final"][reg]]) - len(word["frames"][word["start"][reg]]), "Complete helper native width")
        require((time, reg) not in used_slots, "Repeated helper slot")
        used_slots.add((time, reg))
        if f in owners:
            jobs[f].append(dict(kind="helper", index=index, position=places[time], axes=axes, translation=0))
    require(used_slots == {(t, r) for t in range(144) for r in range(224, 704)}, "Every original helper slot")
    for index, suffix in enumerate(template["idle_children"]):
        f, p, c = suffix["family"], suffix["port"], suffix["child"]
        require(f == family(suffix["replica"], *child_roles[c], p), "Actual idle family")
        axes = pending[p, c][suffix["pending_offset"]:]
        require(len(axes) == suffix["rank"], "Complete idle remainder")
        if f in owners:
            jobs[f].append(dict(kind="suffix", index=index, position=child_places[suffix["replica"], c], axes=axes, translation=0))
    for pos, event in enumerate(events):
        r, kind = event.get("replica"), event["kind"]
        if kind == "local_cover_sweep":
            call = calls[event["time"]]
            require(call["time"] == event["time"] and len({a[0] for a in call["owners"]}) == 704, "Local distinct-owner contract")
            for side in range(2):
                for p in range(112):
                    f = family(r, call["pair"], side, p)
                    require(call["owners"][112*side+p] == [f, [1, call["stage"], p]], "Named data route")
                    if f in owners:
                        scalar_uses[f].append(pos)
                        jobs[f].append(dict(kind="data", index=event["time"], position=pos,
                            axes=list(range(8*call["stage"]+1, 8*call["stage"]+9)),
                            translation=recipes[p]["idle_children"][0]["translation_after"] if call["stage"] == 0 else 0))
        elif kind == "bridge":
            for pair in (event["src"], event["dst"]):
                for side in range(2):
                    for p in range(112):
                        f = family(r, pair, side, p)
                        if f in owners:
                            scalar_uses[f].append(pos)
        elif kind in ("terminal", "terminal_Y_translations"):
            for f in owners:
                if f // 896 == r:
                    scalar_uses[f].append(pos)
        elif kind == "idle_cover_sweep":
            for c in event["child_indices"]:
                for p in range(112):
                    f = family(r, *child_roles[c], p)
                    if f in owners:
                        jobs[f].append(dict(kind="idle_translation", index=c, position=pos, axes=[],
                            translation=recipes[p]["idle_children"][c]["translation_after"]))

    # Reconstruct each complete donor history without the producer's scan.
    for f in owners:
        row = sorted(jobs[f], key=lambda v: (v["position"], v["kind"] == "idle_translation"))
        state, delta = int((f // 112) % 2 == 0), 0
        for item in row:
            advance = mask(item["axes"])
            require(state & advance == 0, "An owner axis is already present")
            state |= advance
            delta ^= item["translation"]
            item["after_axis_mask"] = state
        require(state == (1 << 73)-1-int((f // 112) % 2 == 1), "Complete donor endpoint frame")
        require(delta == recipes[f % 112]["idle_children"][0]["translation_after"], "Complete donor endpoint phase")
        jobs[f] = row

    profile, sides, unequal, polynomial_checks = Counter(), Counter(), 0, 0
    path_lengths, source_window_events = Counter(), 0
    for row in selected:
        c, k = divmod(row["role"], 8)
        r, stage = c // 4, (1, 3, 5, 7)[c % 4]
        begin, end = (places[stages[r, s]["time"]] for s in (stage, stage+1))
        f = row["owner_family"]
        require((row["cohort"], row["replica"], row["stage"], row["start"], row["end"], row["source_port"])
                == (c, r, stage, begin, end, PORTS[k]), "Actual capture and erase boundaries")
        require(not any(begin <= p < end for p in scalar_uses[f]), "A donor has a scalar use while it holds a query")
        path = [item for item in jobs[f] if begin <= item["position"] < end]
        require(path == row["jobs"] and all(item["kind"] == "helper" for item in path), "All and only complete intervening helper jobs")
        indices = sorted(i for item in path for i in item["axes"])
        require(len(indices) == len(set(indices)) == 8 and indices == row["target_axis_indices"], "Exactly eight new interval axes")
        actual_vectors = [bases[f % 112][i] for item in path for i in item["axes"]]
        require([bases[f % 112][i] for i in indices] == row["target_axes"], "Native axes from actual port chart")
        prior = [item for item in jobs[f] if item["position"] < begin]
        entry = prior[-1]["after_axis_mask"] if prior else int((f // 112) % 2 == 0)
        require(entry == row["entry_axis_mask"] and entry.bit_count() == row["owner_entry_rank"], "Actual donor entry rank")
        require(row["query_entry_rank"] == 8*stage, "Query entry rank")
        unequal += entry.bit_count() != 8*stage
        side = "Y" if (f // 112) % 2 else "X"
        require((row["owner_replica"], row["owner_pair"], row["owner_side"], row["owner_port"])
                == (f // 896, (f % 896) // 224, side, f % 112), "Owner identity")
        sides[side] += 1
        path_lengths[len(path)] += 1
        profile.update(len(item["axes"]) for item in path)
        U, inv = row["U_columns"], row["U_inverse_columns"]
        require(len(U) == len(inv) == 73, "Full cover map dimensions")
        require(all(apply(U, inv[i]) == apply(inv, U[i]) == 1 << i for i in range(73)), "Both inverse orders")
        require(all((a & b).bit_count() % 2 == int(i == j)
                    for i, a in enumerate(U) for j, b in enumerate(U)), "Cover map is orthogonal")
        fresh = list(range(8*stage+1, 8*stage+9))
        require(fresh == row["source_fresh_axis_indices"], "Exact source fresh block")
        require(all(row[key] == 0 for key in ("interval_translation", "capture_translation", "erase_translation_owner_coordinates")), "Literal zero translation")
        direct = phase_polynomial(actual_vectors)
        mapped = phase_polynomial([U[i] for i in fresh])
        require(direct == mapped, "All coefficients of the full 73-variable Z4 phase")
        polynomial_checks += 1 + 73 + 73*72//2

        # Check the available selected-Y alias in the actual asynchronous window.
        source_pair = stages[r, stage]["pair"]
        source_y = {family(r, source_pair, 1, p) for p in range(112)}
        require(f not in source_y, "Capture does not change its source")
        if k == 0:
            for event in events[begin+1:end]:
                source_window_events += 1
                if event["kind"] == "local_cover_sweep":
                    require(not source_y & {o[0] for o in calls[event["time"]]["owners"]}, "An intervening call touches source Y")
                elif event["kind"] == "idle_cover_sweep" and event["replica"] == r:
                    require(event["pair"] != source_pair, "An intervening idle sweep touches source Y")
                elif event["kind"] == "bridge" and event["replica"] == r:
                    require(event["src"] != source_pair, "An intervening bridge writes source Y")
                elif event["kind"] in ("terminal", "terminal_Y_translations"):
                    require(event["replica"] != r, "An intervening terminal touches source Y")

    require(dict(profile) == {8: 479, 4: 66} and sum(r*n for r, n in profile.items()) == 4096, "Already-paid native profile")
    require(dict(sides) == {"X": 348, "Y": 164} and unequal == 499, "Representation count")
    require(receipt["selected_existing_native_profile"] == {str(k): v for k, v in sorted(profile.items())}, "Receipt profile")
    require(receipt["added_native_children"] == receipt["added_productive_families"] == receipt["added_physical_families"] == 0, "No new native or field claim")
    require(alias["capture"]["ADDs"] == alias_review["capture_ADDs"] == 424
            and alias["capture"]["real_primitives"] == alias_review["capture_real_primitives"] == 4224,
            "Normalized source query bill")
    require(alias["unload"]["ADDs"] == 8 and alias["unload"]["real_primitives"] == 64, "Erase bill")
    require(receipt["capture_ADDs"] == 64*424 and receipt["erase_ADDs"] == 64*8
            and receipt["added_scalar_real_primitives"] == 64*(4224+64), "Complete scalar subtotal")

    first = selected[0]
    vectors = first["target_axes"]
    wrong_phase = phase_polynomial(vectors, vectors[0])
    wrong_order = phase_polynomial([first["U_inverse_columns"][i] for i in first["source_fresh_axis_indices"]])
    two_jobs = next(row for row in selected if len(row["jobs"]) == 2)
    controls = [
        reject(lambda: require(wrong_phase == phase_polynomial(vectors), "Changed native translation"), "extra_translation"),
        reject(lambda: require(wrong_order == phase_polynomial(vectors), "Wrong cover conjugation order"), "inverse_cover_order"),
        reject(lambda: require(sum(len(j["axes"]) for j in two_jobs["jobs"][:-1]) == 8, "Missing complete helper"), "omitted_rank4_job"),
        reject(lambda: require(len({row["owner_family"] for row in selected[:-1]} | {first["owner_family"]}) == 512, "Duplicate old owner"), "duplicate_owner"),
    ]
    result = dict(status="PASS_INDEPENDENT_ALL512_RELATIVE_DIRTY_CACHE", producer_imported=False, producer_executed=False,
        producer_pins=PINS, dependency_pins=DEPENDENCIES, source_members={k: dict(path=p, sha256=h) for k, (p, h) in MEMBERS.items()},
        archive_sha256=digest.hexdigest(), checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        actual_schedule_events=len(events), original_helper_slots_checked=len(used_slots), original_idle_suffixes_checked=len(template["idle_children"]),
        complete_donor_histories=512, selected_paths=512, complete_eight_row_cohorts=64, globally_distinct_old_owners=512,
        selected_owner_sides=dict(sides), unequal_entry_ranks=unequal, selected_path_lengths=dict(path_lengths),
        selected_existing_native_profile=dict(sorted(profile.items())), selected_existing_native_mass=4096,
        full_73_variable_phase_polynomials=512, exact_phase_coefficients=polynomial_checks, scalar_phase_one=True,
        source_alias_window_event_incidences=source_window_events, helper_and_source_alias_reviews_bound=True,
        required_placement="All cover classes capture before each B core sweep; all erase before each F core sweep.",
        capture_ADDs=27136, erase_ADDs=512, scalar_real_primitives_subtotal=274432,
        old_live=14336, old_physical=14826, additional_native_children=0, additional_fields=0,
        arbitrary_background_lemma_reviewed=True, all_tensor_multiplicities=True, negative_controls=controls,
        not_replayed=["The original complete local scalar programs and native helper normalizers; their reviewed arbitrary-input contracts are retained.",
                     "Candidate enumeration and matching search; the full 512-row distinct-owner witness is checked directly."],
        excluded=["Clean query access", "Local C alias", "A dirty-cache read protocol", "Restoration of source G", "A full data controller", "Finite address, control, precision, and recursive invoice", "Kappa improvement"])
    output = LANE / "RELATIVE-OWNER-REUSE-REVIEW.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"])
    print(json.dumps({k: result[k] for k in ("selected_paths", "selected_existing_native_profile", "exact_phase_coefficients", "scalar_real_primitives_subtotal")}, sort_keys=True))


if __name__ == "__main__":
    main()
