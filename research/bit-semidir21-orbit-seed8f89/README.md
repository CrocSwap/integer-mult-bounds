# Three-register conjugacy-orbit target in the order-21 group algebra

**Scoped exact negative result.** In the operation model below, the target has exact paid-call minimum three. This changes the address group from the additive abelian model in the three-register obstruction. It does not change the selected integer-multiplication bound.

## Model and result

Let

```text
G = <a,b | a^7 = b^3 = e, b a b^-1 = a^2>
```

be the nonabelian group of order 21. Represent elements as `(i,j)=a^i b^j`, with multiplication

```text
(i,j)(k,l) = (i + 2^j k mod 7, j+l mod 3).
```

Work in the formal group algebra `F2[G]` on three registers. Every nonidentity `g in G` and every rank-one idempotent `N=xy^T in M3(F2)` with `y^T x=1` defines one paid operation

```text
D_N([g]) = I + ([g] + [e]) N.
```

There are 20 nonidentity group elements, 28 rank-one idempotents, and 560 paid operation types. Calls are multiplied in order. No free address or register transformations are part of this model.

The target is

```text
diag([a], [a^2], [a^4])
```

with `a, a^2, a^4` the conjugacy orbit of `a` under `b`. The direct word uses three calls with `E11,E22,E33`. The verifier finds no word of length zero, one or two. It exhausts all 313,600 ordered two-call words and compares the resulting nine group-algebra entries coefficientwise. Therefore the exact minimum in this finite model is three.

The search covers all formal coefficients in `F2[G]`; it is an exact result for the named finite group and alphabet, not a test at selected address values. It gives no claim about larger groups, other targets, rational-frame realizations or integer multiplication.

## Search receipt and controls

- 560 complete paid operation types.
- 313,600 ordered pairs; 258,581 distinct product matrices.
- Ordered-pair stream SHA-256: `c5f116aa86ed6d2cbca21580027b0eab01804cad2ef65a1d1f3917b5df41b00f`.
- No one-call witness for the target; no two-call witness.
- Positive control: `diag([a],[a^2],[e])` is found with two calls.
- Group controls verify `b a b^-1=a^2`, `b^2 a b^-2=a^4`, noncommutativity, and all 28 rank-one idempotents.
- Direct three-call witness is replayed coefficientwise.

Nearby work uses different objects and endpoints: [PR #1745](https://github.com/CrocSwap/integer-mult-bounds/pull/1745) studies restricted four-label binary-affine targets; [PR #1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822) studies Q8 central pairs; [PR #1953](https://github.com/CrocSwap/integer-mult-bounds/pull/1953) studies D10 reflection pairs; [Discussion #1999](https://github.com/CrocSwap/integer-mult-bounds/discussions/1999) studies an order-24 `SL2(F3)` address group with a three-register mixed target and a four-call question; [Discussion #1774](https://github.com/CrocSwap/integer-mult-bounds/discussions/1774) studies a five-role GL2(F2) target; [Discussion #1773](https://github.com/CrocSwap/integer-mult-bounds/discussions/1773) studies a four-role D8 target; [Discussion #1759](https://github.com/CrocSwap/integer-mult-bounds/discussions/1759) studies a UT4 root pair; [Discussion #1769](https://github.com/CrocSwap/integer-mult-bounds/discussions/1769) studies a UT5 height-three root pair; and [Discussion #1740](https://github.com/CrocSwap/integer-mult-bounds/discussions/1740) studies an S4 target. The fresh complete scan at 2026-10-14T16:59Z covered 392 open PRs and 640 discussion records and found no other exact order-21 scope. The exact group, three-register conjugacy-orbit endpoint and complete 560-call alphabet here are distinct.

## Reproduce

From the repository root:

```sh
python3 -I -B research/bit-semidir21-orbit-seed8f89/verify.py
python3 -I -O -B research/bit-semidir21-orbit-seed8f89/verify.py
python3 scripts/research_package.py --package research/bit-semidir21-orbit-seed8f89 --check-only
```

The registered package runner specifies Python 3.12. The local environment has Python 3.14.7 and no Python 3.12 binary; the exact verifier is also run directly in both normal and optimized modes.

## Open next questions

Does four registers over the same `C7 semidirect C3` address group permit a nontrivial reduction for a four-entry conjugacy-orbit target? A feasible first step is to enumerate the rank-one idempotents of `M4(F2)` and write the exact word-length budget for a fixed four-entry target before searching. The larger alphabet and target are outside this cycle's length-two exclusion.

## Credit

Track `bit-mechanisms`, seed `8f89febe96e436a0b664eb258cbb53ec`, exact assigned base `1c47876ef742ba64bf9140b0527d63acf656a3b4`. Prepared by OpenAI Codex at Cinna's direction, with substantial AI assistance. Source pins, selected-record hash, catalogue revision and claim link are in [TASK.json](TASK.json) and [SOURCES.json](SOURCES.json). New work is Apache-2.0.
