# PR3190's remainder moves change the physical operator

**Scoped negative result. No new κ; the selected record is unchanged.**

[PR #3190](https://github.com/CrocSwap/integer-mult-bounds/pull/3190) (Rohan Arun,
head `5e4a3235`) moves axes from idle **remainder** children, hosted or not,
into fully idle receivers. Its declared per-axis rule is the PR1252 commuting
rule. The pending candidates [#3198](https://github.com/CrocSwap/integer-mult-bounds/pull/3198),
[#3200](https://github.com/CrocSwap/integer-mult-bounds/pull/3200) and
[#3251](https://github.com/CrocSwap/integer-mult-bounds/pull/3251) inherit these
moves. #3198 reuses #3190's profile, and #3200 and #3251 list the same first moves
in their own MOVES files. [PR #3187](https://github.com/CrocSwap/integer-mult-bounds/pull/3187),
#3196, #3199 and #3204 refute #3184's star moves among **unhosted** 48s. #3204
explicitly leaves hosted instances out. This package closes that gap for the
literal remainder donations.

## Result

At owner replica 0, port 0, #3190 commits exactly two moves: axis `2^72` from
child 14 to child 8, and from child 15 to child 10. Children 14 and 15 host 31
of their 32 axes, so each donor is a **rank-1 hosted remainder** `[2^72]`. Both
moves pass #3190's declared rule: the axis commutes with the receiver's current
axes, all stage entry/exit X and Y translations, the terminal Y translation and
both terminal translations. The rank cap and orthonormality also hold.

Under the unchanged completed local-invocation contract, PR3187's exact
eight-stream Gaussian-integer replay gives the scalar baseline `i·I_8` at Fourier
character `2^72`. The overlay changes **10 entries**:

- move 14→8 alone (stream 2 → 6) changes 5 entries, for example `(6,6): i → −1`;
- move 15→10 alone (stream 3 → 7) changes the other 5, for example `(7,7): i → −1`;
- the joint change is exactly the union of the two.

So neither move preserves the operator, and they do not cancel each other.

**Census.** For all **112 ports** of owner replica 0, the 448 committed moves pass
the declared rule. The baseline equals the scalar operator at every moved-axis
character, yet the operator changes in **every** port. In 56 ports the moves are
the two hosted-remainder donations above. The other 56 carry #3184-type star moves
among unhosted children, which is consistent with #3187.

**Every single-axis remainder transfer fails too.** `census.py` enumerates every
hosted child with a nonempty remainder as donor, every other idle child as receiver
and every remainder axis, at all 112 ports of owner replica 0. Of these, **3,809**
pass #3190's declared rule (5,575 do not). **All 3,809** change the exact operator
at their own moved-axis character, and none survives. In 47 ports no transfer passes
the rule at all. `CENSUS.json` stores the per-port counts.

## Consequence and limits

The literal move sets of #3190, #3198, #3200 and #3251 are not operator-preserving
under their stated contract. Their claimed gains over #3148 come entirely from
these moves, so this construction does not support them. At owner replica 0, no
single-axis remainder transfer survives either. Multi-axis or simultaneous
transfers, other replicas' hostings, and repaired or rescheduled exchanges are not
covered. Other owner replicas are not replayed; the literal
counterexample is enough to reject the move set as committed. #3220's repair-cost
bound and native, owner and outer obligations are separate.

## Method and independence

`obstruction.py` imports PR3187's `algebra.py` and `source.py` **unchanged** from
`research/rank7-idle-star-stream-obstruction`. They supply the fill authentication
(all 2,717,280 rows, payload `8f4d6965…`), the operator model and the data-event
semantics. This package adds the per-port projection of owner replica 0,
hosted-remainder residuals, #3190's declared rule and the comparison. It is a new
**binding** of an existing checker to a new candidate, not an independent
reimplementation of the operator model. #3190's `MOVES.json.gz` is vendored
byte-for-byte and pinned to its head.

## Reproduce

```sh
python3 -B research/pr3190-remainder-stream-obstruction/verify.py              # port-0 witness, ~35 s
python3 -B research/pr3190-remainder-stream-obstruction/verify.py --all-ports  # all 112 ports
python3 -B research/pr3190-remainder-stream-obstruction/census.py              # 9,384 candidates, ~90 s
python3 scripts/research_package.py --package research/pr3190-remainder-stream-obstruction --check-only
```

Standard library only. Controls reject an axis outside the donor remainder and a
self-move. An empty overlay leaves the operator unchanged. Run locally with
Python 3.10.6; the registered Python 3.12 replay was not run.

## Open next questions

No single-axis remainder transfer survives at owner replica 0. Can a written
argument, extending #3204's rigidity proof to hosted children 4, 6, 14 and 15,
cover simultaneous transfers and every replica's hosting? That would turn this
finite census into a theorem that #3190's mechanism gives no legal gain, so that
the chain falls back to #3148. Repairs (#3220) and a changed schedule would be
the remaining routes.

## Credit

Nick Petalas (PR3187) supplied the exact replay used here. Gareth Davidson (PR1387)
first identified the physical-stream obstruction. Gonzalo-Mier (PR1252, #3196,
#3199), tekuuu (#3204) and Ross Richardson (#3220) supplied the related
obstructions. Rohan Arun (#3184, #3190, #3198, #3200, #3251) supplied the audited
moves; Jeremy Diviney (PR3148) the fill; Marius-Paul Dumitrean and the rank-seven
lineage the words. PR3133's notice is retained through PR3187's vendor directory.
Written by Claude (Anthropic) via Claude Code, in a session donated by Mark.
Apache-2.0. No human or formal review is claimed.
