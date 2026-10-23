# Scalar compression on the final Cao native word

**Author-checked result; not yet independently reviewed; no new kappa.** Applying Cinna Davis's
PR4692 compressor to Cao Yifan's final PR4610 word, with one paid-profile-safe
exception, removes **151 scalar ADD macros in each orientation** while preserving
every chronological per-owner Fourier climb. The conservative real scalar allowance falls by **1,216 per call**: forward `158120 -> 156904`, backward `158168 -> 156952`. The complete paid profile remains
`{1:2201,2:412,3:510,4:127,5:40,8:8}`. All 408 independent helper boundaries,
632 independent inputs, main boundaries, native maps, phases and owned operations
are unchanged. Consequently the entire recursive moment is identical.

The changed word passes both retained exact literal interpreters on all 632
arbitrary-input columns in both directions. The formal prefix magnitude remains below the retained 2^192 envelope. A corrupted scalar sign is rejected.
No new native phase recipe is needed: every chronological frame transition is
exactly inherited. This is not an integer-multiplication theorem, a higher
conditional exponent, a measured runtime speedup or a selected-result update.

## Allowance accounting

The allowance is not a flat rate per macro. Each scalar primitive is priced by
`primitive_allowance` in the retained `rebuild_native.py`: a clear or copy costs
2, a scale costs from its coefficient's dyadic size, and an ADD with coefficient
`n/d` costs `2*(3 + bit_length(n) - 1 + bit_count(n) + bit_length(d) - 1)`, which
runs from 8 to 18 for the coefficients in this word. Per direction, the rewrite
deletes 205 ADD events with a combined allowance of 1,812 and inserts 54
replacement ADD events with a combined allowance of 596. The net count is
205 - 54 = 151 fewer events, and the net saving is 1,812 - 596 = 1,216. Costed
flat at 8 per net event the saving would be 1,208; the extra 8 is the
coefficient-size difference between the deleted and inserted events
(172 above the flat rate on the deleted side, 164 above it on the inserted
side). Both directions give the same three totals.

## Construction and predecessor credit

`construct.py` imports the original commuting ADD merger and reproduces the
credited triangle rewrite from PR4692. Its only new triangle restriction excludes
helper 628. Without that restriction, the repeated compressor removes 152 macros
but splits its original rank-four transition `0 -> 2085` into rank-two transitions
`0 -> 131 -> 2085`. For `0<t<1`, strict concavity gives `2*2^t > 4^t`, so that
additional deletion worsens the recursive bill. The restriction keeps 151 deletions
and the entire predecessor invoice. Four productive rewrite rounds suffice;
a fifth round confirms the fixed point.

PR5265 independently supplied 17 commuting inverse pairs (34 removed ADDs) on the
same final Cao word. This package uses PR4692's broader predecessor compressor;
it claims neither priority for the rewrite identities nor a kappa improvement.
Cinna Davis's original PR4692 applied the compressor to the older selected PR4470
word. Cao Yifan's PR4610 supplies the newer native word and joint-map optimizer.
Credit Cinna Davis, Dugongue, zxv, Jacob Alan Sussman and all retained native,
Clifford, scalar, geometry, compiler, precision and analytic sources.
Prepared for ahrazzle with substantial OpenAI Codex assistance; Apache-2.0.

## Exact replay

From the repository root, with Python 3.12 and the source files pinned in
`SOURCES.json`:

```sh
python3 -B research/cao-trace-retiming-20261023/verify.py
```

This rebuilds the word in memory, checks every source hash, verifies both exact
interpreters and the scalar corruption controls. Both interpreters
(`trace_cao_rows` and `trace_cao_literal`) are retained predecessor
implementations, not new implementations written for this package. The source archive and all frozen
predecessor receipts remain unchanged. The default verifier is read-only; `--write` is an explicit authoring option. `COMPRESSION-STAGES.json` records the
initial discovery run; `VERIFICATION.json` records the final package replay.

## Bounded search for a paid gain

Two full contact/helper/native-map models were run on the changed scalar graphs,
reusing the credited PR4610 exact frame enumeration and floating SciPy/HiGHS
optimizer. All 72 late native maps were available; the 12 prelude line contracts
were preserved. Every enumerated quotient interval had dimension at most five.
The helper exits, scalar chronology after the rewrite, and main boundaries were
fixed; all 408 helper entrances and scalar contacts were variable.

| Input graph | Variables | Constraints | Best local moment improvement over PR4610 |
|---|---:|---:|---:|
| 152 deletions, including the costly helper 628 triangle | 1,623,742 | 307,270 | -0.000223150946 |
| 151 deletions, helper 628 triangle excluded | 1,635,654 | 308,767 | 0 |

Both discovery runs retained the predecessor optimizer exponent `t = 1 - 0.00302157135`; the comparator is the final PR4610 paid/helper profile. The filtered optimum has identical complete profiles, so its zero gain holds at every exponent. Both runs completed in about 14 seconds and reported numerical finite-model optimality.
**These are bounded numerical negative searches, not exact ceilings or universal
impossibility results.** `UNFILTERED-SEARCH.json` and `FILTERED-SEARCH.json` preserve
the actual outputs. No negative-screen map candidate is admitted as a new supplier.

To rerun the filtered optional discovery (SciPy 1.17.0, NumPy 2.3.5 used here):

```sh
python3 -B research/cao-trace-retiming-20261023/construct.py --output /tmp/cao-trace-word.json.gz
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B research/cao-trace-retiming-20261023/search.py --word /tmp/cao-trace-word.json.gz --operator all --seconds 180
```

The discovery writes separate `DISCOVERY-*` files and does not overwrite the
frozen two search receipts. A solver is unnecessary for the exact positive scalar
result. The candidate has no changed recursive invoice, so no full controller,
compiler, BIT or outer-ledger run is claimed.

## Prelude-route scope

An initial attempt to free the common prelude lines was stopped when the live
overlap check found PR5096's first-image theorem and PR5179's inverse-return
rigidity theorem. The 152- and 151-deletion graphs both retain all 12 exact
post-inverse line caps, checked independently through reachable main-Y exits.
This is supplementary bounded evidence, not a new proof of those predecessors.

## Open next questions

A paid-profile improvement must change a restriction beyond this tested scalar
rewrite/contact model. One concrete first step is to replace an actual chronological
owner dependency while preserving arbitrary-input action, then test whether the
PR5179 path cap disappears. Its single-edge deletion is a relaxed graph control,
not a legal circuit edit. No repeated fixed-invoice search is justified by the
present negative results alone. The retained physical/native all-size, compiler,
precision, stock, analytic and recovery assumptions remain unresolved here.
