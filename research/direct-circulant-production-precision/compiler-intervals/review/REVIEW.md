# Separate review of source-ordered compiler cuts and relative intervals

**Disposition: accept the scoped mathematical result under its stated
source premises.** The reviewed author proof is `norm/package/PROOF.md`,
SHA-256
`e942012e66adc2d696cde3fedd6ae9c73df98e77a71b16e5004f5a74ccdfaa07`.
The explicit definition of C requested below is included in this reviewed
revision. It is the only clarification from the initial frozen draft; no
numerical constant or mathematical conclusion changed.

The accepted scope is a statement about exact stored one- and two-wire
mathematical gates, including any subset of a matching layer. It is not
a claim about partially overwritten physical outputs, workspace lifetimes,
the complete multiplier or any canonical assumption discharge.

## 1. Primitive partial matchings

The retained `engine.Builder` adapts the authenticated FFT/shear syntax,
constructs exactly two spectral matchings and checks the certified rational
phases are unit modulus. Its butterfly has columns `(a,b)` and `(b*w,-a*w)`;
`a^2+b^2=1` and `|w|=1`, so these columns are exactly orthonormal. Independently
prepared twists are also exactly unitary. Each other primitive gate stays
inside one of the two banks. The two spectral layers consist of disjoint
lower-shear pairs.

For a bank-diagonal unitary V and lower shear S(A), conjugation changes A
to `Vy A Vx^-1` without changing its norm. Moving all bank unitaries to one
side of an arbitrary gate interval leaves a sum of at most two such
transformed masked spectral diagonals. A partial matching merely replaces
some diagonal entries by zero. Its norm is no greater than the entire
diagonal's norm. Consequently the same `1+Mg+Mh+2v` cap holds for the
interval and its exact inverse. This argument is valid over the complex
numbers and uses no commutation between the two transformed A matrices.

This does not improve Brian's #4976 generic interpolation theorem. An
arbitrary nonunitary compensating factor can violate the source-specific
claim. Nor does replacing a complex twiddle by its conjugate reverse the
entire butterfly. The source's complete inverse gate/order is necessary.

## 2. Triangular and generator hierarchy

The actual `Triangle.parallel` compares the siblings' `(start,stop)` macro
partitions and rejects overlapping macro supports. Thus the fragments at
this level really are direct sums. The source admission gives each shear
fragment cap seven and stored scalar reciprocal cap four. Its macro
perturbation argument gives completed prefix cap `2 Btri` and remaining
suffix cap `4 Btri`. Multiplication by at most seven yields `28 Btri`,
which is strictly below the retained `3200 m^3 = 32 Btri` allowance.
Matching-subset cuts add no extra interpolation constant.

I checked the generator checkpoint formulas directly without commuting
any of p, h, A or C. The four chronological calls are

    diag(p,I); S(h); diag(p^-1,I); S(-h).

They compose to `S(h(p-I))`. If A is the sum of preceding **stored** term
operators and C is the sum of the current stored term **plus all later
stored terms**, the four displayed prefixes and suffixes in the author
proof follow by matrix multiplication. In particular the suffix after
the first call is `L(p^-1, C p^-1)`. Defining C as only the later terms
would make that formula wrong. The retained `GENERATOR-PROOF.md` §3
already gives the intended inclusive definition; the author has made
it explicit in the accepted supplement.

The inverse formula is `L(B,D)^-1=L(B^-1,-D B^-1)`, with this order.
Using `||p||<=2`, `||p^-1||<=4`, `||h||<=k` and `||A||,||C||<=a`
gives the stated common checkpoint cap `4+4a+2k`. The final checkpoints
use the actual completed earlier/later term sums rather than bounding
every individual term again. Combining one unfinished child with one
checkpoint gives the original Hgen. A rank-zero child is an identity
atom with no active fragment. The conditioning, generator identities,
phase certification and coefficient-defect assumptions remain inherited.

## 3. Source-time factorization and disjoint active atoms

For this recursive source DAG, an upper atom precedes all descendants,
and the lower atom follows them. Incomparable atoms have disjoint logical
supports even if the physical wire list is permuted. Their exact stored
endpoints commute for that reason, not because all source matrices commute.

At a cut in layer k, atoms with `stop<=k` form a downset I. A zero-duration
atom is included at its actual timestamp, even if that timestamp is also
the first layer of a descendant. Atoms with `start<=k<stop` are an antichain;
their supports are disjoint and `I union A` is also a downset. A selected
subset may finish all gates of an active atom's last matching layer while
the timestamp convention still regards that atom as active. Its remaining
fragment is then identity, so the factorization remains valid.

Commuting only disjoint work gives

    C(u) = Fu Qhat(Iu).

The prefix factor Fu is a direct sum of active local prefixes with identity
elsewhere. Its norm and inverse norm are bounded by H, independent of the
number of active atoms. The suffix identity uses the analogous direct sum
of tails on the right of the unstarted endpoint product. Multiplying the
predecessor completed-endpoint bounds by H therefore proves Result A with
the stated `K=2 L0 B H`.

## 4. Independent proof of the relative-interval envelope

For two source-ordered cuts, `Iu` is a subset of `Iv`. List the first
downset, then the difference, then the complement in a topological order.
Every predecessor of an atom in a downset is already in that downset, so
this is a legal **single shared order**. Products of stored or ideal
incomparable endpoints commute, hence these products equal the source
products regardless of the legal order chosen within each block.

For that shared order let `Qj=Aj...A1` and `Qhatj=Ahatj...Ahat1`. Define

    Gj = Qj^-1 (Ahatj-Aj) Q(j-1),
    Zj = Qj^-1 Qhatj.

Direct substitution gives `Zj=(I+Gj) Z(j-1)`. The factor order matters.
If `i=|Iu|` and `j=|Iv|`, then

    W = Zj Zi^-1 = (I+Gj)...(I+G(i+1)),
    Qhatj Qhati^-1 = Qj W Qi^-1.

Both equalities are exact without commutativity. Inverting reverses their
factor order; `Zi^-1 Zj` is generally different from W. The source premise
bounds every ideal downset and inverse by B, so `sum ||Gj|| <= theta`.
For nonnegative gl with sum at most theta<1,

    product(1+gl) <= 1/(1-sum gl),
    product(1-gl)^-1 <= 1/(1-sum gl).

The first follows from elementary symmetric sums bounded by powers of
the total sum; the second follows by induction from
`product(1-gl)>=1-sum gl`. Neumann inversion then bounds W and W inverse
by `1/(1-theta)`. Therefore the relative completed endpoint and its inverse
have norm at most `B^2/(1-theta)`.

Finally,

    C(v) C(u)^-1 = Fv [Qhat(Iv) Qhat(Iu)^-1] Fu^-1.

Both boundary factors cost H. This proves the advertised interval and
inverse cap `B^2 H^2/(1-theta) <= (4/3)B^2 H^2 < 2B^2 H^2`.
No norm of the ideal whole endpoint is needed in this relative argument;
removing the old L0 squared factor is justified. The argument includes
identical completed sets and multiple simultaneous active atoms. In one
matching layer, actual time-ordered subsets are nested, and the same
formula applies. Empty or full local fragments cause no exception.

Substituting the separately retained production inequalities gives
`2 B^2 H^2 <= 2^189 t^100`. That arithmetic is correct. Propagating this
gate cap through the external sixteen-H lowering and complete precision
selector remains separate work; the reviewed package does not claim it.

## 5. Separate exact evidence

`independent.py` imports neither the author's `audit.py` nor a retained
factory or source matrix helper. It authenticates all 18 retained origins
and checks a distinct set of rational fixtures using standard-library
Fractions. Its spectral oracle checks **all principal minors** of
`cap^2 I - A^T A`, independently of the author's Hermitian PSD engine.

The completed normal and optimized Python runs check identical evidence:

| Scope | Coverage |
| --- | ---: |
| Primitive cuts with two masked spectral matchings and rational rotations | 17 cuts, 149 ordered intervals |
| Exact spectral interval/inverse certificates | 298 |
| Asymmetric recursive synthetic DAG | 10 atoms, 38 downsets |
| Every nested pair of those downsets, with one shared legal order | 475 |
| Actual matching-subset cuts in that independent schedule | 53 |
| Ordered intervals and inverse envelopes | 1,404 |
| Same-layer interval cases | 136 |
| Cuts with simultaneous nonempty active fragments | 22 |
| Zero-duration-predecessor cases | 32 |
| Wrong relative order distinguished | 394 nested pairs |
| Noncommuting generator prefix/suffix formulas | 8 checkpoint equalities |

The DAG fixture uses physical wire order `(2,0,3,1)`, unequal sibling
durations and one empty upper atom. Its matrices and defects are generated
independently and satisfy an explicitly computed B, eta and theta. These
are **synthetic fixtures**, not another run of the actual source factory.
They corroborate the general causal/algebraic implication while the author
fixture and the manual source review establish the specific source binding.

The generator control verifies that omitting the current term from C changes
the remaining suffix. Noncommuting pairs ensure that an accidental reversal
of relative endpoint order would fail. The primitive oracle tests the
unchanged cap 14/9 for its exact two diagonal envelopes, including partial
bank-unitary and cross-bank matchings. It does not infer all-size validity
from the finite tests; that rests on the arguments above.

## 6. Limits and remaining proof obligations

The theorem assumes the original ideal downset envelope and source admission,
generator rank, certified phase and coefficient-defect bounds. It does not
replace them with an observed finite norm. Inverses are exact inverses of
the same stored coefficients. It is not a statement about independently
rounded inverse tables or a rounded forward/inverse round trip.

A cut between writing two outputs of a single gate may be singular even
when the whole gate is unitary. The theorem correctly excludes those
physical microsteps and their saved temporaries. Actual tape movement,
coefficient production, storage and whole-multiplier recovery remain open
interfaces. The canonical five assumptions and selected kappa are unchanged.

Credit Jose Manuel, Vlado Vojdanovski, Chafik Boukhalfa, Brian/JoyboyBrian,
Nick Petalas and Ali Romman for the distinct source/compiler, phase, trace,
matching, downset and application results identified in the author's exact
origin manifest. Prepared for Jerry Chen / @CubeJerry with substantial
OpenAI assistance. This is separate model-assisted review, not independent
human or formal-kernel acceptance.
