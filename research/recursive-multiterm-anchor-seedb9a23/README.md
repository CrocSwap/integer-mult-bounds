# Coalesce dirty-anchor fanout for a sum of shared products

**Finite local construction with an exact cost ledger. No selected-provider admission or new \(\kappa\).**

For (q\ge2) arbitrary-dirty output accumulators (A_i), suppose every output needs the same sum of (s\ge2) bilinear products plus one private product:

\[
A_i^{out}=A_i^{in}+P+u_iv_i,
\qquad P=\sum_{j=1}^{s}x_jy_j.
\]

Use (A_0), a required output with arbitrary initial value (a_0), as the persistent anchor. First send the old anchor value across the other outputs, (A_i\leftarrow A_i-A_0). Accumulate all (s) common products in (A_0), so it now holds (a_0+P). Send that updated anchor once across the other outputs, (A_i\leftarrow A_i+A_0), and add each private product. The result is (A_i^{in}+P+u_iv_i) for every (i). Reversing these steps restores every arbitrary dirty accumulator and leaves every source unchanged.

The complete local bill is:

| Schedule | Rank-one child calls | Width-\(w\) row additions |
|---|---:|---:|
| Compute every common and private product independently | (q(s+1)) | 0 |
| Accumulate common sum, then broadcast once | (s+q) | (2(q-1)) |
| Repeat a two-wave dirty-anchor fanout for each common term | (s+q) | (2s(q-1)) |

Thus the construction saves (s(q-1)) multiplication children over independent evaluation, and coalescing the shared sum saves (2(s-1)(q-1)) row additions versus repeating the one-term dirty-anchor schedule. If μ is the cost of one rank-one child and (A_w) is the complete cost of one width-\(w\) row addition, the net saving over independent evaluation is

\[
(q-1)(s\mu-2A_w),
\]

so the local break-even is (\mu>2A_w/s). For (q=3,s=3,w=1), the direct schedule uses 12 children; the aggregate anchor uses 6 children and 4 row additions, while repeating single-term fanout uses the same 6 children and 12 row additions. These counts include every multiplication child and all inter-output additions. The construction requires no clean helper, source copy, frame change, or cleanup child. The multiplication-add interface must preserve its source factors and add its product into the requested arbitrary target; this is the inherited child contract.

For scale only, eight hypothetical (q=3,s=3) blocks would remove 48 rank-one children from the selected fixed-word profile and introduce 32 scalar additions at width one. Waiving those additions, the exact fixed-word ceiling rises only 0.905971%, well below 5%. This is a rank-only screen, not evidence that the selected word contains eight instances. The source trace does not identify common-product output families or an admission schedule, so no supplier or \(\kappa\) gain is claimed.

The verifier checks the polynomial identity and its inverse for (2\le q\le5), (1\le s\le4), exhausts all 60,073 dirty/input states for (q=s=2) over \(\mathbb F_2\) and \(\mathbb F_3\), and rejects schedules that omit either compensation wave or use the wrong sign. The odd field control checks the subtraction explicitly.

## Reproduce

Python 3.12 and the standard library are sufficient:

```sh
python3 scripts/research_package.py --package research/recursive-multiterm-anchor-seedb9a23 --check-only
python3.12 scripts/research_package.py --package research/recursive-multiterm-anchor-seedb9a23
```

Expected verifier line starts `PASS_RECURSIVE_MULTITERM_DIRTY_ANCHOR`. The selector assignment and original card are pinned in [TASK.json](TASK.json); selected-record and moment-model pins are listed in [SOURCES.json](SOURCES.json). The claim is [Discussion #1167](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18927047).

This scope extends, but does not repackage, the one-common-product dirty-anchor construction in PR #1944 and active claim #18925817. It changes the object to a sum of (s\ge2) common products, accumulates that sum before fanout, and removes one compensation pair per extra common term. PR #1907 uses a clean required-output anchor; PR #1872 uses a clean helper and cleanup; PR #1155 treats general linear restoration coalescing rather than this bilinear output contract.

## Open next questions

Can the selected local word or another admitted supplier expose several common bilinear summands shared across at least two dirty output roles with a legal source, frame, and output schedule? The next step is a source-level incidence search for (s\ge2) common product terms, followed by a fully charged placement; the current selected trace does not encode enough operand ownership to infer such a pattern.

**Attribution.** The selected construction remains credited to its authors (see the pinned selected record and manifest). This multi-term local identity, exact finite replay, and package were prepared by Cinna Davis with substantial OpenAI Codex assistance; no subagents were used. No independent human review or supplier-level result is claimed.
