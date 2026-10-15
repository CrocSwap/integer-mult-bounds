# Completed entrance banks on the PR200 bit word

This applies PR197's construction (see its PROOF.md, sections 1-7) verbatim. The only change is the source word: PR200's terminal-modified bit word instead of PR187's. This file lists only what changes. Every argument not restated here is PR197's, with the same inherited interfaces.

## 1. Actual physical chains

PR200 at `a1175449f34d39ff933d9d8ab23ced1f32b290ec` emits and fully checks its bit word: 18,908 logical auxiliary roles, 1,760 donor/recipient splices and 34 PR166 terminal sinks, hence 17,114 physical chains. Its verifier checks the F2 identity on all formal columns, the integer decoder, the exact frames, the prime witnesses for all 24,401 used frames, and the terminal substitution.

There are 3,960 logical gauges:

- 1,760 rank-21 gauges are recipient starts internal to the paid splices;
- 2,200 rank-20 gauges, on 220 distinct frames, start otherwise unpaired chains.

The packing checker verifies all of the following from the frozen word:

- no donor is gauged;
- donors and recipients are disjoint;
- every recipient is gauged;
- no sink role is a donor, a recipient or gauged.

Deleted sink registers have no residual. The 2,200 rank-20 gauges supply rank-4 entrance residuals, and every other physical chain has a rank-24 residual.

## 2. Charts

Each distinct rank-20 frame is given by four integer annihilator rows `A` in PR200's frame table. The checker computes an exact integer basis of `ker A` (20 vectors) and the G-orthogonal complement `15a-(sum a)1` (`G=9I-J`). It checks orthogonality and both inverse identities of the 24×24 chart, and replays its fraction-free elementary factors. The largest chart has 171 factors. Numerators are at most 5, denominators at most 18, and every nonzero integer is below 2^80, so the charts remain invertible at every allowed prime `q > 2^80`.

## 3. Banks and scheduling

There are three full copies, and each physical chain occurs nine times:

```
6·3300 = 9·2200,      2·3300 + 3·42542 = 9·(17114 − 2200).
```

The chain/bank multigraph (154,026 incidences, degree 9 at each chain and at most 8 at each bank) receives a proper 9-edge-colouring. An independent check verifies every incidence, and a duplicated colour is rejected. Scheduling, the cover bijection and the endpoint identity are PR197's sections 3 and 4.

## 4. Profile, routing and moments

Take three copies of PR200's recounted histogram and remove its 6,600 rank-60 exterior children; everything else is retained. Then:

- `W = 3·2·1760 + 45,842 = 56,402`;
- deficit `72W − mass = 5,808`;
- maximum child 22.

The conservative extra selector bound is `18((W−1) + 17114·72·(171+71)) = 5,368,513,266`. It is paid as in PR197 section 5.

The packed coarse saving is `683528191056257/10^18`; the next grid point fails under two independent rational enclosures. Three finite ordinary-leaf levels start from PR200's completed ordinary supplier `a_0 = 677340914792209011107/10^24` (its certified θ-wrapper) and give `a_3`. All gaps `a_j < c < 1 − a_j` are positive.

## 5. Assembly

PR193's complex supplier, `700918443859411/10^18`, does not bind. With `eta = beta = 10^-24`, the unchanged 47-constraint balanced assembly certifies

```
kappa = 683061299399923/10^18.
```

The next `10^-18` point fails for these fixed suppliers and parameters.

## 6. Limits

The finite checks establish the charts, banks, profile, moments, leaf recurrence and assembly arithmetic. As in PR197, the following remain inherited assumptions:

- the completed-core contract;
- the general Clifford interface;
- uniform weighted compilation;
- restored rows;
- fixed-tape transfer.

PR193's disclosed limitations on the complex side are also retained.
