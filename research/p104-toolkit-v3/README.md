# P104 toolkit v3: token-settled drops, frame-perp duality, fast exact replay, κ(k) caller law (no κ)

This package ships our stable, verified P104 tools for the hosted-word format of ToikY's
[#7546](https://github.com/CrocSwap/integer-mult-bounds/pull/7546) and later words. Each tool has a usage section
below, a runnable command-line example and tests with positive and negative controls. The tests run in minutes on
vendored data (the #7546 word, the #7113 caller and our #7601 edit list).

It makes **no κ claim** and ships no frontier word. At the time of writing the frontier is aliromman's #7605
(κ 0.0036504442446). The one new word the tools produce here, #7601 + the main-902 drop (§C.3), prices below it.

| | tool | what it does | needs |
|---|---|---|---|
| A | `pricekit.py` | exact caller + native invoice, certified κ enclosure, D0, ledger law | stdlib |
| B | `dualword.py` | frame-perp transpose: word ↦ dual word, an exact involution that preserves the price | stdlib |
| C | `tokdrop.py` (+ `modp.py`) | token-settled drop engine: stay-drop repair in clean mode, premix settlement rank, exact build | numpy (python-flint optional) |
| D1 | `accx.py` (+ `fastreplay.py`) | admissibility of an edited word against its base; replay mod 2^61−1 with exact re-checks | stdlib |
| D2 | `lossless.py` | law DUAL: finds every lossy owned CLEAR in one forward pass | stdlib |
| D3 | `nativeplan.py` | helper-plan extractor (routes, stays, typed events, requirement blocks, exact π-states) | stdlib |
| D4 | `validate.py` | one command: accx + lossless + the repository's invoice tools | stdlib |
| E1 | `kformula.py` | closed-form caller C(k) and the κ(k) law | stdlib |
| E2 | `layout_price.py`, `cap_check.py` (+ `sl_lib.py`) | parametric mask-layout pricer; crossing caps and the Floor lemma on a real caller | stdlib |

Tags:

- **[C]** exact computation, re-run by the tests in this package (`tests/`, listed in [VERIFY.json](VERIFY.json)).
- **[C-param]** exact price of a stated parametric histogram, not of a word.
- **[P]** proved (short argument given here).
- **[S]** judgement.

Nothing tagged [S] is claimed as a result.

## How to verify

```
python3 -I -B research/p104-toolkit-v3/tests/test_pricing.py    # A, E    PASS_TOOLKIT_PRICING
python3 -I -B research/p104-toolkit-v3/tests/test_checkers.py   # D       PASS_TOOLKIT_CHECKERS
python3 -I -B research/p104-toolkit-v3/tests/test_dual.py       # B       PASS_TOOLKIT_DUAL
python3 -I -B research/p104-toolkit-v3/tests/test_drops.py      # C       PASS_TOOLKIT_DROPS      (numpy)
python3 -I -B research/p104-toolkit-v3/tests/test_dualdrop.py   # B + C   PASS_TOOLKIT_DUAL_DROP  (numpy)
python3 scripts/research_package.py --package research/p104-toolkit-v3
```

Run them from the repository root; `validate.py` needs the checkout for the repository's invoice tools and skips
that step elsewhere. Every tool also runs alone (`python3 TOOL.py` prints its usage). Words are JSON or gzipped JSON
in the hosted native format (`public`, `owned_fields`, `frames`, `initial`, `final`, `live`, `hosted`, `program`).

---

## A. `pricekit.py`: the exact pricer

Our single exact pricer for P104 caller + native invoices (PRICEKIT lane, vendored unchanged). The module docstring
states the full accounting contract: charging rules for caller events, the native word's paid and helper histograms,
the ledger law, and the parametric native.

```
python3 pricekit.py data/caller-7113.json.gz data/base-7546-word.json.gz
# [PRICEKIT pricekit/1 (2026-11-11)] ...: S=1424 kappa=0.00364841129479084532481164 D0=393242.1350 ...
```

- API: `native_from_word(W)`, `caller_invoice(C)`, `invoice(caller, native)`, `price(inv)` → S, κ enclosure, D0, Dk;
  `check_slots(C, native)` (the ledger law d = m); `replay(W)` (exact Fractions); `drop_registers` / `verify_drop`.
- κ is the root of F(t) = Σ (T_r − P_r) r^(1−t). It is enclosed by bisection with error-bounded Decimal signs.
  Uniqueness is certified by interval monotonicity.

Controls [C]:

- #7546 prices to S = 1,424, κ = 0.00364841129479084532481164, D0 = 393,242.1350 and 110,468 paid jobs. The
  enclosure is narrower than 1e−50 and uniqueness is proved.
- Our #7601 word, rebuilt from its edit list, prices to κ = 0.0036490213053944204892137903671.
- The ledger law d = m holds for both port types.
- Negative controls: an invoice with S ≤ 0 returns `NO_CROSSING`, and 104 extra rank-1 paid jobs lower κ.

## B. `dualword.py`: frame-perp duality

`dual(W)` reverses time, transposes every local op and replaces every frame F by F^⊥ (standard dot on F₂⁹). It also
swaps the X and Y register of each port (live r ↔ r + 112, hosted X2 ↔ Y2). The op rules:

- `ADD r += q·s` becomes `ADD s += q·r`, and `SCALE` is unchanged.
- `MOVE a→b` becomes `MOVE b^⊥→a^⊥`. Perp reverses inclusion, so an ascent stays an ascent with the same gap.
- `INIT` and `CLEAR` trade places, and `COPY` becomes `ADD`.

```
python3 dualword.py data/base-7546-word.json.gz /tmp/dual.json.gz
python3 accx.py data/base-7546-word.json.gz DUAL_WITH_SCALES.json.gz --allow-owned-reframe
```

Results:

- **[P] The price is invariant.** Every charge of the native invoice is a function of dimension gaps: a MOVE pays
  |dim b − dim a|, and a helper is credited dim final − dim initial. Perp maps dim d to 9 − d, so every gap is kept.
  Hence the dual has the same T and P histograms and the same κ. The cost table is not symmetric in dim, but only
  gaps are priced.
- **[C]** dual(#7546) has identical native histograms and the same S, κ enclosure and D0 bit for bit.
  dual(#7601) prices to #7601's κ.
- **[C] dual is an involution.** dual(dual(#7546)) differs from #7546 in exactly one event: the single COPY comes
  back as an ADD, and `restore_copy` puts it back. The frame basis lists differ; their spans agree.
- **[C] B ports.** The 8 native-B ports (the ports outside `hosted.Dports`) need free contract SCALEs (x·2 at the
  start, Y·½ at the end; 16 events, `fix_b_ports`). After them, all 1,501 public rows equal #7546's exactly.
- **[C] A second admissible base.** The dual passes every accx check except our edit lanes' rule "owned MOVEs
  identical to the base": its 47 owned moves use different frames, with the same 24 descents and 23 ascents. It has
  0 lossy CLEARs.
- **[C] Negative control.** The transpose without the X ↔ Y port swap fails accx.

**[S] Use.** Duality gives a second admissible word with the same κ and different owned frames and co-locations.
Scans that are blind on the primal can see edits on the dual (§C.3).

## C. `tokdrop.py`: the token-settled drop engine

This is the engine behind our [#7601](https://github.com/CrocSwap/integer-mult-bounds/pull/7601). A **stay** is one
interior stop of a public register, `(r, F, t_arr, t_dep)`. Dropping it deletes the MOVE into F and every event of r
at F, and lets r climb straight to its next frame. The engine then decides whether the damage repairs for free, in
three steps.

1. **Clean-mode repair** (`Context.test`, `Engine.solve`).
   - Unknown corrections `a += k·b` are placed wherever a and b share a frame after a became dirty, with b still
     clean there. This keeps the final rows linear in k.
   - Every main, and every helper not ending at V, must end with its base row. The comparison uses the main (π)
     columns only: this is "clean mode", where the helper-token columns are deleted.
   - Helpers ending at V must land in the row span of the V group, because V post-ops are free.
   - Owned rows at every owned→public write and at every CLEAR must equal the base.
   - The system is solved mod 2^31 − 1 by random rank-1 tensor projections (Schwartz–Zippel), a rank test and the
     canonical rref solution.
2. **Settlement rank** (`Context.settle_rank`). Clean mode ignored the helper-token columns. They are settled by a
   premix at t = 0: an invertible block-diagonal map on registers that share a birth frame.
   rank = Σ_f rank[X_new,f | X_base,f] − rank X_new,f, and rank 0 means such a premix exists. Tier B keeps every row
   exact; tier A relaxes helpers that end at V.
3. **Exact build** (`Context.build_exact`).
   - Rational reconstruction of the corrections.
   - An exact Fraction solve for the premix, as ADDs at the birth frame at t = 0.
   - Exact V post-ops.
   - An exact replay against the base. The build refuses (`BuildError`) unless every step is exact and no new owned
     observation appears.

```
python3 tokdrop.py data/base-7546-word.json.gz scan 134:595 100:783       # repair + settlement ranks
python3 tokdrop.py data/base-7546-word.json.gz build 100:783 134:595 OUT.json.gz
```

`numpy` is required. If `python-flint` is installed, `modp.py` uses it; otherwise a pure-numpy backend runs. Both
return the same canonical rank, rref and null space. The rebuild below is byte-identical under either backend: we ran
it with flint in the lane and with numpy here.

### C.1 Controls on #7546 [C]

- The census lists 4,728 interior public stays with their stop price m. The stop price is the D0 per call saved by
  merging the two MOVEs: f(gap) − f(a) − f(b), with f(x) = x ln x.
- **134@595** repairs in clean mode with K = 355 candidates (r1 = r2 = 135), settlement rank 0 in tier A and tier B,
  and π exact.
- **100@783** repairs with K = 118 candidates (r1 = r2 = 46), settlement rank 0/0.
- **Negative control.** With correction candidates switched off (`frames_mode='none'`), both drops leave violated
  rows. The repair is what makes them free.
- **Negative control for the build.** On the dual (§C.3), stay 1289@117 settles in tier A but not in tier B, and
  `build_exact` refuses it because its premix is not exactly solvable.

### C.2 #7601 rebuilt byte-for-byte [C]

Running `build_exact` on both stays gives **exactly the #7601 word**: 76,642 events, 4 corrections, 152 premix ADDs at
{0} and 0 post-ops. Its stop price is 3.8191 D0 per call. One owned observation is removed (`134 += −2·owned1503 @595`)
and none is added. accx gives ALL CHECKS PASS and κ = 0.0036490213053944204892137903671.

### C.3 The main-902 drop, found on the dual [C]

This is the dual scan of our DUALSCAN lane:

1. Take the dual of #7601 and swap frames 3 ↔ 127, since {0} and V trade places under perp. The engine then runs
   unchanged on the dual.
2. On the dual, register 794 (the image of hosted main 902) drops its stop at chart 595 with **K = 0**: no
   correction, no premix, settlement rank 0/0.
3. Map the result back with `swap_frames`, `dual` and `restore_copy`. Main 902 then climbs 3 → 618 in one MOVE
   instead of 3 → 595 → 618, and the 5 owned ADDs it made at chart 595 vanish.

Results:

- accx against #7546 (strict, owned MOVEs identical): ALL CHECKS PASS, with 0 lossy CLEARs.
- The word **#7601 + 902@595** prices to κ = 0.00364932638757719639692487. That is ×1.0000836 over #7601 and
  below the frontier #7605.
- **Negative control.** The primal engine cannot find this drop: on #7601, dropping 902@595 directly has no clean
  repair (K = 211, rank test fails). It is a V-side-origin edit.

Caveats:

- The drop removes one owned observation, the public→owned write 1532 += 2·w902, as 134@595 did in #7601.
- This word has not had an independent audit of owned-observation legality, so we make **no κ claim** for it.

**[S] Scale.** Single token-settled drops are worth about +0.008% each. In our census only a handful have rank 0, so
this is a small layer of about 10 D0 per call, not a mass mechanism.

## D. Checkers

### D1. `accx.py` + `fastreplay.py`: admissibility against a base

```
python3 accx.py BASE NEW [--caller CALLER] [--allow-owned-reframe]
```

The checks:

1. The owned, live, ports and hosted blocks are the same. Extra helpers may be appended.
2. The replay is clean: frames, exits and owned lifetimes all check.
3. Every base final row is unchanged.
4. Mains keep their initial and final frames.
5. Helpers end as the identity row, owned rows end empty, and every helper strictly ascends.
6. MOVE legality holds.
7. The owned MOVEs are the same as the base's.

Then it prints both prices and the κ ratio. `fastreplay.py` replays the N × 4 projection row·R mod 2^61 − 1 instead
of the full row matrix. A nonzero row difference vanishes with probability 2^−244, and every flagged register is
re-checked by an exact Fraction replay of its backward slice. So **FAIL is exact-confirmed and PASS is
randomised-exact**.

Results [C]:

- #7546 against itself passes in about 1 s; the exact accx2 took 14 s.
- #7601 passes with GAIN.
- One corrupted ADD coefficient fails, and the exact re-check confirms the differing row.
- One reversed public MOVE fails.

### D2. `lossless.py`: law DUAL

**[P] The law.** While the live rows span Qⁿ, the relation space Λ = {λ : Σ λ_r row_r = 0} over live registers has
dimension equal to the number of live owned registers. Ops act on Λ contragrediently:

- `ADD d += q·s` acts as λ_s −= q·λ_d.
- `INIT o` adds e_o to Λ.
- `CLEAR o` is lossless iff some λ ∈ Λ has λ_o ≠ 0; then Λ shrinks to {λ_o = 0}.

So one forward pass mod p finds every lossy CLEAR. `culprit_chain` names the read that killed the coordinate.

```
python3 lossless.py WORD.json.gz
```

Results [C]:

- #7546, #7601 and the dual each have 0 lossy CLEARs.
- Deleting one owned→public write-back in #7546 makes a CLEAR lossy, and it is found.
- On 400 random programs the law agrees with exact Fraction ranks (141 of them have a lossy CLEAR).

### D3. `nativeplan.py`: the helper plan

```
python3 nativeplan.py WORD.json.gz
```

It extracts the helper layer as a plan: routes and stays; every helper event typed as pickup, delivery, relay or
scale; meetings; requirement blocks linked to their deliveries; exact π-states at every stay entry and exit; and the
requirement-space basis. `recost(plan)` re-costs the helper layer from routes alone, and `reemit_check` regenerates
every helper event from the plan.

Results on #7546 [C]:

- 1,101 helpers, 3,427 interior stops, 2,682 requirement blocks, 36,299 meetings, and state basis rank 253.
- The recost is **9,975.447669**, the same from routes and from stays.
- All 70,714 helper events are re-emitted identically.
- Negative control: one tampered plan coefficient breaks the re-emission check.

### D4. `validate.py`: one command

```
python3 validate.py BASE NEW
```

It runs accx, then lossless, then the repository's `compare_recursive_invoices.py` (BASE → NEW) and
`evaluate_recursive_power.py` (NEW against the empty invoice) at C just below and just above NEW's certified κ.
It prints a summary table, and the exit code is 0 iff every step passes.

Results [C]:

- On #7601: OVERALL PASS. The repository tools give `uniformly_better` and place the crossing in
  (0.0036490213053, 0.0036490213054), as in #7601's own certificate.
- A corrupted word gives OVERALL FAIL.

## E. Pricing models

### E1. `kformula.py`: κ as a function of the stage count k

The closed-form caller C(k) has two arms ⌊k/2⌋ | ⌈k/2⌉, 2 hubs and grow 2, with g = h − 1 = 8. Per port:

- **Targets.** 2·T[gj+1] for each arm role, and 2·T[gk+1] for the hubs.
- **Paid.** 2·P[gj] for the interior arm idles.
- **Type A (96 ports).** 4·P[g] + 4·P[1].
- **Type B (8 ports).** 2k·P[g] + 4·P[g+1].

The invoice is Invoice(k) = C(k) + k·N, where N is a word's native invoice.

```
python3 kformula.py 12 16 17 18 24
```

Results:

- **[C] C(17) is the #7113 caller.** C(17) equals the #7113 caller invoice (T and P), and C(17) × the #7546 native
  prices to κ(#7546). C(16) differs.
- **[P, C] S(k) = 96k − 208 = 2k(v − c) − ρv** (v = 104, c = 56, ρ = 2), checked for k = 4..64. Per port, arm field j
  and idle j cancel their gj parts: an A port gives 34k − 2, a B port 18k − 2, and the native gives −3,312 per call.
- **[P, C] The D0 slope.** D0(k)/104 = β k ln k + α k + O(ln k), with β = 2(2h − 1) = 34. Measured from
  k = 1000, 2000: 33.976. The ln k comes from the hubs (degree k) and arm tops (degree k/2): they carry each stage's
  2(h − 1) main mass at rank about (h − 1)k.
- **[C] The exact sweep.** κ(k) peaks at k = 17 and is strictly unimodal on 6..40: κ(16) = 0.0036481937 and
  κ(18) = 0.0036477620.
- **[P, C] The first-order law.** κ(k) ≈ S/D0 = (ε − ρ/k)/(β ln k + α) with ε = 2(1 − c/v) = 12/13. At k = 17,
  κ/(S/D0) = 1.0075. With α = 124.913 the formula is within 1% of the exact κ.
- **[P, C] The optimum.** Stationarity gives **κ* = ρ/(βk*) = 1/((2h − 1)k*)**. Here γ = 1 + α/β + ln(ρ/ε) = 5.4471
  and u* = −W₋₁(−e^−γ), so k* = 16.15 and κ* = 0.003641. The exact family optimum is k = 17.
- **[P] No positive limit.** κ(k) ~ ε/(β ln k) → 0: every nested two-arm root decays like 1/ln k.

### E2. `layout_price.py` and `cap_check.py`: caller layouts

These tools come from CALLEROPEN, an outside-session lane of DreamingOfClouds'.

**`layout_price.py` [C-param]** prices a ρ = 2 mask layout from role masks and per-boundary line caps.

- Ledger: T = Σ T[8·deg + 1]. Idle incidences at stage k are |Z_k| − 2. There are n + 2 − 2L thin QUERYs, absorbed
  as IDLE_ODD.
- Lines continue the oldest first, up to the caps.
- It prices against three what-if readings of the #7546 native:
  - *twins deleted*: the hosted main moves removed from the paid histogram. This is a ceiling.
  - *shadows*: the hosted block priced as helpers.
  - *shadows + 2 relays*.
- These are prices of hypothetical callers with hypothetical natives, not words.

Results:

- **[C-param]** Model B reproduces the built B caller's readings: 1.0950 / 1.0031 / 0.9773 (κ ratios against #7546).
- **[C-param]** Uncapped lines give the unreachable reference 1.8950 / 1.6368 / 1.5695.

**`cap_check.py` [C]** works on the built #7113 B program. It computes end-referred x and y spans per call mod p, at
q₀ = 1 and q₀ = i, and checks:

- **Lemma C.** The crossing cap at boundary k|k+1 is |S| − rank(Y_k, Y_{k+1} | S), with S = Z_k ∩ Z_{k+1}.
- **The Floor lemma.** rank(X of the arm up to k, plus the hub vectors) = |Z_k|.

Results [C]:

- rank = 4 at all 15 non-centre boundaries, at both q₀ = 1 and q₀ = i.
- The Floor lemma holds with equality at every non-centre call.

---

## What is not included, and overlap with earlier packages

- **Excluded as work in progress.** The network-compiler route (NETC2–NETC6 and the REBUILDKIT netc planners), and
  `floor_report.py`, which reads NETC2 plans. Nothing from that route is claimed.
- **Excluded as not self-contained.**
  - The RES-LAYER sensitivity sweep, which executes another lane's script on a composite W6805 model.
  - The TOY5 Pocket-Lemma checker, which needs CP-SAT, unavailable in generic CI.
- **Already shipped in #7606** (`research/p104-odd-unit-per-grading`):
  - The Cut Lemma checker on real words (WEBS `cutcheck.py`, shipped there as `cuts.py`).
  - The CLONEAUDIT Rank-lemma toy, in `walls.py`.
  - The TOY4 F₂³ question, recorded there as in progress.
- **#6170** (`research/p104-designer-toolkit-v2`) is our earlier toolkit for the #6030 word lineage and its verifier
  profiles. This package targets the hosted #7546 format and does not replace it.
- **#7601**'s `check.py` certifies one word. `tokdrop.py` is the engine that found and built that word.

## Open next questions

1. **More dual drops.**
   - *Question.* Do the untried non-owned stays of the dual (about 4,500), or the dual of the current frontier word,
     hold more rank-0 drops?
   - *First step.* Run `tokdrop.py scan` over the dual census in shards, then `build_exact` each hit and map it back.
2. **Exact tier-A settlements.**
   - *Question.* Can the tier-A-only settlements be made exact?
   - *The candidates.* 624@117, 627@117 and 490@594 on the primal; 438@245, 271@306 and 1289@117 on the dual.
     Together they are worth up to about 7.7 D0 per call.
   - *First step.* Give the exact premix solve the V post-op freedom.
3. **Bounded headers.**
   - *Question.* Is there a caller whose stages meet in bounded headers stitched by tree nodes, so that
     D_caller = O(k) and κ(k) has a positive limit?
   - *First step.* Price a toy 8-stage version with `layout_price.py` and check its crossings with `cap_check.py`.

## Credits

The tools are ours (DreamingOfClouds with Claude Opus 5.5, via Claude Code); CALLEROPEN is an outside-session lane
of DreamingOfClouds'. Credits for the data:

- ToikY for the #7546 word.
- Rohan Arun for the #7113 caller.
- Clear1nsight, ToikY and the P104 price and replay lineage for the conventions these tools follow.

See [NOTICE](NOTICE).
