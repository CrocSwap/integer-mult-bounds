# Four signed-connector shears must all point the same way

**Scoped arbitrary-coefficient theorem with an exact finite residual census;
no new kappa or selected-supplier admission.** At exactly twelve ordinary signed
queries and four nonzero scalar shears on two arbitrary dirty roots, the signed
three-by-three target below admits **no mixed-direction shear word**. Thus
allowing both directions adds no valid word to the union of the two one-way
classes. Combined with Charles Bethin's [PR1983 one-way theorem](../nonunit-signed-connector-rigidity/PROOF.md),
every valid word has unit transfer coefficients and one of two complementary
forced port assignments.

This closes the four-pass handoff in Cinna Davis's
[PR1675](../bidirectional-root-obstruction-seed50/README.md). That predecessor
already excluded at most three passes in the bidirectional alphabet. Ross
Richardson's PR1651 already supplies the attaining four-pass word; PR1682
establishes its one-way unit-port rigidity. Neither their minimum nor their
construction is new here. The new result excludes the remaining genuinely
mixed four-pass alphabet, including the exceptional **port-changing pairs**
that cannot be discarded by assuming the old one-way pairing lemma.

## Exact interface and claim

Work over Q or C with eight distinct arrays
`x0,x1,x2,y0,y1,y2,z,w`, of any common positive length and arbitrary independent
initial contents. Fixed linear maps `Ai,Bj` are arbitrary and need not commute
or be invertible. The program is a data-independent finite word, uniformly
correct for every choice of maps and inputs. Sources and coefficients are
immutable; outputs are never read. Every child restores its private scratch,
other rows and required head positions.

The only operations are

```
B query: r += s Bj xj       A query: yi += s Ai r       (s in {+1,-1})
U(a): z += a w             L(b): w += b z             (a,b nonzero in Q/C)
```

There are exactly twelve queries and four shears. No root permutation,
scaling, copy, clean initialization, source mutation, extra root, output
feedback or scaled ordinary query is free or permitted. The endpoint is

```
x'=x; z'=z; w'=w;
yi' = yi + sum_j Mij Ai Bj xj,
M = [[1,1,1], [1,1,-1], [1,-1,0]].
```

**Theorem.** All four shears have the same direction. Their coefficients are
then two `+1` and two `-1`, by PR1983. For direction `z += a w`, the query ports
are `B0=B1=A2=w` and `B2=A0=A1=z`. The opposite direction swaps the root names.
Each operator uses one positive and one negative query at its forced port.
The mixed-direction impossibility is proved below by an unbounded symbolic
reduction and a completely exhausted, independently enumerated unit residual
case. It is not inferred from a finite box of rational coefficients.

## 1. Pairing and root-only identities

Every operator appears at least twice. It cannot be absent because every row
and column of M is nonzero. A single B injection cannot vanish under invertible
root shears; a single A read cannot cancel independent initial root dirt.
Independent sources prevent cancellation by a different B. Thus twelve queries
force exactly two occurrences of each operator.

Let G be the cumulative two-by-two shear matrix. Its final value is identity
by root restoration. A B injection at port r contributes a signed column
`G^-1 e_r` to the normalized root vector. Its two columns must cancel. An A
read contributes signed dirty row `e_r^T G`; its two dirty rows must cancel.
**Different physical ports may pair when these vectors agree up to sign.**
This is essential to the residual case, not a relaxation of dirt restoration.

Classify all sixteen length-four direction words:

* The two constant-direction shapes are the one-way predecessor class.
* In a shape with three U's and one L, the lower-left entry of the final matrix
  equals the lone L coefficient, regardless of the U coefficients. It cannot
  vanish. The root-swapped argument covers three L's and one U.
* In the chronological alternating shape `U(a),L(b),U(c),L(d)`, the final
  upper-left entry is `1+bc`, so restoration forces `bc=0`, contrary to the
  nonzero premise. Swap roots for the other alternating shape.
* The remaining four shapes are disjoint or nested inverse excursions.
  For `U(a),U(c),L(b),L(d)`, closure forces `c=-a,d=-b`.
  For `U(a),L(b),L(c),U(d)`, closure forces `c=-b,d=-a`.
  The other two shapes swap roots. These implications follow directly by
  combining adjacent shears and inspecting the off-diagonal entries.

A valid word's endpoint commutes with every allowed operation: its only
nonidentity block sends immutable sources to unread outputs, whereas queries
and shears only touch roots between those layers. Therefore **cyclically
rotating the complete word preserves the endpoint**. This is an algebraic
bijection for the impossibility proof, not a free physical rebinding. Rotate
a nested loop immediately after its first shear to obtain a disjoint loop;
rename roots if needed. Every mixed candidate consequently reduces to

```
U(a), U(-a), L(b), L(-b),       a,b != 0.
```

Queries can occur arbitrarily before, between or after the shears. Rotation
may change first query signs, which the census below explicitly allows.

## 2. All nonexceptional coefficients collapse to one root

The five phase matrices of this disjoint loop are `I,U(a),I,L(b),I`.
The normalized source columns and dirty reader rows are:

| Phase type | B at z | B at w | A at z | A at w |
|---|---|---|---|---|
| I | (1,0) | (0,1) | (1,0) | (0,1) |
| U(a) | (1,0) | (-a,1) | (1,a) | (0,1) |
| L(b) | (1,-b) | (0,1) | (1,0) | (b,1) |

Cross-port source pairing is possible only through
`(1,-b) = s(-a,1)`, with `s=+1` or `-1`; hence `a=b=-s`.
Cross-port reader pairing is possible only through `(1,a)=s(b,1)`;
hence `a=b=s`. Thus **any port-changing pair forces
`(a,b)=(1,1)` or `(-1,-1)`**. This exact coefficient argument includes
arbitrarily large, irrational and nonreal coefficients.

Outside those two cases, all B and A pairs remain at one physical port, with
opposite signs. Their same-port pairing restrictions are also exact for every
nonzero a,b: a w-source pair either lies wholly in the unique U phase or has
both endpoints outside it; a z-reader pair has the analogous restriction.
The root-swapped statements hold for the unique L phase. There are no further
nonzero exceptional same-port strata.

Here is why a paired w-source cannot reach a paired z-reader. In the U
excursion, a w-source wholly inside its middle phase injects no z signal at
the first shear and has already canceled by the second. A w-source with both
endpoints outside has constant source coefficient throughout that phase; its
z signal is constant inside and zero outside. A paired z-reader either stays
inside that phase or has both ends outside, so the difference is zero. The
later L excursion cannot create new z signal (it only changes w); nor can it
retain an old one, since the U excursion's source contribution has already
canceled. The same reasoning exchanges roots and U/L for z-source to w-reader.
Same-root source coefficients remain the ordinary two-step signed pulses;
there is no completed round trip between the disjoint excursions.

For an exact symbolic corroboration, the verifier propagates polynomials in
indeterminates a,b over all **420** interleavings of a B pair, an A pair and
the four ordered shears, for each ordered cross-root pair. Every placement
with restored source and canceled reader dirt has zero cross coefficient.
Dropping either condition admits nonzero controls. The phase argument above
is what ensures no special nonzero coefficient specialization was missed.

Every nonzero entry of M therefore requires its A and B pair to use the same
root. The bipartite support of M is connected, so all six operators use one
root. Its source signal is an ordinary six-step signed prefix walk. The
inherited PR944 obstruction excludes all three rows of M from its differences;
we reproduce all 720 walks with histogram `[72,84,84,48,264,84,84,0]`.
PR1983 also gives a written six-vertex cube proof of that inherited obstruction.
No new one-root theorem is claimed.

## 3. Complete exceptional unit case, including changing ports

Conjugating all root coordinates by `diag(1,-1)` maps the `(-1,-1)` case to
`(1,1)` while only changing allowed query signs; it fixes the endpoint. This
is again a proof bijection, not an unpriced operation in an implementation.
It remains to examine the single fixed chronological loop

```
U(+1), U(-1), L(+1), L(-1).
```

Delete the A queries, which do not change roots. A source trace has six B
occurrences, two per label, and the four fixed shears. Normalize the first B
sign for each source to `+1` by multiplying that independent source symbol by
its original sign. The target must then be tested against **all eight column
sign choices**, not just M as written. A closing B occurrence may use either
physical port and either sign, but is retained exactly when its normalized
column cancels the first injection.

Two independent exact implementations exhaust this class:

1. `verify.py` inserts every legal next B occurrence or next shear and
   propagates both integer root rows on the five formal columns
   `(z_initial,w_initial,B0x0,B1x1,B2x2)`.
2. `independent.py` enumerates all **90** labeled paired-source orders and
   all **210** nondecreasing assignments of their six events to the five
   phases. For every first/closing port choice it reconstructs source
   coefficients as `G * (open normalized injection intervals)`, without
   propagating source coefficients through gates.

The 18,900 order/phase skeletons produce exactly **69,948** restoring canonical
source traces, or **559,584** after the eight first-sign choices. Neither
enumerator assumes that a B pair remains at one port. They agree on the exact
map from every entire source word to its complete **27-bit reader-row mask**,
not merely the final count or exclusion.

There are eleven gaps and two root values per gap. For each output the exact
criterion is that two signed root observations sum to zero on the two dirt
columns and to the required target row on the three source columns. The first
engine groups signed-normalized dirty rows and takes all signal differences;
the second uses membership of complementary full five-column observations.
It includes changing-port readers. All A pairs can be inserted independently
at their selected gaps, even when gaps coincide, because outputs are distinct
and unread. Thus the criterion is both necessary and sufficient, and no reader
chronology is lost.

**Zero traces admit all three target rows under any column-sign choice.**
`EVIDENCE.json` contains the complete row-availability histogram and a canonical
SHA256 over all source-word/reader-mask records. This is a finite exact exclusion
of the residual case, not a kernel-checked theorem. Together with Sections 1–2
it excludes arbitrary-coefficient mixed four-shear words.

The checker also supplies legal one-source `A B` pilots with a changing B port
and with a changing A port. They prevent a misleading negative result obtained
by reusing the predecessor's same-port pairing assumption. An all-ones target
is attainable in the full census. These controls show the expanded checker is
not simply rejecting all mixed-direction programs.

## Complete cost consequence

Let `q_F,r=c_F,r,+ + c_F,r,-` include both complete signed invocations at port r:
source/coefficient access, all children, arithmetic, precision, frames/routing,
private restoration, head return and dispatch. Let `t_d,+` and `t_d,-` price
complete unit full-row passes in direction d, with the same obligations.
For common additive admission/preparation/controller overhead `I+P+D`, define

```
C_(w->z) = q_B0,w + q_B1,w + q_B2,z + q_A0,z + q_A1,z + q_A2,w
           + 2 t_(w->z),+ + 2 t_(w->z),-;
C_(z->w) = q_B0,z + q_B1,z + q_B2,w + q_A0,w + q_A1,w + q_A2,z
           + 2 t_(z->w),+ + 2 t_(z->w),-.
```

The exact additive optimum of this **twelve-query/four-shear class** is
`I+P+D+min(C_(w->z), C_(z->w))`: this theorem excludes every mixed direction;
PR1983 supplies the coefficients/ports in either remaining class; PR1651's
literal word and its root swap attain the sums. If overhead depends on order
or orientation, use its actual value; no optimum for that changed tariff is
claimed without pricing the words. Different query counts are also outside
the optimization.

For example, if every query pair costs 20 at z and 200 at w, and every unit
root pass costs 1, both orientations cost **664**, excluding common overhead.
The independently cheapest-port relaxation of 124 is still unattainable even
with arbitrary complex bidirectional coefficients. The census itself does not
measure a native tariff or implement an all-size supplier.

The complete primitive recurrence and 300-factor lowering of the credited
attaining word remain PR1651's work, not rerun or newly claimed here. This
package replays its atomic complete-query contract, free noncommutative
endpoint, literal inverse and all sixteen cyclic rotations, plus independent
integer block operators in dimensions two and three, including singular and
noncommuting maps. All source, target and root dirt columns are retained.
Omitted-shear, wrong source restoration and aliased-dirt controls must fail.

## Reproduce and evidence boundary

From repository root, standard library only:

```sh
uv run --python 3.12 --no-project python -I -O -B research/bidirectional-four-shear-rigidity/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/bidirectional-four-shear-rigidity
```

Expected primary marker:
`PASS_BIDIRECTIONAL_FOUR_SHEAR_RIGIDITY canonical_traces=69948 signed_traces=559584 mixed_successes=0 symbolic_shapes=16 no_new_kappa`.
The registered launcher additionally authenticates source/provenance metadata.
`verify.py --record` is the explicit evidence generator; normal replay does not
rewrite any file. An exported checker can use `--source-root /path/to/repo`;
all five live predecessor input hashes are verified before computation. Exact
source bytes, rather than regenerated compression containers, are pinned.
No predecessor executable is imported. `VALIDATION.md` records actual runs.

The universal result relies on the written program-to-census reduction above.
Finite checks alone do not quantify over arbitrary programs. No proof assistant,
independent human review, selected cold replay, native supplier admission,
all-size compilation, hosting/precision contract or analytic multiplication
transfer is asserted. The selected conditional kappa remains
`836330098538459/500000000000000000`.

## Provenance, overlap and credit

Independent OS seed `652b2d372ee11d8364eb3ba12820c34c` was drawn once at base
`e112d71c8d7bb32435debcc54df932593dd8223a`; complete emitted cards are in
`SELECTION.json`. The chosen card is `connector-alphabet-change`, refined to
PR1675's actual four-pass handoff. `TASK.json` was written before computation.
The [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2049#discussioncomment-18931220)
records the distinction. `SOURCES.json` pins the predecessor bytes, base, blob
IDs and selected/catalogue provenance. The selected record was followed to
`community-batch1099-review.md`, `community-frontier1094-audit/SELECTED-SOURCE.json`
and `make frontier1094-verify`; that full replay is not required for this isolated
interface theorem and was not run.

Credit Ross Richardson for PR944/934/943's connector model and signed target,
PR1651's four-pass witness (`e6180f6acd6324d823031cab2ab51f31a388eb49`), and
PR1682's one-way port theorem (`faa9bc8e85c6b505fc61424e6357b7d80e88e922`).
Credit Charles Bethin for PR1637's two-root twelve-query interface
(`9bee6cc01f151b92ccfe147046855715843f066a`) and PR1983's arbitrary-coefficient
one-way theorem (`9cb25cd2851fd4d4474abd515b63d721f5f370c7`). Credit Cinna Davis
for PR1675's short bidirectional theorem and explicit handoff
(`a8d459974abf7ba88316c87396565f7e5fc9656f`). Their inherited notices and
attribution remain in the unchanged source packages.

The cached shared overlap snapshot had 329 open PRs including drafts at
2026-10-14T18:11:09.770757Z and 692 discussions including comments/replies at
18:12:32.610168Z, both completely paginated. Local integrated packages through
PR2027 and live Discussion1660/PR1675/PR1983 were inspected. This is not a
novelty guarantee; closed work outside local records and later changes may be
missed. The separate round-three F2 five-source/two-root question has a
different target, characteristic and transfer budget.

Prepared for Adam Gall with substantial OpenAI Codex assistance in proof,
implementation, experiments and prose. Both checker implementations were
written by the same assistant; “independent” refers to algorithms, not people.
No subagents were used. New work is Apache-2.0.

## Open next questions

* **Can extra queries or a longer mixed loop improve an actual nonuniform
  complete tariff?** This theorem fixes twelve queries and four transfers.
  First specify port prices and search a bounded changed class with all
  source/read/transfer restoration retained. Native prices and an intended
  interface are needed before a count improvement has physical meaning.
* **Does an admitted selected-supplier seam expose this signed target?** Pin
  six immutable complete child contracts and two root lifetimes, then price
  their exact frames, ownership, precision, routing and control. No such seam
  is provided here; without one, neither this tariff theorem nor the earlier
  constructions change the paid recursive moment.
