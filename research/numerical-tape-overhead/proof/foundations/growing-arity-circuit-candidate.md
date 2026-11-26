# A growing-arity rational Walsh circuit

Status: **proved in the stated arithmetic/indexing model; independently reviewed
by the session lead**. See [lead-review-B-var.md](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/verification/S002/lead-review-B-var.md).
The source map and coefficient audit in [polynomial-auxiliary-cost-audit.md](polynomial-auxiliary-cost-audit.md)
supplies the quantitative interface used below. This is not a theorem
about a fixed-alphabet tape machine or about integer multiplication.

This route uses [pairwise-newton-division.md](pairwise-newton-division.md) and the recovered finite
batch-contraction lemma. It differs from a fixed family selected by
universal search: its arity changes with the current active width.

## 1. Quantifying the retained binary routing geometry

The source is Fourier `kernel.tex` at
`openai/math@3344da59991ed94f9ba711217b29c1d760badfa6`. Let `m` be odd and
sufficiently large, put `u=ceil(log_2 m)`, `v=ceil(log_2(u+2))`, and choose
the following even `L` and power of two `q`:

    L = 2 ceil(sqrt(u/v)),
    q = 2^ceil(2 + 2u/L).

The source labels are `[q]^L`, and `t=L/2`. The expansion of
`Gamma(v,w)=1-Delta(v,w)` over `F_2` gives `D_route <= 1+Lq`.
There are at most

    N_charged <= sum_(j=0)^(L/2) binom(L,j)q^j <= 2^L q^(L/2)

charged rectangles. Hence `m N_charged/q^L <= 1` by the choice of `q`.
For each label on either side, the free-rectangle construction has at
most `(1+log_2 q)^L` incidences: at each coordinate there is one equal
choice, or at most `log_2 q` first-differing-bit choices. The charged
incidences add at most `2^L`, bounded by the same quantity. A safe pencil
call bound is therefore

    R_m <= 10(1+Lq)(1+log_2 q)^L.                 (R)

The factor 10 covers both free endpoints and charged common transforms,
using the source `2D_route` calls per incident row. Taking logarithms and
using `log_2 q <= 3+2u/L` gives the absolute-constant estimate

    log_2 R_m = O(sqrt(u log(u+2))).              (R-rate)

Thus `D_route=o(m)`, `R_m=m^o(1)`, and

    q^L <= 4 * 2^(3L)m^2 = m^(2+o(1)).

For all sufficiently large, effectively bounded `m`, one may use the
weaker convenient bounds `D_route<=m`, `q^L<=m^3`, and `R_m<=m`.
These follow from the displayed elementary formulas; no construction
search is needed to select the parameters.

The square-root ceiling is obtained by integer comparison `b^2 v>=u`.
The companion auxiliary-cost audit gives a deliberately coarse explicit
threshold and a source-operation count with `K=50`.

## 2. Finite template after contraction

The small rational construction has `W<2(m+1)` shift rows. With
`h=ceil((log_2 m)/4)` contraction levels it gives arity
`A_m=2(m+D_route-1)` and

    W_m <= 16 q^L(m+1)m^(3/4) = m^(15/4+o(1)),
    a_m := sigma_m/W_m <= C sqrt(m)(R_m+1).      (T)

For large `m`, `2m <= A_m <= 4m`. The predictor/repair representation has
no all-shift factor `2^m`, generalized Clifford dimension or cyclotomic
coefficient rank. The number `2^m` survives only as an optional spectral
table generation/storage bound. The `15/4` is the sum `2+1+3/4` for labels,
seeds and contraction; it is not a multiplication complexity exponent.

Moreover the exact width is a power of two: `W_m=W q^L 8^h` and all
three factors are powers of two. This permits exact batching into
spectator bits, without a padding loss.

## 3. Auxiliary-cost interface

The source counted nonrecursive operations as a constant after fixing a
template. The needed quantitative strengthening is:

**Interface B-poly.** There are absolute effectively specified constants
`K,C` such that the templates have at most `C m^K` ordinary rational-linear
arithmetic/indexing operations per input coordinate. Coefficient bit
lengths are at most `C m^K`. The template and its tables can be generated
in at most `2^(C m)m^K` bit operations and bits. Indexing uses `O(k)`-bit
words at active width `k` when `m<=k^gamma` for a fixed `gamma<1`.

The proof is completed in the companion source-map audit. Its structure is:

* The labels have polynomial size. Construct their Gram matrix over
  `F_2`, compute its radical and bases by Gaussian elimination, and choose
  each local basis in polynomial time and space in `m`.
* Both charged rectangles and total free incidences are polynomial in
  `m`, by (R-rate). Every rectangle is nonempty, so its count is bounded
  by its total incidences. Endpoint maps and query-dependent middle maps
  are explicit polynomial-dimensional linear coordinate or row maps.
* The predictor has polynomially many coefficients and stages. A repair
  table is `O(m)` square with polynomial rational bit lengths. There are
  at most `2^m` spectral tuples. Source-style table selection uses the
  `m`-bit tuple and costs a word lookup, not a scan over all tuples.
* Finite contraction repeats base maps blockwise and its ordinary work
  sums geometrically. Its enlarged batch width remains polynomial. It
  does not require a dense map on an exponential enlarged batch.
* Rectangle weights from `p(d)=product_(j<=L/2)(1-d/(2j))` have numerator
  and denominator lengths `O(L log(L+2))`. Coordinate changes over `F_2`
  introduce signs/phases, without a coefficient field extension.
* Column-prefix enumeration visits a linear number of array positions.
  An extension and coordinate tuple require `poly(m)` word operations.
  Precomputing every `A_m`-bit column tuple costs `2^O(m)poly(m)`, included
  explicitly in the generator bound. It is not declared polynomial.

Physical head movement and scalar bit multiplication are outside this
arithmetic/indexing model. Independent review should check the companion
audit's map-classification table and normalization. No complete tape
implementation is claimed.

## 4. Uniform quantitative rational Walsh circuits

**Theorem B-var.** For even `k`, normalized binary Walsh transforms on `N=2^k` coordinates
have an effectively constructible rational linear-circuit family of
size

    O(N sqrt(k+1) 2^[C sqrt(log(k+2) log log(k+4))])

including source-style word indexing, for an absolute `C`. The circuit is
exact over `Q` for even `k`. Odd widths may use the unnormalized rational
transform or one algebraic `1/sqrt(2)` butterfly if that field is allowed.
This is an explicit subpower envelope in the arithmetic model only.

### Recurrence and proof

Take `K=50` from the auxiliary-cost audit and fix `gamma=1/1000`.
Thus `gamma K<=1/4` and `gamma<1/4`. For large `k`, choose
an odd `m` within a fixed factor of `k^gamma`. Choose inactive width

    r = log_2 W_m,

and let `f` be the largest even integer at most `(k-r)/A_m`. The inactive
bits supply an exact integer number of complete batches. Extra inactive
bits are common spectator coordinates, so all batches follow the same
instruction list. Direct normalized
four-point butterflies handle the even remaining width `k-A_m f`, which
is `O(r+A_m)=poly(m)`. Bounded active widths use direct transforms.

The source recursion and (T), normalized by `2^k`, give

    C(k) <= C_0 m^K + a_m C(f).                 (V)

Enlarge `K` to include the polynomial remainder work. Template setup
`2^(C m)m^K` is absorbed in `2^k` since `m=O(k^gamma)` and `gamma<1`, at
a fixed effective threshold. This can be charged even if setup repeats
at a node: the node has at least `2^k` array coordinates.

Write `F(k)=C(k)/sqrt(k+1)`. The additive term is `O(k^(-1/4))`. Since
`A_m=Theta(m)` and `f<=k/A_m`, the recursive multiplier of `F(f)` is at
most

    b(k)=C_1(R_m+1)
        <= 2^[C_2 sqrt(log(k+2) log log(k+4))].

Beyond an enlarged fixed base threshold, `f<=k^(1-gamma/2)`. Along a
recursion path `u_i=log(k_i+2)` therefore decreases by a fixed factor
until bounded. There are `O(log log(k+4))` levels, and

    sum_i sqrt(u_i log(u_i+2))
       <= sqrt(log(u_0+2)) sum_i sqrt(u_i)
       = O(sqrt(u_0 log(u_0+2))).

Iteration bounds the answer by the depth times the product of
`max(1,b(k_i))`, up to a fixed factor. The depth is absorbed in the same
exponential. This proves the claimed gate bound. QED.

The source arithmetic/indexing proof and a physical caller have different
costs. The latter remains open. The programme must report **No new complete tape
overhead bound** until that stronger bridge is proved.

## 5. Why this is a consequential research gate

Small-batch prediction changes a potentially dominating finite
representation cost and permits growing arity without storing a
generalized Clifford module. The retained routing multiplier determines
the displayed rate. The next question is whether interchange and tape
execution admit comparably quantitative costs. The rational predictor
alone does not supply them.

If some purportedly local map instead takes exponentially many operations
per input coordinate, (V) must use that actual bill. A finite successful
example would not repair this family estimate.

Credit: source routing and Walsh identities are from the pinned OpenAI
manuscripts and their predecessors; contraction is from the recovered
prior programme note. The small-batch route and this candidate assembly
were developed with substantial AI assistance for @CubeJerry. No full
literature novelty claim is made.
