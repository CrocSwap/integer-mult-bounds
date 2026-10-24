# Fresh-stage terminal codes: an all-length obstruction and a changed interface

For the actual PR4933 code, a product of any fixed number of distinct fresh
stages cannot acquire a constant-size scalar/monomial terminal decoder. This
holds for every order, every nonzero integer stage power, arbitrary scalar
owner mixing, and owned workspace. The proof gives
`ADDs >= max(0, 2f - 24k)` for k stages and tensor width f.

Exact short certificates cover **all sixteen negative-output banks** in the
saved caller, including its eighteen-stage bank. They give the stronger bound
`ADDs >= max(0, 2f - 6)` for each bank. These bounds cannot be added across
banks. The earlier two-stage result has a better constant for its two banks.

The [proof](PROOF.md) separates every owner path through the private stage
coordinates. It then contracts a few coordinate columns to retain one
nonmonomial term. The [receipt](RESULT.json) and [marker certificates](MARKERS.json)
contain the finite source and caller checks. The all-length statement rests
on the written induction, not a stage-count census.

**No new kappa is claimed.** The selected conditional value at the pinned base
is 0.0030217758. This result rejects free terminal cancellation by adding more
distinct fresh stages. It does not reject paid decoders, a number of scalar
operations that grows with f, correlated retained histories, repeated stages,
changed whole-controller boundaries, or a new recursive job family.

There is a constructive boundary example. With **two shared central axes**,
two different owner paths have the same complete operator. Actual source
coefficients +1/4 and -1/4 then cancel at every tensor width. Section 7 gives
all maps and checks their phases. This supplies a concrete cancellation
mechanism outside the theorem. It is only a two-path construction, not a
complete 112-owner provider or a favorable recursive invoice.

## Reproduce

Use Python 3.12 and its standard library, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/fresh-stage-code-separation
```

The standalone, read-only checks are:

```sh
python3 -I -B research/fresh-stage-code-separation/verify.py
python3 -I -O -B research/fresh-stage-code-separation/verify.py
```

Expected final marker:

```text
PASS_ALL_LENGTH_FRESH_STAGE_SEPARATION_NO_NEW_KAPPA
```

A direct normal replay took 7.91 seconds on the author's CPython 3.12.13
macOS host. This is a local measurement, not a portable performance bound.
The checks include 57,344 signed normalizer entries, 12,544 code-polynomial
entries, all 12,656 two/three-stage paths, 12,654 explicit killing markers,
and forward/reverse dynamic programs for the short certificates. The larger
path controls reach 64 stages. Exact repeated-stage cancellation and a
two-shared-axis collision check the excluded premises.

The marker proposer is separate from the verifier. To reproduce its bounded
search, use a new output file:

```sh
python3 -B research/fresh-stage-code-separation/select_markers.py --output /tmp/fresh-markers.json
```

The verifier imports no source evaluator or proposer. Its two path evaluators
use composed signed maps and literal lookup tables. Its two dynamic programs
run in opposite directions with different local calculations. They share the
source data and elementary matrix code; this is not independent human or
proof-kernel review. No complete supplier, compiler, outer, selected cold,
Lean or Docker replay is claimed.

## Open next questions

1. Complete a two-shared-axis native provider that uses the displayed
   cancellation. Start with one two-stage pair, complete every owner map and
   every original-input output, then price the extra central axis and lost
   targets. The current two-path witness supplies neither that provider nor
   a favorable cost allowance. A full optimistic bill must pass before a
   larger search is justified.
2. Bind one original negative bank to an available paid IDLE or to a charged
   scalar program whose length depends on f. Check every input, return,
   precision and movement charge. The ADD lower bound alone cannot compare
   that complete cost with the center saving. Existing paid-history and
   coupled-helper caller claims remain separate.

## Source, credit and status

The base is canonical main `1ec1119972c9aefe42525172d07b332fcff81cb4`,
priority revision 7. [SOURCES.json](SOURCES.json) binds all copied bytes and
retains source notices and license. The
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19156145)
records the scope and overlap. [RESEARCH-NOTES.md](RESEARCH-NOTES.md) records
the route decision and the failed preliminary screen.

Dillon's [PR #4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933)
supplies the physical normalizers, one-stage support argument and complete
coded caller. Cinna Davis's
[PR #5065](https://github.com/CrocSwap/integer-mult-bounds/pull/5065) supplies
the two-stage marker proof and the longer-product question. Dugongue's
[PR #4929](https://github.com/CrocSwap/integer-mult-bounds/pull/4929) supplies
the center-free code. Cao Yifan / intqwq, Cinna Davis / 1337isnot1337, zxv,
Jacob Alan Sussman, Ryanson Jonathan and the native/controller lineage retain
their source credit. The inherited code, its spectrum and the one-stage
four-point expansion are not new results here.

The new contribution is ordered fresh-stage path separation, the all-length
support bound, short exact certificates for the other caller banks, and the
explicit two-center path cancellation. These are author-checked mathematical
results, without a literature-priority claim. Prepared by Ali Romman with
substantial OpenAI Codex assistance; Apache-2.0. No selected frontier change,
merge, or change to another contributor's work is requested.
