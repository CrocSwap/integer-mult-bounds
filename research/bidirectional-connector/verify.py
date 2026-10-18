#!/usr/bin/env python3
"""Exact free-linear replay of the paid bidirectional connector witness.

conorholds, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported. Checks also run under python -O.
"""
import argparse
from collections import Counter
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def roles(n=5, roots=2):
    return [f"x{j}" for j in range(n)] + [f"y{m}" for m in range(1, 1 << n)] + [f"z{p}" for p in range(roots)]


def ports(op, n=5, roots=2):
    require(isinstance(op, list) and op, "invalid instruction")
    kind = op[0]
    require(kind in ("A", "B", "C"), "unknown instruction")
    require(len(op) == (2 if kind == "C" else 3), "invalid instruction length")
    port = op[-1]
    require(type(port) is int and 0 <= port < roots, "invalid connector port")
    if kind == "C":
        require(roots == 2, "transfer requires two root rows")
        return None, f"z{1-port}", f"z{port}"
    index = op[1]
    require(type(index) is int and index in (range(n) if kind == "B" else range(1, 1 << n)),
            "invalid operator index")
    if kind == "B":
        return f"B{index}", f"x{index}", f"z{port}"
    return f"A{index}", f"z{port}", f"y{index}"


def interpret(word, state, n=5, roots=2):
    state = {role: set(poly) for role, poly in state.items()}
    for op in word:
        coefficient, source, target = ports(op, n, roots)
        additions = {term if coefficient is None else (coefficient,) + term
                     for term in state[source]}
        state[target].symmetric_difference_update(additions)
    return state


def initial(n=5, roots=2):
    return {role: {(role,)} for role in roles(n, roots)}


def expected(n=5, roots=2):
    state = initial(n, roots)
    for mask in range(1, 1 << n):
        state[f"y{mask}"].update((f"A{mask}", f"B{j}", f"x{j}")
                                  for j in range(n) if mask & (1 << j))
    return state


def skeleton_states(skeleton):
    state = initial()
    states = [[set(state["z0"]), set(state["z1"])]]
    for op in skeleton:
        require(op[0] in ("B", "C"), "readout in skeleton")
        state = interpret([op], state)
        states.append([set(state["z0"]), set(state["z1"])])
    require(state == initial(), "skeleton fails arbitrary-dirty restoration")
    return states


def boundary_table(states):
    result = []
    dirt = {("z0",): 1, ("z1",): 2}
    sources = {(f"B{j}", f"x{j}"): 1 << j for j in range(5)}
    for pair in states:
        require(all(poly <= dirt.keys() | sources.keys() for poly in pair), "unexpected root term")
        result.append({"dirty": [sum(dirt.get(term, 0) for term in poly) for poly in pair],
                       "source": [sum(sources.get(term, 0) for term in poly) for poly in pair]})
    return result


def paired_readouts(states):
    """Find the first chronological pair for each mask; no search certificate needed."""
    pairs = {}
    for first in range(len(states)):
        for second in range(first, len(states)):
            for p in range(2):
                for q in range(2):
                    difference = states[first][p] ^ states[second][q]
                    for mask in range(1, 32):
                        target = {(f"B{j}", f"x{j}") for j in range(5) if mask & (1 << j)}
                        if difference == target:
                            pairs.setdefault(mask, [[first, p], [second, q]])
    require(set(pairs) == set(range(1, 32)), "missing source mask or uncancelled dirt")
    return {str(m): pairs[m] for m in range(1, 32)}


def assemble(skeleton, readouts):
    require(set(readouts) == {str(m) for m in range(1, 32)}, "readout domain incomplete")
    slots = [[] for _ in range(len(skeleton) + 1)]
    for mask in range(1, 32):
        pair = readouts[str(mask)]
        require(isinstance(pair, list) and len(pair) == 2, "need two readouts per mask")
        for entry in pair:
            require(isinstance(entry, list) and len(entry) == 2, "invalid readout")
            boundary, port = entry
            require(type(boundary) is int and 0 <= boundary <= len(skeleton), "invalid boundary")
            op = ["A", mask, port]
            ports(op)
            slots[boundary].append(op)
    word = []
    for boundary, reads in enumerate(slots):
        word.extend(reads)
        if boundary < len(skeleton):
            word.append(skeleton[boundary])
    return word


def invoice(word):
    for op in word:
        ports(op)
    counts = Counter(tuple(op) for op in word)
    return {"source_calls": [[counts[("B", j, p)] for p in range(2)] for j in range(5)],
            "readout_calls": [[counts[("A", m, p)] for p in range(2)] for m in range(1, 32)],
            "transfers": [counts[("C", p)] for p in range(2)],
            "root_calls": len(word), "reserved_data_rows": 38, "dirty_root_rows": 2}


def check_endpoint(word, n=5, roots=2):
    output = interpret(word, initial(n, roots), n, roots)
    require(output == expected(n, roots), "wrong output map or arbitrary-dirty restoration")
    require(interpret(list(reversed(word)), output, n, roots) == initial(n, roots), "literal inverse failed")


def check_certificate(cert):
    require(cert["schema"] == "bidirectional-connector-v1", "unsupported certificate")
    states = skeleton_states(cert["skeleton"])
    require(cert["boundaries"] == boundary_table(states), "boundary evidence differs")
    require(cert["readouts"] == paired_readouts(states), "readout evidence differs")
    word = assemble(cert["skeleton"], cert["readouts"])
    require(cert["word"] == word, "literal program differs from boundary placements")
    check_endpoint(word)
    paid = invoice(word)
    require(paid == cert["invoice"], "unpaid instruction or row")
    require(all(sum(c) == 2 for c in paid["source_calls"] + paid["readout_calls"]),
            "changed minimum A/B incidence")
    require(paid["transfers"] == [3, 3] and paid["root_calls"] == 78, "changed six-transfer claim")
    return word


def check_predecessor():
    """Replay the credited eight-transfer construction, not its native exclusion."""
    sources = json.loads((HERE / "SOURCES.json").read_text())
    pin = sources["merged_reference"]
    content = (HERE / pin["local_path"]).read_bytes()
    require(sha256(content).hexdigest() == pin["sha256"], "predecessor SHA256 drift")
    require(sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest() == pin["git_blob"],
            "predecessor Git blob drift")
    cert = json.loads(content)
    skeleton = [op if op[0] == "B" else ["C", 0] for op in cert["skeleton"]]
    word = assemble(skeleton, cert["readouts"])
    check_endpoint(word)
    require(invoice(word)["transfers"] == [8, 0] and len(word) == 80, "changed predecessor invoice")
    return word


def controls(word, old_word):
    rejected = 0
    for program in (word, old_word):
        for index in range(len(program)):
            try:
                check_endpoint(program[:index] + program[index + 1:])
            except ValueError:
                rejected += 1
            else:
                raise ValueError("omission control accepted")
    # Two cancelling transfers preserve the endpoint, but must both remain paid.
    padded = word + [["C", 0], ["C", 0]]
    check_endpoint(padded)
    require(invoice(padded)["root_calls"] == 80 and invoice(padded)["transfers"] == [5, 3],
            "cancelling operations were underpriced")
    return rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    try:
        cert = json.loads(args.certificate.read_text())
        word = check_certificate(cert)
        old_word = check_predecessor()
        rejected = controls(word, old_word)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, str(exc) + "\n")
    print(f"PASS_BIDIRECTIONAL_CONNECTOR masks=31 AB_calls=72 transfers=6 "
          f"root_calls=78 predecessor_transfers=8 omission_controls={rejected} no_new_kappa")


if __name__ == "__main__":
    main()
