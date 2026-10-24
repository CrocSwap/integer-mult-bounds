# Independent review of productive-owner drift

The two counterexamples pass independent review. The 37-exchange alias
repair also passes its stated job-preservation checks. It does not repair
the output map. In both assignments, the constant unit input in family
13005 gives output `-1/4` in family 112, where the required output is zero.
The result holds with the original mode signs and with a negation after
each mode occurrence.

The review checks the frozen
[original counterexample](../../encoded-controller/PRODUCTIVE-OWNER-DRIFT.md),
[repaired counterexample](../../encoded-controller/REPAIRED-OWNER-DRIFT.md),
and [same-call repair](../../source-domain/productive-owner-drift/PROOF.md).
Their exact inputs and hashes are in [REVIEW.json](REVIEW.json).
No producer or other checker is imported by [review_drift.py](review_drift.py).

## Literal counterexample replay

The checker reads the frozen 626-event schedule and binds every event
to the selected template or accepted paired marker. It executes every
paired physical ADD on the actual productive family. It then executes
all 20,389 scalar events in each raw FULL-MODE core. It does not use the
producer's closed formula for a raw core. Across one complete word this
is 2,936,016 core scalar events and 193,536 paired graph ADDs.

The state has all 14,336 productive coordinates. There is no separate
clean-mode input. Cross-core aliases are used literally in the original
assignment. In the repaired assignment, all promoted fields avoid every
role in the other core. The two variants also apply mode negation once
per occurrence, including both occurrences of a shared owner in the
original assignment.

All four complete output vectors match the frozen defect hashes. There
are 177 defective output families with the original signs and 176 with
the additional signs. The first defect is family 112 with coefficient
`-1/4` in all cases. The inverse of every literal scalar event, bridge,
and terminal restores the unit input exactly. This establishes that the
failure is an output-restoration defect of these reversible words.

The exact input is constant on the native payload and cover. Each
complete retained native operator and each route or translation fixes
this sector. This uses the pinned native-core and paired-phase contracts;
the review does not repeat their native kernel checks. A successful
constant-sector replay would not establish a native construction. A
nonzero defect in this sector is enough to reject the fixed content word.

## The first dependency

At position 1, raw call 0 sends the first promoted owner 13005 into target
family 112 with coefficient `-1/4`. This is the actual first mode column
of the literal core. At position 9, the next backward call sends `+1/4`
to X-family 0. The later forward call at position 29 restores family 112
to zero, but does not remove family 0's value. At position 324, the retained
terminal sends its negative into family 112. Family 112 is not changed
after this event.

Owner 13005 has no later promoted occurrence. Its later active data calls
are 117 and 127, after the defective output has closed. A suffix sign can
restore this owner's initial sign, but it cannot remove the earlier
data dependency. These facts concern the fixed schedule and input; they
do not prove that every use of productive owners must fail.

## The alias repair

The checker reconstructs the original 36 incidences by intersecting the
two complete owner sets in each pair. These give 37 bad promoted positions:
15 first-mode/second-helper cases, 20 second-mode/first-helper cases, and
one shared mode owner that occupies two positions.

For every bad position, it recomputes all ordinary width-nine donors in
the same call whose owners are absent from the other core. It verifies
each reported matching and the exact exchange of whole source-job IDs.
The 37 exchanges change 74 positions in 14 calls. They leave every active
data family, every complete call owner set, all 626 schedule positions,
and each call's complete job multiset unchanged. Every destination
width-nine slot has canonical I-to-FULL endpoints. The destination's
slot-specific whole-job wrappers must remain in use.

All 69,120 jobs keep their time, route, and pending axes. Thus the accepted
strict owner windows remain valid. The remaining 1,369 shared occurrences
are ordinary helpers in both cores. The independent check confirms the
same pending child and disjoint coordinate intervals for each such pair.
The accepted complete-helper contract remains a dependency; this review
does not repeat the earlier deep 280-slot chart audit.

Within fixed complete call owner sets, each of the 37 bad jobs must leave
the mode positions. Each needs a different ordinary position, and each
replacement comes from an ordinary position. Hence at least 74 positions
must change. The frozen 37 disjoint exchanges attain this bound. This
does not give a minimum over changed call times, owner stock, or graphs.

The conditional centre-removed native rank mass is 1,032,192. It has no
new family or child from the alias exchanges. It is not a supplier
profile because the productive output contents are wrong. Exact native
views for inherited old-mode prefixes, the output decoder, the complete
finite invoice, and recursive admission remain separate obligations.

## A bounded assignment escape

[screen_first_owner.py](screen_first_owner.py) tests all 202 admissible
single exchanges of call 0's promoted role 225 with an ordinary width-nine
role. All other repaired calls and graphs stay fixed. Each exchange
retains the full job contract and avoids a new cross-core alias.

For each candidate, set its newly promoted owner to one and all other
productive fields to zero. Both sign variants have a nonzero output
defect. [FIRST-OWNER-EXCHANGES.json](FIRST-OWNER-EXCHANGES.json) gives the
first defect for each of the 404 cases.

This screen evaluates the exact dyadic word in the field modulo 65537.
The modulus is prime and odd, so every power-of-two denominator is a
unit. A nonzero reduced defect proves a nonzero rational defect; this
is not a probabilistic inference. The endpoint algorithm is also checked
against both independent literal base replays. Its use on each candidate
requires the verified absence of cross-core mode aliases.

The result rules out each single reassignment in this stated class.
It does not rule out several coordinated exchanges, a changed graph,
a paid correction, or another controller. Moving owner 13005 out of the
first mode position can remove that particular witness, but every legal
single replacement has a witness on its own arbitrary input.

## Reproduction

From the workspace root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/circuit-interface/productive-owner-review/review_drift.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/circuit-interface/productive-owner-review/screen_first_owner.py
```

Expected statuses:

```text
PASS_INDEPENDENT_PRODUCTIVE_OWNER_DRIFT_AND_ALIAS_REPAIR
PASS_ALL_SINGLE_FIRST_MODE_EXCHANGES_HAVE_EXPLICIT_DEFECTS
```

No unresolved material finding remains in the stated counterexamples or
same-call alias repair. No full productive-owner construction, complete
decoder, or kappa improvement is claimed. The review used an independent
OpenAI Codex agent, not an independent human reviewer.
