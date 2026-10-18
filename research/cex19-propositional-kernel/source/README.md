# The 19-line configuration has exact pairing cost 21

The minimum raw pairing cost of DreamingOfClouds' `cex_min_1` configuration
is **21**. An admissible pairing attains block ranks **7, 6, 8**. A shipped
1,301-addition RUP refutation excludes cost at most 20. Replay regenerates
the CNF and checks every proof step without a SAT solver.

This answers [Q2 of the independent-check request](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18936173).
[PR2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) supplied the
configuration, a multi-copy lower bound of 20 and an upper witness of cost 22.
[PR2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162) supplied the
characteristic-two framework and the handoff. Those results retain their credit.
The new result closes this one finite gap. It proves no general rank-three
bound, physical supplier or new multiplication exponent.

## Exact scope

The 19 pairs of rational three-vectors `(p_t,q_t)` are copied byte-for-byte
in [configuration.json](configuration.json). For every binary 19-by-19 matrix B,
require `B_tt=1`, and permit `B_ts=1`, for `t!=s`, only if `p_t dot q_s=0`.
B need not be symmetric. Define

```
R_j = {t : p_t[j] != 0},   A_j = {s : q_s[j] != 0},
cost(B) = sum_{j=0}^2 rank_F2 B[R_j,A_j].
```

There are 114 free off-diagonal bits. The lower bound covers all `2^114`
assignments, not a sampled set or an enumeration stopped on timeout. The
per-total floor in the broader physical pricing rule is not included here.

The source blob is `4629aa02b1ffc882152726609d4027dd919ac014` at both:

- PR2111 head `98da76c2839ba38538b510420dec54546ccabf0b`, path
  `research/three-total-decoders/data/cex_min_1.json`;
- PR2162 head `113a718265c62aec301c5695f4bfb9c421bef7ab`, path
  `research/char2-jets/data/cex_min_1.json`.

[SOURCES.json](SOURCES.json) records the source SHA256, exact heads and search
environment. No predecessor executable is imported. The scientific base is
canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The scope change from `uniform-transfer-audit` to this requested decoder
side result is explicit in [TASK.json](TASK.json). This does not discharge a
selected all-size compiler obligation. Coordination is in
[Discussion2202](https://github.com/CrocSwap/integer-mult-bounds/discussions/2202).

## Why the CNF excludes every cost-at-most-20 pairing

All indices below are zero-based and follow the copied configuration order.
Each block has a principal minor that is unit upper triangular for **every**
admissible B. The ordered pivot lists are:

```
block 0: 9,11,3,17,2,8
block 1: 1,10,11,2
block 2: 1,4,7,10,11,3
```

Every diagonal entry is forced one and every entry below these diagonals is
forced zero by the rational incidence predicate. The checker verifies these
conditions before using any pivot. Reorder the block's rows and columns to
put this minor first. Ordinary F2 row elimination clears its columns below
the minor, giving `[U C; 0 S_j]`, with U invertible. Column elimination can
then clear C, so the rank is exactly `dim(U)+rank(S_j)`.

| Block | Original shape | Forced rank | Schur residual shape |
| --- | --- | --- | --- |
| 0 | 19 by 13 | 6 | 13 by 7 |
| 1 | 13 by 14 | 4 | 9 by 10 |
| 2 | 16 by 14 | 6 | 10 by 8 |

Consequently `cost(B)=16+sum_j rank(S_j)`. A hypothetical cost at most 20
has total residual rank at most four.

`encoding.py` represents the shared admissible B entries by Boolean variables
and computes the three residuals with exact AND/XOR gates. For each residual,
it encodes `S_j=X_j Y_j`, with four factor columns and activation bits
`e_jk`. An inactive column has its whole X column zero. Active columns form
a prefix within each block. All entries of each rectangular residual are
constrained, including entries away from its diagonal. Finally, for each
five-element subset of the twelve activation bits, a clause forbids them
all being active.

This encoding is complete. Any residual of rank `r_j<=4` has a rank
factorization with `r_j` columns. Pad it to four columns, activate its first
`r_j` columns, and zero the remaining X columns. If the ranks sum to at most
four, every budget clause holds. Conversely, any satisfying assignment gives
`rank(S_j)<=sum_k e_jk`, hence cost at most 20. The prefix constraints do not
exclude any rank factorization.

The resulting CNF has **2,856 variables and 9,964 clauses**. Its canonical
DIMACS SHA256 is
`7c89c203e5cc4552f1090b4b8cd54ed617bd9bc91cd3ba39591c389c861c1fe1`.
[lower.rup](lower.rup) ends in the empty clause. For each addition C,
`rup.py` negates all literals of C and requires unit propagation to contradict
the original CNF plus earlier additions. Thus each addition is entailed,
and the final empty clause proves the CNF unsatisfiable. The proof has no
RAT steps or deletion instructions. The solver's verdict is not trusted.
Together with the explicit admissible cost-21 witness, this proves the minimum.

## Witness and replay

[RESULT.json](RESULT.json) contains the nineteen upper-witness row bitmasks.
Bit s of row t is `B_ts`. Replay checks every diagonal, every allowed nonzero
and the three complete rectangular block ranks before comparing the entire
receipt. It also verifies the copied configuration's SHA256 and Git blob.
Nothing is regenerated in the package on normal replay.

From the repository root, Python 3.12 and its standard library suffice:

```sh
python3.12 -I -Werror -B research/cex19-exact-pairing/verify.py
python3.12 -B scripts/research_package.py --package research/cex19-exact-pairing
```

Expected mathematical check:

```
PASS_CEX19_EXACT_PAIRING minimum=21 ranks=7,6,8 RUP=1301 no_new_kappa
```

The registered replay includes ten behavioral test groups, normally and
with `-O`. Tests cover:

- the real command and a standalone relocation without Git;
- the witness's ranks by separate column elimination;
- Schur rank identities on 64 admissible pairings;
- a complete satisfying assignment at cost 21 when the budget is raised;
- rejection of the lower refutation when the essential budget clauses are removed;
- all gate truth tables and propagation comparisons on 960 small cases;
- the **entire 1,301-step proof again**, using an independent bit-mask,
  repeated-whole-clause-scan propagation implementation;
- missing, malformed or truncated proofs, a false unit claim, capacity limits,
  forbidden witness entries, source corruption, duplicate JSON keys and
  incorrect or missing receipts.

The watched-literal check takes under a second locally; the independent
whole-scan check takes about 18 seconds on Linux x86_64 / CPython 3.12.15.
These are verifier timings, not multiplication runtime measurements. Search
used CaDiCaL 1.9.5 through `python-sat==1.9.dev15`; neither is needed for replay.
The original unrestricted rank-factor search was stopped without a conclusion.
The completed Schur-reduced refutation, not that search, supplies the lower bound.

## Resource limits and verification limits

The code has no recursive calls. Functions stay below 60 physical lines.
RUP proof input is capped at 1 MB and 5,000 additions, with at most 128 literals
per addition. The formula is capped at 10,000 variables and 20,000 input clauses;
the propagator retains at most 25,000 clauses and units. Its queue and iteration
bounds follow from these capacities. JSON inputs are byte-bounded, and the
configuration is restricted to nineteen pairs of three integer coordinates.

Power-of-Ten rule 3 has a managed-runtime deviation in these Python checkers:
Python allocates integers and collections during verification. Fixed-capacity,
allocation-free operation would require another runtime. The enforced input,
clause and queue limits bound live data instead. The compensating checks are
exercised by the replay; a future generalization must retain or replace these
limits. Python library allocation internals are not audited. Diagnostics use
warnings as errors, compile checks and local call-graph inspection; no static
type checker or formal proof kernel is claimed.

The mathematical trust boundary includes the displayed rank-to-CNF argument
and the two small proof checkers. There is no formal-kernel verification,
independent human review, full selected supplier replay, hosting admission,
precision/tape proof or outer multiplication theorem here. Frozen source
packages and the selected frontier remain unchanged.

## Open next questions

Can a short structural rank inequality explain why this configuration costs
21 while its retained multi-copy certificate reaches only 20? Such an
inequality might transfer to other decoder configurations. Start with the
three displayed Schur residuals and characterize why their ranks cannot sum
to four. The current obstruction is a finite RUP refutation, not a reusable
closed-form inequality. The exact-cost question itself is closed by this package.

## Credit

DreamingOfClouds supplied the configuration, its original 20-to-22 interval,
the multi-copy certificate and characteristic-two work in PR2111/2162.
The decoder-cost model and retained root-unit lemmas precede this package.
Their mathematical results are not claimed as new. PR2176's exact jf0 result
motivated the independent-check request but concerns a different input.

Nick Petalas contributed the cost-21 witness, Schur-reduced refutation,
independent replay and failure controls. New material and the retained
configuration follow the repository's Apache-2.0 license.
