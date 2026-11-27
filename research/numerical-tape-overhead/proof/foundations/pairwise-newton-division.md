# Constant-tail rational prediction with a small batch

Status: **proved algebraic/enabling result, subject to independent review**.
This note gives no new complete tape overhead bound. It concerns rational or
characteristic-zero binary Fourier templates, with explicit oracle-call and
coefficient bounds. It does not silently specialize rational division to a
small-characteristic data ring.

Source: `openai/math@3344da59991ed94f9ba711217b29c1d760badfa6`, Fourier
`build/repair.tex` (count prediction, matrix-root evaluation, Hermite repair),
`kernel.tex` (shared pencils and binary target/diagonalizer closure),
`binary.tex` (normalized Walsh). The tape comparison uses `build/walsh.tex`
and `interchange.tex` in the November 24 tape paper.

## 1. Mechanism and distinction

The source uses every binary shift, evaluates a multivariate predictor with a
generalized Clifford matrix root, and retains ring identities over
`Z[1/2]`. Here we retain only the characteristic-zero Walsh application:

1. An explicit pairwise-independent set of only `O(m)` shifts gives a
   constant exceptional fraction at every spectral tuple.
2. The count predictor is evaluated in the Newton basis by `O(sqrt(m))`
   pencils and two live row arrays. There is no matrix-root dimension and
   no cyclotomic scalar expansion.
3. Actual predictor discrepancies are nonzero even integers. Dividing by
   them permits two predictor evaluations in the repair, and its inverse
   discrepancies have absolute value at most `1/2`.
4. The previously recovered finite batch-contraction construction removes
   the need to pay for a full spectral conversion axis by axis on a
   constant fraction of the rows.

This changes the finite representation and its quantitative dimension.
It does not solve the routing factor or the end-to-end tape compiler.

## 2. A simultaneous constant-tail shift family

Let `m >= 9`, let `r=ceil(log_2(m+1))`, and set `W=2^r`. Choose distinct
nonzero vectors `a_1,...,a_m` in `F_2^r`; the binary expansions of the integers
`1,...,m` are one explicit choice. For each seed `t in F_2^r`, set

    beta_j(t) = a_j dot t  (mod 2).

These `W` shifts are distinct: the selected vectors include a basis. We
have `m+1 <= W < 2(m+1)`, and `W` is divisible by 16. For every fixed
spectral tuple `k in F_2^m`, define

    c_t(k) = sum_j (k_j + beta_j(t) mod 2).

**Proposition B1 (uniform second-moment tail).** For every `k`, the count
over the uniformly selected seed has mean `m/2` and variance `m/4`.
Consequently, for

    B = ceil(2 sqrt(m)),
    u = floor(m/2 - B),  v = ceil(m/2 + B),  D=v-u,

at most `W/16` seeds have `c_t(k)` outside `[u,v]`, and
`D <= 4 sqrt(m)+3`.

**Proof.** A nonzero linear functional on `F_2^r` is balanced. Two distinct
nonzero binary functionals are linearly independent, so every pair of
their values is uniform. Adding the prescribed bits `k_j` preserves both
facts. The variance of their sum is the sum of the variances, `m/4`.
Outside the displayed integral window the distance from `m/2` is greater
than `B`. Markov's inequality applied to the squared deviation bounds its
probability by `m/(4B^2) <= 1/16`. Since the support has exactly `W` seeds,
the count is at most `W/16`. The bound on `D` follows from rounding. QED.

The tuple is arbitrary. This is not an average over frequencies or a
randomized algorithm. The argument requires only pairwise independence,
because a constant tail is sufficient for the additional contraction.

## 3. Exact Newton evaluation without a Clifford root

Let `Q_1,...,Q_m` be commuting involutions with a common eigenbasis. On the
row with seed `t`, put

    C_t = (m I - sum_j (-1)^beta_j(t) Q_j)/2,
    gamma_t = (-1)^(u - sum_j beta_j(t)).

At spectral tuple `k`, `C_t` has eigenvalue `c_t(k)`. Define

    P_t = gamma_t sum_(h=0)^D (-2)^h binom(C_t-u I,h).

Here the binomial is a rational polynomial. If `u <= c <= v`, the binomial
theorem gives `sum_(h=0)^D (-2)^h binom(c-u,h)=(-1)^(c-u)`, so the
multiplier of `P_t` equals `z=(-1)^(sum_j k_j)`. This is the source count
identity interpreted over `Q`; it does not assert that each Newton
division is valid over every ring to which the source specializes.

**Proposition B2 (charged predictor evaluation).** On `W` arbitrary input
rows, this predictor uses exactly `D` pencil applications, pointwise
rational row maps, and two live arrays of `W` rows. The active pencil has
`W` rows, not `2W` rows.

**Proof.** Initialize `V_0=X` and `Y_0=gamma X`. At step `h=1,...,D`, use

    V_h = (C-(u+h-1)I) V_(h-1) / h,
    Y_h = Y_(h-1) + gamma (-2)^h V_h.

The first update is one source-style pencil on the `W` rows of `V`, since
`C` is a sum of `m` queries with diagonal row coefficients. The array `Y`
is parked during that update; its subsequent update is pointwise. Induction
gives `V_h=binom(C-u I,h)X` and the required partial sum for `Y_h`. At the
end, `Y_D=PX`. Every input row remains an arbitrary independent input to
the *whole* predictor. The parked array and any initialized values are
workspace and are not counted as extra independent inputs. A compiler
that insists on treating both live arrays as one pencil may charge `2D`
instead, which changes only a stated factor; that is unnecessary for the
source pencil interface. QED.

For the normalized Walsh setting the common eigenbasis is unitary. Put
`R=m+D+1`. For all integral spectral counts `0 <= c <= m`, all intermediate
operators in this recurrence have norm at most

    M_m = (D+1) [2R]^D.

Indeed, every factor in a generalized binomial numerator has absolute
value at most `R`, and division by `h!` cannot enlarge the crude bound
`R^h`. Thus `log_2 M_m=O(sqrt(m) log(m+2))`. The coefficients used directly
by a Newton step have `O(log(m+2))` bits apart from `(-2)^h`, which has
`O(D)` bits. They are generated by elementary integer arithmetic in
`poly(m)` bit operations.

This bound concerns ideal query application. Intermediate norms inside a
physical shared-routing implementation of a pencil require a separate
bound.

## 4. Two-evaluation repair with an inverse-gap bound

The following lemma is not restricted to this shift family.

**Proposition B3 (division repair).** Work over a field `K`, or over a
commutative ring in which all the inverses mentioned below exist. Let `F`
have common row multiplier `z` at a frequency, and let `P` have known
diagonal row multipliers `p_i` with actual defect set
`J={i:p_i != z}`, of cardinality at most `s`. Suppose a fixed `s`-by-`W`
check matrix `H` has an invertible `j`-by-`j` submatrix on the columns of
each possible `J`, where `j=|J|`, and every `p_i-z`, `i in J`, is a unit.
Then `F` on `W` arbitrary inputs uses two applications of `P`, a spectral
table on `2s` rows (forward and inverse), and pointwise linear maps.
No assumption `z^ell=1` is required by this algebraic lemma.

**Proof.** Compute `PX` and transform the check rows `HPX,HX`. At each
frequency, their difference is

    H e = H(PX)^hat - z H X^hat,
    e_i = (p_i-z) X^hat_i.

Restricting to an invertible check submatrix recovers `e_J`. Divide by the
known unit gaps to recover `X^hat_J`. Use the transpose of the same
submatrix to choose a check-coordinate vector `a` satisfying

    (H^T a)_J = X^hat_J.

The table returns `a,za`; inverse conversion followed by the fixed lift
`H^T` gives ordinary arrays `Z,FZ`. Return

    PX - PZ + FZ.

At every frequency its error on row `i` is
`(p_i-z)(X^hat_i-Z^hat_i)`. On `J` the second factor is zero; outside
`J` the first factor is zero. The case `J` empty uses a zero table. The
two evaluations are the initial `PX` and `PZ`. QED.

For B2 over `Q` or `R`, every generalized binomial at an integer is an
integer. The term for `h=0` is 1 and every other term is even. Thus every
`p_i` is odd, while `z` is `+1` or `-1`. On the *actual* defect set,

    p_i-z is a nonzero even integer,  |(p_i-z)^(-1)| <= 1/2.   (G)

It is necessary to use the actual defect set. An outside-window count can
accidentally give the right answer, and division by its zero gap would be
invalid. This distinction is included in the verifier.

### Explicit check matrix and table norms

Take `x_i=i/W`, `0 <= i < W`, and `H_(h,i)=x_i^h`, `0 <= h < s`.
For a defect set of size `j`, use its first `j` rows, obtaining a
Vandermonde matrix `V_J`. The Lagrange-polynomial formula gives

    |(V_J^-1)_(a,b)| <= (2W)^(j-1),
    ||V_J^-1||_2 <= j (2W)^(j-1) <= B_s := s(2W)^(s-1).

The numerator coefficient sum is at most `2^(j-1)` because every node
lies in `[0,1]`; the product of the nonzero node spacings has magnitude
at least `W^(-(j-1))`. These observations prove the displayed estimates.

The table from the input pair of check vectors to `(a,za)` has norm at
most `B_s^2`: taking the difference has norm `sqrt(2)`, inversion of
`V_J` costs at most `B_s`, gap inversion costs at most `1/2` by (G),
transpose inversion costs at most `B_s`, and output duplication costs
`sqrt(2)`. Also `||H||_2 <= sqrt(sW) <= W`. Therefore the logarithms of
the table and lift norms are `O(m log(m+2))` when `W=O(m)` and `s=W/16`.

The norm estimate is not a bound on rational denominator length by itself.
A common-denominator calculation gives the safe bit-length bound

    O(s^2 log(W+2) + s D log(m+D+2))

for table entries: use the squared Vandermonde determinant and the product
of the `j` nonzero gaps as a common denominator. This is `poly(m)`.
There are at most `2^m` different spectral tuples. Constructing the entire
table list therefore takes `2^m poly(m)` bit operations and bits using
ordinary exact polynomial/matrix arithmetic. Storing or generating these
tables is charged; finite constructibility is not declared free.

## 5. The finite contraction and resulting call invoice

The earlier local note is preserved at [batch-contraction-repair.md](batch-contraction-repair.md).
Its original path was [batch-contraction-repair.md](batch-contraction-repair.md) in the
preceding session cache; its SHA-256 on recovery was
`1ee4dc077d82e0d4c900f26dfb4cce026407ef830bb7cab918427f8663f3830e`.
The present note reuses, and does not claim to originate, its finite
two-phase composition. The lead preserved its recovery provenance and
replayed the current note's verifier in an isolated copy. Current lead
algebraic review found no objection; this is AI review, not human or
formal-kernel verification.

For clarity the needed implication is stated here. Take odd `m`, as
required by the binary source kernel's auxiliary-axis identity. Suppose the source
routing has `q^L` labels and call cost `R_m` per original row per pencil.
The binary arity is `A=2(m+D_route-1)`. The base batch has

    W_0 = W q^L

independent input rows, with no coefficient-extension multiplier. Each
repair phase has `2s q^L=W_0/8` rows. Its non-spectral axis-call bill is

    a_m W_0,  a_m=2 D R_m,

including both predictor evaluations. For integer `t>=0`, bundle
`W_t=W_0 8^t` inputs, recurse separately on the two pending conversion
phases, and use the direct `A`-axis fallback at depth zero. Exact row
divisibility gives

    sigma_t/W_t <= a_m sum_(h=0)^(t-1) 4^(-h) + A 4^(-t).

No cyclic same-size algorithm is assumed: `t` is a finite unrolling
parameter and the fallback terminates it. Normalized binary Walsh is its
own inverse, and the source's query product is monomially equivalent to
that Walsh transform, so both conversion directions are covered.

When `D_route=O(m)` and `t=ceil((log_2 m)/4)`, the result is

    sigma_t/W_t = O(sqrt(m) (R_m+1)),
    W_t <= 16 q^L (m+1) m^(3/4).

Thus the predictor/repair part has a polynomial batch multiplier instead
of the all-shift/generic-Clifford/cyclotomic multiplier. The source label
factor `q^L` is retained explicitly. This is a quantitative finite-template
improvement, not yet an asymptotic improvement in multiplication.

The two work arrays, the checks and returned corrections use a fixed
multiple of the original volume at the ideal row-program level. The
additional contraction has child volume `V/8`, so parked volumes form a
geometric series. Dense `H` operations take `O(W^2)` scalar operations
per spatial coordinate at the base level, or `O(W)` per original row;
their corresponding volume-normalized bill is multiplied by at most
`sum_h 4^(-h)=4/3` by the finite unrolling. This cost must appear in a
growing-parameter recurrence even though it is a constant for fixed `m`.

## 6. Binding gaps and forbidden inference

1. The source routing factor `R_m` has not become constant. A fixed factor
   above the critical `sqrt(A)` call ratio still compounds in spatial
   recursion. No endpoint follows from removing a `sqrt(log m)` tail cost.
2. A growing-arity theorem must charge the explicit local `O(W)` bill,
   routing tables and coefficient arithmetic, and ensure that seed
   generation, table generation, norms and batch thresholds fit every
   local volume. The formula above alone is not that theorem.
3. The characteristic-zero Walsh predictor is compatible with rational
   fixed-point arithmetic after a precision analysis. Its denominators
   are not all powers of two. A complete tape caller must prepare and
   multiply these coefficients, charge rounding, and establish a common
   visited-cell cap with the routing machinery included.
4. The tape interchange proof routes over a small characteristic `p`.
   The Newton step `1/h` fails if `p` divides `h`; merely reducing the
   rational circuit mod `p` is invalid. Choosing `p>D` changes the label
   geometry and its costs. A p-adic lift would need a compatible routing
   identity over `Z/p^K`, which the source rank argument does not supply.
5. The table norm bound controls this rational repair, not the norms of
   the source's expanded physical routed pencils. Those remain separate.

The decisive next questions are whether the small rational representation
admits a quantitatively efficient physical caller, and whether a distinct
small-characteristic division-free evaluator can replace its Newton
division without reintroducing a huge full-rate dimension.

## 7. Coverage, tests and credit

Read in full for this route: Fourier `repair.tex`, `kernel.tex`,
`binary.tex`, `layers.tex`; tape `walsh.tex`. Tape `integers.tex` and
`interchange.tex` were read in relevant part; no full paper or Lean build
is claimed. Repository `AGENTS.md` and `CONTRIBUTING.md` were read.

Finite verification is provided separately. It tests count identities,
pairwise moments, actual-defect selection, field repair as a matrix
identity, negative controls and the exact call invoice. Finite checks do
not prove a tape implementation or the asymptotic claims left open above.

Credit: @CubeJerry; the OpenAI November 24 Fourier and tape manuscripts
and their cited predecessors; the recovered earlier programme's finite
batch-contraction construction. The pairwise/Newton/division combination
and explicit bounds here were developed with substantial ChatGPT research
assistance. Root and Route C independently investigated compact scalar
factorizations during this session. No claim of exhaustive literature
novelty or of authorship of the source results is made.
