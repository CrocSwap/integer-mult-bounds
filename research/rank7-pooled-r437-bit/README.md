# Pooled R437 slack across bit replicas on PR3958: conditional κ = 0.001736738651088946052684 − 10⁻⁴⁶ − 10⁻⁷⁰ (+0.00533%)

**Author-checked conditional candidate; not maintainer-reviewed.** The selected record on
`main` is still #1094. This package stacks on the open PR3958. PR3958 composes PR3955's complex side
with PR3647's R437 bit supplier and is bit-bound at R437's endpoint. This package applies PR3939's
cross-replica owner map to R437.

| | complex root lower | bit endpoint | binds | κ headline |
|---|---|---|---|---|
| PR3958 | 0.0017411725885452521674224 | R437 0.001736646042038446578551 | bit | 0.001736646042038446578551 − … |
| **this** | 0.0017411725885452521674224 | **pooled R437 0.001736738651088946052684** | **bit** | **0.001736738651088946052684 − …** |

The gain is **+0.00533% over PR3958**. About 4.4e-6 of complex headroom remains.

## Idea

PR3647 (ai-nanachi) hosts all 125,856 R437 helper residuals in PR1023-model slots. Per replica:

- **Window 6** (capacity 42, pair 0, stages 3–8) keeps 209 five-residual families, one two-residual
  family (idle 26) and 12 empty families.
- **Window 8** (capacity 14, pair 2, stages 7–8) keeps one residual per copy (idle 6).

Pooled over 32 replicas, the window-6 slack is `32·63 = 2016 = 403·5 + 1` places. Residue `t = 1`
in mightyOil's `bit-partial-width7-optimum` table then gives the pooled32 slot optimum: 403 empty
42-families plus one empty capacity-14 copy.

This package builds that optimum explicitly with 63 moves:

- the 62 residuals in the two-residual families of replicas 1–31;
- replica 0's window-8 residual (stage 8, helper 215), which lies inside window 6's stages.

They fill replica 0's two-residual family (offsets 16, 24, 32) and its 12 empty window-6 families,
five residuals each. The idle bill changes by `{2:+13, 6:−1, 14:+1, 26:−32, 42:+19}`. Rank mass
1,808,352 and maxchild 42 are unchanged.

## Verification

```sh
python3 -B research/rank7-pooled-r437-bit/build.py    # writes POOL-MOVES.json, CLAIM.json (~7 s)
python3 -B research/rank7-pooled-r437-bit/verify.py   # independent of build.py (~10 s)
```

**Inputs.** `R437-GLOBAL-TEMPLATE.json.gz` is PR3647's `generated/GLOBAL-TEMPLATE.json.gz` at head
`a24f9ff9`. Its decompressed SHA-256 equals `template_content_sha256` in PR3647's `EXPECTED.json`,
which PR3958 vendors. Its `hosting.slots` and `hosting.windows` are R437's per-replica placement
and slot windows.

**Role audit.** `verify.py` rebuilds all 125,856 hosted roles (32 replicas × 9 stages × 437 helpers)
and applies the moves. It checks every role against the slot rules:

- the host child's window contains the stage;
- the host pair is inactive at that stage;
- the width is 8 and fits the capacity;
- cells are disjoint and prefixes are compact;
- every (stage, replica, helper) is hosted exactly once.

**Baseline.** The rebuilt baseline equals PR3647's `EXPECTED` profile, and its endpoint is accepted
at c and rejected at c + 10⁻²⁴.

**Pooled endpoint.** The pooled endpoint is accepted at 0.001736738651088946052684 and rejected at
the next 10⁻²⁴ point, with the 10⁻¹⁶·32m² fallback envelope.

**Composition.** PR3955's complex root bracket is rechecked, and
`κ = min(floor₂₄(complex), bit) − 10⁻⁴⁶ − 10⁻⁷⁰`, with the bit side binding.

**Controls.** Six mutation controls are rejected:

- a move outside its window;
- a cell collision;
- a wrong source;
- a dropped move;
- the next grid point of the pooled endpoint;
- κ off the grid.

## Scope

**Hypothesis (as in PR3939):** the bit supplier may use a cross-replica owner map. The slot rules
are audited, but PR3647's native hosted emission was not run with these owners.

The result also inherits:

- PR3647's R437 interfaces, with its admission pending;
- PR3955's complex-side hypotheses: hosted frame selection, hosted receivers and hosted donors;
- every obligation of both stacks.

## Open next questions

- **Does PR3647's native hosted emission accept this cross-replica owner map?** First step: run
  PR3647's matching/emitter with these 63 owners. Blocked by: cross-replica owner support in the bit
  emitter.
- **Can the bit side rise further below the complex root 0.0017411726?** First step: price width-7
  conversions or further R437 helper deletions under the pooled slot model.

## Credit

- ai-nanachi (PR3647): R437.
- Ali Romman (PR1043): helper470.
- Sagar Thakrar (PR3700, PR2423 and PR1023): OQ4 coalescing and the slot model.
- mightyOil (PR1281): the pooled32 optimum.
- The PR3955 stack, including OpenCode (Space bunny free) for ideas in the stacked complex-side
  predecessors.

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
