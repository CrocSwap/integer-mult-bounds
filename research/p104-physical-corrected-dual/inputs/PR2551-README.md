# P104 dual boundary contracts are not interchangeable

Three recent finite P104 results use two different meanings of a dual boundary.
This note makes their relationship explicit and gives an exact physical
counterexample to treating them as the same operator. For the shared unchanged
coefficient `C[2,0]=1/2`, input `Y2=delta_0` gives `X0[0]=0` in the backward-chart
dual, whereas the ordinary physical inverse-transpose gives `(-1+i)/64`.
This holds separately for the canonical and intrinsic boundary versions.

The predecessors already state their contracts correctly. This is a source-bound
navigation result and interface witness, not a defect report or another dual
construction. In particular, PR2522's removal of private allocation remains a
valid result for its exact original-core physical operator.

## Which result answers which caller?

| Exact source | Logical object and persistent inputs | Physical boundary | Private contract and finite rank mass |
| --- | --- | --- | --- |
| [PR2479](https://github.com/CrocSwap/integer-mult-bounds/pull/2479), `65e58f85d98b4a6344c6221623df1d4caa519604` | Original `G/2` core; 280 | Ordinary physical `F_core^(-T)`; inverse-transposed endpoint adapters | Eight owned zero accumulators with nonzero discard; 2368 |
| [PR2497](https://github.com/CrocSwap/integer-mult-bounds/pull/2497), `7f2cf129d42030d3eb3975b7d1b07392c6d32a1b` | Two-target correction: rows 0 and 1 are identity, other rows `G/2`; 358 | `Gamma_i S_two^(-T) Gamma_f^(-1)` in backward canonical charts; separately described intrinsic adapters | Eight private collectors restored to known zero; clean word 3126 |
| [PR2522](https://github.com/CrocSwap/integer-mult-bounds/pull/2522), `bd1f069a0a7a36d8f04fe2dbe2c286cab3b2703d` | Same original core as PR2479; 280 | Same ordinary physical `F_core^(-T)` | No private allocation/COPY/discard; existing Q excursions, 2424 = 2368 + 8 H7 |

These masses price different words and contracts; the table is not an efficiency
ranking. PR2522 removes PR2479's private-storage assumption locally, with paid
nonmonotone persistent Q paths. It does not automatically supply PR2497's
corrected endpoint operator or its full hosting bill. Conversely, PR2497's
restored private collector does not by itself establish a physical `F_two^(-T)`.

For a caller requiring the original core's physical inverse-transpose, follow
PR2522 and its remaining owner/precision obligations. For a caller requiring the
two corrected target rows in reversed canonical charts, follow PR2497. For a
corrected physical inverse-transpose, first resolve the conversion below rather
than moving a number or a restoration claim between these rows. The earlier
[PR2133 scope map](https://github.com/CrocSwap/integer-mult-bounds/pull/2133)
organizes forward side-correction premises; it predates this dual-boundary split.

## Algebra identifies the missing conversion

Let the public logical shear, including the identity on all dirty helpers, be

```
S = [ I  0  0 ]
    [ C  I  0 ]
    [ 0  0  I ].
```

Each register's physical array is its logical array multiplied by a unitary
chart. Let `Gamma_i` and `Gamma_f` be the block-diagonal initial and final
charts of the chosen forward word. Then

```
F       = Gamma_f S Gamma_i^(-1),
F^(-T)  = Gamma_f^(-T) S^(-T) Gamma_i^T.
```

PR2479 uses dual charts `Delta_V=Gamma_V^(-T)` and complete public-macro
inverse-transposes. PR2522 preserves that physical operator while changing the
macro realization. For PR2497, reverse chronological adjoints and X-register
negations give, since C is real and the sign matrix J commutes with the charts,

```
R = J F* J = Gamma_i S^(-T) Gamma_f^(-1).
```

Here `*` is conjugate transpose, while `T` is ordinary transpose. The last
expression is not generally `F^(-T)`. Its exact algebraic conversion is

```
A = Gamma_f^(-T) Gamma_i^(-1),
B = Gamma_f Gamma_i^T,
A R B = F^(-T).
```

The identity follows by cancelling adjacent `Gamma_i^(-1) Gamma_i` and
`Gamma_f^(-1) Gamma_f`. It holds for any invertible charts, with the displayed
formula for R; deriving R by adjoints also uses their unitarity. The wrappers
act on every public register, including helpers. They are not established to
be free, monomial, admissible to existing owners, or favorable in cost. Native
recipes, scalar/address work, physical precision and a complete invoice would
be required for an independent physical rewrapping result. This note supplies
that obligation, not such a result.

## An unchanged coefficient gives a physical witness

Both logical objects have `C[2,0]=G[2,0]/2=1/2`; the two-target correction only
changes rows 0 and 1. We deliberately use row 2, so the discrepancy cannot be
explained by comparing different correction rows. Set physical `Y2=delta_0`
on the 512-address space and every other public input to zero. Zero helpers
are a legitimate input for either arbitrary-dirty contract. Only the
`Y2 -> X0` off-diagonal block is needed to separate the full operators.

In the original physical labels, the pinned canonical representatives are

```
X0 initial: (386,),
Y2 final:   (257,129,64,32,17,8,5,2),
X0 final:   FULL,
Y2 initial: ZERO.
```

Write `F9` for the symmetric nine-direction child. Its inverse-transpose is
`F9^(-1)`. Thus the unit-coefficient block of the ordinary physical dual is
`F9^(-1)`, while R's canonical unit block is

```
Gamma_(386) Gamma_(257,129,64,32,17,8,5,2)^(-1).
```

The exact former column at `delta_0` has 512 nonzero entries and its address-0
entry is `(1-i)/32`. The latter has 128 nonzero entries and address-0 entry
zero. Multiplication by the shear coefficient `-1/2` gives the stated
`(-1+i)/64` versus zero.

The intrinsic version must be calculated separately. Its physical roots are
`q_X0=386`, `q_Y2=405`; the forward boundary charts are `C_386` and
`F9 C_405^(-1)`. Its R unit block is

```
C_386 C_405 F9^(-1).
```

It again has 128 supported entries and zero at address 0. The full canonical
and intrinsic columns are **different**, as recorded by their separate hashes
in RESULT.json. Equal support and one common zero do not identify the operators.

For a transparent intrinsic calculation, put `a=(1+i)/2`, `b=(1-i)/2` and
`f(x)=b^(9-wt(x)) a^wt(x)`. Then `C_q=a I+b X_q`, and the intrinsic block's
address-0 entry is

```
a^2 f(0) + ab f(386) + ab f(405) + b^2 f(386 xor 405)
= (1+i)/64 - (1+i)/64 + (1+i)/64 - (1+i)/64 = 0.
```

This calculation does not use a frame constructor or native interpreter.
By comparison `f(0)=(1-i)/32` is nonzero. The canonical witness is checked by
the pinned exact Gaussian interpreter and a separate Fraction column evaluator.

## Evidence and reproduction

Standard-library Python 3.12; read-only by default:

```sh
python3 -I -O -B research/p104-dual-boundary-contracts/verify.py
python3 -I -O -B research/p104-dual-boundary-contracts/test_verify.py
python3 scripts/research_package.py --package research/p104-dual-boundary-contracts
```

The first command authenticates all live mathematical inputs and retained proof
texts by SHA256 and Git blob before importing the native interpreter. It
reconstructs the E8 port order, verifies all 14,400 physical label pairings,
binds both literal endpoint frames and their intrinsic adapters, derives the
shared Gram coefficient, and recomputes the complete receipt. It checks both
512-entry witness columns by two arithmetic implementations and the intrinsic
four-term cancellation. For each convention, signed Pauli action plus exact
global phase verifies the two-sided wrapping identity for this complete
Clifford block. That block check is not a compiled 358-register wrapper.

Eight rejecting controls remove either wrapper, confuse the symmetric child's
inverse with the child itself, or insert a global phase, separately in each
boundary convention. The tests additionally exercise a Git-free read-only
export, missing/altered retained proof, native executable tampering before
import, and a false equality field in the saved receipt. `--out NEW.json`
writes a recomputed receipt only to an unoccupied path.

The algebra above is the full general identity; the finite column is its
non-equality witness at the pinned P104 boundary. The source READMEs are retained
as exact contract evidence. This package does not execute or independently
recertify any predecessor's full chronological word. Its operation counts are
explicitly attributed source claims, not newly replayed invoices. No full
supplier, all-size admission, new precision bound or kappa follows.

## Open next questions

Can PR2497's corrected backward-chart dual be converted to a desired physical
supplier interface at a favorable complete cost? First instantiate A and B
for all 358 public registers and produce native recipes with scalar, owner,
idle and residual charges. The current result only identifies the required
operator; monotone complementary paths, ownership, precision and all-size
admission remain separate obligations. [TASK.json](TASK.json) records the
structured handoff and bounded overlap coverage.

## Provenance and credit

Canonical base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
[SOURCES.json](SOURCES.json) records exact source bytes, Git blobs and the three
PR heads above. The native frame/interpreter evidence comes from Chafik
Boukhalfa / PR1991 and the retained PR1862 interpreter lineage; Rohan Arun /
PR1972 supplied the logical core, Adam Gall / PR1940 its schedule, Josie
Elliston / PR1071 the fixture, and Ali Romman / PR1125 the preceding geometry.
Ross Richardson / PR2445 and PR2458 supplied the corrected-word ancestry.
PR2479, PR2497 and PR2522 supply the dual constructions and their stated limits;
the ordinary transpose and change-of-chart identities are not newly claimed.
Original source notices remain unchanged. New work is Apache-2.0.

Prepared for **ywz65** with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing. No independent human, formal-kernel,
selected cold-replay or hosted-CI result is claimed.
