# P104: Whitehead native objects and price targets

No kappa claim above #6936. Both words here are priced below it.

A Whitehead (t = -1) hosted pair has d = 0: the Y register ends with no y in it. That removes part of the hosts' public cost, but each host then needs an owned rank-1 move that the t = -1/2 pairs of #6936 do not. This package records the objects built for that, with exact replays, and the exact price a better native has to meet.

## What is here

| object | what it is | result |
|---|---|---|
| the hosted Whitehead word | #6936's mixed word with the outer Whitehead stage on the 8 hosted ports (stages 1 and 18). The native is #6936's plus one owned UP carrier per hosted port; the other 16 stages and the 96 two-chain ports are unchanged. Native, joint caller, invoice. | kappa **.0035927413806393823240**, S = 1504, **-0.9451%** against #6936 (.0036270188296). Not a candidate. |
| window native | A helper-free d = 0 native on all 104 ports: X = x + alpha y, Y = beta x for (alpha, beta) = (-2, 1/2) and (-1, 1). One window swap removes y; the beta crossing is 2 owned rank-1 moves per port. | Exact. Public 1652.63 R0 (1.13 above the floor 1651.50), owned 208. Over the replacement budget by 35.2 (outer) / 32.1 (rho = 1) per W call. |
| rho = 1 root | The connected all-Whitehead root: 38 fields, 18 stages at t = -1, product -I, rank G = n, irreducible. | Passes every requirement. Break-even 0.1395 UP per port-call; free-native ceiling +19.33%. |

`data/OBJECTS.json` lists the sha256 of every object. PROOF.md has the construction, the targets, the closed and open routes, and what is replayed here and what is quoted.

## Targets (exact, from the ledger)

- Break-even per port-call: **0.110** on the outer root, **0.1395** on the rho = 1 root. The the carrier costs 1.00, nine times over.
- A native that replaces #6936's at each W call must satisfy `owned <= 111.573 + T - dpub`, with `dpub` the change in public bill against 1702.405 and `T = 11.426` (outer) or `14.513` (rho = 1) R0 per call.
- Pass line with the helper-free public layer: **1.66 owned per port** (outer), 1.69 (rho = 1). The window native pays 2.0.

## Checks

```
python3.12 -I -B check.py                    # about 100 s
python3.12 -I -B checks/check_joint_w.py    # about 100 s
```

`check.py`: sha256 of the objects; exact Fractions replay of both natives; both Whitehead roots with controls; exact kappa and the invoice move; the target arithmetic; the 104-port native (regenerated, two engines, 100 mutants, 97 rejected, the 3 accepted are one true equivalence). `check_joint_w.py`: the joint caller replayed mod p at four characters, and the invoice rebuilt from the roots. Standard library only.

## Declared assumption: owned ascent

Both words move owned registers up as well as down (the Whitehead word: 8 carrier UPs on top of #6936's 23; window native: 104 UPs). The verifiers here accept an owned MOVE between nested frames in either direction, paid |change in dimension| as for a descent; public MOVEs still ascend strictly. The strict predecessor rule rejects the hosted Whitehead word at exactly 31 events (the 23 of #6936 and the 8 carriers) and the window native at exactly its 104 UPs. The cost argument and the precedent are those of #6883 and the P112 backward word, where owned registers are accumulated, moved up and read; see PROOF.md section 2. Every number here is conditional on that allowance.

## Not claimed

No candidate, no admission, no human review. The the hosted Whitehead word's second engine, physical streams, ordinary-call and outer checks come from its build record and are not rerun here. The window native is not joined to a caller: its 2 x 2 block is checked, the joint replay is not.

## Credit

Ali Romman (#5599: the split lemma and helper pricing the invoice rule rests on), CubeJerry (#6912 caller blocks, #6914 owned-rise argument, #6916 split application in #6936's word), unpaidmoon (#6930 width-2 phase test, used by #6936's physical audit, not rerun), icekylinx (#104 odd grid; the certificate S = 1125 in the replay), and the retained work of #6936 and its predecessors.

## Open next questions

1. A d = 0 native at t = -1 with at most 1.66 owned per port per W call on P104 and a public layer no dearer than 1652.63. Candidates: Gamma coupling on the Y registers after the bounce; shared landings for the beta crossing; a hybrid of Gram coupling and window swaps. See PROOF.md section 6.
2. Whether a shared owned run can carry many ports' beta crossings without leaving junk in the other ports' registers.
3. Whether a public schedule exists that gives the beta crossing through Gram-type coupling while the window swap still removes y.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
