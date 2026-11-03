# Exact Boolean triple tariff on a directed cycle

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped written proof with exact finite corroboration.**
For the Boolean demand `(110,101,011)`, the exact complete abstract tariff is

```text
OPT = min(mu_0, mu_1, mu_2) + 8c
```

when the three ADD edges `0 -> 1 -> 2 -> 0` cost `c>0`, every source
insertion price `mu_i` is at least `8c`, and every reverse ADD edge price
is at least `8c`. Coefficients do not affect prices. The cone need not be
maximal. With insertion and reverse-edge prices 100 and cycle-edge price 1,
the optimum is **108**, attained by one insertion and eight cycle ADDs.
Three direct insertions cost 300.

This answers one price family of Open next question 1 in lee-phys's
[PR5304](https://github.com/CrocSwap/integer-mult-bounds/pull/5304).
That predecessor proves destination-row tariffs and leaves independently
directed prices open. The new step is the exact cycle column distance,
its conversion to a dirty-restored lower bound, and the attaining word.
It is a local arithmetic result. No new kappa or physical supplier is claimed.

## Contract

Let `R=F2^3`, represented by masks 0 through 7 with XOR addition, AND
multiplication and identity 7. Three arbitrary independent dirty rows
`A_0,A_1,A_2 in R^w`, `w>=1`, and a disjoint preserved source `p in R^w`
are available. A fixed finite word must implement

```text
A_i <- a_i + lambda_i p,      lambda=(3,5,6).
P_i(beta):  A_i <- A_i + beta p,       price mu_i
E_ij(alpha): A_i <- A_i + alpha A_j,   price c_ij, i != j.
```

Every coefficient is allowed; zero gates can be deleted. All original dirt
columns must return exactly. There are no extra rows, CLEARs, observations,
free basis changes or adaptive choices. Prices are positive, stationary,
coefficient-independent abstract complete gate prices. An application must
supply such prices including its required access, routing and restoration.
Separate inverse execution must be paid separately.

The three cycle edges have equal price `c`. The other three edge prices
may differ. Put `m=min_i mu_i`. The theorem assumes `m>=8c` and
`min_reverse c_ij>=8c`.

## Four ADDs are necessary and sufficient to split one inserted column

Consider an ADD-only word C taking `7 e_i` to lambda. First let `i=0`.
Every destination must change: rows 1 and 2 start zero but have nonzero
targets, and row 0 starts 7 but must end at 3. With at most three cycle ADDs,
each destination must therefore receive exactly one gate. To change row 2,
its only parent row 1 must first have changed. To change row 0, its only
parent row 2 must first have changed. The only possible order is

```text
E_10(alpha), E_21(beta), E_02(gamma).
```

Row 1 is then already at its final value 5 when row 2 changes. Consequently
row 2's final value is `beta AND 5`, which cannot equal 6. This excludes
every word with at most three cycle ADDs, including arbitrary coefficients.
For the other roots, cyclic row relabeling gives the same argument: each
required target is incomparable with its parent's mask under support
inclusion. Thus the column distance is at least four for every root.

Here is an attaining suffix for any root i. Put `j=i+1 mod 3`,
`k=i+2 mod 3`, and `h_i=7 XOR lambda_i`. Execute

```text
C_i = E_ji(lambda_k), E_kj(7), E_ji(lambda_i), E_ik(h_i).
```

The source column changes through

```text
7 e_i -> (7, lambda_k, 0) -> (7, lambda_k, lambda_k)
      -> (7, lambda_j, lambda_k) -> (lambda_i, lambda_j, lambda_k),
```

where the entries are ordered as i,j,k. The final step uses
`h_i AND lambda_k=h_i`; all displayed coefficients are nonzero. Hence the
distance is exactly four. The written argument applies to every finite
ADD-only word; no search cutoff is used in the theorem.

## Restoration doubles the column distance

Suppose a correct word has exactly one insertion `P_i(beta)`. Write M
for the dirt matrix of its ADD-only prefix and L for that of its suffix.
Every ADD is invertible, and restoration forces `LM=I`, so `L=M^-1`.
The source column is `L(beta e_i)=lambda`.

Every one of the three bit coordinates occurs in lambda. If the
corresponding bit of beta were zero, that whole coordinate of the source
column would remain zero under L. Thus beta must be 7.

The suffix is therefore an ADD word taking `7 e_i` to lambda. Reversing
the prefix gives another word for L, because every Boolean ADD is its own
inverse. If only cycle edges are used, each of these two words has at
least four ADDs. Any one-insertion cycle word needs at least eight ADDs.

The chronological word `C_i^-1, P_i(7), C_i` attains this lower bound and
returns every dirt column. For root zero it is

```text
E_02(4), E_10(3), E_21(7), E_10(6), P_0(7),
E_10(6), E_21(7), E_10(3), E_02(4).
```

For example the suffix sends its source column through
`(7,0,0),(7,6,0),(7,6,6),(7,5,6),(3,5,6)`.
The first four gates prepare dirt, and the last four restore it while
delivering the inserted source. Omitting that preparation is invalid.

## Complete tariff lower bound

A correct word needs at least one insertion. The following cases exhaust
all finite words under the stated prices.

- At least two insertions cost at least `2m>=m+8c`.
- A reverse ADD and at least one insertion cost at least `m+8c`.
- Exactly one insertion and only cycle ADDs cost at least `m+8c`, by the
  preceding restoration argument.

Choose a minimum-price insertion root and use its nine-gate word. Its cost
is exactly `m+8c`, proving the theorem, including the boundary equalities.
This settles the complete program optimum within the displayed cone,
rather than only the one-insertion branch. All-width correctness follows
coordinatewise from the same ring-linear identity.

## Exact verification

Use CPython 3.12 and the standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/boolean-directed-cycle-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/boolean-directed-cycle-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/boolean-directed-cycle-tariff --check-source-history
```

Another CPython 3.12 path may replace the local interpreter path. Normal
and optimized warning-strict direct commands are registered in VERIFY.json.
Each writes only stdout, including a generated receipt bound to all five
package file hashes. The expected scientific status is
`PASS_BOOLEAN_DIRECTED_CYCLE_TARIFF`.

The packed source-column graph has exactly `7^3=343` vertices. In each
bit coordinate the nonzero three-entry column stays nonzero under invertible
ADDs. The verifier visits every state for each root, checks every directed
distance inequality and finds target distance four. Its layer sizes are
`1,7,19,74,176,66`. A separately arranged bit-coordinate implementation
enumerates all columns reachable through length three and excludes the
target. These two programs use different state orientations.

A separate literal bit-list interpreter checks all 4,096 assignments of
the three dirty scalars and source for each root, both forward and inverse:
12,288 input cases in total. Formal basis-column checks establish each
linear endpoint. Twelve exact rational price fixtures include nonuniform
insertion prices and cone boundaries. Twenty-five controls reject nine
deleted gates, nine changed nonzero coefficients, three omitted-preparation
words and four invalid price/arity boundaries. Counts are enumerated by
the verifier. No predecessor executable or reported numerical census is
used as an oracle.

## Scope and resources

Independent human and formal proof-kernel review are unclaimed. The proof
covers the specified Boolean triple, three rows and the displayed price cone.
It does not settle arbitrary directed tariffs, extra workspace, non-Boolean
rings, native operators, precision/tape costs, stock, supplier admission or
a complete multiplication theorem. The selected frontier is unchanged.

The current selected-record positive control passed. That command checks
metadata bindings and is not scientific evidence for this local theorem.

The verifier has no recursion, subprocesses or runtime source imports.
All search loops have fixed finite domains: three roots, 343 column states,
21 cycle gates, three short-word layers, and 4,096 scalar assignments per
root. Short-word frontiers have at most 343 entries. Literal states have
four rows of three bits and words have at most nine gates. Functions stay
under 60 lines. Guards raise exceptions under normal and optimized Python.
Power of Ten rule 3 deviation: CPython collections, fractions and hashing
allocate dynamically; the finite domains and five 128 KiB file limits bound
the owned input and state. Standard-library dispatch is fixed by the code.
Warning-strict execution and AST compilation are the available diagnostics;
no repository-wide configuration change is introduced.

## Open next questions

What is the exact tariff outside this cone, with all six ADD prices
independent? The 343-state graph solves the single-insertion column problem,
but multiple insertions need a dirt-aware lower bound. Start by deriving
that bound before extending the tariff search. The present proof gives
no physical gate prices or complete supplier invoice for such an expansion.

## Credit and coordination

lee-phys's PR5304 supplies the Boolean triple, arbitrary-dirty restoration
contract, destination-price comparison and explicit directed-price question.
Credit lee-phys PR5259, Ali Romman Discussion5266/5300, Krzysztof Wojt
PR5045, Ross Richardson PR3063/3121, Nick Petalas PR4916/5208, and the
earlier fanout lineage retained there. Their results are credited premises,
not audit deliverables. No literature-priority claim is made for elementary
matrix conjugation or shortest-path search.

The base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8. SOURCES.json retains the card, selected-record and
PR5304 README provenance at that ancestor. These are provenance records,
not executable dependencies. The proof and verifier are self-contained.
The changed `bit-helper-contract` scope concerns the cost of a local dirty
interface, rather than an audit or a changed G20 word.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19377650).
Overlap checks covered live PRs and claims, the cached complete corpus and
distinctive main/merged searches. They do not certify novelty against
unpublished work or every historical diff. PR5933's Z/4 nonunit cycle and
PR5948's orthogonal Boolean demand are different instances; neither proves
this tariff. Their original credit and source packages remain unchanged.
