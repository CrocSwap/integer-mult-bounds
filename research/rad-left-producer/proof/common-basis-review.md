# Changed left-DAG frame and common-basis review

Status: accepted component, conditional on the retained compiler/tape interfaces. This is a written mathematical argument and independent exact finite checker, not external human review or formal verification. Literal dirty-state compilation is separately checked by the graph worker.

## Independently reconstructed changed facts

The checker [independent_axis_review.py](code/independent_axis_review.py) imports no upstream producer, positive labeler or matching selector. It reads the retained binary DAG, positive labels and selected-link witness, checking their supplied hashes before independently reconstructing all integer input-support sets and output supports. At h23 and h25 every addition has disjoint integer supports, every designated partial output is exactly the required common-point exclusion, and every retained total contains exactly all triples through its common point.

The new results are respectively `c=36328,q=5336,links=4021,R=37643` and `c=48063,q=6925,links=5233,R=49755`. There are 75,412 and 99,909 distinct checked positive-space inclusions, covering 751,196 and 1,086,127 integer basis vectors. Each selected donor and each operand/terminal-use target is unique. Strict controller-event dependencies are acyclic under the retained rank/envelope/logical-event order. The high-bit terminal-use vertices are distinct from every middle-producer input incidence.

For a non-source positive label, let `F` be its one- or two-element forced common core and let the remaining nonzero coordinate symbols be signed components. For component k use the integer vector with nonforced coordinates `(3-|F|)*sign(k)` and forced coordinates equal to the sum of its signs. These vectors span the exact label space, are independent by their distinct free component coordinates, and satisfy `sum x_i=3x_c` for every forced point c. Each source is its retained triple indicator. On that common-point hyperplane the actual form `G=I-J/9` obeys

`x^T G x = sum_(i != c) x_i^2`.

Thus each new label and every nested difference is nondegenerate over the rationals. The checker tests containment on every integer basis vector, including new matched dependencies; it does not substitute rank inequalities for space containment.

The complete independently reconstructed physical rank histograms equal the selector's saved histograms, including zero-rank calls. Their mass is `hR+2h(h-1)`. Retained centers are the h designated totals, each of rank h-1. The copied-center replacement removes exactly h rank-h original cleanups and adds h rank-one complements while retaining every rank-(h-1) copy transform. Its local mass is `hR+h(h-1)`. The new graphs do not change the two-stage data/source-gauge topology or remove the N paid rank-one endpoint corrections.

## Why the retained common basis applies

The reversed (23,25) geometry at PR37 `cb86e50e9a07685068874d8e4174b2e6c209b95c` fixes the controlled permutation completions, and leaves the two local basis factors free in `GL_23(Q) x GL_25(Q)`. Every new local physical residual is a rational idempotent: it is an orthogonal label projector, its complement, or `P_V-P_U` for verified nested nondegenerate spaces. The latter is idempotent because `P_V P_U=P_U P_V=P_U`. It has rank `dim V-dim U`. Inverse chronology uses the same projector differences, through complement duality.

For a fixed local rank-r idempotent pi in dimension h, all rational idempotents of rank r are conjugate under `GL_h`. The generic ordinary lower/lower profile condition is therefore a nonzero rational minor condition on the free local basis, yielding r singletons for `2r<=h`, or `h-r` singletons plus one `2r-h` block otherwise; rank h gives a complete h block. Under the controlled permutations, the first/last h ambient restriction is the local conjugate up to nonzero diagonal scaling, as in the pinned PR37 proof. This applies to each new residual independently of the old graph's particular projector identities.

There are finitely many new residuals. Each ordinary condition is nonzero on the same irreducible free basis space. The unchanged triple-line auxiliary restrictions and data null-corner conditions are also nonzero there, with PR37's all-parameter rank cuts and exact witnesses retained. Their finite product is nonzero. A rational point therefore satisfies all old boundary and new local conditions simultaneously. This changes the fixed address table and eligible prime, and requires recording their additional finitely many bad denominators/minors; it adds no runtime basis adapter.

This argument supplies existence rather than a materialized giant ambient basis. Fixed native setup/table constants, eligible prime, eventual cutoff and the complete semantic/bulk recurrence remain explicit conditional qualifications. It justifies reusing the reversed data profile nine singletons plus `[21,17,481]` with the new local rank histograms, provided the independently compiled dirty timeline has the stated restored endpoints and role-volume fractions.

## Boundaries of this review

The component does not itself certify the multiplication exponent. The coordinator independently reconstructs the complete histogram and exact moment, all paid rank-one corrections, maximum child, product row stock, semantic guard, leaf stopping, 47 strict assembly conditions and eventual absorption. The graph worker independently checks the actual compiled scalar/dirty timeline and physical controller stock. The present argument cannot authorize omitting either set of checks.

The first checker invocation supplied the wrapping axis JSON instead of its `producer` field and failed before reading scientific inputs. A fresh v2 invocation corrected only this input adapter; the failed log is retained in external evidence. The successful [h23](results/independent-left-axis-23.json) and [h25](results/independent-left-axis-25.json) certificates retain hashes, counts, finite scope and limitations.
