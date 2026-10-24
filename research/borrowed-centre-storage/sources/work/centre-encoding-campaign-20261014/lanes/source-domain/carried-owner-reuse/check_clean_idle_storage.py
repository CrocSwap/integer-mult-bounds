"""Bind clean post-B query storage to strictly idle old owners."""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import bisect
import gzip
import json
import tarfile


ARCHIVE = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz"
TEMPLATE = "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760"
ALIAS = "42fb664f2273bacdc04603c548961de4a75ec04d752974794f0f0b311ca18bd2"
PORTS = [21, 37, 47, 76, 81, 87, 92, 110]


def require(value, label):
    if not value:
        raise ValueError(label)


def family(replica, pair, side, port):
    return 896*replica+112*(2*pair+side)+port


def no_event(positions, start, end):
    return bisect.bisect_left(positions, start) == bisect.bisect_left(positions, end)


def swap_word(first, second):
    return [["ADD", first, second, 1], ["ADD", second, first, -1],
            ["ADD", first, second, 1], ["SCALE", second, -1]]


def swap_matrix(omit_sign=False):
    state = [[1, 0], [0, 1]]
    for op in swap_word(0, 1):
        if op[0] == "ADD":
            _, a, b, c = op
            state[a] = [x+c*y for x, y in zip(state[a], state[b])]
        elif not omit_sign:
            state[op[1]] = [op[2]*x for x in state[op[1]]]
    return state


def window_matrix(redirect_read=True):
    state = [[int(i == j) for j in range(3)] for i in range(3)]
    program = swap_word(0, 1)+[["ADD", 2, 1 if redirect_read else 0, -1]]+swap_word(0, 1)
    for op in program:
        if op[0] == "ADD":
            _, a, b, c = op
            state[a] = [x+c*y for x, y in zip(state[a], state[b])]
        else:
            state[op[1]] = [op[2]*x for x in state[op[1]]]
    return state


def main(args):
    require(sha256(args.archive.read_bytes()).hexdigest() == ARCHIVE, "Selected archive pin")
    with tarfile.open(args.archive) as archive:
        raw = archive.extractfile(MEMBER).read()
    require(sha256(raw).hexdigest() == TEMPLATE, "Selected template pin")
    require(sha256(args.alias.read_bytes()).hexdigest() == ALIAS, "Exact selected source-alias premise")
    alias = json.loads(args.alias.read_text())
    require(alias["status"] == "PASS_CARRIED_QUERY_ALIAS" and alias["arbitrary_helpers_restored"] == 480, "Source q and all arbitrary helpers")
    template = json.loads(gzip.decompress(raw))
    calls, events = template["calls"], template["execution_schedule"]
    positions = {e["time"]: i for i, e in enumerate(events) if e["kind"] == "local_cover_sweep"}
    by_stage = {(c["replica"], c["stage"]): c for c in calls}
    uses, helper_positions = defaultdict(list), defaultdict(list)
    counts = Counter()
    for i, event in enumerate(events):
        replica, kind = event.get("replica"), event["kind"]
        if replica is None:
            require(i >= 480, "Every all-live event follows every query window")
            continue
        if kind == "local_cover_sweep":
            call = calls[event["time"]]
            owners = [owner[0] for owner in call["owners"]]
            require(len(owners) == len(set(owners)) == 704, "Distinct persistent local owners")
            for register, owner in enumerate(owners):
                uses[owner].append(i)
                if register >= 224:
                    helper_positions[owner].append(i)
            counts["calls"] += 1
        elif kind == "idle_cover_sweep":
            # Exclude the whole event even if an owner's suffix has rank0.
            # This also excludes every complete-idle phase translation.
            for side in range(2):
                for port in range(112):
                    uses[family(replica, event["pair"], side, port)].append(i)
            counts["idle_events"] += 1
        elif kind == "bridge":
            for pair in (event["src"], event["dst"]):
                for side in range(2):
                    for port in range(112):
                        uses[family(replica, pair, side, port)].append(i)
            counts["bridges"] += 1
        elif kind in ("terminal_Y_translations", "terminal"):
            for owner in range(896*replica, 896*(replica+1)):
                uses[owner].append(i)
            counts[kind] += 1
        else:
            raise ValueError("Unknown selected event: "+kind)
    require(counts == dict(calls=144, idle_events=160, bridges=144, terminal_Y_translations=16, terminal=16), "All482 source events are covered")
    require(sum(len(v) for v in helper_positions.values()) == 69120, "Every complete ordinary helper use is excluded from storage windows")

    query_sources = {family(replica, pair, 1, port)
                     for replica in range(16) for pair in range(4) for port in PORTS}
    require(len(query_sources) == 512, "All query-source families are distinct")
    selected, windows, read_replacements, used_donors = [], [], [], set()
    for replica in range(16):
        for stage in (1, 3, 5, 7):
            backward, forward = by_stage[replica, stage], by_stage[replica, stage+1]
            start, end = positions[backward["time"]]+1, positions[forward["time"]]
            require(backward["pair"] == forward["pair"], "The selected source pair remains the same in each window")
            endpoint_owners = {v[0] for call in (backward, forward) for v in call["owners"]}
            eligible = [owner for owner in range(14336)
                        if owner not in endpoint_owners and owner not in query_sources
                        and no_event(uses[owner], start, end)]
            available = [owner for owner in eligible if owner not in used_donors]
            require(len(available) >= 8, "Eight globally unused strictly idle donors are available")
            chosen = available[:8]
            used_donors.update(chosen)
            window = dict(window=len(windows), replica=replica, stage=stage,
                backward_position=start-1, capture_before_position=start, erase_before_position=end,
                candidate_count=len(eligible), excluded_endpoint_owner_count=len(endpoint_owners),
                original_pair=backward["pair"], donor_families=chosen)
            windows.append(window)
            for k, (port, donor) in enumerate(zip(PORTS, chosen)):
                source = family(replica, backward["pair"], 1, port)
                require(source in endpoint_owners and donor not in endpoint_owners
                        and donor not in query_sources and donor < 14336,
                        "No endpoint, private C, query-source or donor alias")
                allowed_reads = []
                for i in range(start, end):
                    event = events[i]
                    if event.get("replica") != replica:
                        continue
                    if event["kind"] == "bridge" and event["dst"] == backward["pair"]:
                        require(event["coefficient"] == 1, "The selected source is read in the plus bridge")
                        replacement = dict(position=i, replica=replica, stage=stage, port=port,
                            old_source_family=source, new_source_family=donor,
                            target_family=family(replica, event["src"], 1, port), coefficient=-1,
                            cover_and_native_address="unchanged")
                        read_replacements.append(replacement)
                        allowed_reads.append(i)
                    elif i in uses[source]:
                        raise ValueError("The parked old donor value has an unhandled source use")
                require(len(allowed_reads) == (0 if stage == 7 else 1), "Every selected-Y read is replaced")
                # The source must not be an owner of another replica's local
                # helper job. Such use is global even when replica differs.
                require([i for i in uses[source] if start <= i < end] == allowed_reads,
                        "There is no unhandled source helper, idle, data, bridge or terminal use")
                selected.append(dict(role=len(selected), window=window["window"], source_port=port,
                    source_family=source, donor_family=donor,
                    capture_program=swap_word(source, donor), erase_program=swap_word(source, donor),
                    physical_cover_map="g to g", physical_native_address_map="identity",
                    original_source_read_positions=allowed_reads))
    require(len(selected) == len(used_donors) == 512 and len(windows) == 64, "Complete clean-query storage assignment")
    require(len(read_replacements) == 384, "All48 affected bridge events have eight selected read changes")
    require(swap_matrix() == [[0, 1], [1, 0]], "The complete physical swap has the exact sign")
    require(swap_matrix(True) != [[0, 1], [1, 0]], "Omitting the swap sign is rejected")
    require(window_matrix() == [[1, 0, 0], [0, 1, 0], [-1, 0, 1]],
            "The whole window restores both fields and preserves the original query read")
    require(window_matrix(False) == [[1, 0, 0], [0, 1, 0], [0, -1, 1]],
            "An unchanged selected-Y read would leak the arbitrary donor")
    result = dict(status="PASS_ALL512_CLEAN_QUERY_IDLE_SWAPS",
        source_archive_sha256=ARCHIVE, source_template_compressed_sha256=TEMPLATE,
        source_alias_receipt_sha256=ALIAS, source_alias_payload_sha256=alias["payload_sha256"],
        source_schedule_events=len(events), source_counts=dict(counts), log_ports=PORTS,
        windows=windows, selected=selected, bridge_read_replacements=read_replacements,
        distinct_old_donors=len(used_donors), complete_query_rows=512, complete_cohorts=64,
        globally_excluded_query_source_families=sorted(query_sources),
        minimum_candidates=min(row["candidate_count"] for row in windows),
        maximum_candidates=max(row["candidate_count"] for row in windows),
        physical_swaps=1024, complex_unit_ADDs=3072, complex_sign_SCALES=1024,
        added_real_scalar_primitives=1024*(3*8+2), new_native_children=0,
        new_productive_families=0, new_physical_families=0, old_live=14336, old_physical=14826,
        full_cover_capture_sweeps=64, full_cover_erase_sweeps=64,
        native_query_frame="The exact physical post-B selected-Y frame; no normalization or new source phase is applied",
        value_after_swapback="The exact original post-B source output and the exact original idle donor value",
        excluded_claims=["A common-I or common-F clean query", "A local-C alias", "Storage through the next forward call", "Source G inversion", "A complete scalar/address/precision supplier invoice", "A kappa improvement"],
        rejected_controls=["Wrong unsigned-swap sign", "Use parked donor h in the original bridge read"])
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"])
    print(json.dumps({k: result[k] for k in ("complete_query_rows", "minimum_candidates", "maximum_candidates", "physical_swaps", "added_real_scalar_primitives")}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("archive", "alias", "out"):
        parser.add_argument("--"+name, type=Path, required=True)
    main(parser.parse_args())
