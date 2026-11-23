# Independent review of the selected joint native/compiler implication

## Disposition and frozen boundary

**Accept the conditional joint implication stated in the reviewed proof, under
exactly `owned_erasure`, `precision_tape`, and `analytic_recovery` in their
pinned selected meanings.** I found no blocking mathematical objection after
checking finite syntax versus runtime execution, whole-owner batching, new
carrier arithmetic, and parameterized primitive domains. This concerns the
alternative implementation described there. It does not assert execution of
the historical selected transition table, change the selected record, or
certify a complete unconditional multiplier.

Reviewed file: `work-compiler/package/PROOF.md`, SHA-256
`814c514717592ef64bf4afd1bc5dff8284cf534790287fc8b2d1a0408c6caee5`.
This version includes §§5.1 and 6.1. The disposition must not be transferred
to an earlier draft lacking those parameterized interface arguments.

| Source | Frozen commit | Reviewed material |
| --- | --- | --- |
| Ali Romman, #7828 | `03b572b3b9ab72c6ba67762e85e1630cda1daad5` | `single-grade-rank-compiler/PROOF.md`, `APPLICATION.md`, `product.py`, `schedule.py`, selected witnesses in `RESULT.json` |
| CubeJerry, #7840 | `adf2e0aa6777977a280ce50f8938f4a0f4f19b76` | `selected-native-four-premise-specialization/PROOF.md`, especially §§2–8 |
| Canonical interface | `e54523517d0f03e58352e647c403a5af3e525a57` | Selected record, finite-precompilation and delayed-cover bridges, specialization and selected application, common-grid proof and cited cover/row contracts |

`EVIDENCE.json` records SHA-256 values for sixteen authenticated references.
The independent boundary checker verifies their supplied Git blob IDs, and
the canonical SHA-256 pins, directly from bytes. Neither the submitted proof
nor the predecessor files was edited during this review.

## 1. The joint implication avoids a logical cycle

I checked the dependency structure by treating a positive query as a typed
formal operator before considering an implementation. Three objects must
remain separate: a raw list with a proved formal denotation; a finite compiled
list whose rank-one queries remain formal; and a runtime interpreter for that
list. The proof maintains this separation.

For the raw complex word, tensor multiplicativity applies to operator
products, while the scalar/free-word identity is proved separately. No tensor
power is distributed over ADD or LAMBDA. Absolute monomial phases lift once
per column; scalar coefficients act once on the entire array. The whole-field
Q² is formed before LAMBDA's two-term combination. The selected one-column
catalogue supplies complete operator identities, not numerical samples used
as an all-column assertion.

For the binary word, polynomial identities of split projectors supply the
address-map denotation over the rational ring. Payload arithmetic over F2 is
separate. The 111 coupled raw main pairs use the same route within each pair.
Only after the complete caller has role-diagonal endpoints can the compiler
use different whole-job matchers on its independent productive roles. This
ordering is essential and is respected.

The finite compiler needs exact matrix arithmetic, owner labels, instruction
substitution and integer batching. Elementary arithmetic suffices; it does
not execute a positive query or assume a fast integer multiplier. Rational
matchers and exclusion witnesses are formed before selecting q. Later
cover-dependent pivots are inverted only when they are local-ring units;
there is no infinite prime-exclusion oracle.

The runtime proof uses the lexicographic order `(stage, active width)`.
Same-stage children have width at most `floor(width/N) < width`, including
bad-class children and their reversals. A movement call goes to a completed
lower ordinary stage, with no requirement that its width decrease. This is
well-founded: after finitely many stage decreases, any infinite descent
would give an impossible infinite decreasing sequence of natural widths.
The complex service comes after all binary stages. The elementary stage is
an actual complete scan/bucket algorithm, not the previously assumed
positive-saving backend.

Thus the proof does not combine two circular existence implications. It
constructs finite syntax using denotations, then constructs execution by a
different well-founded induction.

## 2. Whole owners, target zeros and paid queries

The chronological product assigns separate U instances to V's productive
roles. At a suspended paid position, each instance contributes its actual
owner, possibly an owned center. Correlation of their values is allowed by
arbitrary-input linearity; owner aliasing and copied productive credit are
not. Complete adapters and role order return before the parent resumes.

Unselected targets are supplied with distinct owned zero fields. They may
be nonzero internally, so all instructions and paid positions remain in the
word, including queries whose current value is zero. The completed direct-
sum endpoint returns each discarded field to zero before its retirement.
Actual nonzero private CLEAR instructions still use `owned_erasure`. Neither
endpoint zero nor arbitrary-input linearity supplies a physical allocator.

For a homogeneous e-axis job, `c=floor(e/K)` and the first `Mc` working axes
fit in the original N-axis field. A child has rank `h_i c < e`; its next
working window is no larger than its parent's. Spectators, remainders and
the complete root remain present. The nondecreasing depth function ensures
that divisibility by `B^D(e)` supplies every smaller required child batch.
Root tiles reuse the same productive fields, so sequential tiles do not
create extra output credit. Keeping both original whole-job factors around
a split also avoids assuming that a two-sided normalization is one
conjugation by an inverse pair.

I inspected the scheduler and the contributor's separate group-algebra
oracle. Its finite controls exercise aliasing zeros, dropped zero queries,
wrong return permutations, tensoring an exterior scalar, and reversing a
paid leaf. The 18-case receipt is corroboration; the universal conclusion
rests on the preceding argument. I did not rerun that unchanged toy suite.

## 3. Funding and the new common-grid boundary

The modal exchange inequalities are sufficient: each last selected priority
dominates every next unselected priority, so the type is a multinomial mode.
Its mass is at least the inverse of the number of types. The two margins in
§3 control both parts of the split bill: use
`log(T_-/P_+) >= 1-P_+/T_-` for the unsplit moment and the second margin
for `J^(t-1) P(1)^v/T_-^v`. With at most `(v+1)^d` types, the displayed
condition on `v*delta` gives `mu < 3/8`. This is not inferred from raw
endpoint tests alone.

The leaf recurrence gives `F(e) <= 2 K^(1-t) e^t`. Concavity across at most
`3M/K` root tiles and the new H inequality then give
`P_N/W_N < N^(1-U)`. The paid list includes the zero-valued queries. The
logical-record estimate is explicitly pre-cover and is not a polynomial
bound on the physical cover cardinality.

The new independent checker imports no contributor scientific module. It
reads the frozen witnesses and checks the new ambient/funding inequalities,
the three exact cold-stage debits, and the unfinished-depth grid comparison.
The actual binary ambient is `8+18*7=134`, not 127; the complex ambient is
`9+18*8=153`. For `L_raw=2(H+v)`, the bit lengths of `356 L_raw` are 74 and
99. Both comparisons with the respective `N=2^H` are strict without
constructing N.

The depth argument also has the required source meaning. One chronological
product adds at most v open raw levels, while homogeneous recursion shrinks
by at least `2^v` and has at most `H/v` levels. Allowing raw caller/native
contexts gives `2(H+v)`. Completed siblings and parallel instances do not
add unfinished denominator debt. Runtime recursion over a D-axis original
root has at most `ell=floor(log_N D)` such compiled levels. Hence, when
`ell>=1`, `356 L_raw ell < N ell <= N^ell <= D`. At `ell=0` the elementary
Clifford base has no unfinished raw context.

The complete original root and per-call 1125 scale/unscale discipline are
preserved. Completed children remove only their extra exterior debt. This
invokes the retained prefix proof correctly; it does not replace it by
endpoint cancellation or assume exact numerical children to prove their
own exactness. Root preprocessing and the single final truncation remain
those covered by the selected outer interface.

## 4. Admitted grammar and tariff quantifiers

The principal possible gap would have been replacing `precision_tape` by
the broader premise “this new arbitrary program is physically admissible.”
The frozen §§5.1 and 6.1 avoid that step. The exact canonical contracts
already parameterize fixed finite monomial/positive-child programs and
rational-cover routes by their actual dimensions, owner counts, scalar
allowances and full route records. Each generated instruction is mapped
into that grammar: fixed complete coordinate/role placement, source scalar
operations, disjoint positive splits, image/kernel matchers, rank-one
children, or finite descriptor recipes. No generic address gather is used.

The complete right route is a low/high local-ring cover bijection with its
carry and inverse. Its exterior weight reads exposed ancestors and atom
indices, independently of the invocation's fresh cover and roles. New
leaf weights become data of the next invocation's exposed parent. This
retains the admitted weighted-child class; independently normalizing several
parent roles into incompatible fresh weights would not.

The fallback multiplier is charged. Its loss is paid by the separate
`10^-10` debit and the actual `q>2^45 N^5` inequality. Fresh low/high
cylinders justify the bad-class fraction separately at every paid edge;
no stochastic independence across calls or payloads is required. All those
children obey the same strict active-width descent.

The complex tariff remains in its source domain: `f<=p`, address length
`O(p)`, complete dirty-control reservations, the specified record-width
condition, and a record fibre dominating every fixed descriptor polynomial.
Binary descriptor preparation is polynomial in original e and therefore
in its fixed `w=ceil(e^(1/250))`; the complete target fibre is what pays
for it. These are per-fixed-template bounds. They do not provide a constant
uniform over a growing family of compiled templates. The proof fixes the
template, prime, route expansion, constants and cutoffs before varying
operand length, as the retained contract requires.

The stock, parked-parent and scalar prescriptions use the new N, W, P, O
and G. A new N-dimensional route is not priced by the old 134-dimensional
raw allowance. `owned_erasure` still pays new banks and discarded targets;
`precision_tape` still supplies completed primitive tariffs and backing.
The joint theorem, and this review, do not prove either remaining premise.

## 5. Independent explicit productive-cover cutoff

The proof's effective stock-fit argument is valid. The following additional
bound checks that the new carrier is actually substituted. It concerns only
productive-cover rows, not owned banks or compact-control stock.

Let `N=2^H`, `H>=3`, `W_N<=N^15`, and `q>=2`. Since
`|GL_N(F_q)| < q^(N^2)`,

```
ell_F = ceil(log_q(W_N |GL_N(F_q)|))
      <= N^2 + 15H <= 2N^2,
C_row = 16(N^2+ell_F+1) <= 64N^2.
```

The middle inequality holds at H=3 and persists as H increases: `2^(2H)`
grows by four while `15H` increases by 15. Thus the three live ordinary-stage
reservations are at most `192 N^2 e^(1/250) log2(2e)`, once lower-stage
target widths are at most e as required by the proof's fixed-template domain.
They fit strictly within `e/2` for every

```
e >= 2^(4H+100).
```

For a direct proof, write `2^j <= e < 2^(j+1)`. It suffices that

```
249j > 500H + 2251 + 250 log2(j+2).
```

At `j0=4H+100`, `j0+2=4H+102 <= 2^(H+6)`. The left side is
`996H+24900`; the resulting right side is at most `750H+3751`. Thereafter
the dyadic upper bounds decrease in ratio, since `(j+3)/(j+2) <= 4/3`
and `(4/3)^250 < 2^249`, itself implied by `(4/3)^2 < 2`.

This is a computable productive-row cutoff from the new H alone. The full
algorithm must take the maximum with its primitive, descriptor, ownership,
scalar and outer-geometry cutoffs. It is not a practical entrance bound or
a replacement for those requirements.

## 6. Objections, limits and remaining premises

There is no blocking objection to the frozen conditional implication. The
acceptance does not extend to altered claims that skip zero queries, give
coupled raw pairs unequal routes, choose q from only raw frames, reuse old
route costs at the new dimension, replace prefix precision by endpoint
cancellation, or require tariff constants uniform over growing templates.
The reviewed proof explicitly avoids those alterations.

| Retained premise | Work not supplied here |
| --- | --- |
| `owned_erasure` | Concrete allocation, erasure and historical ownership for added zero targets, nonzero raw clears, parked parents and primitive banks |
| `precision_tape` | Literal fixed-tape tariffs, complete descriptor/route execution, full backing, and the prescribed precision/storage interfaces |
| `analytic_recovery` | Selected analytic decomposition, fine-prime geometry, layer interface and exact integer recovery |

The selected native catalogue/scalar predicates and outer theorem are
imported mathematical results from the pinned #7840/canonical sources.
I read their relevant proof interfaces; I did not freshly replay the
3,057-map catalogue, all scalar events or the complete outer checker.
The contributor's arithmetic engine and receipts were inspected, not
relabelled as this reviewer's executions. The new independent execution
is the source/boundary check below. No production-dimensional word or
multiplier was materialized, and no human or proof-kernel acceptance is
claimed.

## Reproduction and credit

From this directory:

```sh
python3 -I -B check_boundaries.py
```

Publication integration places the authenticated `refs/` tree beside this checker,
and the frozen reviewed `PROOF.md` one directory above it. The checker's default
path resolution was adapted to this layout; no arithmetic or review gate changed.
Pass `--source-root` only to select an identically arranged review directory.

The JSON status is `PASS_JOINT_BOUNDARY_CROSS_REVIEW`. It authenticates the
reviewed proof and pins and checks the targeted new-carrier, stock, grid,
covered-moment and cold-stage arithmetic. Checks use explicit exceptions
and exact integer/Fraction arithmetic.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance,
by a separate task agent from the joint-package author. Ali Romman supplied
the single-grade compiler. The selected specialization, raw callers/native
words, primitive contracts and common-grid arguments retain their source
credit. The explicit productive-cover cutoff in §5 is an independent
calculation made for this review. This is model-assisted scoped review,
not independent human peer review.
