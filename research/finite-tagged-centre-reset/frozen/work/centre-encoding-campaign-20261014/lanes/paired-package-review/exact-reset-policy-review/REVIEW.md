# Independent review of all retained pure-reset policies

Result: accept the complete finite family theorem in
`temporal-reuse/EXACT-TAGGED-RESETS.md`, SHA-256
`3a5f2bd40804d6106192f75c3abe7aefdf4d98c829cec03979bd79e8adb3d3b4`.
No material issue remains in its stated scope. This review also gives
a sharp improvement of the uniform surplus from 13 to 17.

The native response result covers every subset of the permitted reset
sites. It is not only a search over the displayed best policies. The
cost consequence still assumes the stated independent relative-error
width rule. It does not prove that every native algorithm needs that
width, or rule out a different centre encoding.

## Complete source and reset scope

The independent checker reads the pinned raw backward word and performs
a new exact replay of all 704 initial coordinates. It imports no
research checker. The ideal inputs at a native event include every
data and helper coordinate. A permitted reset is on the target field,
immediately after an existing scalar or native event before event
12995, and only when its ideal row is pure data or pure helper.
The reset must preserve that ideal row and have zero error derivative.

There are 860 permitted sites. All 644 sites before the first native
event have no native error to remove. The last pure-data site is event
637; the first native event is 9742. The other 216 sites are pure helper
sites. These counts and every underlying row are reconstructed from
the raw source. No target row is identically zero.

The ideal value stays unchanged under each permitted reset. Thus
earlier reset choices do not change which later sites are permitted
or whether a native input is mixed. In particular, the enumeration
does not assume that a reset changes a helper baseline to zero.

The accepted native frame typing is inherited. A native output error
is an arbitrary vector in the complete physical output field. On
conversion to that field's canonical coordinates, it remains arbitrary.
The same-frame scalar gates then give the exact response calculated
here. The argument uses this typing; it does not replace the native
frame with a plain partial transform on its listed basis vectors.
No new native phase cancellation is asserted.

## Why the group reduction is complete

The checker propagates Boolean supports from all eight centre outputs
back through the complete prefix. At an ADD it takes a union into the
source. Nonzero SCALE preserves the support. This graph contains every
possible scalar path without using cancellation. A reset can delete
a path but cannot add a path that is absent from this graph.

Of the 216 later sites, 180 have no Boolean path to any centre. They
cannot affect any centre response under any policy, even if another
reset removes an exact cancellation. The 36 remaining sites form three
groups of 12, with centre masks 15, 48, and 192. Every relevant reset
has support in only one group. Each of the 176 possible native error
ancestors also has support in only one group. All 176 native inputs
are mixed data and helper inputs.

These facts prove independent optimization. A reset in one group has
no path to an output in another group under any policy. A native job
cannot contribute a shared cost across groups. Therefore any global
choice has the sum of its three local costs, and any three local
choices form a permitted global choice. This remains valid if a scalar
operation is present in more than one filtered program: scalar program
overlap does not create a shared native error or reset choice.

Thus 3*4096 local policies cover all 2^36 effective global policies.
All earlier and Boolean-irrelevant site choices leave the native
response unchanged. The reduction is a proof about the complete family,
not an assumption inferred from a sample of costs.

## Exact independent enumeration

The producer uses integer vectors with a common denominator. This
review uses a separate scalar Fraction response for each centre query.
It reconstructs each filtered program from the raw Boolean calculation.
For every one of the 12288 policies it compares the complete histogram
of native rank and exact query support with the producer's payload.
It checks every local subset minimum and its policy witness, then
composes and checks all 255 nonempty global query subsets.

Every active rank is one or four. For every policy, a subset S has
exactly |S| active rank-four jobs. Thus minimizing the rank-one count
also minimizes every nonnegative rank moment. No trade between ranks
is hidden by a mass-only objective.

The minimum masses by query count are

    25, 44, 60, 65, 90, 109, 134, 153.

For all eight queries, resets after events 10008 and 10012 give
121 rank-one and eight rank-four jobs. The checker also performs a
separate full forward impulse propagation for all 176 Boolean native
ancestors under no resets, all eligible resets, and this best policy.
All 528 impulses agree with the reverse calculation. Their numbers
of zero responses are 44, 18, and 47 respectively. The all-reset policy
therefore cannot be substituted for the optimum.

The accepted inequalities in the source proof follow for every policy,
because each exact local minimum is a lower bound for that policy.
In particular, n1(S)>=8|S|+13 and mass(S)>=(65/4)|S|. The uniform
width threshold 97/65 follows from the latter inequality exactly as
stated in the source. This threshold is attained at sigma=1 by the
four-query group with mass 65, when all other new work is free.

## Sharp surplus of 17

The same complete minima give the stronger inequality

    n1(S)-4|S| >= 17

for every nonempty S and every policy. Equality holds for S={5} or
S={7}, with no resets: each has 21 rank-one jobs and one rank-four job.
These mode numbers start at zero.

For 0<=sigma<=1, put x=2^sigma. Then 1<=x<=2, so

    8^sigma-4^sigma = x^2(x-1) <= 4.

Consequently,

    sum_(j in C(S)) r_j^sigma - |S|*8^sigma
      = n1(S)-|S|*(8^sigma-4^sigma)
      >= n1(S)-4|S| >= 17.

The constant 17 is sharp over the declared interval and family. The
one-query examples above give equality at sigma=1. This conclusion
uses exact rational minima and an elementary all-interval inequality;
it uses no floating-point sample of sigma.

For nonnegative query allocations gamma_k, integrate the subset
inequality over S(t)={k:gamma_k>t}. The exact result is

    sum_j r_j^sigma max_(k in support(j)) gamma_k
      >= 8^sigma sum_k gamma_k + 17 max_k gamma_k.

The empty-support maximum is zero. The constant is again sharp by
putting all allocation on mode 5 or 7 at sigma=1. A policy that varies
by bit layer obeys the same inequality whenever its costs add by layer.
This does not by itself emit or admit such a varying native word.

## Reproduction and limitations

Run:

    python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/paired-package-review/exact-reset-policy-review/check_policies.py

Expected status: `PASS_INDEPENDENT_ALL_PURE_RESET_POLICIES`.
The checker accepts `--out` for a separate output receipt. It reads
pinned files and changes no producer evidence. It uses one CPU.

The theorem excludes new scalar edges, changed bases or encodings,
joint resets, reset sites at other times, changed native interfaces,
and correlated or lattice-restricted child errors. The finite physical
reset implementation and its complete margins are separate premises.
The negative cost result grants those operations for free. It also
grants the original width to any retained private-centre jobs; it does
not claim an emitted partial-centre controller.

There is no supplier or kappa claim. No PR, commit, or push was made.
OpenAI Codex supplied this independent review and the sharp surplus
extension. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
