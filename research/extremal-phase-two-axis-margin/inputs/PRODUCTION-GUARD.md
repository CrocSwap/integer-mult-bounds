# Production guards imply positive weights and a retained-band error bound

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This is a source-relative written proof, not a formal proof-kernel check or
independent human review. The live scientific source is canonical main
721c03822c421b7f7fcbb2598993b947c4d88419; physical Gaussian code last changed at
7ab67b4a84d28cd562b9711aa315ca5b47822b37. No predecessor bytes are changed.

## Precise dependency and claim

Use the scalar theorem of [PR6085](https://github.com/CrocSwap/integer-mult-bounds/pull/6085)
at 9fc80f1db55d4939c7b53c0799e6840cce35fbf8, PROOF.md in
`research/encoded-gaussian-directed-coefficient-audit`: for P,F>=1 and rational
0<=f<=F, the unchanged encoded coefficient routine returns a dyadic c with
0<=c<=exp(-pi*f) and exp(-pi*f)-c<2 eta, eta=2^-P. Its Axis argument-domain
lemma is cited but the particular arguments used here are checked below.
This is a mathematical dependency, not imported pending receipt/code and not
an independently repeated scalar audit. Exact Count/Rational arithmetic and
its ownership semantics remain the retained runtime contract.

For every canonical parameter tuple admitted by ProductionPlan and the Axis
layout guards, let H be the entries prescribed by Axis.matrix_entry, before
its separate validate_rows acceptance check. Define N_w on residues 0..s-1:
diagonal one; zero when neither signed cyclic displacement has modulus <=w;
on every other position choose the unique such displacement delta and set

    (N_w)ij = exp(-pi*u*((rho*delta+beta_i)^2-beta_j^2)),
    rho=t/s, theta=rho-1, q_j=floor(rho*j+1/2), beta_j=rho*j-q_j.

Then every prepared similarity weight is >2^(-8p-1) and

    ||H-N_w||_infinity < p*2^(16p+4)*eta < p*2^(16p+7)*eta.

This concludes one retained-band perturbation implication. It does not prove
that Axis.validate_rows succeeds for every tuple, the ideal infinite-matrix
tail bound, global ideal rowgap, inverse/LU validity, full production page,
online solve, tensor/CRT admission, physical total cost or a new kappa.

## Production inequalities and positive weights

ProductionPlan checks p>=101, s<t<2s, u>=ceil(log2(8p)), ud<=p,
4d(t-s)>s, (2d-1)(t-s)<s, and d>4w+2. It computes P=32768p
and w=ceil(sqrt(16p/u))+2: the loop seeks the least integer whose square
is >=ceil(16p/u), equivalent to >=16p/u. Remaining width/window/halo guards
restrict this domain further. Axis separately checks 2w<s.

The half-up nearest convention gives -1/2<=beta_j<1/2, also at ties.
Thus F_j=u*(1/4-beta_j^2)/theta lies in [0,u/(4theta)] and

    F_j < ud <= p,    0<a_j=exp(-pi*F_j)<=1.

Using pi<4 and e<4 gives exp(pi*p)<exp(4p)<2^(8p), hence a_j>2^-8p.
These classical loose inequalities suffice; no numerical pi oracle is used.
The prepared argument ceiling is >=u/(4theta), so the scalar theorem applies.
Reflection reuse preserves a_j: q_{s-j}=t-q_j off ties, whereas both beta
values equal -1/2 at a half-integer tie. Their squared offsets agree.

Since P=32768p>8p+2, 2eta<2^(-8p-1). Consequently

    a_hat_j > a_j-2eta > 2^(-8p-1) > 0.

This proves the prepare_weights positivity guard from production parameters
and the scalar contract, rather than assuming it because a finite page passed.

## The original-coordinate identity and physical cuts

For a direct pair delta=j-i with equal phase q_i-i=q_j-j,
q_j-q_i=delta and beta_j-beta_i=theta*delta. Therefore

    F_i + u*rho*delta^2 - F_j
      = u*((rho*delta+beta_i)^2-beta_j^2).

It follows exactly that a_i*G_delta/a_j=(N_w)ij, where
G_delta=exp(-pi*u*rho*delta^2). This is the original-coordinate entry;
the bare Toeplitz kernel G_delta is not interchangeable with it.

Axis takes that ratio only when raw displacement is direct AND phases agree.
Every wrapped pair takes the coefficient branch, even if a lifted phase label
would agree across a physical-period seam. Every direct different-phase pair
also takes it. For these nonzero integral delta,
|rho*delta+beta_i|>=rho-1/2>1/2>=|beta_j|, so the decay argument is positive.
It is at most u*(rho*w+1/2)^2, covered by argument_bound. The kernel argument
u*rho*delta^2 is covered too, since rho>1. Thus the scalar theorem applies to
all retained coefficient branches. The diagonal bypass returns exactly one;
nonretained positions return exactly zero, both matching N_w without error.

The definition of N_w deliberately uses the source's cyclic displacement and
physical cut. Identifying it with a particular infinite-periodized ideal
matrix requires an additional tail/comparison theorem; it is not implicit here.

## Ratio error and row sum

For a same-cell entry write x=a_i, y=a_j, g=G_delta and put hats on the
rounded values. All lie in [0,1], y>2^-8p and y_hat>2^(-8p-1).
The directed scalar contract gives each scalar difference <2eta. Consequently

    |x_hat*g_hat-x*g| <= |x_hat-x|*g_hat + x*|g_hat-g| < 4eta,
    |x_hat*g_hat/y_hat-x*g/y|
      <= |x_hat*g_hat-x*g|/y_hat + x*g*|y-y_hat|/(y*y_hat)
      < (2^(8p+3)+2^(16p+2))*eta
      < 2^(16p+4)*eta.

The last inequality holds for p>=1. No additional rounding occurs: the actual
consumer uses exact Rational.times followed by Rational.over. This error need
not be downward, since dividing by a downward denominator can increase it.
Other retained off-diagonal entries have error <2eta, hence obey the same cap.
Since 2w<s there are exactly 2w potential retained off-diagonal positions per
row. The production guards u>=1, ud<=p and d>4w+2 imply 2w<p. Summing proves
the asserted infinity-norm bound. Principal restrictions can only reduce it.

If a separately proved ideal comparison ||N_w-N||<=2^-46p is supplied, the
triangle inequality yields the original weaker p*2^(16p+7)*eta+2^-46p budget.
Neither that comparison nor a rowgap of N is established by this package.
