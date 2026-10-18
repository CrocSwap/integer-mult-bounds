# An all-length floor for the reverse-positive bound map

## Statement and objective

Let a chronological word consist of `r[d] += r[s]`, with distinct indices, on exactly six ordered registers. All arithmetic in the forward lift is over the nonnegative integers. There are no additional registers, permutations, COPY/CLEAR gates or changes to the integer target. The target from Chris Barber's PR1058 is

```text
M = [1 0 1 1 1 1]
    [1 1 1 2 1 1]
    [1 1 3 3 2 3]
    [0 0 1 1 1 1]
    [1 1 2 3 3 3]
    [1 1 1 2 1 2].
```

For any such word realizing M, let Q be the nonnegative integer matrix obtained by running its operations in reverse order, retaining positive ADD signs. This is the reverse-positive bound map used to majorize inverse cleanup magnitudes. Its infinity norm is `max_i sum_j Q[i,j]`. For a common incoming bound b on the six coordinates, the maximum outgoing positive bound is `b * ||Q||_inf`; the unit input of six ones attains that value. The signed integer inverse and Q are different matrices.

**Theorem.** Over all finite words in this class realizing M, the minimum infinity norm of Q is exactly **9**. There is no length restriction in the lower bound. The 11-ADD word pinned from PR1266 attains it.

## Three necessary invariants for every length

The following argument applies to n ordered registers. For a chronological word of length L, write

`G_k = I + e_(d_k) e_(s_k)^T`, with `d_k != s_k`.

Thus `M = G_L ... G_1`, while the reverse-positive map is `Q = G_1 ... G_L`. Since `(e_d e_s^T)^2 = 0`, the signed inverse of each gate is `G_k^-1 = I - e_d e_s^T`. Therefore

`R := M^-1 = G_1^-1 ... G_L^-1`.

1. **Absolute inverse.** Entrywise, `|AB| <= |A| |B|` by the triangle inequality. Also `|G_k^-1| = G_k`, because the off-diagonal gate entry does not overlap the identity. Induction in the displayed order gives `|R| <= Q` entrywise.
2. **Positive diagonal.** Each G is identity plus a nonnegative matrix. Expanding their ordered product includes the identity term, and every remaining term is nonnegative. Hence `Q >= I` entrywise, in particular `Q[i,i] >= 1`.
3. **Inverse parity.** Modulo two, `G_k^-1 = G_k`. Consequently `R = Q (mod 2)` entrywise, with the same product order. If `R[i,i] = 0`, the positive integer `Q[i,i]` is even, so `Q[i,i] >= 2`.

These invariants hold for arbitrary L, including repeated and noncommuting gates. They require no path enumeration, cutoff, or gate-minimum theorem. A convenient universal lower-bound matrix is

```text
B[i,j] = |R[i,j]|                    if i != j or R[i,i] != 0,
B[i,i] = 2                          if R[i,i] == 0.
```

Then `Q >= B` entrywise for every allowed factorization. This is a necessary matrix floor; it need not itself be realizable as a reverse-positive gate product.

## Instantiate the lower bound

Exact inversion of the pinned target gives

```text
R = [ 1  0  0 -1  0  0]
    [-1  0  1 -3  1 -1]
    [ 0  0  1 -1  0 -1]
    [ 0  1 -1  3 -1  1]
    [ 0  0  0 -1  1 -1]
    [ 0 -1  0  0  0  1].
```

The decisive coordinate is register 1, using zero-based indices. Its inverse row has absolute row sum 7, but its diagonal is zero. Positivity and parity force the corresponding diagonal of Q to be at least 2. The other entries already have lower bounds `1, 1, 3, 1, 1`, so

`sum_j Q[1,j] >= 1 + 2 + 1 + 3 + 1 + 1 = 9`.

The full lower-bound row sums are `[2, 9, 3, 7, 3, 2]`. Hence every allowed word has `||Q||_inf >= 9`. In particular, amplification 7 or 8 is excluded even if longer words are admitted.

## Attainment

The forward witness from PR1266 is

```text
[(1,3), (3,4), (2,5), (3,2), (0,3), (1,0),
 (5,1), (4,5), (4,3), (2,3), (2,1)].
```

Each pair means `register[dst] += register[src]`. Exact replay gives M. Its reverse-positive matrix is

```text
Q = [1 0 0 1 0 0]
    [1 2 1 3 1 1]
    [0 2 1 1 0 1]
    [0 1 1 3 1 1]
    [0 0 0 1 1 1]
    [0 1 0 0 0 1].
```

Its row sums are `[2, 9, 5, 7, 3, 2]`, so `||Q||_inf = 9`. Combining this witness with the universal lower bound proves the stated minimum. The witness has eleven forward ADDs and eleven literal reverse bit-cleanup ADDs on the same six existing registers at the source quad frame 306. The proof introduces no new access, helper, frame, copy, restoration or recursive child. It establishes an optimum of this local positive bound objective; whole-word native pricing is a separate integration obligation.

## Why the scope matters

A free permutation does not preserve the positive-diagonal invariant. On two registers, the swap matrix P has `P^-1 = P` and reverse-positive norm 1, but zero diagonal entries. The formula above would give diagonal floors 2 and norm 3. This is a concrete counterexample to extending the theorem to an alphabet with free SWAP gates. The checker includes it as a scope control.

The result also fixes the exact integer lift. A different lift of the same bit map can have a different signed inverse. Extra workspace, alternative primitive gates, and nonuniform incoming coordinate budgets require their own analysis. The target is a historical R420 quad; no selected supplier, hosted invoice, precision admission or new multiplication exponent follows from this local theorem.

## Verification versus proof

The all-length implication is the algebraic argument above. `verify.py` checks its numerical instance by two exact engines: elementary matrix multiplication with rational inversion, and direct numerical basis-column ADD/SUB replay. It checks all 64 local Boolean inputs and literal reverse cleanup, the attaining word, the critical row, the full lower-bound matrix, and the committed receipt. Tests exercise shorter independent fixtures, malformed words, archive/receipt corruption and relocated optimized replay. Finite tests support implementation correctness; they are not a formalization of the universal proof or of integer multiplication.

## Predecessor credit

Chris Barber (@cbarber1), PR1058 at `d148d200f2d64c90504fa3a9608e455aaa4c0c21`, supplies the fixed target, its 11-ADD gate-minimum construction and the original complete DAG. Cinna Davis (@1337isnot1337), PR1266 at `8edfb5d97aea03d26316964f35359d1864731dbe`, supplies the norm-9 witness and shortest-word cleanup envelope. This note closes the all-length question left explicitly open there; it claims no new witness or search technique. The underlying R420 word, helper architecture and native interface are by eumemic in PR543, with the further lineage retained in `inputs/PR1058-NOTICE.md`.

New proof and package: Cinna Davis with substantial OpenAI Codex assistance. Both verifier engines belong to this AI-assisted contribution; no independent human review or proof-assistant formalization is implied. Apache-2.0.
