# Source-bound free-operator tensor lift

This audit affirms one specific premise in PR4100's `COMPLEX.md`, lines 62–89:
the retained four PR4088 words cancel in a free group algebra before any
particular native operator is substituted. The premise is true for the exact
source exports checked here. This is a local algebra and source-binding result;
it supplies no new paid profile, numerical allowance, encoded implementation,
physical hosting theorem, outer release or selected-frontier improvement.

## Exact source and contract

The audited text is `research/unconditional-batched-crt/COMPLEX.md`, Git blob
`c3be56fbfdb4fb29c1ace88cbcdfa7475fb6e343`, SHA256
`853e1295850862752e4f854aa9e8b28f9ca6eaa9306e2af110b7b77526d1b5e1`.
It is identical at retained PR4100 head
`337d04939571a637aeab54a0f58f54fde811663a` and canonical main
`12fa8c5c844be21bfefb38a19503fbd867a11244`.

Its stated source is PR4088 head
`72d7efc181edb21806a878f174847c96dd410ab0`, package
`research/staged544-mixed-fourth-entry`. This audit exports the exact four
`inputs/{THREE,FOUR}-{base,extra}.json.gz` files, retained `vendor/audit_core.py`,
`vendor/audit_verify.py`, source `verify.py`, `PROOF.md` and `NOTICE.md`.
`SOURCE-PINS.json` records every original commit, path, length, Git blob and
SHA256. Every file is authenticated before the retained checker is executed.
No native runner, owner fill, solver, NumPy or historical outer engine is run.

Each word has 632 live registers, 91 arbitrary dirty private registers,
72 abstract unary generators and 36 listed initial correction terms. The
forward common-label contract on the 723-register direct sum is

`(x,y,h,b) -> (x,y+x,h,b)`.

The dual contract is `(x,y,h,b) -> (x-y,y,h,b)`. In particular every private
buffer is an independent input, returns identically, and has no leakage into
live outputs. Neither contract assumes zero private inputs or a product state.

## What the retained checker actually computes

In `audit_core.py`, lines 297–391, a register value is a sparse dictionary

`(initial_input, reduced_signed_operator_word) -> Fraction`.

`program` includes every declared initial correction, precondition,
compensation, A and cut gate, chronologically inserted B warp, B gate,
restoration and cleanup gate. `_left` and `_right` cancel only adjacent inverse
letters; `_axpy` adds exact rational coefficients and removes exact zeros.
There is no commutation, finite-order relation, numerical operator matrix,
Fourier-character evaluation or univariate minimal-polynomial reduction.

`audit_verify.semantics` runs all 723 independent symbols forward and dual,
compares an independent direction of pullback, and checks both cleanup-boundary
contracts. Every emitted provider passes. Each endpoint consists of exactly
835 nonzero terms: the 723 diagonal terms and 112 intended shear terms. Every
surviving operator word is empty.

That is a universal algebraic identity, rather than an identity inferred from
one operator realization. The source's use of the word “symbolic” is justified
by these actual data structures, reductions and endpoint predicates.

## All positive tensor multiplicities

Let `F` be the free group on symbols `g_1,...,g_72`, and let `A=Q[F]` be its
rational group algebra. The finite word program is a product of elementary
723-by-723 matrices over `A`. A correction `c*g_word*x_source` is an off-diagonal
entry of one such elementary matrix. Scalar ADD and SCALE entries belong to
`Q*1_A`.

Let `K` be any characteristic-zero field (in particular `Q[i]`) and let `V`
be any finite-dimensional vector space over `K`. Choose arbitrary invertible `K`-linear operators
`G_k` on `V`. All tensor products below are over `K`. For every positive integer `f`, define

`rho_f(g_k) = G_k tensor ... tensor G_k` (f factors).

The assignment of free generators extends uniquely to a group homomorphism
`F -> GL(V tensor f)`: inverses map to tensor products of inverses, and

`(G H) tensor f = (G tensor f)(H tensor f)`.

Extend this map rationally from `A` into the `K`-linear endomorphisms of
`V tensor f`. This extension is a unital rational algebra
homomorphism because multiplication of finite formal sums distributes and
because the group map preserves products. In particular

`rho_f(sum_w c_w*w) = sum_w c_w*rho_f(w)`.

Apply this homomorphism entrywise to the certified elementary-matrix product.
It preserves each elementary action, the order of events and the product.
Since the certified endpoint has only rational multiples of empty words, its
image is exactly the same register-level shear with each scalar multiplied
by the identity of `V tensor f`. This proves the endpoint for every positive
`f` and every input in the 723-register direct sum of `V tensor f`, including
arbitrarily correlated live/private data.

The number of register roles remains 723. We are changing the internal space
of each role; we are not taking a tensor power of the 723-by-723 register matrix.
The latter operation would create a different program with 723^f roles.

The dual pass treats `d_k=G_k^(-T)` as separate free generators. The same
argument applies, and `(G_k^(-T)) tensor f = (G_k tensor f)^(-T)` in the product
basis. Native frame labels can be replaced by their tensor powers if the
separately supplied directed native recipe identities are exact. This audit
does not reprove or rerun those native recipe identities.

## The distinction that must be retained

This algebra homomorphism is linear on formal sums. Therefore

`rho_f(g-I) = G tensor f - I`,

not `(G-I) tensor f`. Likewise `rho_f(c*g)=c*(G tensor f)`, not
`(c*G) tensor f = c^f*(G tensor f)`. A role SCALE or bridge coefficient must
remain scalar, while a constant phase already inside a unary generator is
part of that generator and therefore occurs in every tensor factor.

For an exact small counterexample, take `G=[[1,1],[0,1]]` and `f=2`.
Then `(G tensor G-I)` sends `e_2 tensor e_2` to
`e_1 tensor e_1 + e_1 tensor e_2 + e_2 tensor e_1`; whereas
`(G-I) tensor (G-I)` sends it only to `e_1 tensor e_1`. Their difference is
nonzero over `Q` (and over the supplemental field F101).
The code checks a distinct noncommuting 72-generator family as well, and rejects
both the whole-difference and whole-scalar tensorization rules.

## Independent evidence and its scope

`independent.py` imports or executes no retained implementation. It reconstructs
the literal sequence from the four exported words and, for each of the 723
outputs separately, pulls the output functional backward through that sequence
over exact `Q[F_72]`. The reverse traversal appends words on the right; a stack
reduces only adjacent inverse letters. All four forward and all four dual
contracts match exactly: 5784 output-functional checks, 6680 endpoint terms and
zero surviving nonempty words. Its controls preserve a nontrivial commutator,
a fourth power and the two distinct terms of `g-I`.

This implementation is independent of the source engine; the format and
endpoint contract were read from the same credited source. Agreement is
supplemental to inspection of the finite exact computations, not a substitute
for proving what the reductions mean.

`verify.py` also reconstructs and executes the literal events directly on dense
vectors over F101, with 72 distinct invertible 2-by-2 matrices. The first two do
not commute. It substitutes their tensor powers at `f=1,2,3` in both orientations
of all four providers, yielding 24 direct fixtures; all 723 registers are given
deterministic dirty values. These finite-field experiments are controls, not
the proof for every rational input or unbounded f. Erasing the actual listed
correction generators fails at 20 registers; tensorizing the actual role SCALE
coefficients fails at the reported registers. Exact inverse and product
compatibility controls also pass.

## Remaining obligations and credit

This positive result discharges only the source's formal free-operator premise
and its algebraic implication to per-role tensor multiplicity. The physical
lowering of native monomials, directed native recipes, placement, common cover,
hosted slices, analytic bounds, coefficient precision, fixed-tape inventory,
recovery and complete ordinary/outer release are outside this audit. The source
construction makes additional written claims about these interfaces; this audit
neither verifies nor refutes those claims.
No paid-rank saving, all-size multiplication theorem, independent human
acceptance or new kappa is claimed.

The tensor-lift proposal and current construction are credited to Cinna Davis,
the PR4100 author; this audit does not claim to invent the representation argument.
Cinna Davis's PR4088 supplies the four literal providers and source integration.
Sagar Thakrar's PR3687 exact free-operator engine and roger-sato's PR3693
all-dirty/reverse audit are reused explicitly. Retained lineage includes Rohan
Arun/PR4076, Dugongue/David Ganz/PR4085 and PR3945, Nick Petalas, Ross
Richardson/PR3605, dataisfire/PR3734, ChaloupeMusic/Erwan Secousses, Marius-Paul
Dumitrean, zxv and the earlier geometry/native/compiler/owner contributors.
The byte-identical source notice and source-file notices remain in `source/`.

The formal and F101 implementations were separately written by one Codex agent. A second Codex agent independently reviewed them and supplied the exact rational signed-permutation oracle in `independent_real.py`; see `INDEPENDENT-REVIEW.md`. None is a human or formal-kernel acceptance.

`mutation_controls.py` also produces exact actual-program counterexamples in `MUTATIONS.json`: erasing the first correction generator yields `(I-G59)x273` in output115; dropping the first nonidentity scale yields `-3*x119` in output119. Both baseline output functionals pass first. Every actual correction word has length one, so a multi-letter correction reorder is inapplicable rather than counted as an executed control.
