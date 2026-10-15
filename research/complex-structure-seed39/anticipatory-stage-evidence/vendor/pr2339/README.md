# PR2226 low (anticipatory) aliases on the T74 pivot-566+554 borrow words

**Construction (local, verified) plus exact packing ceiling and model prices. No kappa claim.** PR2269 (Jeremy Kothe) put
43 **high** PR2226 aliases on both T74 local words (`gauge44` "base" and `extra`). This
package adds PR2226's **32 low (anticipatory) aliases** and the **5 high aliases that PR2269
omitted** to both words. Each word now has 80 aliases. The 32 low aliases come with the
64 initial compensation terms `c K_G z`.

| word | aliases | helpers | local paid profile | local mass |
|---|---|---|---|---|
| gauge44, PR2269 (43 high) | 43 | 437 | `{1:2351,2:501,3:414,4:129,5:42,8:8}` | 5385 |
| gauge44 + 32 low | 75 | 405 | `{1:2303,2:527,3:386,4:125,5:42,8:8}` | 5289 |
| gauge44 + 5 high | 48 | 432 | `{1:2351,2:501,3:414,4:129,5:37,8:8}` | 5360 |
| **gauge44, this package (80)** | 80 | **400** | **`{1:2303,2:527,3:386,4:125,5:37,8:8}`** | **5264** |
| extra, PR2269 (43 high) | 43 | 437 | `{1:2339,2:509,3:418,4:125,5:42,8:8}` | 5385 |
| extra + 32 low | 75 | 405 | `{1:2287,2:535,3:386,4:125,5:42,8:8}` | 5289 |
| extra + 5 high | 48 | 432 | `{1:2339,2:509,3:418,4:125,5:37,8:8}` | 5360 |
| **extra, this package (80)** | 80 | **400** | **`{1:2287,2:535,3:386,4:125,5:37,8:8}`** | **5264** |

Change per call: −121 rank units, i.e. −96 from the low aliases and −25 from the five high
aliases. COPY64 is still included. Each word has 624 independent input columns and 44 private
FULL-cleanup zero buffers (PR2269 had 76). The identity `mass = 1856 + sum of helper widths`
still holds: width inventory `{4:4,5:4,7:36,8:84,9:272}`, sum 3408.

All 16 low helpers that were not aliased are blocked by one exact condition: no lender is
left (see below). There is no second construction choice that would avoid it.

## What was checked

`python3 -B build_ext.py --controls` is deterministic. Run it with
`PYTHONPATH` pointing at a numpy install; numpy is needed only for the Gaussian products. It
does the following:

1. Checks the git-blob pins of every input. The inputs are copied from PR2269 head `b479fc55`
   and PR2226 head `dacaf3d8`.
2. Replays PR2269's shipped 43-pair witnesses with `replay_core.py` and reproduces its
   recorded profiles exactly. `replay_core.py` is PR2226's `replay.py` in function form. Its
   semantics are unchanged; only the `80 pairs / 32 low` assertion is now a parameter.
3. Builds the low and high pairs. The initial corrections are read off the residual of an
   exact diagnostic replay. Every residual term must have the form `(lender, (op,))` for a
   low operator, with a dyadic coefficient. No other term is allowed.
4. Re-runs the full exact replay for all three variants: free noncommutative operator
   algebra over all 624/629/656 independent inputs, `Y'=Y+X`, nested frame chronology,
   cold restoration, inverse cleanup at FULL with private zero buffers, and the
   omitted-inverse-warp control. It also confirms that dropping the compensation fails, and
   so does flipping one coefficient's sign.
5. Runs PR2226 `operators.py` on all 80 warps per word: exact Gaussian handoff and FULL-exit
   products, all 512 columns, phases included. The 43 inherited records are reproduced
   byte-for-byte.
6. Emits `words/BORROW-WORD-80{base,extra}.json.gz` with PR2269's unchanged emitter, then
   runs PR2269's independent `audit_local.py` as a subprocess. It passes in both
   orientations (`PASS_INDEPENDENT_EXACT_BORROWING_WORD`: 80 warps, 64 corrections, profile
   and width inventory re-derived from the word alone).
7. With `--controls`, runs PR2269's `borrow_controls.py`. All 23 mutations are rejected for
   the expected reason, including the four initial-correction controls, which are not
   vacuous here (`receipts/CONTROLS-80*.json`).

Receipts: `receipts/BUILD.json` (per-candidate decisions and blockers),
`receipts/AUDIT-80*.json` and `receipts/CONTROLS-80*.json`.

## Independent check and model prices

- `python3 -I -B check_ext.py --out` (standard library only; imports no PR or construction code;
  reads the reference inputs as git blobs at the PR2269/PR2226 heads) prints
  `PASS_T74_LOW_ALIAS_WORDS_INDEPENDENT`: warp algebra, anticipatory-term structure (frame-zero
  source = lender of its own operator), frame recount, exact forward and dual replay, links to
  the canonical words, and 28/28 negative controls per word (`check_ext.receipt.json`).
- `python3 -I -B run_all.py --out` re-runs the check, then prices the recounted profiles with
  `price_ext.py` (`price_ext.ext80.receipt.json`). E = 80586 extra freed mass versus PR2269.
  These are **model prices of an idle refill that was not built**:

| model | b (floor, 1e-22) | vs PR2269 b |
|---|---|---|
| F | 0.0017255088890837212072 | +1.725% |
| C | 0.0017126737497248571464 | +0.968% |
| C8 | 0.0017140567316684824711 | +1.050% |
| P | 0.0016871233700042746562 | −0.538% |

Model caveats. F keeps PR2269's realized idle remnants fixed and caps idle children at rank 48;
it is not a ceiling (fully repacking all idle mass into rank 48 would give about 0.001748).
P is not a floor for a real supplier, because hosting may add paid adapters. C reproduces
PR2269's own refill exactly by construction. Out of sample, both calibrated rules overshoot
the realized record they were not fitted to: C on T8 by 2.0e-6 and C8 on T74 by 2.3e-6.
C8 is not exact even in sample; it is 5.2e-6 above PR2260's realized b (`price_ext.py controls`).

## Packing ceiling for the new local words (exact, any hosting)

`python3 -I -B cap_ext.py` evaluates the merged fixed-word packing ceiling
(`research/complex-local-word-ceiling/ceiling.py`) on the call-weighted local profile. It uses
m = 73, 896 families per nine-stage replica and centre 64, with the largest idle child R = 48
(T74's maximum child) or 51. Each cap is an upper bound on b for **any** hosting, owner packing or
idle refill of that fixed local word under the coverage law.

| local words | cap, R = 48 | cap, R = 51 |
|---|---|---|
| PR2269 (43 high) | 0.001717935928829 | 0.001727257612832 |
| **this package (80)** | **0.001747958371974** | **0.001758245201617** |

The ceiling rises by +1.75%. PR2269's claimed b realizes 98.74% of its own R = 48 cap. PR2322
reports 98.66% of a 0.001720061 cap for its profile. At the same 98.74%, the new words would
give b ≈ 0.0017259. **This is an estimate, not a bound or a claim.** It sits above every open
T74 claim (top: PR2322, 0.001697060296). It needs every obligation under *Scope and limits*.

## Reproduce

From the repository root, with the standard library and `git`. It takes about 25 s and fetches
the pinned PR heads if they are absent:

```sh
python3 -I -B research/t74-low-alias-borrowing/run_all.py --fetch
python3 -I -B research/t74-low-alias-borrowing/cap_ext.py
```

Expected final lines: `PASS_T74_LOW_ALIAS_RUN_ALL check=PASS price=PASS crosscheck=PASS ...` and
`PASS_T74_LOW_ALIAS_PACKING_CAPS cap48_high43=0.001717935929 cap48_ext80=0.001747958372`.
`run_all.py` rewrites its receipts. Repeated runs differ only in elapsed-time fields.

Rebuilding the words needs numpy, which is used only for the Gaussian products:
`python3 -B research/t74-low-alias-borrowing/run_all.py --build --numpy-site DIR`. It
reproduces `words/` and `witness/` byte for byte.

## How PR2269 derived its T74 witnesses from PR2226 (reconstructed)

PR2269 ships its T74 witnesses as inputs; the derivation script is not in the PR. Diffing
`witness_43_*.json` against PR2226 `WITNESS.json` shows how they were made:

- The 43 kept high pairs keep the PR2226 register and lender.
- Each handoff index is the T74 block `first_input`, which is the T8 index + 7.
- `retirement_B_event` is moved to the T74 index.
- `handoff_basis` is recomputed as the first `dim(lender)` vectors of the echelon basis of the
  helper's first post-handoff frame.
- The 48 early-tail gates are unchanged, with `before_B` moved to T74 indices.
- `initial_corrections = []`, and every low pair is dropped.
- High pairs 606, 635, 637, 638 and 639 are dropped.

## Low aliases: conditions and outcome

These are the PR2226 low-pair conditions as enforced here:

- **(a)** The lender is retired before the handoff. It has no B, deferred or early-tail touch
  after the handoff.
- **(b)** At the handoff, the lender is exactly its own initial dirty input (asserted in the
  replay).
- **(c)** The lender's entrance frame has dimension 0. Every compensation term
  `c K_op z_lender` then reads a frame-zero helper input, so the monomial `K_G` is free. The
  auditor also requires that the source is the lender of its operator.
- **(d)** The handoff has rank zero: `E` is the first `dim(lender)` vectors of the helper's
  first post-handoff frame.
- **(e)** Every pre-handoff event on the low helper, other than the deferred helper-only
  corrections, is either an echo (`target += c L`, which is deleted) or a temporary
  external addition (`L += a ext`) with zero net change. An echo that reads a nonzero
  temporary part is rewritten as direct reads `target += c a ext` at the same index and frame.
- **(f)** The residual target response is exactly `-sum c K_op z_lender`, with dyadic `c`.

**32 transfer, with PR2226's own lenders.** The 64 corrections form the same
`(target, source, coefficient)` multiset as PR2226's 64 T8 terms; only the operator ids
differ. The prefix rewrites come from the T74 pivot kernels:

- 628 gets two rewrites, because the kernel inserts a temporary `±2·567` pair.
- 672 gets two, because the kernel's `B[6]` donates `−2·566` until `B[232]`.
- 676 gets one, as in T8.

The exact replay accepts all five rewrite gates (`add 214 566 -1`, `add 151 567 1`,
`add 117 566 1`, `add 181 566 -1`, `add 181 566 1`, all at frame 3).

**16 are blocked:** low helpers 632, 633, 634, 636, 640, 641, 642, 644, 648, 649, 650, 652,
656, 657, 658 and 660. Each one has a legal prefix plan. The blocker is lender supply. At
every one of the 12 handoffs, exactly 32 registers satisfy (a)–(c): the PR2226 low lenders
273…394, all at dimension 4. No other register qualifies, including registers that B never
touches. All 32 are used. Every low alias saves the same 3 units
(the lender is at dimension 4, the helper enters at dimension 1), so choosing a different 32
cannot help.

The other 16 cold registers with entrance dimension 0 are 311, 327, 498, 500, 501, 510,
512, 513 (final dimension 8) and 572–575, 580–583 (final dimension 7). Restoring them early
by moving more tail gates would hand off at dimension 7–8 into first frames of dimension 4–5.
That is a paid dimension-drop handoff. It is outside PR2226's rank-zero scope, and it costs
more mass than it saves.

## The five omitted high aliases

In T74, helpers 606, 635, 637, 638 and 639 enter at dimension 4. Their first frame after the
handoff is also dimension 4, because the pivot kernels re-solved those frames. The PR2226
lenders 395, 363, 530, 331 and 299 are at dimension 5 at the handoff. Using them would need
a paid 5→4 drop. That is why PR2269 dropped these aliases.

An exhaustive search over retired, unused, non-target registers found rank-zero lenders at
dimension 4: the X registers 12, 6, 31, 4 and 1. They retire in B between 732 and 862, and
their final frame is FULL. Each alias saves 5 units because the climbs to FULL merge.
Precedent: PR2226 and PR2269 already lend X register 73 to helper 653. The only other
rank-zero dimension-4 lenders are the 32 low lenders, and using them would give up a low
alias for no saving.

## Scope and limits

This covers the local scalar/frame construction plus exact Gaussian handoff products. It
does **not** include any of the following:

- native lowering of the new words in either orientation (PR2269 `run_native_borrow.py`
  chain, warp recipes, the Lemma G stage);
- a window-exact owner fill for 400-helper words;
- a refreeze of PLAN/SPEC;
- a certified price (only the model prices above), outer assembly or a kappa.

Hosting caveats:

- The five new high aliases lend X-register fields.
- The 64 compensation terms read 32 frame-zero helper inputs before the preconditioner.

Whole-call ownership of these must be re-checked in the hosted owner map. A naive
per-call-type difference, `249·Δgauge44 + 417·Δextra`, gives
`{1:−33636, 2:+17316, 3:−20316, 4:−996, 5:−3330}` (mass −80586). That figure is only
arithmetic: how the freed units fill idle depends on a new fill.

## Open next questions

1. Run PR2269's native chain (`bw_transport`, `bw_emit`, warp recipes, LOCAL-PROGRAMS, Lemma G
   labels) on `BORROW-WORD-80*`. Do the 64 frame-zero compensation reads and the X-register
   lenders lower without paid adapters in both orientations?
2. Build a window-exact owner fill at 400 helpers per call, then price it. The model prices
   above (-0.54% to +1.73% on b; calibrated about +1%) stay unverified until that fill exists.
3. Is there a rank-zero source of extra low lenders for blocks 632, 640, 648 and 656? One
   option is a dimension-4 cold register with entrance dimension 0 created by re-solving a
   pivot-kernel frame. The 16 remaining helpers would save at most 48 more units per call.

## Credit

- PR2226, anticipatory dirty borrowing (Cinna Davis, @1337isnot1337, with OpenAI Codex): the
  mechanism, the alias rule, initial compensation, `replay.py` (adapted here as
  `replay_core.py`) and `operators.py` (vendored).
- PR2269 (Jeremy Kothe, `research/gmx-t74-borrow43`): the T74 canonical words, the 43-alias
  witnesses, and the BORROW-WORD emitter, auditor and controls (vendored byte copies).
- PR2260 (Dugongue): concurrent application of high aliases to the T8 parent.
- PR2322 (Vlado Vojdanovski) found concurrently and independently that retired source fields
  can serve as rank-zero lenders for high roles: 619/621/622/623 to X fields 1/4/6/12 at a
  common rank-4 chart. This package's five extra high lenders (X 12, 6, 31, 4, 1) use the same
  idea. Its owner exchanges and the other open records (PR2302, PR2309, PR2312) use high aliases
  only. None of them adds the 32 low (anticipatory) aliases.

The full predecessor lineage is in `vendor/*/NOTICE*` and `SOURCES-PR.json`. Prepared with
substantial AI assistance (Claude Code, Anthropic); Apache-2.0. No independent human review
is claimed.
