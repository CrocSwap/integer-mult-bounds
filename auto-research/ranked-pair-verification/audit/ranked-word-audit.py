#!/usr/bin/env python3
"""Independently bind the selected words, frame paths, CRT inputs and child list.

Default: reconstruct profiler inputs from the bundled words and run the pinned
C++ profiler. --reuse-profiles instead requires byte-identical existing inputs
and receipt-identical existing outputs; it does not rerun the profiler.

Both modes directly interpret every Boolean basis direction in both orientations,
including arbitrary dirty auxiliaries. This is finite verification, not a proof
of the full framed-word, fixed-tape or analytic multiplication transfer.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
import gzip
import json
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "finite-frames"))
from pinned_upstream import PIN, generated_directory, git, require, validate_upstream
from scatter_binding_audit import verify_scatter


def audit_word(h, root, generated, manifest, reuse_profiles, profiler, exactness, js):
    path = PACKAGE / f"finite-frames/pair-ranked-word-{h}.json.gz"
    packed = path.read_bytes()
    raw = gzip.decompress(packed)
    word = json.loads(raw)
    receipt = json.loads((PACKAGE / f"finite-frames/pair-ranked-{h}-receipt.json").read_text())
    word_hash = sha256(raw).hexdigest()
    require(word_hash == manifest["words"][str(h)]["word_sha256"] == receipt["word_sha256"] ==
            receipt["transitions"]["word_sha256"], "Word source binding")
    require(sha256(packed).hexdigest() == manifest["words"][str(h)]["gzip_sha256"], "Bundled gzip binding")
    v, roles = word["v"], word["R"]
    require(h == word["h"] and v == comb(h, 3), "Axis mismatch")
    frames = [tuple(frame) for frame in word["frames"]]
    require(len(set(frames)) == len(frames), "Duplicate frame")
    ranks = []
    for common, union in frames:
        require(type(common) is int and type(union) is int and
                0 < common < (1 << h) and union < (1 << h) and not (common & ~union), "Frame domain")
        require(common.bit_count() in (1, 2) or common == union and common.bit_count() == 3,
                "Frame outside the certified family")
        ranks.append(1 if common == union else union.bit_count() - common.bit_count())
    strict_scatter = verify_scatter(word)
    # Two duplicate unrecorded XORs cancel algebraically, yet must be rejected
    # because the literal scatter incidence list is part of the paid interface.
    mutant = dict(word)
    unrecorded = next(s for s in range(roles) if s not in {out[0] for out in word["outputs"]})
    rogue = [v, 2 * v + unrecorded]
    mutant["scatter"] = word["scatter"] + [rogue, rogue]
    try:
        verify_scatter(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("Strict scatter binding accepted duplicate unrecorded XORs")

    actual = [None] * roles
    transitions = Counter()

    def incidence(slot, frame):
        require(type(slot) is int and 0 <= slot < roles and
                type(frame) is int and 0 <= frame < len(frames), "Operation domain")
        old = actual[slot]
        if old is not None:
            common, union = frames[old]
            new_common, new_union = frames[frame]
            require(not (new_common & ~common) and not (union & ~new_union), "Frame containment")
            require(ranks[frame] >= ranks[old], "Decreasing frame rank")
        if old != frame:
            transitions[old, frame] += 1
        actual[slot] = frame

    triples = list(combinations(range(h), 3))
    lookup = {frame: index for index, frame in enumerate(frames)}
    for index, slot in word["sources"].items():
        mask = sum(1 << j for j in triples[int(index)])
        incidence(slot, lookup[mask, mask])
    for target, source, frame in word["ops"]:
        require(target != source, "Self XOR")
        incidence(target, frame)
        incidence(source, frame)
    for slot, frame, common, triple in word["outputs"]:
        incidence(slot, frame)

    event_state = [None] * roles
    events = Counter()
    for slot, old, new in word["events"]:
        require(type(slot) is int and 0 <= slot < roles and
                type(old) is int and -1 <= old < len(frames) and
                type(new) is int and 0 <= new < len(frames), "Event domain")
        old = None if old == -1 else old
        require(event_state[slot] == old, "Event chronology")
        if old != new:
            events[old, new] += 1
        event_state[slot] = new
    require(events == transitions and event_state == actual, "Actual word and event path differ")
    require(all(frame is not None for frame in actual), "Untouched physical role")

    # Independently reconstruct every transition charged to the CRT profiler,
    # including copied centers, terminal cleanup and side-output growth.
    catalog = [(0, 0, 0), (0, 0, h)] + [(c, u, rank) for (c, u), rank in zip(frames, ranks)]
    charged = Counter({(0 if a is None else a + 2, b + 2): count
                       for (a, b), count in transitions.items()})
    outputs, centers, singles = set(), 0, 0
    for slot, frame, common, triple in word["outputs"]:
        require(slot not in outputs and actual[slot] == frame, "Output terminal frame")
        outputs.add(slot)
        cm, um = frames[frame]
        if len(triple) == 1:
            require(cm == 1 << common and um == (1 << h) - 1 and ranks[frame] == h - 1, "Center frame")
            charged[0, frame + 2] += 1
            charged[frame + 2, 1] += 1
            centers += 1
        else:
            require(cm == 1 << common and
                    um == ((1 << h) - 1) ^ sum(1 << j for j in triple if j != common), "Side-output frame")
            singles += h - ranks[frame]
    require(centers == h, "Center count")
    for slot, frame in enumerate(actual):
        if slot not in outputs:
            charged[frame + 2, 1] += 1
    rank_mass = singles + sum((catalog[b][2] - catalog[a][2]) * n for (a, b), n in charged.items())
    require(rank_mass == h * roles + h * (h - 1), "Charged transition mass")
    require(all(catalog[b][2] > catalog[a][2] and n > 0 for (a, b), n in charged.items()),
            "Nonpositive charged transition")
    encoded = bytearray(struct.pack("<6I2Q", h, v, roles, len(catalog), len(charged), singles, rank_mass, h * (h - 1)))
    for common, union, rank in catalog:
        encoded.extend(struct.pack("<2QI", common, union, rank))
    for (old, new), count in sorted(charged.items()):
        encoded.extend(struct.pack("<2Iq", old, new, count))
    binary_path = generated / f"ranked-{h}.bin"
    profile_path = Path(str(binary_path) + ".profiles.json")
    if reuse_profiles:
        require(bytes(encoded) == binary_path.read_bytes(), "Literal charges differ from existing CRT profiler input")
    else:
        binary_path.write_bytes(encoded)
        subprocess.run([str(profiler), str(binary_path)], check=True)
    profile_raw = profile_path.read_bytes()
    profile = json.loads(profile_raw)
    require(profile == receipt["profile"], "Fresh/existing CRT profile differs from selected receipt")
    require(profile["h"] == h and profile["v"] == v and profile["R"] == roles and
            profile["frames"] == len(catalog), "Profile axis/frame binding")
    blocks = profile["blocks"]
    require(len(blocks) == h + 1 and blocks[0] == blocks[-1] == 0 and
            all(type(n) is int and n >= 0 for n in blocks), "Profile domain")
    require(sum(t * n for t, n in enumerate(blocks)) == rank_mass == profile["rank_sum"] ==
            receipt["replay"]["rank_mass"], "Complete local rank mass")
    require(profile["crt_disagreements"] == 0, "CRT disagreement")
    exact = js(exactness(h))
    require(exact == receipt["exactness"], "Recomputed bounded-minor CRT arithmetic differs")

    # Interpret all basis columns simultaneously as integer bitsets, independent
    # of the compiler and its replay implementation. Linearity covers every
    # source, target and arbitrary dirty auxiliary state in both orientations.
    initial = [1 << i for i in range(2 * v + roles)]
    mixer = [(2 * v + a, 2 * v + b) for a, b, _ in word["ops"]]
    source_copy = [(2 * v + slot, int(index)) for index, slot in word["sources"].items()]
    scatter = [tuple(pair) for pair in word["scatter"]]
    wrapped = mixer + scatter + mixer[::-1] + source_copy + mixer + scatter + mixer[::-1] + source_copy
    for dual in (False, True):
        state = initial.copy()
        for target, source in (reversed(wrapped) if dual else wrapped):
            if dual:
                target, source = source, target
            require(0 <= target < len(state) and 0 <= source < len(state), "Wrapped word domain")
            state[target] ^= state[source]
        expected = initial.copy()
        for index in range(v):
            expected[index if dual else v + index] ^= initial[v + index if dual else index]
        require(state == expected, "Full basis semantic failure")

    original_raw = git(root, "show", PIN + f":research/pair-assembly/frame/frame-profiles-{h}.json")
    original = json.loads(original_raw)
    require(roles == original["R"], "Role count changed from PR62")
    delta = [n - old for n, old in zip(blocks, original["blocks"])]
    caps = {k: sum(n * min(t, k) for t, n in enumerate(delta)) for k in range(1, h + 1)}
    require(sum(t * n for t, n in enumerate(delta)) == 0, "Rank mass changed from PR62")
    require(all(value <= 0 for value in caps.values()) and caps[1] < 0, "Concave dominance failed")
    print(f"PASS h={h}: complete dirty basis both orientations, literal charges, CRT profile and concave dominance", flush=True)
    return dict(h=h, v=v, R=roles, word_sha256=word_hash,
                packed_sha256=sha256(packed).hexdigest(), literal_scatter=strict_scatter,
                duplicate_unrecorded_scatter_rejected=True, transition_types=len(transitions),
                complete_charged_transition_types=len(charged), binary_profiler_input_sha256=sha256(encoded).hexdigest(),
                side_growth_singletons=singles, full_basis_directions=2 * v + roles,
                full_basis_orientations=2, elementary_xors=len(mixer), wrapped_xors=len(wrapped),
                profile=blocks, mass=rank_mass, profiler_output_sha256=sha256(profile_raw).hexdigest(),
                original_profile_sha256=sha256(original_raw).hexdigest(), exactness=exact,
                profile_delta=delta, capped_delta=caps,
                concave_dominance="Strictly smaller sum n_t*t^p for every 0<p<1 by positive min-basis second differences")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--generated", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="JSON audit receipt; defaults to GENERATED/ranked-word-audit.json")
    parser.add_argument("--reuse-profiles", action="store_true",
                        help="Read and bind existing profiler inputs/outputs instead of rerunning C++")
    args = parser.parse_args()
    root, manifest, source_hashes, _ = validate_upstream(args.upstream)
    generated = generated_directory(args.generated, root)
    experiments = root / "scripts/experiments"
    sys.path.insert(0, str(experiments))
    from binary_frame_math import exactness, js
    profiler = generated / "ranked-profile-verifier"
    if not args.reuse_profiles:
        subprocess.run(["c++", "-O3", "-std=c++17", "-I",
                        str(root / "references/frame-compiler/pr48/scripts/partial_swap"),
                        str(experiments / "binary_frame_profiles.cpp"), "-o", str(profiler)], check=True)
    axes = [audit_word(h, root, generated, manifest, args.reuse_profiles, profiler, exactness, js)
            for h in (23, 25)]
    N, m = comb(23, 3) * comb(25, 3), 575
    parts = {"data": Counter({1: 18 * N, 21: 2 * N, 17: 2 * N, 481: 2 * N}),
             "endpoint": Counter({1: N})}
    for axis in axes:
        h, v, roles = axis["h"], axis["v"], axis["R"]
        repetition, bank = N // v, N // v * roles
        parts[f"internal_{h}"] = Counter({t: repetition * n for t, n in enumerate(axis["profile"]) if t and n})
        parts[f"exterior_{h}"] = Counter({h: bank, m - 2 * h: bank})
        parts[f"growth_{h}"] = Counter({1: 2 * N, h - 2: 2 * N})
    children = sum(parts.values(), Counter())
    W = 2 * N + sum(N // axis["v"] * axis["R"] for axis in axes)
    mass = sum(t * n for t, n in children.items())
    selected_path = PACKAGE / "selected-certificate.json"
    selected = json.loads(selected_path.read_text())
    bit = selected["bit"]
    require((bit["m"], bit["W"], bit["total_rank"], bit["deficit"]) ==
            (m, W, mass, m * W - mass), "Selected aggregate dimensions mismatch")
    require(children == Counter({int(t): n for t, n in bit["child_multiplicities"].items()}),
            "Selected aggregate children mismatch")
    require(all(selected["finite_bridge"]["bit"][key] == value
                for key, value in [("m", m), ("W", W), ("maxchild", max(children))]),
            "Selected assembly bit bridge mismatch")
    result = dict(status="PASS", upstream_pin=PIN, verified_source_files=len(source_hashes),
                  verified_upstream_sources=manifest["sources"], verified_compiler_transform=manifest["compiler_transform"],
                  profiler_mode="reused and bound" if args.reuse_profiles else "fresh pinned C++ execution",
                  axes=axes, m=m, N=N, W=W, s=mass, deficit=m * W - mass, maxchild=max(children),
                  child_multiplicities=dict(sorted(children.items())),
                  selected_certificate_sha256=sha256(selected_path.read_bytes()).hexdigest(),
                  scope="Independent literal scatter, event/operation binding, full Boolean basis, CRT-input reconstruction, bounded-minor arithmetic, child aggregation and all-exponent concave dominance. The pinned C++ profiler and its general minor-bound proof are inherited. Full framed-word/tape/analytic transfer remains outside this finite check; run the package exact-arithmetic verifier separately.")
    output = args.output.resolve() if args.output else generated / "ranked-word-audit.json"
    require(output != root and root not in output.parents, "Audit receipt must be outside upstream checkout")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"PASS selected child list: W={W}, mass={mass}, deficit={m * W - mass}; receipt {output}")


if __name__ == "__main__":
    main()
