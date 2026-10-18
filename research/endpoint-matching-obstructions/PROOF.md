# Endpoint matching and exact support certificates

This is a fixed-word obstruction in a formal complex group algebra. The
written argument and exact finite certificates are not a proof-assistant
formalization or a new integer-multiplication exponent.

## 1. The necessary endpoint matching

Let G be a group and let a word over C[G] consist of scalar invertible W by W
matrices B_k and diagonal matrices of group basis elements. Let S be its
final matrix. For each entry (i,j), specify a permitted set A_ij of group
elements. The endpoint requires every coefficient outside A_ij to vanish.

The augmentation epsilon(sum a_g[g])=sum a_g is an algebra homomorphism.
Every group diagonal augments to the identity, so

    epsilon(S) = B_L ... B_1,       det epsilon(S) != 0.

Consequently some permutation pi has every epsilon(S)_{i,pi(i)} nonzero.
For each such entry at least one permitted group coefficient is nonzero;
at least one path contributing to it then has nonzero scalar product.

Thus the bipartite graph of **active permitted paths** must have a perfect
matching. This is stronger than checking the graph of all syntactically
possible rank-three paths before any scalar entry is set to zero. It remains
only necessary: multiple active paths can cancel, and a matching alone does
not establish invertibility or an endpoint.

No positivity, unitarity, bound on coefficients or numerical conditioning is
used. The lemma applies to arbitrary invertible scalar matrices over a field
and arbitrary permitted entry sets. We make no priority claim for this
elementary augmentation/Hall argument.

## 2. The Boolean relaxation

For the supplied W=3 words, a Boolean variable represents each scalar entry
being nonzero. A path variable is equivalent to the conjunction of its entry
variables. There is exactly one chosen full-rank frame per input column.

Necessary clauses require:

- Each scalar block has at least one active determinant monomial.
- A forbidden group coefficient never has exactly one active path monomial.
- Some endpoint permutation has an active permitted path in each matched
  entry, conditional on the selected column frames.

All paths and group coefficient classes are reconstructed. A successful
complex word would supply a model of these clauses. In particular, a SAT
model is not a circuit: cancellation and nonsingularity still need algebra.

For a frame triple excluded by PR800's Laurent criterion, we may also add the
clause forbidding those three frame selectors together. Every such addition
is checked using the exact inequalities and cancellation equalities in the
retained [PR800 proof](PR800-PROOF.md), not a numerical LP outcome.

The five endpoint-matching-only certificates do not use Laurent exclusions.
`evolved-11` uses matching plus Laurent exclusions. `evolved-24` and
`evolved-31` additionally require exact polynomial identities.

## 3. Polynomial identities and diagonal normalization

Fix the zero/nonzero entry support and the column frames of a Boolean model.
Form the off-target coefficient polynomials and, for every scalar block,
adjoin a variable z_k with equation z_k det(B_k)-1=0. Hence singular matrices
are excluded algebraically, not merely by the Boolean matching relaxation.

Make a layered graph with a vertex for each register at every scalar-block
boundary. Choose a forest of nonzero scalar-entry edges. Diagonal gauges
transform each block as D_k B_k D_{k-1}^{-1}. They commute with the intervening
group diagonals and rescale final entries by nonzero boundary scalars, so
they preserve all zero-coefficient endpoint conditions and invertibility.

Every chosen tree edge can be normalized to one: set a root gauge in each
component, and solve successively for neighboring vertex gauges. A forest
has no cycle constraints, and no extraction of roots is needed.

After this valid normalization, a supplied exact rational identity

    sum_l q_l f_l = 1

contradicts simultaneous vanishing of the constraint generators f_l. The
checker reconstructs the polynomials, checks forest acyclicity, and expands
the identity coefficient by coefficient using rational arithmetic. Search
timeouts and failure to obtain an identity are never used as exclusions.

The blocking clause may use fewer premises than the complete support model.
For every used generator, the checker verifies that every omitted monomial
has a certified zero entry, every used normalized tree edge is required
nonzero, and every off-target rank-three frame is required absent. Other
scalar entries may vanish. These checked premises suffice to reconstruct
the same identity, and their conjunction is therefore impossible.

## 4. Proof composition and independent replay

The finite search used clause learning. Its discovery algorithm is not
trusted by the public verifier. Each learned clause is accompanied by a
chain of propositional resolutions from earlier clauses. The checker uses
literal sets to replay every resolution pivot; the final clause is empty.
Algebraic blocking clauses are admitted only after the preceding checks.

The group model retains Pauli signs and quotients only central scalar phase.
The supplied generators have rational Gaussian entries and central phases
in {1,-1,i,-i}; the inherited intended tensor interpretation removes these
phases for multiplicities divisible by four. Full-rank endpoints are common
left monomial frames per input column. This is the formal model of PR680,
PR705 and PR800. Concrete 8 by 8 matrices check group equalities, frames and
ranks independently; their linear independence is never assumed.

## 5. Exact coverage and limits

The unchanged PR705 payload contains 73 literal words, each with eight paid
calls. Its retained rank-homogeneous checker excludes 64. PR800 already
excludes `evolved-27`. The new certificates exclude the other eight:

| Words | Additional certificate |
| --- | --- |
| evolved-01, 03, 05, 06, 14 | Active endpoint matching and Boolean resolution |
| evolved-11 | Matching, Laurent frame exclusions and Boolean resolution |
| evolved-24, 31 | Matching, Laurent exclusions, 67 polynomial identities and resolution |

All nine formerly heterogeneous words have four arbitrary invertible scalar
3 by 3 blocks. Their 2,187 full paths are reconstructed by both the signed
tableau and exact dense Gaussian engines. The package replays 490
frame-specific Laurent certificates and 5,342 resolution clauses.

This closes this fixed corpus, not all four-block words, every generator
family, or the general m=3, W=3, s=8 problem. Arbitrary nonunitary mixers and
different unary words remain an open search direction. No positive cheaper
primitive, improved kappa, all-size compiler, physical hosting, precision or
tape realization, or full multiplication theorem is supplied.
