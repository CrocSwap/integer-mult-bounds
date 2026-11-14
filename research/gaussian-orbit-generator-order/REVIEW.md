# Independent review of the combined orbit construction

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Reviewed PROOF.md SHA256 `35bcef9c289957ef3eda6177195b93263a9433793931b108dafa26ced2355ee7`
and PRIME-ORBITS.md SHA256 `738481071650e0fc86305ac0bffd50cd3c0494e6975df8932a273a893b159b70`.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance. The
orchestrator proposed the two orbit mechanisms, the worker independently
derived and challenged them, and the orchestrator performed the following
separate mathematical and computational checks. This is not independent human
or formal-kernel acceptance, nor a claim of literature-wide priority.

## Quantified argument checked

For any actual kernel symmetry a, listing its cycles consecutively ensures
that both predecessors are related by a whenever neither index starts a cycle.
The Stein displacement consequently vanishes off the union of the start rows
and columns. The decomposition QE+(I-Q)EQ counts the intersection once, gives
2c explicit outer products, and telescopes to 2c ordinary triangular Toeplitz
products because the ordinary shift is nilpotent. Inversion preserves the same
permutation symmetry. This proves the inverse statement without assuming a
Toeplitz inverse or silently reversing its displacement shift.

For the complemented rotation, a^ell reverses all selected labels. Even n
makes that action fixed-point-free, and the power-of-two divisors imply every
cycle has length2ell. Arbitrary spectators do not change the argument. The
primary Springer article was opened independently and equation13/Lemma3.4
were checked: the binary complemented rotation and its periods are classical.
The even-n kernel application and the generator consequence are the scoped
new use, not discovery of that automorphism.

For prime blocks, a single block has exactly n constant words and all other
orbits have prime length. For a chosen tuple of block cycles, pairwise coprime
periods make their Cartesian product one cycle, by the elementary Chinese
remainder theorem. Multiplying those exact counts proves (P3), including the
short cycles. The correction bound uses log(1+u)<=u and the exact geometric
sum sum(2j/4^j)=8/9. It is uniform in n>=2 and in the number of distinct odd
primes. The counterexample525/256 shows that replacing the correction by2 is
invalid. Repeated primes and composite block lengths require different counts.

The cited Erdős1932 primary proof was opened and its sections4--5 checked:
Bertrand's theorem supplies a prime strictly between2^i and2^(i+1) for i>=1.
For k=floor(log2 d)-2, summing the upper endpoints gives2^(k+2)-4<=d,
while multiplying the lower endpoints gives2^(k(k+1)/2)<P. For every fixed
n and a>0, the logarithm of P/(e^(8/9)n d^a) tends to infinity because its
positive quadratic term in k dominates all linear terms. No finite prime
search is being substituted for that theorem. This is an upper representation
bound; no unbounded all-order rank lower bound or optimality follows.

## Precision, source and complete cost boundaries

Prime rotations directly preserve any internally matched factors, including
common nonzero shifts and odd dimensions. They need no shift-removal diagonal.
For unequal shifts converted by D, the exact log condition number is the sum
of endpoint log ranges. The conjugation error norm bound is sharp for arbitrary
norm-bounded errors by a matrix unit between extreme diagonal positions.
That worst-case black-box guard is not a claim about every structured error.
The large-cap obstruction in PROOF.md applies only to that explicit conversion,
not to the directly invariant prime construction.

The represented input/output permutation is paid. Its scan bound can use one
precomputed O(b_label)-cell guide marking the selected block boundaries. With a
single coordinate-sized buffer, a sequential pass rotates each block; the guide
and buffer are restored by linear scans. No random-access visited table or
input-dependent tape alphabet is necessary for the stated conservative bound.
The 2c dense nontrivial generator vectors contain2cT slots, with prescribed zeros
still stored. Their setup size is Theta(T^2/P) in the prime family, and for fixed
n this eventually exceeds direct axis application O(dTn), since log P=o(d).
Thus the paper's rank saving is not a complete-cost algorithm improvement.

Actual heterogeneous source factors, rounded tables, periodic tails, gauges,
owner/routing/stock contracts and coefficient generation remain separate. All
five retained assumptions and the selected kappa remain unchanged.

## Independent computation

`independent_check.py` imports no worker implementation. It constructs local
necklace cycles by direct cyclic rotations, then assembles global cycles through
their Cartesian phases. This differs from the worker's global visited-set orbit
enumeration and Burnside comparison. Every off-start displacement entry is
checked exactly with rational Gaussian coefficients.

The two n=2, blocks3+5, 256-label cases use shifts1 and3/2. Each has32 cycles,
with period counts {1:4,3:4,5:12,15:12}, giving64 generator terms. The n=3,
block3, shift2 case has27 labels and11 cycles, giving22 terms. Repeated3+3
is rejected by duplicate-label detection; the correction525/256 is checked
exactly. Normal and optimized runs are registered. These finite witnesses
corroborate the universal proof and do not establish a larger scope.

Separately, before the prime extension, direct SymPy1.14 rational inversion
checked forward/inverse ranks for six complemented-rotation cases, including
n=4,d=2 and n=2,d=4 with q=1/2 and2/3; odd-alphabet, non-power, unequal-factor
and interior-order mutations were detected. That optional supplementary run
is preserved in the recovery checkpoint; it is not a runtime dependency of
this package's standard-library registered checks.
