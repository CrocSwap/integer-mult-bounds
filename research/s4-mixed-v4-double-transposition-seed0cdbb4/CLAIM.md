# Cycle F local claim

- Track: `bit-mechanisms`; seed `0cdbb418f7a976685134143f77494c2c`.
- Task: `bit-new-register-model`; priority revision 3; catalogue SHA-256
  `6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075`.
- Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256
  `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Object: in formal `F2[S4]` on three arbitrary dirty roles, use paid adjacent
  transpositions `s1=(12), s2=(23), s3=(34)` and every rank-one idempotent
  `N` in `M3(F2)`. Test whether `diag([p],[q],[e])`, with
  `p=(13)(24)=s2*s1*s3*s2` and `q=(12)(34)=s1*s3`, has a four-call word.
- Baseline and objective: the direct word costs six calls. Both targets have
  displacement rank two, so PR #1333 gives the optimistic full-alphabet floor
  four. Every candidate call is charged one; a four-call word would save two
  calls in this finite model. No free interface, extra role, hosting or
  supplier operation is counted.
- Method: complete two-plus-two meet over all 84 paid factors, 7,056 ordered
  pair words and 49,787,136 length-four words. Check the exact formal
  `3x3` group-algebra endpoint. A positive control is `diag([q],[q],[e])`,
  which has a four-call direct word; `diag([p],[p],[e])` is a negative control.
  If the mixed target has no four-call word, the sign quotient makes all valid
  word lengths even, and the group-word length of `p` excludes lengths below
  four. The direct six-call word then proves the exact minimum six.
- Closest overlap: PR #1734 studies `diag([p],[p],[e])` in the same alphabet
  and role count, with minimum eight; this changes the target to two distinct
  commuting double transpositions and direct bill six. PR #1720 treats two
  identical 4-cycles; Discussion #1740 / PR #1749 treats distinct noncommuting
  3-cycles. PR #1333 supplies the broader rank-floor benchmark. Current exact
  search found no `p,q` target match: authenticated REST overlap read 456 open
  PRs and 140 Discussions at 10:03 UTC. The overlap helper's discussion
  snapshot was stale/rate-limited, so live PR and Discussion reads were used.
- Expected evidence: complete exact four-call exclusion or a checked
  four-call witness, six-call positive word, positive/negative controls,
  source pins and reproducible package. Stop after the complete meet and
  parity proof; no supplier or kappa claim.
- Predecessor attribution: PR #1333 and PR #1734 are the closest sources;
  neither executable is imported. Prepared with substantial OpenAI Codex
  assistance; no independent human review is claimed.
- Intended expiry: `2026-10-14T12:03:00Z` (approximately two hours after scope selection).

The remote Discussion claim could not yet be posted because GitHub's GraphQL
comment mutation is rate-limited. This local claim preserves the full scope
while the exact experiment proceeds.
