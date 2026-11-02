# Conditional kappa 0.00328637739144124222748802: the PR6398 mixed root with a third group-1091 anchor

This package replaces the PR6375 native word inside the PR6398 mixed-root
composition by the same word with one more helper anchor. It claims
**kappa 0.00328637739144124222748802**, conditional on the five inherited
framework assumptions listed below. That is **+1.626e-7** (**+0.00495 percent**)
over PR6398's 0.00328621476572836015146308, and about 4.2897 percent over PR6375's
0.00315120; almost all of the latter is inherited from the mixed root and the
PR6375 lifts. The exact raw crossing of this word with the unchanged caller lies in
(0.00328637739144124222748803, 0.00328637739144124222748804), as printed in
`RESULT.json` (`price.raw_root_interval`). All checks are author checks.

This claim does not exceed the open draft PR6417 (0.003286849), which composes the
PR6399 native merge with the PR6398 root; this package is built on PR6398 alone and
is independent of PR6399. The third-anchor word edit touches registers and frames
disjoint from the PR6399 merge (group 1091 and frames 245/246, against role 400 and
frames 1090/477), so it can be stacked on it; that stack is a separate recompute.

## What changes against PR6398

Only the native word changes. The mixed root, the six-field caller, the compiler
and the outer ledger are byte-for-byte the PR6398 ones.

- `final[234]` goes from frame 127 to frame 246. Helper 234 is the third anchor of
  group 1091, after anchors 224 and 227 (frame 245).
- Per native call the paid profile changes by +1 at rank 4 and -1 at rank 5, and the
  productive profile by +1 at rank 8 and -1 at rank 9; the paid call count is unchanged.
- The word has 44 owned lifetimes (PR6375: 43) and real scalar allowance 131,052
  (PR6375: 129,670), that is 1,382 more units. Both are charged by the unchanged checkers.
- One new native chart (1091, 246) is checked; the native word has 2,942 distinct maps (PR6375: 2,941).
  The helper and main-field normalizers (1,124 and 208) are unchanged.
- Paid mass 5,925 and helper mass 4,205 (PR6375: 5,926 and 4,206).

## Construction

On the transposed PR6353 word, group 1091 has joint capacity exactly 3 across the
entrance frames 245 and 246: the response-free input directions U_245 and U_246 each
have dimension 2, the helper-only departure functionals have dimension 7, and the joint
pairing rank is 3. A dyadic solution places anchors 224 and 227 at frame 245 and
anchor 234 at frame 246. It is stored in `SPEC.json` and rebuilt by `construct3.py`,
which generalizes the PR6372 contact-block constructor and reproduces the PR6372 word
exactly when given no spec. The PR6375 lift rounds are then re-applied unchanged. The
capacity computation is exploratory; acceptance rests on the exact replay of the final word.

## Tariff scope

Per call the third anchor changes the signed local invoice by (H5-H4)-(H9-H8) with
H(r) = r^t. This is positive for every strictly concave increasing H, in particular for
every t in (0,1), because increments of a strictly concave function decrease. It adds no
paid call. The word as a whole keeps the scope of PR6375: that word's six input lifts
add paid rank-1 calls and are positive only for power exponents of about 0.873 to 1,
and zero at linear cost. The claim is made at the stated exponent only and is not a claim
for every concave tariff.

## Reproduce

Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/mixed-root-third-anchor-composition
python3.12 -I -B research/mixed-root-third-anchor-composition/verify.py
python3.12 -I -O -B research/mixed-root-third-anchor-composition/verify.py
```

`--build-only` runs the cheap rebuild and local-delta checks. `--write-result`
generates `RESULT.json`; the plain command compares against it. Direct runs on one Windows laptop
(CPython 3.12.10): `--write-result` 58m43s under heavy load, the plain comparison
(`-I -B`) 16m05s and the optimized run (`-I -O -B`) 12m50s, all exit 0, ending with
`PASS_MIXED_ROOT_THIRD_ANCHOR_KAPPA_00328637739144124222748802`. On slow hardware the
runs can exceed the 590 s per-command cap declared in `VERIFY.json`; that is a
timeout, not a failed check. The retained PR6372 and PR6375 sources
are in `contact-source.tar` and `lift-source.tar`, bound by `CONTACT-INPUTS.json` and
`LIFT-INPUTS.json`. Six live files of the preceding composition are pinned and declared;
see the source-pin note below. Exact packing-cap statement: PR6398 reports the all-binary-size
fixed-root ceiling (`fixed_root_ceiling` in RESULT.json) and no separate packing-cap
fraction; this package does the same, and its claim lies less than 2e-26 below the raw
optimum (`raw_optimality.certified_kappa_distance_upper`).

## Scope and limits

- Five inherited framework assumptions remain: native_all_columns, owned_erasure,
  compiler, precision_tape and analytic_recovery. This is a conditional finite certificate.
  It is not a proof of the multiplication theorem.
- It is not a runtime speedup, no materialized uniform word or rounded multiplier is
  claimed, and the selected frontier is unchanged.
- The all-width native claims are inherited: native maps are checked at tensor width one and
  extended by frame induction; the central query is made an involution through the
  inherited normalization (Q^2 = X, a translation with absolute phase +1).
- The package consumes PR6375's native word construction with one more anchor, so it
  inherits the PR6375 tariff scope above.
- Author replay only: not independently reviewed, and no formal-kernel acceptance.
- `RESULT.json` price field `refinement_kind` is a label inherited from PR6398 and does
  not describe this word; the complete invoice and word are the ones listed above.
- The shadow rows for owned labels 779 to 781 are zero in the transposed preparation but
  not at the forward CLEAR; this is the inherited `owned_erasure` obligation, as in PR6372.
- Source-pin note: the six live inputs from `mixed-root-source-composition` are pinned
  with `head:24f03629fc2a939ea0c6c015017bf1cdc07e06cd` (the PR6398 head). A real-repository
  submission needs that commit to be reachable, so the branch must be based on or contain
  PR6398 (or those files must be committed first).

## Open next questions

- Independently review the third anchor: recompute dim U_245, dim U_246, dim L and the
  pairing rank 3 in exact rationals, then replay the word and the new chart (1091, 246).
- Check whether other first-departure groups and entrance frames admit more anchors by the
  same exact pairing-rank computation. Only group 1091 with frames 245 and 246 was examined.
- A larger gain needs a changed caller or root, or a new source construction.

## Credit

New composition, third-anchor construction and adapted verifier: Claude Sonnet 5.5 via
Claude Code, orchestrating subagents, for the user Erwan L. Substantial AI assistance;
Apache-2.0.

Predecessors, with the exact wording and lists retained in `NOTICE` and the source archives:
Ali Romman (aliromman) with OpenAI Codex: PR6398 mixed-root composition, PR6353 joint
output contraction, PR6372 contact blocks, PR6348 query tree, PR6349 source, PR6167
retained operands, PR5544; DreamingOfClouds with Claude Opus 5.5: PR6375 shared-carrier
lifts, PR6314 and PR6143/PR6144; Cinna Davis (productive caller, query thinning,
controller lineage); Mason Hale (PR5811); Pierre-Loic Doulcet (hexapode, PR5565);
Chris R / Clear1nsight (PR3998); Jacob Alan Sussman (productive recursion); zxv and Cao
Yifan (intervals, compiler, native and pricing lineage); Gareth Davidson, David Arias,
flyingviper, thu-nmrc, ToikY, Douglas Colkitt, Maxime Fleury, Tekalign and Nick Petalas
(source-history and replay controls). No Matarener work is credited here because none appears in the NOTICE chain
of the consumed sources.
