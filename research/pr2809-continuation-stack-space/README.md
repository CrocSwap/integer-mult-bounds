# Depth-first continuation stack keeps O_q(V) at the new c

**Scoped space lemma. No new κ.** The selected conditional exponent stays
`60403/20000000`. The PR2809 simulator is not run.

## Result

In the depth-first model written in `BIT.md` §2, with
`c = 8667/5000000`, the parked ancestor stack is `O_q(V)` for every stream
whose volume satisfies `V ≥ e`. The constant proved here is **26041**. The
per-level allowance named as the first step of
`research/bit-stock-recurrence-audit` fails at level 1 for every integer
`e ≥ 2`.

Let `q = 2^89 - 1`, `W = 28416`, `N = |GL_64(F_q)|`, `G = W N`, and
`w = ceil(e^c)`. `BIT.md` gives the child payload volume `V/G`. The suggested
level-1 allowance is `V / (G q^{4096(w-1)})`. For `2 ≤ e ≤ 2^576` one has
`w = 2`, and for every `e ≥ 2` one has `w ≥ 2`, so the child payload is
exactly `q^{4096(w-1)} ≥ q^{4096}` times that allowance. At `e = 1` the
factor is 1, so the bound `e ≥ 2` is sharp. The geometric ratio `1/G` is a
different, larger allowance. The infinite sum of the ancestor payloads is
`V/(G-1) < V`, with no dependence on `c`.

Parameter bits are charged one cell each. `D(e)` cuts, each storing one
integer of size at most `K(w)^{D(e)}`, cost at most `D(e)^2 bitlength(K(w))`
bits. On the `w = 2` plateau, `bitlength(K(2)) = 729117`. The ratio of those
bits to `e` is largest at `e = 448`, where `D(448) = 4` and the least integer
`C` with `C e` at least the bit count is **26040**. The same `C` covers every
larger address length, including those with `w > 2`. Therefore

```text
parked payload + parameter bits ≤ V/(G-1) + 26040 V ≤ 26041 V.
```

The constant depends on `q` and not on `e` or `V`. The argument is
[PROOF.md](PROOF.md).

A different reading, in which each of the `D(e)` cuts parks a fresh copy of
the root volume, is not `O_q(V)`. For `e = 2^26050`, `D(e) ≥ 26042 > 26041`.
`BIT.md`'s geometric sentence is the reading proved here.

## Scope

Task card `uniform-transfer-audit`, priority revision 7, base
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`. Scope status is **refined**.

The card asks whether one quantified step of #4100 holds at its caller. This
package takes only the continuation-stack question left by
`research/bit-stock-recurrence-audit` after that package checked the finite
and algebraic statements of `BIT.md` §§1–4. It does not audit another #4100
sentence and it does not change the selected record.

This is item 2 of the eligible list below. Fewer than eight items remained,
so the assigned index is `(8-1) mod 3 = 1`.

Ordered eligible list for session r30. Open handoffs from the 19 October
index come first, with a closed smallest task removed and a still-open
remainder kept when it is distinct. Priority-table rows whose stated next
decision is still open come next. Catalogue cards that are not already those
rows follow. Dropped before the cut: work this account already delivered,
results on current main, questions covered by an open pull request, and
topics already on a fork `cursor/*` branch. The sibling branches visible at
selection included `cursor/qq16-l546-head-move-306b`,
`cursor/r437-parent-spectator-blank-7c47`,
`cursor/r437-source87-fibre-multiplicity-9b2b`, and
`cursor/ledger-boundary-exponent-efc8`.

1. A caller that accepts `(w, q, v_N)` without restoring the original source
   slots (discussion comment 19030045; open question 1 of
   `research/p104-role-exchange-caller-audit`). The cleanup consumer in
   `research/p104-residual-consumer` leaves that caller open.
2. **This package.** The PR2809 encoded continuation stack at the new `c`.
3. A 14-point difference basis of `F_2^6` with a simple closed walk of step
   weight at most 3. The displayed witness in
   `research/fixed-fourteen-basis-walk` needs weight 4, and open question 1
   of `research/f2-six-difference-basis` asks about any other 14-point basis.

Excluded before this cut: the fresh T385 wrapper, closed by
`research/t385-r437-copy-audit`; the six-tape head-move bill, on
`cursor/qq16-l546-head-move-306b`; the retiming handoff, covered by #4122
and #4128; the four-provider rebind, on main in
`research/mixed-provider-admission`; the matched park/restore bill, covered
by open #4167 and #4172; the R437 fixed-tape blank-return, on
`cursor/r437-parent-spectator-blank-7c47`; the #4100 ledger boundary
exponent, on `cursor/ledger-boundary-exponent-efc8`; the #4091 word, capacity
and stock equivalence, on main in `research/fourth-entry-ceiling-transfer`;
the compact-switch contract and its sharp-window density; the rank-8/u2
producer topic, on `cursor/rank8-u2-separate-idle-a7b8` and
`cursor/rank8-u2-slack-stop-7249`; and the replay-runtime and portable-replay
cards, which already have measured fast paths and the gzip payload
convention on main.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/pr2809-continuation-stack-space --check-only
python3.12 -B scripts/research_package.py --package research/pr2809-continuation-stack-space
```

`verify.py` prints

```text
PASS_PR2809_CONTINUATION_STACK_SPACE C=26040 witness_e=448 witness_bits=11665872 K2_bits=729117 level1_factor_bits=364544 payload_ratio=1/(WN-1) full_copy_exceeds_bitlen=26051 no_new_kappa=true
```

`test_verify.py` prints `PASS_PR2809_CONTINUATION_STACK_SPACE_CONTROLS`.
Not run: the PR2809 simulator, Lean, Docker, and the selected cold replay.

## Open next questions

1. Does the PR2809 continuation serializer park the ancestor chain, or one
   root-sized stream per cut? The second reading is not `O_q(V)`, because
   `D(2^26050) ≥ 26042`. First compare the bytes written at one recursive cut
   with the child capsule. Blocked here because this package does not extract
   or run that serializer.
2. Are the marker, template and erased-backing cells inside the `26041 V`
   budget, or do they add another `q`-dependent multiple of `V`? `BIT.md`
   includes them in the `O_q(V)` sentence. First charge one fixed template per
   live role against `V/(G-1)`. Blocked here because §2 does not give the
   live role count during recursion.

## Credit

The construction and the `O_q(V)` sentence are Cinna Davis's #4100
(`research/unconditional-batched-crt/BIT.md`). Mark (Matarener), with
Claude Code assistance, checked `BIT.md` §§1–4 in
`research/bit-stock-recurrence-audit` and left this stack question open.
Jose Manuel's `research/physical-ordinary-interchange` proves an `O_q(V)+F_q`
space bound for the older `c = 17/10000` on the stream `P G S q^{2e}`; that
replay is not a dependency of the arithmetic here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
