# R439 z-program: exact 3->2 rewrites with unchanged frame paths and paid profile

**Finite bit-supplier result for the selected PR589 word; no new kappa.** This
package rewrites the *z-program* of the punctured R439 word
`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz` (PR589,
DreamingOfClouds on eumemic's PR555): the 2,629 source edges of the A and B
z-destination gates and their literal-reverse cleanup mirrors in section C.
Each accepted rewrite is one exact transvection (Steinberg) 3->2 identity:
one forward source edge is deleted and two kept edges swap order, so the rebuilt
cleanup loses its mirror edge as well. **Each accepted rewrite removes exactly
2 ADDs** from the complete exported word while changing **nothing else**: the
full F2 word map, all 661 register frame paths, and the paid profile are
verified identical to the base word.

The base word is pinned at base commit `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`
by canonical SHA-256 `5642fd0e35a1acc11acff8d0c08350c1617e95f310d4d35ad63a651f9eeeba0b`
([SOURCES.json](SOURCES.json)).

## Result

N = **405** exact rewrites (witness: [MOVES.json](MOVES.json)):

| complete local quantity | base (PR589 tuned) | candidate | change |
|---|---:|---:|---:|
| complete exported ADDs | 24,305 | **23,495** | **-810** |
| exported records | 27,234 | 26,424 | -810 |
| MOVEs / COPYs / ERASEs | 2,911 / 9 / 9 | 2,911 / 9 / 9 | unchanged |
| register frame paths (661) | reference | identical | unchanged |
| paid profile | reference | identical | unchanged |
| z-program product U (550 x 550 over F2) | reference | identical | unchanged |
| F2 endpoint on all 661 basis columns | pass | pass | unchanged |
| bit saving / kappa | conditional, complex-bound | unchanged | **no new kappa** |

Candidate word canonical SHA-256
`8aedb3be192baae884c80a2ff3d15d9f32ae8c8055dff170bebca2f87e75539a`
(committed as [CANDIDATE-WORD.json](CANDIDATE-WORD.json)). The paid
profile and every frame path are bit-identical, so the frozen hosting and the
whole pricing chain carry over exactly as in the prior phase-B block packages
(e.g. `r439-bsection-survey`, `r439-frame524-seed13`): this is a finite scalar
circuit-size result only. It does not change the selected exponent and asserts
no measured runtime improvement.

## The identity and its window

For three distinct z-registers `b, a, x` whose edges `(b,x)`, `(b,a)`, `(a,x)`
all occur in the z-program, over F2 (gate order left to right):

```
[b += x] [b += a] [a += x]   ==   [a += x] [b += a]     when (b,a) precedes (a,x)
[a += x] [b += a] [b += x]   ==   [b += a] [a += x]     when (a,x) precedes (b,a)
```

so the pair `(b,x), (b,a), (a,x)` collapses to the two kept edges `(b,a)` and
`(a,x)` in swapped relative order, and `(b,x)` is deleted. A multi-source gate
is a group of same-destination transvections, so an edge may be deleted from a
larger gate and an edge may split out of one.

A candidate instance is **accepted** only when all of the following hold:

1. **Window commutation.** Every gate strictly between the earliest and the
   latest of the three edges commutes with all three edges at the register
   level: same destination, or disjoint read/write registers; y-gates block
   only if they read the moved edge's destination; the scatter snapshot blocks
   on retained registers. This makes the contiguous identity applicable without
   changing any observable intermediate state.
2. **Exact endpoint.** The rewritten word with its rebuilt literal-reverse
   cleanup replays to the exact F2 endpoint on all 2v+R = 661 basis columns
   (hence J = I and the helper matrix K are unchanged and the untouched dirt
   compensation D still matches).
3. **Frame paths.** All 661 register frame paths are identical to the base
   word (checked register by register).
4. **Paid profile.** The climb/COPY paid profile is identical.

Search coverage and stopping rule: every triangle instance `(b,a,x)` of the
z-stream of the committed word is enumerated (complete base census: 2,606
distinct triangles, 2,613 instances; 293 base instances have a fully commuting
window). Rewrites are applied greedily in deterministic order, one per disjoint
window and edge set; accepted rewrites unlock further instances, and the search
stops at a fixed point: a full rescan with zero accepted rewrites (seven rounds,
405 accepted, zero endpoint rejections). The complete census, per-round
accept/reject counts and the fixed-point remainder are in
[MOVES.json](MOVES.json). "No further candidate" in the residual class is a
statement about this class on this word, not an impossibility theorem; the
greedy order is one deterministic order, not an optimum over orders.

The paired-transvection control class is exhausted on this word: the z-program
has only 17 duplicate edges `(dst, src)`, and every pair is blocked by an
intervening reader/writer or the scatter snapshot (also recorded in MOVES.json).

## Structural note: cleanup headroom

The z-program's product `U` satisfies `rank(U - I) = 539` over F2
(`rank(U_A - I) = 439` for the A section alone). Since a product of t
transvections has `rank(M - I) <= t`, any forward program and any exact
cleanup need at least 539 edges each, against 2,629 each in the base word
(2,224 each after these rewrites). The literal reverse cleanup is therefore
not claimed optimal; this gap is the unexplored structural headroom of the
word, and the present package only takes the exact local rewrites that
preserve every path and the profile.

## Reproduce

From the repository root, standard-library Python 3.11+ (CPython 3.13 used):

```sh
python3 -I -B research/r439-z3to2-seed13/verify.py
```

Expected:

```text
PASS_R439_Z3TO2 moves=405 ADDs=24305->23495 records=27234->26424 columns=661 paths=661 profile=identical U=identical controls=6/6 exporter=ok no_new_kappa
```

`verify.py` imports no search code. It re-applies every witness move of
[MOVES.json](MOVES.json) from the pinned base word, checks each move's
three-register identity and window commutation independently, compares the
rebuilt word with the committed [CANDIDATE-WORD.json](CANDIDATE-WORD.json),
runs its own exact replay on all 661 columns for base and candidate, compares
the 550 x 550 z-product U, all 661 frame paths and the paid profile, recomputes
the full ADD/MOVE/COPY/ERASE invoice and cross-checks it against the repository
exporter `research/e8-bit-carrier-skeleton/code/bit/export_records.py` run on
both words, rejects six tamper controls (source corruption, deleted cleanup
gate, truncated cleanup, tampered move list, non-commuting gate swap without
cleanup rebuild, truncated dirt gate), and compares the recomputed summary with
[CERTIFICATE.json](CERTIFICATE.json) byte for byte.

To regenerate the witness search (deterministic; same fixed point):

```sh
python3 -I -B research/r439-z3to2-seed13/search.py
```

## Scope and inherited assumptions

- **Word and class.** One finite word, one rewrite class (single-edge triangle
  3->2 with commuting windows), one greedy order. The identity is exact over
  F2 and the acceptance gate is exact, but the search is not an optimality
  proof for the z-program: multi-edge factorizations, non-commuting-window
  moves and alternative cleanups are outside this package.
- **Interfaces.** The candidate keeps H1-H5 of the interface lemma literally:
  D untouched and first, A writing only z, the scatter unchanged, C the literal
  reverse of the z-destination gates of A and B at the full frame, and V = I.
  Only the z-gate lists of A/B and their rebuilt C differ from the base word.
- **Hosting and pricing.** Frame paths and the paid profile are identical, so
  the frozen hosting selections and every priced quantity carry over unchanged,
  exactly as argued by the prior block packages. Native 5/9/11-stage C++/Boost
  checkers were **not** run here (no C++17/Boost toolchain in this
  environment); the result is an exact finite word-level certificate in the
  sense of PR1040/PR1047's "semantic" candidates, not a native hosted supplier
  admission.
- **Kappa.** The bit side does not bind the selected exponent (complex b <
  bit c), the profile is unchanged, so there is no new kappa and no new bit
  headroom. The value is finite circuit size on the selected bit supplier's
  word.
- **Not a theorem.** All checks are finite replays of one word. Nothing here is
  a formal proof of the upstream multiplication theorem.

## Credit

See [NOTICE.md](NOTICE.md). Prepared with help from opencode; substantial AI
assistance is disclosed. Assignment seed 13 (OS randomness), bit-supplier
track; the object choice (A-section z-program rather than the phase-B blocks
covered by concurrent PRs) is recorded in [CLAIM.md](CLAIM.md).
