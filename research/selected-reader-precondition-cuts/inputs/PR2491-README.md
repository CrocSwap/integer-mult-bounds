# The selected dirty centre reader has no unitary paired-cycle intertwiner

**One source-bound missing-interface obstruction; no new kappa or supplier
admission.** At the selected `gauge44` cut after zero-frame preconditioning and
before entry adapters, the full reader of eight centre totals cannot satisfy
`A_native P = Q_native A_native` when P is unitary and Q_native permutes the
eight output blocks as two four-cycles, even allowing a different unitary
payload map on each output edge. This includes both physical row permutations
and frame-conjugated output permutations. Every one of the 704 input fields is
arbitrary; the 480 helper fields cannot be discarded.

The exact diagonal Gram blocks are the following scalar multiples of identity:

```
(150, 130, 146, 134, 122, 126, 142, 146).
```

A unitary input action preserves the Gram matrix, so output blocks in the same
cycle would need equal entries. No value occurs four times. The proof therefore
excludes all 1,260 relabellings of paired four-cycles and arbitrary unitary input
mixing, not just signed input permutations.

The useful boundary is exposed by two controls. The 112-column **data-only**
reader has Gram `56 I` and an explicit signed order-four intertwiner; ignoring
helpers would report a misleading success. Conversely, the full reader has an
explicit **nonunitary** order-four intertwiner `P_t=I+J(Q^t-I)A`, with `AJ=I`.
It sends unit vector `e_224` to a vector of squared norm `8/7`. Thus paid
nonorthogonal implementations remain open.

## Relation to the missing interface

[PR1391's retained contract](../z4-persistent-pair-seed57/inputs/PR1391-README.md)
and [PR1410](../z4-persistent-pair-seed57/README.md) use an order-four action
whose output octet is two four-cycles. Their abstract selector children satisfy
the intertwining equality. [PR2464](https://github.com/CrocSwap/integer-mult-bounds/pull/2464),
pinned at `f364b97ff4700147fc06e622b79952b9fe6c4fa8`, explicitly leaves a named
host child exposing that equality open. Its exact README is retained in
[inputs/PR2464-README.md](inputs/PR2464-README.md), with source blob and SHA256
in [PREDECESSOR.json](PREDECESSOR.json).

This result reconstructs one actual selected reader and excludes its direct
unitary embedding at a named cut. It does not restate a generic absence of a
host, invalidate the abstract echo, or presume PR2464 had proved the missing
embedding. It does not cover arbitrary subquotients, paid changes of basis,
other cuts, output scalings, alternative totals or new contracts.

## Exact certificate and native interpretation

[PROOF.md](PROOF.md) gives the typed prefix induction for **every** live field.
The source segment is the half-open event range `[7401,12550)` of the pinned
forward program: 704 entry adapters, 3,451 scalar gates and 992 frame climbs.
All scalar operands share their current frame; the exact retained native
transition identities give `A_native=T_out (A tensor I) U_in`, with both frame
factors unitary. Hence its diagonal Gram blocks are the scalar row norms times
identity. No claim that Clifford wrappers fix constant payloads is used.

[verify.py](verify.py) independently reconstructs the 8-by-704 scalar reader
both forward and by reverse covector pullback, checks the typed segment and all
6,088 serialized monomials for unitarity, enumerates the paired cycles, builds
the data-only signed action, and checks the explicit nonunitary escape. All
arithmetic and acceptance are exact, with no optimization-sensitive asserts.
[RESULT.json](RESULT.json) contains the complete reader, Gram matrix, each
rejection witness, and the positive control's signed permutation. Seven test
groups exercise byte drift, bad/missing entry wrappers, wrong scalar/climb
frames, singular monomials, dropped signs, helper omission and the escape.

The native interpretation inherits the source's exact Clifford identities; it
does not rerun their complete independent compiler audit. The pre-entry prefix
is invertible but may be nonunitary. An action unitary **before** that prefix
can become nonunitary at our cut and is outside the excluded class. The result
does not change the centre charge, supply a new invoice, prove all-size
admission, or alter the selected record.

## Reproduce

From the repository root, with full Git history for source provenance:

```sh
python3 scripts/research_package.py --package research/selected-dirty-reader-z4 --check-only
python3.12 scripts/research_package.py --package research/selected-dirty-reader-z4
python3.12 -I -B -O research/selected-dirty-reader-z4/verify.py
python3.12 -I -B -O research/selected-dirty-reader-z4/test_verify.py
```

The registered replay uses only the standard library. Local replay was tested
with CPython 3.12.7 and 3.14.5, including optimized execution. The card's ceiling
and lever checks pass: sharing the centre by two has an ideal planning ceiling
1.90 times the selected local ceiling. That favorable relaxation motivated the
interface audit; it is not a claimed realized improvement. No selected cold
replay, full Lean build, hosted CI or independent human review is claimed.

## Open next questions

- Can the explicit nonunitary `P_t` be implemented with legal source restoration
  and a favorable complete native invoice? Start by lowering the rank-eight
  update `J(Q-I)A` at this cut, pricing the reads, intermediate storage, inverse,
  precision and owner transport. An algebraic formula supplies none of those.
- Does a different cut or different set of copied totals admit the paired-cycle
  interface? Start with its **full dirty-input** native reader and exact Gram
  blocks before optimizing a schedule. This obstruction does not transfer
  through arbitrary nonunitary preconditioning or new output normalization.

## Credit

New proof, checker and packaging by **ywz65**, with substantial **OpenAI Codex**
assistance; Apache-2.0. Selected source lineage: Rohan Arun's PR1094 on Jeremy
Kothe's retained word and its contributors. The local emitter and residual
wrappers retain DreamingOfClouds' Claude-assisted extensions of icekylinx's
Codex-assisted code and the chafreaky wrapper construction. The typed echo is
by Cinna Davis with OpenAI Codex assistance, extending Ross Richardson and
Sagar Thakrar. The PR2464 handoff is by Aaron Wang with opencode assistance.
Frozen sources and the selected frontier are unchanged.
