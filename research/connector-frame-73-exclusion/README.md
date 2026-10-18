# Paid connector frames still require 74 map calls

The generic five-source dirty connector cannot use **73 A/B map calls**, even
with arbitrarily many invertible changes of the connector's coordinates.
Together with the existing 74-call construction, this gives the exact minimum
of 74 map calls in the contract below, even if frame calls have zero price.
This closes the first open question in Adam Gall's
[PR #1915](https://github.com/CrocSwap/integer-mult-bounds/pull/1915), inspected
at `d30d64fea909219c364b11c2452f2207326e2b1f`.

PR #1915 excludes 72 map calls and proves the 74/76 unit-token bounds.
Its normalization argument is credited and restated here. The new step handles
the one operator that must occur three times in a 73-call word. No selected
supplier, physical runtime improvement or new multiplication exponent is claimed.

## Contract

Work over F2 with five immutable L-bit source rows `x_j`, 31 output rows
`y_m`, one connector `z`, and `L >= 1`. Every row starts arbitrarily dirty.
For every nonzero five-bit mask `m`, the required output is

```text
y_m += A_m sum_{j: m_j=1} B_j x_j;   all x_j and z restored.
```

The maps `A_m,B_j` are arbitrary L-by-L binary matrices. They may be singular
or noncommuting. A single straight-line word, including its frame matrices,
must work for every choice of these maps and inputs. The word may depend on
L and the requested masks, but not on the entries of the maps.

The only operations are complete calls

```text
B_j: z += B_j x_j
A_m: y_m += A_m z
FRAME_R: z <- R z, with R invertible
```

Each call preserves other rows and restores its private scratch and tape heads.
No additional connector, source mutation, output mixing, reset, direct product
call or free copy is allowed. Frame implementations are charged. This is
PR #1915's extension of Ross Richardson's
[original connector contract](../universal-connector-boundary/README.md).

## Normalize the connector and count the exceptional map

Let `P_t` be the chronological product of frames through time t. In normalized
coordinates `u = P_t^-1 z`, a source event at phase H inserts `H^-1 B_j x_j`.
A readout at phase K applies `A_m K` to u. Arbitrary connector dirt forces
`P_final = I`. Each active B needs at least two calls to cancel its transported
source. Each active A needs at least two calls to cancel connector dirt.
There are 36 active maps, so at least 72 map calls are necessary.

For a paired source, restoration gives `H^-1 + H'^-1 = 0`, hence `H=H'`.
For a paired output, dirt cancellation gives `K+K'=0`, hence `K=K'`.
Between two readouts, a paired source contributes zero if both its events or
neither event occur in the interval. If exactly one occurs, its coefficient is
`A_m K H^-1 B_j`. For arbitrary A and B, this equals `A_m B_j` precisely when
`K=H`, and cannot be identically zero because `K H^-1` is invertible.

Thus a 72-call word projects to an ordinary twice-per-source word whose prefix
differences include every requested mask. Richardson's exact 945-pairing
exclusion rules this out for five sources. The local verifier reconstructs
that census without importing predecessor code.

At 73 calls, exactly one map occurs three times and every other map twice.
The following two cases exhaust the possibilities. They use no assumption
that every map count is even.

## Case 1: one output has three readouts

All five sources are paired. Every pair of source labels occurs together in
some paired output, even after removing the exceptional output from the 31
masks. The preceding coefficient condition therefore forces every source's
insertion phase to be one common H.

Let `K_1,K_2,K_3` be the three exceptional readout phases. Dirt cancellation
requires `K_1+K_2+K_3=0`. All three are invertible, nonzero and distinct.
Their proper nonempty subset sums are exactly the three K matrices.
The exceptional mask is nonzero, so some source coefficient must equal H
before multiplying by `H^-1`. Hence exactly one K equals H. Write its index
as r, and the other two indices as s,t. Then `K_t=H+K_s`.

Let `q_r,q_s,q_t` be the source-parity prefix vectors at these readouts.
For each source j, the exceptional coefficient before `H^-1` is

```text
H (q_rj + q_tj) + K_s (q_sj + q_tj).
```

Distinct nonzero matrices H and `K_s` are linearly independent over F2.
For this expression to be either zero or H for every j, `q_s=q_t` is
necessary. The requested mask is therefore `q_r + q_t`, already an ordinary
two-prefix difference. The extra readout adds no mask. The other 30 outputs
also give ordinary differences, contradicting the 945-pairing exclusion.

## Case 2: one source has three insertions

Call the exceptional source e. The other four sources are paired and every
output is paired. Outputs containing pairs of ordinary sources force their
insertion phases to one common H. Any output mask containing an ordinary
source must have readout phase H.

Write the three normalized insertion matrices of source e as
`U_1,U_2,U_3`, where each U is the inverse of its physical insertion phase.
Restoration gives `U_1+U_2+U_3=0`. They are invertible and distinct. Consider
an output containing e and one ordinary source. Its interval must select a
subset of the U matrices with sum `H^-1`. The proper subset sums are exactly
the three U matrices, so exactly one, `U_r`, equals `H^-1`.
For the other indices s,t, `U_t=H^-1+U_s`.

For any readout interval with phase H, let `d_k` indicate whether exceptional
event k lies inside it. The normalized coefficient of e is

```text
H^-1 (d_r + d_t) + U_s (d_s + d_t).
```

It must be zero or `H^-1`. Independence of `H^-1` and `U_s` forces `d_s=d_t`.
Replace the exceptional event at r and the event at s by two ordinary
toggles of source e, and delete event t. Each interval for an output containing
an ordinary source preserves its mask, since the new e coefficient is
`d_r+d_s`. All ordinary source coefficients also remain unchanged.

Only the singleton mask `{e}` may have used a different readout phase. It is
always a prefix difference of the new word: take the boundaries immediately
before and after either remaining e event. Consequently the new word has two
events per source and covers all 31 nonzero masks. This again contradicts the
945-pairing exclusion. This replacement is a proof device, not a claim that
arbitrary frame words can be erased without changing their map.

## Complete cost consequence

Both 73-call cases are impossible. Richardson's `five_extra_output` word
attains 74 map calls without frames, so the map-call minimum is exactly 74.
The verifier checks that full word and its dirty-state inverse.

For a word W, price the complete implementation as

```text
C(W) = I(W) + P(W) + D(W)
       + sum_F n_F c_F + sum_frame_events c_R.
```

I includes admission and row layout. P includes coefficient and frame
preparation. D includes instruction storage, scheduling and root dispatch.
Each complete call price includes its arithmetic, source access, target
updates, private scratch and head restoration. At fixed positive map prices,
let `c_min = min_F c_F`. The new necessary map/frame bill is

```text
sum_F n_F c_F + sum_frame_events c_R
    >= 2 sum_F c_F + 2 c_min + sum_frame_events c_R.
```

If the word uses a nonidentity frame, restoring arbitrary dirt requires at
least two nonidentity frame events. With a positive lower frame price f_min,
the last term is at least `2 f_min`. For equal map price c, frames cannot
reduce the `74 c` map bill even when their own price is zero. For unit call
tokens this recovers PR #1915's 74 minimum and 76 minimum when nonidentity
frame use is required. For `L>=2`, a shear/inverse pair followed by the
unframed 74-call word attains 76. These token bounds were already in #1915.

This is not an exact weighted optimum. Additional calls to cheap maps could
change which expensive map must repeat, and I, P and D still need pricing.
No occurrence of this interface in the selected supplier is established.

## Reproduce the finite evidence

The standard-library verifier checks the proof's finite implications and
independently replays the inherited positive construction. The claim for
arbitrary L is the written proof above, not a finite-search extrapolation.

```sh
uv run --python 3.12 --no-project python scripts/research_package.py \
  --package research/connector-frame-73-exclusion
uv run --python 3.12 --no-project python -I -O -B \
  research/connector-frame-73-exclusion/verify.py
```

Both commands passed on CPython 3.12.13, macOS 27.0.1 arm64. The registered
run emitted `PASS_REGISTERED_RESEARCH_PACKAGE` and passed all four behavioral
tests. The optimized direct run emitted `PASS_CONNECTOR_FRAME_73_EXCLUSION`.
The repository's 42 onboarding tests, package metadata/source-pin check,
Ruff checks and `git diff --check` also passed. In a temporary mutation,
reversing the output-acceptance predicate made three of the four tests fail.
Hosted CI is separate. No selected-supplier cold replay was run.

The receipt includes these bounded checks:

| Check | Domain and conclusion |
| --- | --- |
| Phase identities | All 12 and 8,064 ordered zero-sum invertible triples in GL(2,2) and GL(3,2); all subset sums obey the two-case reduction |
| Arbitrary-map coefficients | 294,912 direct vector comparisons over every pair of two-by-two binary A/B maps, including singular and noncommuting maps |
| Exceptional output | All 810,810 pairing/boundary-triple/distinguished-phase cases; 170,820 scalar-mask cases, no new mask |
| Exceptional source | All 51,975 annotated source words; at most 31 masks even after granting the singleton; a concrete wrong-deletion counterexample |
| Full-word controls | The pinned 74-call word, basis-column and dirty-state inverse replay; odd-count framed restoration; missing restoration, missing readout and wrong target rejection |

The source enumeration uses `binomial(11,3) * 105 * 3` cases: three positions
for source e, every canonical pairing of the four ordinary sources, and the
distinguished event. Exchanging the other two phase labels does not change
scalar-mask validity. It grants arbitrary frame availability at readout
boundaries, which enlarges the possible schedules. The exclusion survives
this favorable relaxation.

## Scope, provenance and credit

Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
[TASK.json](TASK.json) records selector seed, scope, overlap and predecessor
head. [SOURCES.json](SOURCES.json) pins the inherited certificate, contract
and attribution by Git blob and SHA256. The local proof includes all needed
normalization steps and imports no code from pending PR #1915.

The final overlap refresh completely paginated 588 open PRs at 14:30:45 UTC
and 566 Discussion records at 14:32:56 UTC on 2026-10-14, without warnings.
The direct predecessor remained at its pinned head. These are search leads,
not proof of novelty; arbitrary code diffs and all closed work were not searched.
The [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884#discussioncomment-18925922)
records the complementary scope and attribution before the computation.

Adam Gall's PR #1915 supplies the paid-frame contract, normalization,
paired-endpoint proof and the precise 73-map question. Ross Richardson's
PR943/PR934 supplies the universal connector, paired-prefix criterion,
five-source exclusion and attaining word. His pinned NOTICE retains the
common-factor fanout and dirty-commutator lineage, including @shhxera and
Chafik Boukhalfa. PR #1887 uses two connectors, PR #1858 uses map-dependent
structured charts, and PR #1524 permits source mutations. Those contracts
fall outside this theorem and their constructions are not contradicted.

The selected record and all frozen inputs remain unchanged. This result
does not settle operator-specific synthesis, more workspace, physical hosting,
precision or any inherited multiplication-theorem obligation. It is a scoped
written proof with exact computational checks, not a proof-assistant theorem.

## Open next questions

No additional investigation is assigned by this package. The named 73-map
question is closed under its exact generic one-connector hypotheses. A new
construction attempt needs an explicit change to those hypotheses or a
separate unequal-price objective. No selected-supplier occurrence or cost
data is supplied to justify choosing such a next experiment here.

Prepared by Arham Garg with substantial OpenAI Codex assistance in the proof,
implementation, checking and writing. New work is Apache-2.0. No independent
human review is claimed.
