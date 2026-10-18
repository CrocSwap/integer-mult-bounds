# Scope

This package concerns the P6k4 complex word underlying the selected
construction's SW4 read-set exchange. It decides one explicitly open finite
class: simultaneous full entering-copy read exchanges at arity two and three.

It does not change any supplier, certificate, assembly, Makefile target, or
file under `upstream/`. It claims no new kappa and no formal theorem.

# Result

**Scoped negative result (no new kappa).** Every unordered pair (703) and
triple (8,436) of the 38 legal full single-pair exchanges was applied at once
on bare P6k4 and refitted exactly:

- all 9,139 combinations are frame-legal (no cap, tail, end, edit, or
  conflict rejection);
- all conserve the local rank mass exactly (5,634);
- none beats the four-exchange SW4 word by the credited floating-cost proxy
  (best pair +0.00349, best triple +0.00175 above SW4; the input word sits
  +0.00699 above SW4);
- none dominates the SW4 profile componentwise, so no weighting-independent
  improvement exists in this class either.

Structural findings recorded in the evidence:

- The 602 single-pair choices reproduce the credited census exactly:
  564 frame-rejected, 38 legal, all legal ones full exchanges.
- The 38 legal fulls fall into three exact profile-delta classes:
  4 SW4-type `{1:-6, 2:+4, 3:+2, 4:-2}`, 20 of
  `{1:-2, 2:+2, 3:+2, 4:-2}`, 14 of `{1:-2, 2:+8, 3:-2, 4:-2}`.
  SW4's delta is exactly four times the SW4-single delta.
- 679 of 703 pairs are exactly additive (profile equals input plus the two
  single deltas); 24 pairs interact through shared targets. All 24 stay
  above SW4 by floating cost.

# Method

`search.py` implements pair discovery (BRoute rule), the credited one-pass
rewrite/frame policy, and paid-profile accounting from scratch, then
enumerates the complete arity-2/3 domain. Validation anchors: the input and
SW4 profiles reproduce the recipe pins, the 16 derived recipe moves equal
the recipe's byte for byte in effect, the 602/564/38 census matches, and all
703 pair outcomes reproduce under PR #775's independent evaluator code
(run separately, not imported).

`verify.py` is a second independent implementation (separate evaluator,
copy-first pair discovery, explicit-subspace spot checks, independent SW4
byte reconstruction with sha match, exact mod-p B-end-state controls, and
mathematical failure controls). It replays every committed evidence entry.

Floating cost is a nomination proxy only, credited to PR #775 / the PR #699
complex endpoint (`exponent = 0.0016634287545402057`); exact profiles are
committed for re-ranking under the true assembly pricing. Concurrent PR #874
shows the true ideal gains are strictly convex (not linear) in the number of
exchanges at the X4 stage; nothing here assumes linear ideal gains. The six
SW4-internal pairs and four SW4-internal triples below overlap PR #874's 16
exchange subsets, where both contributions agree they are admissible; PR #874
prices them through moment engines while this note enumerates the wider
38-pair domain through frame refits.

# Reproduce

Standard-library Python 3.11+ from the repository root:

```sh
python3 -B -I research/sw4-fullpair-seed29/verify.py
```

Expected final line:

```text
PASS_SW4_FULLPAIR_SEED29 pairs=703 triples=8436 legal=9139 no_beats_sw4 seconds=...
```

To regenerate the evidence from scratch:

```sh
python3 -B -I research/sw4-fullpair-seed29/search.py --out <dir> --arity 2 3
```

then compare `<dir>/EVIDENCE.json` against the committed
`EVIDENCE.json.gz` (gunzipped bytes).

# Limits

Arity four and above, partial-involving combinations (see PR #775),
alternative pre-read positions, relaxed frame floors, moved helper
boundaries, different decoders, and global (owner/invoice/outer) admission
are outside this class. Finite enumeration is not a formal proof and does
not touch the inherited all-size/compiler, hosting, precision/tape, or
analytic assumptions.
