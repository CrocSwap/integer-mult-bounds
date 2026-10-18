# Whole-helper packing cap for PR2339 on the T74 bin stock

**Scoped negative result; no new κ.** For either pinned 400-helper word of
[PR2339](https://github.com/CrocSwap/integer-mult-bounds/pull/2339), or any mixture
of them across the 666 T74 calls, the primitive exponent satisfies
**b < 0.0016870** if helpers remain unsplit and the PR2269 bin inventory is
unchanged. This is below PR2269's attained primitive endpoint and the conditional
κ = 0.001697065994108880 claimed in
[PR2349](https://github.com/CrocSwap/integer-mult-bounds/pull/2349)
(head `bb2486ec93c099afe9acd93442f13864b566296a`, observed 2026-10-15 UTC).
These open-PR claims are not the maintainer-selected frontier.

The cap permits **arbitrary fractional combinations of legal integer bin
patterns**, with no chronology, owner-family or physical-port coupling
restrictions. It therefore excludes every integral owner assignment in this
fixed model, including a different call order with the same bin inventory.
The certificate does not need an optimal LP solution or an attainable packing.

PR2339 correctly labels its favorable rank-48 cap (about 0.001747958372) and
calibrated prices as bounds/models, not a κ claim. That cap forgets whole helper
widths and actual bin counts. This package supplies a tighter cost check for
its unchanged T74 parent. It does not refute PR2339's local circuit or its
more permissive cap.

## Literal cost interface

`verify.py` independently recounts the frame invoice using explicit subsets of
GF(2)^9. It checks monotone climbs, private cut-copy descents, invertible handoff
maps and terminal climbs. Its implementation follows the accounting rule of
PR2322's `paid_profile`, using a different subspace representation. It does not
prove the scalar payload, cleanup semantics or phases.

The resulting profiles and widths are:

| Input | Rank/count inventory | Rank mass per call |
|---|---|---:|
| extra local calls | 1:2287, 2:535, 3:386, 4:125, 5:37, 8:8 | 5264 |
| base local calls | 1:2303, 2:527, 3:386, 4:125, 5:37, 8:8 | 5264 |
| helpers, either word | 4:4, 5:4, 7:36, 8:84, 9:272 | 3408 |

For 0 < b < 1, let p = 1-b and c_r = (r/73)^p, with c_0 = 0.
The base word costs 16c_1 - 8c_2 = 8c_1(2-2^p) > 0 more than extra.
Using extra for all 666 calls is thus a favorable lower envelope for any mixture.
Both words have exactly the same helper widths and mass.

The pinned PR2269 plan contains 74 replicas, 18 windows per replica and 112
ports per window. Recounting the window ranks gives:

| Bin capacity R | Number B_R |
|---|---:|
| 8 | 49728 |
| 16 | 33152 |
| 32 | 33152 |
| 48 | 33152 |

There are 3,580,416 bin rank units. The 666 copies of the helper inventory
consume 2,269,728, leaving 1,310,688 idle units. Adding the local rank mass gives
4,816,512 = 73 × 66,304 - 23,680. W = 66,304 is the parent live dimension.
Window contents are pinned and checked for basic structural consistency;
rederiving the parent from its scalar schedule is outside this scoped proof.

## Exact dual proof

Fix b = 1687/1000000. For 0 ≤ r ≤ 48 define

    f_b(r) = (73 c_r - r)/b,
    f_b(0) = 0.

For capacity R, an integer pattern is a nonnegative vector n indexed by
s ∈ {4,5,7,8,9}, with Σ_s s n_s ≤ R. Its idle remainder is
r = R - Σ_s s n_s. The verifier enumerates all **1,163** patterns, including
empty bins, and checks the rational coefficients y_s, z_R in `DUAL.json` satisfy

    z_R + Σ_s n_s y_s ≤ f_b(r).

Every comparison uses a directed rational **lower** enclosure of f_b(r).
Multiplying these inequalities by any nonnegative fractional pattern counts
and summing gives

    Σ_idle f_b(r) ≥ D = Σ_s (666 N_s)y_s + Σ_R B_R z_R,

provided the helper and bin count equalities hold. This is weak duality; neither
numerical optimizer correctness nor optimality is an assumption. Fractional
pattern counts relax integrality of the number of bins of each type, while
helpers remain whole within each pattern.

Consequently the native recurrence moment obeys

    M(b) ≥ [666 Σ_r local_count_r c_r
             + (1,310,688 + bD)/73] / 66,304.

The exact lower endpoint is stored in `EXPECTED.json`. It exceeds 1 by
approximately **6.41624964026 × 10^-8**. Every positive child has rank below 73,
so each term (r/73)^(1-b) increases with b. Thus M(b) > 1 for every
b ≥ 0.0016870 in the recurrence's range: the admissible endpoint is strictly
below the stated cap. Additional costs cannot repair this failure.

The directed engine is the unchanged `fine_moment.py` from PR2322. This verifier
sets its grid to 2^-256, with 100 logarithm terms and 96 exponential terms.
The finite series retain their explicit outward tail bounds. These constants
are ample for this coarse separation; no decimal arithmetic is used in the
proof. Floats appear only in the printed diagnostic margin.

As a non-vacuous positive control, the pinned *attained* PR2269 global profile
has an exact upper moment below 1 at the same b. Eight mutations reject an
undercharged local invoice, a missing width-9 helper, a nonmonotone gate, a bad
warp image, duplicate calls, altered bin stock, an overstated dual and an
unsupported stronger cap. Checks remain active under `python -O`.

## Reproduce

No network, optimizer or third-party Python package is required:

```sh
python3 -I -O -B research/t74-low-alias-width-cap/verify.py
python3 -I -B research/t74-low-alias-width-cap/check_export.py
```

Expected: `PASS_T74_LOW_ALIAS_WIDTH_CAP 1687/1000000 patterns 1163 ... rejecting_controls 8`
and `PASS_T74_WIDTH_CAP_EXPORT controls 8`.

The package also registers its commands for the repository replay hook:

```sh
python3 scripts/research_package.py --package research/t74-low-alias-width-cap --check-only
python3.12 scripts/research_package.py --package research/t74-low-alias-width-cap
```

`--record NEW_PATH` regenerates the exact receipt and refuses overwrite. Normal
verification compares every field to `EXPECTED.json` and writes nothing.
`check_export.py` verifies a standalone, read-only source copy outside Git, and
rejects a changed input, a changed expected result and receipt overwrite. The
registered metadata check needs Git history for `SOURCES.json` provenance;
the mathematical verifier and export check do not.

`INPUTS.json` pins every bundled predecessor input by commit, upstream path
and SHA-256. The PR2269 plan is stored as deterministic gzip to reduce size;
its original uncompressed digest is checked too. Package-local `.gitattributes`
preserves CRLF bytes in the two immutable text inputs. `SOURCES.json` records the
historical selected record and task catalogue, not a claim of selection.
SciPy 1.18.1 / HiGHS was used to nominate nine dual coefficients during search.
The submitted certificate independently validates the nominated rationals.

## Scope and limits

This result fixes the two literal PR2339 words, their full helper lifetimes,
666 calls, m = 73, W = 66,304 and the tabulated bin stock. Splitting helpers,
changing their initial/final contract, changing local kernels, mixing other
providers or changing the parent capacity inventory is outside the claim.
No full multiplication theorem, new κ, native supplier admission or global
stock/precision contract is established here. The cap concerns the primitive
recurrence b; applying it to an outer κ requires that outer construction's
inherited b-to-κ relationship.

The arithmetic loader executes the exact source bytes checked against
`INPUTS.json`, without consulting Python bytecode caches. `-B` alone suppresses
cache writes but still permits cache reads. Four export controls install
conflicting timestamp or unchecked-hash caches and replay in both normal and
optimized mode; every run must retain the original receipt and leave the export
unchanged. This repairs the same source/cache distinction identified in the
related [PR2766](https://github.com/CrocSwap/integer-mult-bounds/pull/2766).
[PR2553](https://github.com/CrocSwap/integer-mult-bounds/pull/2553) isolates the
registered runner's cache namespace; this fix also covers direct verifier calls.
The arithmetic source, inputs, dual and expected mathematical receipt are unchanged.

## Open next questions

1. **Can an anticipatory alias keep its lender narrow?** The 32 low aliases
   reduce helper count, but increase the number of width-9 lifetimes. Seek a
   local factorization with the same compensation identity and a smaller exit
   width. First derive a candidate's invoice and apply this pattern bound before
   attempting a full native build. The unresolved part is a realizable changed
   local contract.
2. **Can a different parent stock fit the wide helpers cheaply?** Search legal
   stage/controller changes that redistribute capacities while charging their
   changed coverage and local costs. Recompute the pattern certificate for each
   stock before scheduling. A hypothetical inventory alone is not a parent
   construction.
3. **Which partial low-alias subsets can clear the packing gate?** Optimize
   subset choice together with width-pattern costs, rather than helper count.
   This certificate does not exclude partial subsets. First enumerate exact
   per-alias profile/width changes and solve a relaxation, then verify promising
   combined words and their physical owners. Interactions between aliases and
   overlapping lender lifetimes remain the main constraint.

Structured scope, stopping criteria and these questions are in `TASK.json`.

## Attribution

Jeremy Diviney, with substantial OpenAI Codex assistance: independent cost
recount, scoped dual bound, exact certificate and controls. The inputs and
method lineage remain credited to their authors:

- Sagar Thakrar / `thakrarsagar`, PR2339: the two 400-helper words and their
  favorable model prices, with Claude Code assistance.
- Cinna Davis / `1337isnot1337`, PR2226: anticipatory dirty borrowing and the
  low-alias compensation mechanism, with OpenAI Codex assistance.
- Jeremy Kothe / `jeremykothe2`, PR2269: the T74 parent plan and attained profile,
  following the supplier lineage documented there; PR2312 and PR2349 are later
  improvements, not inputs to this proof.
- Vlado Vojdanovski, PR2322: the literal frame-invoice accounting
  implementation used as a reference and the bundled directed moment engine.
  Its numerical-engine lineage includes Douglas Colkitt's exact moment checks
  and the subsequent base-two/fixed-grid contributors credited by PR2322.

Ali Romman's [PR1129](https://github.com/CrocSwap/integer-mult-bounds/pull/1129)
and the incorporated [R480 pattern-dual audit](../selected-t16-pattern-dual/README.md)
previously apply this same 1,163-pattern relaxation to a different fixed helper
inventory. The present result applies the established method to PR2339's changed
widths; neither the relaxation nor weak duality is claimed as new.

The concurrent [PR2359](https://github.com/CrocSwap/integer-mult-bounds/pull/2359)
independently audits PR2322's four-role raw ledger using explicit span sets.
It studies different words and does not address the PR2339 packing cap here.

New contributions are Apache-2.0. See `NOTICE.md` for bundled source provenance.
