# QQ16 needs more than twelve coordinates of retained linear information

The fixed QQ16 `F0/B_1_2` controller still loses original selected inputs
when given the **full initial `R2 X` query** for free. Its known erased
family contains at least `ceil(88|G|/7)` dimensions of original A/T data.
A read-only rational-linear transcript of rank d leaves at least
`max(0,ceil(88|G|/7)-d)` of them invisible.

For a record with one scalar in each of q coordinates per regular-cover
owner, every q<=12 fails. Thirteen is only a necessary width in this
model. Information dimension is not recursive-child rank or native
cost. No supplier or kappa change is claimed.

## What this adds

The claim is in [discussion #2074](https://github.com/CrocSwap/integer-mult-bounds/discussions/2074#discussioncomment-18933989),
taking its full-initial-`R2 X` handoff. [The proof](PROOF.md) combines
the joint A/T defect of Ali Romman's QQ16 witness with Ross Richardson's
three-query rank calculation in
[PR #2104](https://github.com/CrocSwap/integer-mult-bounds/pull/2104).
It permits arbitrary rational linear records of all original coordinates,
including selected inputs and mixing across cover owners.

[PR #2079](https://github.com/CrocSwap/integer-mult-bounds/pull/2079)
tests `B2 X_U`; #2104 quantifies its remaining A loss.
[PR #2122](https://github.com/CrocSwap/integer-mult-bounds/pull/2122)
excludes the scalar-mixer family `B0+M B2`. This result concerns total
record dimension and the different full-source query. Those predecessors
retain credit for their calculations; the three-query trace bound is
not claimed as a new or independently invented result.

## Exact scope

Keep the first pair and ordinary schedule. Observe selected endpoints
after B1, completed-X descendants at the retained output endpoint and
all five forward-query histories. Saving F0's transient A endpoint
would count as extra information. Records are side-effect-free;
common dirty affine baselines are allowed. Nonlinear record encoders
and changes to the first pair are excluded.

Capacity counts actual rank on the erased family. Independent payload
modes must be counted even when they share a named field. The full
`R2 X` query preserves the payload-constant subspace and has capacity
at most `8|G|` there.

This is an author-checked scoped proof with exact finite source checks.
It has not received independent review or formal-kernel verification.
Native access, full word replay, hosting, recursive precision and the
complete supplier invoice are not checked. No compact witness for the
actual regular cover is emitted; its existence follows from the rank
argument. The small explicit witness is a rational control fixture.

## Reproduce

From the repository root, Python 3.12 and its standard library:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-transcript-capacity
python3 -I -O -B research/qq16-transcript-capacity/verify.py
```

Expected verifier line:

```text
PASS_QQ16_TRANSCRIPT_CAPACITY defect>=88|G|/7 q<=12_excluded full_R2_X_insufficient
```

The registered replay checks [RESULT.json](RESULT.json), source pins,
actual owner-route distinctness, Gram facts, the retained tail, exact
noncommuting-chart fixtures and semantic failure controls. It reads
main's frozen QQ16 packet and imports no predecessor verifier. No
network or pending PR checkout is needed. [SOURCES.json](SOURCES.json)
records exact blobs and byte hashes; [TASK.json](TASK.json) records
scope and remaining questions. The selected record and catalogue are
historical provenance, not live mathematical inputs.

## Open next questions

1. **Can two query records recover the complete controller?**
   `(B0 X_U,B2 X_U)` recovers the selected defect on this erased family.
   First characterize the complete observation kernel on all inputs,
   then test that pair on it. This family is only a subspace; its
   recovery is insufficient for a controller or favorable physical bill.
2. **What is the exact required record dimension?** The gap between
   necessary width thirteen and the sixteen-coordinate description of
   the family remains. First sharpen the exact rank of `[B0;B1;B2]`
   using its actual route algebra. The trace inequality is a lower
   bound; the regular cover is too large for naive matrix expansion.
   A sharper rank still would not price a legal implementation.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Ali Romman and the contributors in
[joint-query/NOTICE.md](../joint-query/NOTICE.md) supplied the maps,
ordered sections, bridge semantics and original witness (PR #1969,
`a6e6ad3936f67b8f63b5b68c5e75d540610a65e7`). Ross Richardson supplied the trace
bound and full-R2 handoff (PR #2104,
`4bdc574da394a39f955e8cf4637075649c43a632`). Cinna Davis supplied the
extra-B2 and mixed-helper investigations (PR #2079,
`49df8190b158e3028e702b2c6b798117006f7249`; PR #2122,
`7045301a8c15eb4408e3e9d80969c9d50a914cde`). Adam Gall's PR #2086 and
#2093 are adjacent logger and explicit nonzero-chart obstructions.
The retained lineage, including Rohan Arun and Jeremy Kothe, keeps its
existing notices. New work is Apache-2.0.
