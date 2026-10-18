# Frame toolkit for gauge44/k8 local words

**Tooling only; no new κ.** This package collects the tools used to find, compose and admit width-neutral changes to
gauge44-lineage local words (X4, U8, the k8 leaver words and their slot, end and entrance variants):

- a **frame solver** for a fixed scalar program, with two per-instance certificates (see [What is certified](#what-is-certified)):
  exact optimality for its floored integer surrogate weights, and a rigorous rational interval for the true per-call moment
  at the chosen endpoint b;
- a **pricing harness** for B-phase delivery rewrites: the auditor's static program rules, the B+tail map mod p, an unchanged
  derived compensation, then frames; every reported gain and every returned word is re-checked by the unchanged `audit_local.py`;
- **searches**: read-fusion candidates, the fusion + enlarged-reader repair sweep, joint triangle-hybrid candidates;
- **composition**: slot-recipe splitting, slot/fusion composition, and interface transplant onto a newer word;
- an **exact κ pricer** for any replica count and owner map;
- **admission drivers** that reuse unchanged upstream packages: native local chain, PLAN/SPEC rebinding, discovery → unpin →
  freeze, T16 discovery, and negative controls.

Pure Python 3.11+ with NumPy, on Linux, macOS and Windows (see Revision 3). No C++ compiler, Boost, LP/MILP solver or
network access is needed. Upstream sources are
imported unchanged from this checkout through `paths.py`; set `IMB_ROOT` to use another checkout.

## Check the installation

```sh
python -B research/exact-frame-toolkit/selftest.py          # about 2 minutes; --quick (about 30 s) skips the search and composition steps
python -B research/exact-frame-toolkit/portability.py       # the same selftest through the Windows code paths, on any OS
```

Do not run the toolkit with `-O` or `PYTHONOPTIMIZE`: its assert statements are checks, so it refuses to start.

It uses only files already on main: the seven-slot k8 word and the pre-slot word from the #1094/#1042 replay archives,
#1094's replay receipt (`research/community-frontier1094-audit/REPLAY.json`) and #942's checkpoint
(`certificates/checkpoints/frontier942.json` and the `research/community-frontier942-audit/ASSEMBLY.json` it names).
Expected final line: `SELFTEST PASS`. The steps are:

| Check | Expected |
|---|---|
| `kappa.py` on #1094's complex profile (T16) and #942's (T37) | the selected and checkpoint κ, exactly |
| surrogate frame optimum of the seven-slot word `c2b29430` | its published profile `{1:2412,2:418,3:432,4:142,5:82}` (+8·H8 centres), integer certificate |
| true-moment interval of the seven-slot word at b | published frames within 1.5e-11 units of the minimum over the frame model (rigorous); the surrogate alone bounds this only by 1512 units |
| control: a deliberately worse assignment | interval width = its exact true excess (6763.29 units) |
| control: exact dual with multipliers of magnitude 2^62–2^90, then one NaN | still a lower bound in Python integers; NaN rejected |
| control: a port written at the end of B and undone in the first early tail | passes the B+tail map screen; harness `compensation-changed`; `audit_local` endpoint failure |
| each of #1018's seven slots on the pre-slot word `db2c7cfb` | −1788 surrogate units each, all seven −12516; every one a certified true gain at b (−1784.83 true units each, −12493.80 together) |
| source-holder fusion + full exchange at the X=439 and X=444 slot sites | −3957 each |
| five slots + both fusions | −16854, `audit_local` PASS, unchanged interfaces, κ 0.001672756914849856 on #1094's owners |

## Modules

| Module | Purpose |
|---|---|
| `frames.py` | Frame solver. Event graph per register chain; L/U domain propagation; chain dual decomposition with an exact integer duality gap; exact elimination on small components. `Graph(..., tail_mutable, caps, cut_equality)`, `optimal_frames(word, Costs(b), graph=g, interval=True)`, `moment_interval(g, costs, assign)`. |
| `word.py` | `inline(word)` (frames.Graph input) and `recount(word)` (the lineage's independent paid-profile recount). |
| `model.py` | `cone_caps(word)`: the inverse-row and dirt-column cones of `audit_local.py` as end-of-B frame caps. |
| `writeback.py` | `write_back(word, graph, assignment)`; `audit(word)` runs the unchanged `audit_local.py`. |
| `exchange.py` | BRoute's read-set exchange family (copy pairs, movable reads, moves, exact B map mod p). `python -B exchange.py` regenerates the published SW4 word. |
| `harness.py` | `Pricer(word, interval=False).price(edits)`: compile build_tri-style edits (B deletes/inserts, early tails, FULL prepends); static program rules; B+tail+prepend map mod p; unchanged derived compensation; recomputed cone caps; frames; `audit_local` on every negative delta and every returned word. Returns the surrogate delta and profile (with `interval=True` also `realized_delta_units`, `max_gain_units`, `gain_certified`). |
| `fusion.py`, `joint.py` | Fusion candidates (a target's two reads merged through a holder donation); joint triangle-hybrid candidates per copy pair. |
| `repair.py` | Multiprocess sweep: every fusion with single/pair swap repairs and the full exchange of its copy pair, priced by the harness (`--interval` bounds the true gain of every non-gain candidate). |
| `sites.py` | The repair step on chosen `(t, A, H)` fusions. |
| `slots.py` | Split a slot recipe into instances and price each alone and together. |
| `compose.py` | Pre-slot word + slots except chosen sites + source-holder fusions at those sites, priced and audited. |
| `transplant.py` | Put a target word's entrances/ends onto a donor scalar program, re-solve all frames, audit, price on the target's owners. |
| `kappa.py` | Exact κ (moment root on the 1e-24 grid, retained 47-constraint outer assembly, PR589 bit) for any T. |
| `baseline.py` | Audit a word, compare its surrogate frame optimum with its published profile, print its true-moment interval. |
| `native.py` | PR635's native local chain (transport audit, ledgers, local replay, wrappers, phases) for a FULL-WORD. |
| `rebind.py`, `unpin.py`, `t16_discover.py` | Rebind an owner package's PLAN to a new local with unchanged widths; remove re-derived SPEC keys; T16 discovery run. |
| `controls.py` | Per-site negative controls (drop restore, drop/flip donation, keep fused read, drop both), judged by `audit_local.py`. |
| `compat.py` | Platform-dependent pieces: the per-pricing wall-clock deadline, peak memory, the sweep's process start method, the subprocess environment, and the `-O` refusal. |
| `portability.py` | Runs the Windows code paths of `compat.py` on any OS, then the selftest in the same process. |

## Typical workflow

**1. Price a change.** Cost deltas are surrogate units: the per-rank moment lower bounds at an endpoint `b` near the frontier
root (`harness.DEFAULT_B`, or `IMB_B`), floored on a 2^-40 grid; negative is better. With `Pricer(..., interval=True)` the
same call also returns the true realized delta at b and a rigorous bound on any true gain. For a width-neutral change on a
fixed owner map, κ is then computed exactly from the profile, never from cost units:

```sh
python -B research/exact-frame-toolkit/kappa.py --local '{"1":2406,"2":424,"3":428,"4":146,"5":80,"8":8}' \
  --calls 144 --T 16 --idle '{"1":2276,"3":377,"7":7,"48":4866}'
```

**2. Search.** `python -B repair.py WORD.json.gz OUT.json --workers 6`. On the pre-slot k8 word this sweeps 2405 fusions in
about 6 minutes on 6 workers; the only negative surrogate deltas are the two sites above. With `--interval` (about 8
minutes), no other priced candidate can gain more than 3.3e-11 units at b (`REVISION2-REGRESSION.json`). Revision 1
also listed nine neutral fusions as feasible whose programs `audit_local` rejects ("non-target reads target"); the
static rule screen now rejects them. Each pricing has a SIGALRM timeout (`--timeout`); workers are recycled
(`--max-tasks-per-child`) to bound memory.

**3. Compose and transplant.** `compose.py PRE.json.gz OUT/ --reference SEVEN.json.gz --host CALLS:T:IDLE` builds the
five-slot + two-fusion word. `transplant.py DONOR TARGET REF OUT --calls --T --idle --target-kappa` moves a newer word's
entrances and ends (for example #1148's) onto it after checking that the target keeps REF's scalar program.

**4. Admit, in increasing strength.**
1. `writeback.audit` / `audit_local.py`: exact forward and dual endpoints, frames, entrances, cones.
2. `native.py WORD OUT/`: the five native stages; the output `local/` is a provider directory.
3. Unchanged start/end frames: any owner map of the base word applies (`transplant.py` and `compose.py` report this).
4. Strict owner admission with the base package's own engines:
   `rebind.py SRC_PKG LOCAL OUT_PKG --T 8` (or `--plan/--spec` for other layouts) → the package's discovery run
   (`verify_global.py --discover`, `t16_discover.py`, or a package's `--discover` flag) → `unpin.py SPEC DISCOVERY` →
   the package's `freeze_spec.py` → the unchanged strict verifier. `controls.py` adds the mutation controls.

## What is certified

Each solve proves two separate statements, and only for its own instance (no general optimality claim rests on the selftest):

1. **Surrogate optimality.** The weights are `c_r = floor(2^40 · lo_r(b))`, where `lo_r(b)` is the engines' outward lower
   bound of the per-child moment term `T_r(b) = r (m/r)^b / (mW) + 32 m^(1+b) / (10^16 W)`. `certified` means the integer
   weak-duality bound equals the primal for these floored weights (one cost unit = 2^-40 of the per-call moment). Because
   every jump carries a rounding error in [0, 1) unit, this alone bounds the true suboptimality only by the number of
   jumps (1512 units on the seven-slot word).
2. **True-moment interval at b** (`interval=True`, `moment_interval`). The lower end is a Lagrangian bound (or exact
   elimination on small components) with lower weights `floor(2^224 · (lo_r − λ r))`, evaluated entirely in Python integers,
   plus the constant `λ · (total rank)`: along every register chain the ranks telescope to dim(end) − dim(start), so the shift
   changes every assignment by the same amount. The upper end is the engines' upper bound of the returned assignment's
   moment. On the two selftest words the width is 1.5e-11 and 1.9e-11 units. A comparison is decided only when its
   interval excludes the other side: `gain_certified` for a realized gain, `max_gain_units` for how much any assignment of
   a candidate program could gain. Gaps are computed, never assumed.

Not certified: the global recursive moment root or κ (nonlinear in the whole profile; always recomputed by `kappa.py` and the
package chain), the ordering at an endpoint other than the stated b, minimality outside the frame model below, and exact
optimality for the irrational weights `T_r(b)` themselves (the interval width is never exactly zero).

**Numeric conversions.** Float64 arrays drive only the dual sweeps and the greedy decode. `Costs` checks every surrogate
weight below 2^53 before building its float image. Every bound, primal value, certificate and interval is evaluated from the
integer weight tables. Float multipliers are converted exactly (`Fraction(float)`) after a finiteness check. The previous
revision rounded float unaries and multipliers and cast them to int64 without range checks. At these magnitudes (weights
below 2^25) that was exact, but nothing checked it.

**Surrogate and true deltas.** Surrogate deltas of two optimal assignments differ from the true deltas by less than one unit
per changed jump: a #1018 slot is −1788 surrogate and −1784.83 true units, and all seven slots are −12516 and −12493.80. A search
that reports no negative surrogate delta therefore leaves gains smaller than the rounding of the compared profiles open
unless it runs with intervals.

## Model and pitfalls

- The solver models monotone register chains, fixed starts/ends, target hyperplane caps, cut equality (centre frames and
  target levels), mutable early tails, and the final helper cones as caps. Centre descents (8·H8) are constant and not
  modelled; add them back when pricing.
- Cone caps depend only on the prefix scalar map and the end frames, so `Pricer.price` recomputes them per candidate.
- The audited program is precondition + compensation + A + cut + B + tail + rest, and the compensation is derived from the
  A+cut+B map. A gate that writes a port register in B and is undone in an early tail leaves the B+tail map unchanged but
  changes the compensation. The previous revision's screen (B+tail map only) priced such programs as `ok`. It also did not
  apply the auditor's static rules. The harness now rejects both kinds of program (`compensation-changed`, `rule:...`) and
  audits every negative delta. Admission never relied on the screen: `audit_local` and the package chains check the whole
  program exactly. The gaps therefore could not admit a false construction; they could make a search list an invalid
  program as an `ok` candidate.
- `freeze_spec.py` rejects re-derived keys that differ from pinned ones; run `unpin.py` between discovery and freezing.
- `emit_allcold.py` reads `SPEC.data.plan_sha256` directly, so the PLAN pin must be updated before discovery (`rebind.py` does).
- `evidence/local` in the gauge44 T8/T16 packages is historical #645 evidence (R=492), not the package's word; take k8 words
  from the replay archives or the constructors.
- Δκ/κ ≈ −ΔS/S with S = Σ n_r r ln(73/r); one cost unit of per-call local improvement is about 2.2e-11 in κ at these sizes (T8–T37).
  Always confirm with `kappa.py` and then with the package chain.

## Scope

These are finite search and admission tools. A candidate is only a construction after the unchanged package chain admits
it. The inherited all-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape,
analytic-transfer and bit H1–H5 assumptions remain; nothing here is a formal proof of the multiplication theorem.
See [NOTICE.md](NOTICE.md) for sources and credit.

## Revision 2 (2026-10-14)

This revision answers the maintainer's review continuation point on #1186: qualify the optimality claims or supply an
interval-separation proof, and certify bounds before float64/int64 conversion. It also fixes the harness screen gap described
above, which turned up during a later pivot search on #1319's words. The changes:

- the true-moment interval (`frames.moment_interval`);
- the exact integer dual path and checked float image;
- the harness's static rules, compensation check and `audit_local` re-check;
- the qualified wording;
- the new selftest controls.

All previous selftest values reproduce unchanged. A side-by-side run of `repair.py` on the pre-slot word with both revisions
is recorded in `REVISION2-REGRESSION.json`. It finds the same two gains and the same 3763 evaluations, and the nine fusions
that only revision 1 counts as feasible are all programs that `audit_local` rejects.

## Revision 3 (2026-10-14): Windows

woklerx's independent audit of revision 2 could not run the selftest on Windows, because `harness.py` imported the
Unix-only `resource` module (and its per-pricing timeout used SIGALRM, which Windows also lacks). `compat.py` now holds
the platform-dependent pieces:

- **Deadline.** POSIX keeps SIGALRM. Elsewhere a watchdog thread interrupts the main thread and the interrupt becomes the
  same `Timeout`; a real Ctrl+C still raises KeyboardInterrupt. The watchdog acts a few milliseconds late, which only
  matters for deadlines far below the default 90 s.
- **Peak memory.** The 6 GiB worker-recycle flag (`rss_exit`) now reads `ru_maxrss` in the right unit on each POSIX system;
  on Linux it used to compare KiB as if they were bytes, so it never fired. Windows has no `resource` module and skips the
  flag; `--max-tasks-per-child` still recycles the workers there.
- **Workers.** `repair.py` uses fork where available, else spawn (`EFT_START_METHOD` overrides).
- **Text files and subprocesses.** UTF-8 everywhere, LF line endings for the JSON outputs (so outputs are byte-identical
  across systems), and `audit_local.py`/`compose.py` run in UTF-8 mode without `PYTHONOPTIMIZE`.
- **No `-O`.** The asserts in `kappa.py` (the 47 outer constraints), `word.py` and the archive pins are checks, so importing
  the toolkit under `-O` raises an error instead of silently skipping them.

On a GitHub Actions Windows runner (Windows Server 2025, Python 3.12.10, NumPy 2.5.4) the full selftest and
`portability.py` pass and `-O` is refused. The spawn-mode `repair.py --interval` sweep of the pre-slot word matches the
macOS sweep in all 2,405 records. It takes about 60 minutes on the runner's 4 CPUs, against 8 here.

`frames.py` is unchanged, so woklerx's audit of its elimination and dual routines still applies byte for byte. No search
result, price or certificate changes; see `PORTABILITY.json` for the checks of this revision.

## Open next questions

- **Re-certify published surrogate sweeps.** Several negative sweeps were run with revision 1's surrogate:
  - #1195 and #1337 (this author);
  - #1288 and #1338 (Wronskode);
  - #620 §9 (GamingPuzzled).

  For them, gains below the rounding of the compared profiles remain open. First step: `repair.py --interval` (or
  `Pricer(..., interval=True)`) on those words and families. Cost: about twice the runtime.
- **Root-consistent comparisons.** Deltas are taken at a fixed b near the root. Pricing at each owner map's own certified
  endpoint, as `transplant.py` already does, removes the b qualification; deciding a sign at the root itself needs the root
  bracket of `kappa.py`.
- **Model equivalence.** That `frames.Graph`'s feasible set equals `audit_local.py`'s frame constraints rests on
  construction plus the audit re-check of every returned word. A machine-checked equivalence would let surrogate or interval
  minima be quoted without that re-check. Blocker: the constraints are spread over the audit, cone caps and cut rules.
