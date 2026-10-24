# Independent review of the varying-response controller

Verdict: accept the existing all-m reciprocal controller as a conditional
appendix. The historical producer freeze remains unchanged. This review
supplies a separate proof check; it does not infer correctness from that
freeze. The reviewer read PR-DESCRIPTION-STANDARD.md.

First check the unit-response network. Let x_m=0 and w_-1=0. Immediately
before the backward call on pair i, its X value is x_i and its Y value is
x_i+y_i+w_(i-1). The backward call leaves w_i=-y_i-w_(i-1) in X. The plus
bridge adds x_(i+1). The forward call leaves x_i+x_(i+1) in retired Y.
The minus bridge restores w_i in retired X and prepares the next Y as
x_(i+1)+y_(i+1)+w_i. These equations prove the recurrence for every pair.
The descending final bridges give w_i+w_(i-1)=-y_i. On Y they subtract
the already reduced x_i from x_(i-1)+x_i. The endpoint is (-y_i,x_i).

For general routed E_s, compare each physical content row with that ideal
network. After F0 and the first X code, X0 is E1^-1 x0 and Y0 is
E0(y0+x0). The pre-B1 Y factor removes E0. At each subsequent B_s the
active X is E_s^-1 times the ideal value and active Y is plain. The call
therefore produces E_s^-1 times the ideal difference. Left multiplication
by E_(s+1)^-1 E_s gives the required next X code, without any commutation.
The next X preparation gives equal codes on the two bridge operands.
F_(s+1) cancels its inverse code in the Y update. The minus bridge is
therefore valid, and the next transition prepares the following B call.
Final X decoding precedes every descending full bridge. This is an all-m
induction on arbitrary independent inputs.

There are three initial factors, m active-X transitions, m-1 next-X
preparations, m-1 next-X transitions, and m final decodings: 4m+1 in total.
A common routed E removes the 2m-1 transition factors and leaves 2m+2.
The note's different three-factor one-pair identity is also valid; neither
factor count is asserted to be minimal.

The general three-call equations have the stated product order. Vanishing
of the final X-from-x block forces b1=E1 a0 E0^-1. The Y-from-x block then
forces b2=a0^-1 E1^-1. The Y-from-y block forces a1=E2^-1 a0^-1. Finally,
the X-from-y block forces a2=b0^-1 E0 E2. These deductions also prove
necessity under the stated invertibility assumptions. They do not permit
reversal of a stage transition.

The terminal equation A V J0=W is direct block multiplication. It uses
Q^2 Q^-1=Q and introduces no E/Q commutation. The uncoded common-E
endpoint is diag(Q E Q^-1,E^-1) relative to the raw input. The actual
564 off-diagonal source entries have distinct port directions, so the
retained character witnesses distinguish each paired intrinsic line.
No untyped scalar decoder is supplied by this observation.

The unchanged source checker was read and run from copied closures in
normal Python and with -O. Both complete receipts match the frozen receipt
byte for byte. It checks all input blocks for one through eight pairs,
common and varying free ordered symbols, all 19 retained content events,
ten idle sites, the terminal equations, all 564 source witnesses, and
six mutations that remove a code or reverse a transition. It imports no
producer proof engine. The finite cases supplement the induction; they
do not replace it.

This result is useful beyond the parent package's one-pair residual-code
identity because it supplies an explicit all-pair placement with varying
stage operators and a raw physical endpoint. Its stronger endpoint uses
stronger access premises, including future-stage products at specified
completed-X cuts. It does not establish those premises. In particular,
a native transpose response is not a native inverse response. No new
native construction, source access, owner admission, map price, precision,
or complete multiplication exponent is proved.
