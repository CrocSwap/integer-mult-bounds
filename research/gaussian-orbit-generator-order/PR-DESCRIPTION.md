## What changed and why it matters

The preceding Gaussian tensor lower bounds fix lexicographic coordinate
order. This package constructs two arbitrary simultaneous row/column orders
with smaller ordinary Toeplitz generator bounds, and states the costs that
still prevent a runtime or unconditional-theorem claim.

The stronger family rotates disjoint blocks of distinct odd-prime lengths
p_i. For any repeated n-by-n factor B, n>=2, put T=n^d and P=product p_i.
The exact number of orbits is

`c=(T/P) product_i(1+(p_i-1)n^(1-p_i)) <= exp(8/9) T/P`.

Concatenating those orbits gives ordinary Stein rank and explicit ordinary
lower-times-upper Toeplitz generator count at most 2c, for both the forward
matrix and its inverse when it exists. Equality of factors within each block
suffices; arbitrary spectators are permitted. Common shifted factors, odd n
and nonsymmetric factors need no reversal symmetry or diagonal conversion.

For d>=8 choose k=floor(log2 d)-2 and Bertrand primes in (2^i,2^(i+1)). They
fit within d coordinates and have P>2^(k(k+1)/2). For identical Gaussian
factors the lexicographic minimum is 2T/n; the certified saving factor
P/(exp(8/9)n) grows faster than every fixed power of d for fixed n. This is
a representation saving, and the rank bound still grows with T.

The complementary even-n centrosymmetric construction uses complemented
rotation on ell power-of-two coordinates and gives the bound T/ell. Its
16-point binary example has exact forward/inverse rank 4 at q=1/2, versus
lexicographic rank 16. Either order may be preferable at a small parameter
point. Both proofs include explicit generators and inverse symmetry.

## Novelty and exact provenance

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`. SOURCES.json
contains six exact canonical Git-blob/SHA256 pins. The proof restates its
algebra, and the verifier has no external runtime inputs.

This addresses the arbitrary-coordinate-order question left by the
[rank package at 326844a](https://github.com/CubeJerry/integer-mult-bounds/tree/326844a3e0c570fdafa4f3737095cd37154743a6/research/tensor-gaussian-displacement-rank)
and [rounding-margin package at 575491d](https://github.com/CubeJerry/integer-mult-bounds/tree/575491d5fc353eac26010e45e9ced60fc9870017/research/gaussian-generator-rounding-margin).
It changes the shift through a permutation; it does not contradict either
fixed-order theorem.

The complemented-rotation automorphism and binary orbit-length fact are
credited to Gregor, Merino and Mütze,
[*The Hamilton Compression of Highly Symmetric Graphs*](https://doi.org/10.1007/s00026-023-00674-y),
section 3.3, equation (13), Lemma 3.4. They are not claimed new. The prime construction uses classical necklace
counting, coprime cyclic
products and Bertrand--Chebyshev prime existence, with primary credits to
[Moreau (1872)](https://www.numdam.org/item/NAM_1872_2_11__309_0/) and
[Erdős (1932)](https://www.renyi.hu/~p_erdos/1932-01.pdf). The scoped contribution
is the explicit ordinary-generator consequence, exact two-family kernel
scope, verified prime-family growth and paid cost/precision boundary. Preserve the
originating source authors' credit, including Vlado Vojdanovski's
capped-phase-fusion work. No literature-wide priority claim is made.

## Reproduction and executed checks

```sh
python3 -I -W error -B research/gaussian-orbit-generator-order/verify.py
python3 -I -O -W error -B research/gaussian-orbit-generator-order/verify.py
python3 -I -W error -B research/gaussian-orbit-generator-order/prime_verify.py
python3 -I -O -W error -B research/gaussian-orbit-generator-order/prime_verify.py
python3 scripts/research_package.py --package research/gaussian-orbit-generator-order --check-only
python3 scripts/research_package.py --package research/gaussian-orbit-generator-order
```

Both verifiers passed normally and under optimization with identical JSON
per script. The original checks cover 15 rational fixtures, 30 targets and
22 literal reconstructions. Prime checks add nine direct cycle enumerations
compared with independent Burnside sums/product counts; six rational
fixtures, 12 targets and 12 literal reconstructions; a 256-point finite-field
full inverse and rank check; and ten finite Bertrand families through d=4096.

Fifteen primary failure controls detect unsupported cycle lengths, repeated
prime periods, broken within-block factor/shift equality, wrong gauge
orientation, unstructured perturbations, singular inversion, a forged rank
bound and a false correction constant. Finite tests do not prove the
universal prime theorem, global rank minimum or runtime claims.

## Independent review and publication checks

A separate standard-library Cartesian-necklace construction checks exact rational
Stein support for three full matrices, without importing either contributor
verifier. It rejects repeated-prime cycles and a false correction constant.
Both modes are registered; all six canonical commands pass. REVIEW.md records
the independent proof, inverse, growth, precision and complete-cost review.
Committed bytes/modes, canonical source pins, whitespace and official export
integrity pass. The full-history gate is unavailable in the shallow checkout;
no success is claimed for it. Exact provenance and direct base ancestry were
checked separately. No hosted CI result, human review or formal acceptance is
claimed.

## Costs, limitations and open obligations

Explicitly materializing the prime-family generators takes `Theta(T^2/P)`
scalar slots and still loses to direct axis application for fixed n as d
grows, because log P=O(log²d)=o(d). The complemented family has T^2/ell slots.
The proof
charges uniform order generation, fixed-tape sorting in both directions,
generator access, accumulation and restoration; it does not admit a native
repository controller or a complete three-transform recurrence.

Prime rotations directly preserve already matched shifts. Removing
unmatched shifts by diagonal conjugation instead has the paid range
`log cond_2(D)=sum_i (n_i-1)|log v_i|`. A black-box normwise conversion must
charge that precision. The package gives a narrowly scoped fixed-shift cap
obstruction; it does not silently undo the retained gauge-free construction
or claim unmatched shifted factors satisfy the prime symmetry.

The all-order minimum, fast implicit generator use, and a stable actual-source
caller remain open. **No new kappa:** selected #7000 remains
`363005817/100000000000`, conditional on all five inherited assumptions.

Prepared for @CubeJerry with substantial OpenAI ChatGPT assistance. The
orchestrator proposed the orbit and prime-block applications and scoped
precision obstruction;
the worker independently derived and checked the proof and costs, identified
the classical overlap and packaged the result. New files are Apache-2.0.
