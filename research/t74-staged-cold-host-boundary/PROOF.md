# A coordinate that host-only staged recovery cannot observe

This is a scoped obstruction, not a new multiplication bound. Both literal
PR2823 hosted words for `473 -> 277` are pinned in `SOURCE-PINS.json`.
Indices below are zero-based B-gate indices. The inherited frame engine and
source words are copied without modification; the new argument is the
information-invisibility argument below.

## Contract and exact target

Keep the inherited scalar word, all warp interfaces and target port ends fixed.
After the final inherited read of host 277, at B1201, permit any finite sequence
of additional scalar additions **writing only host 277**, at arbitrarily
separated B/restore positions. Arbitrary rational coefficients, repeated reads,
and host scalings do not help the argument. Arbitrary legal monotone frame
refits are allowed, but no new warp, write to another register, precomputation,
or changed target end is allowed. Require the host's final frame to have rank
at most eight.

The exact recovery objective here is the reference value `z` immediately after
the new host warp. The inherited rational inverse-substitution calculation gives,
at the cut immediately before B1202,

```
z = x277 - x100 - x226 + x54.
```

PR2823's separate normalized zero-frame inverse-prelude repair is the route that
binds restoration of this reference to the desired original dirty-input
contract. It does not change the frame argument. This package does not reprove
that complete operator fixture or claim a native supplier.

Every ordinary live register is an independent coordinate at the cut: the
prefix is a composition of shears between distinct live registers, nonzero
scales, invertible operator warps, and initial correction shears. In particular,
the centre cut consists of ordinary invertible additions. The checker verifies
these premises on the pinned word. The normalized prefix repair also uses only
invertible shears and a zero-frame inverse warp.

## Frame witnesses

The unavoidable host frame after B1201 is

```
H = span(260, 128, 68, 33, 17, 8, 3).
```

It has rank seven and contains vector 33. That vector is outside both target
112 and target 169's fixed port-hyperplane ends: its dot product with each
respective port is one. All inherited warps occur before this cut (the latest
position is 1176), so no later warp or equality pin can reset these frames.
The host is not used again by the inherited B or restore word.

If an added recovery gate reads source 100 before B1429, its common frame forces
H into source 100. The inherited gate B1429 reads 100 into target 112, forcing
vector 33 into that target and violating its end. If source 100 is read after
B1429, its already forced frame joined with H has rank nine. Thus it cannot be
read by a rank-at-most-eight host at any permitted time. Source 67 has the same
dichotomy at B1430 and target 169. Targets 112 and 169 cannot themselves be read
by the host at any time, because their fixed ends exclude H.

The late source floors are, respectively,

```
100: span(256,128,64,32,16,9,4,3)
 67: span(256,128,64,40,24,4,2,1).
```

Each has rank eight; each joins with H to rank nine. Additional host-only gates
can only enlarge frames, so testing these necessary lower floors is valid for
every allowed refit and every arrangement of additional recovery gates.

## Information-invisibility proof

Vary only the independent cut coordinate `a = x100`; keep every other cut
coordinate fixed. Initially the host has zero coefficient on this variation,
whereas its required reference z has coefficient -1.

The checker propagates this variation through every remaining inherited scalar
gate. Only registers 100, 67, 112 and 169 ever carry it. The only changes are
B1428, which gives 67 coefficient -1/2; B1429, which gives 112 coefficient -1/2;
and B1430, which gives 169 coefficient -1/2. No subsequent gate changes this
support. All four registers are unreadable by a valid recovery gate, by the
frame witnesses above.

Every value an admissible new gate can read therefore has zero a-coefficient.
Host-only additions and scalings preserve the host's zero a-coefficient by
induction, even with arbitrary coefficients or repeated reads. They cannot
produce the required coefficient -1. This rules out all host-only staged
recovery under the stated contract, beyond PR2823's contiguous-block census.

## A bounded natural-bank screen

`exploration/natural_bank_coordinate.py` separately tests an alternative:
read already paid, naturally accumulated cold FULL-ended helpers after their
final inherited use, with no new writes to them. It permits any rational linear
combination of such bank rows and arbitrary preloads of initial cold-helper
values into the host at frame zero. Each bank's minimum final paid frame must
join with H at rank at most eight.

Exactly 22 banks pass that necessary frame filter on each pinned provider.
A separately implemented free-operator single-column propagation shows that
all 22 have zero coefficient of original input 100, whereas the needed recovery
increment has coefficient -1 on that input. Hence even an arbitrary linear
combination of those unchanged retired-bank rows cannot supply the recovery.
This is a necessary-coordinate screen, not an optimality result for changed
precomputation circuits. New writes before retirement, changed warps, new helper
lifetimes, and changed target contracts remain outside it.

## Checks and remaining work

`python3 -I -B verify.py` recomputes the source-bound main receipt. The same
command with `-O` produces identical output. Each provider includes a positive
rank-eight single-read fixture (source 54), plus rejecting controls for a
changed coordinate-to-target gate, an inherited host use after the cut, and a
noninvertible prefix. `RESULT.json` is the retained stdout; the script recomputes
its findings rather than trusting or automatically comparing that file.

A separate agent independently checked the frame facts using explicit sets of
GF(2)^9 vectors and a register-version inclusion graph, and independently
propagated the sparse variation. That is separate AI verification, not
independent human review or formal proof-assistant verification.

An improvement now needs a genuinely changed information route: for example,
put the missing input-100 component into a compatible bank before the target
barrier. Any such construction must include preloads, changed output
compensation, bank/host restoration, cleanup, owner inventory and the complete
rank-neutral cost delta. No such paid construction is provided here.
