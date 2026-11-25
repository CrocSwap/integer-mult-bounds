Apache-2.0 (see `LICENSE`). Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

The Lean sources are new. They formalise the realization part of Lemma A of PR #484 (DreamingOfClouds), which PR #484
adopted from PR #458 §3 (chafreaky: one helper per physical family per call, paid wrappers, restored spectators), with
PR #471's same-owner spectator borrowing (Dugongue), the footprint rule of PR #471/#500 (Dugongue, rohanarun) and, as a proved variant, PR #505's asynchronous whole-owner borrowing
(Dugongue). The event semantics are those of PR #425's conjugation lemma (jacklightChen / Zhihao Chen), reused from the
Lemma G package `../e8-lemma-g-lean` (a Lake path dependency, same Lean and Mathlib pin as `formal/lean` on main).
`code/check_owners.py` reads PR #484's emitted hosted template and its `EXPECTED.json` (read-only). The stream
model (family, cover class) is that of PR #442's idle-axis hosting (DaysSky) and PR #458; the pure banks are PR #433's
(icekylinx). `code/check_windows.py` is written independently of PR #484's audit_hosted_gk.py and PR #505's audit_async.py.
