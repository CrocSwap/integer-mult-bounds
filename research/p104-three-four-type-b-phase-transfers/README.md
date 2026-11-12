# Three and four simultaneous Type B phase transfers

**NO VERIFIED GAIN. Exact conditional κ change 0%.** All 10,400 triple and 14,950 quadruple choices change the signed Type B endpoint on the exact [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. Two exact methods give a nonzero witness for every case at q=−1 with all body variables set to one. The complete scope is exhausted with zero survivors and zero unresolved keys.

Choose exactly three or four of four original signed singleton idles and the same number of 26 original even idles with mask sizes 2–8. Demote the former and promote the latter. All literal clocks, owner roles, body masks, 17 J blocks and other events stay fixed. Overlapping masks are included. Different pairings of the same selected donor and receiver sets yield the same word. [Proof and exact scope](PROOF.md)

## Price before support

The independently reproduced comparator is [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, conditional κ = 0.00364665195644. Its complete signed invoice has 110,519 paid and 22,461 productive positions, signed rank surplus 1,424 and zero empty credit. Each selected receiver of size m trades paid ranks (9,8m) for (8,8m+1) across eight Type B ports. Both position counts and both rank masses stay fixed.

The directed optimistic upper is about 0.17095747230019032 raw for three transfers and 0.22541521474570153 raw for four at the incumbent raw crossing. The replay emits the exact rational bounds. They share the same four donor clocks, so the larger bound is the whole-stock upper. It grants every ancillary cost free. One extra raw paid rank-one position makes the best complete margin negative from the incumbent bracket's lower endpoint through the retained BIT cap. At fixed κ 0.0040075385047236 the optimistic all-four complete margin is at most −139.519571366627 raw. The exact endpoint exclusion lowers the compatible saving to zero.

## Reproduce

Use CPython 3.12 with assertions and the standard library. From a clean checkout:

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-three-four-type-b-phase-transfers
~~~

From the package directory or a Git-free copy:

~~~sh
python3.12 -I -B replay.py --out fresh-receipts
~~~

The replay authenticates the exact source bytes, generates the complete price and 25,350 keys before either endpoint check, reproduces every modular and independent rational witness, and verifies the exact per-key agreement. It regenerates five plaintext receipts using the [pinned hashes](receipts/SHA256.json), and rejects a changed caller. No earlier run, checkout or download is required. [Verification and provenance](VERIFICATION.md)

## Open next questions

A changed surrounding interval or one changed clock could alter the endpoint obstruction. Start by specifying one exact changed signed interval and pricing every changed paid call, route and owner before an all-phase endpoint test. An additional paid rank-one call already exceeds this fixed-stock upper. Any surviving multi-stage signed idle requires all-width compiler binding at the same volume, exact ownership and restoration, and precision and tape verification.

## Attribution

[#7323](https://github.com/CrocSwap/integer-mult-bounds/pull/7323) supplied the exact two-transfer inventory and the modular and rational methods. [#7317](https://github.com/CrocSwap/integer-mult-bounds/pull/7317) excluded single transfers and established the earlier phase-transfer price. [#7315](https://github.com/CrocSwap/integer-mult-bounds/pull/7315) supplied the signed Type B decoder. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplied the caller, [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) the complete comparison, [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) directed arithmetic, and [#7342](https://github.com/CrocSwap/integer-mult-bounds/pull/7342) the directed derivative helper. OpenAI Codex and subagents materially assisted.
