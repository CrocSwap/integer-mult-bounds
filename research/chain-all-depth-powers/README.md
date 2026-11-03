# Which balanced chain schedules can repeat?

At every depth L≥2, a single prime determines whether a repeated block can
reach the required endpoint. Let d be the repetition factor, n the copies
of each label in one block, and m=dn. Find the smallest prime q dividing d
but not n, with q=∞ if none exists.

| Relation | Result for a block that is correct modulo n for target t |
|---|---|
| q<L | Some proper interval fails for every block. |
| q>L | The repeated target is d t modulo m. |
| q=L | The repeated target is d t+(d/L)n^L modulo m. |

For q≥L the shorter block must also satisfy every proper interval condition.
These rules give the exact count fixed by each rotation in terms of the
shorter literal count W. They answer open question 1 of the depth-four
study. [Proof](PROOF.md) · [PR #6652](https://github.com/CrocSwap/integer-mult-bounds/pull/6652)

Three consequences make the rule concrete.

- For target zero the shortest rotation period is L times the product of
  the distinct primes dividing m that are at most L. The proof constructs
  every allowed least period. For L=5,m=360 the minimum is 150.
- For a unit target, a nonprimitive word can exist only at prime depth
  L=p, with m=pn, p∤n and c=n^p modulo p. It repeats exactly p times and
  the shorter-block multiplicity decides existence. A retained 35-letter
  block gives a 175-letter unit-target word of least period 35 at m=35,c=12.
- Of all length-75 correct words at L=5,m=15, exactly 4,697,520 have a
  shorter period. All have c=3 and form 313,168 classes of period 15.
  Two complete, separately implemented counts of the small root row
  establish the number. [Numerical certificate](ROOT-COUNT.md)

The proof also gives a closed divisor D whose divisors are exactly the
arithmetically eligible rotation orders. The distinction between eligibility
and existence matters. At L=5,m=10,c=7 the candidate order 5 has zero
fixed words because W_5(2,1)=0. An explicit correct primitive word for this
target is checked.

## Reproduce

From the repository root, using Python 3.12 and its standard library,

```sh
python3.12 -I -W error -B research/chain-all-depth-powers/verify.py
python3.12 -I -O -W error -B research/chain-all-depth-powers/verify.py
python3.12 -I -W error -B research/chain-all-depth-powers/audit_mutations.py
python3.12 -B scripts/research_package.py --package research/chain-all-depth-powers
```

The scientific verifier reads only the exported package. Its JSON output
contains `PASS_CHAIN_ALL_DEPTH_POWERS`, the recomputed [EXPECTED.json](EXPECTED.json)
data and every package file's SHA-256. The fault-injection command uses
temporary private copies. See [validation](VALIDATION.md) for the observed
environment and publication checks.

## Evidence and limits

- A position-based subsequence counter and a chronological integer matrix
  executor check all 123,698 blocks in the specified domains. The corpus
  covers n=1 through depth 7, n=2 through depth 5, n=3 through depth 3
  and (L,n)=(2,4). There are 309,184 direct repeated-word comparisons
  and 804 fixed-point count bins. For 24 small (L,m,c) cases, literal
  rotation classes and least periods agree with the divisor transforms.
- The two depth-five counters group words by prefix/suffix and by the
  middle three labels, respectively. They cover the full multinomial
  mass of 168,168,000 at n=3 and 113,400 at n=2. At n=2 the row also
  agrees with the separate literal word census.
- An arithmetic check covers 195,072 binomial coefficients for 1≤n≤24
  and 1≤d≤128. The closed divisor formula agrees with direct unreduced
  binomial gates in 979,380 order tests over 102,225 (L,m,c) cases, including
  53,715 unit targets. Depths are 2..16. Moduli are 2..96 and six larger
  composites through 900. There are 585 constructed zero-target words
  with literally checked least periods.
- All 173 retained depth-five witnesses are executed at byte-pinned
  source and raised to seven powers each. The run also checks 519 prefix/
  inverse-suffix joins on their positive targets. Six balanced examples
  and the credited unbalanced depth-six boundary have complete basis checks
  with noncommuting two-coordinate maps, including a singular family.
- The mutation audit attempts 17 specific code and data changes in both
  Python modes, plus two unchanged positive probes. Each mutation must
  reach its named semantic check.

The finite evidence supports a written proof for all depths, moduli and
targets in the balanced unsigned model. W at larger roots remains an input
to the counting transform. The engines share the same assisted author and
Python integer semantics. Physical routing, precision, supplier prices and
independent mathematical review have separate obligations.

The largest half-word search in the registered verifier has 5^8 lexical
candidates. The largest gap-weight matrix has 220² entries. Full enumeration
stops at the stated corpus; powers of upstream words stop at d=12. Python
performs bounded dynamic allocations. The checker launches no network calls,
and each mutation subprocess has an explicit timeout.

## Task, overlap and credit

The `connector-alphabet-change` card is recorded as changed. We investigate
period accounting for the existing complete calls. This supplies exact
deduplication and census checks for future connector studies. Improving κ
would require a priced supplier contract. The orientation baseline reproduced
its 945 pairings. Canonical base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8. [Task](TASK.json) · [Overlap coverage](OVERLAP.json)

Nick Petalas supplied the depth-four law, the depth-five witnesses and the
unbalanced depth-six example. SHIN09-git's depth-three work supplied the
cyclic fixed-point formulation. The earlier complete-call model credits
Ross Richardson's #943/#934 lineage. The depth-four source note at
`e364eeb19e5268967189ed12aa4813ee73edf3dc` is retained byte-for-byte in
publication ancestor `fd1b2f3e103f11734750a0fe93aa2431fd5468ad`; its original
head, path and blob accompany the retained pin. [Exact source manifest](SOURCES.json) · [#6080](https://github.com/CrocSwap/integer-mult-bounds/pull/6080) · [#6652](https://github.com/CrocSwap/integer-mult-bounds/pull/6652) · [#4281](https://github.com/CrocSwap/integer-mult-bounds/pull/4281) · [#4748](https://github.com/CrocSwap/integer-mult-bounds/pull/4748)

The Parikh matrix encoding, its integer power expansion, Burnside's lemma and
Möbius inversion are classical. Our contribution is the reduction modulo dn,
the eligible-order divisor, the sharp zero-target spectrum, and the scoped
depth-five counts. [Mateescu et al.](https://www.numdam.org/item/ITA_2001__35_6_551_0/) · [Atanasiu, Poovanandran and Teh, Theorem 3.1](https://arxiv.org/pdf/1808.04102)

Prepared for SHIN09-git with substantial OpenAI Codex assistance in
derivation, implementation, checking and writing. Apache-2.0.

## Open next questions

1. What is W_5(7,1)? It is the exact number of repeated words at m=35,c=12.
   The retained witness proves positivity. Start by profiling the middle-gap
   method at n=4 against the n=2,3 baselines before committing to the larger
   count. Growth of the middle words and gap pairs is the obstacle.
2. How do the gates change for unequal positive letter counts? Start with
   the (2,4,4,4,4,2) binary profile of #4748. A length-p pure term then
   contains the product of nonuniform singleton counts, so the obstruction
   used for a balanced block can disappear.
