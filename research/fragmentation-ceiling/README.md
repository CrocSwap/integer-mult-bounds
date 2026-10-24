# Fragmentation loss: one number governs the native call

**No κ change. This package does not add a word.** It gives an exact test for any word in the #4610 family, and prices the centre-free (coded) constructions against it.

TL;DR. For a word in the kap family at unit (112, 8) with the 8-job rank-8 centre, κ ≥ 0.0030233 requires

  Λ(t\*) ≤ Λ\* = **23.8536932758** per call,

where Λ(t) = Σ over fields of (Σ climbs c^t − R_f^t) is the *fragmentation loss* and t\* = 1 − 0.0030233. The #4610 word has Λ = 23.8746264727, so it is **0.0209331969 per call** (0.088% of Λ) above the threshold. Equivalently the public invoice is at f(t\*) = −0.3767975440 = 18 × the gap. Λ is exact, linear in the climb profile, and needs no κ solve.

## What is in the package

| file | content |
|---|---|
| [PROOF.md](PROOF.md) | definitions, hypotheses, every theorem with a status tag (PROVED-LEAN / PROVED-PAPER / CHECKED-EXACT / CONDITIONAL) and its scope |
| [verify.py](verify.py) | stdlib-only script, about 10–15 s: rebuilds Λ, the identity φ = −2v·d^t − centre − Λ, the threshold Λ\*, the descent prices and the coded-family budget from #4610's public package |
| [data/verify_output.txt](data/verify_output.txt) | its output, `ALL CHECKS PASSED` |
| [lean/Skel.lean](lean/Skel.lean), `lean/lean-toolchain`, `lean/lakefile.toml`, `lean/lake-manifest.json` | Lean 4 + Mathlib (pinned): 37 theorem/lemma declarations, no `sorry` |

## Results

1. **Λ decomposition (Theorem B).** φ(t) = −2v·d^t − Σ_centre c^t − Λ(t), with Λ_f ≥ 0 and Λ_f = 0 iff the field pays one climb of rank R_f. PROVED-LEAN; exact on all 632 fields of #4610.
2. **Theorem C.** No helper is net-productive: its moment contribution is −Λ_f ≤ 0 for every credited rank. PROVED-LEAN.
3. **Exact ship threshold.** Λ\* = 23.8536932758; p = 16, a = 7 is the best controller in the kap family for every native call (CHECKED-EXACT for p ≤ 400, with a proved bound for p > 400). One 1+1 → 2 merge is worth 0.0041868 per call; five per call would clear the bar.
4. **Descents never help (Lemma 5) and have an exact price (Theorem D).** A rank-r descent costs at least r^t + (9+r)^t − 9^t: 1.99022 for r = 1, so at most 11 descents fit under Λ\*. PROVED-LEAN.
5. **A30-CUT.** Under the stated contact hypotheses the owned centre is moment-optimal: every use costs at least 8^t\* = 7.9499, whatever the carriers, inverse credit or sharing. PROVED-LEAN (dual, with the parity summation on paper) plus PROVED-PAPER (cut lemma), CONDITIONAL on P-ATOM, DELIV and mains net-up.
6. **Coded centre-free family.** The coded endpoint is #4610 with its centre deleted, so its exact per-call budget is B = 8·8^t\* − 0.0209332 = 63.577975271157. Per-call and deferred repairs cost at least 8·8^t\* per stage in scope, short by exactly the #4610 gap (18 × 0.0209332 = 0.376798 over the invoice). CONDITIONAL on the A30-CUT scope (P-ATOM, DELIV, mains net-up; owned carriers and fixed main chains for the deferred case); see PROOF.md section 6.

## Reproduce

From a checkout containing the public #4610 package:

```sh
python3 -B research/fragmentation-ceiling/verify.py [PKG_ROOT] [BAR]
```

`PKG_ROOT` is the directory that contains `research/kappa-round3-warp-20261022/` (found automatically when this directory sits next to it, or via `$INTMULT_PKG`). `BAR` defaults to 0.0030233; any other bar changes t\* and so Λ\*, and the script reports the corresponding values. It reads only `ACTUAL-WORD.json.gz`, `ARITHMETIC.json` and `NumericalMoments.lean` of that package, and uses Python's `decimal` at 60 digits.

Lean (optional): `cd research/fragmentation-ceiling/lean && lake exe cache get && LEAN_NUM_THREADS=4 lake build Skel`. The lakefile pins the Mathlib revision; with the Mathlib cache the build compiles only `Skel.lean` (a few minutes). The `#print axioms` lines at the end of the file report `propext`, `Classical.choice`, `Quot.sound` only.

## Scope and caveats

- The threshold is for words in the family: kap path controller (A17 e = 1, thick set {0, 2p, odd}), unit (v, d) = (112, 8), centre of 8 rank-8 jobs per call. It is necessary for every such word; sufficiency assumes the invoice has a single crossing in (0, 0.05] (checked on a grid for the invoices used).
- H1–H3 (frame dimension changes only at paid transports; transport rank; credit once) are the package's own contract (see PROOF.md section 0 for line citations). H2 for non-nested transports is derived, not a contract line.
- "Mains are net-up" and P-ATOM are hypotheses of A30-CUT. Open scope: cross-use sharing at a common frame, deliveries at frames meeting the port, decoders that break P-ATOM, carriers that ride warps, query shears.
- Statements about #4929, #4933, #4932, #4931, #4940 and #4694/#4698 rest on those PRs' published data as fetched, and were priced here; their authors' claims were not re-run.
- The numbered constants in PROOF.md that are marked "source" were computed in research notes from data that is not shipped here; `verify.py` rebuilds the others.

## Open next questions

- A word in this family clears +0.05% only if Λ(t*) ≤ 23.8537 per call (gap 0.0209 to #4610). Which scalar-program changes can merge enough climbs? Edits to #4610's fixed program have not produced any so far.
- Can a decoder for P112 that uses gather/scatter-interleaved (staircase) atoms cost below 64? Atoms that beat the masked price exist, so the single-wire decoder wall does not cover them.
- Does A30-CUT extend to cross-use sharing at a common frame, to deliveries at frames meeting the port, and to warp-riding carriers?

## Credits

- **Cao Yifan (intqwq), #4610**: the round-three word, its verifier, the contract (P, Q, V) and the public invoice that everything here is computed from.
- **Dugongue, #4929**: the centre-free producer and the explicit code A = I − 14P.
- **Cinna Davis (1337isnot1337), #4694, #4698, #4470**: the 640-field interface, +112 cache pricing, eight chains, and the kap controller lineage.
- **dillona, #4933**: the coded p16 caller, deferred negative banks, `GAUGE.json` identities and the physical ABI of the coded call.
- **Clear1nsight (Chris R), #4931, #4932**: the one-bank grade-2 ceiling and the prefix offer.
- **SethBurkart123 (Cayden Burkart), #4940**: the controller-conjugation idea and its exact diagonalisation.
- zxv and the earlier lineage of the kap family.

Written by Claude Opus 5.5 (Anthropic), via Claude Code.
