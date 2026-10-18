# Two inputs optimally detect every single ADD omission in PR967 D

**Adversarial audit / exact finite test-suite minimum; no new kappa.** Two
fixed binary input assignments detect every one of the **5,563 elementary
ADD omissions** in the frozen PR967 semantic-D word, when all 661 output
coordinates are observed. One assignment cannot suffice. The result is a
compact diagnostic suite for this exact fault class, not an arbitrary-map
verification shortcut.

The lower bound is particularly small: before gates **236, 258 and 259**,
their source values are respectively

```text
x185, x188, x185 XOR x188.
```

No binary input makes all three values one. The two assignments in
[WITNESS.json](WITNESS.json) attain the resulting lower bound. Their input
supports, gate locations, exact coverage and a scope counterexample are
recorded in [CERTIFICATE.json](CERTIFICATE.json).

| Detection by the two assignments | Omission count |
|---|---:|
| First assignment only | 2,036 |
| Second assignment only | 1,779 |
| Both assignments | 1,748 |
| Neither | 0 |

These are binary data values, including arbitrary incoming helper dirt and
target values; they are not gate masks or symbolic test seeds. Registers are
zero-based. The assignments have 377 and 387 one bits across 661 coordinates.
Each experiment starts from its prescribed input and compares the complete D
output with the unmodified D output. No reset cost or production running-time
improvement is asserted.

## Exact model and proof

Expand every D record `[frame,destination,sources]` into its ordered elementary
updates `x[destination] ^= x[source]`. All 1,165 records have frame zero;
each of the 5,563 ADDs has distinct source and destination registers. A fault deletes **exactly one** such
update while preserving every other operation and its order. The observations
are all 661 output bits after the complete standalone D word. Inputs may be
chosen freely in F2^661, are fixed before execution, and do not depend on
which gate is missing. The declared optimum counts input assignments, not
the number of observed output bits or the cost of physically running tests.

Let P_i be the correct prefix before gate i and v_i the row that gives its
source value from the original input. The correct and faulty trajectories
are identical up to this gate. Omitting it changes the state there by
`e_destination * (v_i x)`. The unchanged suffix is invertible because every
remaining update is an invertible binary transvection. Therefore the full
final output differs **if and only if** `v_i x = 1`. This argument also explains
why observing all outputs matters: the suffix can carry the error entirely
into helper coordinates.

The forward symbolic pass derives every v_i using 661-bit row masks. It finds
761 distinct nonzero forms. For the three displayed gates their XOR is zero
and their number is odd. If one input detected every gate, these three forms
would each evaluate to one, contradicting linearity: their XOR would evaluate
both to zero and to one. This proves a universal one-input impossibility;
it is not a failed search over inputs.

For the upper bound, the verifier checks that every v_i evaluates nonzero on
at least one of the two frozen assignments. A separate implementation then
replays all **5,563 complete literal mutant words**, from the original nested
record lists, using a two-bit value per register to carry the two independent
experiments. It imports no discovery or row-factor code. XOR acts separately
on the packed bits, so this executes exactly both experiments. It performs
**30,941,406** elementary mutant updates and **3,677,143** complete-output
value comparisons. The algebraic and literal coverage patterns agree.

The lower-bound source forms receive another check: a set-based reverse
pullback through each prefix reconstructs the three supports without using
the forward row masks. The baseline D map is compared with selected PR589's
D on all 661 symbolic input columns; the other word fields must agree exactly.
No native, whole-word, frame, COPY/ERASE or precision replay is inferred.

## Why this is a restricted guarantee

The same two assignments **miss a concrete two-omission error**. Delete gates
527 and 528, the adjacent updates `x111 ^= x228` and `x111 ^= x246`. Both tests
still produce the correct complete output. Starting instead from the singleton
input `x228=1`, with every other input zero, changes 27 target coordinates.
The certificate lists them, and the independent literal interpreter checks
both the two passing tests and the failing singleton. This is an actual
counterexample to extending this suite's guarantee to two simultaneous
omissions; it is not a defect in the predecessor's full-boundary verifier.

Observing only the 111 target outputs also misses exactly 221 single
omissions, the final helper-restoration updates. This independently corroborates
PR1017's distinction between target-only and full-boundary observation; it is
not claimed as a new atlas. All-ones input alone likewise fails. General
coefficient changes, wrong operands, record deletions, frame faults, several
omissions and propagation through the surrounding word remain outside the
proved coverage. A passing pair of tests cannot establish arbitrary-input
equivalence of a proposed replacement word.

## Reproduce

Python 3.10+ and standard library only, from the repository root:

```sh
python3 -I -B research/r439-optimal-omission-probes-seed66/verify.py
python3 -I -O -B research/r439-optimal-omission-probes-seed66/verify.py
```

Use `python` on Windows. Expected final line:

```text
PASS_R439_OPTIMAL_OMISSION_PROBES minimum=2 faults=5563 forms=761 controls=12 pair_counterexample=1 no_new_kappa
```

The default verifier writes nothing. It checks the exact mandatory source-pin
inventory before reading the words and compares every decoded certificate
field with type-sensitive canonical JSON. Duplicate fields and nonfinite
numbers are rejected. Add `--write-certificate` to deliberately regenerate
the receipt. All checks remain active under optimized Python.

Twelve rejection controls cover zero/repeated/out-of-range/Boolean probes,
broken lower-bound dependence or parity, target-only and all-ones claims,
missing source pins and duplicate/nonfinite JSON. The explicit two-fault
counterexample is separately accepted as evidence of the guarantee's limit.

`python3 -I -O -B research/r439-optimal-omission-probes-seed66/test_package.py`
also checks optimized relocation, exact receipt regeneration, deterministic
discovery replay and seven actual on-disk corruptions. It prints
`PASS_R439_PROBE_PACKAGE relocation=1 regeneration=1 discovery=1 corruptions=7`.

[find.py](find.py) records discovery by deterministic weighted local repair
with seed 66 and a 10,000-step cap. It found the assignments after 688 steps;
running it deliberately regenerates WITNESS.json. Its heuristic does not
prove optimality or enumerate all pairs of assignments. Exact optimality
comes solely from the three-form lower bound and the exhaustive fixed-fault
upper-bound replay. The default verification never runs discovery.

## Sources, overlap and obligations

Frozen experimental base: **abdc6a7002abdbcd9e21bfc5e1a795784deacfdf**.
Assigned seed **66**, adversarial audit track, with no reroll. Candidate
selection and the pre-experiment refinement are in [CLAIM.md](CLAIM.md).
[SOURCES.json](SOURCES.json) binds both consumed compressed word artifacts.
The selected construction remains PR942's T37 conditional
`kappa=0.001661960547713947`, retaining PR589's bit supplier. No selected
pointer or predecessor package is modified.

Credit **Sricharan Vagvala's PR967** for the helper-star word; **DreamingOfClouds'
PR589** and **eumemic's PR555/543** for its selected bit ancestry. Our earlier
**PR1017** supplies the single-omission syndrome interpretation and complete
atlas. This package adds an **optimal two-input diagnostic suite**, its
three-form impossibility witness, and an explicit correlated-fault blind spot;
it does not present a larger atlas as new work. No predecessor executable is
imported.

**Sagar Thakrar's PR762** already constructs an optimal ten-assignment suite
for every change of at most three coefficients per target row in historical
R420 compensation. That is a different, broader coefficient fault model with
a different word and observation boundary. The two-input result here neither
improves that theorem nor substitutes for its guarantees. PR675's owner timing
audit, PR1070's affine-agreement audit and PR1085's dirty-prefix precision audit
concern different obligations. Fresh overlap research used Curiosity Bot;
no priority over general linear test-suite methods is claimed.

Native replay, physical/common-frame realization, whole-call hosting and
invoices, precision/tape, all-size compilation, analytic transfer and inherited
bit-interface obligations remain outside this finite audit. No new supplier,
paid recursive profile, kappa, practical speedup or formal multiplication
theorem is claimed. Prepared for **@woklerx** with substantial **OpenAI Codex
assistance**; separate algorithms and AI review are not independent human
peer review. Apache-2.0; see [NOTICE.md](NOTICE.md) and [VALIDATION.json](VALIDATION.json).
