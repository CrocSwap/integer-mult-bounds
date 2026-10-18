# Volume I self-review

Scope: all A001–A100 statements, proofs, hypotheses, dependencies and conjecture boundaries were reviewed informally. Inventory:100 consecutive unique IDs,96 proof blocks,4 explicitly unproved conjectures. The volume is13716 whitespace-separated words at this checkpoint. This is mathematical editorial review, not independent peer review or kernel certification.

## Corrections made during review

- A002 uses left cosets gH, with no quotient-group assertion unless H is normal.
- Section III makes m>0 explicit for cyclic groups.
- A066 uses a single Bézout identity with the lcm so independent root descent cannot destroy the product-one condition.
- A075–A077 keep twisted products ordered and use commutativity only where it is actually needed.
- A087 proves exactness by fixed bases and rank preservation, avoiding invalid averaging in modular characteristic.
- A095 separates the trivial degree≥grid-size bound before the inductive root count.
- A099 restricts gauge equivalence to basis changes reducing to identity; otherwise the linear quotient alone would miss the residual automorphism action.
- A100 now uses G_x/Z, quotienting the unavoidable central two-dimensional scalar kernel. A full tensor GL stabilizer cannot be unipotent in the intended positive dimensions. The height conjecture is unproved, has no global novelty/open-status claim, and supplies no proved premise elsewhere.

## Boundary cases checked

Zero tensors and deficient supports (A011–A017); nonabelian coset order (A001–A009); finite versus infinite fields in weight comparison (A028,A033–A034); characteristic dividing group order (A035–A040,A083–A087); zero-dimensional diagrams and empty determinant products (A048–A049); noncommutative endomorphism rings (A045–A050); inseparable extensions where only determinant norms are used (A063–A067); negative exponents in groups; finite-field q=2; rank-zero modular kernels explicitly separated in A096.

## Source and credit audit

All8 inspected local source byte hashes remain unchanged. Eight historical DAG query rows are metadata, not fresh verification. In particular the Prop:=True markers in L5 are excluded, no goal/sorry statement is used as evidence, and source names do not stand in for proofs. Primary P1–P6 supply bounded context; the body gives independent derivations. Standard norm, Hilbert90, invariant, quiver and flag results are not represented as new discoveries. This is a substantial connected toolkit with some short foundational lemmas, not100 globally new theorems.

## Remaining review request

Independent peer review should especially inspect A018–A019 intrinsic algebra recovery, A022 termination, A045–A046 local-ring exchange, A051–A055 simultaneous flag blocks, A066 coupled root correction, and A084–A090 semilinear descent. No unresolved proved-claim gap was found in this self-review. Conjectures A010,A030,A060,A100 remain proposals only; this source search does not determine their global status.

## Cross-volume overlap correction

A059 was strengthened beyond the graph lemma also appearing as B006: it now proves the fractional symplectic chart transition (c+dS)(a+bS)^−1, the exact invertibility domain a+bS, and symmetry in every characteristic. The proof uses the actual projected graph map, so it proves both necessity and sufficiency without assuming the denominator exists.

## Peer corrections and readability

The independent reviewer correctly required A059 to qualify symmetry: the new graph map is symmetric if and only if the original S is symmetric. The statement and proof now say exactly this. A078 now says component corrections multiply to a global solution. A002 uses left cosets and A032 uses the explicit notation gG_x. Prose/math spacing was normalized, headings made consistent, and runs of blank lines reduced; equation internals were retained. The L6 source entry now includes the actual hypLift_isIsometry declaration and proof excerpt, not just a file hash.

## Final hypothesis and sufficiency readback

A071 now explicitly calls φ a group homomorphism. Shared sectionVIII group actions and sectionIX finite-Galois/semilinear hypotheses are stated before their entries. Independent review covered all A081–A100 and found no further blocking error. A032 now explicitly assumes y lies in Gx for its full character-fibre assertion and proves that any candidate with the same ratios as a known transporter is itself a transporter; existence between arbitrary points remains a separate hypothesis.
