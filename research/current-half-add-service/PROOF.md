# The terminal half-ADD bridge

## Exact source and local domain

Fix the candidate bytes in VENDORED.json. The source is the 150009-event
native word from PR7660 at d12b854d4825e9edfa3a3466909e1abf3525e929.
The verifier replays chart metadata through clock 100503. Both public
roles 210 and 457 are then in chart 218. Clock 100504 is the literal
half-coefficient ADD recorded in RESULT.json. The registry key includes
that clock and the complete event tuple.

Assume canonical finite signed fields on physically distinct tapes, with
the same shape and grid. Public and borrowed context heads start at their
origins. Each private work body is contiguous, has a blank historical
tail, and its head lies in that body or at its frontier. These are the
retained primitive's input premises. They are not inferred from the
local scalar values.

## Specialize the retained literal service

For coefficient -1/2, the retained rounded-ADD compiler forms
`2x-y+1`, takes mathematical floor after division by two, and checks the
final signed range. Since x is an integer,

```text
floor((2x-y+1)/2) = x - floor(y/2).
```

This includes negative odd y and the smallest signed inputs. The retained
carry proof and staged-installation proof apply to every positive width
and every nonempty complete complex field. The finite graph has 669 rows
and 210 states. Its only runtime instructions are the six existing tape
opcodes. The compiler's integer construction is not a runtime callback.

Let L=-2^(W-1) and U=2^(W-1)-1. For each fixed source y, the exact success
domain for x is the intersection of [L,U] with
[L+floor(y/2), U+floor(y/2)]. This interval describes final range only;
there is no divisibility restriction. On success the source stays fixed,
all heads return and private work is retired. Staging all components
before installation protects the whole public target on a late failure.
Failure does not promise clean work or returned heads.

The general retained cost theorem, with denominator two-adic exponent
one, gives 512(S+1)+64R+7(A_0+A_1)+16Q_c in physical/control units.
It includes source reads, carry work, staging, copying, rewind, head return
and both retirements. Its private backing bound is
max(H_0,3S)+max(H_1,3(S+1)). Positive setup, public, context and ancestor
charges are separate. These bounds do not use a conversion to the source's
815804876 ordinary-model units.

## Exact error transport through the current suffix

Write y=2k+b, where b is zero or one, including for negative y. The rounded
output x-k differs from x-y/2 by b/2. For grid step Delta the real error is
Delta*b/2. With N complex entries, there are 2N real components, so
squared field error is at most N*Delta^2/2. Equality holds when all real
components have odd source numerators and the rounded outputs fit.
For the 512-entry fixture, the squared error is exactly 256*Delta^2.

Now compare executions that differ only by this local error. Inspect every
one of the 49504 later events. No event reads role 210 as a source. The
only event that writes it is clock 100527:

```text
ADD 210,292,-1/2,218
```

The source of that update is unchanged between the two executions. All
other roles evolve from identical inputs under identical local operations.
The update adds the same value to role 210 in both executions. Its existing
difference is therefore preserved exactly. The same statement holds if
that later ADD uses a source-only rounded increment, when both executions
are in the service's range domain. It does not assert that the later
exact-halving service has already been replaced or is defined off-grid.

Role 210 returns in chart 218. Its error multiplier is exactly one. No
other public field and no owned observation or erasure receives this
one-site error. This follows from the literal dependency graph; it needs
no unitary bound for a later MOVE because no later MOVE acts on the changed
field. It still assumes the stated local operation semantics and distinct
logical fields. It does not prove those physical interfaces globally.

A separate positive forward-envelope pass gives peak and terminal gain
one, public squared gain sum one, and zero gain at all 75 later CLEARs.
An independently ordered backward pass returns the same coefficient at
the injection site. The exact dependency certificate is stronger than
this norm corroboration. A legal reversed ADD at 100527 would export the
error, and a legal SCALE there would change its gain; both controls reject.

## What this does not compose

The isolated arithmetic is a rounded alternative to the exact-child
service. It changes that service's numerical semantics. The later
half-ADD, all other scalar services and the complete caller remain open.
The local fixtures are admitted primitive inputs, not full-prefix traces.
The local native-return error is not a complete signed-caller error.

The word's operator, owned erasure, compiler, precision/tape and analytic
recovery assumptions remain. A full contribution to the multiplication
exponent needs all 17 local bindings, complete error transport, the common
physical tariff and rounded outer recovery. No such admission is claimed.
