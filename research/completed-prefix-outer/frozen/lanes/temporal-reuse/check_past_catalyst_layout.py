"""Check the bit permutations used by the past-coordinate layout."""

from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REVISION = "3ae9a6f3ac74ded022ab3b4872a7357a621af6fb"
PINS = {
    "upstream/build/sections/02-streams.tex":
        "606c80db61cad13aa0c3b6060dc4b88dbbe7ac60cdd831aa93f28d908fd09dab",
    "upstream/build/sections/04-swap.tex":
        "412b170ccaab38dba96e95e3cbfae09f4876a9818f8d278776a746b0f8044906",
    "upstream/build/sections/05-layers.tex":
        "20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594",
    "upstream/build/sections/06-transforms.tex":
        "924316e4bc905066281d8f9e8746a49d8829aeb393688608deb1e61c3c87853c",
    "research/community-frontier1094-audit/ASSEMBLY.json":
        "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def swap(fields, a, b, width):
    need(a+width <= b or b+width <= a, "Swap fields overlap")
    fields[a:a+width], fields[b:b+width] = fields[b:b+width], fields[a:a+width]


def permutation_inverse(labels):
    out = [0]*len(labels)
    for position, label in enumerate(labels):
        out[label] = position
    return out


def rotation_check():
    cases = []
    for chunks in range(1, 7):
        for width in range(1, 8):
            length = chunks*width
            for offset in range(width):
                cut = (length-offset) % length
                labels = list(range(2*length))
                if cut:
                    swap(labels, 0, 2*length-cut, cut)
                    swap(labels, cut, length, length-cut)
                    swap(labels, 0, length, length)
                expected = (list(range(cut, length))+list(range(cut))
                            +list(range(2*length-cut, 2*length))
                            +list(range(length, 2*length-cut)))
                need(labels == expected, "Three-swap rotation identity")
                location = permutation_inverse(labels)
                old_selected = [j*width for j in range(chunks)]
                new_selected = [j*width+offset for j in range(chunks)]
                need([location[x] for x in old_selected] == new_selected,
                     "Selected offsets differ")
                mask_old = sum(1 << x for x in old_selected)
                mask_new = sum(1 << x for x in new_selected)
                pulled_mask = sum(((mask_new >> position) & 1) << label
                                  for position, label in enumerate(labels))
                need(pulled_mask == mask_old, "Conjugated selected translation")
                need(not (pulled_mask >> length), "Spectator field is changed")
                for i in range(2*length):
                    need(labels[location[i]] == i, "Inverse placement")
                cases.append([chunks, width, offset])
    return cases


def reserve_check():
    cases = []
    for copies in range(1, 5):
        active, past = 64*copies, 9*copies
        for width in range(2, 8):
            group = active*width
            length = past*width
            need(2*length < group, "The reserve does not fit")
            total = 4*group
            sources = [j*width+width-1 for j in range(past)]
            early_targets = [3*group+j*width for j in range(past)]
            late_targets = [j*width for j in range(past)]
            labels = list(range(total))
            for source, target in zip(sources, early_targets):
                swap(labels, source, target, 1)
            location = permutation_inverse(labels)
            need([location[x] for x in sources] == early_targets, "Early past placement")
            spectator = range(3*group+length, 3*group+2*length)
            need(all(labels[x] == x for x in spectator), "Early spectator is not disjoint")
            for source, target in reversed(list(zip(sources, early_targets))):
                swap(labels, source, target, 1)
            need(labels == list(range(total)), "Early placement does not restore")
            for source, target in zip(sources, late_targets):
                swap(labels, source, target, 1)
            location = permutation_inverse(labels)
            need([location[x] for x in sources] == late_targets, "Late past placement")
            need(all(labels[x] == x for x in range(group, total)),
                 "Late placement changes an uncompleted group")
            for source, target in reversed(list(zip(sources, late_targets))):
                swap(labels, source, target, 1)
            need(labels == list(range(total)), "Late placement does not restore")
            cases.append([copies, width, active, past])
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=ROOT / "worktrees/k5-centre-sharing")
    parser.add_argument("--out", type=Path, default=HERE / "PAST-CATALYST-LAYOUT.json")
    args = parser.parse_args()
    sources = {}
    for path, digest in PINS.items():
        raw = subprocess.check_output(["git", "-C", str(args.repo), "show", REVISION+":"+path])
        need(sha256(raw).hexdigest() == digest, "Source hash: "+path)
        sources[path] = raw
    assembly = json.loads(sources["research/community-frontier1094-audit/ASSEMBLY.json"])
    epsilon = Fraction(assembly["outer"]["epsilon_positive"])
    c = Fraction(assembly["outer"]["c_positive"])
    kappa = Fraction(assembly["kappa"])
    need(1-epsilon*(1+c) > 0, "There are not asymptotically many chunk groups")
    need(1-epsilon-kappa > 0, "The finite initial digit moves are too expensive")
    receipt = {
        "status": "PASS_PAST_CATALYST_LAYOUT",
        "revision": REVISION, "source_sha256": PINS,
        "rotation_cases": rotation_check(),
        "two_reserve_cases": reserve_check(),
        "interchanges_per_offset_alignment": 6,
        "interchanges_for_nonadjacent_past_block": 2,
        "fixed_slot_order_maps": "At most the fixed number of native slots",
        "added_native_children": 0,
        "extra_address_bits": 0,
        "initial_and_final_bit_moves": "O(d) per transform",
        "per_invocation_time": "O(V ((eK)^tau+1)) under the cited chunk-swap interface",
        "chunk_group_margin": str(1-epsilon*(1+c)),
        "startup_margin": str(1-epsilon-kappa),
        "scope": "Exact address wrappers conditional on a native word that fixes the spectator fields.",
        "not_claimed": ["The fixed-past cover condition", "The active child profile",
                        "The selected finite compact-engine invoice", "Recursive encoded-child closure",
                        "A kappa improvement"],
    }
    args.out.write_text(json.dumps(receipt, sort_keys=True, indent=2)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
