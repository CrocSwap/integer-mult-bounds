"""Certify the shared dispatcher, minimality partition and packed representation.

Produced by Nick Petalas. Apache-2.0.
"""
import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
implementation = runpy.run_path(str(HERE / "dispatcher.py"))
require = implementation["require"]


def quotient_certificate(table, roots, quotient, entries, mapping):
    """A complete homomorphism check proves all tapes, including nontermination."""
    n, m = len(table) - 4, len(quotient) - 4
    require(len(mapping) == len(table), "wrong mapping size")
    require(set(mapping) == set(range(len(quotient))), "mapping not onto")
    require(tuple(mapping[n + i] for i in range(4)) == tuple(m + i for i in range(4)),
            "output labels not preserved")
    require(all(mapping[s] < m for s in range(n)), "premature output")
    require(tuple(mapping[r] for r in roots) == entries, "wrong entry pointer")
    require(all(tuple(mapping[t] for t in row) == quotient[mapping[s]]
                for s, row in enumerate(table)), "transition does not commute")


def partition_certificate(table, history, mapping):
    """Check each refinement independently by sorting signatures, not interning."""
    n = len(table) - 4
    require(history[0] == (0,) * n + (1, 2, 3, 4), "wrong empty observation")
    for before, after in zip(history, history[1:]):
        signatures = [(0 if s < n else 1 + s - n,
                       before[row[0]], before[row[1]])
                      for s, row in enumerate(table)]
        order = sorted(range(len(table)), key=signatures.__getitem__)
        require(all((signatures[u] == signatures[v]) == (after[u] == after[v])
                    for u, v in zip(order, order[1:])), "wrong refinement split")
        require(len(set(after)) == len(set(signatures)), "reused class name")
    require(history[-1] == mapping, "wrong final partition")
    require(len(set(history[-1])) == len(set(history[-2])), "not stable")


def reachable(table, roots):
    seen = set(roots)
    frontier = list(roots)
    for index in range(len(table)):
        if index == len(frontier):
            break
        for target in table[frontier[index]]:
            if target not in seen:
                seen.add(target)
                frontier.append(target)
    require(len(seen) == len(table), "unreachable states in minimality count")


def run(table, start, bits):
    internal = len(table) - 4
    state = start
    if state >= internal:
        return state - internal, 0
    for used, bit in enumerate(bits, 1):
        state = table[state][bit]
        if state >= internal:
            return state - internal, used
    return None, len(bits)


def literal_controls(table, roots, quotient, entries):
    count = 0
    for root, entry in zip(roots, entries):
        for bits in product((0, 1), repeat=8):
            require(run(table, root, bits) == run(quotient, entry, bits),
                    "literal tape changed")
            count += 1
    return count


def sharp_separation(table, history):
    """Extract a pair not distinguished at depth 8 but distinguished at depth 9."""
    older, newer = history[8], history[9]
    representatives = {}
    pair = None
    for state, color in enumerate(older):
        prior = representatives.setdefault(color, state)
        if newer[prior] != newer[state]:
            pair = (prior, state)
            break
    require(pair is not None, "missing sharp depth-nine pair")
    left, right = pair
    bits = []
    for depth in range(9, 0, -1):
        if history[0][left] != history[0][right]:
            break
        choices = [b for b in (0, 1) if
                   history[depth - 1][table[left][b]] !=
                   history[depth - 1][table[right][b]]]
        require(bool(choices), "missing distinguishing continuation")
        bit = choices[0]
        bits.append(bit)
        left, right = table[left][bit], table[right][bit]
    require(len(bits) == 9 and run(table, pair[0], bits) != run(table, pair[1], bits),
            "incorrect depth-nine witness")
    return {"states": pair, "coins": "".join(map(str, bits))}


def rejection_controls(table, roots, quotient, entries, mapping, history):
    rejected = 0
    # Corrupt different parts of the complete certificate, not sample tapes.
    for kind in ("output", "entry", "edge", "map", "partition"):
        q, e, mp, h = list(quotient), list(entries), list(mapping), list(history)
        if kind == "output":
            mp[-1], mp[-2] = mp[-2], mp[-1]
        elif kind == "entry":
            e[0] = (e[0] + 1) % (len(q) - 4)
        elif kind == "edge":
            q[0] = (len(q) - 1, len(q) - 1)
        elif kind == "map":
            mp[0] = (mp[0] + 1) % (len(q) - 4)
        else:
            h[1] = (0,) * (len(table) - 4) + (1, 2, 3, 4)
        try:
            quotient_certificate(table, roots, q, e, mp)
            partition_certificate(table, h, mp)
        except ValueError:
            rejected += 1
    require(rejected == 5, "corrupted certificate accepted")
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--emit-dir", type=Path)
    args = parser.parse_args()
    table, roots = implementation["disjoint_bank"]()
    quotient, entries, mapping, history = implementation["minimize"](table, roots)
    quotient_certificate(table, roots, quotient, entries, mapping)
    partition_certificate(table, history, mapping)
    reachable(table, roots)
    reachable(quotient, entries)
    counts = [len(set(colors)) for colors in history]
    require(counts == [5, 15, 56, 282, 1850, 7426, 14824, 20274,
                       22450, 22486, 22486], "unexpected exact partition counts")
    require(len(quotient) - 4 == 22482, "unexpected internal-state minimum")
    width = (len(quotient) - 1).bit_length()
    codes = tuple(t for row in quotient[:-4] for t in row)
    payload = implementation["pack_codes"](codes, width)
    entry_payload = implementation["pack_codes"](entries, width)
    require(implementation["unpack_codes"](payload, len(codes), width) == codes,
            "transition packing changed codes")
    require(implementation["unpack_codes"](entry_payload, len(entries), width) == entries,
            "entry packing changed codes")
    require((width, len(payload), len(entry_payload)) == (15, 84308, 270),
            "wrong packed bank accounting")
    tapes = literal_controls(table, roots, quotient, entries)
    controls = rejection_controls(table, roots, quotient, entries, mapping, history)
    result = {"status": "PASS_SHARED_RESIDUE_DISPATCHER", "configurations": len(roots),
              "original_internal_states": len(table) - 4,
              "minimal_internal_states": len(quotient) - 4,
              "partition_counts": counts, "literal_tapes": tapes,
              "rejected_corruptions": controls, "code_width": width,
              "transition_bytes": len(payload), "entry_bytes": len(entry_payload),
              "shared_bank_bytes": len(payload) + len(entry_payload),
              "separate_bank_bytes": 144 * 702,
              "saved_bytes": 144 * 702 - len(payload) - len(entry_payload),
              "transition_sha256": sha256(payload).hexdigest(),
              "entries_sha256": sha256(entry_payload).hexdigest(),
              "depth_nine_witness": sharp_separation(table, history),
              "scope": "fixed ordered-coin forward behavior; no physical tariff or new kappa"}
    if args.emit_dir is not None:
        args.emit_dir.mkdir(parents=True, exist_ok=True)
        (args.emit_dir / "transitions.bin").write_bytes(payload)
        (args.emit_dir / "entries.bin").write_bytes(entry_payload)
    if args.receipt is not None:
        hashes = {p.name: sha256(p.read_bytes()).hexdigest()
                  for p in sorted(HERE.iterdir()) if p.is_file()}
        args.receipt.write_text(json.dumps({"files_sha256": hashes, "result": result},
                                           indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
