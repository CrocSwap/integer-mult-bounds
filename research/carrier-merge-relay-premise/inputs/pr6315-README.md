# Network-coded owned carriers on P104: stops, shedding and pair merges do not go below 56

`research/fragmentation-ceiling/PROOF.md` §6.7 lists "network-coded carriers with stops and shedding" as one door
outside the A30-CUT scope. This package tests that door on the selected PR6030 local word and its 8-carrier code,
which PR6166 shows is unique up to sign.

**Scoped negative result. No new word or kappa is claimed.**

## Result

| Mechanism | Result | Evidence |
|---|---|---|
| stops, copies, branches, relays through public helpers | a carrier pays at least its COPY cost (the F2 pairing rank) | Lemma S, PROVED-LEAN |
| additions and shedding along one path | equivalent to loading at the top | Lemma A, PROVED-LEAN |
| any merge of k carriers with a tail of length <= 1 | costs more than 7k | `merge_count`, PROVED-LEAN + finite facts |
| any merge of two carriers | costs at least 14 = 7 + 7 | `pair_merge`, PROVED-LEAN + exhaustive check |

The proofs use a dual picture. A frame C is replaced by C^perp. Public ascents shrink the dual for free, and owned
descents grow it at their price. The union span of every visited dual grows by at most the paid amount. With this
one inequality, stops, copies, branches and relays reduce to the COPY cost. For merges, each carrier must also
reach the other carrier's normal g_a. Since g_a . l_c = 1 for a ≠ c, each content tree then spans all of F2^9.

The PR6030 word already uses a coded owned network. It has 31 owned lifetimes, 14 owned-to-owned additions and
owned reads at frame dimensions 0-8. It is tight against the seven dimension cuts of
[p104-owned-coding-boundaries](../p104-owned-coding-boundaries/JOINT-BOUNDARY.md), with exactly 8 crossings on
every level 2..8 (owned paid 56).

## Reproduce

```sh
python3 -B research/p104-network-coded-carriers/verify.py
```

The check uses the standard library only and takes about 17 s. Expected marker: `PASS_P104_NETWORK_CODED_CARRIERS`.
It replays the PR6030 word exactly and checks the Y/X frame facts and the 8 carriers. It extracts the delivery lines
(removed E8 root lines), the normals g_c and the receivers R_c. It checks the Lemma S equality (dual walk cost =
pairing rank = 7), the unique masked decoder (d_jc = ±2) and the `merge_count` spanning facts. It runs the
exhaustive pair `nocover` check (28 pairs × 2 ratios × 11,811 subspaces) and compares the result with
[RESULT.json](RESULT.json).

Lean (optional, not run by `verify.py`): `cd lean && lake exe cache get && lake build && lake env lean Audit.lean`.
Every theorem prints only `propext`, `Classical.choice` and `Quot.sound`. The Mathlib pin is the one used by
`p104-carrier-code-uniqueness`.

## Relation to existing work

- `fragmentation-ceiling` §6.4 (single-commodity lemma) and §6.7 (the door). Lemma S is the P104 form of the
  single-commodity statement, with arbitrary stops and public relays.
- `p104-owned-coding-boundaries`: its seven cuts close arbitrary sharing for a fixed public boundary with
  dimension-1 deliveries. This package removes the boundary premise for stops, shedding and pair merges.
- Matarener's open PR6267 (owned-lineage factorization) asks whether its floor extends to merges. Pair merges are
  answered here.
- `p104-signed-mixed-carrier-bank` builds mixed carriers in a relaxed frame model. Here the actual frame rules are
  used, and pair mixing does not pay.

## Open next questions

- Merges of 3 or more carriers with tails of length >= 2, and multi-stage merge trees.
- Codes with 9 or more carriers (masked floor beyond rank 8).
- Decoders reading X (P-ATOM).

Prepared for Matarener with Claude (Anthropic), via Claude Code. Apache-2.0.
