# Common carry gauge: independent algebra and cost

The proposed beta-weight mixed-radix identity is exact. Put
`beta_ell=0` and choose `q_i beta_i-beta_(i+1)=1`. For ordinary
radix carries `c_i` in `x+y=r mod T`,

    S(x)+S(y)-S(r)=sum_i c_i,
    S(x)=sum_i beta_i x_i.

Thus gauged ordinary cyclic convolution gives a polynomial
`Q_r(lambda)` of degree at most `ell`. Its constant coefficient is
the tensor lower Toeplitz result. Its input and kernel phases have
rational exponents; the output polynomial has integer exponents.

For output zero, kernel position `x=w_s` and input position
`y=T-w_s` give the monomial `h_1^(s) lambda^(ell-s)`.
The zero input position supplies a nonzero constant. Every `h_1` is
nonzero, so this output realizes the entire polynomial space of
degree at most `ell` as the arbitrary input varies. At most `ell`
nonzero samples of this one output cannot recover its constant
coefficient. A pointwise root average with `L>ell` does recover it,
but uses `L` ordinary cyclic convolutions of length `T`. This sample
bound does not exclude a new coupled readout using other outputs.

The exact gauge range is `S_max=ell-beta_0`. A single small positive
lambda must satisfy `lambda<=2^(1-p)` for uniform absolute error
`2^(-p)`: the degree-one case has coefficient magnitude
`|h_1|=1/|1-u|>=1/2`. Its inverse gauge therefore has logarithmic
norm at least `(p-1)(ell-beta_0)`. At `ell=Theta(p/log p)` this is
`Omega(p^2/log p)`. This one-sample scheme does not retain an
`O(p)` or `p*polylog(p)` inverse-gauge guard. This is a bound for
separate gauges around a convolution with a uniform absolute-error
promise on one common grid. A different relative precision supplier
or exact coupled correction needs its own proof.

## Exact carry derivation

Use `w_i=product_(j<i) q_j`, `T=product_i q_i`, and little-endian
digits `n=sum_i x_i w_i`. In ordinary addition, let `c_i` be the
outgoing carry from coordinate `i`, with `c_-1=0`. The output modulo
`T` has digits

    r_i=x_i+y_i+c_(i-1)-q_i c_i,    c_i in {0,1}.

Set `beta_ell=0` and `beta_i=(1+beta_(i+1))/q_i`. Substitution gives

    S(x)+S(y)-S(r)
       =sum_i [q_i beta_i-beta_(i+1)]c_i=sum_i c_i.

For a fixed tensor kernel `K(x)=product_i h_i(x_i)` and arbitrary
input `v`, form the ordinary length-`T` cyclic convolution of
`lambda^(S(x))K(x)` and `lambda^(S(y))v(y)`. Divide its output at
`r` by `lambda^(S(r))`. It is exactly

    Q_r(lambda)=sum_(x+y=r mod T) K(x)v(y) lambda^(sum_i c_i).

Each `beta_i` has denominator dividing `T`. The intermediate input
powers are fractional, but the resulting output powers are integers
from zero to `ell`. A zero carry count means every coordinate sum
stays below its radix. Its output is therefore

    [lambda^0]Q_r=sum_(y_i<=r_i) product_i h_i(r_i-y_i) v(y).

This is the tensor lower Toeplitz map. The same argument applies to
the reciprocal kernels `g_i`. Formal specialization at `lambda=0`
is valid for `Q`; it is not an invertible diagonal gauge and does not
provide a cyclic implementation.

At output zero, the ordinary complement of `w_s` has carries exactly
in coordinates `s,...,ell-1`. The kernel at `w_s` equals the nonzero
coefficient `h_1^(s)`. Hence the basis columns described above supply
all monomials. For any `m<=ell` nonzero sample points `lambda_j`,
the polynomial `product_(j=1)^m(lambda-lambda_j)` has degree at most
`ell`, vanishes at all samples, and has a nonzero constant. The basis
columns realize it with an input. A common rescaling can make that
input a disk input. Thus even nonlinear readout from these samples
of `Q_0` alone cannot recover its constant. Other-coordinate readout
would be a different operator, which is not supplied here.

## Exact finite reciprocal spill

Let `u` be a primitive odd `q`th root, and put

    H_j=product_(s=1)^j(1-u^s),
    h_j=1/H_j,
    g_j=(-1)^j u^(j(j-1)/2)/H_j,    0<=j<q.

The finite q-binomial identity gives `(h*g)_0=1` and
`(h*g)_n=0` for `1<=n<q`. It does not remove the higher coefficients.
Let `P_q(z)=sum_(j<q)h_j z^j` and `G_q(z)=sum_(j<q)g_j z^j`.
Then

    P_q(z)G_q(z)=1+z^q E_q(z),    degree E_q=q-2.

Two exact nonzero endpoints determine that degree. First,
`H_(q-1)=q`. For `1<=k<q`,

    H_(q-k)=q/[(-1)^(k-1)u^(-k(k-1)/2) H_(k-1)].

Consequently `g_k h_(q-k)=-1/[q(1-u^k)]`. Pairing `k` with `q-k`
in the sum uses `1/(1-u^k)+1/(1-u^(-k))=1`, and gives

    (h*g)_q=-(q-1)/(2q).

The highest coefficient has only one product:

    (h*g)_(2q-2)=h_(q-1)g_(q-1)=u/q^2 !=0.

Here `(q-1)(q-2)/2` is congruent to one modulo odd `q`. In particular,

    q=3: P_3(z)G_3(z)=1-z^3/3+u z^4/9.

In the ring `z^q=lambda`, this becomes `1+lambda E_q(z)`, with a
nonconstant `E_q` when `q>=3`. It is not a scalar `1+c lambda`.
The identity is therefore not a scalar compact inverse correction.
Applying or inverting this residual still needs a paid operator.

## Gauge, precision, and complete convolution cost

The recurrence telescopes to

    S_max=sum_i beta_i(q_i-1)=ell-beta_0.

For odd radices, `0<beta_0<1/2`. Write `lambda=2^(-b)` for the
small positive sample. The diagonal gauge contracts, while its inverse
has norm `2^(b S_max)`. The basis column for `s=ell-1` gives
`Q_0(lambda)=h_1^(ell-1)lambda`, with desired constant zero and
`|h_1|>=1/2`. Thus `b>=p-1` is necessary for absolute error below
`2^(-p)` in this direct approximation.

If `|K(x)|<=2^A` and the input is a disk input, the total unwanted
wrap contribution is at most `lambda*T*2^A`. Taking

    b >= p+log2(T)+A+1

is sufficient for small wrap error. A convolution output error is
amplified by the inverse gauge; a common internal grid needs at least
`p+b S_max` precision bits, plus kernel, normalization, and arithmetic
error guards. The root-choice kernel bound gives
`A=O(ell log^3 q_max)`. At `ell=Theta(p/log p)` and polynomial prime
sizes, the sufficient inverse-gauge guard can reach
`O(p^2 log p)`, and the necessary guard is already
`Omega(p^2/log p)`. This is not a lower bound on every carry compiler.

For exact extraction, choose a root-of-unity sample length `L>ell`:

    [lambda^0]Q_r=(1/L)sum_(j=0)^(L-1) Q_r(exp(2 pi i j/L)).

Define the fractional phases consistently using a root of order
`LT`, since `T S(x)` is an integer. They have unit modulus, so this
route has no inverse-gauge norm growth. Kernel magnitude, numerical
phase setup, and the full convolution precision still have a price.
The pointwise averaging construction uses `L` global cyclic products.
Its total processed coefficient volume is `LT`; storing them all also
uses `LT` slots. Streaming can reduce live storage to a constant
number of `T`-slot banks, but retains all `L` product calls. If those
products use ordinary signed integer packing, their child operand
length is `Theta(T*P)` per call: it remains at global scale.

The product of cyclic groups with coprime radices is isomorphic to
`Z/TZ` by CRT. That gives a different exact global packing permutation,
not a free tensor convolution. A common wrap parameter also works
there with weights `1/q_i`; its gauge range is
`sum_i(1-1/q_i)=Theta(ell)`. It has the same small-sample conditioning
issue and still requires the complete cyclic convolution and paid CRT
movement.

Ordinary full multivariate convolution has side lengths `2q_i-1`.
Its complete rectangular volume is
`product_i(2q_i-1)=T product_i(2-1/q_i)`, exponential in `ell`.
Ordinary univariate convolution in the original mixed-radix packing
uses only `2T-1` slots, but merges digit carries into other output
coordinates. For radices `(3,5)`, a kernel term at index two and an
input at index one contribute at index three. The corresponding
tensor lower Toeplitz output at digits `(0,1)` must omit that term.
The marker identity corrects this distinction through constant
extraction; it does not make the unweighted full convolution the
desired operator.

## Exact replay and limits

`verify_common_carry_gauge.py` checks full `h*g` coefficient arrays
in exact small cyclotomic fields for `q=3,5,7`, at roots `a=1,2`.
It confirms both spill endpoints and the extra `q=3` degree-four term.
The multiaxis replay uses nonzero rational tensor kernels on radices
`(3)`, `(3,5)`, and `(3,5,7)`. It checks 11,259 digit-addition pairs,
all constant outputs against direct lower Toeplitz sums, the output
zero monomial columns, nonzero-sample ambiguity witnesses, and root
averaging. These rational kernels test the universal carry algebra;
they are not multiaxis cyclotomic `q`-kernel execution.

The saved receipt passes in 0.119 seconds with 20 MiB peak RSS.
No further tests were run after that receipt. The prior root-choice
packet is preserved. No cheap full cyclic product, new coupled
readout, fixed-tape movement, or multiplication gain is proved.

Prepared with OpenAI Codex assistance. Apache-2.0.
