# Literal one-rounded global LAMBDA

**Result:** a source-bound physical provider implements
`Lambda_s(Q_f)=((1+s*i)I+(1-s*i)Q_f²)/2`, with one final rounding per
real/imaginary component and actual-input defect at most `eta_X`. It uses
an exact, paid translation for `Q_f²`, the unchanged serial monomial
implementation, a literal Gaussian numerator table, and explicit owned
staging and cleanup. **The new outer header contract remains to be installed
by the full caller; no tariff cap, new kappa or unconditional theorem follows.**

The source is the 3,095-event QUERY-only caller published at
`617903497387a98f7ca929ad0b6928dd32abffec`, using DreamingOfClouds'
[CrocSwap/integer-mult-bounds#6936](https://github.com/CrocSwap/integer-mult-bounds/pull/6936)
word and the [#6937](https://github.com/CrocSwap/integer-mult-bounds/pull/6937)
lineage. Its 14,480 expanded LAMBDA occurrences have 104 actual directions.
The exact source phase definition identifies `Q_f²` as the simultaneous
phase-free address translation by q in every central column.

## What is new

The published [precision package](https://github.com/CubeJerry/integer-mult-bounds/tree/56bc9383594a3efc303148e00bb746851abd1ed5/research/query-only-precision-envelope)
explicitly leaves a completed one-rounded LAMBDA primitive as a contract.
This package supplies its literal arithmetic and its actual source-to-monomial
recipe/header join. It does not treat a formal involution as a free reflection.

`LambdaProvider` copies the complete public field into one owned bank,
executes the unchanged serial provider with the new identity9/offset-q,
phase-zero recipe, forms both width-`W+2` Gaussian numerators, and stages
one-rounded results back into that owned bank. Only after all components
pass final range checks does a separate literal COMMIT table write the
public field. Two one-component numerator banks are reused throughout.

`HeaderView` physically changes exactly `remainder=0` and
`selected_axes=9f` in a private 23-field descriptor. It preserves the full
ambient row and every other field. This handles outer remainders that
cannot be passed directly to a rank-nine monomial. The complete geometry
and the meaning of the central axes are explicit in `PROOF.md`.

The Gaussian STAGE tables have **5,275 rows per sign**. They form
`a-s*b+c+s*d` and `b+s*a+d-s*c` exactly before rounding. Three plus signs
and one minus sign give strict `W+2` headroom, so cancellation is not lost.
Upward rounding is applied once to each complete numerator; no commutation
of rounding with signs is assumed.

Global LAMBDA stays outside tensor powers. Applying one butterfly per
column would be wrong: two odd factor characters give global Lambda=1,
while their factor Lambda product is -1. The source and controls retain
this distinction.

## Admission, error and ownership

The assembled provider requires uniform signed width `W>=2`, a common grid,
canonical complete fields, valid reserved current geometry, disjoint
physical segments, origin public/context heads, and contiguous old private
bodies. It succeeds exactly when the rounded outputs fit the public width.
The sufficient norm domain in the proof gives a total contract without
range rejection. Any X-fibre used for its norm must contain all 9f
translated axes.

Its per-component residual is at most half a grid unit, so its actual-input
complete-fibre defect is `eta_X=2^((X-1)/2)*Delta`. The current precision
width/radius substitution remains conditional on genuine caller/header
installation and the other retained operator contracts.

A named late arithmetic rejection preserves the entire public field,
retires the partial owned copy and all private work, and restores public
and context heads. This cleanup is explicit in the wrapper. Arbitrary
malformed/interrupted native execution and process termination are outside
that rollback statement.

The current rank-nine construction has **1,965 fixed owned roles**, including
all retained monomial/ordinary/descriptor inventory, the new full-field
copy and two numerator banks. All old backing remains allocated after
retirement. No new recursive paid job or productive helper credit is added.

## Positive cost and limits

The complete inherited serial bill remains

    O_9(f*((g+1)*(Vraw+M1*A1^6)+V+(E+1)^4+P)),

with `g=popcount(q)` (3 or 7 at these source ports). The new Gaussian work
has the conservative positive tape-plus-control bound `4096(S+1)`.
Copying, physical head returns, private header work, retirement, fixed
inventory, finite setup and initial dirty backing are additionally paid.
Only under the proof's explicit padding absorptions does this simplify to
`O_9(fV)`, plus setup and old history. No exchange rate to the old
1000-unit LAMBDA allowance or full supplier raw cap is asserted.

The new recipe is derived from #6936. Reusing a generic implementation does
not mean the selected #6030 catalogue covers #6936: those sources have
22,803/3,453 versus 71,144/6,323 events/MOVEs respectively. Neither full
catalogue membership nor an existing outer-LAMBDA exporter is inferred.

## Reproduction and executed evidence

```bash
python3 -I -B research/current-rounded-lambda/verify.py --suite all
python3 -I -O -B research/current-rounded-lambda/verify.py --suite all
```

Expected: five `PASS_CURRENT_ROUNDED_LAMBDA_*` lines. Registered runs split
into audit, arithmetic, descriptor and composition suites, each capped at
120 seconds. Standard library only; exported replay needs no Git/network.

Executed author evidence includes 544 exhaustive width-1/2 four-input cases,
1,536 wider endpoint cases, 12 complete physical header checks, both-sign
full reduced-rank compositions, a late rejection and retry, arithmetic
mutants, strict typed-source controls, and 53,248 source-character/compiled-
flip checks. Separate lead AI review checked 48 wider cases through
129-bit components, with a read-only-public STAGE trap, long-to-short
history, an independent rational oracle, 1,020 global character cases and
the full positive arithmetic bill. Exact receipts and reviewed hashes are
in `REVIEW.md` and its unchanged runner/JSON artifacts.

**A complete nine-axis source numerical execution is not claimed.** The
minimum case has 4,096 records. The 16-record reduced run used over five
million physical actions in 0.91 seconds; simple record scaling already
screens the source case above the 120-second attempt cap, before extra
flips. This is a feasibility screen, not a wall-time lower-bound theorem.
The source-specific all-size join is proved using the retained provider;
reduced physical tests are clearly labelled.

## Open next questions

1. Install the actual outer source-token/header exporter and prove its
   central-axis, common-grid and radius substitution for every occurrence.
2. Assemble all 14,480 positive invocation bills, owned lifetimes and
   unfinished-context stock into a complete physical supplier invoice.
3. Complete the remaining native, arithmetic, recursive and analytic
   recovery interfaces. All five framework assumptions remain globally open.
4. If a larger bounded replay environment is available, run a full actual
   nine-axis composition without replacing its runtime with a host oracle.

## Credit

Prepared for **@CubeJerry**, with substantial **OpenAI assistance** in proof,
implementation, source analysis and verification. Credit DreamingOfClouds'
#6936/#6937 source and proposal; the native phase/monomial lineage including
[CrocSwap/integer-mult-bounds#3087](https://github.com/CrocSwap/integer-mult-bounds/pull/3087)
and [#4172](https://github.com/CrocSwap/integer-mult-bounds/pull/4172);
CubeJerry's lifecycle, scalar, serial-provider and source-precision work.
Gaussian identities, carries, Fourier characters and rounding are classical.
The contribution is their literal source-bound physical join and complete
stated cost/domain proof. AI review is not human or proof-kernel acceptance.
Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
