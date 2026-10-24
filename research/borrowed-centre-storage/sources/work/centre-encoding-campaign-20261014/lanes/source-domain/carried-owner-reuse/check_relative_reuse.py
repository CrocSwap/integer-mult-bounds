"""Bind an external dirty query cache to original native owner advances."""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import bisect
import gzip
import json
import tarfile


ARCHIVE = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PINS = {
    "template": ("candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz", "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760"),
    "word": ("candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz", "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"),
    "phases": ("candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json", "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"),
}
ALIAS_PIN = "42fb664f2273bacdc04603c548961de4a75ec04d752974794f0f0b311ca18bd2"
ALIAS_PAYLOAD = "677199e44967cb598bdd6b92f23400cf88ac40020e195f07a0c6e5244a3ace0d"
PORTS = [21, 37, 47, 76, 81, 87, 92, 110]


def require(value, label):
    if not value:
        raise ValueError(label)


def family(replica, pair, side, port):
    return 896*replica+112*(2*pair+side)+port


def axis_mask(indices):
    return sum(1 << i for i in indices)


def apply(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length()-1]
        vector ^= bit
    return result


def inverse(columns):
    return [sum(((v >> i) & 1) << j for j, v in enumerate(columns)) for i in range(73)]


def field_span(rows, start, end):
    positions = [r["position"] for r in rows]
    return rows[bisect.bisect_left(positions, start):bisect.bisect_left(positions, end)]


def main(args):
    require(sha256(args.archive.read_bytes()).hexdigest() == ARCHIVE, "Pinned selected archive")
    inputs = {}
    with tarfile.open(args.archive) as archive:
        for key, (member, pin) in PINS.items():
            raw = archive.extractfile(member).read()
            require(sha256(raw).hexdigest() == pin, "Pinned member: "+key)
            inputs[key] = json.loads(gzip.decompress(raw) if member.endswith(".gz") else raw)
    require(sha256(args.alias.read_bytes()).hexdigest() == ALIAS_PIN, "Exact carried-query alias receipt")
    alias = json.loads(args.alias.read_text())
    require(alias["status"] == "PASS_CARRIED_QUERY_ALIAS" and alias["payload_sha256"] == ALIAS_PAYLOAD
            and alias["arbitrary_helpers_restored"] == 480, "Selected source alias and arbitrary-helper premise")
    template, word, recipes = inputs["template"], inputs["word"], inputs["phases"]["recipes"]
    require(template["cover"] == "all matrices d in O(73,2), in lexicographic row order", "Every constructed map is in the selected cover")
    calls, events = template["calls"], template["execution_schedule"]
    position = {e["time"]: i for i, e in enumerate(events) if e["kind"] == "local_cover_sweep"}
    by_stage = {(c["replica"], c["stage"]): c for c in calls}
    bases, pending, child_type, idle_position = {}, {}, {}, {}
    for port, recipe in enumerate(recipes):
        basis = [recipe["q"]]+recipe["idle_children"][0]["orthogonal_axes"][:8]+[1 << i for i in range(9, 73)]
        require(all((a & b).bit_count() % 2 == int(i == j) for i, a in enumerate(basis) for j, b in enumerate(basis)), "Complete orthonormal owner basis")
        bases[port] = basis
        index = {v: i for i, v in enumerate(basis)}
        for child, row in enumerate(recipe["idle_children"]):
            pending[port, child] = [index[v] for v in row["orthogonal_axes"]]
    for i, event in enumerate(events):
        if event["kind"] == "idle_cover_sweep":
            for side, child in enumerate(event["child_indices"]):
                child_type[child] = event["pair"], side
                idle_position[event["replica"], child] = i

    histories, touches = defaultdict(list), defaultdict(list)
    counts = Counter()
    for index, row in enumerate(template["hosting"]["pooled_slots"]):
        child, port, offset, width = (row[k] for k in ("child", "port", "offset", "width"))
        axes = pending[port, child][offset:offset+width]
        spectators = [axis for axis in range(73) if axis not in axes][:9-width]
        route = [3, child, offset] if width == 9 else [4, child, offset, width, spectators]
        register = 224+row["helper"]
        require(row["family"] == family(row["owner_replica"], *child_type[child], port)
                and calls[row["time"]]["owners"][register] == [row["family"], route], "Exact original complete helper owner and route")
        require(len(axes) == width == len(word["frames"][word["final"][register]])-len(word["frames"][word["start"][register]]), "Complete arbitrary-input helper width")
        histories[row["family"]].append(dict(kind="helper", index=index, position=position[row["time"]], axes=axes, translation=0))
        counts["helper_jobs"] += 1
    for index, row in enumerate(template["idle_children"]):
        axes = pending[row["port"], row["child"]][row["pending_offset"]:]
        require(len(axes) == row["rank"], "Complete selected suffix")
        histories[row["family"]].append(dict(kind="suffix", index=index, position=idle_position[row["replica"], row["child"]], axes=axes, translation=0))
        counts["suffix_jobs"] += 1
    for i, event in enumerate(events):
        replica, kind = event.get("replica"), event["kind"]
        if replica is None:
            continue
        if kind == "local_cover_sweep":
            call = calls[event["time"]]
            require(len({v[0] for v in call["owners"]}) == 704, "Distinct original local owners")
            for owner, route in call["owners"][:224]:
                port = owner % 112
                require(route == [1, call["stage"], port], "Actual data route")
                histories[owner].append(dict(kind="data", index=event["time"], position=i,
                    axes=list(range(8*call["stage"]+1, 8*call["stage"]+9)),
                    translation=recipes[port]["idle_children"][0]["translation_after"] if call["stage"] == 0 else 0))
                touches[owner].append(i)
            counts["local_calls"] += 1
        elif kind == "bridge":
            for pair in (event["src"], event["dst"]):
                for side in range(2):
                    for port in range(112):
                        touches[family(replica, pair, side, port)].append(i)
            counts["bridges"] += 1
        elif kind == "idle_cover_sweep":
            for child in event["child_indices"]:
                pair, side = child_type[child]
                for port in range(112):
                    histories[family(replica, pair, side, port)].append(dict(kind="idle_translation", index=child,
                        position=i, axes=[], translation=recipes[port]["idle_children"][child]["translation_after"]))
            counts["idle_events"] += 1
        elif kind in ("terminal_Y_translations", "terminal"):
            # The complete signed terminal is an ordinary data use. Exclude
            # it from every cache path, including its phase prelude.
            for pair in range(4):
                for side in range(2):
                    for port in range(112):
                        touches[family(replica, pair, side, port)].append(i)
            counts[kind] += 1
    for owner in range(14336):
        histories[owner].sort(key=lambda row: (row["position"], row["kind"] == "idle_translation"))
        mask = int((owner//112) % 2 == 0)
        shift = 0
        for row in histories[owner]:
            axes = axis_mask(row["axes"])
            require(not mask & axes, "No original owner native axis repeats")
            mask |= axes
            shift ^= row["translation"]
            row["after_axis_mask"] = mask
        require(mask == (1 << 73)-1-int((owner//112) % 2 == 1), "Every old owner reaches its exact preterminal subspace")
        require(shift == recipes[owner % 112]["idle_children"][0]["translation_after"], "Every old owner reaches its exact preterminal basis phase")
        touches[owner].sort()
    require(counts["helper_jobs"] == 69120 and counts["suffix_jobs"] == 7526
            and counts["local_calls"] == 144 and counts["idle_events"] == 160, "Complete original native history")

    cohorts, candidates = [], {}
    for replica in range(16):
        for stage in (1, 3, 5, 7):
            start, end = (position[by_stage[replica, s]["time"]] for s in (stage, stage+1))
            cohort = len(cohorts)
            cohorts.append(dict(cohort=cohort, replica=replica, stage=stage, start=start, end=end))
            eligible = []
            for owner in range(14336):
                use = touches[owner]
                if bisect.bisect_left(use, end) != bisect.bisect_left(use, start):
                    continue
                path = field_span(histories[owner], start, end)
                if sum(len(row["axes"]) for row in path) == 8:
                    eligible.append(owner)
            candidates[cohort] = eligible
    neighbors = {8*cohort+k: owners for cohort, owners in candidates.items() for k in range(8)}
    chosen = {}

    def augment(role, seen):
        for owner in neighbors[role]:
            if owner in seen:
                continue
            seen.add(owner)
            if owner not in chosen or augment(chosen[owner], seen):
                chosen[owner] = role
                return True
        return False

    for role in range(512):
        require(augment(role, set()), "All512 query rows have distinct old owners")
    require(len(chosen) == 512, "No cache owner is reused anywhere in the campaign schedule")
    selected, paid = [], Counter()
    for owner, role in sorted(chosen.items(), key=lambda pair: pair[1]):
        cohort, k = divmod(role, 8)
        interval = cohorts[cohort]
        path = field_span(histories[owner], interval["start"], interval["end"])
        axes = sorted(axis for row in path for axis in row["axes"])
        require(len(axes) == len(set(axes)) == 8 and all(row["kind"] != "data" for row in path), "Exact eight-axis native-only path")
        target_basis = bases[owner % 112]
        native_axes = [target_basis[index] for index in axes]
        source_indices = list(range(9+8*(interval["stage"]-1), 9+8*interval["stage"]))
        rest_target = [i for i in range(73) if i not in axes]
        rest_source = [i for i in range(73) if i not in source_indices]
        columns = [0]*73
        for source_axis, target_axis in zip(source_indices+rest_source, axes+rest_target):
            columns[source_axis] = target_basis[target_axis]
        transpose = inverse(columns)
        require(all(apply(transpose, v) == 1 << i for i, v in enumerate(columns)), "Exact orthogonal map and inverse")
        require([columns[i] for i in source_indices] == native_axes, "The map sends the source's fresh block to the actual donor advance")
        shift = 0
        for row in path:
            shift ^= row["translation"]
            if row["axes"]:
                paid[len(row["axes"])] += 1
        before = [row for row in histories[owner] if row["position"] < interval["start"]]
        entry_mask = before[-1]["after_axis_mask"] if before else int((owner//112) % 2 == 0)
        # This is a finite full-phase witness for T=X_shift U F8 U^-1.
        # It checks all characters on the eight new axes and the independent
        # translation sign; tensor extension is a direct product identity.
        for bits in range(256):
            z = 0
            for j, v in enumerate(native_axes):
                if bits >> j & 1:
                    z ^= v
            source_character = apply(transpose, z)
            direct = sum((v & z).bit_count() % 2 for v in native_axes) % 4
            mapped = sum((source_character >> i) & 1 for i in source_indices) % 4
            require(direct == mapped, "Exact eight-axis Fourier phase of the donor interval")
        selected.append(dict(role=role, **interval, source_port=PORTS[k], owner_family=owner,
            owner_replica=owner//896, owner_pair=(owner % 896)//224, owner_side="X" if (owner//112) % 2 == 0 else "Y",
            owner_port=owner % 112, entry_axis_mask=entry_mask,
            query_entry_rank=8*interval["stage"], owner_entry_rank=entry_mask.bit_count(),
            jobs=path, target_axis_indices=axes, target_axes=native_axes, source_fresh_axis_indices=source_indices,
            U_columns=columns, U_inverse_columns=transpose, interval_translation=shift,
            capture_translation=0, erase_translation_owner_coordinates=shift))
    candidate_counts = [len(candidates[k]) for k in range(64)]
    result = dict(status="PASS_ALL512_EXTERNAL_DIRTY_CACHE_PATHS",
        source_archive_sha256=ARCHIVE, source_members={k: dict(path=p, sha256=h) for k, (p, h) in PINS.items()},
        alias_receipt_sha256=ALIAS_PIN, alias_payload_sha256=ALIAS_PAYLOAD, source_counts=dict(counts),
        log_ports=PORTS, candidate_owner_counts=candidate_counts, selected=selected,
        distinct_old_owner_families=len(chosen), complete_cohorts=64, matched_rows=512,
        old_owner_sides=dict(Counter(row["owner_side"] for row in selected)),
        unequal_absolute_entry_ranks=sum(row["owner_entry_rank"] != row["query_entry_rank"] for row in selected),
        selected_existing_native_profile=dict(sorted(paid.items())), selected_existing_native_mass=sum(k*v for k, v in paid.items()),
        nonzero_erase_translations=sum(row["interval_translation"] != 0 for row in selected),
        full_cover_capture_sweeps=64, full_cover_erase_sweeps=64,
        added_native_children=0, added_productive_families=0, added_physical_families=0,
        old_live=14336, old_physical=14826, original_private_namespace=template["private_namespace"],
        capture_ADDs=64*alias["capture"]["ADDs"], erase_ADDs=64*alias["unload"]["ADDs"],
        added_scalar_real_primitives=64*(alias["capture"]["real_primitives"]+alias["unload"]["real_primitives"]),
        relative_operator="T_owner = X_delta P_U F_Es P_U^-1; cache cover h = query owner cover g U^-1",
        dirty_contract="Add the physical query to arbitrary old owner value, run only its complete original native jobs, subtract X_(h delta) times the exact selected source alias; the old owner is restored",
        local_C_alias=False, clean_query_access=False, source_G_restored=False,
        unresolved=["Independent interval, phase and arbitrary-input review", "Uses of the dirty cache beyond transport and erase", "Source-code and full controller restoration", "Finite address/control, precision and complete recursive supplier invoice"])
    require(result["selected_existing_native_mass"] == 4096, "Exactly eight already-paid native ranks per row")
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"])
    print(json.dumps({k: result[k] for k in ("matched_rows", "old_owner_sides", "unequal_absolute_entry_ranks", "selected_existing_native_profile", "nonzero_erase_translations", "added_scalar_real_primitives")}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("archive", "alias", "out"):
        parser.add_argument("--"+name, type=Path, required=True)
    main(parser.parse_args())
