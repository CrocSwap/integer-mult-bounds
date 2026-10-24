# Direct native recount of the actual Gaussian maps

The concrete result is a faster native evaluation of the source's forward Gaussian map S and inverse N^-1. It is independent of any Turing-machine implementation. It combines the paid Gaussian block/Hankel construction in GAUSSIAN-CHIRP.md, NATIVE-EXP-TABLE.md, NATIVE-BANDED-INVERSE.md and the ordinary bounded-word FFT. No complete improved multiplication exponent is asserted.

## Actual forward map: O(t log p), including its periodic boundary

The source has s<t, alpha>=2 and alpha<sqrt(p), with s/t bounded above and below by positive constants. Its actual forward map is

    (S u)_k = (1/alpha) sum_(j in Z)
                 exp[-pi (j-(s/t)k)^2/alpha^2] u_(j mod s).

Inputs satisfy |u_j|<=X with log(X+1)=O(p), target error is 2^-P with P=Theta(p), and p=Theta(log n). Select a radius R=Theta(alpha sqrt(p)) such that, with a=pi/alpha^2,

    a(R-1)^2 >= P ln 2 + ln(32(X+1)),
    a(2R-1) >= ln 2.

These conditions can be selected by rationally certified squared comparisons and a doubling loop; no exact square-root instruction is needed. For any real center z, splitting the shifted lattice by its two sides and comparing successive terms gives

    sum_(|j-z|>R) exp[-a(j-z)^2]
       <= 4 exp[-a(R-1)^2] / (1-exp[-a(2R-1)]).

Consequently the periodic omitted tail, including the 1/alpha prefactor, is below 2^(-P-1), after the displayed fixed guard. This bound covers the infinite lattice; a finite s-times-largest-entry bound alone would not establish it.

Take a power-of-two block width q=Theta(R). Partition output k and the extended source indices j into q-blocks. Retain a whole source/output rectangle whenever some pair lies within the radius R; each output block meets O(1) source blocks because both slopes are constant. The centered exponent on every retained rectangle is O(p). The exact diagonal-Hankel-diagonal identity in GAUSSIAN-CHIRP.md reduces each rectangle to one paid linear convolution of length O(q), with O(p) magnitude/accuracy guards and O(q log q) native word work. It is essential to evaluate the whole rectangle, rather than reintroduce an entrywise truncation mask.

For the actual asymptotic line lengths, s is superpolynomial in p and hence s>2R. Centers lie in [0,s), so only the three source-period copies in [-s,2s) are needed for retained blocks. Access u_j by j mod s, using bounded-word arithmetic; this adds a constant number of boundary blocks. No scan of infinitely many copies is performed. The tail estimate above accounts for all omitted copies.

There are O(t/q) rectangles. With O(log p) coefficient/precision guards and the ordinary paid exp/root preparation, the complete forward map costs

    O(t log p + n^eta polylog n)

for any fixed small eta>0. Its working words have a sufficiently large fixed constant times log n bits. Prefactor multiplication, root generation, FFT kernel transforms, gathering, summation and periodic boundaries are included. This replaces the literal window-product count O(t alpha sqrt(p)), not merely its tape movement.

## Actual inverse: O(s(1+p/alpha^2))

The source defines N=C T D, with q_i=floor((t/s)i+1/2), beta_i=(t/s)i-q_i and |beta_i|<=1/2. Its actual entries and the explicit tail proof are given in NATIVE-BANDED-INVERSE.md. Truncating to periodic distance h=O(1+sqrt(p)/alpha) gives row-sum error as small as 2^-P, because the tail is bounded by

    4 exp[-pi alpha^2 h(h+1)].

The predecessor bound ||N-I||<2^(-alpha^2 theta) is eventually at most 1/8. Form the positive truncated coefficients using the paid exp table. The ordinary-band part is strictly row diagonally dominant; its factors have pivots uniformly bounded away from zero and no unbounded element growth. The periodic corner entries are a literal rank-at-most-2h update. The Woodbury Schur matrix has norm-distance at most 1/3 from identity, so its small inverse is itself computed by the same proved elimination, rather than supplied by an oracle.

Band factorization, 2h right-hand solves, the small Schur factorization, matrix formation and final recovery together cost

    O(s(1+h)^2) = O(s(1+p/alpha^2)).

The storage is O(s(1+h)). Accuracy P+O(log s+log h) bits suffices by the explicit rounding/residual proof. This remains O(log n). The external diagonal D and selector C cost O(t) extra work with the paid coefficient table. Shared exp/root preparation adds n^eta polylog n, once for the complete family.

## Sum over the actual tensor axes

Let T be the padded array size, d=Theta(p^epsilon), and alpha^2=Theta(d sqrt(p)), as in the source. There are T/t_i disjoint forward lines along axis i, and comparable source/target axis lengths. The sum of the forward costs is O(T d log p). The sum of the inverse costs is

    O(T[d + d p/alpha^2]) = O(T[d+sqrt(p)]).

Including diagonal maps, selectors and setup, the complete Gaussian axis adapters therefore cost

    O(T[p^epsilon log p + sqrt(p)] + n^eta polylog n).

A stronger actual reuse bound is available because all parallel fibers of one axis share the same s_i,t_i,alpha and hence the same matrix N. Factor the ordinary band part and prepare X=A0^-1 U and the small Schur factors once per axis. A new right-hand side then uses only two band triangular solves, a small Schur solve and Xz recovery, for O(s_i(1+h)) work. The Schur O(h^2) solve is covered because s_i>h. Across all fibers, the inverse contribution is O(T d(1+h)); the one-time factor work is O(d r(1+h)^2), where r=max(t_i)=2^{Theta(p/d)}=n^{o(1)}. With h=O(1+p^(1/4)/sqrt(d)), the complete stronger adapter bound is

    O(T[p^epsilon log p + p^(1/4+epsilon/2)]
      + n^eta polylog n + n^{o(1)}).

Numerical factor errors do not accumulate across independent right-hand sides; each satisfies the same explicit operator/residual error bound. All stored factors and Woodbury columns are paid for in O(d r(1+h)) preparation space. This is direct factor reuse of an explicitly stored input-independent map, not an oracle or an uncharged matrix inverse.

This is a strict asymptotic native improvement over direct dense-window evaluation. The direct forward loops alone cost O(T d alpha sqrt(p))=O(T p^(3/4+3epsilon/2)); the new forward contribution is O(T p^epsilon log p). The inverse uses direct band elimination instead of repeated Neumann window applications. These are changes to concrete arithmetic algorithms, not a division of a TM-time estimate by word width.

## Positive O(1)-amortized selected-bit metadata lemma

Suppose a simultaneous layer selects d of the L address bits, with d=(log n)^epsilon for a fixed epsilon<1 and L=O(log n). For each of its O(log n) levels, prepare an array deposit[j], 0<=j<2^d, mapping a compressed selected-bit index to its physical-bit submask. Explicit construction costs O(2^d poly(d,log n)) per level, and total preparation is n^o(1). Any fixed rational-kernel template's permutation and quarter-phase tables on these d bits can be prepared with the same type of paid bound.

Let M be the complementary-address mask. Its submasks can be enumerated in increasing order using

    next = (current-M) & M

in modular word arithmetic, stopping on return to zero. For each complementary base and each j, base OR deposit[j] is its physical address. Every input point belongs to exactly one such pair, and all T gathers/scatters take O(T) word instructions. No PEXT, PDEP, popcount oracle or d-step extraction is required per point.

For a separately applied tensor twiddle diagonal, scan coordinates in natural mixed-radix odometer order. Maintain the sum of the per-axis exponent contributions; only changed axes are updated. Since every radix is at least 2, the total number of axis changes is O(T+d), so the metadata work is O(T+d), with bounded-word arithmetic and the paid root-power queries. This lemma applies when the phase is the actual separated sum of per-axis contributions, as in the common tensor level; it does not assert the same cost for an arbitrary nonseparable phase function.

## Verification scope and next assembly

The real ordinary-band bounded-word reference implementation band_solve.py was independently rerun: 20 systems, 208 rows, maximum raw arithmetic width 193 bits under a 256-bit budget; singular and overflow controls passed. Fraction is confined to its external exact residual oracle. The implementation uses exact product accumulation in substitution and fixed-grid elimination. Its operation counter is an instrumented model, not an emitted RamStd instruction certificate. The periodic real Woodbury implementation periodic_solve.py was also independently reviewed and rerun: 3 periodic systems, 9 right-hand sides reusing the same prepared factors, 123 rows, maximum raw width 192 bits. Its preparation constructs the ordinary factors, the 2h inverse-update columns and small Schur factors exactly once; each new right-hand side performs O(s h) reuse work with no refactor. These periodic fixtures evaluate exact residuals with an external Fraction oracle. The actual Gaussian N is real, so a complex input is handled by separate real and imaginary right-hand solves, doubling only the constant. The general complex-matrix elimination proof remains informal; it is not an executable path covered by these real fixtures.

The rational closed Gaussian/Walsh kernel from #956 also has the positive native precision lowering proved in NATIVE-STABILITY.md. Choosing epsilon=1/8 suggests a conservative full native saved-exponent assembly once its tensor caller, arbitrary twiddles, record products, cyclic embedding, precision and recovery are all connected and replayed. That complete assembler is not emitted here. In particular these component results are not a new best kappa and are not a completed proof of a faster full cyclic transform.

Credit: upstream Gaussian resampling and inverse estimates are predecessor results with their Harvey-Hoeven references; the rational kernel is #956 with its stated lineage; chirp convolution, FFT, diagonal dominance and Woodbury have classical precedents. The contribution here is the explicit native finite-word construction, quantitative conditioning, paid preparation and actual Gaussian caller recount. Prepared for Dugongue with substantial OpenAI Codex assistance.

Additional root integration: periodic_solve.py now replays real Woodbury systems with reusable factors. gaussian_inverse.py constructs the actual positive Gaussian N entries using a paid Machin pi series and signed exp tables, then solves three periodic systems (55 rows), with reference residual below 2^-100. gaussian_block.py evaluates 12 concrete Gaussian rectangles (45 outputs), checked below 2^-60. These are finite operational-model fixtures, not a full cyclic-transform replay; finite Decimal sums are independent validation only.
