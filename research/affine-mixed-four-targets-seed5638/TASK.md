# Cycle 2 task card: mixed affine targets in four registers

- Track: `bit-mechanisms`
- Task: `bit-new-register-model` (selected from the eligible suggestions for the accepted seed)
- Accepted seed: `5638c49abc39ff4644ef875d73a20996`
- Discarded excluded-track draws: `b7968416bea4144aa0ebc623c8c484f0` (`adversarial-audit`), `4cdd0654c4363d88f47619ea1f700153` (`adversarial-audit`)
- Catalogue priority revision: 3
- Base commit: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`
- Scope key: `7f5f4426ef796683c485/AGL2-F2/r4/mixed-targets-h-hi-tx-ty/rank-saturation-6-7`

## Question and changed premise

In the noncommutative group algebra `F2[AGL2(F2)]`, can the four-register target
`diag([h], [h^-1], [t_x], [t_y])` be realized in fewer than its direct 10 paid
calls, where `h(x0,x1)=(x1,x0+1)`, `h^-1(x0,x1)=(x1+1,x0)`, and the paid
labels are exactly `{a,b,t_x,t_y}`, with
`a(x0,x1)=(x0+x1,x1)`, `b(x0,x1)=(x0,x0+x1)`,
`t_x(x0,x1)=(x0+1,x1)`, and `t_y(x0,x1)=(x0,x1+1)`? A call is
`D_N(g)=I+([g]+[1])N` for any rank-one idempotent `N` in `M4(F2)`; free
`GL4(F2)` mixing is included by moving each scalar map through the paid gates,
conjugating its idempotent, and using augmentation to force the net scalar map
to identity.
The target/input registers are arbitrary, with no clean-helper assumption.
This changes the operation alphabet from Cycle 1's rational address-frame
model to a finite nonabelian affine group and changes the target family.

## Price screen and bounded experiment

The homogeneous affine 3-by-3 representation gives target displacement rank
`2+2+1+1=6`; each paid generator call changes it by rank one. Thus the
optimistic floor is 6 versus the exact 10-call direct word, leaving at most
four calls of local headroom before physical/supplier charges (which are outside
this finite model).

Test whether the rank floor is attainable or can be approached at 7 calls.
Enumerate every rank-one idempotent in `M4(F2)` and every one of the four
labels. Search every rank trajectory that can take the exact target from rank
6 to identity in six or seven calls: six strict rank drops for length 6; six
drops and one neutral step for length 7. The evaluated homogeneous-affine
representation is a necessary condition for exact group-algebra equality.
If it finds a word, replay that word in the full formal group algebra. Stop
after this q=6/7 screen and one exact construction attempt; do not claim that
q=8..10 are excluded.

Positive evidence: a full formal group-algebra endpoint and exact replay.
Negative evidence: complete trajectory coverage for q=6 and q=7 in the declared
representation, a direct 10-call positive control, and dropped-factor/wrong-
target controls. Keep all claims scoped to this tuple and paid alphabet.

## Nearest work and claim status

The final pre-submission refresh at 08:28 UTC covered all 419 open PRs and
375 Discussions with complete pagination and no warnings. Direct predecessor
PR #1333 (closed, head `7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2`) proves the
six-call cost when every rank-one affine displacement is paid; this cycle
restricts to `{a,b,t_x,t_y}`. Open PR #1711 uses two affine targets; PR #1716
uses a restricted three-register AGL2 triple. Active Discussion #1738 concerns
a three-register UT3 central pair with `{x,y}`, a different group, target, and
search method. Cycle 1's PR #1733 is a rational address-frame obstruction and
does not overlap this binary-affine label restriction. Discussion #1317 is
the completed coordination thread for PR #1333. This cycle's claim #1727 was
posted at 08:04 UTC and expires at 08:55 UTC:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1727.

## Outcome and handoff

The full rank-one affine alphabet has optimum six calls for this target by PR
#1333. In the fixed four-label subalphabet `{a,b,t_x,t_y}`, the q=6 strict-drop
search and q=7 six-drop/one-neutral search both have empty terminal frontiers.
Together with the displacement-rank floor and direct ten-call word, the
restricted-alphabet minimum lies in `[8,10]`; q=8 and q=9 remain open. The
exact package is `research/affine-mixed-four-targets-seed5638/`, submitted as
open PR #1745:
https://github.com/CrocSwap/integer-mult-bounds/pull/1745. No kappa change or
physical supplier admission is claimed.
