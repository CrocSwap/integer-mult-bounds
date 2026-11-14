# Independent lead review of affine-period outward slack

Base: `e54523517d0f03e58352e647c403a5af3e525a57`.
The final author proof and code were reviewed in the publication snapshot.
All eight exact remote source pins match; normal/optimized author replay and
the separate root rational/source replay pass. The proof and implementation
hashes are recorded in PUBLICATION-MANIFEST.json.

## Universal equality

Let U be a square orthogonal matrix, F integer-valued, and Lambda a full-rank
integer lattice satisfying F(x+lambda)=F(x)+U lambda. Each error e=F(x)-Ux
is constant on its coset. The triangle inequality bounds every outward norm
increment by ||e||. For the reverse bound, choose a coset representative a.
The full-rank lattice has a bounded covering radius, so there are lambda_t in
Lambda with lambda_t=t U^T e+O(1). If e is nonzero, the vector U(a+lambda_t)
has length tending to infinity and unit direction tending to e/||e||.
Rationalizing the difference of its norm and the norm after adding e gives
the limit ||e||. If e=0 the difference is identically zero. The finite quotient
therefore gives the claimed maximum. This is a different proof of the lower
bound from the author's exact rational-ray argument.

The source arithmetic is rational, so the author's stronger exact ray also
works: some positive integer multiple of U^T e belongs to Lambda. In fact
rationality of U follows from the other hypotheses: choose an integral basis
matrix B of Lambda; the columns of UB are integral differences of F values,
so U=(UB)B^-1 is rational. Bijectivity is not needed. If present, it makes
the inverse affine-periodic on U Lambda, with inverse error -U^T e at F(x),
and hence identical uniform error norm and identical outward-slack supremum.

This is a statement on the unbounded lattice. It does not guarantee the same
supremum on an arbitrary fixed signed-width box, input ball, or selected caller
domain. Nonexpansion failure does not by itself give a new multiplication bound.

## Fixed-sum conservative family

For a Gaussian pair let s=x+y and d=x-y. The map fixes s and sends d to
sigma*i*(d-c(s))+c(s). Its error is (q,-q), where
q=(1-sigma*i)c(s)/2, of ambient pair norm |c(s)|. The orthogonal inverse image
of that error is also zero-sum. Twice that image is the Gaussian-integer tangent
vector (-(1+sigma*i)c(s),(1+sigma*i)c(s)); it preserves s and its image is
twice the error. Thus the exact-ray proof applies on each fixed-sum fiber,
even though the source's sign-dependent center is not globally periodic.

Integer outputs require Re(c)+Im(c) congruent to Re(s)+Im(s) modulo two.
At mixed parity, every Gaussian integer center has magnitude at least one.
Consequently the least possible global outward slack among these legal
center-on-sum affine-difference rules is one. The source #6509 selects centers
of magnitude zero or one, so attains it. This does not classify arbitrary
nonperiodic bijective rounders in #6619.

On the specific positive-sign ray (1-t-it,t+it), the unchanged source returns
(1+t-it,-t+it). Squared norms are 4t^2-2t+1 and 4t^2+2t+1. For integer t>=1,
the outward difference is strictly between (32t^2-2)/(32t^2+1) and one.
To prove the lower bound, write each radical as sqrt((2t +/- 1/2)^2+3/4)
and use sqrt(a^2+c)<a+c/(2a) for a,c>0 in their rationalized denominator.
The upper bound follows because each radical is greater than 2t +/- 1/2.
For h=2^-p and t=2^(p-1), the physical squared norms are 1-h+h^2 and
1+h+h^2. This is a pair Euclidean unit-ball obstruction, not an obstruction
to every selected component guard or every possible finite-width interface.

## Independent executed evidence and controls

`check_norm_slack_root.py` uses exact Fractions, a new rational rotation,
complete representatives modulo 5Z^2, and squared polynomial inequalities
instead of floating square roots. It reads and authenticates the unchanged
#6509 source blob before compiling those bytes directly; it does not import
the author's checker or any bytecode cache. The accompanying RESULT records
80 rotation-ray checks, 20 actual source ray/inverse checks through t=2^256,
and dyadic ball witnesses through p=257. These finite checks corroborate the
proof and source binding; they do not prove a universal theorem by enumeration.

Failed-premise controls explain the limits. An incorrect proposed period
fails the affine identity. For U=2I and F=U the error is zero but outward
growth is unbounded, so orthogonality matters. With only the period along the
first coordinate, F(a,b)=(a,b-sign(b)) has error norm one and never increases
the norm, so full rank matters. For a rectangular isometry Ux=(x,0),
F(x)=(x,x mod 2) has period 2Z and error maximum one, but outward supremum
sqrt(2)-1; the error cannot be aligned using input directions. The square
orthogonal assumption avoids that problem.

The pinned #6534, #6536 and #6758 proofs supply their kernel error/period
premises. This review read their relevant proofs but did not independently
regenerate the #6536 matching or #6758 large finite tables. Any applications
must retain that explicit source dependency. Source approximation optima are
predecessor results; the present contribution converts them to exact radial
slack statements within the stated family. No new kappa or native tariff.

Prepared for @CubeJerry by the lead OpenAI research agent, with substantial
AI assistance. This is independent reasoning and implementation within the
same AI-assisted session, not human review or proof-kernel certification.
