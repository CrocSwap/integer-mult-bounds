# Pricing the retained rank-12 toy flow

Mihir Srivastava's #4507 compiles zxv's #4436 chronological flow for Sussman's integer construction. Its equality fixture has target multiplicities $\{2:4,3:1\}$ and paid multiplicities $\{1:6,2:2\}$. The source supplies a smaller width and an older nested width for each child rank. Their normalized rank-one leaf costs agree. This comparison offers both existing compiled widths to each positive-rank cut of the rank-12 parent. The added hypothesis is **one unit per top-level child dispatch**, in addition to the source leaf bill. The rank-zero complement has zero cost. Internal dispatch, physical routing, storage and precision are outside this pricing experiment. [#4507](https://github.com/CrocSwap/integer-mult-bounds/pull/4507) · [compiled source at the frozen base](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/chronological-batch-width/batches.py) · [original rank-12 receipt](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/chronological-batch-width/RESULT.json)

There are 158 parent source jobs and 515 positive-rank child cuts. Each occurrence below must complete its own $aq$ jobs.

| Rank | $q$ | Occurrences | Smaller width | Nested width | Leaves per smaller call | Leaves per nested call |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 216 | 1 | 1 | 1 | 1 |
| 2 | 1 | 216 | 1 | 1 | 2 | 2 |
| 3 | 6 | 1 | 5 | 5 | 14 | 14 |
| 4 | 1 | 72 | 5 | 25 | 19 | 95 |
| 4 | 64 | 1 | 5 | 25 | 19 | 95 |
| 6 | 60 | 1 | 140 | 3,500 | 740 | 18,500 |
| 8 | 1 | 8 | 700 | 2,744,000 | 4,996 | 19,584,320 |

The smaller width divides the nested width at every row. Exact fill is possible precisely when the smaller width divides $aq$ at each cut. The least common feasible replication is 700, forced by the eight separate rank-eight cuts. Conversely the table shows that every multiple of 700 is feasible. Replacing those eight by a single eight-job cut would admit wrong candidates.

For each row, one nested call replaces exactly (nested width)/(smaller width) smaller calls at **identical leaf cost**. It saves one fewer than that ratio in dispatch units. Consequently the optimum uses the maximum number of nested calls that fit and fills the remainder with smaller calls. Unchanged normalized leaf cost over the whole parent is $19448/1975$. At every multiple of 700 the first six rows can already use only nested calls. For each rank-eight cut, up to replication $2{,}744{,}000$, only smaller calls fit until the final replication. This makes the normalized bill constant for the first 3,919 feasible replications and strictly smaller at the 3,920th. At that point every positive cut uses a lowest-density program, so all larger replications are dominated. The least excess period in the original replication coordinate is $2{,}744{,}000$ and it starts at one, including the infeasible residue classes.

| Replication | Productive width | Rank-one leaves | Child dispatches | Normalized total |
| ---: | ---: | ---: | ---: | ---: |
| 700 | 110,600 | 1,089,088 | 307,068 | $349039/27650$ |
| 2,744,000 | 433,552,000 | 4,269,224,960 | 1,203,675,208 | $684112521/54194000$ |

These are the two Pareto points. Increasing replication by a factor of 3,920 buys a saving of exactly $3919/54194000$ per productive unit. The counted quantities come from the toy compiler. The one-unit fee is hypothetical.

**Break-even price.** Suppose the rank-eight smaller and nested calls have respective additional fees $u,v\ge0$. The other six rows can use a minimum-density program at every feasible replication because each row's two widths divide its job total there. One nested rank-eight invocation replaces 3,920 smaller ones with equal leaf cost. If $v\ge3920u$, the smaller program attains the minimum density at every feasible replication, leaving only the point at 700. If $v<3920u$, both points above remain, and the normalized saving is exactly $8(3920u-v)/(158\cdot2744000)$. This identifies a concrete price comparison for a physical implementation. The verifier checks both strict sides, equality and a fractional fee pair.

[rank12.py](rank12.py) regenerates the inputs from the retained #4507 compiler and checks them against its retained result. It compares the general residue solver with the direct quotient-and-remainder bill for all 3,920 feasible replications through the first floor. Grouping identical cuts multiplies the price by the number of occurrences and leaves each cut's job count unchanged. [Exact schedules and bills](RESULT.json) · [Source identities](SOURCES.json)

## Charging every internal call of the two fixed libraries

Keep each child program's historical internal choices fixed. Assign one unit to each positive-rank invocation, recursively through its terminal calls, in addition to its original leaf charge. The external rank-12 parent is the pricing boundary. Rank zero makes no invocation. Let $T_e$ be the number of positive invocations inside one width-$B_e$ program, including its root. The compiler gives $T_0=0$, $T_1=T_2=1$, and for higher ranks
$$
T_e=1+\sum_{(d,q,c)}c\frac{(B_e/S_e)q}{B_d}\,T_d.
$$
Here $S_e$ is the source count, $q$ the jobs at one cut and $c$ the number of occurrences. The quotient is integral at each individual cut. All children have lower rank. Apply this recurrence separately to the smaller and nested libraries. At the rank-12 parent either finished program is available. This gives two explicit tariffs for the earlier break-even criterion.

| Child rank | Calls in one smaller program | Calls in one nested program |
| ---: | ---: | ---: |
| 1, 2 | 1 | 1 |
| 3 | 13 | 13 |
| 4 | 14 | 66 |
| 6 | 515 | 12,771 |
| 8 | 3,639 | 13,928,545 |

At every row the nested program has at most the smaller program's number of calls per job. For rank eight, replacing 3,920 smaller programs by one nested program saves $3920\cdot3639-13928545=336335$ internal and root invocations. Both earlier Pareto coordinates therefore persist. The counts change as follows.

| Replication | Rank-one leaves | All positive child invocations | Normalized total |
| ---: | ---: | ---: | ---: |
| 700 | 1,089,088 | 747,012 | $2623/158$ |
| 2,744,000 | 4,269,224,960 | 2,925,596,360 | $179870533/10838800$ |

The exact saving becomes $67267/10838800$ per productive unit. [recursive_dispatch.py](recursive_dispatch.py) checks the recurrence against the compiler's leaf counts, literally visits all 3,639 and 13,928,545 invocations of the two rank-eight programs, and recounts the rank-12 bill at all 3,920 feasible replications through the floor. The larger parent bills use these checked program counts. This second model prices every invocation in the fixed trees. Physical dispatch duration, movement, live memory and re-optimizing the internal programs require additional evidence.
