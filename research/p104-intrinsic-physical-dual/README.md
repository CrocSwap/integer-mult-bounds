# Independent column certificate for P104 intrinsic dual endpoints

[PR2586](https://github.com/CrocSwap/integer-mult-bounds/pull/2586), head
`7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`, explicitly supplies the ordinary
physical inverse-transpose in **canonical** endpoint charts and leaves the
intrinsic convention outside its theorem. This package supplies that remaining
boundary bridge: **104 source-entry and 104 target-exit monomials**, with
**zero added positive recursive children**. Every one of their **106,496 basis
columns** is checked with exact Gaussian integers, including phase.

This is a finite interface result, conditional on the middle implementation's
stated physical contract. The standard inverse-transpose identity and the
forward endpoint adapters are credited ingredients. The new artifact makes
their wrapper direction explicit, supplies literal conjugated recipes and
checks every column using a separate closed-form evaluator. It neither
recertifies PR2586's interior nor supplies a complete supplier or new kappa.

The final live refresh discovered the parallel
[intrinsic-endpoint claim in Discussion2647](https://github.com/CrocSwap/integer-mult-bounds/discussions/2647),
also an Arham Tahir donated Codex session. This package is retained as an
**independent implementation and corroborating column certificate**, with no
priority claim for the bridge. Its distinguishing evidence is a closed-form
all-column oracle that imports neither the retained interpreter nor compiler.
The parallel claim also plans a full predecessor replay; this package assumes
that middle contract explicitly. No independent human review is implied by
parallel AI-assisted implementations.

## Boundary proof

Write `Gamma_i`, `Gamma_f` for the block-diagonal canonical charts, and `B_i`,
`B_f` for the intrinsic charts. At a source port with odd physical normal `q`,
`B_i=C_q`; at a target port, `B_f=F9 C_q^-1`. The other endpoints retain their
canonical zero/full charts, including both endpoints of all 150 dirty helpers.
Use the same root/port order and physical isometry as PR1991.

The retained forward adapters are

```
A_i = Gamma_i B_i^-1       (104 source entries; identity elsewhere)
A_f = B_f Gamma_f^-1       (104 target exits; identity elsewhere).
```

For any invertible logical middle `S`, define

```
F_can = Gamma_f S Gamma_i^-1
F_int = B_f S B_i^-1 = A_f F_can A_i.
```

Inverse-transpose preserves the order of multiplication:
`(ABC)^(-T)=A^(-T)B^(-T)C^(-T)`. All endpoint adapters are unitary, so
`A^(-T)=conjugate(A)`. Consequently

```
F_int^(-T) = J_f F_can^(-T) J_i
J_i = conjugate(A_i),  J_f = conjugate(A_f).
```

Thus execute `J_i` **before** the pinned canonical dual, and `J_f` **after** it.
These wrappers are complex conjugates, with their original entry/exit roles;
using forward adapters or swapping wrapper roles does not follow this identity.
No assumption about real `S` is needed for the boundary algebra.

Equivalently, the checked identities at every port are

```
J_i conjugate(C_q) = conjugate(Gamma_<q>)
J_f conjugate(Gamma_(q-perp)) = conjugate(F9 C_q^-1).
```

Since each adapter has only `D, P, X, phase` operations, conjugation negates
its Z4 linear and global phases and leaves its binary address map, offset and
off-diagonal quadratic coefficients unchanged. The latter are 2 modulo 4.
[ADAPTERS.json](ADAPTERS.json) contains all literal resulting rank-zero recipes.

## Exact verification and cost boundary

The verifier imports no retained interpreter, compiler or predecessor executable.
It reconstructs all 120 doubled-coordinate E8 root lines, the physical isometry,
all 14,400 binary pairings and the 104-port puncture. It binds each endpoint
frame both to the retained forward witness and to PR2586's frozen word.
The word is retained byte-for-byte as data in [inputs](inputs/PR2586-WORD.json);
its exact head, Git blob and SHA256 are in [PREDECESSOR.json](PREDECESSOR.json).

For a canonical chart `Gamma_W=E F_k E^-1`, the verifier derives its columns
directly from the basis-extension matrix and quadratic phase. The Fourier
numerator at displacement `z` is
`(1+i)^(k-popcount(z)) (1-i)^popcount(z)`, with denominator `2^k`.
For target intrinsic charts it independently uses the two-term convolution
of `F9` with `C_q^-1`. It compares every sparse column, including its zero
support and complex phase, after exact denominator alignment. This covers
arbitrary address functions by linearity, rather than sampled inputs or only
unsigned Pauli actions. Full regeneration compares every recipe field.

Six semantic controls reject missing port coverage, a phase fault, a wrong
root normal, a positive-child recipe, unconjugated forward adapters and an
incorrect exit address map. Export tests also reject source/predecessor changes,
adapter/receipt drift and overwriting an existing regeneration output.

The literal 5,398-event middle is unchanged; adding one event per wrapper gives
5,606 events in this representation. Recounting its positive transport records
gives the unchanged profile

```
1632 H1 + 74 H2 + 86 H3 + 104 H4 + 48 H5 + 42 H6 + 76 H7 + 8 H8,
rank mass 3542.
```

This recount authenticates the retained inventory, **not** its native recipes,
full logical endpoint map or recursive admission. In particular the existing
416 H1 conversions remain charged. This work does not implement the separate
[endpoint-fusion investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2619).
Rank-zero monomials still have address/phase work: no tape, movement or runtime
price for them is established here. The wrapped circuit preserves the middle's
private lifetimes and dirty-helper logical contract by composition, conditional
on that contract; neither is independently replayed in this package.
The pinned forward shear corrects only two target rows; the other 102 remain
Gram/2. Changing its endpoint convention does not complete those corrections.

## Reproduce

Standard-library Python 3.12 or later, from the repository root:

```sh
python3 -I -O -B research/p104-intrinsic-physical-dual/verify.py
python3 -B research/p104-intrinsic-physical-dual/test_verify.py
python3 scripts/research_package.py --package research/p104-intrinsic-physical-dual
```

The direct check is Git-free and read-only. `--emit NEW.json` independently
derives and verifies the complete adapter payload, then writes it exclusively
to an unoccupied path. Sources are authenticated before parsing proof inputs.
The saved [RESULT.json](RESULT.json) is compared in full. The registered replay
also checks historical provenance against the base Git commit.
Local registered replay passes on CPython 3.12.14; the relocated optimized
source-export tests also pass on CPython 3.14.7. Hosted CI is separate evidence.

## Open next questions

Bind an actual caller to these intrinsic endpoints and price its physical
implementation, including monomial movement, descending edges, private returns
and restoration. The feasible first step is a complete boundary/cost ledger
for that caller and this pinned middle, before another construction round.
The blockers remain owner/routing and idle charges, rounded strict-zero erasure,
precision and all-size admission. These are structured in [TASK.json](TASK.json).
No favorable complete moment or selected-frontier change follows here.

## Provenance and credit

Base main `b4560d9e7216f72b73c5aa940ac099c05e33ccf9`, priority revision 5;
task `p104-side-correction`, refined to this finite endpoint obligation.
[Discussion2647](https://github.com/CrocSwap/integer-mult-bounds/discussions/2647)
is the shared investigation after the late overlap was found;
[the original claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2646)
points there. The task metadata records overlap coverage and its limits;
metadata searches do not establish novelty.

Credit **ywz65 / PR2586** for the canonical physical inverse-transpose and
**PR2497** for its logical clean dual, **PR2551** for the boundary distinction,
and **Nick Petalas / PR2550** for the complementary-frame idea. Retain the
P104/native lineage: Ross Richardson / PR2445, commdata2338, Hiroki Kumazaki,
Philippe Van Velzen, Chafik Boukhalfa / PR1991, Rohan Arun / PR1972,
Adam Gall / PR1940, Josie Elliston / PR1071, Ali Romman / PR1125/1862,
icekylinx / PR531 and their credited predecessors. The forward adapters and
canonical chart conventions are from the unchanged PR1991 package. No retained
executable is copied or imported. Source-specific attribution for the copied
word is preserved here and in PREDECESSOR.json.

Prepared by **Arham Tahir**, with substantial **OpenAI Codex** assistance in
derivation, implementation, verification and writing. Apache-2.0. No independent
human, proof-assistant, complete cold-replay or maintainer-admission claim.
