# Source geometry and payload-query limits

This annex preserves four reviewed results about source access. They give
exact support geometry, a conditional direct-capture bound, an observation
rank separation, a scalar centre restriction, and payload-query bounds.
They improve no complete kappa calculation. The four gate and interface
classes are different. Their bounds must not be added as one cost invoice.

The parent package and its chronological-cache annex keep all 129 original
files unchanged. [PARENT-SNAPSHOT.json](PARENT-SNAPSHOT.json) binds those
bytes. This annex has its own [manifest](ANNEX-MANIFEST.json),
[source record](SOURCES.json), and [portable edits](PORTABILITY.patch).
All original proofs and prior reviews remain unchanged under `frozen`.

## Eight support spaces and a direct-capture bound

The [source proof](frozen/root/CENTRE-SUPPORT-GEOMETRY-20261018.md) and
[independent review](frozen/lanes/independent-review-20261017/centre-support-review-20261018/REVIEW.md)
give eight rank-seven binary support spaces. The four equal-space pairs
are `{0,5}`, `{1,6}`, `{2,7}`, and `{3,4}`. Distinct spaces meet in rank
six. All four meet in rank five and span the rank-eight hyperplane
perpendicular to 45. The shared-port graph is `K_(2,2,2,2)`. Each edge
has two ports, and each of the 48 used ports occurs in two rows.

Assume one unwarped carrier per original source value, an increasing
subspace chain on each carrier, and one direct common-frame capture per
complete row. The frame must contain that row's support. No extra carrier,
stored partial query, or operator-valued source code can supply a term.
Then at most two captures have rank seven. The sum of the eight capture
ranks is at least `2*7+6*8=62`.

This is a conditional bound, not a construction at 62. The pair code uses
two coded carriers and violates the premise. The theorem does not price
scalar work or prove a lower bound for arbitrary native query words.
Both the producer calculation and the independent XOR-closure calculation
are rerun. Their exact [certificate](frozen/root/CENTRE-SUPPORT-GEOMETRY-20261018.json)
and [review receipt](frozen/lanes/independent-review-20261017/centre-support-review-20261018/CHECKS.json)
are retained.

## Dyadic unit logs require sixteen fixed observation fields

The [residue proof](frozen/root/DYADIC-QUERY-SEPARATION-20261018.md) and
[independent proof review](frozen/lanes/bridge-review-20261017/dyadic-query-separation-review-20261018/REVIEW.md)
use `BD=cI`, full residue rank of `B`, zero residue of `c`, and a two-sided
unit `MD` over the coefficient ring. A row relation in `[B;M]`, multiplied
by `D`, first forces its `M` coefficients to zero and then its `B`
coefficients to zero. Thus the stack has rank `2r`. Over an integral
domain, a nonzero residue minor also gives rank `2r` over the fraction
field.

The actual eight-centre matrices have `BD=13I` and a dyadic invertible
eight-column minor of `B`. Every dyadic `M` with dyadic unit `MD` gives
stack rank sixteen. The
[mixed-source unit criterion](frozen/lanes/oblique-native-20261017/minor-input-log/UNIT-COMPLETION.md)
and [full-null terminal family](frozen/lanes/controller-followthrough-20261017/MINOR-LOG-SOURCE-ACCESS.md)
fix the application. Completed X and retired selected Y vanish on that
family. The only further observation of retired ordinary Y is a fixed
linear map `N`. Required outputs force
`ker N` to lie in `ker B` intersect `ker M`, even with nonlinear
postprocessing. Total observation rank is therefore at least sixteen
complete fields. This is not a bound on simultaneous scratch storage.

For `M=B/13`, the stack has rank eight and `MD=I` over the rationals.
With the invertible `B` minor, a unit log with stack rank eight exists
over the coefficient ring exactly when 13 is invertible there. The
normalized choice with `MD=I` is uniquely `B/13`. Allowing denominators
coprime to 13 does not remove this obstruction.

For finite routed arrays with `ell` scalar coordinates per field, the
rank is `16*ell` if the ordered identities and Gaussian-dyadic two-sided
inverses hold after flattening. The map `i -> 5` in `F_13` is used. The
executed noncommuting two-coordinate route test is a fixture, not a full
native or global route replay. The annex implements no odd division,
cheap old-stage query, target scatter, or complete decoder. Arbitrary
nonlinear encodings, extra observations, changed output partitions, and
packing on a bounded finite domain are outside this observation theorem.

Both source and independent checks are rerun. They check 64 perturbed
sections, 24 logs with nonidentity unit `MD`, the explicit stack minor
`1/8`, the route fixture of rank 32, and the ordered full-null algebra.
The [review receipt](frozen/lanes/bridge-review-20261017/dyadic-query-separation-review-20261018/REVIEW.json)
records controls for the unit, residue-rank, zero-residue, and null-family
hypotheses. Historical review-pending text remains unchanged; the retained
independent review supplies the later status.

## Fixed native support forces a scalar centre matrix

The [all-cut proof](frozen/lanes/oblique-native-20261017/interior-cut/ALL-CUT-SUPPORT.md),
[physical support proof](frozen/lanes/coherent-port/centre-mixing-20261018/MIXING.md),
and [independent review](frozen/lanes/bridge-review-20261017/centre-mixing-review-20261018/REVIEW.md)
fix the actual native paths and require equal physical views at scalar
accesses. The first class retains the source computation and Y scalar
tail. It permits one-way equal-frame source-to-Y insertions or gain
changes, with the stated raw-I helper entry correction. The second,
separately reviewed class fixes the exterior and all wrappers. It permits
scalar rewiring only in the canonical interval from cut 7502 to cut
17249, subject to the support induction and the endpoint contract.
Neither class permits arbitrary edits through physical wrappers.

Let `R` be the actual eight-row matrix and `K=R^T/4`. If the retained
response and a constant scalar centre matrix give
`E+KAR=diag(d_0,...,d_111) tensor I`, support gives 6,608 off-diagonal
equations on all 64 entries of `A`. A 63-row minor has determinant
`-2^71=-2361183241434822606848`. Their kernel is exactly `A=cI8`.
The diagonal support witness then gives `d_p=c` at every port.
Over the rational or Gaussian rational field, a nonzero clean diagonal
response therefore needs centre rank eight in this class. A factorization
through seven constant scalar centre channels fails.

The independent checker rebuilds both complete interval inventories and
the 4,276 products. It checks all 640 original columns, helper and owned
outputs, native frame conditions, physical-view restrictions, and private
zero-buffer lifetimes. It computes the determinant by rational elimination.
The [two-basis proof](frozen/lanes/bridge-review-20261017/centre-mixing-review-20261018/TWO-BASES.md)
uses two actual eight-port bases with a connected overlap graph. Its
nonzero overlaps are `+1/2` or `-1/2`, so the scalar-equation conclusion
also holds over a commutative ring in which two is a unit. The
[peer check](frozen/lanes/bridge-review-20261017/centre-mixing-review-20261018/PEER-CHECK.md)
covers that explanation and the bounded canonical interval extension.

The physical support witness applies at every positive tensor depth and
does not assume independence of formal warp words. The frozen producer's
`check_support.py` composes histories in forward list order. All consumed
X histories have length at most one, so this does not alter its result.
The executed independent checker uses reverse order and checks that length
limit. A future packet with longer histories must change the producer loop.

This replay does not run the producer inventory, modular existing-site
rank check, or their source emitters. Their source and historical receipts
are retained. The independent interval replay is the decisive completeness
check. The dense rank-seven projection fails 2,534 equations, a duplicate
certificate row has zero determinant, and a second orthogonal basis pair
with two graph components fails the connectedness premise.

Changed native paths, arbitrary wrappers, unequal physical views, changed
query or scatter spaces, and operator-valued centre entries are outside
these results. No bound on all native encodings follows.

## Plain-input payload queries have source rank 112

The [query-span theorem](frozen/lanes/schur-selection/plane-repair/QUERY-SPAN.md)
and [independent source review](frozen/lanes/source-domain/query-span-review/REVIEW.md)
use scalar free gates `B tensor I`, scalar initial and final interfaces,
and queries `I+uQv` with scalar `u,v`. Singular scalar gates, COPY, CLEAR,
borrowed fields, feedback, and query reuse are allowed. Every non-scalar
payload map must count, including a rank-zero address permutation.
An `r`-direction block query counts `r` times.

After `c` queries, both a scalar response-column factorization and a scalar
source-row factorization have width at most `c`. Applying any collection
of operator functionals that kill the identity bounds the simultaneous
column and row spans by `c`. The ordered proof does not require commuting
payload operators or invertible intermediate scalar gates.

For the actual line-centre query and the proposed matched-plane query,
the scalar source rank is 112 although there are eight output fields.
Exact functionals isolate the line columns or the matched two-column
blocks. The plane minor in matching order has determinant eight. The
same bound holds at every positive tensor depth by compression to fixed
constant characters. A separate mixed-plane endpoint on `n` fields needs
at least `n` payload queries: normalized trace minus constant-character
expectation gives `2^(-lambda)-1` on each plane. A common negative
eigenspace is not required.

Both producer and independent checks are rerun. The independent check
reconstructs R from 10,851 historical scalar events, checks 28,672 exact
plane Fourier columns and 802,816 functional contributions, and verifies
all 56 pair Grams and the determinant. It rejects reversed plane
orientation. The retained [handoff](frozen/lanes/schur-selection/HANDOFF.md)
records the completed review and supersedes the proof's old review-pending
sentence without changing its bytes.

These are payload-query counts, not native-child, native-rank, or scratch
bounds. A source with an existing port-dependent phase code has a changed
input contract. The theorem does not charge that code again. At depth one,
one rank-zero translation and scalar work can form a line phase. The
annex neither prices such implementations nor reruns the separate plane
route construction.

## Reproduction, sources, and open costs

Use Python 3.11 or later, its standard library, one process, and at least
3 GiB of free disk space. Keep the complete parent package at its published
relative paths. Use a new output directory:

```sh
python3 -I -O -B research/actual-query-information-bounds/annexes/source-geometry/replay.py --out /tmp/source-geometry-replay
```

Expected final line:

```text
PASS_SOURCE_GEOMETRY_ANNEX
```

The seven checks run serially and compare every JSON value and type with
the historical receipts. Only an explicit checker-hash field changes to
the portable checker hash. The driver verifies all annex and original
parent bytes before and after execution. It needs no Git, external tool,
network, numerical library, or solver. [ARCHIVE-CHECK.json](ARCHIVE-CHECK.json)
binds the historical archive to the exact parent members used at runtime.
The portable replay does not copy or reload the complete archive.

The publication base is `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`.
Its selected result is the conditional joint-helper result in
[PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470), with
kappa `60403/20000000`. These results use their historical actual source
packets and the parent's historical `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`
source. No transfer to that newer selected construction is proved.
[NOTICE.md](NOTICE.md) retains the predecessor roles, exact source pins,
license records, and AI disclosures.

Open next questions:

1. Price a changed source representation and all required reads, scatters,
   address operations, and restoration. These results do not supply that
   complete physical invoice.
2. For an eight-observation log, implement the required inversion of 13
   under an exact arithmetic and endpoint contract. Prove the remaining
   old-stage query, complete decoder, and recursive precision bounds.
3. For a proposed escape from the centre restriction, state the new
   wrapper, support, native-path, or operator-valued interface. Check it
   against its own source model before deriving a cost.
4. Convert a payload-query count to a native cost only with an explicit
   contract that accounts for rank-zero maps and prior input encoding.
   The present annex supplies no supplier moment or complete kappa gain.
