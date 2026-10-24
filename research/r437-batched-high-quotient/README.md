# Batched high-factor binary Count quotient: a scoped tradeoff

This opt-in adapter refines the actual `fresh_rows.quotient` on **valid fixed
contexts**: prime q, dimension m≥1, encoded modulus q^w with w≥1, positive family
factor F and GL low count G. It replaces m² traversals of the encoded radix
iterator and m²(w−1) divisions by q with one radix traversal and w−1 divisions by
the compiled constant C=q^(m²). It retains binary Count inputs and outputs and
never decodes runtime w. The actual four-statement `Machine.node` quotient/save/
stock guard and its real `save_count`/`commit` bodies are executed unchanged.

**This is a finite execution and fixed-context refinement, not an unconditional
physical speedup.** C has 6,493 bits already at q=3,m=64, with C possible remainder
states. The compile/setup and wide arithmetic bill cannot be treated as free.
The default backend, frozen caller and selected frontier remain unchanged.

## Refinement and ownership

After the identical F and G divisions, let N be the remaining positive Count.
The original accepts the high part iff q^(m²(w−1)) divides N. Successive exact
q-divisions and successive exact C-divisions have the same final quotient,
because C^(w−1)=q^(m²(w−1)); a first failing intermediate division in either
implementation implies failure of the same aggregate divisibility. Both use the
same `complete fresh high factor` error class. For w=1 both do no high division,
though the original still traverses the radix iterator m² times. Positivity and
F/G checks are unchanged. The literal local guard then accepts exactly when the
returned quotient is divisible by the same stock_multiple; that does not claim
the node has executed its payload or later recursion.

The adapter closes its owned Count on ValueError. Both original and adapted
paths preserve the borrowed Count and restore numeric live sets on valid
contexts, including rejected fresh/F/G/high/local-stock inputs. The harness
copies the source AST for only the four quotient/guard statements and the two
save helpers, not full Machine.node. Ordinary Count-backed record tapes are
used; `Lease=()` disables the unrelated Lease-return branch of commit. The
same actual code consumes the candidate and baseline outputs.

The malformed-modulus control (8 in a purported q3,w2 context) is deliberately
**outside this theorem**. The unchanged `radix_power` need-failure leaks two
numeric slots in both versions before its normal frees. The receipt explicitly
records numeric_restored=false and two leaked slots; the harness performs
`arena.rollback` solely to clean its diagnostic fixture. This is not a runtime
repair or successful cleanup claim for invalid contexts.

## Complete bill and what the measurements mean

For each actual Count division the external observer records input bit width,
divisor width, and the number of possible remainder states (hashed integer
receipt). It calls the unchanged `Natural.divide_small`. After each input bit,
that source doubles/adds a bit, compares with the divisor, and conditionally
subtracts it. The pre-subtraction temporary is below 2C. Thus C states require
ceil(log2 C) bits, and transient control needs at most one additional bit. The
receipt's `B*(4*b+8)` is a diagnostic linear-bit-work proxy for B input bits
and a b-bit divisor. The four-linear-scan coefficient is an accounting choice,
not a proved binary-Turing-machine step bound. The source arithmetic admits an
O(Bb) bitwise implementation once its ripple primitives and storage are fixed;
this package does not supply that implementation. The proxy is **not a measured
host-operation count** or a calibrated physical-tape implementation. Count normalization and head
movement remain separately charged in the exact tape meters. The already-large
G division and the final stock_multiple division are included in both invoices.

Constant construction uses an explicit square-and-multiply sequence. The
receipt lists every multiplication's operand widths, multiplication count,
Σ operand-width products (schoolbook bit-product units), and stored divisor
width. This provides an implementable construction bill; native Python big-int
multiplication is not charged as a unit-time physical operation. At m64 it takes
13 products with 14,066,186 schoolbook bit products and stores 6,493 bits. A
finite-state implementation that literally compiles all remainders has C states,
not merely 6,493 states. A binary-state implementation must implement and charge
its comparisons/subtractions instead. Neither representation is free.

At m64,w1 the observed Count record bill is identical (755,782 actions), while
residue actions fall from 4,808,704 to 1,174. However, an unamortized charge of one
unit per stated schoolbook bit product already exceeds that saving. This is a
concrete setup/scan tradeoff, not a net improvement claim. Compile-once reuse
may amortize setup, but still must pay the wide divider's runtime implementation.
A conditional saving requires saved tape/encoded-radix cost to exceed the extra
compile, storage/control and wide arithmetic cost in one explicitly chosen
machine model. This package does not prove that inequality uniformly.

Matched physical replays cover m2,w1/2/3; m4,w2; and real m64,w1. A candidate-only
real m64,w2 execution uses R=9475*(28416*|GL64(F3)|*3^4096)^2 and returns R/A,
then passes the actual local 9475 guard. The original m64,w2 full replay is not
run; equality there follows from the scoped arithmetic refinement, not a measured
baseline. Full receipts include all divisions and separate record/residue lanes.
No field payload, production rows, root admission or supplier budget is run.

## Sources, reproduction and credit

The actual quotient/Count code is David Arias's PR2753 predecessor; ToikY's
`source-directory-setup-cost` identified repeated high-power/radix traversal
costs. #4757 (5dba1acc2ef67e65e6a40e963f727b01edc5e132) covers sharp host entry
and explicitly leaves real binary Count execution open; the present work does
not repeat the 9475 factor proof or change that entry guard. NickPetalas #3246,
Tekalign #3264, Mihir #4685, and codyw912 #4734 retain predecessor credit for the
stock invariant and adapters. All 23 declared inputs are SHA256/git-blob bound
at canonical base 624de9dc66858af0945e5f8a0942488d62280d43 and checked before imports.
The new adapter and harness are Brian (JoyboyBrian), substantial OpenAI Codex
assistance, Apache-2.0. No frozen source was edited.

Run `python3.12 -I -B research/r437-batched-high-quotient/verify.py`, also with
`-O`; both are registered in VERIFY.json. Explicit checks survive optimization,
and JSON typed receipt equality distinguishes booleans from integers. Results
are author-checked; no formal-kernel or hosted-CI acceptance is asserted.

## Open next questions

1. Implement and meter a binary large-constant divider or explicitly priced
   finite controller, then determine the setup-amortization crossover.
2. Compare this batch with a shared radix traversal that retains q-divisions,
   which may avoid large-controller setup while preserving residue savings.
3. Fix the inherited out-of-domain radix iterator cleanup in a separate scoped
   package, preserving its accepted-domain and rejection behavior.
4. Join the encoded quotient to admitted root rows and full caller payload before
   claiming complete R437 supplier admission.
