# A finite P104 inverse-transpose with explicit private accumulators

The original P104 G/2 channel has a finite **ordinary inverse-transpose** word
once each of its eight private fanouts is dualized as a complete public
operation. The resulting 4,058-event word checks all 280 independent logical
inputs, restores all 72 dirty helpers, and has the same 1,410 native transport
uses and rank mass 2,368. It implements

```
X_s -> X_s - sum_t G[t,s] Y_t / 2;
Y_t -> Y_t;
G, Q, D dirty inputs -> their original logical values.
```

This supplies a concrete finite dual under an **explicit owned zero-accumulator
contract**. The original private lifetime copied one Q value and discarded it
after fanout. The dual instead gathers several D values into zero private
storage, transports the sum, updates Q and discards the nonzero sum. Its
physical scalar implementation and all-size storage/ownership admission are
not established by this package. It does not claim the original pure-copy
contract automatically admits this accumulator lifetime.

The object is PR1972/PR1991's original 4,058-event G/2 channel, **not** PR2445's
two-target correction, PR2454/PR2458's native extension of that correction, or
any complete identity supplier. No I-G/2 correction, global owners, favorable
complete moment, new supplier or new kappa is supplied here.

## Why a macro boundary is necessary

For invertible public gates, inverse-transpose preserves chronological order:
if the full operator is `P = L_N ... L_1`, then
`P^(-T) = L_N^(-T) ... L_1^(-T)`. An ADD `dst += a src` becomes
`src -= a dst`. However, private zero allocation and discard are rectangular,
and cannot be inverse-transposed as if they were invertible gates.

The tempting atomwise rule keeps zero/discard, replaces COPY by `Q -= C`, and
dualizes every ADD chronologically. The exact source-bound negative control
fails: its X0 row contains `-2 initial_D0` and has **zero** Y0 coefficient
instead of the required `-1`; its Q0 row contains `+initial_D0`. This is an
explicit failed attempted extension, not a defect attributed to PR1991,
which only certifies the forward channel.

The repair uses the actual uninterrupted private intervals:

| Q | Original event interval, inclusive | D readers | Native rank |
| --- | --- | --- | --- |
| Q0 | 2461–2469 | D0–D4 | 7 |
| Q1 | 2470–2476 | D5–D7 | 7 |
| Q2 | 2477–2484 | D8–D11 | 7 |
| Q3 | 2485–2492 | D12–D15 | 7 |
| Q4 | 2493–2500 | D16–D19 | 7 |
| Q5 | 2501–2507 | D20–D22 | 7 |
| Q6 | 2508–2515 | D23–D26 | 7 |
| Q7 | 2516–2524 | D27–D31 | 7 |

Indices are zero-based. The generator rejects interleaved updates, repeated
readers, changed coefficients or unexpected private operations. Q and each
D have fixed frames throughout the interval; no public transport is hidden
inside a macro. The complete new literal word and source-event bindings are
in [WORD.json](WORD.json), regenerated field-for-field by [verify.py](verify.py).

## Public macro proof and private contract

Let A be the original Q cap and B the common D line. The original private
transport is `L = Gamma_B Gamma_A^(-1)`. After eliminating its owned private
register, the forward macro is exactly

```
Q unchanged;
D_j += L Q, for every listed reader j.
```

The off-diagonal block squares to zero because Q is unchanged and no D is
read back into Q. Thus its inverse-transpose is

```
D_j unchanged;
Q -= L^T (sum_j D_j).
```

In the dual chart `Delta_V = Gamma_V^(-T)`, execute:

1. Allocate owned C with value zero at frame B.
2. Add every D_j into C at B.
3. Apply `L^T` to C, taking it from Delta_B to Delta_A.
4. Subtract C from Q at A.
5. Discard the owned C at A.

The chart identity is
`L^T = Gamma_A^(-T) Gamma_B^T = Delta_A Delta_B^(-1)`.
Consequently every gather and the final subtraction use a common chart.
The full event replay checks that all D readers are still at B and Q is still
at A at their actual chronological cuts. No retiming of the public word is
assumed. The argument holds for arbitrary address arrays and arbitrary Q/D
dirt, because it is a linear operator identity.

C is a new, exclusively owned, **known-zero** scratch lifetime; it is not an
arbitrary dirty helper. Every final C row contains independent D dirt, recorded
in [RESULT.json](RESULT.json). It has not been uncomputed to zero. Allocation
and discard here are explicit finite semantics, with no inference about the
original supplier's all-size COPY/cleanup or memory invoice.

All other scalar and native public operations are invertible and are dualized
chronologically. Composing the eight valid public macro duals with these
ordinary gate duals therefore gives the complete physical public operator
P^(-T). A separate exact rational replay checks the expected all-280-column
logical boundary above; it also checks every frame and all dirty restoration.

## Native phases, ordinary transpose and the invoice

The retained Gaussian interpreter is hash-authenticated before import. The
original 740 recipes, label isometry, all 14,400 root pairings, 208 intrinsic
adapters, event bindings and forward all-input map are checked first. The
source compiler and producer are not imported.

For an ordinary public transport U, unitarity gives `U^(-T) = conjugate(U)`.
Its dual recipe conjugates the Gaussian monomials and uses
`C_q^(-1) = X_q C_q`. For the standard rank-r positive child,
`conjugate(F_r) = X_(2^r-1) F_r`; the extra X is a monomial. Thus every
transport still has one positive child of exactly its inherited rank.

The new private transport is instead the **ordinary transpose** of the old
downward operator. If its old recipe is `M_left F_r M_right`, the new one is
`M_right^T F_r M_left^T`: every translation C_q is symmetric, so `F_r^T = F_r`.
Transposing a monomial reverses its address permutation and leaves its scalar
diagonal values unconjugated. Substituting the adjoint is wrong; an exact
native control detects that substitution.

Each derived operator is compared with its literal Delta-frame operator by
signed Pauli action and an exact Gaussian state column. Equal signed Pauli
actions fix a Clifford up to scalar phase; equality on a nonzero state fixes
that phase. All 512 columns are also compared for each of the eight private
transposes, giving 4,096 complete Gaussian column checks. Intrinsic endpoint
adapters are inverse-transposed Gaussian monomials; their dual chart endpoints
follow from the checked forward adapters and unitarity.

| Finite local quantity | Forward | Dual |
| --- | ---: | ---: |
| Events | 4,058 | 4,058 |
| Scalar ADDs | 2,624 | 2,632 |
| COPYs into known-zero C | 8 | 0 |
| Owned zero allocations / nonzero discards | 8 / 8 | 8 / 8 |
| Native transport occurrences | 1,410 | 1,410 |
| Distinct derived native edges | 740 | 740 |
| Native rank mass | 2,368 | 2,368 |

The native profile remains
`1074 H1 + 58 H2 + 86 H3 + 104 H4 + 48 H5 + 24 H6 + 8 H7 + 8 H8`.
This is an exact finite operation recount, not an assertion of equal global
ownership, boundary-coverage credit, precision reserve or complete supplier
cost. In particular the private birth/death frames change from cap-to-line
copies to line-to-cap accumulators. Those different lifetimes require their
own admission before reusing any supplier bill.

## Validation

Python 3.12, standard library only:

```sh
python3 -I -B research/p104-private-macro-dual/verify.py
python3 -I -O -B research/p104-private-macro-dual/verify.py
python3 -I -O -B research/p104-private-macro-dual/test_verify.py
python3 scripts/research_package.py --package research/p104-private-macro-dual
```

The direct replay takes about 16 seconds locally on native CPython 3.12.14.
Expected marker:
`PASS_P104_PRIVATE_MACRO_DUAL inputs=280 private=8 native=1410 rank_mass=2368 controls=7 no_new_kappa`.

Seven controls cover the actual atomwise-dual failure, a wrong gather sign,
a missing reader, global phase corruption, adjoint/transpose confusion,
all eight nonzero discard witnesses, and equivalent binary frame bases.
Export tests check read-only Git-free replay, complete-word drift, and source
mutation before import. Default replay writes nothing; `--out NEW.json`
exclusively writes a verified receipt. The full word and every receipt field
are compared canonically, not only an operation-count digest.

## Open next questions

Can the changed private accumulator lifetimes be admitted to the actual
all-size storage and owner interface? First write that contract explicitly
for the recorded line births, cap deaths, known-zero requirements and nonzero
D-dependent discards, then derive its complete charge. The finite operator
identity cannot substitute for this missing admission.

Can the same macro-boundary treatment dualize a chronological corrected
P104 word? Start with its exact public/owned-private decomposition, retain
arbitrary dirt, and check the complete coefficient/frame word. A copy of this
rank profile or a collection of inverse native edges is insufficient.

Recursive precision in the dual orientation is also separate. The actual
all-cut signed sensitivity maps must be recomputed, including the new
accumulator magnitudes. No forward precision constant is transferred here.

## Sources and credit

Base: canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
[SOURCES.json](SOURCES.json) pins every executable and data input. [TASK.json](TASK.json)
records the changed scope, live overlap, claim and remaining questions. The
selected record and frozen predecessors are unchanged.

Credit Rohan Arun / PR1972 for the entire forward word, Chafik Boukhalfa /
PR1991 for the finite native realization and retained independent interpreter,
Adam Gall / PR1940 for the schedule, Josie Elliston / PR1071 for the fixture,
Ali Romman / PR1125 and retained geometry/compiler contributors. The repository's
chronological inverse-transpose convention and private-CLEAR distinction are
also recorded in the historical batch932 and batch970 circuit reviews; the
general transposition method is not newly claimed. PR2096 supplies forward
precision, not the new dual's error bounds. Ross Richardson / PR2445 and
PR2454/PR2458's two-target native work are adjacent results, not inputs here.

Prepared for **ywz65** with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing. Apache-2.0. No independent human review,
proof assistant, selected supplier cold replay or hosted CI is claimed.
