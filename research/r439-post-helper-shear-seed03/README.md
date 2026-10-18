# One restored helper shear after PR967 mixing

This finite construction removes **14 complete local ADDs** from the pinned PR967 bit word: **11,783 -> 11,769**. It inserts one helper ADD before the middle target updates and the same ADD afterward, with the corresponding middle-column correction. All 661 source, target and helper inputs may start dirty. The complete paid profile and exact forward/reverse bounds are unchanged. No new kappa is claimed.

| Quantity | PR967 parent | Candidate |
|---|---:|---:|
| Complete ADDs | 11,783 | 11,769 |
| D ADDs | 5,563 | 5,549 |
| Middle target ADDs | 4,509 | 4,493 |
| Forward positive bound F | 72,847 | 72,847 |
| Reverse positive bound B | 10,394,084 | 10,394,084 |
| Paid rank mass | 5,129 | 5,129 |

The changed D bill is **221 + 306 + 1 + 4,493 + 1 + 306 + 221 = 5,549**. The other 6,220 ADDs are retained. The new helper gate is local **242 <- 19**, or physical **x464 ^= x241**, at frame zero. The target basis is frozen. This connects the old singleton {242} to the old component {12,19,30}; its undirected edges become the path 30--12--19--242. Helper 19 is now used by two accumulators, outside the parent's disjoint stars with at most two leaves.

## Exact finite identity

Let h be the 439-vector of helper values after the parent's helper and target preparation, and M its 111-by-439 middle matrix. All arithmetic in this identity is over F2. For distinct d,s, define T = I + e_d e_s^T. Then T squared is I and preparing h' = T h executes h_d ^= h_s.

Replace M by M' = M T. This changes **column s** to column s XOR column d; it does not change column d. The target update is therefore M'h' = M T T h = M h. Executing T again restores every helper value before the parent's remaining restoration. Targets and helpers can be arbitrary on entry; no clean helper assumption is used. Since both new gates and every changed middle row are at frame zero, the new gate is legal without an extra frame move.

If C_j is the support set of column j, the complete saving is

```text
|C_s| - |C_s symmetric_difference C_d| - 2.
```

The subtraction by two pays preparation and restoration. For (d,s)=(242,19), the middle loses 16 ADDs and the two gates give the net saving 14. Omitting either gate, omitting the column correction, or reversing only the preparation direction fails the full dirty-input D boundary.

## Reproduce

From the repository root with Python 3.10+ and its standard library:

```sh
python3 -I -B research/r439-post-helper-shear-seed03/verify.py
python3 -I -O -B research/r439-post-helper-shear-seed03/verify.py
```

On Windows, use python in place of python3. Expected final line:

```text
PASS_R439_POST_HELPER_SHEAR ADDs=11783->11769 pairs=192282 trials=32 columns=661 controls=11 no_new_kappa
```

The default command regenerates and compares every decoded field of both [CERTIFICATE.json](CERTIFICATE.json) and [candidate.json.gz](candidate.json.gz). To deliberately regenerate those artifacts, add --write-certificate. Byte-identical source pins are mandatory, with an exact consumed-file inventory; omission cannot disable a check. Duplicate keys, nonfinite JSON and Boolean-for-integer receipt substitutions are rejected.

[search.py](search.py) uses packed support columns and union-find components. [independent.py](independent.py) uses explicit sets and graph traversal for the full support census, builds the candidate separately from literal rows, and replays chronological primitive events on all 661 symbolic input columns. It imports no search implementation. Both full forward and reverse streams are checked for every one of the 32 priced candidates, including COPY destination cleanliness, matching ERASE values, and the complete arbitrary-input endpoint. The complete D matrix must equal both PR967 and the original PR589 word. The unchanged pinned owning geometry checker reconstructs all 120 root lines, 111 labels and 636 frames. A separate accounting pass compares every register's ordered frame path and the paid rank histogram against the parent and retained EXPECTED.json.

The rank histogram is {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}; nine rank-seven COPY operations remain. Eleven rejection controls cover missing preparation/restoration/correction, wrong direction, precision admission, a strict-boundary equality, the restoration charge, source inventory and JSON typing.

## Coverage and precision

The seed is **03**, assigned before this round; it is not a new random draw. The class is one helper transvection between distinct components of the frozen PR967 preparation graph. All 439*438 = **192,282 ordered pairs** are scored; **191,712** cross-component pairs form the declared class and **931** have positive net support savings. Two implementations reproduce its full histogram and maximum support saving **14**, attained at four ordered pairs.

Positive nominees are ordered by descending saving, then SHA256 of the exact ASCII string 3:d:s, then d,s. Exactly the first min(32,931) nominees receive complete precision pricing, even after a feasible candidate is found. The selected witness is the first admitted nominee, at zero-based position one. This is an **exact support-score census and a bounded 32-candidate precision admission**, not exhaustive precision classification or unrestricted circuit optimization. No multi-shear optimization, alternative target basis, reorderings, restart or composition with another sprint result is covered.

The first tied maximum, (19,242), has F=72,935 and B=10,394,084 and fails the inherited nine-stage 192-bit cap. The selected direction keeps both parent bounds. Admission uses strict integer comparisons:

```text
64 F^3 B^2 = 2672929057893220568931365420032 < 2^104
2^18 F^5 B^4 = 6276870480677531528435239117197771736166837152483102425088 < 2^192
```

The bridge exponent and general formula are checked against the pinned global_k.py, and the 192-bit allocation against the retained tuning receipt. The nine-stage margin is small and is not rounded for admission.

## Scope, source and overlap

The frozen base is 2921874911956718fcaaaf9396fe8267b3cfa9f0. Its selected accepted pointer is PR942's conditional kappa 0.001661960547713947 with the PR589 bit supplier. This is historical context; the mutable selected-result.json is not a runtime dependency. [SOURCES.json](SOURCES.json) binds every consumed predecessor file and the base. [CLAIM.md](CLAIM.md) records the three candidates and the search restriction.

PR967 supplied the full helper-star construction; this package extends that fixed construction by one restored edge. PR965's GL(3,2) extensions and PR753's historical restored helper stars are mechanism precedents. PR915/926 supplied the frozen target basis and pair method. The new witness is not a rediscovery of those basis-change identities. The contribution is this concrete post-PR967 cross-component shear, its paid full word, exact score census, and independently replayable bounds and endpoint certificate. PR978 concerns another historical supplier; PR980/1001/1002/1015 concern A/B preparation; PR1003 concerns R480. Those improvements are not composed here. The concurrent sprint's [PR1040](https://github.com/CrocSwap/integer-mult-bounds/pull/1040) target-transvection search uses a different family; its three-ADD saving is not added to this one's fourteen.

The original syntactic **H2 is false**, and literal **K_equals_D is false**, as for the parent. The owning checker records both failures; the separate semantic D endpoint is what passes. H1/H3/H4/H5 and the other interface conclusions pass. This package does not establish native hosted execution or automatic provider admission. Adoption still needs the semantic-D contract, changed hosted emission, the complete native/precision/provider invoices and outer assembly. Native checks were not run in this environment. All-size/compiler, common-label, mutable-source, hosting and analytic obligations remain. No selected frontier, paid c, runtime claim or new kappa is changed.

Prepared for **@woklerx** with substantial **OpenAI Codex assistance** in research, mathematics, implementation, verification and writing. Separate implementations and an additional agent review are computational checks, not independent human review. Apache-2.0; see [NOTICE.md](NOTICE.md) for predecessor credit and disclosures and [VALIDATION.json](VALIDATION.json) for executed checks.
