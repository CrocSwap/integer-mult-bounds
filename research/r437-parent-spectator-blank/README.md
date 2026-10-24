# The 972-bit R437 child does not pay the parent spectator blank-return

**Partial negative result. No new κ.** The selected conditional exponent stays
`60403/20000000` (`0.00302015`, #4470).

## Result

On the source-entry identities in `research/r437-carrier-integration`, the
full parent payload is exactly `9475 * 3^124` times the executed `972`-bit
child packet. A fixed-tape blank-return that charges at least one visit per
payload symbol is therefore not paid by that execution.

The checked arithmetic is:

```text
lcm(28416, 28425) = 269241600 = 28416 * 9475,
E = 2 * 3 * 2 * 3^4 = 972,
V = 9475 * 2 * (3 * 3^124) * 2 * 3^4 = 9475 * 12 * 3^128,
V / E = 9475 * 3^124.
```

`9475` is the unused-row multiplier in NUMERICAL.md §5. The factor `3^124`
is the `124` atom coordinates present in the parent gap and absent from the
executed gap `3`. Both factors are required: either one alone is a strictly
smaller comparison. The argument is in [PROOF.md](PROOF.md). `verify.py`
recomputes the lcm, the two extent products and the ratio. It does not import
the carrier-integration package.

## Scope

Task card `r437-carrier-integration`, priority revision 7, base
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`. Scope status is **refined**.

The card asks whether the paid two-window carrier is admitted by the pooled
compiler and the physical caller. This package takes open question 1 of
`research/r437-carrier-integration`: bind the checked source entry's parent
spectator multiplicity to the uniform fixed-tape blank-return. The multiplicity
is certified, and the `972`-bit execution does not pay it. Gather, routing,
checkpointing, table setup and the reverse coefficient stay unresolved, so
this is not a global admission and not a supplier.

Ordered eligible list for session r27, after dropping work this account
already delivered, results on current main, questions covered by an open pull
request, and topics already on a fork `cursor/*` branch. Open handoffs in the
19 October index (discussion comment 19029944) come first. Priority-table rows
whose stated next decision is still open come next.

1. Downstream consumer of `(w, q, v_N)` (comment 19030045). The role-exchange
   caller audit still has no favorable caller for that triple.
2. Fresh T385 full-wrapper completion (comment 19030047). The admission audit
   still records the 780-second timeout as unfinished.
3. Six-tape head-move bill at the L546 F0 event (comment 19030049), distinct
   from the adjacent-ADD price in #4162.
4. `BIT.md` weighted-leaf and fixed-tape induction, the remaining shortest
   unaudited #4100 obligation not already delivered by this account.
5. **This package.** Parent spectator blank-return for the R437 carrier.

Excluded before this cut: the retiming handoff (comment 19030053), already
covered by #4122, #4128 and open #4567; the four-provider rebind, already on
main in `research/mixed-provider-admission`; the QQ16 park/restore comparison,
in open #4167 and #4172; the P104 slot, chart, encoding, fiber and port-chart
packages, including the helper-chart half as a refinement of that row; the
compact-switch audit #4321; the rank-8/16-child producer, already in
unpaidmoon PRs #4151, #4156 and #4158 and in fork `cursor/rank8-*` branches;
and the `F_2^6` difference basis, on main in `research/f2-six-difference-basis`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/r437-parent-spectator-blank --check-only
python3.12 -B scripts/research_package.py --package research/r437-parent-spectator-blank
```

Direct checks:

```sh
python3 -B research/r437-parent-spectator-blank/verify.py
python3 -B research/r437-parent-spectator-blank/test_verify.py
```

Expected marker:

```text
PASS_R437_PARENT_SPECTATOR_BLANK rows=9475 omitted_coordinates=124 executed_bits=972 parent_over_executed=9475*3^124 parent_over_executed_digits=64 lcm=269241600 blank_return_discharged=false no_new_kappa
```

`test_verify.py` prints `PASS_R437_PARENT_SPECTATOR_BLANK_CONTROLS`.

Not run: Lean, Docker, the selected cold replay, `physical.py`, the pooled
compiler, and any execution of the 9475-row parent packet.

## Open next questions

1. What is the exact fixed-tape visit count of one blank-return of the
   `9475`-row parent, including cursor motion across the `124` omitted
   coordinates, at this same source entry? The factor above is a payload
   lower bound, not that machine's invoice. First step: one source-bound
   cursor trace on the parent extents. Blocker: the published child bridge
   does not allocate that parent.
2. Can the remaining terms of BILL.md's C/D inequality be instantiated at the
   original root without setting gather, checkpoint or table setup to zero?
   A blank-return lower bound does not sign the whole inequality. First step:
   name one of `G`, `C` or `F` and pin its tariff. Blocker: those tariffs are
   not inputs here.

## Credit

The extents, the constant `269241600`, the quotient `9475`, the executed
`972`-bit tape and the statement that blank-return stays charged are Chris R
/ Clear1nsight, `research/r437-carrier-integration`, from the paid carrier in
PR #4067 and the reverse-coefficient distinction in unpaidmoon PR #4147.
Constructor traffic inside preparation is unpaidmoon PR #4160 and is not this
ratio. Predecessor lineage named in the carrier package remains theirs,
including ai-nanachi / PR #3647, Ali Romman / PR #1043, and Sagar Thakrar /
PR #3700 and PR #2423.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or formal-kernel review is claimed.
