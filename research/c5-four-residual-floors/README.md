# Sharp asymmetric cost 20 on the four remaining physical C5s

Every finite strict-scalar decomposition on each of the four cores below has
complete-plane binary pairing cost at least **20**, and five explicit terms
attain 20. Factors may be asymmetric, with arbitrary rational, real or complex
coefficients; signs, denominators and term count are unrestricted. Transpose is
ordinary transpose, not conjugate transpose.

These are the four residuals of [PR3268](https://github.com/CrocSwap/integer-mult-bounds/pull/3268)
after [PR3271](https://github.com/CrocSwap/integer-mult-bounds/pull/3271) settled
`(10,12,23,35,16)`. That already-covered core is excluded. The new step replaces
the predecessor's fixed cover with physical covers on ten identity blocks and
57 exact rational separation certificates after imposing equality traces.
This is a local obstruction, not a new supplier or kappa.

**Concurrent work.** While this package was being checked, Nick Petalas's
[PR3279](https://github.com/CrocSwap/integer-mult-bounds/pull/3279), head
`67c1360a7a6e81bcac515c698d56656454340b10`, independently published the same
four-core conclusion using finite-state count closure. Its claim and ours are
concurrent; no priority or exclusive novelty is claimed here. This package's
distinct contribution is an explicit rational separation certificate for each
trace class. It excludes even real nonnegative term multiplicities in those
classes and requires no count-state search or reachability implementation.

## Model and finite inputs

The two pinned canonical-main inputs in [SOURCES.json](SOURCES.json) give
112 scalar ports and their partition into 56 two-port planes in F2^9. In each
listed cycle, adjacent planes pair to zero and nonadjacent planes pair nonzero;
each plane has binary Gram matrix I2. Both checkers reconstruct these properties.

A strict scalar fitting matrix K has ten coordinates, two per plane. Its
diagonal is one; off-diagonal entries within planes and every cross entry
between nonadjacent planes are zero. Entries between adjacent planes are free.
For any finite exact decomposition `K = sum_t u_t v_t^T`, discard zero factors
and let A_t and B_t be the five-bit plane-support masks. Its term cost is

```
c(A,B) = rank_F2(pairing of all complete plane labels in A against those in B).
```

Touching either scalar coordinate charges both labels of its plane. This is the
inherited PR2782 tariff, not the scalar rank or the number of terms. The proof
allows nonzero factors with cost zero and does not bound their number.

## Proof

Use these ten forced identity blocks, in this fixed order:

```
H = ({0},{1},{2},{3},{4},{0,2},{0,3},{1,3},{1,4},{2,4})
r = (2,2,2,2,2,4,4,4,4,4).
```

For a support pair define `h_j(A,B)=1` if both A and B meet H_j, else zero.
The restriction of a term to H_j is a nonzero rank-one matrix exactly when
`h_j=1`. Thus its count `n_j=sum_t h_j(A_t,B_t)` is at least r_j, because the
sum of those restrictions is I_(r_j).

**Physical cover.** All 1,024 ordered support pairs on each core satisfy
`d(A,B)=s*c(A,B)-w.h(A,B) >= 0`, using the following integer data:

| Core in cyclic order | s | w, in the block order above | w.r | Cases |
| --- | ---: | --- | ---: | ---: |
| (3,10,4,6,13) | 3 | (2,4,1,2,3,2,1,2,0,3) | 56 | 3 |
| (3,10,12,23,13) | 3 | (2,3,1,2,2,2,1,2,1,3) | 56 | 4 |
| (6,13,23,54,26) | 2 | (2,1,1,1,1,1,1,1,2,1) | 36 | 47 |
| (14,24,47,18,55) | 3 | (1,4,2,3,2,2,3,0,2,1) | 56 | 3 |

These are statements about the actual binary pairing matrices; graph
isomorphism is not used to transfer a tariff.

Suppose for contradiction that the total integer cost C is at most 19.
For positive w_j set `e_j=n_j-r_j`. For zero w_j put e_j=0 as a placeholder:
its actual n_j is still only bounded below by r_j. Summing the cover gives

```
w.e + sum_t d(A_t,B_t) = s*C - w.r <= s*19 - w.r.
```

The right side is respectively 1,1,2,1. Consequently the 3,4,47,3 nonnegative
integer excess vectors in [CERTIFICATE.json](CERTIFICATE.json) exhaust every
possibility. The checker enumerates them independently of that list and
rejects either an omitted or repeated case. This also covers C=18 or lower;
it does not assume C equals 19.

**Equality traces.** If exactly r rank-one matrices sum to I_r, write the
square factor matrices as U,V. `UV^T=I_r` implies `V^TU=I_r`, so each term's
trace is one. For a fixed term put `z_i=u_(t,i)^T v_(t,i)`, on the two scalar
coordinates of plane i. Whenever `w_j>0` and `e_j=0`, the term must satisfy

```
sum_(i in H_j) z_i = h_j(A_t,B_t).
```

Also z_i=0 outside A_t intersect B_t. These rational linear equations are
necessary over each of Q, R and C. They need not be sufficient for a fitting
factorization. The primary checker uses Fraction elimination; the separate
checker uses signed affine propagation on the pair-equation graph, including
odd-cycle constraints and singleton anchors.

For an excess case let `T=r+e` and `b=s*19-w.T`. A term in the hypothetical
decomposition must have `d<=b` and a consistent trace system. This includes
every zero-cost term; no term-count truncation or removal is needed.

**Exact separation.** Each case stores integers p and q>0 satisfying:

1. `p.h(A,B) <= q*c(A,B)` for every support pair surviving those two filters;
2. p_j>=0 wherever w_j=0;
3. `p.T >= 20*q`.

Summing (1) over all actual terms gives `q*C >= p.n`. For positive w_j,
`n_j=T_j` exactly, so negative p_j are permitted. For zero w_j, condition (2)
and `n_j>=r_j=T_j` give `p.n>=p.T`. Condition (3) therefore implies C>=20,
contradicting C<=19. Every coefficient and inequality is checked as an integer;
there is no numerical tolerance, LP solver or coefficient search in acceptance.

This proves the lower bound for arbitrary finite decompositions. The proof
uses the ordinary-transpose identity lemma above, rather than positivity or
an assumption that factors have equal supports.

For each fixed excess case, the same separation also rules out a fractional
count model: assign arbitrary nonnegative real multiplicities to the admitted
support pairs, impose the exact positive-weight block totals T and the other
block lower bounds r, and require cost at most 19. Conditions (1)--(3) make
that linear system infeasible. Integrality is used to enumerate excess cases,
but is not needed for the contradiction within a case.

**Attainment.** For i=0,...,4 let w_i have ones at scalar coordinates
`2*i+1` and `2*((i+1) mod 5)`, and zeros elsewhere. Then `sum_i w_i w_i^T`
is a strict fit: each coordinate appears once and the only nonzero cross
entries join adjacent planes. Each term touches two adjacent complete planes,
whose binary pairing is I4, so its cost is 4. Five terms give total cost 20.
Both checkers evaluate the whole 10-by-10 fit and the five separate tariffs.

## Reproduce and evidence

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/c5-four-residual-floors
```

The replay checks 4,096 physical tariffs, all 57 excess cases and 14,045
admissible-term separating inequalities. It also runs a separate dense binary
and affine-graph reconstruction and behavioral rejection controls. Direct
scripts need only this package and its two pinned input files; no pending PR
executable, Git object, network or third-party dependency is needed.

Exploration used SciPy 1.16.2/HiGHS to propose covers and separators, then
rationalized them. The committed certificates, rather than solver infeasibility
reports, are the evidence. See [CHECKS.json](CHECKS.json) for the actual replay
environment and checks. This is written mathematics with exact finite premises,
not proof-kernel formalization or independent human review.

## Scope and coordination

The scientific base is main `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority
revision 6. The original `coverage-law-change` card is explicitly changed to
this local residual obstruction, following the open handoff in
[#1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19003538).
The card's ceiling positive control passed; it supplies context, not a new bound.
The [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19003766)
records the method and overlap boundary. Existing pending results retain their
own evidence status; this package does not revalidate all of them.

Family decision: stop after this local proof. No general 112-port decoder floor,
native construction, dirty restoration, hosting/precision invoice, supplier
admission, all-size multiplication theorem or new kappa is claimed. In
particular, overlapping local C5 inequalities cannot simply be summed into a
global floor. The selected record and frozen predecessors remain unchanged.

## Open next questions

Can these local lower bounds contribute to a global decoder obstruction without
charging the same term repeatedly? This matters because local cost20 alone does
not supply the global 112-port bill. A feasible first step is to give an explicit
weighted family of physical cores and prove its termwise complete-plane charging
inequality. The blocker is that supports and costs can be shared across cores;
another seed or replay of the four settled tables does not address it. No new
construction/search round is reserved here.

## Credit

Prepared by **Krzysztof Wójt**, with substantial **OpenAI Codex** assistance,
including a separately assigned Luna finite-check implementation. Such agent
cross-checks are not independent human review. New work is Apache-2.0.

Credit **Nick Petalas / PR3268** (`ee5d4f466e6e44a1897896324a36aa4c64cf3912`)
for the residual inventory and physical-core extension, and **PR3271**
(`1bbe044ba2c7187dba149e40734179b2a1ebba84`) for the excluded fifth residual.
The weighted-rank/equality-trace method comes from **thakrarsagar / PR3256**
(`1ea98246dabb46fc7bedf6127eff63f008414a39`). Credit **Tekalign / PR2782**
for the physical inputs, complete-plane tariff and asymmetric handoff;
**Arham Tahir / PR2879** for the related principal-block method;
**Sagar Thakrar / PR2484**, **Cinna Davis / PR1825**, **Adam Gall / PR1889**,
**PR3232**, **Nick Petalas / PR3248**, **ctoth**, **Philippe Van Velzen**, and
the retained E8/P112 and selected-geometry lineage. No predecessor artifact is
modified or presented as newly discovered here.
The concurrent finite-state proof in **Nick Petalas / PR3279** retains its
independent contribution credit.
