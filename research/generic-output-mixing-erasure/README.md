# Generic output mixing can be erased

**Scoped recursive-interface theorem; no new kappa.** Reversible scalar mixing
among output rows and any finite number of dirty output-only helpers cannot
reduce any fixed additive, port-independent map-call tariff for the generic
one-connector batch. Every valid mixed word has an ordinary word with the same
B-call timeline and no more calls of any individual reader A_i.

Consequently the five-source, all-31-mask instance still needs exactly **74
complete A/B calls**, even granting mixing free. Its previously established
heterogeneous fixture optimum remains **182**. These numbers are inherited
corollaries; the new contribution is the all-parameter erasure theorem.

This adds output-bank mixing to the fixed alphabet of Ross Richardson's
[PR943/934](../universal-connector-boundary/README.md). Adam Gall's
[PR1915](../connector-frame-rigidity/README.md) and Arham Garg's
[73-map exclusion](../connector-frame-73-exclusion/README.md) instead change
the connector's coordinates and explicitly exclude output mixing. We do not
claim the combined connector-frame/output-mixing alphabet is covered.

## Contract and all-parameter proof

Let m,n,R be nonnegative integers, R >= n, and L >= 1. There are distinct,
arbitrarily dirty L-bit source rows x_j, one connector z, and an R-row bank Y.
The first n bank rows are outputs; the rest are helpers. Fix an n-by-m binary
matrix M. All A_i and B_j range independently over exact F2-linear endomorphisms
of F2^L, including zero, singular and noncommuting maps. Independence permits
separate assignments; it does not mean the matrices must be pairwise distinct.

The completed endpoint is

```
x_j' = x_j; z' = z;
y_i' = y_i + sum_j M_ij A_i B_j x_j       (i < n);
y_r' = y_r                               (r >= n).
```

The operations are complete calls B_j: z += B_j x_j; reader calls
A_i@p: y_p += A_i z; and paid scalar bank transformations Y <- F Y for
F in GL_R(F2). The theorem grants arbitrary physical reader ports p as a
favorable relaxation, so it also excludes savings when each A_i is restricted
to its original port i. The mixed fixture below uses the more permissive ports.
The bank transformations act only on the row index, never on sources, z, or
coordinates inside an L-bit row.

The word, labels, ports and F matrices are fixed independently of all map
entries and data. They may depend on M,m,n,R,L. Every child preserves its
non-target rows and restores private scratch and promised heads. Root rows
and all bank helpers are reserved against child scratch. Outputs are observed
only at completed batch exit. There is no clean full row, alias, overwrite,
source mutation, direct product call or data-dependent branch.

Let P be the cumulative bank frame, initially I, updated by P <- F P.
Normalize U=P^-1 Y. Mixing leaves U unchanged. At a reader event e=(A_i@p),
write v_e=P_e^-1 e_p and let q_e be the parity vector of preceding B calls.
Then this event adds

```
v_e A_i (z_initial + sum_j q_ej B_j x_j)
```

to U. Neither mixing nor readers change z, so q_e depends only on the B
timeline. Setting every A_i=0 and varying all bank dirt forces P_final=I;
L>=1 is sufficient. Thus the final contribution is the sum of these terms.

For each i, set every other A_k to zero and project to logical row i. Universal
correctness gives

```
sum_(e labelled A_i) (v_e)_i A_i z_e = sum_j M_ij A_i B_j x_j.
```

Keep an event labelled A_i exactly when (v_e)_i=1, retarget it to logical row i,
and delete all bank transformations. Preserve every B call and the relative
order of retained events. Each retained reader sees the same z_e. The displayed
identity gives its required output, while the B timeline restores z and the
unused helpers remain untouched. Each event is retained at most once and
keeps its label. This proves the componentwise bound for all stated parameters.
No commutativity or large-dimension polynomial-independence premise is needed.

Equivalently, validity is exactly the following finite coefficient test:

```
P_final=I, q_final=0;
sum_(e:A_i) (v_e)_r = 0                    for every i,r;
sum_(e:A_i) (v_e)_r q_ej = delta_ri M_ij    for every i,r,j.
```

Necessity follows by independent zero/identity map specializations and varying
each initial source or connector coordinate; sufficiency follows by summing
the event formula. The checker represents these coefficients as integers of
bits and explicitly checks every helper row. Its resource limits (64 sources,
256 outputs, 512 bank rows) limit this implementation, not the written theorem.
Zero rows, zero source/output counts and R=0 obey the same proof. For L=0 the
endpoint is vacuous, but P_final=I need not follow; that convention is excluded.

## Consequences and essential scope controls

Erasure sends any mixed word of at most 73 map calls to an ordinary word of
at most 73 calls. The ordinary support floor is 72: twice each of five B maps
and 31 A maps. At 72, the 945 canonical paired-source words cover at most 31
of 32 masks; none supports all 31 nonzero masks with paired readouts. Ordinary
parity excludes 73. The credited 74-call construction is allowed with every
additional helper untouched, proving exactness in the extended model.

Ordinary parity must **not** be asserted for the mixed word. At fixed z, let
C be h += y. The word A@y, A@h, C, A@y, C is the identity for arbitrary dirt
and arbitrary A, despite using three A calls. The fixed odd-reader fixture
checks this and its erasure to two cancelling calls.

For B prices (1,4,10,16,28) and unit A prices, every ordinary word pays at
least 180. If it has ten B calls, a missing mask needs at least two extra A
calls; if it has at least twelve B calls, it pays at least two extra units
for B. Both cases cost at least 182, attained by the inherited word. Cinna
Davis's [PR1770 weighted result](../weighted-connector-readouts-seed1275309492/README.md)
is credited. Erasure preserves this optimum; it does not solve arbitrary
unequal-price instances.

Independent readers are essential. With one source, two outputs and A_0=A_1=A,
a paid output conjugation broadcasts one dirty-safe ABx update to both outputs,
using two A calls where an unframed implementation needs four. The certificate
has a literal eight-event witness with four charged output XORs. Exhaustive
2-by-2 matrix tests show its endpoint is correct exactly when
(A_0+A_1)B=0: 928 of 4096 triples, including all 256 equal-reader cases.
Its failure for independently chosen readers is checked explicitly. This is
a small scope witness, not a new common-reader broadcast construction;
[PR1707](../common-a-broadcast-readout-seed4a52/README.md) already supplies
that changed interface and its fully charged five-source construction.

## Complete invoice and limits

For nonnegative fixed **target-port-independent** complete prices a_i,b_j,

```
C_maps(W) = sum_i a_i N_Ai + sum_j b_j N_Bj;
C_maps(erase(W)) <= C_maps(W).
C_total(W) = I(W) + P(W) + D(W) + C_maps(W) + sum_F C_F(W).
```

I is admission/layout, P is coefficient/frame preparation, D is instruction
construction/access/dispatch, and each C_F includes the actual mixing
implementation, access, routing and cleanup. All complete child prices include
arithmetic, source/coefficient access, private restoration, frames and head
return. With nonnegative mixing charges the optimum additive macro tariff is
unchanged, since ordinary words are also allowed. The favorable free-mixing
relaxation already fails to improve it, so no larger mixing search is justified
under these hypotheses.

Retargeting A calls can change port-dependent routing, instruction travel,
layout and hosting costs. Those quantities are not dominated by this proof.
The theorem does not instantiate these maps inside the selected supplier,
construct a physical child implementation, prove a recursive moment improvement,
or settle precision, common-label realization, full-row reservation, tape,
compiler, analytic transfer or intermediate delivery cuts. Non-scalar block
frames, output/connector mixing, restricted/shared readers and nonbinary or
rounded operations require separate analysis. No selected frontier changes,
full cold replay, formal-kernel proof or independent human review are claimed.

## Reproduce and covered evidence

From the repository root, with CPython 3.12 and no dependencies:

```
python3.12 -I -B scripts/research_package.py --package research/generic-output-mixing-erasure
```

The registered run checks source pins, the fixed CERTIFICATE.json and
EXPECTED.json, a separate independent oracle, and seven behavioral test groups.
Verification is read-only and fails on missing evidence. Explicit generation
uses verify.py --write-expected NEW_PATH and refuses to overwrite a file.

| Evidence | Exact scope |
|---|---|
| Written theorem | Every M,L>=1 and finite R>=n in the contract above |
| Primary coefficients | All dirty rows and labelled coefficients, both orientations; 74-call baseline and 138-map/128-XOR helper decoration erase to the same 74-call word; odd-reader identity erases 3 to 2 |
| Independent algebra | Sparse noncommutative terms on every original input vector; backward suffix influence computes erasure without using forward inverses |
| Two source enumerators | Restricted-growth words versus least-unmatched endpoint pairings; all 945, identical full coverage histogram |
| Output frame census | Every one of 168 GL(3,2) frames around the stated two-source/three-output batch; 1728 total input readouts |
| Short-word census | Every one of 19531 words of length at most six in the five-letter one-source/one-reader/two-bank alphabet; 76 valid, 44 with mixing; every valid word erases correctly |
| Matrix oracle | All 256 two-by-two A/B pairs; all 4096 common-reader triples; explicit noncommuting reversed-product failure |
| Failure controls | Missing connector restoration/readout, helper-only defect with correct logical outputs, residual output frame, aliased XOR, typed index, independent-reader violation; real coefficient/frame detector deletion is detected |
| Package behavior | Normal/optimized relocated unchanged replay; missing/corrupt/typed/balanced receipt rejection; missing/duplicate fixture, erasure and source drift; generation/no-overwrite |

Finite evidence supports the implementations; it does not replace the
all-parameter argument or constitute a proof-assistant theorem.

## Provenance

Base c676548106012571fefa1dce0ec16f1bcfe11dce; selector nonce
779e702f7c4ee535de2ee386c8e4f4bf; refined connector-alphabet-change card.
[TASK.json](TASK.json) records scope, overlap and exact predecessor heads;
[SOURCES.json](SOURCES.json) pins all inputs by Git blob and SHA256. The selected
record remains SHA256 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32,
conditional kappa 0.001672660197076918, with complex side binding. Its source
bindings were checked, not its full frontier1094 cold replay.

## Open next questions

The useful next question is whether one selected call family has a nontrivial
known relation among its reader maps that invalidates independent isolation
and admits a fully priced shared-reader realization. First extract a pinned
family's exact reader matrices, labels and complete target-port prices; then
test a two-output identity and charge routing/restoration. The blocker is the
absence here of such a selected-supplier occurrence. Repeating universal
scalar output-mixing searches would not answer that changed question.

Credit Ross Richardson's PR943/934 and retained dirty-commutator/fanout lineage
(including @shhxera and Chafik Boukhalfa), Adam Gall, Arham Garg, Cinna Davis,
and PR1707's 1337isnot1337. Prepared by Ross Richardson with substantial
OpenAI Codex assistance in proof, independent algebra, implementation and
writing. The recursive-interface and exact-circuit-verification specialists
performed separate AI-agent checks. New material is Apache-2.0; all predecessor
inputs and notices remain unchanged.
