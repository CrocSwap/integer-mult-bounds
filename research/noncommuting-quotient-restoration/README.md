# Noncommuting workspace drift through a sign-character output

**Scoped recursive-interface construction and exact boundary price; no new κ.**
Six fixed children can carry a noncommuting permutation of six dirty rows
through a one-row output. A complete source-only dirty echo uses **192 ADD +
48 NEG = 240 instructions**, versus **300 ADD + 72 NEG = 372** with eager
restoration. Both source calls, both complete batch directions and every
workspace permutation are included. No clean full row is used.

The added result beyond [PR1227](https://github.com/CrocSwap/integer-mult-bounds/pull/1227)
and [PR1287](https://github.com/CrocSwap/integer-mult-bounds/pull/1287) is the
noncommuting workspace action with a **nonfaithful** output representation:
after child two the output is canonical, although workspace is not. Requiring
canonical output at that cut keeps the boundary price **6**; requiring canonical
workspace raises the exact minimum to **30**. This distinguishes the two
observer contracts on a literal, fully priced word.

The fixed-child restriction is essential. The demonstration implements the
children explicitly; a compiler permitted to remove their internal drift and
evaluate the summed reader directly can beat both wrappers. No real supplier
with the required indivisible boundary has been identified. These are exact
interface operation counts, not a multiplication runtime or exponent gain.

## Typed contract and admission

Work over a characteristic-zero field with exact arithmetic. Let `G=S3`,
`a=(01)`, `b=(12)`, and `χ(g)=sign(g)`. Workspace consists of six length-`L`
rows `W_h`, indexed by the lexicographically ordered permutations `h∈G`.
There is one length-`L` output `D`. Define

```
(P_g W)_h = W_(g^-1 h),       R W = Σ_h χ(h) W_h.
```

Changing variable `h=gk` gives `R P_g = χ(g) R`. The compiler checks this
admission identity before emitting a transported batch. For a scalar reader,
the identity for both generators determines its coefficients uniquely up to
scale: the coefficient at `gk` is `χ(g)` times the coefficient at `k`, and
the generators reach every element of `G`. Thus the admissible reader space
is exactly the one-dimensional sign-character space. The independent ternary
census finds three readers among all 729 vectors in `{-1,0,1}^6`: `0,R,-R`.
The finite census checks implementation; the generator argument proves the
characteristic-zero statement for arbitrary coefficients.

Each indivisible child has the fixed entry/exit map

```
C_g(D,W) = (D + R W, P_g W).
```

Its complete price includes the reader, its internal permutation, access,
dispatch and any private scratch restoration. Its literal inverse is available
at the same declared instruction price. Source/output/workspace ports are
distinct and excluded from child private scratch. The six children are ordered
`a,b,a,b,a,b`; the matrices `P_a,P_b` do not commute, while
`P_b P_a P_b P_a P_b P_a=I`.

The parent may apply complete `P_h` workspace permutations and output `NEG`
in the seven gaps, including entrance and exit. No source copies, partial row
operations or changes inside a child are part of this boundary alphabet.

## Transport proof and observers

Call each child and then negate `D`. Let `p_i=g_i...g_1`. Induction gives

```
W_physical = P_(p_i) W_initial,
D_physical = χ(p_i) (D_initial + i R W_initial).
```

At child entry the two physical registers represent the same sign character.
Admission makes the new reader increment have that sign; the child's odd
workspace action and the paid output negation restore alignment. At `i=6`,
`p_6=1`, so the completed batch is
`E(D,W)=(D+6RW,W)` for every arbitrary initial dirty state and every `L≥1`.

At `i=2`, `p_2=ba` is a nonidentity three-cycle in `ker χ=A3`. Hence `D`
equals the canonical eager output `D_initial+2RW_initial`, while `W` differs
from the canonical eager workspace on some inputs. An output-only observer
is safe there; a workspace observer is not. At an odd cut even the output is
negated, so a canonical-output observer requires additional paid correction.
These checkpoints compare to the eager **batch** state. They do not promise
an early final source-only answer inside the larger two-pass echo.

## Exact boundary minimum, including entrance corrections

All six readers are the same nonzero `R`. In any correct characteristic-zero
boundary word, the coefficient of arbitrary incoming `D` must be `+1`.
Each child contributes either `+R` or `-R` after final output normalization.
Their sum must be `6R`, so all six contributions must be `+R`. Consequently
the cumulative output sign `q` must equal `χ(p)` before every child. This
necessity follows from the endpoint identity; it is not an extra assumption
that correct intermediate values are always required.

After an odd child, a workspace correction `h` requires an output negation
exactly when `χ(h)=+1`. For positive scalar ADD/NEG prices `α,ν`, the literal
regular-action backend charges

```
c(1)=0;   c(transposition)=9α+3ν;   c(three-cycle)=12α.
```

A two-coordinate swap uses three signed ADDs and one NEG. A three-cycle uses
two signed swaps, six ADDs; this is PR1287's existing backend, credited there
to PR1145. Every nontrivial regular action has three swaps or two three-cycles.
These circuits are implemented literally; no primitive-level minimality is
claimed. Within this **complete group-operation alphabet**, multiple corrections
in one gap cannot beat the single correction with the same product: two odd
actions cost more than a three-cycle, and adding an even action cannot make an
odd correction cheaper. Two output negations cancel and have positive cost.

Each of the six post-child gaps therefore costs at least `ν`: an even `h`
needs output NEG, while an odd `h` already costs `9α+3ν>ν`. Entrance cost is
nonnegative. The no-workspace-correction transport attains **6ν** and restores
both registers. This proves the exact minimum for every positive `α,ν` in
the stated alphabet, with the prescribed six fixed children. It does not
optimize arbitrary reversible circuits or finite-characteristic endpoints.

For checkpoint variants, the six-state recurrence keeps the workspace state
`p`. Its entrance cost is `c(p)+ν[χ(p)=-1]`. After child `g_i`, correction `h`
sets `s=h g_i p` with cost `c(h)+ν[χ(h)=+1]`. Output checkpoints require
`χ(s)=+1`; workspace checkpoints and final exit require `s=1`. Minimize over
the six choices of `h`. This gives an exact shortest-path recurrence by the
normalization and admission arguments above.

At unit prices the exact boundary minima are:

| Required checkpoint | Minimum |
|---|---:|
| Final exit only | 6 |
| Canonical output after child 2 | 6 |
| Canonical output after child 1 | 28 |
| Canonical workspace after child 2 | 30 |
| Canonical output after every child | 72 |

The separately represented six-coordinate oracle enumerates **46,656**
endpoint-correct normalized schedules, including entrance operations: choose
`h_0,...,h_5`, and final restoration uniquely determines `h_6`. It agrees
with the planner for all five checkpoint contracts at ADD/NEG prices
`(1,1),(3,1),(1,3)`. Every retained optimal plan is emitted and its required
prefix maps and full dirty endpoint are checked on all basis columns.

## Complete source-only echo and paid invoice

Let `F` be any complete exact additive source call `W += F X`, preserving `X`
and private scratch, with literal inverse `W -= F X`. It need not commute with
the group action. Execute, chronologically,

```
E^-1(D,W);  W += F X;  E(D,W);  W -= F X.
```

The result is `D += 6 R F X`, with `X,W` and all private scratch restored.
The inverse reverses every actual instruction and ADD sign. This proof is
valid for every `L` and every compatible exact linear `F`; finite banded
noncommuting fixtures additionally check that no commutation was assumed.

For the concrete `L=1,F=I` fixture, each child costs `15 ADD + 3 NEG`.
One eager batch costs `144 ADD + 36 NEG`, including its six complete workspace
restorations. A transported batch costs `90 ADD + 24 NEG`, including its six
output corrections. Two source calls cost twelve ADDs in total.

| Complete root | ADD | NEG | Total | Data accesses | Descriptor records | Word moves |
|---|---:|---:|---:|---:|---:|---:|
| Eager | 300 | 72 | 372 | 1,044 | 372 | 8,052 |
| Transported | 192 | 48 | 240 | 672 | 240 | 5,388 |

No child or inverse is omitted. The arithmetic saving is `108α+24ν`.
Data storage is thirteen length-`L` rows: six source, six borrowed arbitrary
dirty workspace and one output. There is no extra clean full row. The concrete
word-address backend places these coordinates consecutively, reads source then
target and writes target for ADD, reads/writes target for NEG, and returns to
origin after **every scalar instruction**. Addresses begin at one. Thus ADD
costs three data accesses and `2 max(address_source,address_target)` word moves;
NEG costs two accesses and twice its target address. `oracle.access_invoice`
reconstructs movement from the literal visit sequence independently of the
primary formula. These are word moves, not bit-tape transitions or timings.

At the abstract complete-call boundary, include admission/layout `I`, coefficient
preparation `P`, and program/dispatch `D_prog`. The transported root bill is

```
I + P + D_prog + 2 c_F + 2 Σ_i c_(C_i) + 12 c_output_NEG.
```

The eager bill replaces the last term by `2 Σ_i c_(P_gi^-1)`; evaluate actual
descriptor/access charges for each word. The concrete table expands child and
source work and records descriptor reads rather than silently treating them
as free. Constructing/storing the explicit instruction stream costs time/space
linear in its length; a dense supplied `F` additionally needs its whole matrix
admission/preparation. Nothing in the scalar table establishes a faster physical
supplier, finite-price moment, contracting multitype recurrence or analytic κ.

For entry magnitudes at most `U`, exact signed prefix row norms give sufficient
working magnitude `peak*U`. In the primary words both peaks are **37**, so
`U=7` permits ten signed bits. This is a conditional integer-width bound,
not a claim that arbitrary full-width dirty integers fit at the same width.
The implementation uses exact Python integers and rational probes. Rounded
leaves, bit-level arithmetic/control, fixed-tape realization and numerical
recovery remain separate obligations.

## Reproduce and evidence boundary

Standard library only. From the repository root:

```sh
python3.12 scripts/research_package.py --package research/noncommuting-quotient-restoration
```

Or run the self-contained checks directly:

```sh
python3 -I -O -B research/noncommuting-quotient-restoration/verify.py
python3 -I -O -B research/noncommuting-quotient-restoration/test_package.py
```

Expected: `PASS_NONCOMMUTING_QUOTIENT_RESTORATION instructions=372->240 ...`
and nine passing test groups. [CERTIFICATE.json](CERTIFICATE.json) is compared
field-for-field with exact regeneration and includes both complete primary
words, all checkpoint plans and invoices. `--write-certificate` explicitly
regenerates it. Tests cover all dirty-state basis columns in twelve root
cases (`L=1,2,3`, identity/banded source, eager/transported), literal inverses,
rational probes, the two-child pilot, typed prefixes and twelve failure controls.
Package controls reject changed source bytes, false source commit and an unpaid
NEG in the on-disk receipt, and replay a relocated package from an unrelated
working directory. See [VALIDATION.md](VALIDATION.md) for observed environments.

The general identities and boundary reduction above are written proofs.
Finite checks are exact implementation evidence, not a proof-assistant theorem
or full multiplication verification. Selected supplier cold replay, physical
admission, common-label/mutable-source realization, compiler/all-size,
precision/tape and analytic transfer are unrun. The selected record remains
`836330098538459/500000000000000000` at the pinned base.

## Open next questions

The structured questions in [TASK.json](TASK.json) ask for a **real** indivisible
equivariant supplier boundary and its required observer cuts. First trace one
candidate's exact reader/drift map and test `R P_g=Q_g R`, then price its complete
corrections and scratch ownership. Stop if internal drift can simply be deleted:
the toy implementation does not justify an opaque boundary for a real compiler.
No candidate supplier or favorable complete multiplication invoice is established.

## Credit and coordination

Research base: fresh main `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
Task seed, original persistent-boundary card, refinement, exact predecessor
heads, limits and next questions are in [TASK.json](TASK.json). Historical
main/catalogue provenance is pinned in [SOURCES.json](SOURCES.json); immutable
PR1287/PR1227 notes retain their complete attribution under `references/`,
with byte/SHA256/Git-blob pins in [PREDECESSORS.json](PREDECESSORS.json).
No predecessor executable is imported or rerun. Entry overlap covers all 847
open PRs including drafts and 98 Discussion body/comment/reply records; final
coverage is recorded in VALIDATION.md. Coordination: [Discussion #1381](https://github.com/CrocSwap/integer-mult-bounds/discussions/1381).

Credit Ross Richardson's PR1287 for equivariant cyclic output frames, Sagar
Thakrar's PR1227 for paid output-sign transport, PR1145 for the existing
six-ADD three-cycle, and mightyOil's PR1203, Adam Gall's PR1205, Sagar Thakrar's
PR1199, Aaron Wang/Navinor's PR1155 and PR889 for the retained restoration/echo
lineage. Their mechanisms and negative examples are not claimed as new here.
The new object is the S3 regular action/sign-character kernel and its precise
checkpoint costs. The final refresh also found Hanson Sun (@bbMisk)'s concurrent
[PR1488](https://github.com/CrocSwap/integer-mult-bounds/pull/1488), head
`13d780ea51248ddd51901cd546b9f59adc76eb43`. It gives faithful two-dimensional
S3 output transport and explicitly distinguishes Discussion #1381's sign
quotient. Noncommuting output transport is shared concurrent work; the
nontrivial output-kernel checkpoint and the fixed six-child sign-reader price
are this package's scope. Its reported 524-to-404 fixture is not replayed here.
Prepared for **@Arham-Tahir64** with substantial
**OpenAI Codex assistance** in algebra, code, verification and writing. New
material is Apache-2.0. No independent human review is claimed.
