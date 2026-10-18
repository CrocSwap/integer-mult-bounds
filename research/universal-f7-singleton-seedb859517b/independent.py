#!/usr/bin/env python3
"""Independent cross-checks for the f(7) certificate (different methods).

Nothing here imports engine.py.  Coverage is tested with the dual predicate
(m is covered iff (P xor m) meets P) over plain Python sets; cycle realization
uses subset dynamic programming instead of depth-first search; the Lemma A
contradiction is re-derived by exhaustive enumeration of the concrete collision
multisets rather than by the closed-form bound.
"""
import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent


def dual_covered(P, m):
    S = set(P)
    return any((p ^ m) in S for p in S)


def coverage_size_dual(P):
    n = max(p.bit_length() for p in P)
    size = 1 << max(n, 1)
    return sum(1 for m in range(size) if dual_covered(P, m))


def hamiltonian_cycle_dp(P, n):
    """Subset DP: a cycle through all of P starting and ending at 0, or None."""
    P = sorted(set(P))
    if 0 not in P or len(P) != len(set(P)):
        return None
    idx = {v: i for i, v in enumerate(P)}
    size = len(P)
    adj = [[False] * size for _ in range(size)]
    for i, a in enumerate(P):
        for j, b in enumerate(P):
            diff = a ^ b
            adj[i][j] = diff and (diff & (diff - 1)) == 0
    full = (1 << size) - 1
    dp = [[False] * size for _ in range(1 << size)]
    parent = [[-1] * size for _ in range(1 << size)]
    dp[1][0] = True
    for mask in range(1 << size):
        for end in range(size):
            if not dp[mask][end]:
                continue
            for nxt in range(size):
                if (mask >> nxt) & 1 or not adj[end][nxt]:
                    continue
                dp[mask | (1 << nxt)][nxt] = True
                parent[mask | (1 << nxt)][nxt] = end
    for end in range(size):
        if dp[full][end] and adj[end][0]:
            word = []
            mask, cur = full, end
            stack = []
            while cur != 0:
                stack.append(cur)
                prev = parent[mask][cur]
                mask ^= 1 << cur
                cur = prev
            stack.append(0)
            stack.reverse()
            for a, b in zip(stack, stack[1:] + [0]):
                diff = P[a] ^ P[b]
                word.append(diff.bit_length() - 1)
            return word
    return None


def _partitions(total, max_part=None):
    """Integer partitions of total as tuples (smallest part first)."""
    if max_part is None:
        max_part = total
    if total == 0:
        yield ()
        return
    for part in range(min(max_part, total), 0, -1):
        for rest in _partitions(total - part, part):
            yield (part,) + rest


def lemma_a_by_multiset(n, s, t):
    """Re-derive feasibility by enumerating collision multisets explicitly.

    A_x and B_x are the numbers of unordered pairs of E and of O summing to x.
    Full coverage forces support(A) u support(B) = all 2^(n-1) - 1 even nonzero
    masks and sum_x A_x B_x >= ceil((s*t - 2^(n-1))/2).  The per-value excesses
    (A_x - 1) sum to C(s,2) - |support(A)|; coverage forces the total excess of
    both sides to be at most C(s,2) + C(t,2) - (2^(n-1) - 1).  We enumerate the
    excess distributions directly (partitions of the excess) and compute the
    largest attainable sum_x A_x B_x, without using the closed-form bound.
    """
    odd_masks = 1 << (n - 1)
    even_nonzero = odd_masks - 1
    A = s * (s - 1) // 2
    B = t * (t - 1) // 2
    need = (s * t - odd_masks + 1) // 2
    if s * t < odd_masks or A + B < even_nonzero:
        return False, "counting"
    cap = A + B - even_nonzero

    def shapes(total, e):
        for parts in _partitions(e):
            yield [1 + p for p in parts] + [1] * (total - e - len(parts))

    best = -1
    for e in range(0, min(A, cap) + 1):
        for b in range(0, min(B, cap - e) + 1):
            shared = A + B - e - b - even_nonzero
            if shared < 0:
                continue
            for sa in shapes(A, e):
                xs = sorted(sa, reverse=True)
                for sb in shapes(B, b):
                    ys = sorted(sb, reverse=True)
                    total = sum(a * bb for a, bb in zip(xs[:shared], ys[:shared]))
                    if total > best:
                        best = total
    return best >= need, f"best_sum_AB={best} need={need}"


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    report = {}

    # 1. dual-test replay of any witness in the certificate
    witnesses = cert["tier3_f7"].get("universal_words", [])
    report["witnesses_replayed"] = 0
    for w in witnesses:
        P = [0]
        q = 0
        for j in w:
            q ^= 1 << j
            P.append(q)
        assert q == 0, "witness word must be restored"
        P = sorted(set(P[:-1]))
        assert len(P) == 18, "length-18 witnesses walk 18 distinct prefixes"
        assert coverage_size_dual(P) == 128, "dual test disagrees on coverage"
        cyc = hamiltonian_cycle_dp(P, 7)
        assert cyc is not None and len(cyc) == 18, "DP cycle check disagrees"
        report["witnesses_replayed"] += 1

    # 2. independent re-derivation of the split identity results
    expected = {(7, 9, 8): False, (7, 8, 9): False, (7, 8, 8): False,
                (7, 9, 9): True, (5, 5, 4): False, (5, 5, 5): True}
    checked = {}
    for (n, s, t), want in expected.items():
        ok, why = lemma_a_by_multiset(n, s, t)
        assert ok == want, ((n, s, t), ok, why)
        checked[f"n{n}_{s}_{t}"] = why
    report["lemma_rows"] = checked

    # 3. dual-test agreement on the small control sets
    P = [0, 1, 3, 2, 6, 4]
    assert coverage_size_dual(P) == 8
    assert hamiltonian_cycle_dp(P, 3) is not None
    assert hamiltonian_cycle_dp([0, 1, 2, 4], 3) is None
    report["control_sets"] = "ok"

    (HERE / "INDEPENDENT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print("PASS_F7_INDEPENDENT " + json.dumps(report, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
