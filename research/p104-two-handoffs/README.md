# Two successor hand-offs on the P104 word (conditional kappa .0030428242)

Complete conditional kappa **.0030428242** (**+1.29e-6** over
[PR5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551)'s .0030415312). The claim is
tested at .0030428205; the exact raw crossing lies in
(76070606559/25000000000000, 304282426237/100000000000000) =
(.00304282426236, .00304282426237).

**Conditional on** (a) the five framework assumptions retained by PR5544/5545/5551; (b) the validity of
PR5551, which is unreproduced at the time of writing; (c) admissibility of a fresh helper that
starts at a non-canonical mid frame. For (c): "Variant A" below passes the **unmodified** PR5545
`local.py`, and the canonical start-frame rule exists only in the #4610 compact-width verifier. The
selected record is not changed; no independent human or proof-kernel acceptance is claimed.

## Mechanism
Helper 473 (event 13725) and helper 531 (event 13941) finish their first rank-1 climb at a dim-2
frame (608, 613) and then idle; no other register holds their symbol. Following the successor
hand-off pattern of PR5472, the rest of each helper's life moves to a fresh helper that starts at
that frame: 473 climbs 8 as 1+7, 531 climbs 7 as 1+6. This is a pure rename: the same 25,310 events,
no extra ADD, identical paid profile (69,912 calls, rank-mass surplus 760). Only the helper targets change (12,814 -> 12,850 productive fields, the extra rank-1 spectators being
moment-neutral): at each of the 18 calls a rank-8 climb becomes 1+7 and a rank-7 climb 1+6, and by
subadditivity the concave moment gains 1-(8^t-7^t) resp. 1-(7^t-6^t), i.e. +6.6e-7 and +6.3e-7 in kappa.

## Files
- `handoff.py` derives `WORD.json.gz` (and Variant A `WORD-VARIANT-A.json.gz`) from PR5551's pinned word `inputs/pr5551-WORD.json.gz` (sha256 48f8734c...).
- `local.py`, `pricing.py` are PR5545/5551's files with ONLY literal changes: 735->737 public inputs, 743->745 rows, targets 12814->12850, kappa constants. See `LITERAL-CHANGES.diff`; `verify.py` re-applies the substitutions and checks byte equality.
- Variant A: the two helpers' leading MOVE is deleted and they start at frames 608/613 (public stays 735). It passes the unmodified `local.py`/native/caller; only the call-count literal in pricing changes (69,912 -> 69,876), and the crossing is identical.
- `verify.py` / `verify.sh` (stdlib, Python 3.12, a few minutes): both words, replay, transpose, native maps, physical caller, pricing with both moment engines, all 54 strict + 4 functional outer checks, exact crossing interval. `--write` refreshes `RESULT.json`.
- `inputs/pr5545-source-closure.tar.gz` is PR5551's byte-pinned capsule (`SOURCES.json`).

## Independent audit
An internal AI audit (separate read-only Claude agent, own builder and pipeline) found the literal
edits identical, the word byte-equal, extra targets double-count free, and reproduced the crossing
.003042824262. It rated legality of the mid-frame start as unresolved, which is why this is conditional.

## Credits
Builds on PR5551 (thu-nmrc), the successor hand-off pattern of PR5472 (GamingPuzzled), and the P104
word line of PR5544/5545 (aliromman; lineage PR2305/2152/2219). All predecessor credit is retained.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## Open next questions

- Is a fresh helper starting at a non-canonical mid frame admissible? The gain depends on it; Variant A passes the unmodified PR5545 `local.py`, and the canonical-start rule exists only in the #4610 compact-width verifier.
- Independent reproduction of PR5551, on which this package builds.
