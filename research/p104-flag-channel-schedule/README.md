# The channel touches every target before every source

**Partial. No new exponent.**

The published matching has 208 flags. In the 4,058-event channel those flags
cite, no event names both an X register and a Y register. Every Y register is
first touched by index 410. Every X register is first touched at or after
index 488. Each matched target therefore begins before its source.

## What was executed

The geometry names sources `X0` through `X103` and targets `Y0` through `Y103`.
The scan uses that naming and does not rebuild the compatibility graph. Across
the whole program, the latest first touch of a target is index 410 and the
earliest first touch of a source is index 488. None of the 208 matched pairs
share an event, and none share a first index.

Flag 0 is the worked record: source `X0`, target `Y34`, basis head 232. `X0`
starts at index 591 on the frame `[232]` and ends on the coordinate basis, so
it is not restored. Its add coefficients are `-2` and `2`. `Y34` runs from
index 129 to 3500, with add coefficients `-1/4` and `1/4`, and its final frame
contains 232. The two registers never meet in one instruction.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
schedule reading. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the flag certificate, the channel witness,
the geometry naming and the task catalogue. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-flag-channel-schedule/verify.py
python3.12 -B research/p104-flag-channel-schedule/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-flag-channel-schedule
```

The scan finishes in under a second.

## Open next questions

A relay through another register could still carry a coefficient from `X0`
after index 591 into `Y34`. This reading stops at the direct schedule.

## Credit

Nick Petalas supplied the 208-flag certificate. The channel witness is the
native word that certificate pins. Chafik Boukhalfa supplied that channel's
lineage through PR 1991, as credited there.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
