# Direct small-integer JP8 accumulation

**Finite complex-supplier circuit construction; no new kappa.** Replace only
historical PR626 JP8 addition macros with reduced coefficients ±2 and ±3 by
repeated signed unit additions into the target, followed by the existing paid
coefficient-work clear. This saves **2,848 real-component primitives in each
orientation** without changing a macro boundary or introducing a register.

| Complete JP8 scalar projection | Accepted PR696 lowering | Candidate | Saved |
| --- | ---: | ---: | ---: |
| Forward | 200,380 | 197,532 | 2,848 |
| Backward / inverse transpose | 200,396 | 197,548 | 2,848 |

Each orientation replaces all **1,424** eligible macros: 1,343 of magnitude two
and 81 of magnitude three. This is a complete census of two frozen programs,
not a search for a better multiplication exponent. The result improves the
specified PR696 baseline; it does not claim the best scalar bill among all
pending lowerings or compositions.

## Reproduce

Python 3.11+ and the standard library, offline, from the repository root:

```sh
python3 -I -O -B research/jp8-direct-small-integers/verify.py
```

Expected:

```text
PASS_JP8_DIRECT_SMALL_INTEGERS macros=1424+1424 saved=2848/2848 columns=725 no_new_kappa
```

The command checks six input pins before loading the reference lowerer, executes
both complete primitive projections, recomputes the occurrence census and every
receipt field, and runs 13 rejection controls. It writes nothing. `--json`
prints the checked receipt. The development option `--write NEW_PATH` creates
a new receipt and refuses existing output. Focused tests:

```sh
python3 -I -O -B research/jp8-direct-small-integers/test_package.py
```

An additional full replay uses `Fraction` coefficients throughout, without
importing the primary interpreter, its row arithmetic or its local controls:

```sh
python3 -I -O -B research/jp8-direct-small-integers/recheck_fraction.py
```

Expected final line:
`PASS_JP8_FRACTION_RECHECK all_program_receipt_fields=equal no_new_kappa`.
This checks all 725 input columns and the entire register state at every one of
the 22,693 scalar macro boundaries in each orientation, recomputes every program
receipt field, and runs seven additional endpoint/prefix/cost mutation controls.
It shares the pinned programs, the two lowerers and the expected receipt with
the first checker; it is a second arithmetic implementation, not independent
human review. See `VALIDATION.md` for the repeated checks and publication pin.

`EXPECTED.json` is an exact certificate of the finite executions and counts,
including every changed event index, coefficient/frame/phase census, complete
primitive-stream digests, prefix metrics and unchanged paid profiles.
`SOURCES.json` records dependency heads, SHA-256 input pins and committed Git
blob identities. Gzip equality is on the entire decompressed payload; harmless
recompression is accepted.

## Circuit, proof and complete local cost

For distinct target T, source S and private work W, let q = sign*m, m in {2,3}.
Use m copies of `T += sign*S`, then `clear W`. After j updates the state is
`(T0 + j*sign*S0, S0, W0)`, by induction on j. Clearing W therefore gives
exactly `(T0 + q*S0, S0, 0)` for arbitrary incoming values, including dirty W.
The source is never written. Both signs and both scalar orientations use the
same argument. The real and imaginary components are executed separately.

| Per real component | PR696 | Candidate | Source reads, old → new |
| --- | ---: | ---: | ---: |
| m = 2 | copy, double, accumulate, clear: 4 | two additions, clear: 3 | 1 → 2 |
| m = 3 | copy, double, source-add, accumulate, clear: 5 | three additions, clear: 4 | 2 → 3 |

Every repeated source access is an explicitly charged addition; the final clear
remains even when W happens to be clean. There are no preparation, source
restoration, new helper, copy, frame transition or recursive-child instructions
in the replacement. Unchanged work outside these macros is recounted in full.
Savings are `2*(1343+81)=2848`, including both real components. Macro-source
reads rise **51,228 → 54,076** per orientation. All arithmetic operand reads
remain **207,138 forward / 207,154 backward**, because target/source reads
replace coefficient-work reads. These are instruction-access counts, not a
measurement of physical memory traffic or wall-clock speed.

The original macros, event order, frame IDs, helpers, copies and recursive
profile remain fixed. Each emitted primitive uses its enclosing macro's frame.
The inherited paid profile is
`{1:2512, 2:400, 3:448, 4:160, 5:70, 6:8, 8:8}`.
The historical controller's paid recurrence and outer assembly are not changed
or repriced. No saving in their exponents follows from this local scalar bill.
A production integration must bind the new lowering and rebuild the complete
physical invoice; this package does not silently replace that certificate.

## Prefix and precision argument

For any input vector and any norm, each intermediate target is the convex
combination

`T_j = (1-j/m)*T_0 + (j/m)*(T_0 + q*S_0)`.

Its norm is at most the larger target endpoint norm. Both endpoint values
occur in the old execution. The source stays fixed. Work retains its incoming
value until the paid clear; that value also occurs at the old entrance. Thus
the maximum over registers and prefixes cannot exceed the PR696 maximum.
This argument permits correlated inputs and does not assume sign cancellation
in a positive majorant. With a triangle envelope, the successive target bounds
are A+jB ≤ A+mB, exactly the old final target bound. No new prefix allocation
is needed.

All new operations are integral additions or clearing. Each intermediate row
stays on the common dyadic grid of the entrance target and source, both of
which are present in the old trace. This preserves the global maximum
fractional depth, even if cancellation makes a particular exit row integral.
It does not by itself prove the full rounded physical implementation.

The complete exact scalar replay confirms unchanged maximum row-l1 norms
**503,316,465 forward / 1,469,388,997/2 backward**, and unchanged maximum
denominator depths **4 / 27**. These stay within the retained historical
positive envelopes (64 / 101 bits, charged allocation 192 bits). Those physical
allocations are retained, not reduced based on exact-coordinate measurements.

## Verification boundary

The primary checker executes primitive instructions on sparse integer rows
with exact power-of-two denominators. A separate direct macro oracle checks
every target and work boundary; allowed-write checks and induction cover the
unchanged registers. Complete endpoints are also checked against the expected
forward and inverse-transpose shears on all **716 logical + 9 private input
columns**. All **492 dirty helpers** restore, and all nine private cells clear.

A separate dense Fraction-matrix interpreter checks the four changed signed
coefficient maps on arbitrary T/S/W columns. Thirteen adverse controls reject
missing repetition/clearing, wrong signs, dirty-work contamination, source
mutation, endpoint-neutral magnitude/grid excursions, an unpaid instruction,
and invalid or aliased macros. Early clearing and reduced rational encodings
are accepted as equivalent positives. Package tests check 3,000 sparse arithmetic
operations against Fraction arithmetic, domain preservation, source corruption,
equivalent gzip repacking, optimized offline relocation, typed-receipt
corruption and output preservation.

The primary primitive and direct-macro all-column engines share row arithmetic.
The dense local checker, bounded Fraction differential checks and the additional
complete `recheck_fraction.py` scalar interpreter check that shared dependency.
The supplemental interpreter uses Fraction-valued rows instead of integer rows
with a shared dyadic denominator; it compares complete register states at each
macro boundary. All implementations were prepared in the same AI-assisted
conversation. No independently implemented complete physical replay is claimed. Non-scalar
frame, phase and wrapper events are preserved and hashed, but not executed by
this scalar checker. The pinned maintainer evidence supplies that ancestry.
Finite linear-map evidence is not formal verification of the full multiplication
theorem.

## Scope, pins and predecessor credit

Exact base: **007664306fff84fbb1c9a1b4053b69f439764034**. At this base the selected
conditional result is **PR890, κ = 0.001661957774647029**; its certificate,
T21 construction and maintainer review were read. This contribution deliberately
uses historical PR626 JP8, not the current U8/T21 supplier. The original
checkpoint is immutable context and input binding; no current-frontier edit is
made. Only this directory is added, and `upstream/` is unchanged.

Source heads:

- PR626: `660de893d27bb7abd1d5b01b1640207528a5c851`.
- PR622: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
- PR696: `5a3f983715027c4fd83f50bc9001d4b18463bed1`.

Credit **Sagar Thakrar / PR696** for copy/unit lowering, the cost baseline and
cleared-work contract; **Jeremy Kothe / PR622** and **Chafik Boukhalfa / PR626**
for the provider and its archived replay; **icekylinx**, DreamingOfClouds,
eumemic, Rohan Arun and their retained compiler, circuit and analytic lineage.
**Philipp / PR882** supplies related single-scratch synthesis and the sparse
dyadic-row verification design. Its bounded graph permits one final target
accumulation; this contribution changes that restriction, so its shortest-word
result is not contradicted or reopened with more computation. **Gareth Davidson /
PR837** and **Chris Pagolu / PR734** provide related coefficient circuits.

PR883 changes paired X4 preconditions; PR945 shares coefficient preparation
across different-source macros; this package preserves each original macro and
work-clearing boundary. Historical **PR355 by Dugongue** already uses
repeated unit additions for integral bit-donor setup. Repeated addition itself
is elementary and no mechanism-priority claim is made. The added evidence here
is a complete JP8 primitive refinement, dirty-input restoration, exact prefix
guarantees and a reproducible cost/access census. No pending code is imported,
and unrelated savings are not assumed additive.

The OS assignment seed was **29** (complex-supplier track). Odd parity selected
historical JP8; seed29 selected coefficient three for the first control. Three
candidate tasks, the initial 703-PR overlap inventory, stopping rule and local
claim are in `CLAIM.json`. There was no pinned sprint coordination issue.
This experiment covers exactly both pinned programs and all ±2/±3 occurrences;
it makes no global circuit optimum or impossibility claim.

Publication resumed after the contributor created a writable fork. A complete
821-open-PR refresh found related later submissions. **Hanson Sun / @bbMisk,
PR1036** (`c4ad801099d0813ffac56f0b517a908cd8ae0c6a`) applies the same
ordinary ±2/±3 unit updates to historical **CK**. This package adds separately
implemented **JP8** coverage, both complete 725-column primitive traces and
exact source-access, prefix and fractional-depth receipts. It does not claim
priority for the elementary identity or the mechanism. PR1036's broader
CK two-register exclusion is not imported or reproved here.

**Seb / @ZK-Snarky, PR999** at
`fd38a824adb3a5c60c101a86c950a6d590454adf` supplies broader bounded target
accumulation. A targeted replay of its pinned `addition` function chooses
unchanged Horner words for ±2 and ±3, at costs 4 and 5 per real component.
Our direct-source words cost 3 and 4. Thus its 4,086-primitive JP8 saving does
not already include these replacements. No full PR999 replay or composition
with that broader compiler is claimed. **Ali Romman / PR1064** credits and uses
PR1036's integer routes in a different raw factory; its factory savings and
physical invoice are not combined with this package.

Refreshed main is `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`, now selecting
conditional κ **0.001672660197076918** (PR1094). All six consumed historical
inputs remain byte-identical or decompressed-payload-identical. The research
base and historical JP8 scope are preserved; no transport to the new selected
supplier is claimed. Exact overlap and targeted comparator evidence are in
`OVERLAP.json`.

All-size compilation, common-label/mutable-source realization, whole-call
hosting, precision/tape/recovery, bit-supplier H1–H5 and analytic-transfer
obligations remain inherited. Native physical admission, production lowerer
integration, global invoices/assembly and transport to U8/T21 remain open.

## Open next questions

- **Can these exact words pass the historical JP8 physical interface?** This
  determines whether the local saving can enter a complete construction. First
  bind the replacement lowerer to that interface and rebuild its source-access,
  frame/owner, precision and complete invoice checks. The blocker is that this
  package executes scalar projections only; the unchanged scalar maxima do not
  discharge physical admission.
- **Does the replacement compose with pinned PR999?** Its retained ±2/±3 Horner
  words suggest additional local savings, but no combined result is certified.
  First replay both complete JP8 programs with an explicit composed dispatcher
  and independently recompute the total cost, prefix bounds and dirty-input
  contract. The blocker is the absent combined replay and interface evidence;
  totals from separate packages must not simply be added.

Prepared by **Michał Ciemięga (@zewelor)** with substantial **OpenAI Codex
assistance** in research, code, proof writing and verification. Apache-2.0,
with predecessor attribution retained. No independent human review is claimed.
