# A P104 side word with delayed query inputs

I construct a finite forward P104 identity word by inserting four delayed
queries into the selected side producer and obtaining four more queries from
its omitted target rows. This replaces the separate gather/delivery architecture
of PR1972/1991. I retain eight rank-seven private descents, hence COPY56.

The exact local profile is

```
2564 H1 + 547 H2 + 432 H3 + 142 H4 + 83 H5 + 128 H6 + 11 H7.
```

Its rank mass is 6782: persistent frame progress 6726 plus COPY56. I replay
all 836 persistent inputs and eight arbitrary private inputs. I check 241 new
native recipes covering 421 paid occurrences, including their global phases.
The 628 dirty helpers regain their logical inputs at their declared output
frames. This is a finite forward construction, not a globally admitted supplier.

I also prove a limit for this fixed profile. Under the paired-chain coverage
law and halving guard, no stage count, owner packing or fully paid auxiliary
bank choice reaches the saving selected at this package's base. The best
among the fifteen small-stage screens has a favorable moment above
1.000554 at that saving. A separate entropy inequality covers all larger
stage counts. I do not claim an exponent improvement.

## Contract and sources

Use the 104 root ports in the pinned PR1972/1991 fixture, expressed in the
selected Hamming gauge. Source X_t enters with intrinsic frame C_qt and exits
at F9. Target Y_t enters at I and exits at F9 C_qt^-1, with logical value
Y_t+X_t. The source logical values remain unchanged.

The helper inventory is:

| Group | Count | Boundary |
| --- | ---: | --- |
| Retained selected-side helpers | 480 | Retained native entry/exit frames |
| Omitted C-source ports | 8 | I to FULL |
| Omitted C-target ports | 8 | I to FULL |
| Early query carriers | 20 | I to FULL |
| Late query carriers | 112 | I to FULL |

All 628 helper inputs are independent and arbitrary. Logical restoration
does not mean that their charged frame transforms disappear. The eight owned
private fields may start dirty; the word clears them before use and finishes
with zero private outputs. It reuses one private field for eight copy/drop
lifetimes under the inherited private-copy convention. I do not claim a
reversible uncomputation of each discarded copy.

The producer is the exact center-free selected word reconstructed by Ali
Romman's `native-source-codes/source_data.py`, with its frozen archive and
original credits. I do not substitute the newer P104 low-rank word for it.
The fixture still comes from Rohan Arun's PR1972 through Chafik Boukhalfa's
PR1991. SOURCES.json pins these inputs and the native compiler/interpreter.

## Algebra of the combined word

Write G for the P104 Gram matrix and

```
D[t,k] = <r_t,a_k>,
T[s,k] = 2 <r_s,b_k> / <a_k,b_k>,
D T^transpose = 2 G.
```

If a side producer on P104 union {a_k} receives ordinary inputs x and
pseudo-inputs z_k=-(q_k+T_k^transpose x)/2 at a_k, its 104 requested rows give

```
(I-G/2)x + D(q+T^transpose x)/4.
```

Initial compensation -Dq/4 makes this x. The mixed deleted basis {b_k} is
not the coordinate frame, so label substitution into the selected P112 word
does not establish that producer. I implement the identity through two
different query cuts in the selected word instead.

Four a_k lie in the second deleted orthogonal frame C. In selected indices
they are X81, X86, X54 and X25. The corresponding coordinate-center rows at
axes 3,4,5,6 have diagonal coefficients g=(-1,-1,1,-1) on these four inputs,
and zero off-diagonal coefficients. Run A with arbitrary inputs h at those
ports. At the A cut, query Q_i contains g_i h_i plus the ordinary source
query and helper dirt. Add delta_i=-Q_i/g_i along the A-state response to
input i. The effective source value h_i+delta_i has no h_i contribution.
The other initial-dirt terms have known linear coefficients and receive
frame-zero compensation.

The other four b_k lie in C. Their completed code-only target rows satisfy

```
Y_b = eta_b - (1/2) sum_s <b,r_s> x_s.
```

All C-source columns vanish in those rows because the roots of C are
orthogonal. Thus they do not depend on the early delayed inputs. Put
g=<a_k,b_k>. Copy -Y_b/g from b_k-perp, descend seven ranks to <a_k>, and
deliver with coefficient D[t,k]. The dirty eta_b term receives initial
compensation; the remaining term is the required Gram contribution.

## Early injection and arbitrary dirt

At original event 12550, each early source column has six relevant rows in
five non-FULL frames. `verify.py` lists their exact registers, coefficients
and frame IDs. The five frames form an antichain: one has rank two and four
have rank three. A private query copy descends to <a_k> and feeds five new
dirty carriers there. Each carrier then climbs to its injection frame.

The program treats the twenty carrier inputs as independent, rather than
assuming a shared dirty value. One carrier needs a later repair: after
original event 16592 it climbs from frame230 to frame240 and subtracts its
whole content from L341. L341 has no later scalar consumer at that frame.
The other nineteen carriers need no non-FULL repair.

Immediately before original event17846, all remaining non-Y responses of
the twenty carriers lie at FULL. The four original query registers L224,
L11, L240 and L9 still hold their A-cut values and have zero response to the
injections. The program makes 135 FULL-frame additions to cancel the
non-Y responses, then twenty additions c_i+=Q_i/g_i to restore the carriers.
It runs the original full-frame cleanup afterward, unchanged. Skipping the
query registers' original cleanup would be incorrect because later cleanup
operations read them.

The twenty carrier paths cost

```
24 H1 + 17 H2 + H5 + 16 H6 + 3 H7,
```

with rank mass 180. Their progress belongs to new dirty helper paths; it is
not an uncharged private ascent or an extra copied-information descent.

## Late-query chronology

The verifier constructs a dependency DAG that preserves strict access order
on each original register, including reads. It removes only the original
center phase. It first executes A and the dependency ideal needed to finish
the four b_C target rows, then resumes the remaining events.

This query-ready cut contains 13,412 original events. The four final query
writes are events16453,16309,16173,15955 on Y110,Y106,Y8,Y50. None of the 208
required live-target upper climbs belongs to that dependency ideal. Each
target therefore still has its requested rank-seven read interval available.
The verifier checks each actual common frame in the reordered word.

For each of the four late queries, 28 carriers serve its 52 targets. The
112 carriers each follow ranks 0 to1 to7 to9, giving

```
112 H1 + 112 H6 + 112 H2.
```

The chosen read occurs after the target's last target-basis mixing or scale,
so the remaining word does not alter its coefficient. At the full-frame
cleanup cut, the omitted query targets climb to FULL. Their still-live values
restore the carriers. After the original cleanup, the program removes each
omitted target's side increment using restored FULL source values.

## Verification and native frames

The checker derives the new initial compensation from an exact formal-row
replay and checks that every required input is available at frame zero. It
then replays the resulting program from scratch on all 844 formal columns.
This proves the linear boundary identity for arbitrary address functions:
each scalar operation acts in one common chart, and each checked native
transport preserves its logical row.

With `--native`, the retained Gaussian-dyadic compiler lowers each new
transport. The separate interpreter compares signed Pauli actions and an
exact nonzero state column, fixing the global phase. Source padding needs
intrinsic C_q before the retained entry adapter; target padding needs C_q
after the retained exit adapter. The checker uses those operators rather
than treating either boundary as an internal canonical-chart edge.

The original native events retain their pinned recipes and their order on
each register. This package inherits their source proof; its native check
covers the new recipes. Semantic controls reject an omitted L341 repair,
an omitted carrier restoration and missing initial compensation. A native
control changes a recipe's global phase and must fail.

```sh
python3 -I -B research/p104-delayed-query-side/verify.py --native
python3 -I -O -B research/p104-delayed-query-side/budget.py
python3.12 scripts/research_package.py --package research/p104-delayed-query-side
```

The replay reads pinned Git evidence and writes no files. The package needs
full Git history for the retained selected archive. I checked the local
prototype with Python3.14.6 and the registered replay with Python3.12.

## Completed optimistic cost obstruction

Grant a dual orientation with the same profile and favorable hosting. All
invocations use this fixed profile; a cheaper second orientation changes the
screened premise. For
paired-chain parameter p>=1, use s=2p+1, m=16p+9, W=208p and one unpaid
coordinate per data family. Let B be the number of additional fully paid
families. The remaining idle rank mass is

```
I = (m-1)W + mB - s*6726.
```

We require I>=0 and put all idle mass at the largest rank R with
m^2>2R^2. This gives a lower bound on any completed moment for the fixed
profile. The budget checker takes the smallest feasible B for each
p=1,...,15 and proves its moment exceeds one at

```
a = 836330098538459 / 499163669901461541.
```

This is the balanced primitive target associated with the selected kappa
at the pinned base. Adding another fully paid family adds favorable cost
(m/R)^a>1 per family, so it cannot repair an already failing moment.

For p>=16, m>=265. The deficit per call is less than48, while exact rational
intervals give

```
a * sum_r n_r*r*log(265/r) > 54.7514 > 48.
```

Using exp(x)>=1+x and discarding the positive idle entropy proves failure
for those p as well. The construction therefore cannot beat the pinned
selected saving within this coverage/guard model. This argument does not
cover a redesigned producer, a changed profile or a changed coverage law.

## Open next questions

- Can a joint target trajectory reduce the 112 late carriers? Start with a
  new legal path for one coordinate query and propagate its coefficient
  through the remaining target mixing. The fixed safe-read paths are already
  priced here; an owner rearrangement alone cannot fix this profile.
- Can the early response carriers share an existing paid path? A candidate
  must restore each independent dirty input and preserve the query until
  the repair cut. Reuse the twenty-column response test before claiming a
  reduced inventory.

Global chronological ownership, the dual word, precision/tape bounds and
all-size admission remain open. I stop this fixed construction at its
unfavorable complete price rather than claiming a new supplier.

## Attribution

Ali Romman's PR1862 supplies the clean-J reconstruction and source pins.
The selected Hamming packet, mutable-source/target, native compiler and
hosting lineage belongs to the contributors retained in that package's
notices, including icekylinx, jacklightChen and DreamingOfClouds. Rohan Arun's
PR1972 and Chafik Boukhalfa's PR1991 supply the P104 query convention and
fixture; Adam Gall's PR1940 and Josie Elliston's PR1071 supply the preceding
delivery geometry. The compiler/interpreter retain their original attribution.
Douglas Colkitt's PR1240 supplies the exact interval arithmetic; the coverage
premise follows the PR1012 and paired-chain lineage.

David Arias's PR2082 and Adam Gall's PR2090 study frozen temporal cuts.
Jeremy Diviney's PR2113 and Ross Richardson's PR2127 extend the retained-path
storage analysis; PR2127 distinguishes productive helper progress from excess
rank. Adam Gall's PR2083 gives the terminal correction floor and its coverage
obstruction; PR2089 gives the direct terminal word. This contribution changes
the query inputs and chronology. It does not claim those terminal or
frozen-cut results. Hope7Happiness's Discussion2131 tests a separate bounded
room-rectangle construction with changed paths.

Jose Manuel (@jmbarrancoml), with substantial OpenAI Codex assistance in
construction, proof, implementation and prose. No independent human review
or proof-assistant verification. Apache-2.0.
