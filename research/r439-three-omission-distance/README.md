# No one, two or three omitted ADDs preserve the frozen PR967 D boundary

The exact5563-ADD PR967 D word has no endpoint-neutral omission set of size1,2
or3, on arbitrary661-column dirty inputs. This excludes15,470,703 pairs and
28,677,526,461 triples by a rank-one factor classification and193,704 grouped
pair checks. It is not brute-force replay of28billion mutants and is not an
unrestricted circuit minimum. Four or more omissions and rewrites remain open.

The predecessor PR1017 proves all single-ADD omission syndromes are distinct.
The new contribution is the multi-omission implication and complete triple
classification. PR1102's two diagnostic input vectors remain guaranteed only
for one omission: endpoint inequality means some input detects a fault, not
that those two vectors do. The selected supplier remains unchanged.

## Exact algebra and proof of coverage

Write the chronological word P=L_k...L_1, each L_i=I+e_d e_s^T, d!=s.
Let B_i=L_k...L_{i+1}. Deleting gate i changes the output relative to P by
T_i=B_i L_i B_i^-1=I+u_i v_i^T, with nonzero u_i,v_i and v_i^T u_i=0.
Deleting an increasing set i_1<...<i_t gives P_deleted P^-1
=T_{i_t}...T_{i_1}. This follows by cancellation of the successive suffixes;
it uses the baseline suffixes, not suffixes of separately mutated words.

Each T_i is an involution. Thus two distinct omitted gates cancel iff T_i=T_j.
All5563 pairs(u_i,v_i) are distinct, as the code checks from literal sources.
Over F2, nonzero rank-one factorization is unique, so this covers every pair.

For distinct T_a=I+u v^T and T_b=I+x y^T,
T_a T_b-I=[u,x] [[1,v^T x],[0,1]] [v^T;y^T]. If u,x and v,y are both
independent, this has rank2: the middle matrix is invertible and the outer maps
are respectively injective and surjective. Therefore their product can be a
transvection only if u=x or v=y. If u=x, nilpotency makes the cross term zero
and the product is I+u(v+y)^T. If v=y it is I+(u+x)v^T. These products commute.
Consequently three distinct transvections multiply to I exactly when they have
one common factor and their other factors XOR to zero.

The verifier groups all factors by u and by v. For every pair within a group it
looks up the XOR partner; there are193,704 such pair checks and no triple.
No other triple can cancel by the proved rank-two case. This covers the entire
declared triple domain, regardless of the positions or noncommutation elsewhere.

## Independent corroboration and controls

The implementation independently replays every literal single omission on all
661 columns and checks the resulting outer-product difference. It converts the
incoming covectors to the common output basis using the exact inverse of P.
Repeating the grouping in the original input basis agrees, as invertible
covector transport preserves equality and XOR.

A separate dense bit-matrix calculation exhausts all420 ordered distinct pairs
of three-dimensional transvections and checks the rank-one product criterion.
A planted duplicate pair and a planted neutral triple exercise the acceptance
and rejection boundaries of the classifier. Seven literal multiple-deletion
replays provide representative corroboration, not claimed exhaustive coverage.
The universal reduction has a written proof above; finite controls do not replace it.

## Reproduce and limits

`python -I -O -B research/r439-three-omission-distance/verify.py`

Python3.12 registered replay, source metadata and selected integrity pass.
All arithmetic is exact F2 bitsets. This rules out removing up to three existing
elementary ADDs while preserving the full D map; it does not cover deleting
whole multi-source records, inserting/reordering gates, target-only observation,
the native multistage compiler, paid hosting, precision or a new kappa.

## Open next questions

Four-omission cancellation can have a rank-two middle product and is not covered.
A feasible next step is an exact meet-in-the-middle catalogue of ordered pair
products, preserving chronological order and all dirty columns. Its quadratic
state storage and duplicate-product representation are the blockers. Do not
infer four-fault distance from the absence of the triples certified here.

## Credit

PR1017 single-omission atlas and PR1102 diagnostic probes, both prepared for
woklerx; PR967 helper stars for theon199, Gareth Davidson PR926/PR915 lineage,
DreamingOfClouds PR589 and eumemic PR555. The source atlas supplies the idea of
suffix/row factors; this package rebuilds them and proves the new multiple-fault
reduction. Substantial OpenAI Codex assistance. Apache-2.0.
Cached overlap coverage and limitations are in OVERLAP.json.
