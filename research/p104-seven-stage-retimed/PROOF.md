# Conditional seven-stage extension of the retimed P104 construction

This is a conditional candidate, not a certified new multiplier bound or an
independent validation of the five inherited premises. An independent reader
reproduced its rate arithmetic and found no counterexample to the role count,
but did not discharge the exhaustive all-size binding from the seventh
dispatcher to the source's physical scratch inventory. The resulting clock
and stock conclusions additionally assume that specific bridge. The base is the exact
[PR #8042 retimed supplier at head `3d33cb0c8a523b66d91e8de8250b85d0a436eb35`](https://github.com/CrocSwap/integer-mult-bounds/pull/8042),
with a different fixed profile and the separately priced seventh ordinary
stage below. Its original result only certifies the listed profiles and its
`activation.py` explicitly caps their count at six.

## Scope of the raw comparison

The binary [transfer](https://github.com/aliromman/integer-mult-bounds/blob/3d33cb0c8a523b66d91e8de8250b85d0a436eb35/research/retimed-native-multiplier/TRANSFER.md) retains all 18,906 productive and
104,904 paid tags of the same 36-call raw word and uses no binary rank-one
split. Its rational transport trial is

    c = 4484997569314581 / 2^60
      = 0.00389011528659446038230784736811074253637… .

The original independent directed receipt was reproduced locally; it checks
the 24-cell binary coupling, the 31-cell numerical coupling, and the entire
five-profile `RESULT.json`. Its directed binary surplus is about
`1.0126850924756136e-18`. This trial lies below the previously audited
fixed-raw-word crossing `0.003890115286594461129996942…`; the retiming does
not itself establish a larger crossing or evade that fixed-word comparison.
The following stage-count change is a separate proposed construction. Nothing here
rules out other words, tariffs, couplings, or architectures.

At six stages and the unchanged `249/250` recurrence, even before any debit
or strictness the retimed trial has ideal limit
`0.003890115286594444448395633477…`, below the six-stage 445 tick. The
seven-stage ideal limit is `0.003890115286594460318572198512…`, so there is
room for a real invoice above the prior six-stage limiting ceiling.

## Exact profile and price

Select `H_i = 10^12 * 16^(i-1)` for `i=1,…,7`, `H_M=36000`, `eta=39/10000`,
`g=10^-20`, and `kappa=0.003890115286594460`. Keep #8042's binary and
numerical coupling, raw ownership, calendar, singleton charges and numerical
debits. The seventh ordinary price is `kappa+5g`.

For each stage the source prices
`covered_i = c - 7/(2H_i)` and checks
`b_i < min(eta, (249 covered_i+b_(i-1))/250)`. The first six rates use
the #8042 strict selector `(floor(10^21 limit)-1)/10^21`. The exact
first six booked rates are

    0.003874554821962082539
    0.003890053044518055869
    0.003890115037612537575
    0.003890115285597681615
    0.003890115286590420074
    0.003890115286594440895

The seventh limit is `0.00389011528659446009657682429162658…` and its
booked price is `0.00389011528659446005`. The signed gate passes all
54 strict and four functional inequalities: its smallest strict margin is
`10^-21`, its ordinary margin is `10^-20`, and its numerical margin is
about `8.87403695156444e-8`. The checks reject `g=0`, the former `g=10^-17`,
and equality at either paid border. Reproduction and exact values are in
[check_seven.py](check_seven.py) and [RESULT.json](RESULT.json).

## Seventh-stage tape and storage accounting

The [actual ordinary dispatcher](https://github.com/aliromman/integer-mult-bounds/blob/3d33cb0c8a523b66d91e8de8250b85d0a436eb35/research/retimed-native-multiplier/machine.patch) derives its
maximum stage from `len(profile.rank_logs)` and passes that bound and tuple
to `admitted_stage`. The similarly named legacy six-stage default is not
called by that dispatcher. Give the seventh fixed stage its own set of
the same named spool roles used by the other six, with distinct delimiters;
seven sets are still a fixed finite collection of tapes, and every movement
is counted separately. The staged recursion only enters a lower numbered
stage. Every stage uses the same unpowered physical source and the same
paid `19/2` singleton factor. Thus the local chronological bounds, returned
owners, high-coordinate volumes, `N^92` true input fields and
`2^66 N^83<N^92` live-row allowance are repeated seven times; they are not
amortized away. `N=2^H` and every supplied `H>=3000`. The separate numerical
source remains at `H_M=36000`.

The ordinary clock source gives the stage-local recurrence

    B_i <= (133/10) J_i^14 (1+B_(i-1)),   J_i = 2^(1024 H_i).

The paid-tree and finite-stage induction lemmas in
[`lean/OrdinaryClock.lean`](https://github.com/aliromman/integer-mult-bounds/blob/3d33cb0c8a523b66d91e8de8250b85d0a436eb35/research/retimed-native-multiplier/lean/OrdinaryClock.lean) quantify over arbitrary natural stage counts.
One can also iterate the displayed inequality directly: an upper envelope
is `2^100 * (2*133/10)^7 * product(J_i^14)`. The actual rectangle factor
and this envelope fit the source's deliberately looser

    B_ord <= 2^40 * (133/10)^7 * product(J_i^16),

since `18 * 2^67 < product(J_i^2)`. Here
`sum(H_i)=17895697000000000000` and
`ceil(log2((133/10)^7))=27`, giving

    ceil(log2(B_ord)) <= 293203099648000000000067.

For the historical storage, each transition to a strictly earlier stage
can increase an ancestor input by at most two; the seventh stage adds one
such factor. The inherited `spineCap`, `stackHigh`, and `stripeTail` lemmas
in [`lean/OuterTickets.lean`](https://github.com/aliromman/integer-mult-bounds/blob/3d33cb0c8a523b66d91e8de8250b85d0a436eb35/research/retimed-native-multiplier/lean/OuterTickets.lean) quantify over the stage count. Substituting
`m=7` in #8042's explicit account gives

    D(s) = 2*2048 + 4096 + 4*(7+1) + 128 + 4*bitlength(s+128)
         = 8352 + 4*bitlength(s+128).

The source's full-row and true high-packet factors are unchanged. For a
conservative role count, assign every ordinary scratch interval a stage
index, one of the original role names, and its saved frame index. Charge
each of the seven stages the full source allowance `2^32(s+128)^2` rather
than sharing that allowance. The union is smaller than
`2^35(s+128)^2`. The native depth per binary stage is at most
`3+ceil(s/H_i)`, and the numerical spine at most `2+ceil(s/H_M)`, as in
`ACTIVATION-SPACE.md`; for the stated heights their sum is below
`32(s+128)`. Even with the three extra interval-count bits, the illustrative
historical head sum is at most
`2048+32*64+(7+12)+7+5+35+3 bitlength(s+128)`, over 4,190 bits below
`D(s)` before its additional bit-length term.

The earlier #8030 powered-forest convenience assertion `G<2^50` was
checked only for its listed ranks and is **not** used here. The present
last height exceeds that scope. The replacement is #8042's own unpowered
retimed calendar: at most `2N^6` births per time, each returning before
`N^77`, with fewer than `2^64` slots per raw context. Its direct bound
`2^66 N^83<N^92` covers the live raw cohort for every `H>=3000`. We reuse
the predecessor's independent outer role names and stage-depth count, not
its powered forest-height or powered stock bound. Mapping every nested
source call and scratch lifetime exhaustively to that inventory remains
an open proof obligation for the seventh stage, beyond the inherited premises.

The interval accounting is tied to actual source roles as follows. The
ordinary rectangle holds its opened and completed spools while `stage_body`
enters a `Receiver`; the predecessor callback has strictly smaller stage
number. A compiled receiver holds the `backing`, `staged`, and `result`
arena frames; a paid leaf adds `issued-leaf`. A direct line retains its
whole owner. A quotient line adds the `chart-line` split and completed
frames, a serial `chart-packet` argument and reply, and the arena's pending
and answer stacks. The stage-local two-frame `pipe` roles also include
`matcher`, `triangular-body`, `exposed-leaf`, and `weighted`; each keeps
its current and other spool until that pipe returns, erasing each previous
source before reuse. A `unit_scale` call retains `current`, `other`, and
`temporary` work tapes; an odd substep can additionally hold seven tapes
(three input, three output, and one scratch), and a carry substep one.
Its nested previous-stage exchange keeps the parent three until return.
The cold and scale passes hold their declared bucket/work-tape scopes and
erase them on exit; each uses no more than the source's 22-spool site cap.
The quotient packet is `high*body`, so the full high coordinates
stay charged. Pending packets and completed answers stay on their parent
stacks until collected; they are not silently reused. Owner route and clone
use one temporary tape, owner swap and XOR two, and every `work_tapes` scope
erases and releases those tapes. `OwnerBanks` allocates a vacant slot first,
and retirement overwrites the slot before reuse. The true raw cohort is
stored on the same backing arena head, and all simultaneous open raw units,
including their zero owners and returns, contribute to the single
`2^66 N^83` slot bound; they are not each granted a full input-volume
spool. The positive receiver holds its own incoming snapshot, outgoing
scratch and child arena. `Arena.child` suspends the parent, places the child
after the parent's historical high, requires zero live child owners at
return and truncates the child frame.

For the abstract `Spine`, `nested` means an actual native argument, not a
scratch or return page: a direct child has the full owner volume `V/B`, a
quotient child has `V/(BQ)` with its real high coordinates, and a positive
child has its actual row volume. Each is bounded by its entering parent.
An `entry` is the strictly earlier ordinary-stage call; its new row pad is
smaller than its entering extent, so its true argument is at most twice
the parent. Root rectangle padding is charged separately. Working spools,
saved replies and simultaneous highs enter the local allowance and the
historical head sum instead of being mistaken for recursive arguments.
This is the proposed source mapping, not an exhaustive verification of every
all-size execution path. It still relies on the physical supplier and lifetime
premises and on resolving the seventh-stage inventory bridge above.

The ordinary entrance cuts are

    1004016064322, 17004016064386, 273004016064450,
    4369004016064514, 69905004016064578, 1118481004016064642,
    17895697004016064706.

At the connected public exponent `A=17895697004016101255`, put `s=A+1`.
The exact first stripe margin is `8947848502008042018`; the monotone
all-size margin floor is `7829367439257035944`, both greater than 1,024.
The actual exponent for the private control envelope becomes
`1024*max(H_i,H_M)+ceil(log2(9)) = 17179869184000000000004`.
The calculation in the local receipt verifies all #8042 size, control,
precision and stock inequalities after its local count guard is widened
from six to seven. The stated storage conclusion remains conditional on
the source's physical high-water and allocation proof, including all
inherited scientific premises.

The fixed installer makes eight bounded recipe objects, seven binary and
one numerical, without opening any scale calendar. The binary coupling and
chart programs are shared; an extra recipe does not add a new raw word.
The largest entrance logarithm fits 64 bits, `92*max(H_i)` fits 71 bits,
the stop denominator has 67 bits, and the numerical rank has 36,001 bits.
These are far below the fixed install proof's `2^38`-bit item allowance.
Its `<2^68` indexed-action and `2^513` sequential-transition envelopes
have room for this one added bounded descriptor, provided the fixed
installer is run on this profile and its source pins are maintained.

## Outer controller at the changed stop gap

The written outer-clock proof takes `(128/g)^16 < 2^1024` only for
`g=10^-17` or `10^-14`; it must not be reused literally at `10^-20`.
The exact integer check instead gives

    ceil(log2((128/g)^16)) = 1176,
    1434 - 1024 + 1176 = 1586 < 1600.

The same polynomial absorption argument therefore fits the displayed
1600-bit allowance in #8042's final clock. With the new ordinary invoice,
assuming the seventh-stage inventory bridge as well, this yields the
conditional integer clock exponent

    E <= 293203099648000007921669,
    time(n) <= 2^513 + 2^E n (1+log2 n)^(1-kappa).

The `g` value is passed to the actual positive supplier as stop denominator
`10^20`. In the actual `power_le` routine this 67-bit exponent requires
at most 67 squarings and 67 selected multiplications; both factors are capped
at the current root-width ceiling after each squaring. Temporary products
therefore have at most twice the bit length of that ceiling, and the added
loop is covered by the numerical proof's existing polynomial control bound.
The controller gate and stop branch still require the original
analytic, all-column physical and numerical assumptions; fixed-size tests
cannot execute the enormous production fields. In particular `H_7` exceeds
this CPython host's `sys.maxsize`; computing `1 << H_7` was observed to
raise `MemoryError`, and would require over two exabytes even to store the
result's bits. The proposed
asymptotic statement concerns the inherited ideal finite-tape construction,
not a practical CPython execution or measured crossover. The smallest input whose
full positive-to-final-ordinary crossing is guaranteed is
`2^(ceil(2^A/6)-1)+1` bits, with the above `A`.

## Validation boundary

the pinned `check_complete.py` exactly reproduced the #8042 source's recorded
couplings and five profile receipts. [check_seven.py](check_seven.py) applies its
arithmetic to the new profile; its local `activation.py` differs only in
the explicit 6-to-7 stage-count guard. [check_runtime.py](check_runtime.py)
checks actual threshold selection, installed recipe objects, stop-policy
propagation, and a feasible signed product. With the new profile object,
the physical reduced-rank product returned `-345550037539`, the first five
coefficients `[11811,10996,4152,868,77]`, 157,248 H calls and 138 shuttles;
the input restoration and output guards passed. The registered replay exposes these separate controls. This is a conditional written extension of the source
estimates, not a kernel proof of the full physical scheduler or an actual
production-scale run. Independent replay of this new profile, especially the
seven-stage historical tape binding, remains needed before presenting it as
a certified multiplier result.
