# Independent join of the selected #4470 p16 invoice to its moment bill

**Independent verification; no new κ.** This covers the selected record,
[#4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470) (Cinna Davis / 1337isnot1337,
conditional κ = 60403/20000000 = 0.00302015). It joins two parts that were already independently
derived, the per-call local unit and the p16 controller word, into the complete target/paid histogram.
It then checks that histogram against the moment and tail inequalities at the selected κ, using a
different enclosure method. The verifier is separately written and imports no checker.

Base `cef4b52f2a59009865bf8eabde1be3f159063703`, priority revision 7.
Claim: [#1166 comment 19137480](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19137480).

## Coverage before this package

| Piece of #4470's changed ledger | Independent coverage |
| --- | --- |
| Local unit: helpers `{4:28, 7:7, 8:47, 9:326}`, paid `{1:2237, 2:388, 3:494, 4:147, 5:36, 8:8}` | #4504 frame audit (Mihir Srivastava), both orientations |
| p16 Laurent factorization and main/idle/thin charges | `research/pr4470-controller-replay` (Ryanson Jonathan) |
| Changed transport recipes | `research/pr4470-coverage-join` (Clear1nsight) |
| Root, tails, compiler and outer rows **on a hard-coded histogram** | #4478 (Ryanson Jonathan), whose `T`/`P` literals are "as printed in #4470" |
| **Complete p16 histogram = controller bill + 18 local units** | author code only (`joint-helper-lattice/verify.py`) |
| **Moment/tail inequalities on a source-derived histogram** | author code only |

The two bold rows are the gap. #4478 never reads `CONTROLLER.json` or the local unit.
`CONTROLLER.json`'s own `invoice` uses the older THREE-base unit (69,012 jobs). Only the
author's substitution step produced the 64,620-job histogram that everyone evaluates.

## Result

**A. Join (exact).** One pass over the 154 committed events gives the following. Full native calls sit
at exactly the 18 thick stages `{0, 32, 1, 3, …, 31}`: 2 forward and 16 backward. Paid query shears sit
at exactly the 15 thin stages. The 15 IDLE windows multiply only distinct thick stages. The 32 diagonal
outputs have central exponent ±1 and no thin-stage credit. The bill is charged as follows:

- each full call gets #4504's unit for its own orientation, plus one fresh copy of the 408 helpers;
- each query shear gets 112 rank-one jobs;
- each IDLE window gets 2·112 jobs of rank 8·|stages|;
- each diagonal output gets 112 targets of rank 1 + 8·|stages|.

The result is:

```text
targets {4:504, 7:126, 8:846, 9:5868, 17..65 step 8: 448 each, 73:224, 145:224}   10,928 fields, mass 239,886
paid    {1:41946, 2:6984, 3:8892, 4:2646, 5:648, 8:144, 16..64 step 8: 448 each, 72:224}  64,620 jobs, mass 239,134
```

The same histogram comes out of all six sources below, exactly:

1. this event-word join;
2. the #4440 closed form (PROOF.md §2, with no event word);
3. `RESULT.json`;
4. `NATIVE.json.gz`'s unit, times the call counts;
5. `CONTROLLER.json`'s embedded invoice, with the THREE-base unit replaced by the new one;
6. #4478's `T`/`P` literals (read with `ast`, never executed).

**B. Moment and tails (second method).** The verifier uses Python `decimal` at 60 digits with
directed rounding. It widens every correctly rounded `ln`/`exp` by 10⁻²⁰ relative, which is far
more than one ulp. This is a different method from the Fraction atanh/Taylor series used by #4470
and #4478. Let `T_t − P_t` be the raw surplus, with `t = 1 − saving`. The results:

| Check | Enclosure | Stated limit |
| --- | --- | --- |
| raw surplus at κ = 0.00302015 | ≥ 0.00395201766 | > 0 |
| raw surplus at tested 0.003020155 | ≥ 0.00271523544 | > 0 |
| root bracket (0.0030201659770, 0.0030201659771) | ≥ 3.86e-9 / ≤ −2.09e-8 | sign change |
| α = P_t/T_t | ≤ 0.999999988558808 | < 1 − 10⁻⁹ |
| γ = P_{t+1/5}/(20^{1/5} T_t) | ≤ 0.956176646498 | < 97/100 |
| δ = 21·10928/(20^{0.003020155} T_t) | ≤ 0.958284435309 | < 97/100 |

These agree with #4470's and #4478's printed values. **No discrepancy was found.**

**Sharpness (new observation).** The whole raw surplus at κ (0.00395) and at the tested saving
(0.00272) is **below the moment of one rank-one paid job** (1ᵗ = 1). The verifier asserts this.
Each of the following single-job edits flips the selected κ by itself:

- one extra rank-one paid job;
- one rank-one job promoted to rank two;
- one rank-9 helper demoted to rank 8.

The selected record is therefore correct only if the complete p16 invoice is exact at
single-job resolution. This is not a defect. It does mean an omitted charge of even one query,
copy or erase would invalidate κ = 0.00302015.

## Controls

The 15 controls below all reject, and the verifier fails if any one passes:

- **Moment controls:** one extra rank-one job; 1→2 promotion; 9→8 helper demotion; κ moved to the
  root's upper end; the #4447 local unit placed in the p16 word; the predecessor p17 invoice at κ.
- **Structural controls:** query shear dropped; query shear promoted to a full call; full call demoted
  to a query; one IDLE stage removed; a diagonal output credited with a thin stage; central exponent 0.
- **Binding controls:** one backward-unit job shifted; one helper rank lowered; tampered pinned bytes.

All 8 of 8 hand mutants of the verifier's sharp constants fail:

- job count; α limit; port count; κ; thin charge; idle line count; γ limit; and the root upper end
  moved below the root.

## Not covered

This package does not cover:

- the native word, phases or helper boundaries (#4504, the coverage join and the maintainer review cover these);
- the Laurent factorization (pr4470-controller-replay covers this);
- the compiler, BIT admission, the outer ledger rows and their parameters (#4478 covers these from printed parameters);
- the physical query/owned-stream protocol.

The cost model is taken as stated in #4440 PROOF.md §1–2 and is not re-derived:

- 112 ports;
- fresh block rank 8;
- one unit per full call;
- a query costs one rank-one job per port;
- idle costs 2·112 jobs of rank 8·|stages|;
- a main output has rank 1 + 8·|stages|.

The decimal enclosure assumes Python's documented correct rounding of `Decimal.ln`/`exp`, with
10²⁰-ulp slack. This is a finite certificate for one fixed histogram. It is not a theorem about
the multiplication algorithm and not a new κ.

## Reproduce

```sh
python3 scripts/research_package.py --package research/pr4470-invoice-join --check-only
python3.12 -B scripts/research_package.py --package research/pr4470-invoice-join
python3.12 -O -B research/pr4470-invoice-join/verify.py
python3.12 -I -W error -B research/pr4470-invoice-join/verify.py
```

The verifier prints `PASS_PR4470_INVOICE_JOIN` in under a second, using only the standard library.
`PROOF.md` states the charging rules and the enclosure argument.

## Open next questions

1. **Single-job completeness of the p16 invoice.** The surplus at κ is below one rank-one job, so is
   every paid operation of a thin query shear and an IDLE window charged exactly once?
   *First step:* enumerate one query shear's per-port copy/query/add/erase steps from #4440's protocol.
   Match each step to a histogram entry or to an explicit nonrecursive allowance.
2. **Stage-zero unit.** All 18 full calls, including stage 0 (multiplier F9·Q⁻¹), are charged the same
   #4504 unit, following #4440/#4470. *First step:* compare the stage-zero call's frame audit with the
   generic unit.

Structured versions are in `TASK.json`.

## Credit

- Construction and claim: Cinna Davis / 1337isnot1337 (#4470, #4440, #4441, #4447). zxv supplied the native/controller lineage.
- Local unit audit: Mihir Srivastava (#4504). Arithmetic audit and controller replay: Ryanson Jonathan (#4478, pr4470-controller-replay). Coverage join: Clear1nsight.
- Maintainer review: docs/research/pr-intake-evidence/pr4470/PROOF-REVIEW.md.

Prepared by JoyboyBrian with substantial assistance from Anthropic Claude (Claude Code, Opus 5.5).
This is not independent human or formal review. Apache-2.0.
