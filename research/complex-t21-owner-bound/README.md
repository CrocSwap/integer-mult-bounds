# Bound for the fixed U8 whole-owner family

The construction in [`complex-t21-owners`](../complex-t21-owners) attains
κ = **0.001661957774647029**. This separate exact enumeration shows that changing
only replica count or whole-helper placement cannot improve that reported grid
value within the following fixed family:

- U8 local paid profile and helper widths `{4:80,5:32,7:54,8:122,9:216}` per call;
- nine complete calls per replica and the existing cap-8/16/32/48 idle stock;
- unsplit whole helpers and the retained prefix charge `113+18T<512`, hence `T≤22`;
- the same bit supplier and seven-step outer recipe.

All execution-window constraints are relaxed, so the bound includes arbitrary
call order in this family. It does not bound other local words, capacities,
split helpers, a sharper prefix analysis, or other outer recipes.

```sh
python -B research/complex-t21-owner-bound/run.py --out /tmp/t21-owner-bound
```

The standard-library producer enumerates 3729 remainder count vectors. A
separately structured checker derives the signed-price table from 1163 legal
bin count vectors, independently enumerates all 3729 remainder vectors, and
uses the second rational moment engine. T21's `{48:6292,3:1,1:3}` is the unique
best normalized relaxed profile. At the successor endpoint it already has
moment strictly greater than one; even that relaxed upper endpoint yields the
same κ on the `10^-18` grid. This proves a grid bound, not the exact real-valued
root or uniqueness of the geometric owner assignment.

The enumeration is not needed to trust the constructive witness. Conversely,
this bound alone does not establish the witness's feasibility. See [PROOF.md](PROOF.md).

Prepared by Chafik Boukhalfa with OpenAI Codex assistance, Apache-2.0.
The signed dual is the one used in PR795. The second arithmetic and outer
helpers are unchanged pinned repository sources, credited in those files and
the companion construction's notices.
