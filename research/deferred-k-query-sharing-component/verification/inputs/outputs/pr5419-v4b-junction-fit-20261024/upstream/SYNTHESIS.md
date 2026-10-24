# Which construction to try next

The literature and executable screens favor a **history-augmented coupled
transducer with an endogenous paid observer**, using an invertible boundary
whose gauge is chosen for the actual precision metric. They do not yet give
an admitted exponent improvement. In particular, the currently missing
component is not another inverse formula: it is a source-compatible, versioned
observation and its affordable termination at the real caller cuts.

This assessment follows the donor's encoded-output question: ask what the next
consumer truly needs, preserve information that is temporarily irrelevant, and
charge its eventual return. A failed eight-field representation is not a proof
that all useful retained information must be decoded immediately. Conversely,
an eight-field mathematical output is not an eight-call physical supplier.

## 1. A concrete ordinary coupled boundary

Use the pinned physical maps

    W = diag(Kp^-1) M diag(Km)/2,
    Z = diag(Km^-1) M^T diag(Kp)/2,
    ZW = 14 I,   C = I - WZ.

For any nonzero a, set b=-12/a. Then

    H(a,b) = [ C    aW ]
             [ bZ  13I ]

is an involution on **112 main fields and eight arbitrary independent mode
fields**. Indeed C²=I+12WZ, CW=-13W and ZC=-13Z, so H²=I. Dugongue's
`native-involutive-port-transfer` (PR4935) already supplies this completion
and three-shear method, with a=6,b=-2 and the same unchanged principal block.
The contribution here is the gauge optimization, separately priced physical
K-frame lift, precision probes and actual restricted-consumer transport.
Neither the completion nor the transpose-program method is new.

In Kp/Km frames its literal in-place implementation is

    h *= a
    h -= M^T x / 2
    x += M h / 2
    h *= -1/a
    h += M^T x / (2a)

with no overwritten original or new scratch. The 448 nonzero M entries give
1,344 ADDs, 16 SCALEs and 240 entrance/exit signed monomial field maps. These
maps have separately authenticated physical words; they are not Gaussian
calls. `BALANCED-PROGRAM.json` contains all scalar instructions and explicitly
counts the 120 maps at each boundary. All 120 input columns are checked against
the analytic matrix, along with H²=I and a changed-coefficient control.

The nontrivial normalized 2-by-2 mode block is

    [-13, a sqrt(14); b sqrt(14), 13].

Its squared Frobenius norm is 338+14(a²+b²). The gauge a=-4,b=3 gives 688,
compared with **898 at the prior PR4935 gauge** a=6,b=-2; the unrestricted real
optimum is 674. The
34-point dyadic search is explicitly limited to a=-2^k or -3*2^k,
-8<=k<=8. This includes both symmetric dyadic optima. Since each block has
absolute determinant one and H is its inverse, minimizing this Frobenius
quantity also minimizes its spectral norm and condition number in the
orthonormal mode decomposition. This norm statement uses the unitary K maps
and Z=W* premise for every width.

The scalar row-sum metric favors a different choice: a=-12,b=1 has bound 50,
where a=-4,b=3 has 97 and the norm-equivalent prior gauge a=-6,b=2 has 69.
The unbalanced reference (-1,12) has 349; it is not the prior implementation
baseline. That comparison is an exact finite
scalar-frame screen, not a physical all-width infinity-norm theorem: physical
monomial blocks can reach different addresses and lose scalar cancellations.
The compiler's actual error metric must decide the gauge.
`ROWSUM-PROGRAM.json` also compiles H(-12,1) without odd divisions: transpose
the **normalized scalar** H(1,-12) program by reversing its instructions and
exchanging ADD source/destination, then wrap the same physical K frames.
It uses 1,344 ADDs, eight sign SCALEs, 240 monomial maps and no new scratch.
Both its analytic endpoint and involution are checked on all 120 columns.
Thus the better row-sum gauge does not require the 1/3 factors of the naive
primal factorization. The balanced program
has intermediate coefficient denominators at most 2^4 on the tested scalar
basis, but this does not fund arbitrary recursive precision for free.

## 2. The next consumer changes the design

For a whole 120-field logical ADD, matching H frames suffice. The actual
controller changes main fields while leaving helpers alone. With
P=diag(I112,0_8), its encoded source-to-destination map is

    H P H = [ I+12WZ   -13aW ]
            [ -13bZ    -168I ].

`construction.py` checks this common-encoding matrix on every column and
rejects substitution of I120. Actual stages have different K maps, so the
required general junction is **H_t P H_s**, not HPH with charts identified.

`junction.py` supplies a complete catalytic implementation of that general
junction. Let L_s be only the first part of the source H_s program:

    h *= a_s
    h -= Z_s x
    x += W_s h.

Its exposed main value z is exactly the top row of H_s(x,h); its mode value u
can be arbitrary. To add H_t P(z,u) to the destination, execute

    destination_x += z
    u += Z_t z
    destination_x -= W_t u
    destination_h += b_t u
    u -= Z_t z
    destination_x += W_t u
    destination_h -= b_t u.

This adds (C_t z, b_t Z_t z), cancels all dirty-u dependence and returns u
unchanged. Undo L_s to restore every source original. Thus the net operation
is precisely `dst += H_t P H_s src`, with the destination's logical helper
coordinates unaffected after decoding. It preserves the independent source
helper rather than assuming it was clean or dropping its target.

At a_s=-4,b_t=3 the full bill is **3,712 ADDs, 16 SCALEs, 960 signed monomial
field maps, no owned fields and no Gaussian calls**. The source/target
normalizations, inverse normalizations and source restoration are all included.
It improves the straightforward four-boundary-conversion implementation
(5,488 ADDs, 64 SCALEs, 960 monomial maps). If the charts really coincide, a
fused program uses **2,360 ADDs and 480 monomial maps**, with no SCALEs or
scratch. That specialization is not used as a free cross-stage adapter.

This junction bill uses the balanced gauge. In the same partial-source
factorization, a=-12 would introduce a 1/12 SCALE on restoration. The row-sum
boundary's division-free dual circuit does not remove that factor from a
different circuit automatically. Gauge, source exposure and restoration must
be optimized together; no free switch of gauges is assumed.

The checker compares all 240 independent input columns over rational free-group
words to a separately expanded H_t P H_s formula. Source and target K labels
remain distinct; no cross-stage commutation is assumed. This identity therefore
holds for any invertible physical K maps, including their phases and tensor
widths, within the declared block interface. A subtractive bridge and omitted
source-restoration control are checked. Exact program hashes and complete
counts are in RESULT.json; `junction.py --emit PATH` emits all three streams.

The following thin-query consumer has a priced wrapper too. After exposing z,
COPY it into 112 distinct owned zero fields, apply the retained Q^-1 queries,
and feed those responses through the same dirty-u target update. Clear the
owned responses after their last use and restore the source prefix. The exact
identity is

    dst += H_t diag(Q^-1,0) H_s src;
    src unchanged; all 112 owned fields return zero.

The checker includes all 352 independent entry columns (240 originals plus
112 owned dirt columns). Its bill retains **112 H1 calls**, 112 COPYs,
224 CLEARs, 112 owned fields, 3,712 ADDs, 16 SCALEs and 960 frame maps.
Lowering the inverse queries to positive H1 calls adds 112 bit translations,
so the full monomial-map count is 1,072. The positive-call/translation identity
is separately checked including absolute phase. These are the existing thin
queries in the proposed typed implementation, not newly eliminated queries or
a free supplier of ZQY. Owned stock and physical tape execution remain charged
compiler obligations.

This combines catalytic dirty-state restoration, low-rank factorization and
alternative-basis propagation into one executable consumer. It avoids forcing
decoding at this ADD boundary once the proposed H block types are installed.
It does **not** install those types in the existing coupled provider, prove
the native FULL dispatch in these types, or implement the missing compressed observer.
The eight-mode stationary-transfer obstruction is not evaded by relabeling:
the junction operates on the full main state and restores its borrowed mode.

H is only a boundary seed. Its insertion into the full 232-field X/Y/eight-mode
provider block, with the other 400 helper originals, remains to be derived.
A pair of such 120-field banks is not silently presumed to match that block.

## 3. Carry history, rather than force stationarity

The first two source backward FULLs and their following thin consumers are
retained at events 1..14; the successor has the identical clip at events 5..18.
The physical eight-mode transfer equation would be

    W3 T = D1 W1.

At fiber width one and nonzero input address one, its projected residual has
rank eight, G00=173/14 and

    det(G) = 1389039784345493055 / 26985857024.

The zero-address residual vanishes and is an explicit false-positive control.
An invertible change of eight mode coordinates leaves the obstruction intact.
Thus the witness has sixteen independent columns after adjoining the second
chart's original eight. This is a finite column-rank statement, **not** a
sixteen-whole-field Gaussian cost lower bound.

The useful displacement identity across charts is

    D1 C1 - C3 D1 = [W3, D1 W1] [Z3 D1; -Z1].

The code evaluates its action on all eight physical witness inputs, including
signed monomial phases: its Gram matrix is 196G, with entry 2422 at (0,0).
This suggests generation-tagged displacement state, not repeated expansion of
a dense operator and not another eight-mode rebasing search. Such state must
have a bounded lifetime: keep it until a real paid contact exposes its needed
observation, then restore it. Unbounded history growth would merely move the
bill into storage or later Gaussian work.

## 4. Build the observer into a paid contact

The scoped local repair needs b=Z Q Y, on the **current output Y version**.
Given b as a preserved borrowed observation, the exact exit is

    Hout = Q H + b = R h
    Xout = X - W Hout = D x - R y
    Yout = Y.

Its verified bill is eight H1 calls, 456 ADDs and 240 monomial maps, with no
new owned fields. The eight H1 calls are already included in the conditional
cost screen below. The missing observer and any extra termination are not.

The 112 source columns Kp_i Q occupy 112 distinct right cosets of the monomial
Clifford subgroup: their images of the Z Lagrangian are distinct. Therefore
one common Gaussian after monomial pre-aggregation cannot implement this
observer. This is a restricted architecture exclusion. It does not exclude
multi-layer, non-monomial intermediate sums, two-sided synthesis or changing
what the native producer preserves. All 6,216 pair comparisons also expose
the orientation trap: rank_B(Ej^-1 Ei)=2 whereas rank_B(Ei Ej^-1)=0. Cancelling
Q Q^-1 in the latter order does not aggregate independent inputs in the former.

Dillon Amburgey's PR5388 already supplies 112 genuine paid Q xi observations
on independent forward-helper coordinates. The code checks all 112 physical
wrapper identities including phase. That is a promising *mechanism*, but xi
is not the current arbitrary main Y. The full 358-helper recoding, original
main inputs, hot helpers, cold-target upgrades and return all stay in the
invoice. Its +136 paid-rank completion also adds +136 target rank. It supplies
no backward bank by simply reversing the list. These are the exact obligations
a joint observer must change.

Catalytic differences Q(a+u)-Qa and finite-field interpolation can eliminate
dirty dependence. They cannot erase the calls or the need for the same version
of a. The implemented Cook-Mertz root-of-unity cancellation and rational
interpolation probes explicitly count evaluations. A useful supplier should
reuse **actual native paid contacts** to obtain the necessary two-sided
observations, rather than buy a second full query bank.

## 5. One combined allowance, then the compiler

At the final submission refresh, canonical main selected **conditional
κ=0.003027288235** from PR5413, at promotion commit
`1a3ced60b2f7a46bc70280a04f2eeb8ca027c700`. Its reviewed conditional status is
acknowledged; this sweep does not rerun or replace that admission.
`current_profile.py` authenticates the selected price receipt and reconstructs
its full chronological invoice from the successor: **18 backward FULLs**,
64,260 paid jobs, 10,928 productive fields, paid rank mass 238,990 and target
rank mass 239,742. Its existing neutral completion returns eight H8 helpers
per FULL. The initial frozen PR4610 reference remains independently replayable
in costs.py and RESULT.json; it has sixteen applicable backward calls and the
earlier 48.387169… per-call cap.

The new conditional supplied-observer exit explicitly pays eight H1 per FULL
and returns eight H9 helpers. Relative to the newly selected profile, the paid
delta is **+144 H1 -144 H8**, and the target delta is **+144 H9 -144 H8**.
The target upgrade is valid only after the actual observer and return contract
are proved. All existing thin queries and IDLEs stay paid. Thus no neutral H8
completion receives unearned H9 credit.

The exact 0.004 signed-moment allowance for the combined observer and extra
termination is **901.134447… total**, or **50.063024… per backward FULL**.
Directed integer roots enclose every r^(249/250); the sign and cap do not
depend on floating-point rounding. The following other regime screens are
numerical, with explicit full price arrays retained:

| Desired saving | Combined observer + extra termination H1/call cap | Uniform paid-precision factor ceiling |
|---|---:|---:|
| 0.0033 | 59.743 (numerical) | 1.004572 (numerical) |
| 0.004 | **50.063024… (exact enclosure recorded)** | 1.003840 (numerical) |
| 0.006 | 22.567 (numerical) | 1.001743 (numerical) |
| 0.007 | 8.908 (numerical) | 1.000691 (numerical) |

These are ceilings under the conditional supplied-observer profile. Observer,
restoration and all additional paid work share one allowance. No extra
original helper target, free inverse, saved center or observation credit can
be stacked on top. A different profile requires recomputation. The precision
factor is a sensitivity model, not a compiler theorem. A 1% paid-precision
increase exceeds each conditional ceiling.

Buying 112 fresh QY values for every backward FULL makes the exact 0.004
moment negative. The newly selected ordinary BIT admission still supplies
0.0034, so reaching 0.004 also requires improved ordinary-work/compiler
admission. A sensible first milestone remains **0.0033**, with a design budget
of at most 32 H1-equivalents per FULL for the joint observer and extra
termination. This is an allocation target, not a supplied algorithm. It leaves
numerical moment margin 499.380 at 0.0033, but only a 1.002118 uniform paid
precision ceiling. At 0.004 its margin is 325.134447… by exact enclosure.
The same allocation fails at 0.006 and 0.007. Precision, volume, constants,
stocking and physical routing still require their complete proof.

## Ranked next experiments and stopping rules

1. **Fit the actual coupled provider and its paid history.** Place the H block
   and verified consumers in the first actual backward FULL/thin-query cut,
   with an explicit, disjoint assignment of original mode fields. Derive the
   full 232-field input/return map; do not assume the provider's coupled output
   already equals this ordinary H encoding. Keep all original inputs. Produce
   the required ZQY version and preserve the demanded Q^-1 X thin response,
   using a paid native history contact or a proved displacement of one. Restore
   the history with a complete combined bill below the chosen cap. Stop if an
   essential read is unavailable or the necessary inequality fails.
2. **Two-generation closure with bounded history.** Use the displacement state
   instead of assuming W3T=D1W1. Terminate it at the second actual contact and
   check every original column, borrowed response and owned-zero return.
   This experiment determines whether the first junction is reusable.
3. **Optimize the installed junction and endpoints.** Use the H_t P H_s and
   retained-query implementations with their complete ordinary/owned bills;
   identify any sharing that the actual ownership permits. Put both endpoints
   in the same type system. Select the gauge using the actual
   precision metric. Panel CNOT elimination and independent-form scheduling
   can reduce ordinary work here; they create no recursive savings alone.
4. **Compile and independently admit.** Only after the joint paid bill passes,
   prove precision and physical volume/storage/tape bounds, then outer
   admission. Retain the earlier no-IDLE, two-FULL, volume and independent-error
   obstructions within their stated scopes.

Deprioritize another inverse-only package, an eight-mode stationary basis scan,
passive one-Gaussian decoding, or an uncharged approximate degeneration.
The native cycle ZW=14I is non-nilpotent; its first four traces are nonzero,
so shrinking the entire WZ cycle by similarity is impossible. The literature's
nilpotent tensor-term construction does not automatically transfer to this
Gaussian supplier. A constructive nilpotent positive control is included to
make that distinction executable.

## Claim boundary

This package supplies 25 paper-to-code adaptations, literal coupled boundaries and cross-chart catalytic ADD/thin-query junctions,
actual caller-cut and physical witness checks, and a priced construction
contract. It does not supply the joint observer, a complete recursive supplier,
a new κ, or an update to the selected frontier. The report narrows the next
construction to a testable interface; scientific success remains a separate
obligation from publication or archival intake.
