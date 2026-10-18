# Exact errors in the combined forward P104 relay word

Inserting the retained P104 channel into Philippe Van Velzen's 1,031-helper
relay-v2 correction gives these **attained, exact event-boundary constants**:

| Quantity | Exact value | First attaining location |
| --- | ---: | --- |
| Ideal logical growth, maximum row l1 norm | **235/2** | core event 3108, Y67 |
| Accumulated independent unit-defect gain, over every cut and register | **3181/4** | relay event 13509, Y93 |
| Accumulated unit-defect gain at the final boundary | **3181/4** | Y93 |
| Largest ideal logical coefficient denominator | **8** | relay event 8115, B35 |

The correction-only 70/56 prefix bounds in
[PR2594](https://github.com/CrocSwap/integer-mult-bounds/pull/2594) do not give
these combined forward constants. This package answers the forward
error-propagation part of that PR's open handoff. It independently composes the
literal core and relay schedules, including all eight owned private-copy
lifetimes. The claim is in [discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18952847).

The closing overlap refresh found parallel
[PR2614](https://github.com/CrocSwap/integer-mult-bounds/pull/2614), head
`a4a2a1c734283272691b1083c819e98e7d757f20`, by ywz65. It independently checks
the same combined endpoint and rank invoice and proves a later-read departure
floor; it explicitly makes no growth claim. That endpoint corroboration is
credited. The new result here is the sharp combined input/error growth and
its local-defect theorem. [PR2604](https://github.com/CrocSwap/integer-mult-bounds/pull/2604)
refutes a universal arrival-shape price premise; this package does not use that
premise or the affected 463-lifetime screen.

This is an author-checked **finite precision certificate with a stated local
defect contract**. It is not native lowering, a rounded recursive
implementation, a dual-program certificate or a new supplier/κ. The word's
unfavorable cost remains: its local-only zero-saving moment is
`104823/60736 > 1` in the retained fixed template.

## The exact word and boundary

The scientific inputs are pinned to:

- Rohan Arun's PR1972 channel witness, head
  `fd82d172f46933fd253c2c6de4bd5eaff5429cfd`, retained in Chafik Boukhalfa's
  `research/p104-native-channel/` (PR1991). Its SHA-256 is
  `0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e`.
- Philippe Van Velzen's relay-v2 `WORD_ct12.json`, fork head
  `fac9e821d31bc199b49e8ed463074a50d1264311`, obtained byte-exact through
  Nick Petalas's PR2594 at `6ae5673429d960a5fd0f936f6dfd67850e353278`.
  Its SHA-256 is
  `10d47696ed9b42992f8518512c7007ce39774c66d95bfe6de3d964d419058a73`.

Insert all 4,058 core events immediately before relay event **13135**, the
first contact labelled core cut 4058. The relay initializer at event 0 declares
the 1,031 arbitrary dirty inputs in the zero frame; it is not an operation
that sets their values to zero. Thus 13,134 relay events precede the core, and
the combined schedule contains **21,682 events**. All event indices in this
README are zero-based in their named source file; EXPECTED.json also supplies
combined indices.

There are **1,311 independent persistent inputs**: 104 X, 104 Y, 72 original
dirty helpers and 1,031 relay dirty helpers. One extra owned private slot C
serves eight nonoverlapping allocate/COPY/descend/erase lifetimes. C is not an
independent input. The checker compares the complete endpoint matrix, including
all zero coefficients (1,718,721 entries):

```
X_s -> X_s                 Y_t -> Y_t + X_t
Q_k, G_j, D_j -> unchanged  B_h -> unchanged
C -> discarded
```

Binary row-space elimination checks every common-frame scalar contact, every
nested transport and its dimension charge, the two relay contact cuts, all
original terminal frames, and every relay helper's monotone ZERO-to-FULL path.
Private COPY requires an allocated ideal-zero destination in the source chart;
erase discards that owned value, which need not be zero. No reversible
uncomputation of C is claimed.

The complete invoice, retained rather than improved, is:

```
15,408 ADDs = 2,624 core + 12,784 relay
 6,250 transports = 1,410 core + 4,840 relay
     8 COPYs, 8 exact allocations, 8 exact erasures

3501 H1 + 1152 H2 + 1084 H3 + 200 H4
 + 114 H5 + 181 H6 + 10 H7 + 8 H8
rank mass = 11,647 = 2,368 channel + 9,279 relay
```

## Local defect contract and theorem

Use the maximum of the **individual register Hilbert norms**, not an
addresswise component maximum or the sum of all register norms. All logical
registers live in the same Hilbert space. Each physical frame chart Γ_W is
unitary. A transport changes the chart and leaves the ideal logical value
unchanged; ADD and COPY have common operand charts, as checked from the word.

Allow an arbitrary local error of norm at most ε in the destination **after
each ADD, transport or COPY**, measured relative to applying that ideal
operation to the current, possibly already erroneous, state. Sources and other
registers are unchanged by that operation. COPY overwrites its owned zero
output with the source plus its error. Allocation and discard are exact;
discard has no output defect. There are **21,666** error sites. Scratch leakage,
errors inside an uncontracted primitive, and approximate endpoint adapters are
not included. A native implementation must establish this contract separately.

For initial register norms at most B, every ideal event-boundary register has
norm at most `(235/2) B`. At every event boundary, including live private C,
the difference between erroneous and ideal states has register norm at most
`(3181/4) ε`. Therefore

```
maximum computed register norm <= (235/2) B + (3181/4) ε.
```

Both separate constants are sharp for this fixed schedule and this independent
local-error model. Sharpness does not assert that a particular rounding rule
produces the worst errors. If B > 0, p is a nonnegative integer and every local
defect is at most `2^(-(p+10)) B`, every boundary error is less than `2^(-p) B`,
and every computed boundary norm is less than `128 B`. Ten is the least integer
extra exponent guaranteeing that error bound under this contract, since
`512 < 3181/4 < 1024`. This is a statement about **local absolute error
tolerances**; it is not a ten-bit floating-point implementation theorem.

For integer logical inputs, every ideal logical value remains in `(1/8) Z`
coordinatewise. This denominator statement concerns logical rows, not the
Gaussian coefficients or internal states of a native chart implementation.

At the final boundary, distinct local tolerances can use the following exact
classwise maxima. Their sum is a valid upper bound; the maximizing register
can differ between columns.

| Error sites | Maximum final coefficient | Contribution at uniform maximizer Y93 |
| --- | ---: | ---: |
| Core ADD | 114 | 109 |
| Core COPY | 3/2 | 3/2 |
| Core transport | 336 | 711/4 |
| Relay ADD | 299 | 290 |
| Relay transport | 217 | 217 |

For example, the final error is bounded by
`114 ε_core_ADD + (3/2) ε_COPY + 336 ε_core_transport
 + 299 ε_relay_ADD + 217 ε_relay_transport`.
With a common ε, the sharper joint maximum is `3181 ε/4`, not the sum of
independent class maxima. These classwise constants apply to final outputs;
only the common-tolerance bound above is asserted at all intermediate cuts.

## Proof and independently directed calculations

Write each ideal event as a linear map M_i on the persistent registers and
one private slot. ADD has `d <- d + c s`, COPY has `C <- s`, and allocation
and erase set the unused private slot to zero. This fixed-dimensional encoding
is equivalent to the checked ownership lifetimes. Transport is logical identity.

The forward input scan starts with the 1,311 independent unit rows and a
zero private row. Exact Fraction row operations give every coefficient of
`P_i = M_i ... M_1`. For a product of Hilbert spaces with the maximum-register
norm, the induced norm of one scalar row is exactly its l1 norm: the triangle
inequality is the upper bound, and signed copies of a single unit vector attain
it. An unchanged row cannot create a new maximum, so examining each written
row covers every row at every cut. The first maximum is Y67 after core event
3108, or combined event 16242. A separate scalar evaluator reconstructs the
signs of that row and attains `235/2` at that precise event.

For errors, induction gives

```
delta_i = M_i delta_(i-1) + e_(d_i) eta_i
delta_j = sum_(i<=j) M_j ... M_(i+1) e_(d_i) eta_i.
```

Only the 21,666 declared sites have an η_i. The forward error scan introduces
a **distinct formal variable for every site** and propagates signed rational
rows, preserving cancellations. The l1 norm of each row is the exact
independent unit-error amplification. It first reaches `3181/4` at Y93 after
relay event 13509 (combined event 17566), and never exceeds it. A separate
scalar replay sets the 1,128 nonzero error variables to their attaining signs
and confirms this value. An unsigned triangle recurrence instead gives 10,315;
that looser envelope is recorded as a diagnostic, not used as the sharp result.

The reverse calculation independently starts from all final output unit
covectors and pulls them back through the word. Immediately before pulling back
gate i, its destination column gives `M_n ... M_(i+1) e_(d_i)`. Accumulating
the absolute entries yields each final output's error budget. Pulling back
ADD updates the source column by c times the destination column. Pulling back
COPY adds the private column into its source and clears the private column;
allocation/discard clear it. This is ordinary transpose propagation through
the **actual forward program**, not a proposed physical inverse-transpose.

The forward error rows and reverse columns agree on all **6,555** final
output/class budgets, compared entry by entry before recording their canonical
exact-vector SHA-256. Both
endpoint directions also agree with `Y += X`. A one-output reverse-covector
implementation and a forward scalar error-injection replay independently
attain the final `3181/4` at Y93. The all-cut and final witness sign digests
agree. [EXPECTED.json](EXPECTED.json) records the values, locations and digests.
There is no floating-point acceptance calculation.

## Reproduce and controls

Python 3.12, standard library only. Direct replay reads pinned files, imports
no predecessor executable and writes nothing:

```sh
python3 -I -O -Werror -B research/p104-relay-forward-errors/verify.py
python3 -Werror -B scripts/research_package.py --package research/p104-relay-forward-errors
```

Expected headline:

```
PASS_P104_RELAY_FORWARD_ERRORS inputs=1311 growth=235/2 final_error=3181/4 no_new_kappa
```

`--out PATH` writes the complete receipt exclusively to a new file. The
registered replay runs eight behavioral groups, including a small signed
COPY/transport fixture whose private intermediate error exceeds its final
error. Controls reject lost dirty compensation, omission of the core, wrong
COPY source, retained final private state, wrong contact cut, rank tampering,
nonmonotone moves and allocation into a public register. Reordered binary
bases pass. Cancelling inserted shears preserve the complete endpoint but
increase intermediate growth or denominators; their two extra independent
defects increase the affected output's budget by exactly two. An optimized
Git-free export verifies unchanged inputs, source-pin failure, receipt drift
and refusal to overwrite output.

The three full scans each run in a few seconds on the recorded Python 3.12
environment. The largest observed signed error state contains 161,347 sparse
coefficients; an explicit 2,000,000-entry cap bounds that scan. The literal
event counts, 1,312 register slots, dyadic input-prefix exponent and numerator
caps are enforced. Python uses dynamic integer/dictionary allocation; this is
a bounded finite checker, not a fixed-allocation native implementation.

Source pins and selection/overlap provenance are in [SOURCES.json](SOURCES.json)
and [TASK.json](TASK.json). No selected cold replay, native recipe regeneration,
physical dual execution, internal primitive rounding proof, global owner/idle
invoice, all-size recursion or tape implementation was checked. The native
Hilbert interpretation remains conditional on the stated unitary-chart and
local-defect interface. No independent human or proof-assistant review is claimed.

## Open next questions

- **Reduce the actual correction bill.** The pinned word already fails the
  fixed-template local-only moment. First reduce merge loss in the shared
  relay pools, then rerun exact endpoint, rank and moment checks. A favorable
  completed invoice is the blocker to supplier use; these error constants do
  not remove it.
- **Discharge the local native error contract.** Supply the new relay
  transport recipes and their internal magnitude/error bounds, then insert
  the derived tolerances into the five final-output budgets. Event-boundary
  constants do not establish internal scalar/address precision. Global
  hosting, tape and all-size admission remain additional blockers.

## Credit

Philippe Van Velzen supplies the cell-tree relay design, literal word and
cost warning; its original README and word are retained byte-for-byte under
`inputs/`. Nick Petalas's PR2594 supplies the correction-only growth audit and
the explicit combined-precision handoff. Rohan Arun's PR1972 supplies the core
word, Chafik Boukhalfa's PR1991 its native channel binding, Adam Gall's PR1940
the schedule, and Josie Elliston/PR1071 and Ali Romman/PR1125 the retained
geometry lineage. Hiroki Kumazaki/PR2353, this account's PR2393 and Ross
Richardson/PR2445 supply the monotone-relay model and acquisition lineage.
Existing notices remain unchanged; this contribution is Apache-2.0.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
OpenAI Codex (GPT-6 Astra) performed the derivation, implementation, checking
and writing. No independent human review is claimed.
