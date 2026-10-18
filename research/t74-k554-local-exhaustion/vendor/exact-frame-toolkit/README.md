# Exact frame toolkit for gauge44/k8 local words

**Tooling only; no new κ.** This package collects the tools used to find, compose and admit width-neutral changes to
gauge44-lineage local words (X4, U8, the k8 leaver words and their slot, end and entrance variants):

- an **exact frame solver** (minimum recursive moment over all frame annotations of a fixed scalar program, with an integer
  optimality certificate);
- an **exact pricing harness** for B-phase delivery rewrites (scalar exactness mod p, then exact frames);
- **searches**: read-fusion candidates, the fusion + enlarged-reader repair sweep, joint triangle-hybrid candidates;
- **composition**: slot-recipe splitting, slot/fusion composition, and interface transplant onto a newer word;
- an **exact κ pricer** for any replica count and owner map;
- **admission drivers** that reuse unchanged upstream packages: native local chain, PLAN/SPEC rebinding, discovery → unpin →
  freeze, T16 discovery, and negative controls.

Pure Python 3.11+ with NumPy. No C++ compiler, Boost, LP/MILP solver or network access is needed. Upstream sources are
imported unchanged from this checkout through `paths.py`; set `IMB_ROOT` to use another checkout.

## Check the installation

```sh
python -B research/exact-frame-toolkit/selftest.py          # about 30 s; --quick skips the search and composition steps
```

It uses only files already on main: the seven-slot k8 word and the pre-slot word from the #1094/#1042 replay archives,
#1094's replay receipt and #942's checkpoint. Expected final line: `SELFTEST PASS`. The steps are:

| Check | Expected |
|---|---|
| `kappa.py` on #1094's complex profile (T16) and #942's (T37) | the selected and checkpoint κ, exactly |
| exact frame optimum of the seven-slot word `c2b29430` | its published profile `{1:2412,2:418,3:432,4:142,5:82}` (+8·H8 centres) |
| each of #1018's seven slots on the pre-slot word `db2c7cfb` | −1788 cost units each; all seven −12516 |
| source-holder fusion + full exchange at the X=439 and X=444 slot sites | −3957 each |
| five slots + both fusions | −16854, `audit_local` PASS, unchanged interfaces, κ 0.001672756914849856 on #1094's owners |

## Modules

| Module | Purpose |
|---|---|
| `frames.py` | Exact frame solver. Event graph per register chain; L/U domain propagation; chain dual decomposition with integer duality gap; exact elimination on small components. `Graph(..., tail_mutable, caps, cut_equality)`, `optimal_frames(word, Costs(b), graph=g)`. |
| `word.py` | `inline(word)` (frames.Graph input) and `recount(word)` (the lineage's independent paid-profile recount). |
| `model.py` | `cone_caps(word)`: the inverse-row and dirt-column cones of `audit_local.py` as end-of-B frame caps. |
| `writeback.py` | `write_back(word, graph, assignment)`; `audit(word)` runs the unchanged `audit_local.py`. |
| `exchange.py` | BRoute's read-set exchange family (copy pairs, movable reads, moves, exact B map mod p). `python -B exchange.py` regenerates the published SW4 word. |
| `harness.py` | `Pricer(word).price(edits)`: compile build_tri-style edits (B deletes/inserts, early tails, FULL prepends), check the B+tail+prepend map mod p, recompute cone caps, solve frames exactly, return the cost delta and profile (and the word with `want_word=True`). |
| `fusion.py`, `joint.py` | Fusion candidates (a target's two reads merged through a holder donation); joint triangle-hybrid candidates per copy pair. |
| `repair.py` | Multiprocess sweep: every fusion with single/pair swap repairs and the full exchange of its copy pair, priced exactly. |
| `sites.py` | The repair step on chosen `(t, A, H)` fusions. |
| `slots.py` | Split a slot recipe into instances and price each alone and together. |
| `compose.py` | Pre-slot word + slots except chosen sites + source-holder fusions at those sites, priced and audited. |
| `transplant.py` | Put a target word's entrances/ends onto a donor scalar program, re-solve all frames, audit, price on the target's owners. |
| `kappa.py` | Exact κ (moment root on the 1e-24 grid, retained 47-constraint outer assembly, PR589 bit) for any T. |
| `baseline.py` | Audit a word and compare its exact frame optimum with its published profile. |
| `native.py` | PR635's native local chain (transport audit, ledgers, local replay, wrappers, phases) for a FULL-WORD. |
| `rebind.py`, `unpin.py`, `t16_discover.py` | Rebind an owner package's PLAN to a new local with unchanged widths; remove re-derived SPEC keys; T16 discovery run. |
| `controls.py` | Per-site negative controls (drop restore, drop/flip donation, keep fused read, drop both), judged by `audit_local.py`. |

## Typical workflow

**1. Price a change exactly.** Cost deltas use the per-rank moment lower bounds at an endpoint `b` near the frontier root
(`harness.DEFAULT_B`, or `IMB_B`); negative is better. For a width-neutral change on a fixed owner map, κ is then exact:

```sh
python -B research/exact-frame-toolkit/kappa.py --local '{"1":2406,"2":424,"3":428,"4":146,"5":80,"8":8}' \
  --calls 144 --T 16 --idle '{"1":2276,"3":377,"7":7,"48":4866}'
```

**2. Search.** `python -B repair.py WORD.json.gz OUT.json --workers 6`. On the pre-slot k8 word this sweeps 2405 fusions in
about 5 minutes on 6 workers and finds exactly the two sites above. Each pricing has a SIGALRM timeout (`--timeout`); workers
are recycled (`--max-tasks-per-child`) to bound memory.

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

## Model and pitfalls

- The solver models monotone register chains, fixed starts/ends, target hyperplane caps, cut equality (centre frames and
  target levels), mutable early tails, and the final helper cones as caps. Centre descents (8·H8) are constant and not
  modelled; add them back when pricing.
- Cone caps depend only on the prefix scalar map and the end frames, so `Pricer.price` recomputes them per candidate.
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
