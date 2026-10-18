# JP8 compensation with a restored target basis

**Finite complex-supplier circuit improvement; no new kappa.** The selected
#626/#622 JP8 supplier's initial dirty-input compensation can be factored through
56 disjoint target pairs. This saves **4,204 scalar additions and 48,400
real-component scalar primitives per local invocation**, including all target
preparation, restoration, source reads and coefficient-work clearing.

| Emitted local quantity | Original | Replacement |
| --- | ---: | ---: |
| Compensation additions | 8,800 | 4,596 |
| Compensation real primitives | 100,272 | 51,872 |
| Whole-program scalar macros, either orientation | 22,693 | 18,489 |
| Forward scalar real primitives | 257,232 | 208,832 |
| Backward scalar real primitives | 257,280 | 208,880 |
| Helpers | 492 | 492 |

The existing paid child histogram, frames, center events and ordered wrappers
are unchanged. The backward positive-prefix bound increases slightly; its
101-bit upper bound remains within the 192-bit local allowance. See
[the proof and complete cost accounting](PROOF.md). This is neither a stronger
asymptotic bound nor a measured runtime improvement.

## Reproduce

From the repository root, Python 3.11+ and its standard library are sufficient.
The command is offline, writes only to a temporary directory, and compares every
field of the freshly computed certificate with [EXPECTED.json](EXPECTED.json):

```sh
python3 -I -B research/complex-compensation-basis/verify.py
```

Expected final line:

```text
PASS_COMPLEX_COMPENSATION_BASIS pairs=56 compensation=8800->4596 saved_real_primitives=48400 columns=716 controls=10+25 kappa=unchanged
```

The checker does not import the search implementation. It verifies the complete
boundary on arbitrary dirty inputs in both orientations; independently replays
both complete original and changed scalar programs using integer matrices; and
runs the unmodified pinned emitter and native frame/wrapper auditor on the new
word. Native emission must agree exactly with independently splicing the new
boundary into the pinned original event streams. The native auditor rejects
all 25 inherited mutations. Ten additional controls include omitted preparation
that passes helper-only testing, omitted restoration, underpriced basis changes,
wrong frame, and reading a cold-ended helper before its wrapper.

Focused primitive and failure-mode tests, and the optional full bounded search:

```sh
python3 -I -B research/complex-compensation-basis/test_verify.py
python3 -I -B research/complex-compensation-basis/search.py
```

The search prints `PASS_SEED24_SEARCH scored=124320 positive=3095 pairs=56
saved=48400`. Six focused tests must pass. The verifier and tests also work with
`-O`: their own checks are explicit exceptions, and native subprocesses always
run with assertions enabled under `-I`. Neither command modifies a committed
artifact. `--output NEW_PATH` explicitly generates a fresh certificate or search
nomination and refuses to overwrite an existing file; it is not the strict
certificate-comparison mode above.

## Domain, provenance and attribution

- Exact repository base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Accepted result at that base: conditional kappa **0.001635527380375392**,
  #626 with #543, as identified by the selected certificate and maintainer
  review. Pending larger PR titles are not treated as accepted results.
- PR622 construction source: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
- Selected PR626 head: `660de893d27bb7abd1d5b01b1640207528a5c851`.
- [SOURCES.json](SOURCES.json) pins every consumed source, including the
  canonical word and both programs by full decompressed payload. Their hashes
  are checked against #626's actual SPEC. Recompression is permitted; changing
  any payload byte is rejected.
- Assignment seed **24**, drawn from OS randomness, selects the complex track
  and JP8. All **112 * 111 * 10 = 124,320** oriented target/coefficient choices
  were scored at q in `{±1/4, ±1/2, ±1, ±2, ±4}`. Exactly 3,095 improve the
  fully paid scalar count. One seeded shuffle followed by descending-gain
  greedy disjoint selection fixes 56 pairs. The search stops there; it makes
  no optimality claim and explores no other supplier, frame or matching class.
  The frozen recipe, rather than search success, is sufficient for verification.
- [CLAIM.md](CLAIM.md) records the three candidate tasks, overlap checks and
  narrow local claim; no pinned sprint coordination issue existed.

Jeremy Kothe's #622 K-triangle construction and Chafik Boukhalfa's #626 selected
package supply the unchanged native input. DreamingOfClouds supplies the retained
cold-helper, emitter and verification work; icekylinx the factory, direct-delivery
and scalar architecture; Dominik Scholz the prefix lineage; Dugongue the local
modules; eumemic the bit supplier. Their full notices and earlier contributors
remain in [the selected package's NOTICE](../complex-k492-owner-repair/NOTICE.md)
and [maintainer review](../../docs/research/community-k492-review.md).

Concurrent [#713](https://github.com/CrocSwap/integer-mult-bounds/pull/713)
(Scott Woolsey Biggart) and
[#716](https://github.com/CrocSwap/integer-mult-bounds/pull/716)
(Sagar Thakrar) are explicitly credited for applying a restored target basis
to the R420 **binary** compensation; #716 also credits Dugongue's #476 and
earlier #450 target mixing. This contribution transfers that mechanism to the
selected **rational complex** circuit, with coefficient-dependent prices and
cold-wrapper obligations. It does not claim invention of basis conjugation.
No code, recipe or certificate from those pending PRs is imported.

Related [#696](https://github.com/CrocSwap/integer-mult-bounds/pull/696) lowers
unchanged complex macros; [#681](https://github.com/CrocSwap/integer-mult-bounds/pull/681)
resynthesizes the raw factory; #411 changes chronological complex target
prefixes and frames. Their results are credited but not composed here.
The historical projection-cut toolkit's failed cold-helper full-lifetime gauge
search does not cover a target-only basis restored at the initial boundary.
No previously closed search is reopened by increasing its computational budget.

The pre-submission refresh covered 562 open PRs through #743. Newly arrived
[#722](https://github.com/CrocSwap/integer-mult-bounds/pull/722) and
[#739](https://github.com/CrocSwap/integer-mult-bounds/pull/739) share coefficient
work in JP8 cleanup; #723/#734 recode individual coefficients. Their bodies and
file inventories were inspected: this compensation-macro replacement is distinct,
and no additive saving is asserted. [OVERLAP.json](OVERLAP.json) records exact
heads, including #716's later binary optimal-matching update.

Prepared by **Sricharan Vagvala (@theon199)** with substantial **OpenAI Codex
assistance** in research, implementation, verification and writing. Parent-only
execution; no independent human review is claimed. New material is Apache-2.0,
and all inherited licenses, notices and assistance disclosures are retained.

## Integration limits

Only this standalone research directory is added. The selected frontier and
`upstream/` are unchanged. A production integration still needs a typed
alternative-compensation construction step, fresh artifact bindings and full
hosting/invoice/outer admission. No global invoice, new assembly, full repository
suite pass, Linux execution or Lean proof is inferred from this local replay.
The inherited uniform compiler, common-label/mutable-basis, physical/hosting,
precision/tape/exact-recovery and analytic assumptions remain. See
[VALIDATION.md](VALIDATION.md) for what was actually run.
