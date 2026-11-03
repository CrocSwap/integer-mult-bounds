# What does replication buy when compatible widths have different prices?

For a finite menu at each chronological cut, this package computes every trade-off between common replication and normalized price. An invocation fills its whole width and pays its complete declared price once. Each cut finishes independently. These are scoped arithmetic results for the priced-menu question in Nick Petalas's #6658. [Source handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/6658)

## A priced application to an existing compiler

In the rank-12 toy flow of Mihir Srivastava's #4507, offer both of its existing compiled widths at each child rank. Retain its rank-one leaf charges and add a hypothetical one-unit fee for each positive-rank child dispatch at the parent. The 515 child cuts give exactly two nondominated choices.

| Replication | Normalized cost | Role |
| ---: | ---: | --- |
| 700 | 349039/27650 | First feasible replication |
| 2,744,000 | 684112521/54194000 | First attainment of the cost floor |

The 3,919 feasible replications before the floor have the same unit cost. A 3,920-fold increase in replication saves exactly 3919/54194000 per productive unit. At rank eight, a nested dispatch can replace 3,920 smaller dispatches with equal leaf cost. If its surcharge reaches the combined surcharge of those calls, 700 is the sole nondominated point. The underlying programs and cut multiplicities come from the source. The fee is an explicit assumption. [Complete invoice and break-even proof](RANK12.md) · [#4507](https://github.com/CrocSwap/integer-mult-bounds/pull/4507)

If the same unit fee is charged at **every internal invocation** of both fixed historical programs, the two replication choices remain the same. A literal traversal of the rank-eight programs finds 3,639 calls in the smaller one and 13,928,545 in the nested one. Substituting a nested call saves 336,335 calls per rank-eight cut. With all positive invocations priced, the normalized saving is 67267/10838800. [Recursive invoice and counts](RANK12.md#charging-every-internal-call-of-the-two-fixed-libraries)

## General results

- The price for each job total is certified by minimum-loss residue labels, attaining whole-program counts and an exact prefix computation. A second residue table gives the last exception in each class.
- For cut $j$, let $h_j$ be the gcd of its cheapest-density widths and $q_j$ its jobs per replica. The least eventual period of the total excess price is $P=\operatorname{lcm}_j h_j/\gcd(h_j,q_j)$, with each quotient taken before the LCM. The first replication from which the period holds also has an exact finite formula. Missing amounts at one cut can mask exceptions in another.
- The first all-cheapest replication is found by testing the cheapest-width menus. The complete frontier consists of strict price records through this first floor. In a two-cut fixed-fee family the number of records is unbounded. Width parameters $12,13$ give ten records at $1,12,13,84,96,108,120,132,144,156$. [Proof and exact hypotheses](PROOF.md)

The selected multiplication bound and the physical implementation of the toy model are outside these claims.

## Reproduce

From the repository root with CPython 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/priced-width-frontier
```

The registered command runs normal and optimized scientific checks, a two-cut census and private-copy mutation checks. In an extracted package the three scripts also run directly with `python3.12 -I -B`. The two independent price computations are the residue solver and an amount-by-amount oracle. Literal count-vector enumeration and charged shear executions provide additional checks. [Exact cases and schedules](RESULT.json) · [Census](CENSUS.json) · [Reproduction details](VALIDATION.md)

## Scope, source and credit

The frozen card is `independent-moment` at priority revision 8. The selected source-binding orientation passed. The scope changed to the priced finite-menu implication requested by #6658. Pending-source bytes from that PR are retained with original path, hash, author and head. Classical knapsack periodicity, Apéry sets and shortest paths supply prior methods. The additions here concern common replication at separate cuts, exact onset, explicit frontiers and the rank-12 tariff comparison. [Source identities](SOURCES.json) · [Task and scope](TASK.json) · [Overlap search](OVERLAP.json)

Mihir Srivastava supplied the single-width theorem and the compiled toy fixture on zxv's chronological flow and Jacob Alan Sussman's integer compilation. Nick Petalas supplied the unpriced compatible-menu model, strict family and direct-sum shear contract. His #4892 and #6612 retain prescribed widths. New work prepared for SHIN09-git with substantial OpenAI Codex assistance in derivation, implementation, verification and writing. Apache-2.0. [#4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436) · [#4892](https://github.com/CrocSwap/integer-mult-bounds/pull/4892) · [#6612](https://github.com/CrocSwap/integer-mult-bounds/pull/6612)

## Open next questions

1. What is the complete, physically justified price of the two rank-eight programs? The break-even ratio supplies a target for an audit of routing, storage, precision, owned lifetimes and recursive calls.
2. Can the next strict price record be found without scanning every feasible replication through the first floor? Begin with the explicit two-cut family and test any skipping rule against early residue exceptions.
