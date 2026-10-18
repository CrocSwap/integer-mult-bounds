#!/usr/bin/env python3
"""Build and verify the rowwise P104 I-G/2 tail correction.

The frozen native channel is an input, not regenerated or edited.  Its exact
boundary is replayed first.  This package then constructs one chronological
tail at which all X sources are full-frame and each Y target is rank eight,
lowers every rank-one promotion/restoration to a native recipe, and proves the
resulting 280-column rational identity with negative controls.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import copy
import gzip
import hashlib
import importlib.util
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P104 = ROOT / "research/p104-native-channel"
INPUTS = P104 / "inputs"
FULL = [1 << i for i in range(9)]
EXPECTED_PINS = {
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    "research/p104-native-channel/inputs/LOWRANK-RESULT.json": "7143ec7780f6f38a8c294df8009c3621936b281d05ae79946ce22f581b73d1b1",
    "research/p104-native-channel/inputs/P104-FIXTURE.json": "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    "research/p104-native-channel/compile.py": "9d2fc2d81962ddb0b4dd7d6482d9918a87a6b05759690317dea79939ca5656a3",
    "research/p104-native-channel/vendor/clifford_exact.py": "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
    "research/p104-native-channel/vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    for bit in sorted(pivots):
        for other in pivots:
            if other > bit and ((pivots[other] >> bit) & 1):
                pivots[other] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def basis_span(vectors):
    return canonical(vectors)


def load_compiler():
    path = P104 / "compile.py"
    spec = importlib.util.spec_from_file_location("p104_tail_source_compiler", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def check_pins():
    for relative, sha in EXPECTED_PINS.items():
        need(digest((ROOT / relative).read_bytes()) == sha, "source pin changed: " + relative)


def base_replay():
    run = subprocess.run(
        [sys.executable, "-I", "-O", "-B", str(P104 / "verify.py")],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=180, check=False,
    )
    need(run.returncode == 0, "frozen P104 positive control failed: " + run.stderr[-2000:])
    result = json.loads(run.stdout)
    need(result.get("status") == "PASS_CONCRETE_NATIVE_P104_LOW_RANK_CHANNEL",
         "frozen P104 replay status")
    need(result.get("formal_boundary_columns") == 280
         and result.get("rank_mass") == 2368
         and result.get("scalar_events", {}).get("add") == 2624,
         "frozen P104 replay receipt changed")
    return result


def correction_data(compiler):
    transform = compiler.label_isometry()[3]
    roots = compiler.root_lines()
    fixture = json.loads((INPUTS / "P104-FIXTURE.json").read_text())[
        "section4_explicit_P104"]
    removed = {tuple(x) for x in fixture["F0"] + fixture["C"]}
    ports = [r for r in roots if r not in removed]
    need(len(roots) == 120 and len(ports) == 104, "P104 port inventory")
    inner = compiler.inner
    gram = [[inner(a, b) for b in ports] for a in ports]
    rows = []
    for t, row in enumerate(gram):
        sparse = []
        for s, value in enumerate(row):
            coefficient = Q((2 * int(t == s) - value), 2)
            if coefficient:
                sparse.append({"source": s, "source_root": list(ports[s]),
                               "gram": value, "coefficient": str(coefficient)})
        need(len(sparse) == 48, "each correction row has 48 charged entries")
        need(all(entry["gram"] in (-1, 1) for entry in sparse),
             "nonzero correction Gram entries are signed unit overlaps")
        rows.append({"target": t, "target_root": list(ports[t]),
                     "nonzero": sparse})
    need(sum(len(row["nonzero"]) for row in rows) == 4992,
         "complete correction entry count")

    word = json.loads((INPUTS / "LOWRANK-WITNESS.json").read_text())
    base_n = len(word["program"])
    need(base_n == 4058, "source channel event count")
    state, frames = replay_rows(word, roots, ports, gram)
    full_key = basis_span(FULL)
    for s in range(104):
        need(frames["X" + str(s)] == full_key,
             "source X register not full-frame at the declared tail cut")
    for t in range(104):
        target_key = basis_span(word["final_frames"]["Y" + str(t)])
        need(len(target_key) == 8 and frames["Y" + str(t)] == target_key,
             "target Y register not at its declared rank-eight frame")

    augmented = copy.deepcopy(word)
    new_transports = []
    for row in rows:
        t = row["target"]
        reg = "Y" + str(t)
        old_compressed = list(word["final_frames"][reg])
        old_physical = list(compiler.canon(transform(x) for x in old_compressed))
        full_physical = list(compiler.canon(transform(x) for x in FULL))
        old_chart = compiler.CE.canonical_frame(9, old_physical)
        full_chart = compiler.CE.canonical_frame(9, full_physical)
        promote_operator = old_chart.adjoint().then(full_chart)
        promote_recipe, _ = compiler.CE.lower_child(promote_operator)
        promote_expected = compiler.N.adjoint(compiler.N.frame(old_physical, 9)) + compiler.N.frame(full_physical, 9)
        need(promote_recipe["rank"] == 1, "rank-one P104 target promotion")
        compiler.N.equal(compiler.N.recipe(promote_recipe), promote_expected,
                         "independent native promotion recipe")
        promote_event = ["transport", reg, old_compressed, FULL[:], 1]
        augmented["program"].append(promote_event)
        new_transports.append({"target": t, "direction": "promote", "rank": 1,
                               "old_compressed": old_compressed,
                               "new_compressed": FULL[:],
                               "old_physical": old_physical,
                               "new_physical": full_physical,
                               "recipe": promote_recipe})
        for entry in row["nonzero"]:
            augmented["program"].append([
                "add", reg, "X" + str(entry["source"]),
                entry["coefficient"], FULL[:]])
        descend_operator = full_chart.adjoint().then(old_chart)
        descend_recipe, _ = compiler.CE.lower_child(descend_operator)
        descend_expected = compiler.N.adjoint(compiler.N.frame(full_physical, 9)) + compiler.N.frame(old_physical, 9)
        need(descend_recipe["rank"] == 1, "rank-one P104 target restoration")
        compiler.N.equal(compiler.N.recipe(descend_recipe), descend_expected,
                         "independent native restoration recipe")
        augmented["program"].append(["transport", reg, FULL[:], old_compressed, 1])
        new_transports.append({"target": t, "direction": "restore", "rank": 1,
                               "old_compressed": FULL[:],
                               "new_compressed": old_compressed,
                               "old_physical": full_physical,
                               "new_physical": old_physical,
                               "recipe": descend_recipe})

    need(augmented["program"][:base_n] == word["program"], "source channel prefix changed")
    need(augmented["initial_frames"] == word["initial_frames"]
         and augmented["final_frames"] == word["final_frames"],
         "source endpoints changed")
    receipt = replay_rows(augmented, roots, ports, gram, corrected=True)
    state, frames = receipt
    need(len(augmented["program"]) == base_n + 5200, "augmented event count")
    need(sum(e[0] == "add" for e in augmented["program"]) == 7616,
         "base and correction scalar addition count")
    need(sum(e[0] == "transport" for e in augmented["program"])
         == sum(e[0] == "transport" for e in word["program"]) + 208,
         "complete frame-change count")
    return word, augmented, rows, new_transports, gram, ports, base_n


def replay_rows(word, roots, ports, gram, corrected=False):
    initial = word["initial_frames"]
    state = {name: {name: Q(1)} for name in initial}
    frames = {name: basis_span(frame) for name, frame in initial.items()}
    scalar = Counter()
    for event_index, event in enumerate(word["program"]):
        op = event[0]
        if op == "transport":
            _, reg, old, new, rank = event
            need(reg in frames and frames[reg] == basis_span(old),
                 "literal transport input frame at event " + str(event_index))
            need(abs(len(canonical(old)) - len(canonical(new))) == rank,
                 "literal transport rank at event " + str(event_index))
            frames[reg] = basis_span(new)
        elif op == "zero":
            _, reg, frame = event
            need(reg == "C" and reg not in state, "owned private zero")
            state[reg] = {}
            frames[reg] = basis_span(frame)
            scalar[op] += 1
        elif op == "erase":
            _, reg, frame = event
            need(reg == "C" and reg in state and frames[reg] == basis_span(frame),
                 "owned private erase")
            state.pop(reg)
            frames.pop(reg)
            scalar[op] += 1
        elif op == "copy":
            _, reg, src, frame = event
            need(reg in state and not state[reg] and frames[reg] == frames[src]
                 == basis_span(frame), "common-chart copy")
            state[reg] = dict(state[src])
            scalar[op] += 1
        else:
            need(op == "add", "unknown scalar event")
            _, reg, src, coefficient, frame = event
            need(reg != src and reg in state and src in state
                 and frames[reg] == frames[src] == basis_span(frame),
                 "common-chart scalar addition")
            c = Q(coefficient)
            for column, value in list(state[src].items()):
                result = state[reg].get(column, Q(0)) + c * value
                if result:
                    state[reg][column] = result
                else:
                    state[reg].pop(column, None)
            scalar[op] += 1
    need(set(state) == set(frames) == set(initial), "private storage not restored")
    need(set(word["final_frames"]) == set(initial), "endpoint register inventory")
    for name in initial:
        expected = {name: Q(1)}
        if name.startswith("Y"):
            t = int(name[1:])
            expected.update({"X" + str(s): Q(gram[t][s], 2)
                             for s in range(104) if gram[t][s]})
            if corrected:
                expected = {name: Q(1), "X" + str(t): Q(1)}
        need(state[name] == expected, "exact arbitrary-input row at endpoint " + name)
        need(frames[name] == basis_span(word["final_frames"][name]),
             "endpoint frame restoration " + name)
    return state, frames


def negative_controls(word, augmented, rows, gram, ports, roots):
    controls = {}
    bad = copy.deepcopy(augmented)
    first_add = next(i for i, e in enumerate(bad["program"]) if i >= len(word["program"]) and e[0] == "add")
    bad["program"][first_add][3] = str(-Q(bad["program"][first_add][3]))
    try:
        replay_rows(bad, roots, ports, gram, corrected=True)
    except (ValueError, StopIteration):
        controls["wrong_correction_sign"] = True
    else:
        raise ValueError("accepted wrong correction sign")

    bad = copy.deepcopy(augmented)
    bad["program"].pop(len(word["program"]))
    try:
        replay_rows(bad, roots, ports, gram, corrected=True)
    except (ValueError, StopIteration):
        controls["missing_promotion"] = True
    else:
        raise ValueError("accepted correction without promotion")

    bad = copy.deepcopy(augmented)
    last = next(i for i in range(len(word["program"]), len(bad["program"]))
                if bad["program"][i][0] == "transport" and bad["program"][i][1] == "Y0"
                and bad["program"][i][2] == FULL)
    bad["program"].pop(last)
    try:
        replay_rows(bad, roots, ports, gram, corrected=True)
    except (ValueError, StopIteration):
        controls["missing_restoration"] = True
    else:
        raise ValueError("accepted missing target frame restoration")

    bad = copy.deepcopy(augmented)
    bad["program"].pop(first_add)
    try:
        replay_rows(bad, roots, ports, gram, corrected=True)
    except (ValueError, StopIteration):
        controls["missing_correction_entry"] = True
    else:
        raise ValueError("accepted missing correction entry")
    return controls


def write_stable(path, payload):
    if path.exists():
        # Generated gzip containers vary across Python/zlib; compare exact payload bytes.
        retained = path.read_bytes()
        if path.suffix == ".gz":
            retained, payload = gzip.decompress(retained), gzip.decompress(payload)
        need(retained == payload, "reproducible artifact drift: " + path.name)
    else:
        path.write_bytes(payload)


def main():
    check_pins()
    native = base_replay()
    compiler = load_compiler()
    word, augmented, rows, transports, gram, ports, prefix = correction_data(compiler)

    roots = compiler.root_lines()
    controls = negative_controls(word, augmented, rows, gram, ports, roots)
    base_result = json.loads((INPUTS / "LOWRANK-RESULT.json").read_text())
    paid = {int(k): int(v) for k, v in base_result["paid_profile"].items()}
    native_paid = dict(paid)
    paid[1] += len(transports)
    need(paid == {1: 1282, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8},
         "augmented native paid profile")
    rank_mass = sum(rank * count for rank, count in paid.items())
    need(rank_mass == 2576, "augmented rank mass")

    ceiling_path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("p104_tail_exact_ceiling", ceiling_path)
    ceiling = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ceiling)
    grid = Q(1, 10**15)
    native_interval = ceiling.ceiling(native_paid, 73, 896, 9, 64, grid=grid)
    interval = ceiling.ceiling(paid, 73, 896, 9, 64, grid=grid)
    shift = [interval[0] - native_interval[1],
             interval[1] - native_interval[0]]
    moment_at_one_percent = ceiling.relax(paid, 73, 896, 9, 64, Q(1, 99))
    need(moment_at_one_percent[0] > 1,
         "exact favorable paid-profile screen should reject one-percent saving")

    witness_bytes = gzip.compress((json.dumps(augmented, sort_keys=True, separators=(",", ":"))
                                   + "\n").encode(), mtime=0)
    rows_object = {"formula": "coefficient[t,s] = delta[t,s] - G[t,s]/2",
                   "gram_matrix": gram, "rows": rows,
                   "row_count": 104, "nonzero_entries": 4992}
    rows_bytes = (json.dumps(rows_object, sort_keys=True, indent=2) + "\n").encode()
    transport_object = {"source_native_checker_sha256": EXPECTED_PINS[
        "research/p104-native-channel/vendor/native_verify.py"],
        "transports": transports, "rank_one_transport_count": 208}
    transport_bytes = gzip.compress((json.dumps(transport_object, sort_keys=True,
                                                separators=(",", ":")) + "\n").encode(), mtime=0)
    # Validate exact mathematical payloads first; bind the retained archive bytes.
    artifacts = [("AUGMENTED-WITNESS.json.gz", witness_bytes),
                 ("CORRECTION-ROWS.json", rows_bytes),
                 ("SIDE-TRANSPORTS.json.gz", transport_bytes)]
    for name, payload in artifacts:
        write_stable(HERE / name, payload)
    result = {
        "status": "PASS_P104_EXACT_TAIL_SIDE_CORRECTION",
        "track": "complex-mechanisms", "seed": "749717109203f916f620456c85e26673",
        "priority_revision": 4, "base_commit": "7c1e7811c730b17fe0eeef6c82ef011318b0465e",
        "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
        "native_channel_status": native["status"], "native_prefix_events": prefix,
        "formal_columns": 280, "ports": 104, "correction_rows": 104,
        "nonzero_scalar_additions": 4992, "rank_one_frame_changes": 208,
        "augmented_events": len(augmented["program"]), "paid_profile": paid,
        "rank_mass": rank_mass,
        "native_channel_local_ceiling_grid_bracket": [str(x) for x in native_interval],
        "optimistic_local_ceiling_grid_bracket": [str(x) for x in interval],
        "corrected_minus_native_ceiling_interval": [str(x) for x in shift],
        "exact_moment_at_a_1_over_99": [str(x) for x in moment_at_one_percent],
        "negative_controls": controls,
        "native_channel_is_frozen": True,
        "scope": "One finite rowwise I-G/2 correction appended at the final source-completed cut. Exact 280-column identity and native rank-one transports are verified. This does not supply global chronological helper hosting, all-size admission, precision accounting, or a new kappa.",
        "remaining_obligation": "Prove a globally legal owner/host schedule for the appended source reads and rank-one transports, charge its copied information, and reassess complete supplier cost.",
        "artifact_sha256": {
            "AUGMENTED-WITNESS.json.gz": digest((HERE / "AUGMENTED-WITNESS.json.gz").read_bytes()),
            "CORRECTION-ROWS.json": digest((HERE / "CORRECTION-ROWS.json").read_bytes()),
            "SIDE-TRANSPORTS.json.gz": digest((HERE / "SIDE-TRANSPORTS.json.gz").read_bytes()),
        },
    }
    result_bytes = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    for name, payload in [
        ("AUGMENTED-WITNESS.json.gz", witness_bytes),
        ("CORRECTION-ROWS.json", rows_bytes),
        ("SIDE-TRANSPORTS.json.gz", transport_bytes),
        ("RESULT.json", result_bytes),
    ]:
        write_stable(HERE / name, payload)
    # Controls use a discarded local root parameter; endpoint verification
    # derives all target/source rows directly from the frozen word and G.
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
