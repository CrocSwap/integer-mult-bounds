# Exact topology optimum for the nineteen-leaf query caller

This contribution was produced by Nick Petalas. Claim type: a scoped
mathematical proof with a finite integer certificate.

For the four-field merge and three-query root of Ali Romman's
[PR6348](https://github.com/CrocSwap/integer-mult-bounds/pull/6348), no
binary topology on nineteen native leaves improves the complete recursive
target-minus-paid power sum at any exponent `0 < s < 1`. The published
forest with root sizes `4,7,8` attains the optimum. Its internal-node size
histogram is the unique optimal histogram for each such exponent:

```text
size          2  3  4  7  8
multiplicity  9  1  4  1  1
```

The result covers every positive three-part root partition, unbalanced
trees, arbitrary leaf labels and either order of the two children. It is
new finite-class optimality coverage. The predecessor supplies the module
and one attaining construction, without claiming a topology optimum. Its
merge identity and native realization are premises here, not review targets.

This rules out a better recursive invoice through topology alone at this
leaf count. A changed merge, a changed leaf count or a changed native local
profile is a different question. There is no new kappa or selected-frontier
change, supplier admission, physical implementation or complete multiplication
theorem.

## Reduction to a tree reward

Write `P` for the number of ports and `d` for the fresh rank of each native
stage. In the actual source, `P=104` and `d=8`. An internal node on `n`
leaves supplies two independent rank-`dn+1` main targets per port, pays two
rank-`dn` whole idle calls per port, and pays one thin rank-one query per
port. All local helper/paid profiles of the nineteen native leaves stay
fixed, as does the rank-153 root target pair. No helper or idle is free.

Thus, with target-minus-paid sign convention, the full recursive margin is

```text
K(H) + 2P sum_v w(n_v),        w(n) = H(dn+1) - H(dn),
K(H) = 19 L(H) + 2P H(19d+1) - 16P H(1).
```

Here `L(H)` is the fixed local helper credit minus local paid bill per
native call. Every three-root forest has sixteen binary internal nodes.
The sum runs over precisely these nodes, including each nontrivial subtree
root and excluding the final three-query root. This accounts for all
topology-dependent recursive targets and paid jobs in the retained contract.
Ordinary scalar work, routing, ownership and compiler realization retain
their separate obligations; this theorem does not optimize those costs.

## A finite certificate for all decreasing convex rewards

Let `F` be any full binary forest with three nonempty trees and nineteen
leaves. Each subtree has at most seventeen leaves. For each integer
`k=3,...,17`, define `h_k(n)=max(k-n,0)`. The certificate proves

```text
sum_{v in F} h_k(n_v) <= B_k,
```

where the attaining histogram above gives, in increasing order of `k`,

```text
9, 19, 33, 47, 61, 76, 92, 108, 124, 140, 156, 172, 188, 204, 220.
```

[CERTIFICATE.json](CERTIFICATE.json) contains seventeen integer upper bounds
`U_k(n)`, for `1 <= n <= 17`, for each hinge. The checker requires

```text
U_k(1) = 0,
U_k(n) >= h_k(n) + U_k(a) + U_k(n-a)   for every 1 <= a < n,
U_k(a) + U_k(b) + U_k(c) <= B_k        whenever a+b+c=19 and a,b,c>=1.
```

Induction on the number of leaves proves the tree upper bound. The last
inequality then proves the forest upper bound. These are exhaustive finite
inequality checks, not samples of trees or real exponents. The verifier
checks 2,040 binary split inequalities and 2,295 ordered root inequalities.
It constructs the attaining forest separately and counts its actual nodes.
The optimizer is used only to generate a witness. It is not trusted by the
upper-bound checker.

For a nonincreasing convex sequence `w(2),...,w(17)`, put

```text
alpha = w(16)-w(17) >= 0,
delta_k = w(k-1)-2w(k)+w(k+1) >= 0,   3 <= k <= 16.
```

Successive finite differences give the exact identity

```text
w(n) = w(17) + alpha h_17(n) + sum_{k=3}^{16} delta_k h_k(n).
```

Every forest has sixteen internal nodes, so its constant term is the
same. Multiplying the certified hinge bounds by these nonnegative
coefficients proves that the named forest maximizes every such reward.
This is an optimality result over a continuum of rewards, obtained from
fifteen exact integer certificates.

For the power tariff, more generally take any real `d,b>0` and let
`w(x)=(dx+b)^s-(dx)^s`. When `0<s<1`,

```text
w'(x)  = ds [(dx+b)^(s-1) - (dx)^(s-1)] < 0,
w''(x) = d^2 s(s-1) [(dx+b)^(s-2) - (dx)^(s-2)] > 0.
```

Consequently every coefficient in the hinge decomposition is strictly
positive. Equality of the reward forces equality of all fifteen hinge
scores. If `c_n` is the number of nodes of size `n` and
`A_k=sum_n c_n h_k(n)`, then `c_2=A_3`,
`c_n=A_{n+1}-2A_n+A_{n-1}` for `3<=n<=16`, and
`c_17=16-sum_{n=2}^{16} c_n`, with `A_2=0`.
Thus those scores and the fixed node count determine the histogram
uniquely. This proves the strict histogram assertion. The real-parameter
extension is a formal reward statement, not a construction of new native
operators. The invoice application uses `d=8,b=1`.

## Reproduce

Use CPython 3.12 and its standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/query-tree-topology-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/query-tree-topology-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/query-tree-topology-optimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/query-tree-topology-optimum --check-source-history
```

Expected marker: `PASS_QUERY_TREE_TOPOLOGY_OPTIMUM`, followed by the
registered runner's `PASS_REGISTERED_RESEARCH_PACKAGE` where applicable.
The direct commands emit generated receipts containing source and package
hashes. `--receipt PATH` additionally creates a new receipt at that path.
Normal and optimized registered commands are read-only. To regenerate the
integer certificate, run `generate.py` with the same interpreter and `-B`;
it writes JSON to stdout and checks equality with the retained certificate.

The verifier checks exact rational hinge identities and rejects a lowered
split bound, an inflated unattainable root bound, an omitted hinge, a
Boolean substituted for an integer, a wrong leaf count and a worse
histogram. It authenticates both predecessor text inputs before checking.
No floating-point power evaluation or predecessor scientific replay is
needed. The written derivative, induction and equality arguments remain
outside a formal proof kernel. Independent human and formal proof-kernel
review are unclaimed.

## Scope, credit and code constraints

Credit Ali Romman for PR6348's four-field extension, paid complement,
binary-tree caller, nineteen-leaf construction and complete invoice;
Cinna Davis for the retained thin-query interface and query-thinned path;
DreamingOfClouds for the preceding native-word work; and the retained
P104/helper/native/compiler/outer lineage. Discrete finite differences and
dynamic programming are classical. The new contribution is the simultaneous
hinge optimum and its fixed-caller consequence. All predecessor files and
credit lines retain their bytes. Apache-2.0.

The five inherited framework assumptions retain their status. Native
all-column implementation, owned erasure, compiler closure, precision/tape
and analytic recovery are not discharged. The source full replay, selected
cold replay, physical caller execution, Lean and Docker were not run.

The new scripts use structured bounded loops, direct calls and checked
contracts. Their functions fit within sixty lines. Rule 3 of Power of Ten
has a managed-runtime deviation in these two Python scripts: Python and
JSON parsing allocate dynamically. The certificate input is capped at
64 KiB, with fifteen rows of seventeen bounded integers; all mathematical
work uses the fixed nineteen-leaf domain. There is no steady service or
unbounded work queue. Warning-strict normal and optimized execution check
the bounded paths and failure controls. A future variable-size solver
would need new resource limits before extending this scope.

## Open next questions

1. Can a changed leaf count improve the complete supplier invoice? This
   theorem fixes nineteen. First form the corresponding complete local,
   thin, whole-idle and root profiles, then retain compiler and outer
   charges. The finite nineteen-leaf certificate does not settle that task.
2. Can a different merge or root contract improve the price beyond this
   topology optimum? First state independent arbitrary inputs and every
   paid complement. A favorable formal reward alone does not establish
   native realization, restoration or supplier admission.
