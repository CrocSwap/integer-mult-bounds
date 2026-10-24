# Independent recount of #4545's transport census for PR4470

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

Clear1nsight's #4545 (head `6034837d`) derives PR4470's required changed transports from its chronological words. It reports that each orientation has **3,302** persistent transport occurrences over **2,856** distinct pairs, and that **406** transport pairs are new. With 17 helper boundaries, these match 423 physical recipes, and all 408 helper owners are represented.

This package recounts the transport census with its own frame tracking. Main's pinned #4470 constructor, run isolated on its 7 SHA256-pinned inputs, emits both the patched #4470 word and the pre-patch PR4447 word. Each persistent field keeps its current frame. A scalar contact or a warp entrance at a different frame, and the final exit, each need one transport `E → F`.

## Results

All recounted figures are confirmed.

| | #4470 forward | #4470 backward | PR4447 word |
|---|---:|---:|---:|
| transport occurrences | **3,302** | **3,302** | 3,355 |
| distinct `(E, F)` pairs | **2,856** | **2,856** | 2,934 |

- **New pairs.** There are **406** distinct transport pairs new relative to PR4447. They are compared by exact ordered frame bases, not frame indices, which differ between the two certificates. The same 406 arise in both orientations.
- **Helper owners.** There are 408 helper owners among 632 persistent fields.

## Verify

```text
python3 -B research/pr4545-transport-census-check/verify.py
```

This runs in about 2 s with the standard library only.

## Limitations

- **Not recounted.** #4545's 17 helper-boundary recipes and its matching against the 423 physical recipes depend on its adapter and recipe definitions. The physical recipes are not re-lowered here; the maintainers' #4470 review already lowers all final transports.
- **Counting only.** This checks the census, not phase-correct frame replacement.

## Open next questions

- None new.

Credit: Clear1nsight (#4545), Cinna Davis (#4470), and the PR4447/#4441 retiming lineage. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
