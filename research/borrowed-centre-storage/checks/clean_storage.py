"""Review query swaps through strictly idle old owner intervals."""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json


CAMPAIGN = Path(__file__).resolve().parents[1] / "sources" / "work/centre-encoding-campaign-20261014"
LANE = CAMPAIGN / "lanes/history-encoding"
SELECTED = Path(__file__).resolve().parents[1] / "sources/selected"
SOURCE = CAMPAIGN / "lanes/source-domain/carried-owner-reuse"
PINS = {
    "CLEAN-IDLE-STORAGE.json": "294a8f4ac078cebb2545834f307628ca1578c635ca10d6c9d309900997d86ae1",
    "CLEAN-IDLE-STORAGE.md": "1015479b667d70be74121c0abd347cbd8fd72938d932b544675b2236dd18864a",
    "check_clean_idle_storage.py": "cd08ffebe6ef9f70b0f20a991c1173153bc9b40ec67009f62e4b1d725a3188bb",
}
PORTS = [21, 37, 47, 76, 81, 87, 92, 110]


def require(value, label):
    if not value:
        raise ValueError(label)


def pinned(path, pin):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == pin, "Source pin: " + str(path))
    return raw


def family(replica, pair, side, port):
    return 896*replica + 224*pair + 112*side + port


def execute(program, labels):
    rows = {v: [int(v == w) for w in labels] for v in labels}
    for op in program:
        if op[0] == "ADD":
            _, target, source, coefficient = op
            rows[target] = [a+coefficient*b for a, b in zip(rows[target], rows[source])]
        elif op[0] == "SCALE":
            _, target, coefficient = op
            rows[target] = [coefficient*a for a in rows[target]]
        else:
            raise ValueError("Unknown swap operation")
    return [rows[v] for v in labels]


def reject(operation, label):
    try:
        operation()
    except ValueError:
        return label
    raise ValueError("Negative control did not fail: " + label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    frozen = {name: pinned(SOURCE/name, pin) for name, pin in PINS.items()}
    receipt = json.loads(frozen["CLEAN-IDLE-STORAGE.json"])
    member = "candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz"
    raw = (SELECTED / "GLOBAL-TEMPLATE.json.gz").read_bytes()
    member_hash = sha256(raw).hexdigest()
    require(member_hash == "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760", "Selected template pin")
    template = json.loads(gzip.decompress(raw))
    alias_path = CAMPAIGN/"lanes/residual-syndrome/physical-algebra/review-gauss/graph-cache/carried-alias/REVIEW.json"
    alias_pin = "e5823787516ad6abbc1e2b0a6b2c3d53422ac56bca462dcfeb6abd6b25569ac3"
    alias = json.loads(pinned(alias_path, alias_pin))
    require(alias["status"] == "PASS_INDEPENDENT_CARRIED_QUERY_ALIAS"
            and alias["pins"]["producer_receipt"] == receipt["source_alias_receipt_sha256"]
            and alias["pins"]["payload"] == receipt["source_alias_payload_sha256"], "Exact clean selected-Y query premise")

    calls, events = template["calls"], template["execution_schedule"]
    require(len(calls) == 144 and len(events) == 482, "Actual schedule size")
    places = {e["time"]: pos for pos, e in enumerate(events) if e["kind"] == "local_cover_sweep"}
    stages = {(c["replica"], c["stage"]): c for c in calls}
    query_sources = {family(r, pair, 1, p) for r in range(16) for pair in range(4) for p in PORTS}
    require(receipt["globally_excluded_query_source_families"] == sorted(query_sources), "All selected source families")

    event_uses, bridges, counts = [], {}, Counter()
    for pos, event in enumerate(events):
        kind, r = event["kind"], event.get("replica")
        if kind == "local_cover_sweep":
            call = calls[event["time"]]
            used = {f for f, route in call["owners"]}
            require(len(used) == 704 and max(used) < 14336, "All local data and helper owners")
            counts["local_calls"] += 1
            counts["helper_occurrences"] += len(call["owners"][224:])
        elif kind == "idle_cover_sweep":
            used = {family(r, event["pair"], side, p) for side in range(2) for p in range(112)}
            counts["idle_events"] += 1
        elif kind == "bridge":
            src, dst, gain = event["src"], event["dst"], event["coefficient"]
            # The selected bridge is X_dst += gain X_src; Y_src -= gain Y_dst.
            operations = [(family(r, dst, 0, p), family(r, src, 0, p), gain) for p in range(112)]
            operations += [(family(r, src, 1, p), family(r, dst, 1, p), -gain) for p in range(112)]
            bridges[pos] = operations
            used = {f for target, source, gain in operations for f in (target, source)}
            counts["bridges"] += 1
        elif kind in ("terminal", "terminal_Y_translations"):
            used = set(range(896*r, 896*(r+1)))
            counts[kind] += 1
        else:
            require(r is None and pos >= 480, "Only final all-live events remain")
            used = set(range(14336))
        event_uses.append(used)
    require(counts == dict(local_calls=144, helper_occurrences=69120, idle_events=160,
                          bridges=144, terminal=16, terminal_Y_translations=16), "Complete original use census")

    chosen = receipt["selected"]
    require([x["role"] for x in chosen] == list(range(512)), "All source rows exactly once")
    donors = {x["donor_family"] for x in chosen}
    require(len(donors) == 512 and donors.isdisjoint(query_sources), "All donor-source pairs are disjoint")
    require({x["source_family"] for x in chosen} == query_sources, "Every selected query source")
    capture, erase, expected_changes = defaultdict(list), defaultdict(list), []
    candidate_counts, operations = [], Counter()
    candidate_sets = {}
    for cohort, stated in enumerate(receipt["windows"]):
        r, s = divmod(cohort, 4)
        stage = (1, 3, 5, 7)[s]
        back, front = stages[r, stage], stages[r, stage+1]
        start, end = places[back["time"]]+1, places[front["time"]]
        require(back["orientation"] == "backward" and front["orientation"] == "forward"
                and back["pair"] == front["pair"], "Actual B-to-F window")
        require((stated["window"], stated["replica"], stated["stage"], stated["capture_before_position"], stated["erase_before_position"])
                == (cohort, r, stage, start, end), "Complete post-B and pre-F cuts")
        endpoint = event_uses[start-1] | event_uses[end]
        busy = set().union(*event_uses[start:end])
        candidates = set(range(14336)) - endpoint - busy - query_sources
        candidate_sets[cohort] = candidates
        candidate_counts.append(len(candidates))
        require(len(candidates) == stated["candidate_count"] and len(endpoint) == stated["excluded_endpoint_owner_count"], "Independent candidate census")
        require(stated["original_pair"] == back["pair"], "Original query pair")
        local_donors = []
        for k, p in enumerate(PORTS):
            row = chosen[8*cohort+k]
            source, donor = row["source_family"], row["donor_family"]
            require(source == family(r, back["pair"], 1, p) and donor in candidates, "Chosen source and strictly idle donor")
            require(row["window"] == cohort and row["source_port"] == p, "Source row assignment")
            require(row["physical_cover_map"] == "g to g" and row["physical_native_address_map"] == "identity", "Physical swap address")
            local_donors.append(donor)
            capture[start].append(row)
            erase[end].append(row)
            use_positions = []
            for pos in range(start, end):
                if source not in event_uses[pos]:
                    continue
                require(pos in bridges, "A source has an unhandled non-bridge use")
                relevant = [op for op in bridges[pos] if source in op[:2]]
                require(len(relevant) == 1 and relevant[0][1] == source and relevant[0][0] != source,
                        "The parked source is read only")
                target, _, gain = relevant[0]
                require(gain == -1, "Selected plus-bridge sign")
                expected_changes.append(dict(position=pos, replica=r, stage=stage, port=p,
                    old_source_family=source, new_source_family=donor, target_family=target,
                    coefficient=gain, cover_and_native_address="unchanged"))
                use_positions.append(pos)
            require(use_positions == row["original_source_read_positions"] and len(use_positions) == int(stage != 7), "Every original source use is handled")
            for name in ("capture_program", "erase_program"):
                program = row[name]
                require(execute(program, [source, donor]) == [[0, 1], [1, 0]], "Literal unsigned physical swap")
                operations.update(op[0] for op in program)
                require(len(program) == 4 and all(op[-1] in (-1, 1) for op in program), "Literal unit-scalar swap invoice")
        require(local_donors == stated["donor_families"], "Cohort donor list")
    require(expected_changes == receipt["bridge_read_replacements"] and len(expected_changes) == 384, "All changed read targets and coefficients")

    # Follow the physical location of every original logical owner.
    location = list(range(14336))
    emitted_changes = {(r["position"], r["old_source_family"]): r for r in expected_changes}
    observed_changes = set()
    for pos in range(len(events)+1):
        for row in erase[pos]:
            a, b = row["source_family"], row["donor_family"]
            require((location[a], location[b]) == (b, a), "Expected parked field locations")
            location[a], location[b] = a, b
        for row in capture[pos]:
            a, b = row["source_family"], row["donor_family"]
            require((location[a], location[b]) == (a, b), "Capture pair is available")
            location[a], location[b] = b, a
        if pos == len(events):
            break
        if pos in bridges:
            for target, source, gain in bridges[pos]:
                require(location[target] == target, "No bridge writes a parked field")
                if location[source] != source:
                    key = pos, source
                    require(key in emitted_changes and emitted_changes[key]["new_source_family"] == location[source]
                            and emitted_changes[key]["target_family"] == target
                            and emitted_changes[key]["coefficient"] == gain, "Bridge follows the exact stored query")
                    observed_changes.add(key)
                else:
                    require((pos, source) not in emitted_changes, "Unnecessary or wrong read replacement")
        else:
            require(all(location[f] == f for f in event_uses[pos]), "An unchanged original event touches a parked field")
    require(observed_changes == set(emitted_changes) and location == list(range(14336)), "Complete symbolic schedule restores every owner location")
    require(min(candidate_counts) == receipt["minimum_candidates"] == 3608
            and max(candidate_counts) == receipt["maximum_candidates"] == 10675, "Candidate range")
    require(operations == {"ADD": 3072, "SCALE": 1024}, "Full literal scalar macro count")
    real_cost = 8*operations["ADD"] + 2*operations["SCALE"]
    require(real_cost == receipt["added_real_scalar_primitives"] == 26624, "Full swap scalar subtotal")
    require(receipt["new_native_children"] == receipt["new_productive_families"] == receipt["new_physical_families"] == 0, "No new native or owner count")

    first = chosen[0]
    a, b = first["source_family"], first["donor_family"]
    target = 20000
    changed_read = [["ADD", target, b, -1]]
    unchanged_read = [["ADD", target, a, -1]]
    correct = execute(first["capture_program"]+changed_read+first["erase_program"], [a, b, target])
    require(correct == [[1, 0, 0], [0, 1, 0], [-1, 0, 1]], "Arbitrary query, donor, and bridge-target identity")
    occupied = next(iter(event_uses[receipt["windows"][0]["capture_before_position"]]))
    controls = [
        reject(lambda: require(execute(first["capture_program"][:-1], [a, b]) == [[0, 1], [1, 0]], "Missing swap sign"), "missing_swap_sign"),
        reject(lambda: require(execute(first["capture_program"]+unchanged_read+first["erase_program"], [a, b, target]) == correct, "Parked donor leaks through old source"), "old_bridge_read"),
        reject(lambda: require(occupied in candidate_sets[0], "An actual event uses this donor"), "actual_idle_event_owner"),
        reject(lambda: require(len({r["donor_family"] for r in chosen[:-1]} | {b}) == 512, "Repeated donor"), "duplicate_donor"),
    ]
    result = dict(status="PASS_INDEPENDENT_ALL512_CLEAN_IDLE_STORAGE", producer_imported=False, producer_executed=False,
        source_pins=PINS, archive_sha256="f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6", archive_replayed=False, packaged_members_verified=True, template_sha256=member_hash,
        alias_review_sha256=alias_pin, checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        original_event_counts=dict(counts), complete_schedule_events=482, complete_intervals=64,
        selected_query_rows=512, globally_disjoint_source_donor_pairs=512, candidate_range=[3608, 10675],
        exact_bridge_read_replacements=384, complete_symbolic_location_replay=True,
        all_14336_owner_locations_restored=True, arbitrary_query_donor_and_target_checked=True,
        physical_swaps=1024, complex_ADDs=3072, complex_sign_SCALES=1024, scalar_real_primitives_subtotal=real_cost,
        added_native_children=0, added_fields=0, old_live=14336, old_physical=14826,
        native_phase_scope="The exact selected-Y query is moved by an unsigned raw swap at the same physical cover class and address; no native phase or chart is changed.",
        placement="Each capture is a complete sweep after B and before the next event; each erase is a complete sweep before F.",
        negative_controls=controls,
        excluded=["Common-frame query access", "Storage through F", "Source-code restoration", "A complete global controller", "Finite address, control, and precision invoice", "Kappa improvement"])
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"])
    print(json.dumps({k: result[k] for k in ("selected_query_rows", "exact_bridge_read_replacements", "scalar_real_primitives_subtotal")}, sort_keys=True))


if __name__ == "__main__":
    main()
