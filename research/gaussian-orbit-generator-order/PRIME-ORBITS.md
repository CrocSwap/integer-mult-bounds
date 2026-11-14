# A stronger orbit family from disjoint prime-length rotations

This extends the unequal-cycle support theorem in PROOF.md, sections 1--2.
It does not change that theorem or the fixed lexicographic lower bound. It
gives another explicit ordering, not an all-order optimum or a fast transform.

## 1. Exact cycle count without reversal symmetry

Let B be any n-by-n matrix, n>=2. Select distinct odd primes
`p_1,...,p_k` with `s=sum p_i<=d`. Partition s coordinates into these block
lengths. Let a rotate each selected block one position to the left,
simultaneously, leaving the other d-s coordinates fixed. For
`H=B^tensor d`, multiplication of the scalar factor entries shows

\[
                              H(ax,ay)=H(x,y).                   \tag{P1}
\]

No centrosymmetry, even dimension, positive entries, or Gaussian form is
required. More generally, each block may have its own matrix repeated on all
coordinates in that block, and an arbitrary square spectator matrix may
replace the remaining tensor factors. The same invariance proof applies.

For a single prime block of length p, the n constant words have period one.
Every other word has period p, since its period divides p. Hence its number
of cycles, including the constant cycles, is exactly

\[
                    c_p=n+{n^p-n\over p}
                        ={n^p+(p-1)n\over p}.                  \tag{P2}
\]

This is the prime case of classical necklace/orbit counting. It is proved
here by the period split, not inferred from finite enumeration. Credit
Moreau, [*Sur les permutations circulaires distinctes* (1872)](https://www.numdam.org/item/NAM_1872_2_11__309_0/),
and the classical orbit-counting lemma commonly called Burnside's lemma.
Neither necklace counting nor cyclic group actions are claimed new.

Choose one cycle in each block, with lengths `r_i in {1,p_i}`. These lengths
are pairwise coprime. The simultaneous successor on their Cartesian product
has period `lcm(r_i)=product r_i`, equal to the size of that product, so it
has exactly one cycle there. Equivalently, the Chinese remainder theorem
lets one simultaneous time realize every tuple of component phases.
Thus different choices of component cycles give disjoint product cycles,
and exhaust all vertices. With `T=n^d` and `P=product p_i`, the exact total is

\[
 c=n^{d-s}\prod_i c_{p_i},\qquad
 {c\over T}={1\over P}\prod_i\left(1+(p_i-1)n^{1-p_i}\right).    \tag{P3}
\]

For a spectator of dimension m, replace the first factor `n^(d-s)` by m
and T by `m n^s`; the displayed ratio is unchanged. Blocks with different
alphabet dimensions n_i>=2 likewise have the same product formula with
the corresponding n_i in each factor.

Concatenate the cycles of a, with each cycle listed in successor order.
Theorem 1 of PROOF.md applies even though those lengths differ. If Z is the
ordinary strict lower shift in this order, both the forward matrix M and,
when it exists, its inverse satisfy

\[
 \operatorname{rank}(M-ZMZ^{\mathsf T})\le2c,\qquad
 \operatorname{rank}(M^{-1}-ZM^{-1}Z^{\mathsf T})\le2c.           \tag{P4}
\]

The explicit start-row/column decomposition in that proof supplies at most
2c ordinary lower-times-upper Toeplitz generator terms for each target.
Inverse invariance follows by inverting the permutation-conjugation
identity; no additional inverse displacement premise is introduced.

## 2. An absolute correction constant

For n>=2, `n^(1-p)<=2^(1-p)`. Since the p_i are distinct odd integers at
least 3, the logarithm of the correction product in (P3) is at most

\[
 \sum_i(p_i-1)2^{1-p_i}
 \le\sum_{j\ge1}{2j\over4^j}={8\over9}.                       \tag{P5}
\]

Here `log(1+u)<=u` for u>=0 and the last equality follows by differentiating
the geometric series, or multiplying its absolutely convergent sum by
`1-1/4` twice. Therefore, with `C=exp(8/9)<3`,

\[
 {T\over P}\le c\le {CT\over P},\qquad
                \operatorname{rank}E(M),\operatorname{rank}E(M^{-1})
                         \le\min(T,2CT/P).                     \tag{P6}
\]

The bound is uniform in the number of selected primes, d and n. Repeated
primes are excluded: their nontrivial cycle lengths are not coprime, and
their Cartesian product splits into more cycles. Nor is (P2) the correct
formula for composite lengths; intermediate periods contribute.

## 3. An elementary family with a superpolynomial gain in d

For d>=8 set `k=floor(log_2 d)-2`. For each `1<=i<=k`, take the least prime
`p_i` strictly between `2^i` and `2^(i+1)`. Existence follows from the
Bertrand--Chebyshev theorem; a primary elementary proof is Erdős,
[*Beweis eines Satzes von Tschebyschef* (1932)](https://www.renyi.hu/~p_erdos/1932-01.pdf),
sections 4--5. This classical prime-existence theorem is an explicitly
cited mathematical input, not a new integer-multiplication assumption.

The intervals are disjoint and all primes are odd. Their total coordinate
budget and product obey

\[
 \sum_i p_i <\sum_{i=1}^k2^{i+1}=2^{k+2}-4\le d,\qquad
 2^{k(k+1)/2}<P<2^{k(k+3)/2}.                                  \tag{P7}
\]

The inequalities are strict because every interval endpoint is excluded.
Combining (P4)--(P7) gives the concrete all-size bound

\[
 \operatorname{rank}E(M),\operatorname{rank}E(M^{-1})
       <2e^{8/9}T\,2^{-k(k+1)/2}.                              \tag{P8}
\]

For the Gaussian factor `B_ij=q^((i-j)^2)v^(i-j)`, with any n>=2,
`0<q<1` and `v>0`, B is invertible and the exact lexicographic minimum is
`2T/n` by the predecessor theorem. All d factors here are identical, including
the shift v. The ratio of that lexicographic count to the certified upper
bound `2CT/P` is `P/(Cn)`. For every fixed n and every fixed exponent a>0,
`P/(Cn d^a)` tends to infinity: (P7) gives a quadratic lower bound in k for
`log_2 P`, while `log_2 d<k+3` is linear in k. This is the precise sense in
which the certified generator-count gain is superpolynomial in d.

Equivalently, the proved rank upper bound is
`T exp(-(log d)^2/(2 log 2)+O(log d))`. It still grows with T; this is not a
bounded-rank representation. For n depending on d, compare `P/(Cn)`
explicitly instead of claiming a uniform gain over lexicographic order.
We do not optimize prime selection or use stronger asymptotic prime estimates.
For small instances, the complemented-rotation or lexicographic construction
may give a smaller bound; all are valid available choices.

## 4. Exact shifts and the retained source boundary

Unlike complemented rotation, ordinary rotations require only equality of
the factors within each block. In particular, common shifted Gaussian
factors already satisfy (P1), so the prime-rotation result needs no diagonal
conversion to unshifted factors. Common rounded or truncated factor tables
also preserve (P1), whatever their symmetry; the inverse again requires
nonsingularity. Different blocks can have different shifts or kernels if
each individual block is internally matched.

Different shifts or coefficient tables within one rotating block generally
break (P1). If one instead removes unequal shifts by diagonal conjugation,
the exact `sum_i(n_i-1)|log v_i|` range and error-transfer cost in PROOF.md
section 5 remain payable. That section's fixed-shift obstruction concerns
that particular conversion; it is not an obstruction to the directly
invariant prime-rotation construction.

The source's actual Gaussian phases, dimensions, physical gaps, periodic
tails and paid gauges must still produce the stated matched blocks. No
all-size caller admission is supplied here. A tensor permutation changes the
layout and must be transported and restored. None of these algebraic facts
discharges analytic_recovery or any other retained assumption.

## 5. Uniform construction and materialization costs

The least primes in (P7) can be found uniformly by trial division, with a
conservative `O(d^2 polylog d)` bit budget; all candidates and trial divisors
are at most d. This deliberately simple choice is not a prime-search speed
claim.

The order of the selected coordinate permutation divides P. For each
lexicographic label x, repeatedly apply the block rotations until returning
to x; at most P steps are needed. Accept x if it is the least label in its
cycle, then output that cycle by the same traversal. This accepts exactly
one representative per cycle and outputs each label once. A cycle traversal
does not assume its length is P: it stops on the actual first return.

With `b_label=d ceil(log_2 n)`, rotating all blocks and comparing labels cost
`O(b_label)` bit scans on a fixed number of tapes. This conservative uniform
enumeration therefore costs `O(TP b_label+d^2 polylog d)` bit steps and
`O(b_label+log P)` scratch beyond its output. The map/sort/join transport
from PROOF.md section 6.1 then gives, in each direction,

\[
 C_{\rm perm}=O(TP b_{\rm label}+d^2\operatorname{polylog}d
                 +T(b+b_{\rm label})\log T).                   \tag{P9}
\]

This is a paid construction, not a claim of optimal enumeration, a native
repository controller, or a source-local permutation. A faster necklace
enumerator could improve it but is not needed for the representation theorem.

The same explicit generator formula now contains `2cT` nontrivial scalar
slots, including prescribed zeros, and (P6) bounds that number between
`2T^2/P` and `2CT^2/P`. Thus it is `Theta(T^2/P)` uniformly. If materialized
at b bits per slot it costs that many bit writes times b. Simple tensor
entry assembly uses `O(cTd)` factor accesses and arithmetic operations, with
the same precision/access qualifications as PROOF.md section 6.2. Apply
its bill (17) with this c and (P9); the full source recovery bill remains
unproved.

For fixed n, (P7) gives `log P=O((log d)^2)=o(d)`, whereas `log T=d log n`.
Consequently `T/(P d n)` tends to infinity. Even optimistic unit-cost
materialization of these generators therefore eventually exceeds direct
dense axis application's `O(dTn)` operations. The superpolynomial saving
against the old generator count does not rescue this explicit application
scheme. Implicit coefficients, compressed access or a different circuit
would need a separately proved complete budget.

## 6. Verification boundary

The companion prime_verify.py cross-checks literal cycles, the independent
Burnside fixed-point average and (P3), including multiple primes and actual
short cycles. Small rational matrices test direct shifted and nonsymmetric
factors, literal forward/inverse ranks, support and reconstruction. A larger
two-prime fixture uses exact modular arithmetic with explicit finite scope.
Repeated primes, composite lengths, unequal within-block factors and a
forged correction bound are failure controls. Finite prime families check
the concrete formulas, not Bertrand's universal theorem.

All infinite-family claims come from the proofs above and the named classical
prime theorem. No finite search implies an asymptotic impossibility or a new
kappa. The selected multiplication bound remains conditional and unchanged.
