# P104 banked-circuit toolkit

This package holds the exact pricer, circuit certifier, word screens, circuit move screens and builders that DreamingOfClouds used for #7705 and #7712. They are packaged so that anyone can price, check or extend a P104 word or banked circuit. The package makes **no κ claim**. Every number in the self-tests reproduces a published result.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/p104-banked-circuit-toolkit
```

Run this from the repository root. It uses the standard library only and takes about four minutes on one core. To run the parts on their own, in the package:

```sh
python3.12 -I -B tests/selftest.py            # A-F below, about 3 minutes
python3.12 -I -B tests/selftest.py --quick    # A-D, about 10 s (--circuits: A, E, F)
python3.12 -I -B note-7717/check.py           # the separate note at the end, about 40 s
```

| Self-test | What it checks |
| --- | --- |
| **A** | Every package file matches `ASSETS.json`. The #7700 cf6a word matches its canonical SHA-256 (`ae62d5d8…1472`). |
| **B** | PRICEKIT controls: a closed-form root (T = {8:1}, P = {1:2} crosses at 2/3), `NO_CROSSING` when S ≤ 0, refusal of negative invoices, large roots. |
| **C** | PRICEKIT on the #7700 word and its 16-call caller reproduces #7700's crossing, **0.00372934317806**. |
| **D** | `wordcheck.py` passes the #7700 word (mod-p rows, nesting, zero-join). It catches a one-coefficient mutant and a reversed public MOVE. |
| **E** | `certify.py` re-certifies the published #7712 circuit: crossing **0.0037427697512569**, S = 1,328, 101,488 paid jobs, with Gaussian column checks. A circuit with one corrupted coefficient is rejected. |
| **F** | `hubbuild.py` applies two recorded hub reroutes to the #7712 circuit, and `certify.py` accepts the result. The paid change per native is {2:+2, 3:−2, 6:−2, 7:+2}. This is a builder regression only. Its crossing (0.0037430938517) is below the current frontier and is not claimed. |

## Tools (`tools/`)

The stdlib tools need only Python 3.12. Of the screens, `relay.py` is stdlib too; the other screens need numpy and are not replayed in CI.

| Tool | Needs | What it does |
| --- | --- | --- |
| `pricekit.py` | stdlib | The exact Theorem-K pricer. It builds the invoice (T and P histograms) from a caller and a native (`native_from_word`, `native_from_hist`, `native_param`). κ is the unique root of F(t) = Σ(T−P)·r^(1−t), enclosed by certified Decimal bisection with a uniqueness check. It also gives S, D0 and Dk, the ledger check `check_slots`, the parametric caller `caller_from_roots`, exact dead-register pruning (`drop_registers`, `verify_drop`) and the ordinary readings. `pricekit.py CALLER WORD` prints a one-line citation. |
| `wordcheck.py` | stdlib | Fast word screens. It runs a sparse replay mod 2^61−1 and compares the final public rows with a base word. It also checks MOVE nesting and runs an exact-zero join census (exact and mod-p versions), with an optional PRICEKIT κ ratio. The 154,768-event #7700 word takes about 3 s. `wordcheck.py [--base B] [--caller C] WORD` |
| `bank.py` | stdlib | Banked-circuit core: `fold` turns a word into a circuit of rational forms over paid tokens and inputs. It also provides `transpose`, `schedule` (locality and acyclicity), `pivot`/`apply` (the #7674 transfer algebra), `hist`, `price_net`, and `load_circuit`/`dump_circuit` (this package's JSON format, or a published banked graph). |
| `exval.py`, `fsolve.py` | stdlib | Exact rational node values, and an exact sparse solve whose tokens are chosen mod p and then solved in Fractions. |
| `nest.py`, `phys.py`, `gauss.py` | stdlib | GF(2) chart nesting and transfer rank. `phys.py` computes the symplectic rank of T_b·T_a⁻¹. `gauss.py` runs an exact Gaussian-dyadic state simulation of a chart transfer on all 512 columns. |
| `certify.py` | stdlib | Independent check of a circuit against a word. It checks locality and acyclicity, then that every edge is nested, has positive rank and has symplectic rank equal to the dimension difference. With `--columns` it adds Gaussian columns. It then checks exact outputs: mains equal the word and helpers are the identity, or, with `--reference`, every output equals a reference circuit. Last, it prices the circuit (`--claim K` gates the lower end). `certify.py WORD CIRCUIT [--caller C] [--columns] [--claim K]` |
| `hubbuild.py` | stdlib (numpy optional) | Exact builder for hub reroutes, the generalised #7682 move. Edge e1: P→Q is re-destined to a hub R that Q already feeds, and e2: Q→T is re-sourced at R. Every receiver recovers its old value from local donors. Each hit must pass the schedule, nesting and exact terminal equality checks. Without numpy it uses the exact fallback, which sufficed for every hit used here. |
| `hub2.py` | numpy | Mod-p screen for hub reroutes over all (Q, P) groups, forward or transposed. `BANK_Q=<chart>` restricts it to one chart. Example: on #7712, `BANK_Q=551 … transpose` finds the first hit of self-test F in about 5 s. |
| `split.py`, `splitbuild.py` | numpy | Screen and exact builder for causal helper splits, the generalised #7697 move used in #7712. A retired role exits early at a cut chart C, and a fresh role carries the remainder; its target rank R splits as d + (R − d). |
| `search2.py`, `search3.py`, `stack.py` | numpy | The #7674-class pivot screen (a single paid token dropped and its reader re-sourced from a lower chart), its batched form, and an exact greedy stacker. |
| `relay.py` | stdlib | Pure relay scan: a paid t: A→B whose only reader is j: B→C with form {t: c} contracts to A→C when the charts are nested. |

The screens are filters. Only the exact builders and `certify.py` decide. Coefficients are exact Fractions, and mod-p arithmetic is used only to choose candidates. `BANK_CALLER` overrides the caller used by `price_net`, and `BANK_KAPPA` sets the κ used to score screen candidates.

## Data

- `source/WORD.json.gz`, `source/CALLER.json.gz`: the #7700 cf6a word and its 16-call caller (SYLforge), as published with #7704 and #7712.
- `data/CIRCUIT-7712.json.gz`: the published #7712 circuit.
- `data/HUBS-ON-7712.json`: the two hub hits used by self-test F.

## Note: a small stacked tweak on #7717

These tools also found a small tweak on aliromman's #7717 circuit. Two transposed hub reroutes (chart 551 to hub 278, chart 545 to hub 488; ranks 6 + 3 → 7 + 2) build exactly on #7717's published graph. On #7717's own published 16-call invoice, plus the paid change {2:+2, 3:−2, 6:−2, 7:+2} per native, the crossing is **0.00376346450049**. That is +0.0087% over #7717's 0.00376313686061.

**This is a note, not a certified result.** `certify.py` cannot check #7717's helper-removal boundary: its graph has 1,470 public roles, against 1,504 for the cf6a word. So the only output check is exact rational equality of all 1,470 outputs with #7717's own graph. The note also inherits every #7717 premise and its physical and compiler bill unchanged. Its bank-cost terms are not recounted.

`note-7717/check.py` does the following:

- Authenticates the vendored graph against #7717's application receipt.
- Rebuilds both reroutes with `hubbuild.py` and checks them against `note-7717/REROUTES.json`, which holds the 4 moved edges and 16 changed forms.
- Checks locality, the schedule, nesting and symplectic rank.
- Proves exact output equality with the graph.
- Reproduces #7717's bracket before adding the paid change.

## Open next questions

- Can the hub-reroute and split screens be made stdlib-only so that CI replays them? Start by porting `hub2.kernel` and `split.left_kernel` to the sparse mod-p rows of `wordcheck.py`, gated against the numpy versions on #7712.
- Can `certify.py` check a circuit whose helper boundary differs from its source word, as in #7717? Start by reading #7713's removal map as data and adding a `--boundary` option.

## Limits

- No κ claim. Self-test F and the #7717 note are regressions on published circuits.
- `hub2.py`, `split.py`, `splitbuild.py`, `search2.py`, `search3.py` and `stack.py` need numpy and are not replayed here. Their output is only ever a candidate list for the exact builders.
- The REBUILDKIT helper-layer compiler, its incremental scorer and its C planner kernels are not included. They depend on unpublished planner state.

## Credit

The tools, tests and the #7717 note are by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. They were written new; predecessor packages were read as data only.

The moves they implement are due to the following authors:

- aliromman: the banked-transfer circuit and pivots (#7674), the relay-cut recodings (#7708), and the helper-quotient, fixed-graph and physical-application work of #7713, #7716 and #7717, whose graph and invoice are vendored in `note-7717/`.
- Clear1nsight: the role-230 reroute (#7682), the chart-595 split (#7697) and the role-1256 relay (#7704).
- SYLforge: the cf6a word and caller (#7700).

The predecessor notices are in `credits/`.
