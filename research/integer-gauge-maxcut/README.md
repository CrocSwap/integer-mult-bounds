# Global integer dyadic-gauge optimization encodes Max Cut exactly

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. Global
constant integer dyadic-gauge optimization under the boundary-inclusive
copy-init scalar tariff is NP-complete. This already holds for fixed
words with original coefficients only 1/2, 1 and 2, one fixed reference
register, arbitrary dirty data, and both entry and exit scales paid.

For every simple graph G with n>=1 vertices, m edges and maximum degree
Delta, an explicit word has exact minimum real-component scalar bill

```text
min B = n(12 Delta+10) + 8m - MaxCut(G).
```

Its ungauged bill is the same expression without the MaxCut subtraction.
Every integer optimum is binary and corresponds to a maximum cut. A
quantitative clipping inequality covers every integer gauge, including
ones outside any finite search box. [PROOF.md](PROOF.md) gives the word,
full bill, clipping argument, complexity reduction and dirty endpoint proof.
For complex arithmetic the inherited separate real/imaginary lowering
simply doubles the real bill; it does not alter the optimizing gauges.

Philipp / mightyOil's [PR1310](https://github.com/CrocSwap/integer-mult-bounds/pull/1310)
provides the exact scalar objective and explicitly separates pair
stationarity from a global optimum. This new result explains a worst-case
obstruction to a general efficient global optimizer. It does not audit,
replay or decide that predecessor's historical 237-helper instance.
Classical Simple Max Cut hardness is due to Garey, Johnson and Stockmeyer;
the [primary paper](https://doi.org/10.1016/0304-3975(76)90059-1) is cited
with its locator in the proof. No general literature-priority claim is made.

## Evidence and reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/integer-gauge-maxcut/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/integer-gauge-maxcut/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/integer-gauge-maxcut
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/integer-gauge-maxcut --check-source-history
```

Another Python 3.12 path can replace the absolute interpreter path. Direct
replay prints `PASS_INTEGER_GAUGE_MAXCUT` in a generated JSON receipt bound
to every package file and the pinned predecessor README. It writes only
standard output. The registered manifest repeats the direct verifier
normally and with optimization, with a 120-second limit per command.

The checker enumerates every simple labeled graph through four vertices.
For every graph it compares the literal event tariff with the reduced
objective on every gauge in {-2,-1,0,1,2,3}^n, verifies quantitative clipping,
and independently enumerates every binary cut and decision threshold.
The universal theorem rests on the written proof, not this finite box.
The generated counts are 75 graphs, 1,098 binary assignments, 84,750
integer assignments and 430 threshold comparisons. The complete-graph
minimum bills at n=1,2,3,4 are 10, 51, 124 and 228.

Separately, every graph through three vertices and every gauge in
{-1,0,1,2}^n is lowered to literal COPY, ADD, CLEAR, DOUBLE and HALVE
instructions. Their lengths must equal the charged bill. All basis
columns, including independent coefficient-work dirt, and two signed
rational states must match the direct ungauged linear endpoint. No
predecessor executable is imported. Controls exercise the coefficient
ratio, missing exit, truncated word, boundary price, unit discount,
frustrated triangle and invalid graph boundaries.
The literal checks cover 548 gauge words, 3,796 dirty endpoints and
419,653 executed primitives. There are 1,799 local-lemma substitutions,
six semantic controls and eight invalid-graph rejections.

## Scope and provenance

The card `complex-new-helper-inventory` is marked changed in TASK.json.
This is a scalar-search side result. It does not satisfy that card's
physical productive-inventory acceptance gate. The orientation baseline
passed source bindings only. Canonical base is
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. The selected
record is #7000 at kappa 0.00363005817; the priority headline describes an
older checkpoint. Source manifests pin the original card, selection and
predecessor text. The sole live external input is that text, authenticated
before mathematical execution and included in the replay/export inventory.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19601582)
reserves this exact global-integer problem. Main-tree, merged-PR, open-PR
and live Discussion checks found related coframe hardness and local gauge
results, but no matching integer-gauge construction within that bounded
coverage. The overlap cache covered 846 open PRs, 7,483 Discussion records
and 10,178 HEAD notes. This is not a proof of novelty or an exhaustive
literature search.

This fixes the chronological word and the declared lowerer. Repeated
instructions may be resynthesized under a different problem. Work CLEARs
are charged and retain their owned-work semantics. No claim is made about
physical tape cost, rounded precision, stock, native operators, supplier
admission, a changed recursive moment, the selected frontier or complete
multiplication. No predecessor scientific replay, selected cold replay,
Lean or Docker ran. Independent human and formal proof-kernel review are
unclaimed.

## Open next questions

Can a useful structural restriction on the actual scalar interaction
graph yield an exact global optimizer despite this worst-case reduction?
First measure one pinned graph's treewidth or a small deletion set that
removes its frustrated edge potentials, then derive a complete-state
algorithm with both boundary scales and unit discounts retained. This
matters because the theorem leaves structured supplier instances open.
No width bound or such algorithm is supplied here.

## Credit

Credit Philipp / mightyOil #1310 for the explicit objective and global
optimality distinction, Hanson Sun / bbMisk #1214 for the earlier exact
pair method, woklerx #1161 for scalar gauge conjugation, and Sagar Thakrar
#696 for the retained copy-init lowerer, with Jeremy Kothe, Hao Yan /
icekylinx, Douglas Colkitt and the retained supplier lineage. Their files
and credit lines remain unchanged. Classical Max Cut hardness and the
standard diagonal conjugation identity keep their established credit.
The new contribution is the graph word, exact full-tariff identity,
all-integer clipping proof and its finite corroboration.

Nick Petalas #6225 is an older local exclusion on a fixed historical
instance. Nick Petalas #5888 is an older transported-coframe rank-cost
hardness result. Neither supplies this construction, objective reduction,
proof or executable. They are related background, not main predecessors.

## Checker bounds

Every loop is bounded by the fixed census domains: at most four vertices,
six edges, 72 source ADDs, 1,024 primitive instructions, 1,296 integer
gauges per graph, 16 binary gauges and seven endpoint fixtures per word.
Each function is below 60 physical lines. Exceptions keep checks active
under optimization. There is no recursion, network use, dynamic code,
subprocess or file writing in the scientific verifier.

Power of Ten rule 3 has a managed-runtime deviation. Python allocates
integers, tuples, lists and Fractions during execution. The bounds above
limit live mathematical data, while fixed file inventories limit source
reads. The largest integer gauge tested in the census is three in
absolute value, and literal endpoints use exponents from -1 through two.
No heap profile or fixed-allocation native implementation is claimed.
Rule 10 uses warning-strict normal/optimized execution and AST inspection;
a separate static analyzer is unavailable in the declared environment.
Extending these domains requires revisiting their memory and loop bounds.
