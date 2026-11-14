# Audit of the actual encoded Gaussian coefficient contract

JoyboyBrian, with substantial OpenAI Codex assistance; Apache-2.0.
This is a source-relative written proof plus independent-algorithm finite
checks, not formal-kernel or independent human acceptance. It audits PR3851's
encoded producer, not the different host Gaussian.exponential audited in
`gaussian-scalar-backend-audit`.

## Quantified statement

For integers P,F>=1, a rational 0<=f<=F, a Boolean growth flag and integer
sigma>=0 (None means zero), the pinned Exponentials.grid_interval returns
integers l<=u such that, with eta=2^-P,

    l eta <= 2^-sigma exp((+1 if growth else -1) pi f) <= u eta,
    u-l <= 2.

Consequently coefficient, which returns l, has downward error <2eta. All
Exponentials constructor, Taylor-range, interval-width and final-width checks succeed
mathematically. Termination is for every finite represented input, with the
encoded Count/Rational operations and ownership semantics retained. There
is no assertion that arbitrary non-admitted input succeeds. In particular
negative f and f>F must be rejected. No global H row-gap theorem follows.

## Directed primitives and Machin interval

`quotient(a,b,True)` is ceil(a/b), because it increments precisely for a
nonzero remainder; the ordinary branch is floor. `ceil_shift` performs the
right shift and increments precisely when a discarded bit is one. Reading
beyond the number's right marker does not add a discarded bit. Both preserve
the input head by rewinding. Thus nested downward divisions and nested
upward divisions preserve the corresponding exact rational bounds.

Write X=4F, k=ceil(log2(8(X+1))), H0=P+X+k+16, c=ceil(log2 H0),
R=P+4X+4k+2c+64, h=2^-R, J=ceil(R/4)+8, N=ceil(R/3)+8.
All are the actual Count computations, including remainder-based ceilings.
For this domain H0>=27, R>=115, R<5H0, N<=R/2, and R>=4k.
For the R<5H0 bound use c<=H0/2, valid for integral H0>=4:
R<=P+4X+4k+H0+64<5(P+X+k+16), since P>=1.

The actual nested archive's twiddle_setup.arctangent encloses each of J
alternating terms using [floor(term/h),floor(term/h)+1]h. The signs reverse
the endpoint order for negative terms. The next omitted arctangent term
has magnitude at most 1/5^(2J+1)<h because 25^J>16^J>2^R;
the 239 tail is smaller. Its symmetric one-unit padding is sufficient.
Machin's identity pi=16 atan(1/5)-4 atan(1/239) then encloses pi with width
(20J+40)h<=7Rh. The exact signs and nested source bytes are authenticated.
The classical bounds 3<pi<16/5, together with this tiny width, also give
the constructor's strict 3<pi_lower<=pi_upper<4 checks. For example pi>25/8
and pi<22/7 follow from elementary rational series enclosures; the independent
arcsine oracle checks stronger rational bounds without using Machin.

Multiplication by f and outward quotient yield width at most (7RF+2)h.
The upper x endpoint is <X: pi<16/5 and (7R+1)h<4/5 for R>=115.
After division by 2^k and outward rounding, the y interval obeys

    Delta_y <= (7R+65)h/32 <= Rh/4,
    0 <= y_lower <= y_upper <= 1/8.

Indeed 2^k>=32F+8 and the extra shift adds less than 2h. For the range,
X/2^k<=X/(8(X+1)); the missing margin is at least 2^-k>=h.
This derives the actual range check, not just an assumption about exp inputs.

## Taylor termination, early exit and squaring

The true positive Taylor terms for every y in the interval are enclosed by
the actual lower/upper recurrence. In real R-grid units, each nested rounding
adds at most 2h per endpoint. Upper terms stay <=1 by induction, since their
next value is <= previous/8+2h<1. For term-width d_j,

    d_j <= d_(j-1)/8 + Delta_y + 4h <= 2Delta_y+5h.

At early exit the added upper term is <=h; all following exact term ratios
are <=1/8, so the omitted positive tail is <=h/7. At fixed exit after N
updates the tail is <(8/7)2^(-3(N+1))<h. The extra upper unit therefore
suffices in both branches. Closing the encoded iterator on early exit is
part of the unchanged source's scratch-release path.

The accumulated interval has lower endpoint >=1 and width
E0<=N(2Delta_y+5h)+h<=R^2 h. Comparing upper terms with the exact series
at y_upper gives rounding excess <=(16/7)Nh+h<=3Nh. Thus its upper endpoint
u0 satisfies log(u0)<=y_upper+3Nh.

Let li,ui denote the endpoints after i outward squarings. They remain >=1,
and log(u_(i+1))<=2log(ui)+h. Consequently

    sum_(i=0)^(k-1) log(ui)
      <= (2^k-1)y_upper + 2^k(3N+1)h < X+1.

The last inequality follows from 2^k y_upper <= x_upper+2^k h and
2^k(3N+2)h<1. To see the latter uniformly, use k<=R/4,
3N+2<=2R<=2^(R/2), so the product is <=2^(-R/4)<1.
Widths satisfy E_(i+1)<=2ui Ei+2h. Since each factor 2ui>=2,
unrolling the recurrence and summing the reciprocal geometric majorant gives

    Ek <= 2^k exp(X+1)(R^2+2)2^-R
       < 2^(-P-2X-3k-57) <= 2^(-P-83).

Here R^2+2<=32H0^2, H0<=2^c and exp(X+1)<2^(2X+2).
This proves the positive_interval strict width check (<eta).
No finite sweep in P,F replaces these inequalities.

## Reciprocal and final normalization

For decay, reciprocation reverses endpoint order. On [1,infinity) it cannot
increase width; the two outward R-grid quotients add less than 2h. Growth
keeps the original enclosure. Both branches therefore have width <eta/2.
Scaling by 2^-sigma does not increase it. Final outward P-grid rounding adds
less than 2eta to width. The endpoint difference is an integer number of
eta units and is strictly below 5eta/2, hence at most 2eta. The actual source
accepts difference<=3; the proved tighter bound implies that check. The pre-final normalized interval has width <eta/2 and the final
lower floor loses <eta, so coefficient error is <3eta/2<2eta. The
lower coefficient is an approximation, not necessarily the exact irrational
floor. Changing this contract to exact-floor equality would be unjustified.

## Binding every Axis argument family

The actual Axis requires s<t<2s and 2w<s, all positive integers. Put
rho=t/s, theta=(t-s)/s. It computes q_j=floor(rho*j+1/2), beta_j=rho*j-q_j,
so -1/2<=beta_j<1/2, including half-up ties. Its declared F is the maximum
of ceil(u/(4theta)) and ceil(u(rho*w+1/2)^2).

The weight argument u(1/4-beta_j^2)/theta is in [0,u/(4theta)]. The
normalized growth diagonal uses u beta_j^2<=u/4 with sigma=2u. For reflected
rows, beta_(s-j)^2=beta_j^2: ordinary ties change the sign, while half ties
remain -1/2 on both sides. This justifies the source's squared-offset check
and reuse; it is not an unproved identity of signed beta values.

The nonzero kernel argument u rho d^2, d<=w, is <=u(rho*w+1/2)^2.
For a cross-cell entry let delta be the chosen signed cyclic distance,
|delta|<=w. Since rho*s=t is integer,

    rho*delta+beta_i = beta_j + m,  m an integer.

The nearest-integer property gives |beta_j+m|>=|beta_j|, including ties.
Thus f=u[(rho*delta+beta_i)^2-beta_j^2]>=0, while
f<=u(rho*w+1/2)^2. Direct and wrapped branches both satisfy the prepared
domain. The zero-distance kernel and the H matrix diagonal bypass the backend
by returning exactly one. The normalized diagonal still invokes growth,
including at beta=0.
This proves the coefficient-call domain for every admitted Axis tuple. It
does not prove nonzero rounded weights for arbitrary P: positive exact
weights may truncate to zero. That is a separate Axis admission check and
production precision obligation, expressly retained.

## Independent checks and costs

The oracle uses pi=6 asin(1/2), a positive series whose consecutive-term
ratio is <1/4, so eight times the next term bounds the pi tail. It computes
exp(-x) by alternating even/odd rational sums at x<=1/4, applies outward
dyadic squaring, and obtains growth by reciprocal. Thus the source positive
Taylor/Machin paths are not their own numerical oracle. Every source output
must contain the entire finer oracle interval; mere overlap is insufficient.
Oracle source/self-tests are frozen before source-output capture. This is
algorithmic separation within one AI-assisted contribution, not a claim of
independent authorship or human verification.

The adapter executes unchanged encoded Axis construction and isolated boundary
calls with no_decode active. It records raw arguments, endpoints, setup grid
and branch counters; decodes only after protected execution returns. It also
checks the actual argument multiset against the rational formulas above,
including reflection, wrapped differences, growth and normalization. It
supplies no approximation or host arithmetic to the source producer.

The retained ordinary-arithmetic bound per coefficient preparation/application
is O(R^3+(R+B_f)^2), plus O(sigma+R) for the explicit final shift scan and
storage for its encoded extent. Machin and O(R) Taylor iterations operate on
O(R+X+B_f)-bit carriers, X<=R; k squarings and reciprocal divisions fit that
coarse bound. It is not a bit-length-only tariff for enormous sigma. Actual
Axis repeats coefficients and pays matrix setup/storage; the audit does not
claim a free cache, a new machine-step leading constant or faster setup.
Independent-oracle memory and observer snapshots are verification overhead.

## Open next questions

Compose these directed scalar errors with the actual weight ratios and
cross-cell entries to obtain the production old-H perturbation bound, then
bind the ideal matrix row gap. Preserve the separate positive rounded-weight
admission and exact arithmetic/movement contracts. The present theorem does
not install global row dominance, LU caps, online Core error, tensor/CRT
admission or a multiplication theorem, and changes no selected frontier.

Credit Jose Manuel/jmbarrancoml PR3851 for the physical encoded producer and
its original precision proof, the retained physical-ring Machin runtime and
Gaussian lineage, and the distinct prior scalar-backend audit. Frozen inputs
and source-specific notices remain unchanged.
