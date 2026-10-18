# Twisted helper contract: helper-star restorations absorbed into A

**Replacement-interface result with finite R439 instances. No new κ, and the bit side does not
bind.** The selected result, the selected bit supplier (PR589) and `upstream/` are unchanged.

## The interface result

PR1194's semantic-D contract lets D mix helpers temporarily. D must still return every helper:
`(x, y, h) -> (x, y + N h, h)`. This package weakens that requirement. D may leave the helpers
**twisted** by any invertible helper-only map T, provided the cleanup absorbs the twist:

| | inherited / PR1194 | twisted contract |
|---|---|---|
| D operator | `(x, y + N h, h)` | `(x, y + N h, T h)`, T helper-only and invertible |
| D shape | zero frame, source-free, no COPY/ERASE/climb | same |
| cleanup C | literal reverse of A/B z-gates, so `C U = I` | z-only at the full frame, `C · U' · (I ⊕ T) = I` on z |
| target response | `N = K` | `N = K' T` |
| H1, H3, H5, `J = I` | kept | kept |

Block algebra gives `y + x + (N + K'T) h = y + x` on every F2-module. Assume the kept conditions
and the structural clauses (D's operator form, and C being z-only at the full frame). Then the two
new equations are necessary and sufficient for the dirty boundary `(x, y, h) -> (x, y + x, h)`.

**How it weakens PR1194, in two places.**

- **The cleanup is weakened even at `T = I`.** Every PR1194 word meets the twisted contract with
  `T = I`, but the converse fails at `T = I`. H4-tw replaces the literal-reverse cleanup by the
  semantic condition `C U' (I ⊕ T) = I`. PR1311's stale-cleanup control satisfies the twisted
  contract at `T = I`, yet the lineage rejects it: an endpoint alone does not give a chronological
  bridge for a non-literal cleanup.
- **The helpers may stay twisted.** The instances below have `T ≠ I`.

The two instances are not exposed to the first point. Their C is byte-identical to the base word's
literal C, and they are bridged cut by cut.

[PROOF.md](PROOF.md) gives the lemma, the uniqueness of the substitute register set, the exact
single-edge criterion and the chronological per-cut argument.

**Newly used premise.** The instances rely on the inherited common-frame / climb-additivity
premise, now applied to helpers: identical ordered per-register frame paths plus identical logical
values give identical physical states, across nonzero frames. Targets already rely on it, since
they climb holding `y + N h`. PR1194 deliberately restricted its substitution to frame-zero prefixes.
Here exactly three helpers (506, 507, 514) make their first climb out of the zero frame while
holding `centre + leaf`. Each does so at its absorbing gate, which immediately compensates. Nothing
beyond this premise is claimed about physical realization.

## The helper-mixing word

A helper-star restoration is the D gate `a ^= b` (centre a, leaf b). Delete it, and replace the
source set Sg of an A gate that writes a before a's first read by `Sg ⊕ S`. Here S is the unique
register set whose current values sum to b's input column. The state is invertible over F2 at every
cut, so S is unique. This preserves the whole boundary **if and only if** the new source set is
exactly `Sg ⊕ S`.

The three frame-legal positive moves are the same on every lineage word:

| deleted D restoration | absorbing A gate | old sources | new sources |
|---|---|---|---|
| `506 ^= 374` | A[288] at frame 71 | `[374]` | `[69]` |
| `507 ^= 355` | A[290] at frame 74 | `[355]` | `[72]` |
| `514 ^= 367` | A[304] at frame 65 | `[367]` | `[360]` |

In each case A has already performed `leaf ^= substitute` at the same frame. The centre therefore
reads the substitute in place of the updated leaf. C is left byte-identical. The words are
[absorbed-pr1062.json.gz](absorbed-pr1062.json.gz) and [absorbed-pr1188.json.gz](absorbed-pr1188.json.gz).

| complete local quantity | PR1062 word | absorbed | PR1188 word | absorbed |
|---|---:|---:|---:|---:|
| ADDs | 11,500 | **11,497** | 10,492 | **10,489** |
| D / A / C ADDs | 5,548 / 2,130 / 2,495 | 5,545 / 2,130 / 2,495 | 5,548 / 1,626 / 1,991 | 5,545 / 1,626 / 1,991 |
| exporter records (ADD / COPY / ERASE / MOVE) | 14,429 (11,500 / 9 / 9 / 2,911) | 14,426 (11,497 / 9 / 9 / 2,911) | 13,421 (10,492 / 9 / 9 / 2,911) | 13,418 (10,489 / 9 / 9 / 2,911) |
| forward / reverse positive bound F / B | 25,717 / 5,911,840 | 25,717 / 5,858,638 | 13,667 / 3,758,418 | 13,667 / 3,748,680 |
| local / nine-stage bits (strict caps 104 / 192) | 95 / 182 | 95 / 182 | 91 / 175 | 91 / 175 |

For both absorbed words, `verify.py` checks the following:

- **Boundary and frames.** The boundary is `(x, y, h) -> (x, y + x, h)` on all 661 dirty columns,
  forward and reverse, through the literal COPY/ERASE stream. Every register has the same frame at
  every D/A cut. The ordered per-register frame paths and exporter MOVE records are identical to
  the base word's and to PR589's.
- **Paid profile.** It is `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, rank mass 5,129, with
  nine rank-7 COPYs. It is recomputed from frame paths and from the pinned exporter
  (`research/e8-bit-carrier-skeleton/code/bit/export_records.py`).
- **Owner checker.** The unchanged `research/e8-bit-p111-tuned/code/xcheck_p.py` accepts the
  complete geometry and endpoint. Exactly four flags are false:
  `H2_D_frame0_targets_from_helpers`, `H4_C_literal_reverse_at_full`, `K_equals_D` and
  `C_is_U_inverse`. All five others are true. The base words carry only the first and third.
- **Twisted identities.** `T ≠ I`, with off-diagonal entries exactly (506,374), (507,355) and
  (514,367). T is invertible and helper-only. The checks also give `C U' (I_x ⊕ T) = I` and
  `C U' ≠ I`,
  `N = K'T` and `N ≠ K'`, and `V = J = I` with U in block form. D is frame-zero and source-free,
  and C is z-only at the full frame.
- **Base-word bridge.** The PR1194-style splice of each base word with PR589's D passes every owner
  flag, and each base D operator equals PR589's on all 661 columns.
- **Chronology.** A lockstep replay covers 3,270 cuts (PR1062) and 2,821 cuts (PR1188). At each cut
  the differing registers are exactly the pending centres, each off by its leaf column. At most
  three registers differ, at 459 cuts, and they stay at the zero frame. Each absorbing gate is the
  first A gate touching its centre.
- **Uniqueness.** All 1,980 one-register perturbations of the three new source sets break the dirty
  boundary.

## Single-edge census

The census covers every pair (trailing D restoration, A gate writing its centre before the centre's
first read) on four lineage words. Every pair's edited word is replayed on all 661 dirty columns in
both directions, and all of them preserve the boundary, as the criterion predicts. Frame legality
and the ordered frame paths are then checked separately.

| word | star edges | pairs | gain histogram | positive | frame-illegal | admitted |
|---|---:|---:|---|---:|---:|---:|
| PR967 | 221 | 445 | −10:1 −8:1 −7:1 −6:21 −5:25 −4:5 −3:15 −2:45 −1:169 0:114 +1:48 | 48 | 45 | 3 |
| PR1062 | 236 | 481 | −10:1 −8:1 −7:1 −6:25 −5:30 −4:6 −3:12 −2:45 −1:192 0:120 +1:48 | 48 | 45 | 3 |
| PR1122 | 236 | 489 | −10:2 −9:2 −8:1 −7:2 −6:7 −5:14 −4:10 −3:27 −2:50 −1:203 0:123 +1:48 | 48 | 45 | 3 |
| PR1188 | 236 | 470 | −10:2 −9:2 −8:1 −7:2 −6:5 −5:13 −4:8 −3:20 −2:52 −1:195 0:123 +1:47 | 47 | 44 | 3 |

On every word the three admitted moves are the triples above. Every negative-gain move is
frame-illegal. Among the gain-0 moves, two keep identical paths, two are legal but change paths,
and the rest are frame-illegal.

Some centres are never read in A: on each word, 6 star edges have a centre that is first read by
the scatter COPY. The only other writers of a centre before its first read are its other D-tail
restorations: 128 pairs on PR967 and 148 on the others. All of them have gain exactly 0 and are replayed exactly. No B or
C gate precedes a first read. All counts are pinned in [EXPECTED.json](EXPECTED.json).

## Controls (each instance; all must fail or be rejected)

1. **Omit the restorations without the A edit.** The dirty endpoint is wrong on 102 registers
   (99 targets and 3 helpers). The clean-helper endpoint passes, which makes this a dirty-input
   counterexample.
2. **A edit with the literal cleanup of the edited A** (inherited literal H4 enforced). The result
   fails exactly on dirty helpers 506, 507 and 514, which end as centre + leaf. It passes on clean
   helpers, and the owner checker rejects it with `helpers not restored: [506, 507, 514]`.
3. **Absorption after the first centre read** (PR1062 A[1218] for centre 514; PR1188 A[853] for
   centre 506). The dirty boundary fails.
4. **Wrong substitute register** (`[72]` instead of `[69]` at A[288]). The dirty boundary fails.
5. **One frame-illegal substitution** (centre 234, A[247], new source `[9]`). Its F2 boundary is
   exact, but the frame replay rejects it: register 9 cannot move from frame 115 to frame 11.
6. **PR1194/PR1311-style splice** (absorbed A/B/C with PR589's target-only D). The owner checker
   rejects it with `helpers not restored: [506, 507, 514]`.
7. **Corrupted source pin.** The SHA-256 check rejects it.

## Reproduce

From the repository root (standard library only, about 20 s per run on an Apple-silicon Mac):

```sh
python3 -I -B research/r439-twisted-star-absorption-seed02/verify.py
python3 -I -O -B research/r439-twisted-star-absorption-seed02/verify.py
python3 scripts/research_package.py --package research/r439-twisted-star-absorption-seed02 --check-only
python3.12 scripts/research_package.py --package research/r439-twisted-star-absorption-seed02
```

The expected final line is:

```text
PASS_R439_TWISTED_STAR_ABSORPTION words=4 instances=2 ADDs 11500->11497 10492->10489 columns=661 controls=16 no_new_kappa (… s)
```

All seven inputs are pinned by SHA-256 in [SOURCES.json](SOURCES.json): four lineage words,
PR589's word, the owner checker and the exporter. The verifier refuses drifted bytes. It executes
the owner checker from the verified bytes in-process; that checker raises its own `Reject`, not
`assert`. It runs the exporter from the verified bytes in a child interpreter without `-O`. Checks
raise `ValueError`, so `-O` cannot weaken them. The report must equal EXPECTED.json exactly, and
the committed absorbed words must equal the rebuilt ones. `--write` regenerates both. The report is
identical under CPython 3.12.15 and 3.14.8.

## Scope and limits

- **Class.** The census covers only the single-edge, single-writer class: one deleted restoration
  absorbed by one edited gate. Joint application of the three admitted moves is checked; this is
  not a global minimum or an unrestricted circuit optimum.
- **New result.** The new content is the interface lemma, its finite instances and the census. The
  three-ADD saving is a small finite consequence. It does not change the paid profile, the selected
  moment or κ.
- **Not run.** Native 5/9/11-stage C++ replay was not run on the absorbed words. Open PR #1509's
  checked `cpp_int` stand-in may make that possible on hosts without Boost. Hosted
  emission/invoice and outer assembly were not rerun either. All-size compiler,
  common-label/mutable-source, rounding/tape and analytic obligations remain inherited.
- **Physical realization.** It is argued only for the two instances. The argument uses the
  per-cut comparison with the PR1194-bridged base words and the climb-additivity premise stated
  above. The scalar lemma alone is not a chronological bridge for arbitrary twisted words.
- **Terminal-restoration exclusions.** Open PRs #1580 and #1592 rule out moving restorations to
  the end of C and arbitrary terminal compensation. Absorption happens before the centre's first
  read and changes A, so it lies outside their terminal domain and is consistent with them.
  #1592's stated next question was to move the cut earlier and change the continuation; this
  package answers it for the centre-writer class.

## Concurrent work on the same card and words

None of these uses the twisted mechanism: none leaves helpers twisted (`T ≠ I`), and none edits A
to absorb a D restoration.

- **Same base word, other mechanisms.** These open PRs work on PR1062's 11,500-ADD word:
  - #1543 (ToikY): two nonpositive helper moves, 11,500 → 11,489;
  - #1709 (Cinna Davis, @1337isnot1337): a five-helper cycle, 11,500 → 11,488;
  - #1704 (Ross Richardson): a two-copy scatter under a replacement immutable-temporary interface,
    11,500 → 11,380.

  Their scalar savings are larger than this package's three ADDs. Whether the three absorptions
  compose with them has not been tested.
- **Restored-helper (H2-sem) work.** #1782 (Aaron Wang) and #1805 (VictorLiwentao) admit and price
  PR848's helper-sharing wraps under PR1194's contract, with `N = K` and `T = I`. That is a
  different object.
- **Terminal deferral.** Discussion #1743 (Cinna Davis) claimed compensated terminal deferral; it
  expired with no PR. That domain is the terminal one PR1592 already excludes.

## Open next questions

The structured versions are in [TASK.json](TASK.json).

1. **Multi-gate splits and the neutral moves.** Can a restoration be absorbed by splitting S across
   two or more centre writers, or by chaining one of the gain-0 moves (two path-preserving per
   word) with a positive one? The single-edge census excludes these by construction. *First step:*
   extend the census to two-writer splits of S, on the same frame-legality filter.
2. **Native replay of the absorbed words.** *First step:* run PR1188's native 5/9/11-stage
   checkers on `absorbed-pr1188.json.gz`, with Boost or PR #1509's stand-in. *Blocker:* a host with
   Boost or an accepted stand-in.
3. **Feedback results with a twisted helper exit.** PR1706 (with PR1306/PR1557) finds no
   target-feedback saving for fully restored dirty shears, which is the `T = I` case. Does any
   feedback or shear gain appear once the helper exit may be permuted or twisted (`T ≠ I`) and
   absorbed by C? *First step:* rerun the 3-by-3 shear census allowing any helper exit T in
   `GL(R, 2)`, and charge the C absorption.
4. **Adoption of the twisted contract.** Would maintainers accept H2-tw/H4-tw/K-tw, together with
   the helper climb premise, as the interface for hosted admission?
   - *Why it needs more than the premise:* adopting H4-tw as a general interface also needs a
     chronological bridge for non-literal full-frame cleanups. PR1311 declined to infer one from
     endpoint success, and the helper climb premise does not cover it.
   - *How the instances avoid it:* they keep the base word's literal C.
   - *Blocker:* a maintainer decision, then a hosted emission of an absorbed word.

## Credit

- **Interface and checker lineage.** woklerx's PR1194 semantic-D contract and frame-zero
  substitution argument; Arham Tahir's PR1311 bridge on the composed word; Zhihao Chen's PR425
  scalar-interface lemma; eumemic's PR555 checker adaptation (`xcheck_p.py`); Dylan Crow's exporter.
- **Lineage words.** Sricharan Vagvala (@theon199): PR967 helper stars. Sagar Thakrar: PR1062
  B-block and helper-star D composition. Gareth Davidson (@bitplane): PR1122 A/B/star composition
  and PR1188 GL5 windows. Aaron Wang's PR1015 and Ross Richardson's PR923 B circuits are inside
  those words. DreamingOfClouds' PR589 tuning sits on eumemic's PR555 punctured word.
- **Terminal-restoration exclusions.** Arham Tahir's open PRs #1580 and #1592.
- **Restoration-coalescing lineage.** #1155 (Aaron Wang, open), #1199 (Sagar Thakrar), #1203
  (mightyOil) and #1205 (Adam Gall).
- **Concurrent same-card work.** Cited above: #1543, #1704, #1709, #1782, #1805 and the #1743
  claim. #1592's next question motivated the early-cut absorption.

Prepared by Sagar Thakrar with substantial Anthropic Claude assistance (Claude Code, including
subagents for the probes). No independent human review. New work is Apache-2.0.
