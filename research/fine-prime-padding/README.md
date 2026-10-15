# Fine source-prime padding

Conditional **kappa = 0.001679754788150048** in
`T(n)=O(n (log n)^(1-kappa))`, above PR1758's reported
0.001679745508802299051546 by more than 9.2793e-9.

Choose the source primes closer to their dyadic targets, with relative gap
Theta(p^-2) instead of Theta(1/d). Trudgian's established prime theorem
supplies enough distinct primes eventually. The smaller Gaussian phase
increment reduces the remaining chirp guard. Coefficient setup increases to
O(p^2 log p) bits, paid polynomially per microbox; online records remain
O(p) bits. A larger polynomial halo is charged. The boundary uses the existing
explicit Strassen format, without relying on structured-solver stability.

The point is epsilon=0.9999999, beta=0.9999997,
xi=epsilon(1+q)-3/32+10^-64, with q strictly below the admitted supplier
endpoint. Its 56 strict checks pass; 14 invalid variants reject. Read
[the proof](FINE-PRIME-PADDING.md) for every changed hypothesis, norm and
precision bound, setup amortization, locality scale and paid cost power.
The extreme eventual cutoff and polynomial setup are not practical claims.

## Exact inputs and reproduction

The supplier is unchanged from PR1699, head
`9f0c00d353b521c6840729861e48d7d0da20d345`:
global profile `{1:1560432,2:336336,3:278724,4:84912,5:54612,8:5328,48:22748}`,
dimension 73, live width 66304, 319680 roles, 249 base/417 extra calls,
prefix 1441 charged at 2048 and row coefficient 19545 below 20161.
Its certified complex endpoint is
`335950991225108904267/200000000000000000000000`.

```sh
python3 -m pip install -r research/fine-prime-padding/requirements.txt
CXX=c++ BOOST_INCLUDE=/path/to/boost/include python3 -B \
  research/fine-prime-padding/verify.py --work /absolute/new-work
```

The checkout must contain the unchanged sibling
`research/t74-signed554-phase-fusion`. SOURCE-PINS.json binds its manifest
and the byte-preserved PR1758 inputs. The driver reruns the complete 18-stage
supplier admission without reuse flags, including ancestry, both native
words, independent maps, owners, strict T74, moments and geometry controls.
It then checks the retained gauge-free/union evidence and the new prime,
precision, locality and arithmetic controls. Generated output is isolated
under --work; the source packages may be read-only. MATH.json contains the
platform-independent mathematical receipt.

Finite controls include 30 explicitly proven prime witnesses with exact
capacity ratios, four bad-prime mutations per fixture, and an actual underflow
witness for the old absolute weight precision. These are small fixtures;
the asymptotic prime guarantee comes from the cited theorem. A separate
implementation checks all nine paid powers. None of these finite checks
proves the inherited all-size compiler or a practical cutoff.

## Scope and credit

The result remains conditional on the inherited all-size compiler, common-label
and mutable-source realization, whole-call hosting, semantic online precision
C1=1, fixed-tape/prime-packing implementation, equal-chunk interchange,
exact recovery and analytic transfer. The written prime/precision/locality
replacement is additional mathematical material requiring review.
No unconditional multiplication theorem, independent human review or
proof-assistant verification is claimed. The selected record is unchanged.

Prepared by Chafik Boukhalfa with substantial OpenAI Codex assistance.
New material is Apache-2.0. Credit Tim Trudgian for the cited prime theorem;
Vlado Vojdanovski for PR1673; IdeaOuter and the PR1758 contributors for
fractional-shift interiors and per-visit union accounting; Jeremy Kothe and
the package contributors for the radix-union lineage; LeverRank for the
second schedule simulation; and the complete supplier lineage retained by
PR1699. PR1672 has priority for the signed-554 kernel. Original notices remain.

## Open next questions

1. Independently review the setup/online precision separation and uniform
   conditioning. Start with proof sections 2-4 and the source audits.
2. Review the enlarged locality window and its tape/core accounting in
   sections 5-7. The finite verifier does not implement an enormous full call.
3. Improve the finite supplier endpoint, with exact pricing and fresh native
   admission. This package changes only the outer transfer.
