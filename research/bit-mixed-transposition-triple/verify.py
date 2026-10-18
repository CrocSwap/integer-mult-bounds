#!/usr/bin/env python3
"""Exact radius-four search in M_3(F2[GL_2(F2)]), standard library only."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
R = 3
PERMS = tuple(itertools.permutations(range(3)))
INDEX = {p: i for i, p in enumerate(PERMS)}
MUL = tuple(tuple(INDEX[tuple(p[q[i]] for i in range(3))]
                  for q in PERMS) for p in PERMS)
E = INDEX[(0, 1, 2)]
A = INDEX[(0, 2, 1)]       # [[1,1],[0,1]] on nonzero vectors
B = INDEX[(2, 1, 0)]       # [[1,0],[1,1]]
S = INDEX[(1, 0, 2)]       # aba = bab, the coordinate swap
TARGET_LABELS = (A, B, S)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def translate(mask, group_element):
    """Right multiply a formal F2[G] coefficient by one group element."""
    out = 0
    for g in range(6):
        if mask >> g & 1:
            out |= 1 << MUL[g][group_element]
    return out


def identity():
    return tuple((1 << E) if i == j else 0
                 for i in range(R) for j in range(R))


def projectors():
    """All distinct rank-one idempotents uv^T over F2^3."""
    return tuple((u, v) for u in range(1, 1 << R)
                 for v in range(1, 1 << R)
                 if (u & v).bit_count() & 1)


def generators():
    return tuple((u, v, g) for u, v in projectors() for g in (A, B))


def append(state, gate):
    """Right multiply by I + ([g]+1) uv^T in the formal group algebra."""
    u, v, g = gate
    out = list(state)
    for i in range(R):
        row_sum = 0
        for k in range(R):
            if u >> k & 1:
                row_sum ^= state[i * R + k]
        correction = row_sum ^ translate(row_sum, g)
        for j in range(R):
            if v >> j & 1:
                out[i * R + j] ^= correction
    return tuple(out)


def word_state(word, gates):
    state = identity()
    for index in word:
        state = append(state, gates[index])
    return state


def target(labels=TARGET_LABELS):
    return tuple((1 << labels[i]) if i == j else 0
                 for i in range(R) for j in range(R))


def matches_target(state, labels=TARGET_LABELS):
    return state == target(labels)


def right_diagonal(state, labels):
    """Return state * diag([labels[0]], ..., [labels[R-1]])."""
    return tuple(translate(state[i * R + j], labels[j])
                 for i in range(R) for j in range(R))


def ball2(gates):
    """Complete ball through radius two, with one exact witness per state."""
    root = identity()
    words = {root: ()}
    layers = [[root]]
    for _depth in (1, 2):
        layer = []
        for state in layers[-1]:
            prefix = words[state]
            for k, gate in enumerate(gates):
                nxt = append(state, gate)
                if nxt not in words:
                    words[nxt] = prefix + (k,)
                    layer.append(nxt)
        layers.append(layer)
    return words, layers


def encode_state(state):
    """Canonical nine-entry, six-bit little-endian state encoding."""
    value = sum(entry << (6 * i) for i, entry in enumerate(state))
    return value.to_bytes(7, "little")


def state_digest(states):
    digest = hashlib.sha256()
    for state in sorted(states):
        digest.update(encode_state(state))
    return digest.hexdigest()


def direct_word(gates):
    wanted = ((1, 1, A), (2, 2, B),
              (4, 4, A), (4, 4, B), (4, 4, A))
    lookup = {gate: i for i, gate in enumerate(gates)}
    return tuple(lookup[gate] for gate in wanted)


def meet_in_middle(words, gates):
    """Find T=UV with U,V in the exact radius-two ball."""
    wanted = target()
    hits = []
    for state, left in words.items():
        # Every paid generator is an involution, so reverse(left) is U^-1.
        inverse = word_state(tuple(reversed(left)), gates)
        needed = right_diagonal(inverse, TARGET_LABELS)
        right = words.get(needed)
        if right is not None:
            candidate = left + right
            if len(candidate) <= 4:
                need(matches_target(word_state(candidate, gates)),
                     "meet-in-the-middle hit did not replay formally")
                hits.append(candidate)
    return hits


def controls(gates, dword, wanted):
    direct = word_state(dword, gates)
    need(matches_target(direct), "five-call direct word fails formal endpoint")

    omitted = 0
    for i in range(len(dword)):
        need(word_state(dword[:i] + dword[i + 1:], gates) != wanted,
             "omitted-call control reached the endpoint")
        omitted += 1

    wrong_label = list(dword)
    # Change the final a in aba to b, so the third target is not the swap.
    wrong_label[-1] = next(k for k, gate in enumerate(gates)
                           if gate == (4, 4, B))
    need(word_state(tuple(wrong_label), gates) != wanted,
         "wrong-address-label control reached the endpoint")

    wrong_target = target((A, B, MUL[A][B]))
    need(not matches_target(wrong_target),
         "wrong-target fixture passed the endpoint predicate")

    dirty_leak = list(wanted)
    dirty_leak[1] = 1 << E
    need(not matches_target(tuple(dirty_leak)),
         "off-diagonal dirty-leak fixture passed the endpoint predicate")

    # Every enumerated scalar factor has N^2=N and rank(N)=1.
    checked = 0
    for u, v in projectors():
        need((u & v).bit_count() & 1, "non-idempotent scalar gate admitted")
        checked += 1
    need(checked == 28, "rank-one idempotent inventory changed")
    inverse_checks = 0
    root = identity()
    for gate in gates:
        need(append(append(root, gate), gate) == root,
             "paid generator is not an involution")
        inverse_checks += 1
    return {
        "direct_formal_endpoint": True,
        "omitted_call_controls": omitted,
        "wrong_address_label_control": True,
        "wrong_target_control": True,
        "off_diagonal_dirty_leak_control": True,
        "rank_one_idempotents_checked": checked,
        "paid_generator_involutions_checked": inverse_checks,
    }


def calculate():
    gates = generators()
    words, layers = ball2(gates)
    wanted = target()
    dword = direct_word(gates)
    need(matches_target(word_state(dword, gates)),
         "five-call direct control fails formal target")
    hits = meet_in_middle(words, gates)
    need(not hits, "a four-call or shorter formal word was found")
    return {
        "status": "PASS_BIT_MIXED_TRANSPOSITION_TRIPLE",
        "model": "M_3(F2[GL_2(F2)]), paid labels a,b only",
        "target_labels": ["a", "b", "s=aba"],
        "registers": R,
        "all_register_inputs_dirty": True,
        "scalar_rank_one_idempotents": len(projectors()),
        "paid_generators": len(gates),
        "radius_layers": [len(layer) for layer in layers],
        "radius_two_ball": len(words),
        "radius_two_sha256": state_digest(words),
        "left_inverse_target_hits_through_four": len(hits),
        "minimum_paid_calls": 5,
        "direct_five_call_word": [list(gates[i]) for i in dword],
        "controls": controls(gates, dword, wanted),
        "scope": "exactly three registers; free scalar GL3(F2) mixing absorbed by augmentation",
        "no_kappa_claim": True,
    }


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true",
                        help="print the freshly calculated receipt")
    args = parser.parse_args()
    actual = calculate()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    expected = json.loads((PACKAGE / "EXPECTED.json").read_text())
    need(canonical(actual) == canonical(expected),
         "fresh exact receipt differs from EXPECTED.json")
    print("PASS_BIT_MIXED_TRANSPOSITION_TRIPLE minimum=5 ball=1807 hits=0 omission_controls=5 negative_controls=3 involutions=56 no_new_kappa")


if __name__ == "__main__":
    main()
