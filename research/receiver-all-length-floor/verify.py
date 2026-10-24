#!/usr/bin/env python3
"""All-length frame-cost floor, separately implemented from #4546/#4567.

The inherited #4470 constructor supplies data only. No predecessor search,
relaxation, endpoint census, or acceptance function is imported here.
Prepared for mihir-s-05 with substantial OpenAI Codex assistance. Apache-2.0.
"""
from bisect import bisect_right
from collections import Counter
from functools import lru_cache
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = (
    "research/fresh-helper-boundary/CHANGES.json",
    "research/fresh-helper-boundary/native.py",
    "research/joint-helper-lattice/PATCH.json",
    "research/joint-helper-lattice/native_joint.py",
    "research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-CANONICAL.json.gz",
    "research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz",
    "research/missing-join-frame/PATCH.json",
)
PAIRS = ((0, 1), (0, 2), (1, 2))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    require(sorted(r["path"] for r in rows) == list(INPUTS), "exact input closure")
    for row in rows:
        raw = (root / row["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def span(vectors):
    values = {0}
    for vector in vectors:
        require(type(vector) is int and 0 <= vector < 512, "binary frame coordinate")
        values.update(x ^ vector for x in tuple(values))
    return frozenset(values)


def dimension(space):
    size = len(space)
    require(size > 0 and size & (size - 1) == 0, "power-of-two frame size")
    return size.bit_length() - 1


def constructor_data():
    # -B alone does not prevent cached imports. This child has a fresh cache
    # namespace as well as isolated Python and authenticated source inputs.
    code = (
        "import json,sys;sys.path.insert(0,sys.argv[1]);"
        "import native_joint;candidate,programs,*_=native_joint.construct();"
        "print(json.dumps([candidate,programs['forward']]))"
    )
    with tempfile.TemporaryDirectory(prefix="receiver-floor-pyc-") as cache:
        completed = subprocess.run(
            [sys.executable, "-I", "-B", "-X", "pycache_prefix=" + cache, "-c", code,
             str(ROOT / "research/joint-helper-lattice")],
            check=True, capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
    return json.loads(completed.stdout)


def contacts(event):
    """Persistent uses: (role, frame required before operation, frame after)."""
    if event[0] == "scalar":
        gate = event[1]
        require(gate[0] in ("add", "copy", "scale", "clear"), "known scalar kind")
        require(gate[0] != "clear" or gate[1][0] != "L", "no persistent clear")
        roles = gate[1:3] if gate[0] in ("add", "copy") else gate[1:2]
        return [(r[1], event[2], event[2]) for r in roles if r[0] == "L"]
    if event[0] == "warp":
        require(event[1][0] == "L", "persistent warp")
        return [(event[1][1], event[3], event[4])]
    return []


def extract_windows(candidate, program):
    """Next-use lists bind exits; chronology supplies entrances.

    Indices follow the inherited convention: the program with climbs removed.
    Climb costs are reconstructed from the actual contact frames.
    """
    events = [e for e in program if e[0] != "climb"]
    uses = [[] for _ in candidate["start"]]
    use_positions = [[] for _ in candidate["start"]]
    for position, event in enumerate(events):
        for role, before, _ in contacts(event):
            uses[role].append(before)
            use_positions[role].append(position)
    frame_spaces = [span(basis) for basis in candidate["frames"]]
    current = list(candidate["start"])
    phase = None
    windows = []
    for position, event in enumerate(events):
        if event[0] == "phase":
            phase = event[1]
        pair = events[position:position + 2]
        if phase in ("B", "cleanup_tail") and len(pair) == 2 and all(
                e[0] == "scalar" and e[1][0] == "add" for e in pair):
            first, second = (e[1] for e in pair)
            if all(r[0] == "L" for g in (first, second) for r in g[1:3]):
                a, x, b, y = first[1][1], first[2][1], second[1][1], second[2][1]
                coefficients = []
                for gate in (first, second):
                    numerator, denominator = gate[3:5]
                    require(denominator != 0, "nonzero coefficient denominator")
                    if abs(numerator) != abs(denominator):
                        break
                    coefficients.append(1 if numerator * denominator > 0 else -1)
                if x == y and len({a, b, x}) == 3 and len(coefficients) == 2:
                    owners = (a, b, x)
                    exits = []
                    for role in owners:
                        next_use = bisect_right(use_positions[role], position + 1)
                        exits.append(uses[role][next_use] if next_use < len(uses[role])
                                     else candidate["final"][role])
                    windows.append({
                        "index": position, "phase": phase, "roles": list(owners),
                        "coefficients": coefficients,
                        "starts": tuple(frame_spaces[current[r]] for r in owners),
                        "ends": tuple(frame_spaces[f] for f in exits),
                        "frames": tuple(frame_spaces[e[2]] for e in pair),
                    })
        for role, _, after in contacts(event):
            current[role] = after
    return windows


def incumbent_profile(window):
    current = list(window["starts"])
    ranks = []
    for (i, j), frame in zip(((0, 2), (1, 2)), window["frames"]):
        for role in (i, j):
            require(current[role] <= frame, "incumbent contact containment")
            gap = dimension(frame) - dimension(current[role])
            if gap:
                ranks.append(gap)
            current[role] = frame
    for frame, end in zip(current, window["ends"]):
        require(frame <= end, "incumbent exit containment")
        gap = dimension(end) - dimension(frame)
        if gap:
            ranks.append(gap)
    return tuple(sorted(ranks))


def relaxed_profiles(starts, ends, required=(4, 4, 0)):
    """All finite contact words, quotiented by a strictly increasing state.

    masks[i] records initial roles that can have met role i along a temporal
    undirected contact path. This overapproximates scalar information flow.
    dims[i] is the current contact dimension. No coefficients or word cap.
    """
    if not all(s <= e for s, e in zip(starts, ends)):
        return frozenset(), 0
    end_dims = tuple(map(dimension, ends))
    joins = {mask: span(v for i in range(3) if mask & (1 << i) for v in starts[i])
             for mask in range(1, 8)}

    @lru_cache(None)
    def visit(masks, dims):
        profiles = set()
        if all(mask & needed == needed for mask, needed in zip(masks, required)):
            profiles.add(tuple(sorted(e - d for d, e in zip(dims, end_dims) if e > d)))
        for i, j in PAIRS:
            merged = masks[i] | masks[j]
            lower = joins[merged]
            upper = ends[i] & ends[j]
            if not lower <= upper:
                continue
            for contact_dim in range(max(dims[i], dims[j], dimension(lower)), dimension(upper) + 1):
                next_masks, next_dims = list(masks), list(dims)
                next_masks[i] = next_masks[j] = merged
                next_dims[i] = next_dims[j] = contact_dim
                next_state = (tuple(next_masks), tuple(next_dims))
                if next_state == (masks, dims):
                    continue  # zero-cost self-loop; no remaining endpoint constraint
                rank_before = sum(dims) + sum(mask.bit_count() for mask in masks)
                rank_after = sum(next_dims) + sum(mask.bit_count() for mask in next_masks)
                require(rank_after > rank_before, "strictly increasing state rank")
                gaps = tuple(contact_dim - dims[k] for k in (i, j) if contact_dim > dims[k])
                for tail in visit(*next_state):
                    profiles.add(tuple(sorted(gaps + tail)))
        return frozenset(profiles)

    profiles = visit((1, 2, 4), tuple(map(dimension, starts)))
    mass = sum(end_dims) - sum(map(dimension, starts))
    require(all(sum(p) == mass for p in profiles), "all terminal gaps charged")
    return profiles, visit.cache_info().currsize


def concave_floor(old, other):
    """Integer certificate for every increasing concave f with f(0)=0.

    Equal mass and ordered capped-rank sums imply the cost ordering.
    README proves the discrete-slope expansion; no floating point is used.
    """
    return (sum(old) == sum(other) and all(
        sum(min(r, cap) for r in old) <= sum(min(r, cap) for r in other)
        for cap in range(1, 10)))


def boundary_record(window):
    def basis(space):
        out, generated = [], {0}
        for vector in sorted(space):
            if vector not in generated:
                out.append(vector)
                generated.update(x ^ vector for x in tuple(generated))
        require(generated == space, "canonical basis spans frame")
        return out
    names = {"starts": "start_bases", "ends": "exit_bases", "frames": "contact_bases"}
    return {names.get(key, key): ([basis(s) for s in value] if key in names else value)
            for key, value in window.items()}


def compute():
    authenticate()
    windows = extract_windows(*constructor_data())
    require(len(windows) == 128, "128 eligible source windows")
    require(len({w["index"] for w in windows}) == 128, "unique window indices")
    require(Counter(w["phase"] for w in windows) == {"B": 123, "cleanup_tail": 5}, "phase census")
    rows = []
    for window in windows:
        old = incumbent_profile(window)
        profiles, states = relaxed_profiles(window["starts"], window["ends"])
        require(old in profiles, "incumbent admitted at " + str(window["index"]))
        require(all(concave_floor(old, p) for p in profiles), "concave floor at " + str(window["index"]))
        rows.append({**boundary_record(window), "incumbent_ranks": list(old),
                     "relaxed_rank_partitions": [list(p) for p in sorted(profiles)],
                     "states": states, "concave_floor": True})
    return {"status": "PASS_RECEIVER_ALL_LENGTH_CONCAVE_FLOOR", "windows": rows,
            "window_count": len(rows), "state_count": sum(r["states"] for r in rows),
            "partition_count": sum(len(r["relaxed_rank_partitions"]) for r in rows),
            "boundary_sha256": hashlib.sha256(canonical([boundary_record(w) for w in windows])).hexdigest(),
            "word_length_cap": None, "coefficient_cap": None,
            "cost_scope": "Every increasing concave rank weight f with f(0)=0; in particular r^q for 0<q<=1",
            "new_kappa_claimed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="author the receipt; not the registered replay")
    args = parser.parse_args()
    result = compute()
    if args.write:
        header = json.dumps({k: v for k, v in result.items() if k != "windows"}, indent=2)
        rows = ",\n".join("    " + json.dumps(row, sort_keys=True) for row in result["windows"])
        receipt = header[:-2] + ',\n  "windows": [\n' + rows + "\n  ]\n}\n"
        (HERE / "RESULT.json").write_text(receipt, encoding="utf-8", newline="\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        require(canonical(result) == canonical(expected), "complete retained receipt equality")
    print(json.dumps({k: v for k, v in result.items() if k != "windows"}, sort_keys=True))


if __name__ == "__main__":
    main()
