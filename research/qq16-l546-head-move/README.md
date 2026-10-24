# Sharp six-tape head moves for `L546 -= L561`

**Scoped tariff. No new κ.** The selected conditional exponent stays
`60403/20000000`. Same-frame legality of this ADD does not make its tape-head
bill zero.

## Result

After both complex registers already occupy the six tapes of the pinned axis
kernel, the coordinatewise subtraction `L546 -= L561` has the closed-return
cell-action bill

| | count |
| --- | ---: |
| READ | \(4NW\) |
| WRITE | \(2NW\) |
| MOVE | \(8NW-12\) |

Here \(N=2^n\) with \(n\ge 1\), \(W\ge 1\) is the signed component width, and
every head starts and ends at its interval origin. The move count equals
\(\sum 2(L_t-1)\) over the six kernel lengths
\((NW, NW, NW/2, NW/2, NW/2, NW/2)\), so it is sharp for that placement.
L561's cells are unchanged. The argument is in [PROOF.md](PROOF.md).

data0 and data1 hold L546. The four half-length scratch tapes hold L561, split
after coordinate \(N/2\). Those six lengths have exactly the \(4NW\) cells the
two registers need. Borrow stays in finite control and resets on each
coordinate. The schedule never steps one past the last cell.

For the kernel fixture size \(N=512\), \(W=5\), the formula gives
MOVE \(=20468\), READ \(=10240\), WRITE \(=5120\). That width is the kernel
fixture's width, not a measured width of native event 9895.

## Scope

Task card `joint-query-controller`, priority revision 7, base
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`. Scope status is **refined**.

This is item 2 of the eligible list below. It answers open question 1 of
`research/qq16-adjacent-add-bill` and the layout half of discussion comment
19030049 that remains after `research/qq16-f0-first-caller` bound event 9894.
It does not repeat #4162's four scalar-work steps, and it does not price the
matched park/restore comparison left by #4166.

Ordered eligible list for session r24. Dropped first: work this account
already delivered, results closed on current main, questions covered by an
open pull request, and topics already on a fork `cursor/*` branch. Open
handoffs from the 19 October index come first, with a closed smallest task
removed and a still-open remainder kept when it is distinct. Priority-table
rows whose stated next decision is still open come next. Catalogue cards that
are not already one of those rows follow.

1. A caller that accepts `(w, q, v_N)` without restoring the original source
   slots and without repaying the saving (discussion comment 19030045). The
   q-field cleanup in `research/p104-residual-consumer` and the 192-transport
   return in `research/p104-role-exchange-caller-audit` leave that caller open.
   Distinct from the encoded-exit standard-Y consumer and from `(N-P)⊗M`.
2. This package.
3. Four-provider ordinary/outer rebind (`supplier-boundary-audit`; open
   question 1 of `research/staged544-mixed-fourth-entry`). The idle-cost block
   is recorded; the four-id rebind is not.
4. Matched park/restore bill for the #4166 caller (`joint-query-controller`
   as stated in the priority table; open question of
   `research/qq16-caller-install`). Open #4167 and #4172 do not price it.
5. R437 fixed-tape preparation and parking bill (open question 1 of
   `research/r437-carrier-integration`). The reverse coefficient is already
   covered.
6. `#4091` model equivalence on the later 1090-call fill
   (`independent-moment`).
7. The PR2809 encoded-stack visited-space bound left by
   `research/bit-stock-recurrence-audit`. The algebraic BIT.md induction is
   closed there. CRT join, row-field movement, the half-gap budget and the
   uniform evaluator are already on fork `cursor/*` branches or in the listed
   unpaidmoon PRs.

Excluded before this cut: the fresh T385 wrapper (comment 19030047), closed
by `research/t385-r437-copy-audit`; the retiming handoff (comment 19030053),
already covered by #4122, #4128 and later shear work; `p104-side-correction`
as its own row, because the slot, chart, encoding, fiber and standard-Y
pieces are already certified; `formal-interface-lemma`, because #4321 audited
the compact-switch contract and a fork branch holds the sharp-window density.

## Not charged

- Moving L561 from its native home onto these scratch windows.
- Copying it back, or clearing scratch for a later kernel.
- The preceding axis kernel (MOVE \(=20NW\) on its own contract) and the
  frame climb of event 9894.
- A native component width for event 9895. The formula keeps \(W\).
- Park/restore, F17 consumption, and any change to κ.

Unknown placement cost is not zero. This is a conditional tariff for one
stated packing, not a physical embedding extracted from the native word.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3 scripts/research_package.py --package research/qq16-l546-head-move --check-only
python3.12 -B scripts/research_package.py --package research/qq16-l546-head-move
```

Directly:

```sh
python3 -B research/qq16-l546-head-move/verify.py
```

Expected:

```text
PASS_QQ16_L546_HEAD_MOVE move=8*N*W-12 read=4*N*W write=2*N*W bound=sum_2(L_t-1) sharp=yes placement=data_full_scratch_halves heads=origin L561=preserved no_new_kappa
```

The verifier loads the pinned tape object, checks the bill on every
\(N=2^1..2^7\) and \(W=1..5\), checks signed fixtures including \(N=512\),
\(W=5\), rejects a non-unit move, and flips every payload cell of one
\(N=2\), \(W=2\) instance.

## Open next questions

1. What does it cost to place L561 onto the four scratch windows before this
   subtraction? The move bill above starts only after that placement. The
   first step is to name the intervals that actually hold L561 at event 9895.
   PR #3932 leaves those intervals unbound.
2. If the next kernel needs zero scratch, L561 must be copied out before that
   clear. The first step is to bind the next tape-using event after 9895 to
   these six windows. No such binding is in the forward word's frame bill.

## Credit

The six-tape rules and the axis-kernel lengths are Clear1nsight's
`research/qq16-gaussian-axis-tapes` (PR #3884). The first-caller cut at event
9894 is PR #3932. The same-frame scalar price of event 9895 is unpaidmoon's
#4162 (`research/qq16-adjacent-add-bill`), whose open question 1 is the
question answered here. Ali Romman's QQ16 lineage and Nick Petalas's numerical
formats are the retained background; they are not re-proved.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or formal-kernel review.
