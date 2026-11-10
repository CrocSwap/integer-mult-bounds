# Precision envelope for the actual QUERY-only caller

Prepared for **@CubeJerry**, with substantial OpenAI assistance. Canonical base:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. This is a source-specific
conditional precision lemma and an exact-service boundary audit. **No new
kappa; no physical rounded caller; no unconditional multiplication theorem.**

## 1. Exact question and predecessor boundary

The caller is the published 3,095-event QUERY-only source at
[`617903497387a98f7ca929ad0b6928dd32abffec`](https://github.com/CubeJerry/integer-mult-bounds/tree/617903497387a98f7ca929ad0b6928dd32abffec/research/p104-query-only-interval).
It has 76 symbolic A/B main roles, 18 joint native calls, and no QSELF.
Every joint call uses the unchanged 71,144-event word of
[CrocSwap/integer-mult-bounds#6936](https://github.com/CrocSwap/integer-mult-bounds/pull/6936),
head `03626137d0bd57f09b0bf9597376183ce6fa9683`. The helper allocation is
the published caller's: 3,952 actual main inputs and 18 disjoint families of
1,061 arbitrary helper inputs. Helpers are not initialized zero or reused
between stages. The 51 owned labels, 54 lifetimes and peak 43 in each local
word remain unchanged.

`DEPENDENCIES.json` pins eleven unmodified inputs by original repository,
commit, path, byte count, Git blob and SHA-256. The executable source blobs
are `cf55f4271009a06ad192a070d330a4466b6d44fa` (caller) and
`d93e67ca7628bf5531ae6e369da4dd7b7907b88f` (compressed native word).
The native proof/checker, rounded note and exact-grid proof are authenticated
reference material; this package does not execute their dependency trees.

There are three different predecessor claims:

1. [CrocSwap/integer-mult-bounds#6901](https://github.com/CrocSwap/integer-mult-bounds/pull/6901)
   proves an exact common-grid implication under its stated ideal recursion,
   source and complete-job premises. It explicitly does not allow arbitrary
   rounded child returns. Its numerical/source constants belong to #6030.
2. DreamingOfClouds' #6936 and the exact common-odd-grid lineage use an
   `S=1125` prefix divisibility certificate with exact completed children.
   CubeJerry's published `odd-native-common-grid`, commit
   `e45e844303e04947cf6591fb46b43bf8a7bc5356`, makes a related exact-grid
   reduction for the preceding word. Those exact statements do not imply
   divisibility after an adversarial nonzero child defect.
3. DreamingOfClouds' `ROUNDED-DIVISION.md` in
   [CrocSwap/integer-mult-bounds#6937](https://github.com/CrocSwap/integer-mult-bounds/pull/6937),
   head `a98df73ddae1d1ea85a62b6bdf2714b28cb7b359`, states a different,
   total rounded-division contract and a complete-fibre defect-tree method.
   Its displayed word constants refer to #6932's 67,079-event source; the
   note explicitly requires later words to recompute them. Its S1--S5
   structural premises and physical implementation obligations remain
   premises here.

The new work is an exact, reproducible envelope for the **actual changed
caller with every current native call expanded at all its source cuts**,
including backward checks of its critical prefix/suffix bounds. It supplies
current format and integer temporary constants, checks the retained large
threshold, and locates a concrete actual-source obstruction to replacing
total rounded division with the existing checked exact table. It neither
reproves the exact endpoint nor treats formal endpoint equivalence as
equivalence of rounded executions.

## 2. Norm, input domain and primitive contract

Let `D>=1`, `p,h>=0` be integers, with one common component grid
`Delta=2^-F`. Every real and imaginary component of every arbitrary public
input is on this grid and has absolute value less than `2^h` at the stated
raw/root boundary. Owned INIT produces exact zero. Public inputs include
every helper, independently; no correlation or cancellation is assumed.
For the outer-wrapper extension below, D is the total selected factor
`D=q+R`: the q preprocessed coordinates and the remaining reference factor
R. Establishing the input p,h domain at the chosen external boundary is
separately paid. The q kernels must precede the later R-fibre computation,
as stipulated by the retained wrapper contract; the proof converts once
from the D-fibre norm to the R-fibre norm in the safe direction.

For a selected set of `X` binary coordinates use the supremum, over complete
`X`-fibres, of the Euclidean norm on that fibre's `2^X` complex entries.
Write this as `||z||_X`. For complete nested factors, `||z||_R<=||z||_D` when
`R` is contained in `D`. If every component has error at most `Delta/2`,
then the error in this norm is at most

    eta_X = 2^((X-1)/2) Delta.

An input with the component bound above has fibre norm less than

    B_root = 2^(h+(D+1)/2).

The norm contracts are explicit:

* Each completed native frame change, Q query and D-mask job is the intended
  complete-fibre unitary, with the absolute phases and column multiplicities
  required by the inherited source. This is a semantic premise, not a
  consequence of the finite frame-span check.
* Q and the D_j commute where the frozen exact endpoint uses that identity,
  and `Q^4=I`. Therefore

      Lambda_s = ((1+s i) I + (1-s i) Q^2)/2,  s in {-1,+1},

  is unitary: the unitary involution Q^2 has eigenvalues ±1, and Lambda_s
  has eigenvalues 1 and s i. In particular it is not `(I+Q^2)/2`.
* A completed primitive with ideal map T has a **total** contract on every
  input in its declared grid/radius domain: it returns a grid value differing
  from T of that actual input by at most its declared epsilon. The contract
  may be nonlinear and its residual may depend adversarially on the input.
  It must cover actual inputs to each recursive child, not just ideal ones.
* Scalar rounding, when invoked, is the total function

      RDiv_(a/b)(m) = floor((a m + floor(b/2))/b),   gcd(a,b)=1, b>0.

  Its scalar residual has absolute value at most 1/2. Integer coefficients
  are exact. For ADD, round the product and then add the old target exactly;
  equivalently add the integer `b*old_target` inside the numerator. Negative
  values use mathematical floor. Upward ties mean RDiv is not an odd map.
* Lambda needs its own completed primitive with residual at most eta_X,
  for example exact formation of its common denominator-two numerator
  followed by one rounding per component, with an exact Q^2 monomial
  service. This is an explicit contract; no such physical table is installed
  here. An implementation which rounds twice must supply the resulting
  larger residual instead.

For the local estimates take `epsilon>=eta_X`, and bound each completed
child, QUERY, IDLE and Lambda residual by epsilon. Arithmetic and native
operations must run to their completed source cut before another field
reads them. No assertion that partially constructed Clifford outputs are
Clifford vectors is used. Scalar numerator temporaries are handled separately
in section 6; arbitrary internals of a native provider are inherited
obligations, not unnamed source cuts certified by this package.

**Why this is uniform in column multiplicity.** Tensor products of unitary
complete-fibre maps have norm one. Rational scalar coefficients are applied
once and are not raised to a tensor power. The only dimension factor is the
single conversion `eta_X` at a componentwise rounding site. These facts hold
for every positive column multiplicity under the complete-fibre premise.
Coordinate supremum norms do not have this property: the exact Gaussian row
`((1+i)/2,(1-i)/2)` sends `(1,i)` to `1+i`, of modulus sqrt(2). A phase error
may preserve norm one, so a norm certificate cannot certify native phase
correctness.

## 3. Native prefix and suffix certificate

For each live native register r carry two nonnegative rational numbers
`m_r,e_r`. Initially m=1 on every public input and m=0 on owned labels;
e=0 everywhere. At each source event use:

| Source event | Mass update | Defect update |
|---|---|---|
| MOVE r | m_r unchanged | e_r <- e_r+1 |
| ADD/COPY r,s,q | m_r <- m_r+abs(q)m_s | e_r <- e_r+abs(q)e_s+1_(q noninteger) |
| SCALE r,q | m_r <- abs(q)m_r | e_r <- abs(q)e_r+1_(q noninteger) |
| INIT/CLEAR r | m_r <- 0 | e_r <- 0 |

COPY in this source is additive COPY into freshly initialized zero. The
checker proves that source precondition. It does not erase an arbitrary
target's earlier residual by fiat. Register frames agree at scalar contacts;
each MOVE starts at its declared current frame and uses the declared public
or owned direction. A separate exact span/lifetime scan checks all of these
syntactic premises and the final public frame list.

By chronological induction, at every source cut the exact ideal value has
norm at most `m_r B`, and the realized-minus-ideal value has norm at most
`e_r epsilon`, for input norms at most B. MOVE preserves norms by the stated
unitary contract. ADD and SCALE use the triangle inequality. INIT/CLEAR kill
all earlier error channels. Also track the product `abs(q)m_s` and its defect
bound before every ADD/COPY; rounded product residuals are bounded by the
corresponding final target bound, whose other summands are nonnegative.

This positive propagation deliberately forgets all cancellations. It is a
valid, loose bound rather than a claim that these extrema are attained by a
choice of actual unitary inputs. In particular the large constants below do
not contradict the smaller cancellation-aware exact-grid row estimates.

The exact rational scan of all 71,144 events gives:

| Bound | Meaning | Strict bound |
|---|---|---:|
| M_W | all stored fields and pre-ADD products | 2^237 |
| Sigma_W | all-cut propagated unit residual mass | 2^235 |
| Gamma_W | returned public residual mass | 2^235 |

The maximum prefix is register 1443 after event 71119; the returned defect
maximum is the same register after the whole word. `ENVELOPES.json` records
the exact rational values and witnesses, not floating logarithms. There are
6,323 MOVE sites and 25,923 noninteger scalar sites, including 4,143 odd
scalar divisions. There is no multiplication by the number of public fields
because the contract takes a maximum over fields.

**Separate critical check.** `native_adjoint` starts a covector at each
reported maximum and runs the transpose recurrence backwards. Reverse ADD
adds `abs(q)*lambda_target` to the source covector; reverse SCALE multiplies
its covector; reverse INIT/CLEAR zeros it. A residual site contributes the
current target covector. The sum on initial public inputs reproduces M_W,
and the sum on residual sites reproduces Sigma_W/Gamma_W. There are 24,507
nonzero residual-site contributions at the worst witness. This is a
separately coded reverse calculation, not an independent physical execution
or formal proof-kernel check. The forward induction is the mathematical
reason a finite exact source scan proves a statement about all inputs.

## 4. Full caller and every expanded native cut

Caller scalar operations use the same positive recurrence. SWAP permutes the
two pairs of bounds. LAMBDA and IDLE leave mass unchanged and add one unit
of residual. QUERY adds the source mass/error to the target and adds one
residual. This uses the complete query contract, including restoration;
it does not treat the query copy/erase lifecycle as free.

For a J contact, the frozen exact local endpoint on the six symbolic main
roles is, with unitary factors suppressed in the positive bound,

    A: (u,v,x,y) -> (u, v+Q^-1 u, x-Q y, y), then D_j;
    B: (s,t)     -> (s-Q t, (Q^-1 s+t)/2), then D_j.

Use the positive endpoint matrix

    (u,v,x,y,s,t) -> (u, v+u, x+y, y, s+t, (s+t)/2)

on old mass/error values simultaneously, then add Gamma_W to each returned
main's defect coefficient. Helpers return their own unitary-transformed
input plus at most Gamma_W epsilon. Each helper family belongs to exactly
one joint stage, so it starts with mass bound 1 and no prior raw-caller
defect. This does not identify distinct helpers or suppose they vanish.

At that J entrance let `m_in=max(1, the six main mass bounds)` and
`e_in=max(the six main defect bounds)`. Every internal native cut obeys

    ideal norm <= M_W m_in B;
    defect norm <= (M_W e_in + Sigma_W) epsilon.

These inequalities include prior caller errors arriving at a native call;
restarting the native word with zero error on its mains would be invalid.
They also include all fresh arbitrary helper inputs. The source scan checks
J stages 1 through 18 in order, type-local six-role bindings and 400 actual
main fields/1,061 helper fields at each contact.

For the actual 3,095-event caller, the results are:

| Bound | Strict bound |
|---|---:|
| Caller-only mass | 2^121 |
| Caller-only all-cut defect coefficient | 2^342 |
| Largest J entrance mass | 2^119 |
| Largest J entrance defect coefficient | 2^340 |
| **M_ctx**, including native interior products | **2^355** |
| **Sigma_ctx**, including native interior products | **2^576** |
| **Gamma_ctx**, all returned public fields | **2^337** |

The worst J entrance is stage 18, caller event 2958. The caller-only peak is
role 38 at event 3049; the final defect maximum is role 75. Full exact
fractions, cuts and separate caller-adjoint identities are in the receipt.
The reverse J rule adds `sum(lambda_r)*Gamma_W` and transposes the six-role
positive endpoint matrix. It independently reproduces the caller peak,
entrance and final coefficients, separating J residuals from primitive
residuals. No old 67,079-event or previous-caller constant is reused.

Thus this concrete expanded raw context has the all-input contract

    output defect <= Gamma_ctx epsilon;
    every certified source cut <= M_ctx B + Sigma_ctx epsilon.

The statement is uniform for all positive columns under section 2's operator
and completion premises. It is not a physical tape execution of the caller.

## 5. Retained recursive precision guard, explicitly conditional

This section proves a replacement-constant implication for the structural
organization S1--S5 of the pinned rounded note. It does **not** independently
establish those compiler, whole-job, ownership or normalization premises.
In particular retain the following: at most K_star unfinished raw contexts
per ordinary level; at most ell ordinary levels; at most K_star/v flow
classes; at most m(H+1) two-job frames; complete sequential splitting and
completion on disjoint axes with norm-one suffixes; a rank-e sequential base
with e<m; a remainder of fewer than N direct stages; and the prescribed
root wrapper with at most D+3 sequential unitary/contractive steps. All
actual input fields, origins and primitive contracts must meet section 2.
This uses the stated unitary/contractive normalizer reading. A normalizer
which introduces additional rounded C stages needs their residuals and
costs added; the weaker normalizer discussion in the predecessor note is
not silently assumed to install or price those stages here.

For the current word's published strictification parameters use

    v=1920,  m=153^v,  H=14,161,600,000,000,000,000,
    N=2^H,  K_star=v m (H+1)^2,
    ell=floor(log_N D),  t=ell K_star.

The logarithm power is **2226**, with minimum 2225 in the source. This is
not the earlier word's 2224. The exact threshold check is

    (10^14*141616+1)^2226 < 2^141616,

and the preceding index fails. The verifier constructs those 141,616-bit
threshold integers and K_star (14,073 bits), not N. It proves

    4096 K_star < N

by the bit length 14,085 of the left side. Consequently `t<D/4096` when
ell>=1, using `ell<=D/N`.

The inherited split/completion sizes have `R<=153^v`, `J=11^v`, `L=12^v`.
Exactly,

    (R/J+1)(L/J+2) < 2^(6v).

For example `(153/11)^v+1<2*16^v` and
`(12/11)^v+2<3*2^v`, and `6*32^v<64^v` for v>=3. The verifier also checks
the integer inequality without logarithms. Since Gamma_ctx<2^337, the
per-context equivalent gain after this charge has logarithm less than 343.
The positive noncontext overhead

    m(H+1)+H+log2(m) <= K_star

follows from the checked stronger bound with `log2(m)<8v`. Since
`log2(M_ctx+1)<356`, the retained path accounting yields

    X(D) = 2 log2(D+3) + 344 t,
    L(D) = 1 + 357 t,
    E_root <= 2^((D-1)/2 - F + X(D)),
    admitted input radius <= B_root * 2^L(D).

These are convenient strict upper envelopes, not optimal constants.

**Admission is not circular.** Keep raw contexts as individual nodes in
the defect tree; do not collapse their all-cut coefficients into a silently
larger unreported Sigma. A split/completion node has unitary prefixes and
at most `m+2` sequential child residuals. A frame has two; a base has fewer
than m; a remainder fewer than N. The wrapper, if grouped, has at most D+3.
Therefore for D>=N a valid coarse bound is

    max Sigma_node <= N (D+3).

This deliberately retains the wrapper's D dependence. A wrapper cannot in
general be bounded by N merely because the local remainder is below N.
For every node the chronological argument is: if earlier child contracts
held, its local error term is at most `Sigma_node E_root`; if this is at
most 1<=B_root, the next child lies in the advertised enlarged radius.
Its total contract applies, allowing the induction to continue.

Take g=0 for D>=19 and g=5 for 1<=D<19, and set

    F=p+D+g,    J=h+D+2,    W=F+J+1=p+h+2D+3+g.

For D>=N, `344t<D/8` and `357t<D/8`. Also
`3 log2(D+3)+H<=D/8`: if `2^k<=D<2^(k+1)`, k>=16, its left side is less
than `4k+7<=2^(k-3)<=D/8`; the elementary integer induction is recorded.
Hence

    X(D)+H+log2(D+3) < D/4 <= (D-1)/2.

It follows that `E_root*N*(D+3)<=2^(-p-1)<=1`, closing the admission guard,
and in particular `E_root<=2^(-p-1)`. The radius exponent satisfies

    h+(D+1)/2+L(D) < h+D+2 = J,

so every certified signed component lies strictly inside the W-bit range
on grid 2^-F.

If ell=0, the retained structure has no raw contexts or upper ordinary
frames; only the sequential base/wrapper estimate remains. The guard is
equivalent to

    (D+3)^4 <= 2^(D+2g-1).

The verifier checks D=1,...,19 exactly. It continues for D>=19 because
`((D+4)/(D+3))^4<2` there and decreases. The control g=4 at D=3 fails.
Moreover `(D+3)/2<=2^((D+1)/2)`, so the direct sequential stored bound is
at most `2 B_root`, again strictly inside 2^J. This concludes the conditional
common-grid, error and signed-admission implication for all D>=1.

The output error is a complex-modulus bound because the fibre norm bounds
each coordinate modulus. It does not preserve a strict unit-disk boundary:
the outer shrink/quantizer and analytic recovery changes discussed in the
rounded note still need their own full source and cost admission.

## 6. Integer temporaries and complete cost boundary

The actual native source has maximum numerator 14,729,531, at event 252,
and maximum denominator 393,216, at event 2798. It has 864 coefficients
whose numerators exceed 40,864. Thus the old rounded note's 16-bit numerator
premise is false for this source. The new safe bound is

    abs(a)<2^24,  b<2^19,  temporary signed width W+26.

Indeed a signed W-bit input has absolute value at most 2^(W-1), so
`abs(a*m)<2^(W+23)`. The rounding offset is below 2^18. Even forming an
ADD numerator `b*target+a*source+floor(b/2)` has absolute value below
`2^(W+25)`, the signed magnitude limit of W+26 bits, with room for sign
extension/carry. Lambda's denominator-two numerator uses fewer such bits.
An output width check is justified by section 5's source-cut bound, not by
merely enlarging its temporary. Variable power-of-two normalization divisors
can be implemented by a bit drop and carry, but their actual service and
schedule remain inherited contracts.

This width calculation is not a construction of total RDiv on the retained
machine. The existing exact table has different rejection semantics.
The rounded note outlines multiply/offset, a most-significant-first signed
division pass and possible reversals; a literal table must still account
for all those passes, head resets, full source and target access, staging,
restoration, owned allocation/return and erasure of initially dirty and
historically longer backing. Old parked ancestors and simultaneous children
remain live. None of them is removed by a source norm proof.

An optimistic positive tariff screen is nevertheless useful. Starting from
the published QUERY-only conditional total 826,265,904, keep its 2,734,992
exact 1125-conversion charge conservatively even though the unscaled rounded
mode does not use it. Declare the additional arithmetic model

    per noninteger a/b:
    4 (bit_length(b)+1) [1 + 3*1_(oddpart(b)>1)].

This prices one offset scan at every noninteger scalar and three extra
scans at an odd divisor, in the prior raw tariff's scan unit. It is a
declared model, not a measured physical guarantee. Use it also for outer
caller scalars and once for each denominator-two Lambda offset. The exact
current census is:

| Positive item | Charge in this declared model |
|---|---:|
| Native surcharge per call | 941,128 |
| All 18 native calls | 16,940,304 |
| Outer scalar offsets at all actual ports | 51,520 |
| Outer Lambda offsets at all actual ports | 173,760 |
| Total extra | 17,165,584 |
| Baseline plus extra | 843,431,488 |
| Remaining below inherited 10^9 cap | 156,568,512 |

There is no omitted field-replication factor in this **model census**. QUERY
and IDLE completed-child charges are already in the baseline, and the
18 native words, 416 outer QUERY lifetimes, 54 local owned lifetimes per
call and peak 43 local owned banks remain. Their complete positive costs
must remain in an actual implementation invoice. A finite table/code
construction, authenticated source decoding and any denominator setup are
additional fixed-template work, with positive finite constants; they are
not charged as zero by this package. The complete physical runtime has the
form of those fixed setup costs plus the actual full scans and historical
backing terms, each on width W+26. We do not have their certified coefficient
and therefore do **not** infer the cap, recurrence or a new kappa for the
rounded implementation from this optimistic table.

## 7. An actual source cut where the exact service cannot implement the contract

The five consecutive zero-based native events are authenticated literally:

    37476 MOVE  697   1042 -> 591   public
    37477 MOVE  1334  1042 -> 1046  public
    37478 MOVE  901   565  -> 591   public
    37479 SCALE 1334  1/2          frame1046
    37480 SCALE 697   -2/3         frame591

Start all arbitrary public inputs at zero and every earlier primitive
residual at zero. The ideal execution is zero. At the completed MOVE37476,
allow the child to return one quantum Delta in one real component of field
697; all other components and all subsequent child residuals are zero.
This is an allowed format output under a total child contract with
epsilon>=Delta and adequate radius. Such a contract is allowed by the
eta_X model for X>=1. The three intervening events do not access field697.

At SCALE37480 its numerator is 1. The exact result would have numerator
`-2/3`, which is not an integer. Therefore **for every common grid precision
F**, the retained checked exact SCALE rejects this permitted input. Making
Delta smaller reduces the absolute defect but never removes the
divisibility obstruction. This is a countermodel to an implication from
the abstract rounded-child contract to exact-service admission. It is
**not evidence that a retained MOVE implementation actually produces this
one-quantum defect**.

The total RDiv alternative returns numerator -1, whose residual is -1/3
quantum; that is within its half-quantum contract. An exact child, by
contrast, returns zero here and the checked exact scalar succeeds. Thus
the countermodel does not refute the ideal exact-grid theorem or the
S=1125 prefix proof; it locates the extra interface premise needed to move
between exact and rounded modes.

`boundary.py` compiles the frozen generic `SCALE(-2/3)` finite table and
executes it through the unchanged lifecycle `execute_table`. On widths
3 through 9 it checks zero, ±3, 1, and a late-component `(3,1)` failure:
35 cases, 21 accepts and 14 rejects, with a separate integer
divisibility/range oracle. Rejections leave every public component
unchanged; success restores all heads and erases initially dirty private
work. Rejected work/head positions may be dirty/unrestored: no rollback or
successful caller continuation is claimed. This bounded physical check
tests the existing generic kernel's semantics, not all current native
MOVEs or an installed #6936 occurrence-token binder.

## 8. Verification, limits and next obligations

Run `python3 -I -B research/query-only-precision-envelope/verify.py --suite all`.
Expected output is four `PASS_QUERY_ONLY_PRECISION_*` lines followed by
`AUTHENTICATED_SOURCE_FILES 11`. Registered normal and `-O` suites compare
all deterministic receipts. Source guards reject wrong MOVE source/owner,
a dependent frame basis, a public CLEAR, a changed J order and QSELF
reintroduction. Exact norm controls reject coordinate-sup contraction,
the false projector Lambda and omission of the Q^4 premise. A unitary Q
of `(3+4i)/5` gives Lambda squared norm 49/25, so unitarity of Q alone
does not justify the Lambda step. RDiv tie and residual-erasure controls
test other critical distinctions.

The independent methods here are induction plus exact positive source
propagation, reverse covector checks, exact integer guard inequalities and
a direct integer oracle against an unchanged physical scalar executor.
All were prepared with AI assistance. They are not independent human review
or kernel-checked proofs. A separately supplied lead review, when present,
is recorded with its actual scope and file hashes in `REVIEW.md`.

Open next questions:

* Construct and install a total signed RDiv service with the actual source
  token/header binding, W+26 temporaries, full lifecycle and historical
  backing costs. Checked exact division is not that service.
* Bind all complete-fibre norm/error contracts, including Lambda's chosen
  one-rounding semantics and native absolute phases, to literal all-column
  providers. A phase error can escape every norm check here.
* Independently discharge the retained compiler S1--S5 and ownership
  interfaces, or replace them with verified source-to-physical composition.
* Complete the actual physical tariff and outer shrink/analytic recovery
  changes before using a rounded implementation in a complete bound.

This package closes a source-specific numerical-envelope calculation and
reduces the precision seam to explicit total-service and inherited compiler
premises. It does not claim those premises are established.
