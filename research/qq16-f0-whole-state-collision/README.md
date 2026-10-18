# An original-input collision for the fully rounded finite F0 word

The literal finite native F0 reference has **2^512 distinct original inputs with
one identical complete output state** under its specified 53-bit component
rounding. All 480 helpers start at zero and return zero. The eight private
fields also start and finish at zero. This is a scoped noninjectivity theorem,
not a failure of an accuracy bound, a physical supplier, or a new kappa.

The collision occurs at the first ADD, before any native child. It therefore
needs no inverse-prefix reachability assumption. A deterministic continuation
cannot distinguish states that have already become identical.

## Arithmetic and original-input family

Use the 712-field, 512-complex-coordinate F0 reference in
`research/qq16-native-rounded-components/`. Its real components use
round-to-nearest, ties-to-even with 53 significand bits, separate scalar
multiplication and ADD, and the predecessor's pair-first Gaussian butterflies.
There is no injected error, underflow, overflow, or fused multiply-add.

For any sign vector sigma in {-1,1}^512, set the real components of L119 to
sigma and those of L169 to the constant 2^54. Every imaginary component and
all other fields are zero. These are exactly representable binary64 inputs.
In the source's data numbering, L119 is Y7 and L169 is Y57. Both are data
fields, not private workspace or an intermediate child return.

The original data bound is 2^54 per real component. Every input is on the
same integer grid and has the same field norms. Helpers, private fields and
any permitted outside information are identical across the family.

The authenticated first three unfiltered, zero-based events are

```text
0  phase("zero_frame_precondition")
1  L119 <- RN(-L119 / 2)
2  L119 <- RN(L119 + RN(L169 / 2))
```

The phase event is a control label in this reference. At event 1, each target
component becomes -sigma/2 exactly. The source term at event 2 is exactly
2^53. Immediately below 2^53, the adjacent representable number is 2^53-1;
immediately above it, the adjacent number is 2^53+2. Thus 2^53-1/2 is a tie
that rounds to the even 2^53, and 2^53+1/2 also rounds to 2^53.

Consequently all 2^512 original states become exactly the same whole state
after event 2. L119 is the constant 2^53, L169 remains the constant 2^54,
and every other field is zero. This includes all helpers and private fields,
not merely the selected outputs. Exactly 512 real ADD components round,
each by absolute error 1/2. The rounding count and maximum absolute error
also agree throughout this family; the signed errors need not agree.

Every remaining operation is a deterministic function of that common state.
All complete endpoints therefore agree, even if a later operation rounds.
The source-bound finite replay computes their common endpoint as

```text
L169 = 2^54 * constant real vector
all other 711 fields = zero.
```

The recorded endpoint equality concerns values. The proof's merge at event 2
also uses identical binary64 values with the same positive-zero inputs in
all unaffected components. It does not require a general signed-zero
restoration contract for arbitrary inputs.

## What recovery requires

If a caller must recover the original sign vector exactly from the complete
F0 endpoint and a fixed-length b-bit record, with all other retained state
common across this family, the record needs b >= 512. There are 2^512
possible inputs and only 2^b records attached to the one endpoint. This is
an elementary counting bound on this specified boundary, not a physical
child tariff or a universal reversible-computation obstruction.

The two constant-sign inputs have different ideal outputs. Direct exact
native replay returns each original constant-sign input unchanged, whereas
the rounded word erases L119 in both cases. The rounding loss is consistent
with relative-error arithmetic at the large 2^54 data scale. It does not
refute the producer tolerance theorem or show a selected construction error.
A caller retaining an input copy or the signed rounding transcript escapes
the counting premise. The exact-grid producer policies also remain valid
alternatives. At the first cut, 55-bit precision distinguishes this same
pair; that control is not a sufficient precision theorem for the whole word.

## Evidence and reproduction

```sh
python3.12 -I -W error -B scripts/research_package.py \
  --package research/qq16-f0-whole-state-collision
```

The registered standard-library replay checks `RESULT.json`, then runs the
behavioral controls normally and with optimization. It is read-only. Direct
`verify.py --write PATH` creates an absent receipt rather than replacing one.

The certificate checks all 26,099 actual native events. The suffix is executed
once with the credited integer-dyadic engine and once with the separately
written binary64 arithmetic in the predecessor. Every changed suffix field
and all 364,544 complex endpoint amplitudes agree. The engines share the
source dispatcher conventions and credited monomial tables; they are not
independent native-semantic or human reviews. Two exact full-word controls
preserve the distinct constant-sign original inputs.

Six behavioral groups check an independent rational binade oracle against
2,814 integer rounding cases, all 512 single-coordinate sign changes, three
literal ADD mutants, replacement by exact ADD, every live source corruption,
and helper/trace/endpoint omissions. Rational first-cut controls also cover
precisions 2, 3, 8, 24, 53, 65 and 113. These controls are not full native
replays at those other precisions. The analytic signwise argument, rather
than enumeration of 2^512 inputs, proves the whole family.

Local registered replay passes on Linux x86_64 with CPython 3.12.15.
The direct optimized verifier also passes on CPython 3.13.5. Ruff 0.17.1
reports no findings in the new package. These are local checks, not hosted CI
or independent human review.

Scientific base and source closure are canonical main
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
`SOURCES.json` records exact Git blobs and SHA256 values. All five live inputs
are canonical-main files. No unrelated pending PR object or executable is
needed in a clean full-history checkout. The native archive's three member
hashes are checked by the unchanged predecessor loader.

## Scope and overlap

This changes the `supplier-boundary-audit` card's first scatter-export
experiment to a different named recovery implication. PR3273 already supplies
a tested opt-in scatter successor. The contribution here is the actual
original-input and whole-state boundary for a fully rounded F0 reference.

PR3258 establishes a local B1 child-return information bound. PR3294 supplies
an exact B1 prefix inverse under exact-map assumptions and does not claim a
fully rounded original-input collision. PR3293 analyzes exact helper frame
return. Their claims and credit remain separate. The concurrent mixed-
arithmetic PR3067 precision-family investigation rounds scalar operations
but keeps native children exact. This package uses the fully rounded
pair-first native implementation and a different input family, cut and
conclusion. The active multi-depth exact-grid investigation is also distinct.

Entry overlap covers 344 open PR bodies at 2026-10-17T21:11:52Z and 2,143
Discussion/comment/reply records at 21:12:24Z with complete pagination. The
search includes the explicit full-state and prefix-reachability handoffs.
A pre-publication refresh covers 348 open PRs at 21:19:58Z, 2,147 Discussion
records at 21:20:30Z and 2,630 closed/merged PR bodies at 21:20:58Z, all with
complete pagination and no warnings. Canonical main and guidance are unchanged.
This does not exhaust arbitrary diffs or unpublished work. Hosted checks are
recorded separately in the run handoff. No new
human-directed Discussion post is made under this session's restrictions.

Family decision: narrow and stop at this recovery implication. No new
producer construction or optimization campaign is proposed. The statement
is finite and local, at one 512-coordinate layer, under the predecessor's
native event semantics. It gives no full-cover/global caller entry-format
admission, all-depth rounded execution, F17 consumer, routing/tape/storage
bill, recursive tariff, selected cold replay, formal-kernel proof, supplier
admission, or complete multiplication theorem. Unknown costs remain unknown.

## Open next questions

Does an actual caller need exact recovery of these original signs, or only
an approximate output at the common data scale? Pin its complete retained
state and required output first. This distinguishes a genuine information
obligation from an irrelevant demand for reversibility. The actual caller
and its entry-grid/precision policy are the blockers.

If exact recovery is required, can its input copy or rounding transcript be
kept and consumed within the complete paid invoice? Start by counting and
locating that state, including eventual restoration. This package supplies
no native tariff for that storage or consumption. See `TASK.json`.

## Engineering constraints

New functions stay below 60 lines; no recursion or background process is
introduced. The fixed source inventory bounds the loops to 26,099 events,
712 fields and 512 coordinates. Source inputs are at most 32 MiB each.
The rational control precision is limited to 2 through 113 bits.

Power-of-Ten deviations are confined to the fixed scientific replay. Python
allocates managed vectors and exact integers during execution, and the
credited native module executes authenticated source at import. Rewriting
those frozen dependencies would change the independently retained reference.
Compensating controls authenticate every input before loading, use a fixed
source path, bound the event and vector domain, and compare the complete
suffix with hardware arithmetic. The table cache is bounded to 256 monomials;
new trace storage has at most 26,096 SHA256 strings. Test patches have bounded
targets and context-managed restoration. The registered launcher isolates
bytecode caches; the direct predecessor load uses source-only `run_path`.
A future general-input library should replace this fixed replay with a typed
static API and an explicit storage budget. No such library is claimed here.

## Credit

Nick Petalas. Apache-2.0. Automated drafting and checking were used; no
independent human or formal-kernel review is claimed.

Sricharan Vagvala supplied the fully rounded native F0 evaluator and its
binary64 corroboration. Tekalign supplied the retained Gaussian-vector
primitives in PR3017. Arham Tahir supplied the PR3036 scalar witness and
PR3067 mixed-arithmetic physical reference, distinct from this input family.
Credit Nick Petalas/PR3258/3293/2965 and Ross Richardson/PR2999 for the nearby
recovery and dirty-state questions, and Ali Romman, the QQ16 team, Sagar
Thakrar, DLamdata, ywz65, starship-s, Douglas Colkitt and the retained
supplier/native lineage in `research/joint-query/NOTICE.md`. Frozen source
bytes, notices and predecessor claims are unchanged.
