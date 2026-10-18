# Exact E8 A2 three-port gather overlap: a narrow structural-decoder result

**Status:** exact finite, reproducible combinatorial result; **no new κ**; no scheduled circuit or paid supplier. Assignment seed **44**, structural-decoder track (40–49). Research completed **2026-10-13**.

## Statement and significance

Take the 240 norm-two E8 roots, quotient by antipodal sign to obtain 120 root lines, and connect two distinct lines when the absolute scalar product of representatives is one. For each root line `v`, define its **closed gather set** `G(v) = {v} ∪ {w: |v·w| = 1}`. Each `G(v)` consists of exactly 57 lines.

Among **all 280,840 unordered triples** of *distinct* root lines, the minimum union `|G(a) ∪ G(b) ∪ G(c)|` is **84**, reached for **exactly 1,120** triples: those contained in a two-dimensional A2 root subsystem. Every other triple has union size **100, 105, or 107**. The result is independent of the signs chosen for root representatives.

For three separate 57-line gather lists (171 requested occurrences), the A2 triples admit an **optimistic** deduplication count of `171−84 = 87` occurrences, versus `171−100 = 71` for an ordinary triangle. This **16-occurrence structural difference** points toward a *three-port A2 source-read grouping* experiment. However, the ability to combine lists in a set does **not** imply one can realize them with a common admissible register/frame, at zero copy cost, or with a better recursive moment. A paid construction would additionally require frame adapters, rank/copy charges, source-read timing, restorations, copies, helper stock, owner allocation, and complete recursion and assembly budgets. None is supplied here.

### Complete triple census

| Root-line edges among ports | Rank of their 3×3 Gram matrix | Triples | Common **open** neighbors | Common **closed** gather lines | Union of the three closed gathers |
| --- | --- | ---: | ---: | ---: | ---: |
| 0 | 3 | 37,800 | 8 | 8 | 107 |
| 1 | 3 | 120,960 | 12 | 12 | 105 |
| 2 | 3 | 90,720 | 12 | 13 | 100 |
| 3: A2 | 2 | 1,120 | 0 | 3 | **84** |
| 3: non-A2 | 3 | 30,240 | 16 | 19 | 100 |

The source-level incidence model is the standard E8 root-line motif referenced by DreamingOfClouds' [#446](https://github.com/CrocSwap/integer-mult-bounds/pull/446), where the P120 gathered-source context has 57 entries. This result is an independent *three-port* census and a narrowly scoped batching bound, **not** a replacement for #446's physical-copy rank theorem. #620's decoder cost floors, #703's ten Hurwitz-line copy floor, and #697's direct-source E8 implementation concern different questions. No claim that this is the first mathematical observation of A2 triangles in E8 is made.

## Reproduce

Python 3.9+ standard library; no solver, network, external repository inputs, or other dependencies:

```bash
python3 -B research/e8-a2-triple-gathers/verify.py
python3 -B research/e8-a2-triple-gathers/crosscheck.py
```

Expected output begins:

```text
PASS_E8_A2_TRIPLE_GATHERS: roots=240 lines=120 triples=280840 A2=1120 min_union=84 negative_controls=7
```

The primary checker checks the frozen `RESULT.json` byte-for-byte, prints its SHA-256, verifies seven intentional corruptions are rejected, and compares every triple's bit-set union with inclusion/exclusion calculated from the three pair intersections and the triple intersection. It constructs E8 roots explicitly as doubled integer coordinates and computes Gram determinants from dot products. The **second, independent** `crosscheck.py` builds the roots separately, identifies all A2 triples using vector sums rather than determinants, and rechecks every common-neighbor count and union using ordinary Python sets rather than bit masks. Run both without Python `-O`, which would disable assertions; the commands reject optimized execution.

## Mathematical justification and scope

`PROOF.md` gives the explicit edge-count argument for exactly 1,120 A2 triangles, the exact finite counts and the inclusion/exclusion verification. The reported census is a proof by exhaustive, deterministic rational/integer case enumeration for this **fixed** 120-line graph, with a short separate argument for the A2 minimum value and count. There is no claim for different root systems, compressed or mutable frames, actual sources in a changed supplier, or any uniform asymptotic algorithm.

## Reproduction pins, provenance, overlap

- Public repository source baseline: [`66849e1475c930fd7732b1a0067ffee7e1e95f60`](https://github.com/CrocSwap/integer-mult-bounds/commit/66849e1475c930fd7732b1a0067ffee7e1e95f60) (the base recorded by contemporaneous PR #703; **not** a claim that a network clone or current `main` ref was independently verified in this execution).
- Reviewed selected `certificates/selected-result.json` and `docs/research/current-status.md`; accepted conditional `κ = 51110230636731/31250000000000000`, dependent on #626/#622/#623/#543; not changed by this work.
- Existing community foundations: OpenAI's *Integer multiplication below n log n*, Jacob Sussman's E8/five-stage construction lineage, DreamingOfClouds' #446/#595, Joel Pulikkan/GamingPuzzled's #620, Douglas Colkitt's #703, and related #697/#698. This package copies no predecessor files.
- No pinned open coordination issue was visible publicly at review time. A local claim is in `CLAIM.md`. There was no authenticated GitHub write access and no PR/issue/comment was posted; `upstream/` and the selected frontier were left untouched.
- Attribution: prepared by **OpenAI GPT-6 with substantial AI assistance**, at the requesting user's direction; human author identity is not supplied. For inclusion, the user should set the appropriate author attribution. Intended license: repository's Apache-2.0; no other code redistributed.

## What remains open

Before promoting this to a construction, identify a physical mapping of 3 A2 gather lists onto common frames, charge the one-time shared loads plus fanout and schedule/cleanup (including borrowed-ancilla restoration), then compare the complete paid supplier moment against the *currently binding* selected provider and the assembly inequalities. A saving of 16 **source-list occurrences** alone is not a saving of 16 paid operations or recursive children.
