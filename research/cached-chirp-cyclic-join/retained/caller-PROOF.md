# The retained recovery catalogue does not admit the fine-theta port

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This is a source-bound obstruction and replacement-interface specification.
It changes no implementation, selected certificate, supplier or kappa.

## 1. Sources, notation and scope

The canonical source pin is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
`SOURCES.json` authenticates every live input. The public gap proof is pinned
at `9a07c08c014259bb23c0a2b5844a1b67d91892f6`; the actual Reference-to-ideal
compression join is pinned at `4509310a9a58d4c41c74029f899cbf36be1af9a1`.
Their retained proofs are authenticated by `DEPENDENCIES.json`.

Write **p0** for the parameter called `p` in
`research/unconditional-batched-crt/PROOF.md` and `GAUSSIAN.md`. Its family has

    p0=6b, b=ceil(log2 n), D=Theta(p0^epsilon), epsilon=1-10^-30,
    1/(4p0^2)<=theta_i=(t_i-s_i)/s_i<=1/p0^2,
    alpha=ceil(sqrt((4/pi)ln(16p0))), u=alpha^2,
    T/2<S=product s_i<T, 4n/b<=T<8n/b.                  (1)

Write **q** for the old Tensor's *external* precision `TensorPlan.p`.
This is not its private working-grid field `TensorPlan.P`, nor the radix
digit count also named `q` in `Sandwich.run`. Denote that digit count by Q.
The old spacing variable is **d_sep**=`TensorPlan.d`; the axis count is
**D**=`TensorPlan.dimensions`. Literal source ties d_sep=D+1.
All logarithms marked `log2` are binary; `ln` is natural.

Three increasingly permissive domains are considered separately:

1. The unchanged constructor/catalogue/recovery chain at the fine family.
2. A hypothetical relaxation allowing d_sep to vary independently of D,
   but retaining the fine family's alpha and three necessary old guards.
3. A further relaxation allowing alpha (hence u) to change, still retaining
   those guards and the old external fixed-record representation.

The second and third are necessary-condition superdomains, not implemented
ports or asserted feasible production families. Rejection of the first
does not execute its later ingress; the scan lower bound in Section 6 is
conditional on a hypothetical successful relaxed port retaining that ABI.

## 2. Exact caller binding

The relevant unchanged files are:

| File | Actual obligation |
| --- | --- |
| `physical-tensor-crt-sandwich-recovery/sandwich.py` | `run` creates `Catalogue` before numerical work; its default recovery policy calls `admit`; `admit` requires nonzero production mode |
| `physical-gaussian-tensor/tensor_catalogue.py` | reconstructs `TensorPlan(..., production=not header.mode.zero())` from the encoded catalogue |
| `physical-gaussian-tensor/tensor_plan.py` | loads `dimensions=axes+1`, `d=dimensions+1`, `u=alpha^2`; executes `production_axis` for each source axis and `production_common` in production mode |
| `arbitrary-bit-sandwich/boundary.py` | calls `child.run` without disabling its default recovery policy |

The necessary production inequalities are literally

    4 d_sep (t_i-s_i) > s_i,                            (2)
    u >= ceil(log2(8q)),                               (3)
    u d_sep <= q.                                      (4)

Equation (2) is `production_axis`'s strict lower ratio. Equations (3),(4)
are `production_common`'s logarithmic concentration and similarity guards.
The additional upper ratio `(2d_sep-1)(t_i-s_i)<s_i`, paired-halo period,
exact common Gaussian policy, cell separation, padding, chirp and restored
error guards all remain required. We need not weaken them or claim their
sufficiency. In particular changing a header to diagnostic mode cannot
meet `Sandwich.admit`'s production-mode requirement.

The complete source files and required AST sites are checked; no extracted
constructor is executed with substituted Count/Tape objects. Correctness of
the retained Count primitives is inherited. This is a mathematical audit
of the actual encoded contract, not a physical execution of a production
catalogue.

## 3. Literal dimension binding excludes the port

At an axis from (1), (2) implies

    1 < 4(D+1)theta_i <= 4(D+1)/p0^2.                  (5)

Choose an eventual upper constant C_D with D<=C_D p0^epsilon. Since
epsilon<1 and p0>=1, the last expression is at most
`4(C_D+1)/p0`. It is <=1/2 once `p0>=8(C_D+1)` and the bound on D is in
force. Thus every fine axis fails (2) eventually, irrespective of q or
alpha. The literal caller has no production recovery admission on that
eventual family.

This qualitative old-band/fine-band incompatibility is prior knowledge:
`pr1786-fine-prime-transfer-audit` already includes an old theta~1/d
guard as a failing control, and #4029/#4142 already read d=D+1. Our new
claim is the complete encoded recovery binding and the stronger nested
consequences below, not discovery of that generic band mismatch.

## 4. Even independent spacing cannot keep the fine alpha

Now allow d_sep to be arbitrary, which strictly relaxes the literal source.
For any fine axis (2) and theta_i<=p0^-2 imply

    d_sep > p0^2/4,
    q >= u d_sep > u p0^2/4 >= p0^2/4.                 (6)

Here u is a positive integer, as in the source. On the other hand (3) gives

    8q <= 2^u.                                        (7)

For the actual fine alpha, the public gap proof gives
`pi*u<=5ln(16p0)` for p0>=2^200. For completeness this loose explicit onset
needs only elementary inequalities. Put L=ln(16p0). Since ln2>1/2,
L>100. The ceiling definition and 3<pi<4 imply

    pi*u <= 4L+4sqrt(pi L)+pi
          < 4L+8sqrt(L)+4 <= 5L.

The last inequality holds for L>=100 by putting x=sqrt(L)>=10 in
`x^2-8x-4>=16`. Also ln2<3/4, since the positive exponential series gives
`exp(3/4)>1+3/4+9/32+27/384>2`. Hence

    2^u <= exp((5/3)ln2*ln(16p0))
         < (16p0)^(5/4)=32 p0^(5/4),
    q < 4 p0^(5/4).                                   (8)

For p0>=64, `p0^2/4>4p0^(5/4)` (equivalently p0^3>2^16).
Equations (6) and (8) contradict one another. Therefore:

**For p0>=2^200, no external precision q and no independently chosen
positive spacing d_sep can satisfy (2)--(4) with the actual fine alpha.**

This is an all-q exclusion, not merely a failure at q=p0 or a finite search.
Increasing the private working precision P does not change (2)--(4).
The onset is for this alpha estimate and refusal only; it is not an onset
for legal global periods, primes, Core geometry or the complete multiplier.

## 5. Retuning alpha still forces an external precision lower bound

Relax alpha as well, keeping u positive and (2)--(4). Equations (3),(6)
give

    q > (p0^2/4) log2(8q).

Because q>p0^2/4, `log2(8q)>1+2log2(p0)`. Consequently every element of
this enlarged necessary-condition domain obeys the strict bound

    q > (p0^2/4)(1+2log2(p0))
      = Omega(p0^2 log p0).                            (9)

This does not assert that any point satisfying (9) meets the other old
guards, the original dimension binding, or any source accuracy premise.
It states what every successful relaxation retaining these three guards
would have to pay. In particular no q=O(p0) schedule suffices there.
The private coefficient/setup precision O(p0^2 log p0) of the *new* fine
Reference is a different quantity; no setup bit is being mislabeled as a
runtime record bit in (9).

## 6. The external width has an actual full-volume scan bill

`TensorPlan` sets `component_bits=q+2` and `record_bits=2(q+2)`.
`Sandwich.ingress` iterates over every original coordinate in `source_product=S`.
At each it writes a real signed component and an imaginary zero, including
the S-Q padded zero records. `ring_words.write_signed` calls `write_fixed`
in both sign branches; `compact_counts.write_fixed` appends exactly its
declared width, including leading zeroes. Thus one ingress writes exactly

    2S(q+2) payload cells, and the two ingresses write 4S(q+2).       (10)

The full retained parent bank occupies Omega(Sq) cells. Reads, rewinds,
return copies, erasure, metadata, source tables, CRT, scalar products and
the three complete Tensor calls add work; none can cancel these appends.
This lower bound does not require or discount any supplier cost.

Using the fine-family volume S=Theta(n/p0) from (1), (9)--(10) imply

    Omega(Sq)=Omega(n p0 log p0)
              =Omega(n log n log log n).               (11)

For any fixed kappa>=0 this exceeds the intended
`O(n (log n)^(1-kappa))` budget. Again (11) is the consequence for a
hypothetical successful port preserving the named necessary guards and
literal ingress representation after relaxing d_sep and alpha. The
unchanged literal caller already rejects; we do not charge nonexistent
post-rejection execution. Packing, a new admission policy or a different
caller can evade this scoped obstruction and must be analyzed separately.

## 7. Numerical recovery is a separate gate, with two source S factors

This section restates the retained caller's conditional recovery interface;
it is not a new convolution theorem. Let A be its actual `outer_bits`,
M=2^A, and let its own source gamma and E be

    gamma=D(2u+ceil(log2(32q))+1),
    E=Dq^2+6M+22+2D, epsilon=E*2^(gamma-q).

`Sandwich.admit` evaluates exactly

    2^(2b+5) S^2 (3E 2^gamma+2) < 2^q.                (12)

It also requires production mode, so a passing (12) cannot waive
(2)--(4). #5325 improves a conditional restored Tensor error estimate;
its proof explicitly retains all production requirements and cannot waive
these guards either. A small exact descriptor control in our checker passes
(12) while failing (2); it is not an admitted production invocation.

For the ideal source maps `R F_s` and `R F_s^+`, with the source's
multiplicative-index permutation R, the opposite sandwich is
`(u_input *cyclic v_input)/S^2`. Ingress scaled each digit by 2^-(b+2).
The literal recovery routine therefore performs two exact multiplications
by S and one exact shift by 2b+4, then nearest integer. Its temporary width
is `(q+2)+4b+4`, as in #5095; S<2^b and q>=b+2 keep it O(q).

More generally, a replacement complete transform service on every reached
half-disk input with coefficient error <epsilon, including its actual final
normalization restoration, supplies the existing sufficient condition

    S^2 2^(2b+4) (3epsilon+2^(1-q)) < 1/2.             (13)

Retained contraction/radius reasoning makes the rounded pointwise product
an admitted input to the opposite service; its component truncation error
is <sqrt(2)2^-q<2^(1-q). This explains both S factors, the strict half
threshold, and why a per-transform gamma cannot be silently omitted or
counted a second time after a service has already restored it. The exact
integer/CRT controls test these algebraic mistakes without pretending to
execute Fourier or Gaussian code.

## 8. Required replacement interface and remaining obligations

The public Reference/ideal join proves the source-bound *compression*
comparison under its explicit radius, source-first target and producer
contracts. It does not provide a new `TensorPlan`, full prefix, Fourier
service, production catalogue or end-to-end recovery admission. In
particular the old gamma formula above is not automatically the new
group-normalizer ledger's gamma.

A useful next join must replace the literal old policy and authenticate an
actual fine-family catalogue. It must bind original axes/holes, encoded
coefficient/reference delivery, original-coordinate Core/halo/diagonal
services, and a complete expansion/chirp prefix to the new error ledger.
Let Gamma be the *actual total existing* normalization exponent of that
replacement and C_N its exact normalized compression on the padded field.
If a computed prefix yhat and exact prefix y obey the public compression
radius contracts, and the restored compression implementation has error
<=2^-tau on yhat, then the missing source-specific prefix bound gives

    ||output-2^Gamma C_N y||
      <=2^-tau+2^Gamma ||C_N|| ||yhat-y||+e_extra.       (14)

Use the public join's maximum-coordinate component-l1 norm in (14).
A complex-modulus prefix radius or error must be multiplied by at most
sqrt(2) before entering that norm; a resulting component-l1 error already
bounds the complex-modulus error required by (13). Only the exact C_N is
used as a linear operator in (14); no rounded-map contraction is assumed.
Here e_extra explicitly covers any new entrance/output codec or restoration
rounding; exact paid dyadic restoration contributes zero. The public policy
can bound the normalized C_N and Gamma=O(D log p0)=o(p0), but it does not
supply the actual prefix error in (14). Before using (13), that error,
radius and full source/route/setup cost must be proved for all reached
inputs, and the target must be the full `R F_s` or opposite map. A standalone
compression bound must not be labeled a complete transform error.

The desired new policy may retain external q=O(p0); Sections 3--6 show
why doing so requires replacing an old admission clause or the caller,
rather than merely raising its numeric precision. No claim of an
unconditional multiplication theorem, new full kappa, general impossibility,
or defect in the current selected conditional theorem follows.

## 9. Novelty, evidence and costs

`OVERLAP.md` records the bounded predecessor audit. In particular #4142
already extracts the lower ratio and d=D+1; #3861 settles a finite old-domain
precision gap; #5149/#6444 improve the old prime band; the pr1786 audit
already rejects old-theta transfer; #5095 supplies this exact recovery
caller and two-S guard; #5325 joins older Tensor errors; #6185 adds a paid
arbitrary-bit wrapper but retains production admission. We claim the
specific combined refusal, all-q strengthening, relaxed-width/full-ingress
consequence and resulting replacement obligation above.

The universal arguments are Sections 3--6. The replay authenticates whole
source files, checks exact AST sites, exhausts a bounded integer necessary
domain, checks large dyadic-parameter inequalities using integers, and
exercises a separate rational CRT/convolution/rounding oracle. Mutation and
boundary controls detect missing strictness, concentration, similarity,
source-field width, gamma and either S factor. The replay performs no actual
Tensor/CRT/Count/Tape run and imports no predecessor verifier. Counts and
stopping bounds are reported in `evidence/REPLAY.json`; finite coverage is
corroboration, not the all-size proof.

The audit adds no runtime algorithm or amortized setup claim. The lower
bound (10) charges only unavoidable writes; all inherited producer, private
precision, routing, scalar arithmetic, copy, restoration and erasure costs
remain additional. This work does not require a large native replay to
establish failure of necessary admission conditions.
