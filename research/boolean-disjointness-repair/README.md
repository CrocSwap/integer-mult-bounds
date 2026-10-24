# Exact rank of an additive Boolean-disjointness repair

For every integer `h>=2`, let `A_h` be the F2 disjointness matrix on the
nonempty proper subsets of `[h]`. This package proves

```text
rank_F2(I+A_h) = (2^(h+1) - 2*(-1)^h - 3)/3.
```

Thus any F2 additive repair of `A_h` to the identity by `ell` scalar rank-one
terms requires at least this many terms. Under the assumed ledger
`D=2v-3ell`, `v=2^h-2`, its deficit is at most 1 for even h and -3 for odd h.
This rules out a cheap copied-scalar repair of the specific missing endpoint
in [PR #172](https://github.com/CrocSwap/integer-mult-bounds/pull/172).
It does not rule out a new source basis, port design, endpoint, nonadditive
repair, or compiler. There is no construction or complete kappa improvement.

`PROOF.txt` gives the all-dimensional proof. It computes the spectrum of the
full tensor disjointness matrix, then proves the exact rank change when the
empty and full sets are removed. `HISTORICAL-REVIEW.txt` gives a separate
written proof of that deletion step. Its review was by an AI agent, not a
human reviewer or a proof assistant.

## Reproduce

From the repository root, with Python 3.10 or later and its standard library:

```sh
python3 -B research/boolean-disjointness-repair/verify.py
```

Expected final line:

```text
PASS_BOOLEAN_DISJOINTNESS_REPAIR h=2..11 independent_kernels=2..4 no_new_kappa
```

The first check uses exact binary elimination for h=2 through 11. The
separate check enumerates every kernel input for h=2,3,4 by Gray code, with
no elimination. It also checks kernel parity, the required preimages, and
the identity `B^3+B^2+B=J`. These finite checks support the written proof
for all h; they do not replace it. The wrapper checks source hashes and
compares complete mathematical receipts in a temporary directory. No
selected supplier replay, complete repository build, or Lean check is claimed.

## Credit and scope

Publication base: `cef4b52f2a59009865bf8eabde1be3f159063703`.
The consumed semantic interface is PR172 at
`427b23bc79489e7b2b7548bfd434dd9670fd5c47`. Its
[retained package](https://github.com/mikey1201/integer-mult-bounds/tree/427b23bc79489e7b2b7548bfd434dd9670fd5c47/research/zeta-family)
supplies the disjointness endpoint and ledger. The pinned [NOTICE](https://github.com/mikey1201/integer-mult-bounds/blob/427b23bc79489e7b2b7548bfd434dd9670fd5c47/research/zeta-family/NOTICE)
credits icekylinx's [PR #144](https://github.com/CrocSwap/integer-mult-bounds/pull/144)
lineage for the compiler, orthogonality contract, and bookkeeping;
its own construction and checks used Cline assistance. This package does
not claim its graph, compiler, or projected exponent as new work.

Ali Romman directed the rank proof and audit with substantial OpenAI Codex
assistance, including a separate AI proof review and kernel enumeration.
New work is Apache-2.0. `SOURCES.json` and `ORIGINS.json` record source pins
and original local hashes. The physical interpretation assumes F2 scalar corrections and the stated
additive rank-one ledger; a product of general operators is not such a sum.

## Open next questions

Can a different endpoint or a nonadditive physical repair avoid the rank-one
ledger? First write its exact all-input identity and charge every added
operation. The present rank formula alone supplies neither a construction
nor a lower bound for that changed model.
