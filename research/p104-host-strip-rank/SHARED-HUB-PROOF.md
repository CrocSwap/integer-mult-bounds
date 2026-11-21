# Caller strip and shared-role rank review

Status: independent mathematical review and exact bounded controls. The new
arguments below are **not kernel-checked**. They are statements about the
signed-frame and role/piece models, not a proof that the test profiles are
legal caller words and not a kappa or invoice improvement. All upstream
references use #7852 head `41beda1d6435760dc99e38bd7e65f36798aad212`.

## Check of the e=1 strip argument

The #10 argument in `10-extra-thins/RESULT.md` is correct under its stated
nondegenerate host-block and signed-frame assumptions. Write `H` for a host
principal submatrix of `K`, and let

```
d_s = 2 - rank H[s, all hosts except s].
```

For each t, null combinations for all s different from t produce rows
supported on their own s-blocks. The nondegenerate diagonal blocks make them
independent. Together with the two t-rows, they give
`2 + sum_(s != t) d_s <= rank H <= 2+e`. Consequently `k >= e+2`
forces at least one zero deficiency and `sum d_s <= e`. The stated pair-block
bound follows by a Schur complement. The #10 set-RC2 consequence counts
**stage/role incidences** with singleton pieces; it is not automatically a
count of distinct priced events.

A slightly more general projection statement also follows. For *any* set J
of host stages,

```
rank H[J,J] + sum_(s outside J) d_s <= rank H.                 (1)
```

Take row combinations of the J rows whose projections to J form a basis for
`H[J,J]`; adjoin the independent localized null combinations outside J.
Projection to J eliminates the latter; then their disjoint supports and
invertible diagonals prove independence. Thus if `k>=e+2` and
`sum d_s=e`, the principal block on all nondeficient stages has rank exactly
2. In particular, for e=1 with one deficient stage, every pair in the
remaining rank-2 core has an invertible Gram block. The exact host-only
control in `check.py` realizes deficiencies `(1,0,0)` and a rank-2 complement;
it does not purport to be a signed frame.

## The common-hub sign obstruction starts at three stages

Take distinct ordered hosts, each represented by two columns in one actual
stage, with invertible 2-by-2 diagonal blocks. Let `H` now denote the same
**two roles** that are the entire mask intersection for every pair of the
selected hosts. If their principal signed host matrix has rank at most 2, then
three selected stages are impossible when the field has characteristic other
than 2.

Indeed, diagonal invertibility forces rank exactly 2, and a rank factorization
gives blocks `K_ij=X_i Y_j` with all 2-by-2 `X_i,Y_i` invertible. The shared
roles give, for `i != j`,

```
K_ij = sgn(j-i) B_i,H^T A_j,H.
```

All these cross blocks are invertible, so the two hub factors are invertible.
After multiplying by their inverses write `D_i E_j=sgn(j-i) I`. For
`a<b<c`, columns b, a, c respectively give
`D_a=-D_c`, `D_b=D_c`, `D_a=D_b`, a contradiction. Thus the four-stage
obstruction supplied by #9 is valid but can be strengthened to three.

The sign and rank argument is unaffected by thin columns between host stages:
it uses a principal submatrix of the full signed `K` and the ordering of the
actual `beta` stage indices. A purported type-A regrouping still needs its own
bridge proving both selected columns have one `beta` and distinct hosts have
distinct `beta` values. `CallerCfgBridge.Host` explicitly has the corresponding
`hcolbeta` and `hpos` fields for its stated type-B host model; this review does
not assert a separate type-A bridge.

## General rank theorem and shared-rank budget

**Claim.** Over a field of characteristic not 2, take m distinct ordered
two-column host stages with invertible diagonal K blocks. Suppose that for
every pair of these stages the mask intersection is the same two-role set.
Then the selected host principal matrix has rank **at least m**.

**Proof.** Induct on m. The statement is immediate for one or two stages from
an invertible 2-by-2 diagonal. For a larger selected matrix, define row-strip
deficiencies *inside that selected matrix*, and analogously for columns. If a
stage has a deficient row strip, a nonzero row combination is supported only
on its own block and is nonzero there. It adds at least one to the rank of the
complementary principal matrix by projection; the induction hypothesis
applies to the remaining stages. A deficient column strip is symmetric.

Otherwise every local row and column strip has rank 2. Since every
off-diagonal block factors through the same two roles, every individual hub
factor `B_i,H^T` and `A_i,H` is invertible. Invertible block row and column
scalings transform every off-diagonal block to `sgn(j-i) I_2`; call the
arbitrary normalized diagonal of the earliest stage `D`.

For even `m=2h`, take the h odd-indexed stage rows and h even-indexed stage
columns. Their scalar sign matrix has entries `+1` on and above the diagonal
and `-1` below, determinant `2^(h-1)`, so the 2h-by-2h block is invertible.
For odd `m=2h+1`, separate the earliest stage and make this alternating
selection on the other 2h stages. The invertible pivot's Schur complement is
`D+I`. Reversing the alternating row/column choices instead gives the equally
invertible pivot and Schur complement `D-I`. If the whole rank were at most
2h, both complements would be zero, impossible because `2 != 0`. This proves
the claim. The local-strip qualification is essential: full strips over all
k hosts can have rank 2 even when a restricted strip does not.

### Packing consequence

Suppose two roles occur at every one of k host stages. Draw an undirected
edge between stages when some **other** role meets both. If the whole host K
matrix has rank at most `r`, the graph has no independent set of size
`r+1`: the claim would give the corresponding principal block rank at least
`r+1`. Equivalently its complement has no clique of size `r+1`. By Turan's
theorem, for `k=rq+t`, `0<=t<r`,

```
sum_(other roles u) binom(|mask(u)|,2)
  >= number of distinct nonhub edges
  >= t binom(q+1,2) + (r-t) binom(q,2).                    (2)
```

The first inequality permits repeated edges; it can be strict. In a signed
frame, `CallerSGram.sgForward` supplies `rank K <= |iota|-n = 2+e`, so
`r=2+e` is available when its exact hypotheses hold. With k=76 this demands
1,406 nonhub pair incidences at e=0, or 925 at e=1. The #9 configuration of
two global hubs, 73 degree-two nonhub roles and 76 leaves supplies only 73,
so it cannot realize its advertised tight signed frame. It remains a valid
arithmetic relaxation/control; this calculation does not price every other
legal configuration.

## Common-piece extension

The rank theorem also applies if the identical pairwise mask intersection is
a set `H` of size `h>=2`, provided there is a single `(h-2)`-dimensional
subspace `X` of role vectors supported in H annihilated by **every** selected
stage's `B_i,H^T`. Factor all those maps through the common quotient `H/X`,
which has dimension 2. The same local-strip induction works; in its full-strip
case the factored 2-by-2 hub maps are invertible, so the same sign-minor proof
applies. It is not enough to have different unrelated kernels at each stage.

For the #9 two-cluster profile, assume two universal hubs, two disjoint
38-stage roles, and degree-two remaining nonhub roles. If a cluster role has
one piece equal to its entire mask, `CallerRC2.Pieces.x_supp`, `x_ker`, and
`biorth` give a nonzero vector supported on the two hubs plus that role and
annihilated at all 38 stages. Thus an independent set of three within either
cluster contradicts rank 2 by the quotient version. Each cluster needs at
least `binom(38,2)-floor(38^2/4)=342` *internal* pair edges, or 684 between
the two clusters. The proposed 71 degree-two roles cannot supply them. The
simple graph in (2) counts the two cluster roles as edges and does not by
itself rule out that profile; the whole-piece kernel is essential to this
stronger check. At rank 3, the same reasoning with four selected stages gives
222 edges per cluster, 444 in total. These are necessary conditions under the
specified masks and full-mask pieces, not a general kappa bound.

## Independent exact checks

`python3 -I -B check.py > receipt.json` takes a few seconds and checks:

* Git blob IDs for the pinned `CallerSGram`, `CallerExtraThin` and
  `CallerRC2` sources.
* The sign pivots and odd Schur scalars for 2 through 17 stages; 4,900
  independently generated host matrices over F3 and F5; and a three-stage
  F2 counterexample to the characteristic assumption. These finite samples
  are controls, not exhaustive proofs of the rank theorem.
* Every graph on two through six vertices against the exact graph bound, and the
  cited k=76 / 38-stage numerical bounds.
* A two-stage, rank-2 fixed-J signed frame and the #10 agent's three-stage,
  rank-3 fixed-J signed frame. For the latter, the script separately rebuilds
  all seven role rows and four thin factors and checks `P=-I`, full and host
  ranks, masks, and all three host diagonals. A changed thin column fails the
  product check. These sharpness examples are not verifier-legal words.

The upstream frame, excess and piece definitions/lemmas are due to
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code, as credited
on #7852. The e=1 strip analysis and the two checked fixed-J frames are from
`/root/extra_thins`; the original four-stage and common-piece arguments and
profiles are from `/root/thin_window`. The three-stage strengthening, the
all-e rank induction and the graph consequence above were developed in this
independent review. No claim of novelty against the wider literature is made.

Sources: [CallerSGram](https://github.com/CrocSwap/integer-mult-bounds/blob/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/lean/Nov15/CallerSGram.lean),
[CallerExtraThin](https://github.com/CrocSwap/integer-mult-bounds/blob/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/lean/Nov15/CallerExtraThin.lean),
[CallerRC2](https://github.com/CrocSwap/integer-mult-bounds/blob/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/lean/Nov15/CallerRC2.lean),
and [CallerCfgBridge](https://github.com/CrocSwap/integer-mult-bounds/blob/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/lean/Nov15/CallerCfgBridge.lean).
