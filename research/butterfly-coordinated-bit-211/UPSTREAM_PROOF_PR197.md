# Completed entrance banks on the emitted PR187 bit word

This applies completed-bank packing, also used in PR186, to PR187's bit
word. It retains PR187/193's conditional all-size interfaces.

## 1. Actual physical chains

Use immutable PR187 commit `201737a1ec4f936e166e2481fb9e88104cb2ccc7`.
Its unmodified full gate emits and independently checks the complete bit
word, including source controls, target chronology, all source/target/dirty
columns, inverse cleanup, prime coverage, and the paid child histogram.
It has 19,348 logical auxiliary roles and 1,760 donor/recipient splices,
hence 17,588 physical chains. There are 3,960 logical gauges:

- 1,760 rank-21 gauges are recipient starts internal to the paid splices;
- 2,200 rank-20 gauges are starts of otherwise unpaired physical chains.

No donor is gauged; donors and recipients are disjoint. The checker verifies
these properties from the emitted word. Only the second group supplies
rank-four entrance residuals. Every other physical chain has rank-24
residual. Interior recipient starts are not counted again as packable ends.
All source, target, copied-center, compensated-read and internal operations
remain in the word and in the retained histogram.

## 2. Exact charts

For each of the 220 distinct rank-20 gauge frames sigma=ker A in Q^24,
use the form G=9I-J. Its G-orthogonal complement has basis obtained from
rows a of A by 15a-(sum a)1. Put these four vectors before a basis of sigma
as the columns of B. The checker verifies orthogonality, both inverse
identities for B, and an independent replay of its elementary factors.
Thus the residual projector I-P_sigma becomes diag(I_4,0) in this chart.
A nongauged residual is I_24.

All charts have at most 186 elementary factors, coefficient numerator
magnitude at most five and denominator at most eighteen. The exact factors
and integral inverse determinants are checked; all their nonzero integers
are below 2^80. They remain invertible at every inherited allowed prime
q>2^80. These are address charts, not new complex payload coefficients.
They do not change PR193's dyadic scalar word.

Embed each chart into 72 coordinates at its original tensor stage and
permute its residual coordinates into the assigned bank interval. This
uses at most 71 coordinate transpositions in addition to the chart factors.
Explicitly, take H=Pi B^-1, with the identity on the other tensor coordinates.
Then H P H^-1=E for the original residual projector P and the assigned
coordinate projector E. The routing below uses this direction of H.

## 3. Banks and legal scheduling

Take three full copies of the three-stage construction. Each physical
chain occurs nine times. Partition its residual occurrences into

- 3,300 banks of six rank-four and two rank-24 items;
- 43,964 banks of three rank-24 items.

Every bank has rank 72. The inventories are exact:

    6 * 3300 = 9 * 2200,
    2 * 3300 + 3 * 43964 = 9 * (17588-2200).

The physical-chain/bank bipartite multigraph has degree nine on every
chain and at most eight at every bank. A deterministic two-color-swap
algorithm supplies a proper nine-edge-coloring. An independent check
verifies all 158,292 incidences at both endpoints. A duplicate color at a
chain is rejected. Color 3j+b denotes stage j and copy b. Thus every
invocation receives every physical chain exactly once, no bank is used
twice within a color batch, and each data copy retains its original stage
order. No incomplete invocation is shared.

For an item chart H and cover index g, connect bank (c,g) to its physical
chain in core (color,gH). Right multiplication by H is a bijection of the
full local-ring GL cover. Every core receives all required chains, and the
data wiring is unchanged. This uses the inherited completed-core contract:
the data map is independent of arbitrary initial scratch and the completed
scratch endpoint separates the residual of each physical chain. PR187's
internal source controls and compensated splices remain inside that core.

## 4. Bank endpoint and arbitrary dirty data

After the chart changes, a bank's residual projectors E_i have disjoint
coordinate intervals and sum to I_72. Let D_P be the ordinary partial-swap
involution associated with a projector P. For disjoint projectors,

    D_P D_Q = D_(P+Q) = D_Q D_P.

Conjugation by a common cover representative and by the common weighted
address map preserves products. Hence the bank's weighted residual
involutions commute and multiply to the required full weighted endpoint.
The inherited ancestor weights are independent of the fresh selector
fields changed by g -> gH; those ancestor fields remain spectators.
This is an operator identity on arbitrary bank contents, not an assumption
of zero-initialized scratch. The reverse order gives the same endpoint.

Controls check both bank patterns on all 144 formal columns over Z/9,
Z/25 and Z/125, with nonconstant unit weights in both orders. They reject
omitted and repeated blocks. These checks support the identity above;
they do not simulate the full cover or prove the inherited Clifford interface.

## 5. Complete histogram and routing

There are 47,264 banks and 3*3,520 data roles, giving W=57,824 and m=72.
Take three copies of PR187's independently recounted histogram and remove
exactly its 6,600 exterior children of rank 60. Every remaining child is
retained. The bank endpoints already equal the required full endpoint,
which justifies removing those exterior corrections.

The resulting rank mass is 4,157,520, deficit 72W-mass=5,808, and maximum
child rank 22. Dividing by three gives normalized W=57,824/3 and deficit
1,936. The full integer profile is used for verification.

Every retained edge still averages over a complete GL cover under a fixed
bijection. Retain the bad-class allowance 10^-16 and 32m² fallback children
per edge. No simultaneous good-class intersection is assumed.

Routing is paid through the inherited ordinary selector, not treated as a
unit tape instruction. For g=g_0+qX, right multiplication by each fixed H
is a finite low-type permutation and an affine map of X, with carry fixed
by g_0. Preserve complete spectators and restore all borrowed rows.
Extending the injective allocation to a permutation and routing out and
back gives the conservative additional selector-call bound

    18 * ((57824-1) + 17588 * 72 * (186+71))
      = 5,859,111,150.

All original scalar work, source controls, readouts, data routing and
cleanup remain paid. The extra calls cost O(K V w^(1-a_old)); they are not
added as small recursive children. K is fixed independently of atom width.
With w=ceil(e^c), this is at most O(K V e^c). The strictly positive gap
c<1-a_ordinary absorbs it into the existing row/adapter toll, changing a
fixed stopping constant rather than the exponent.

W<q for q>2^80, and the maximum child ratio 22/72 is below one half.
The GL stock and internally borrowed digits therefore keep the inherited
O(w log e) digit order. There is no new external polynomial row reserve.
The completed old ordinary selector used for the additional routes is the
same leaf interface used by PR185/187's finite composition. Its all-size,
weighted, restored-row and fixed-tape guarantees remain assumptions here.

## 6. Exact moments and finite leaf composition

For a profile H, certify the sufficient paid moment

    sum_r H_r (r/m)^(1-c) / W
      + 10^-16 * 32m * (#edges) * m^c / W < 1.

Under the inherited recurrence, substituting a width power 1-c makes
a rank-r child contribute (r/m)^(1-c). Division by W normalizes the
parent stock. A strict moment below one gives contraction of the recursive
term; the separate ordinary-leaf and routing tolls must still satisfy the
strict inequalities below. The finite moment alone is not an all-size proof.

The packed coarse saving is 676537710350481/10^18. The next 10^-18 grid
point fails. A second, independent rational logarithm/exponential enclosure
checks both sides of this exclusion and reproduces the original supplier's
coarse saving. Packing strictly improves the paid moment at that original
saving as well.

Start from PR187's already completed ordinary supplier of saving a_0.
Apply exactly three finite stopped-leaf levels using the packed coarse
construction, atom exponent c, and the previous level for ordinary leaves,
routing and high-part exchange:

    a_j = (1-c)c+c a_(j-1) = c-c^j(c-a_0), j=1,2,3.

This is an acyclic composition. All gaps a_j<c<1-a_j are positive fixed
rationals. Each completed leaf restores its own borrowed rows and keeps
outer fields as spectators. The old external leaf reserve remains unused
slack, as in PR185's written proof; no new external stock or growing-depth
program is assumed. This package does not substitute the unattained limit c.

## 7. Assembly, comparison and limits

Use PR193 commit `187e1010ac8b259af8e9b5166f68b64bc27b4b47` for the complex
supplier. Its unchanged histogram has certified saving
700918443859411/10^18 under the finer rational enclosure, above a_3.
Keep its finite scalar/router and external-row bridge. The additional bit
address routes are covered by the ordinary toll above. Set eta=beta=10^-24
in the same 47-constraint balanced assembly. It certifies

    kappa = 135216063303877/200000000000000000
          = 0.000676080316519385.

The next final 10^-18 grid point fails for these fixed supplies and
parameters. The independent audit recomputes the finite leaf recurrence,
all supplier moments and the final controlling margin. The inherited
assembly recomputes all 47 strict inequalities and seven margins.

No all-size compiler, analytic, precision, restored-row or fixed-tape
hypothesis is proved here. PR193 retains its disclosed lack of a globally
renumbered complex word and full Clifford/router replay. This is a
conditional finite construction and composition, not an unconditional
multiplication theorem or a practical speedup claim.
