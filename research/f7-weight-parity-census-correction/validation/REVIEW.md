# Independent validation of the parity correction

The generic fixed collision budget applied to coordinate-bit-0 groups is
unsound. The corrected C engine passes the independent gates below. These
small counterexamples invalidate the old pruning premise; they do **not**
constitute an n=7, L=20 universal word or by themselves settle that census.

## Explicit counterexamples

The canonical restored word `001212` at n=3 has prefix path
`[0,1,0,2,6,4]` and distinct states `{0,1,2,4,6}`. Direct pairwise XOR covers
all eight masks. Its Hamming-weight groups are E=`{0,6}`, O=`{1,2,4}`,
so the target split is (2,3) and the fixed even budget is
`C(2,2)+C(3,2)-(4-1)=1`. Its weight-group collision excess is 0. Its bit-0
groups have sizes (4,1): the size-four group has six pairs but only three
pair-XOR values `{2,4,6}`, giving excess 3. The old rule rejects this universal
word because 3 > 1.

The balanced, self-avoiding word `01021323` at n=4 is a stronger regression
for the original simple-walk use case. Its prefix path consists of eight
distinct states `[0,1,3,2,6,4,12,8]`; it is restored and its pairwise XOR
covers all sixteen masks. Its weight split is (4,4), with budget
`2*C(4,2)-(8-1)=5`. Its bit-0 split is (6,2). The size-six group has fifteen
pairs and seven distinct XORs; the size-two group has one pair and one XOR,
so the old-rule excess is 8 > 5. In the complete n=4, L=8, (4,4) brute census,
22 canonical words are universal and 6 of those violate the old bit-0 rule.

For weight groups, universality forces `supp(EE) union supp(OO)` to cover all
`2^(n-1)-1` nonzero even-weight masks. Therefore
`C(s,2)-|supp(EE)|+C(t,2)-|supp(OO)| <= C(s,2)+C(t,2)-(2^(n-1)-1)`.
This proof uses s,t as **weight-group** cardinalities. A bit-0 partition also
has an analogous bound, but its pair capacities must use its actual group
cardinalities, which the target weight split does not fix. Likewise, the
correct odd-weight bound is `s*t-|supp(EO)| <= s*t-2^(n-1)`.

## Independent gates

`brute_validation.py` enumerates every raw word, tests positive even label
multiplicities directly, canonicalizes only for counting, and computes
universality by the literal set `{a XOR b : a,b in P}`. It imports no census
engine. Results are in `brute_results.json`.

| n | L | Raw words examined | Canonical restored | Canonical universal |
|---|---|---|---|---|
| 3 | 6 | 729 | 15 | 10 |
| 3 | 8 | 6561 | 210 | 182 |
| 4 | 8 | 65536 | 105 | 26 |

`check_corrected_c.py` compares every split in these three cases, including
zero-hit targets, in four budget modes (both, even only, odd only, none):
**164 successful comparisons**. All universal counts match. Every emitted
hit is independently checked for length, canonical form, restoration, target
weight split, direct XOR coverage, and uniqueness. Exact all-restored leaf
counts are compared only with budgets disabled; budgeted candidate leaf
counts are intentionally not equated with an unpruned histogram.

It also passes **12 fail-closed checks**: caps 1, 10 and 50 return exit 2,
`aborted=true`, `complete=false`, and exactly the allowed nodes; malformed
inputs, missing/unopenable hit output, overlapping shards, and invalid caps
return exit 1; an existing hit file remains unchanged. The receipt is
`corrected_c_results.json`. A caller must require successful exit **and**
`complete=true` before treating a run as a complete exclusion.

`crosscheck_n7.py` supplies a second Python reference with the C traversal's
node semantics. At each novel state it recomputes all pair-support sets from
scratch, instead of copying C's bitset and incremental collision bookkeeping.
It compares n=7 L=20 splits (10,10), (10,9), (10,8), (9,9), (10,7), plus
n=7 L=18 split (9,9), each at prefixes `0012`, `0102`, `0123` with both
budgets and with the even budget alone. All **36 capped comparisons** match
exactly in nodes, candidate leaves, hits, both prune counters, and abort
status. The cap is 5000 per comparison. These are cross-checks, not complete
n=7 census claims. Receipt: `n7_crosscheck_results.json`.

The earlier `agent-b/slow_census.py` has different node and leaf semantics:
it gates only the universal test with budgets and retains all restored
leaves. Its leaf histogram therefore must not be equated to C's budgeted
candidate leaves. The independent n=7 reference here makes the traversal
semantics explicit before comparing counters.

## Reproduction

From the directory containing sibling `engine/` and `validation/` directories:

```sh
python3 -I -B -O validation/brute_validation.py
python3 -I -B -O validation/check_corrected_c.py
python3 -I -B -O validation/crosscheck_n7.py
```

All three default to fresh system temporary output directories and leave the
package untouched. Each accepts `--output-dir PATH` to retain outputs in a
chosen directory. The two C gate scripts accept `--engine-source PATH`;
otherwise they locate sibling `engine/corrected_census.c`. They require a C11
compiler available as `cc`. Critical checks use explicit exceptions, so
Python `-O` does not disable validation. The three commands were executed
successfully with `-I -B -O`.

Freeze scope: the three Python source files, the three JSON receipts, and
this report. Compiled programs and caches are excluded.
