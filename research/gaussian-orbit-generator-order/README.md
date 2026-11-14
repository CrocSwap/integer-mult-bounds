# Orbit orderings with superpolynomial Gaussian tensor generator savings

**No new kappa. An all-size representation upper bound and scoped audit;
no fast transform, all-order optimum or foundational assumption discharge.**

The lexicographic Gaussian tensor obstruction does not extend unchanged to
arbitrary coordinate orderings. This package constructs two orbit orders
whose ordinary Stein displacement is supported only at cycle boundaries.
The stronger family uses disjoint prime-length rotations: it handles any
identical factor, including common shifted Gaussian factors and odd local
dimensions, and gives a superpolynomial-in-d saving in the certified generator
count over lexicographic order for every fixed local dimension. Generator,
transport and precision costs still prevent a runtime claim.

## Prime-rotation result

Let `H=B^tensor d`, with any n-by-n B and n>=2, and let distinct odd primes
`p_1,...,p_k` have sum at most d. Rotate the disjoint coordinate blocks of
those lengths simultaneously. With `T=n^d`, `P=product p_i`, its exact number
of cycles is

\[
 c={T\over P}\prod_i\bigl(1+(p_i-1)n^{1-p_i}\bigr)
       \le e^{8/9}{T\over P}.
\]

Concatenating those cycles gives ordinary Stein rank and explicit ordinary
Toeplitz generator count at most `2c` for H, and for its inverse when it
exists. Different cycle lengths are allowed. Equal factors within each
block suffice; an arbitrary spectator matrix is allowed. No reversal
symmetry or diagonal conversion is needed for already matched factors.
Here `E(X)=X-ZXZ^T`, with Z the ordinary strict lower shift in the stated order.

For d>=8, choose `k=floor(log_2 d)-2` and a Bertrand prime
`2^i<p_i<2^(i+1)` for each i. They fit within d coordinates and give

\[
       \operatorname{rank}E(H_{\rm ordered}),\quad
       \operatorname{rank}E(H_{\rm ordered}^{-1})
          <2e^{8/9}T\,2^{-k(k+1)/2}.
\]

For identical shifted Gaussian factors `B_ij=q^((i-j)^2)v^(i-j)`,
`0<q<1`, `v>0`, the lexicographic minimum is `2T/n`. The certified improvement
factor is at least `P/(e^(8/9)n)`, which grows faster than every fixed power
of d when n is fixed. The rank bound itself remains unbounded in T.
[PRIME-ORBITS.md](PRIME-ORBITS.md) proves the exact cycles, correction constant,
prime family, direct shift scope and full limitations. Prime selection is
not optimized and small instances can favor the next construction.

## Complemented-rotation result

Let `B_ij=q^((i-j)^2)`, `0<q<1`, with even `n>=2`. Set `H=B^tensor d`,
`T=n^d`, and let ell be the largest power of two at most d. There is an
explicit simultaneous row/column permutation P such that, for the ordinary
strict lower shift Z,

\[
 \operatorname{rank}(PHP^{\mathsf T}-ZPHP^{\mathsf T}Z^{\mathsf T})
 \le {T\over\ell},\qquad
 \operatorname{rank}(PH^{-1}P^{\mathsf T}-ZPH^{-1}P^{\mathsf T}Z^{\mathsf T})
 \le {T\over\ell}.
\]

Each ordered matrix has an explicit sum of at most `T/ell` products of an
ordinary lower and an ordinary upper triangular Toeplitz matrix. The
lexicographic minimum is exactly `2T/n`, so the new certified bound improves
on it whenever `2ell>n`, by factor at least `2ell/n`. This factor is
unbounded when `d/n` grows. It does not mean the new rank is bounded in T.

The more general statement needs only ell equal centrosymmetric factors of
even dimension; any square spectator matrix is allowed. Invertibility is
needed only for the inverse target. A common structure-preserving rounded
factor table also satisfies the forward theorem, and the inverse theorem if
its nonsingularity is separately established.

The ordering concatenates orbits of the permutation
`(x_1,...,x_ell) -> (x_2,...,x_ell,n-1-x_1)`. All orbits have size `2ell`.
The kernel is invariant under this permutation, so its ordinary displacement
vanishes off the `T/(2ell)` orbit-start rows and columns. This supplies the
bound and explicit generators without a numerical rank factorization.

For the 16-point Hamming kernel (n=2,d=4), an explicit order is

```
0, 1, 3, 7, 15, 14, 12, 8,  2, 5, 11, 6, 13, 10, 4, 9
```

At q=1/2 its forward and inverse ranks are exactly 4 by rational elimination;
the lexicographic value is 16. The upper bound 4 holds for every `0<q<1`.
[PROOF.md](PROOF.md) gives the full support argument and exact scope.

## Why this remains a representation result

The complemented-rotation generators contain `T^2/ell` scalar slots when
written out; the prime-rotation family contains `Theta(T^2/P)`. For fixed n,
both materializations eventually exceed the arithmetic work of direct
axis-by-axis dense application. An explicit orbit list also requires
generation, movement and inverse movement; both proofs provide conservative
uniform tape enumeration/sorting accounts instead of assuming random access
or a free permutation.

Unmatched shifts within a block can be removed algebraically using
`H_v = D H_1 D^-1`, but
`log cond_2(D)=sum_i (n_i-1)|log v_i|`. Conjugating back can demand that
many additional normwise precision bits. The proof isolates a fixed-shift
regime where simultaneously beating the lexicographic count and keeping a
linear-in-p black-box precision bill is impossible when `n~p^xi`, `xi>1/2`.
This is a scoped obstruction for that diagonal conversion; it is not an
impossibility result for stable algorithms or all source blocks. The prime
family directly preserves already matched shifted factors and does not need
that conversion. Actual source gauges and layouts still require separate
admission.

No full three-transform recovery recurrence is improved. Source access,
helper work, gauges, frames, restoration, recursive children, ownership and
actual native lowering remain separate obligations. The selected #7000
kappa remains `363005817/100000000000`, conditional on all five assumptions.

## Source binding and predecessor relationship

Base: `e54523517d0f03e58352e647c403a5af3e525a57`.
[SOURCES.json](SOURCES.json) records exact canonical Git blobs and SHA256
digests. They are historical provenance, not runtime inputs. The retained
normalized kernel and its smaller chirp-only gauge are in
`research/capped-fusion-t74-k554/outer/GAUGEFREE-INTERIORS.md`; the ordinary
generator method is in `research/capped-phase-fusion/SHALLOW-TOEPLITZ.md`.
Sufficiently large exactly matched blocks are an explicit hypothesis here,
not a newly proved property of every physical Reference. Centrosymmetry and
even dimension are needed only for the complemented-rotation family.

This answers part of the arbitrary-coordinate-order question left by the
[lexicographic rank package at 326844a](https://github.com/CubeJerry/integer-mult-bounds/tree/326844a3e0c570fdafa4f3737095cd37154743a6/research/tensor-gaussian-displacement-rank)
and the [rounding-margin package at 575491d](https://github.com/CubeJerry/integer-mult-bounds/tree/575491d5fc353eac26010e45e9ced60fc9870017/research/gaussian-generator-rounding-margin).
It changes the ordinary shift by reordering, so it does not contradict their
fixed-order exact or robust lower bounds. Those packages are credited but
not external replay dependencies; the required algebra is restated here.

Classical credit is essential. The complemented rotation and binary equal
orbit lengths appear in Gregor, Merino and Mütze,
[*The Hamilton Compression of Highly Symmetric Graphs*](https://doi.org/10.1007/s00026-023-00674-y),
section 3.3, equation (13), Lemma 3.4. We do not claim that automorphism as
new. Ordinary displacement/generator representations are also classical.
The contribution is their explicit combination and extended kernel scope
for this repository question, together with exact controls and the complete
limits of the proposed use. Bounded metadata, predecessor and primary
literature checks found no matching package; they do not prove global priority.

The stronger prime family uses classical necklace counting, coprime cyclic
products and the Bertrand--Chebyshev theorem. Primary credits include
[Moreau (1872)](https://www.numdam.org/item/NAM_1872_2_11__309_0/) and
[Erdős (1932)](https://www.renyi.hu/~p_erdos/1932-01.pdf).
The explicit rank consequence and its cost/scope analysis are the repository
contribution; prime existence is not a new foundational assumption.

## Reproduce

From the repository root:

```sh
python3 -I -W error -B research/gaussian-orbit-generator-order/verify.py
python3 -I -O -W error -B research/gaussian-orbit-generator-order/verify.py
python3 -I -W error -B research/gaussian-orbit-generator-order/prime_verify.py
python3 -I -O -W error -B research/gaussian-orbit-generator-order/prime_verify.py
python3 scripts/research_package.py --package research/gaussian-orbit-generator-order --check-only
python3 scripts/research_package.py --package research/gaussian-orbit-generator-order
```

The standalone commands use only the Python standard library, print JSON
and do not write files. Normal and optimized runs were executed on Python 3.12.14 and returned
identical `status: PASS` records. VERIFY.json registers all four runs and the repository's
Python 3.12 generic environment. Parent publication checks record the actual
registered replay result separately; source-history checks require their
stated Git history and are not inferred from a shallow checkout.

The original verifier covers 15 exact rational fixtures and both forward
and inverse targets: binary factors with q=1/2 and d=1--6; d=4 with q=2/3
and 4/5; n=4 with d=1--3; n=6,d=2; an invertible nonsymmetric centrosymmetric
factor; a nonsymmetric spectator; and one common four-bit rounded table.
Orbit powers are checked by a separate signed-index formula, kernel entries
by both tensor products and direct coordinate products, and small inverses
by full rational elimination. All 30 support decompositions and 22 literal
triangular Toeplitz reconstructions are checked.

Eight failure controls cover odd n, nonpower ell, unequal q, ungauged shifts,
reversed gauge orientation, an unstructured perturbation, a singular inverse
and a forged rank claim. They raise explicit exceptions under optimized
Python as well. The exact paid gauge identity is checked separately. These
finite checks support the written all-size proof; no finite search is used
to infer a universal minimum or an impossibility.

The prime verifier adds nine literal cycle fixtures, independently compared
with Burnside sums and the product formula; six rational fixtures with both
targets and 12 literal reconstructions; and a 256-point two-prime fixture
over the field 1000003 with a full dense inverse residual. It covers common
shifted factors, odd n, nonsymmetric matrices, spectators and an asymmetric
rounded table. Seven additional controls detect repeated primes, composite
periods, n=1, unequal q or shift inside a block, a false correction constant
and a false equal-cycle assertion. Ten finite Bertrand families through
d=4096 check the formulas; the universal statement is the cited theorem.

## Open next questions

1. Can the orbit-boundary generators be applied or generated implicitly in
   near-linear work, with all source access and fixed-tape movement charged?
   Start with the displayed start-row/column formulas. Writing the full
   vectors already incurs `Theta(T^2/P)` scalar slots for the prime family.
2. Does an actual source consumer admit large exactly matched factor blocks
   in a stable frame, with its exact phases, gaps, tails and physical data
   layout? First pin one block and retain its gauge condition number. The
   theorem does not establish that caller premise.
3. What is the minimum ordinary displacement rank over all simultaneous
   coordinate orders for the Hamming kernel as d grows? The present order
   gives an upper bound; neither an unbounded lower bound nor a bounded-rank
   construction has been established.

The precise task scope, stopping rule and structured handoffs are in
[TASK.json](TASK.json).

## Credit

Prepared for @CubeJerry with substantial OpenAI ChatGPT assistance. The
orchestrator proposed the orbit-order application, its even-n/spectator and
prime-block extensions, and the fixed-shift precision obstruction; the research worker
independently proved and checked the support, inverse, generator and cost
statements, found the classical overlap, and packaged the result. Credit
Gregor, Merino and Mütze for complemented rotation and the classical necklace
and Bertrand sources for the prime family. Retain the originating
repository authors' credit, including Vlado Vojdanovski's capped-phase-fusion
work and the cited predecessor packages. New files are Apache-2.0.
