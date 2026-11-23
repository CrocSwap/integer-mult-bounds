# Review of the literal source grammar

This is a scoped source audit of the carried-basis argument in `PROOF.md`.
It does not implement the astronomical completed word or replace the inherited
machine-cost contracts. The reviewed proof SHA-256 is
`080be9adb3d9a6f2bd58be334881d7ce7c3be691b49c7fb451705917d92a1283`.
All source files below are the exact authenticated copies in `retained/`.

## Boundary supplied before composition

The binary section of #7828's `APPLICATION.md` first normalizes a positive
request for an idempotent P in a complete image/kernel basis. In reversed-tail
coordinates its action is D(P), with identity on the entire complementary
space. Splitting the image in that basis produces disjoint idempotents whose
positive requests compose to D(P). The source also explicitly permits full
matchers, multiplicity extensions and restricted-sector embeddings.

The new lattice completion changes the **choice of the complete basis** at
this boundary. It does not change P, the requested D(P), the scalar chronology,
the set of paid occurrences or the endpoint of a public role. In particular,
one cannot substitute a complete basis of the larger raw frame when the
request is the nested difference P-Q. For the actual pair (2,270), that
difference has rank 3 and kernel dimension 5; the larger projector's kernel
has dimension only 4. The smaller image must remain in the difference kernel.

The chart adapters at the 111 coupled X/Y ports keep their original U_i.
They are not replaced independently by arbitrary equal-rank matchers. The
checked U_i and U_i inverse are dyadic, and their body-exchange routes are
dyadic as complete matrices. `PROOF.md` therefore preserves the common route
required at each off-diagonal scalar contact.

## `product.py`: complete substitution and suspended adapters

`compose(outer, inner)` starts one distinct outer callback for every inner
target and invokes it at `target * columns`. For each actual entry of
`outer.paid`, it resumes each callback once and checks the advertised request
length. It then calls `complete_order(axes, machine.n)` and rejects aliasing
owners before executing any inner word.

The added physical operation is `machine.move(owner, order, False)` on the
**whole** owner, followed by the complete inner callback, then the inverse
move. Since `complete_order` appends every unused coordinate, this is a full
permutation, not a minor. The outer Python generator is suspended across the
inner invocation. The outer normalizer remains active until that invocation
returns. Its `next(..., end)` exhaustion check prevents silently ignoring a
later paid occurrence.

No entry of `compose` computes a new rational pivot, selects a square minor,
or adds independent invertible matrices. Target and paid ranks multiply;
the corresponding basis construction is a tensor product followed by a
permutation placing all image columns first. A local basis is extended by
identity on every exterior coordinate before its complete placement.

`specialize` iterates this exact composition, keeps all labelled target paths
of the requested type and supplies distinct zero fields for all other paths.
It retains every source paid position. A zero field receives no productive
credit, and the code retires discarded public roles only after the source
word has returned. Its internal private erasure still uses the separate
owned-erasure contract.

At a paid boundary, `axes[start:start + cutoff * columns]` takes consecutive
pieces of the normalized image-coordinate list. The source callback stays
suspended while **all** those slices run. If B is the existing complete
basis and J is the selected ordered subset, then B times the column
permutation putting J first is a complete child basis. Its kernel includes
the unselected image columns and the old kernel. No extra inverse of a
rectangular submatrix is required. Returning each child before continuing
the next slice preserves the original outer adapters.

## `schedule.py`: completion adds only full permutations and splits

`complete_order` rejects repeated or out-of-range active coordinates and
returns the active list followed by every unused ambient coordinate. Its
matrix has determinant +1 or -1 over every ring. The author's literal-source
tests include empty, complete and reversed non-prefix active lists, along
with the repeated-coordinate failure control.

`expand` forms every placement using that complete order, applies the move,
and keeps it active across recursively completed native requests. Each
`satisfy` call checks common rank and distinct owners. Child axes are supplied
by a suspended callback and have the exact stated `paid * columns` length.
When a child completes, its route is undone before the callback advances.
The leftover axes are ordinary coordinate rank-one requests. A completed
root tile is returned before the next tile starts. The small-ambient branch
uses individual coordinate requests on the one complete owner.

These instructions introduce only complete placements, identity extensions
and image subsets of a previously carried complete basis. The depth proof
and funding argument for those finite callbacks belong to #7828 and #8092;
this audit checks their additional arithmetic operations. It does not obtain
the depth/funding theorem by finite execution.

## Explicit embedding and route boundaries

The restricted-sector expression in `APPLICATION.md` is precisely

    L_E(S) = S tensor E + I tensor (I-E),  E^2 = E.

It is not an arbitrary sum of two invertible matrices. Since the two sector
idempotents annihilate each other, L_E(S)L_E(T)=L_E(ST), with inverse
L_E(S^-1). A carried basis of E makes it a shuffled direct sum of copies of
S and identities. Conjugating by another carried basis preserves the same
localization. The independent reviewer checks a nonorthogonal E and rejects
the proposed inverse when E is not idempotent.

#7840 Section 4 permits full GL elimination with **q-unit** pivots and paid
ordinary swaps. This is essential: its physical route is stronger than the
lower / partial-permutation / lower ordered-shear route studied in #6201.
The determinant-one matrix [[1,3],[0,1]] is a concrete obstruction to that
restricted route over Z/9, while the full GL route succeeds. This supplement
does not relax the #6201 northeast-rank-profile criterion.

After q is chosen, a q-dependent elimination may use coefficients outside
Z[1/2] whose denominators are nevertheless units at q. The dyadic assertion
concerns the **fixed pre-cover projectors, complete bases, matchers and their
inverses**. It is not an assertion that every scalar appearing in that later
q-dependent factorization is dyadic. Both factorization directions and their
full low/high-column work retain the original charges.

## Conclusion and limits

Every additional matrix operation in the retained binary compiler syntax is
covered by complete-basis conjugation, direct sum, tensor product, coordinate
permutation, image split or the explicit idempotent-sector embedding. The
boundary choices can therefore be made over Z[1/2] and carried through every
finite generated word. This is a structural induction on the literal syntax,
not an extrapolation from tested primes or small completed words.

For any odd q, every fixed complete basis and matcher has an inverse after
reduction modulo q^w for all w>=1. The large-prime requirement
q > 2^45 N^5 still uses the **actual final compiler ambient N**, not the raw
134-axis caller or a previous carrier. The growing outer fine-prime choice,
complete ownership/erasure and all tape prices remain separate premises.

Reviewed with substantial OpenAI assistance for Jerry Chen / @CubeJerry.
Ali Romman's #7828 and the credited #7840 native specialization supply the
source interfaces; Nick Petalas's #6201 supplies the ordered-route boundary.
This is separate model-assisted review, not external human or kernel review.
