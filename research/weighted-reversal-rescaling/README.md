# Minimum diagonal rescaling of weighted reversals

**Claim type: scoped algebraic proof with exact finite corroboration. No new kappa.**
This contribution was produced by Nick Petalas. Apache-2.0.

Every defective reversal orbit needs exactly two nonidentity output-coordinate
scales, counting both banks. This holds for every modulus M >= 2, every positive
length, and every list of unit weights. The theorem also counts all minimum
repairs and gives the complete support generating polynomial. It answers the
even-length gap in Wentao Li's [#4095](https://github.com/CrocSwap/integer-mult-bounds/pull/4095)
while allowing multiple defective pairs and a defective central coordinate.

The new result is support optimality and its counting law for arbitrary weight
lists. The reciprocal-weight wrapper contract is Jerry Chen's
[#2950](https://github.com/CrocSwap/integer-mult-bounds/pull/2950).
The odd-length, one-defective-end dual-scale classifications are Wentao Li's
[#4070](https://github.com/CrocSwap/integer-mult-bounds/pull/4070),
[#4073](https://github.com/CrocSwap/integer-mult-bounds/pull/4073) and #4095.
Their results are cited inputs, not re-verification deliverables.

## Exact boundary

Work on G = (Z/MZ)^n, with reversal r(i) = n-1-i and unit weights a_i.
Let R_a x have coordinate a_i x_{r(i)}. The weighted callee is

```text
F_a(H,D) = (R_a D, R_a^-1 H).
```

After this callee, multiply H coordinate i by u_i and D coordinate i by v_i,
where all u_i,v_i are units. A repair must make the resulting map exactly F_b
for some weighted reversal R_b satisfying R_b^2 = I. This is equality on every
arbitrary dirty H,D, with no input restriction or extra bank.

Its support cost is the number of nonidentity coordinate scales on both banks,

```text
c(u,v) = #{i : u_i != 1} + #{i : v_i != 1}.
```

These are algebraic coordinate operations. The cost is not a Boolean gate,
native call, tape-movement or recursive-child price. No physical scale circuit
or supplier invoice is assumed free.

## The minimum and every attaining repair

Call a reversal orbit defective when a_i a_{r(i)} != 1 modulo M. Let p be the
number of defective two-element orbits and c in {0,1} the number of defective
fixed orbits. Put U = (Z/MZ)^*, phi = |U|, and

```text
rho = #{t in U : t^2 = 1 mod M}.
```

Then the exact minimum support is 2(p+c). There are exactly 2^p rho^c distinct
minimum repairs, counted as ordered pairs of diagonal maps (u,v).

They are precisely the following choices, independently in each orbit.

- A nondefective orbit has every u coordinate equal to 1.
- In a defective pair {i,j}, put d = a_i a_j. Set (u_i,u_j) to either
  (d^-1,1) or (1,d^-1).
- At a defective center i, choose any t in U with t^2=1 and set u_i=t a_i^-1.
- In every case set v_{r(i)}=u_i^-1. This determines the entire second bank.

In particular, even n with a=(a0,middles,1), a0 != 1 and reciprocal middles
has exactly two minimum repairs of support two. If another pair is defective,
two scales no longer suffice. An odd central defect is repairable with
independent scales, even though no shared scalar can repair it.

### Proof

The first bank fixes b_i=u_i a_i. The second bank coefficient at coordinate
r(i) is v_{r(i)} a_i^-1. Equality with R_b^-1 forces

```text
v_{r(i)} = u_i^-1.                                  (1)
```

This uses only that a_i and u_i are units. Thus the support cost is exactly
twice the number of nonidentity u coordinates. The condition R_b^2=I is

```text
u_i u_{r(i)} = (a_i a_{r(i)})^-1.                    (2)
```

For a defective two-element orbit, at least one u coordinate differs from 1.
Exactly one suffices, and its value is forced by (2). There are two choices of
coordinate. A nondefective orbit needs none.

At a fixed orbit, (2) says (a_i u_i)^2=1. Its solutions are exactly
u_i=t a_i^-1 for the rho involutory units t. If a_i^2!=1, none equals 1.
If a_i^2=1, the unique minimum choice is u_i=1. Every unit group contains 1,
so the required choices always exist. The orbits are disjoint, proving both
the lower bound, the construction and the stated count. No field cancellation
or odd-modulus assumption is needed.

## Complete support polynomial

Let Z_a(z) = sum z^{c(u,v)}, over all valid repairs. For each two-element
orbit use the corresponding factor below; include the center factor when n
is odd. Then Z_a is exactly their product.

| Orbit | Nondefective | Defective |
|---|---|---|
| Two coordinates | 1 + (phi-1) z^4 | 2 z^2 + (phi-2) z^4 |
| Central coordinate | 1 + (rho-1) z^2 | rho z^2 |

For a pair with product d, choose any u_i in U; (2) uniquely fixes
u_j=d^-1 u_i^-1. If d=1, one choice makes both 1 and the other phi-1 choices
make both nonidentity. If d!=1, exactly two choices make one coordinate 1;
the other phi-2 make both nonidentity. A defective pair requires phi>=2,
so the coefficient is nonnegative. The center factors follow from the proof
above. Equation (1) doubles the support. Multiplication is valid because
neither equation couples distinct reversal orbits.

At z=1 the formula counts phi^{floor(n/2)} rho^{n mod 2} repairs, independently
of the weights. This follows from the explicit orbit enumeration, not from
an independence assumption about a physical producer.

## One scalar shared by both output banks

Now restrict all nonidentity scales on either bank to one common unit lambda;
the two banks' coordinate supports may be chosen separately. If any orbit is
defective, such a repair exists exactly when the center is nondefective and
all defective pair products equal one common lambda != 1 with lambda^2=1.
When it exists its minimum support is 2p, with exactly 2^p minimum repairs.
If no orbit is defective, the unique minimum repair is the identity.

Indeed, (1) requires a nonidentity scale and its inverse on the opposite
bank. Both equal lambda, so lambda^2=1. In a pair, the product of selected
scales is either 1 or lambda; only one selected endpoint changes a defective
product, forcing d=lambda. At a center, multiplying a_i by lambda cannot
change a_i^2, so a central defect cannot be repaired. These conditions also
suffice by selecting one endpoint in each defective pair. This explains why
the independent-bank optimum need not be available under the shared-scalar
restriction.

## Evidence and reproduction

The verifier enumerates all unit-weight lists in 23 fixed modulus/length
domains. For each list it independently enumerates every ordered pair (u,v),
forms the two literal monomial bank maps, compares them and squares the first.
It compares the entire observed support histogram with Z_a, its first
coefficient with the optimum/count formula, and the common-scalar minimum
with the criterion above. The finite enumeration covers 319 weight lists and
622,195 ordered scale assignments.

Six additional fixtures enumerate every constructed minimum repair, including
three defective pairs modulo 15 and a central defect. Literal execution of
the six-operation ordinary wrapper on 202 module-basis columns checks the
dirty-bank interchange. Linearity makes a module-basis check exact for these
finite maps; the quantified theorem is the written proof above.

Ten controls cover invalid/nonunit inputs, an omitted second-bank scale,
incorrect reversal of its support, equal diagonal maps, the central shared-
scalar obstruction, an attaining common involution and differing defects.
The generated [RESULT.json](RESULT.json) binds every other package file by
SHA256. Typed receipt comparison distinguishes booleans from integers.
Normal verification writes no files.

From the repository root, with CPython 3.12 and only the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/weighted-reversal-rescaling/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/weighted-reversal-rescaling/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/weighted-reversal-rescaling
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/weighted-reversal-rescaling --check-source-history
```

Any CPython 3.12 installation can replace that interpreter path. The standalone
verifier also works in a Git-free export. To regenerate evidence, pass
`--emit-to NEW_EXTERNAL_FILE`; this exclusively creates a fresh receipt.

## Scope, provenance and limitations

Base: canonical main 624de9dc66858af0945e5f8a0942488d62280d43, priority revision 7.
The uniform-transfer-audit card is changed to this algebraic side question.
Its connection is the weighted ordinary-callee boundary, where the reciprocal
condition matters before any proposed normalizer can be priced. This package
does not claim an audit of #4100 or a new selected supplier.

Exact main-tree provenance is recorded in [SOURCES.json](SOURCES.json).
No predecessor code or scientific receipt is imported or executed. The selected
source-binding baseline was run as orientation only. Live open PRs, recent
handoffs, merged searches and distinctive main-tree README searches were
checked; the local-note overlap inventory is sparse and incomplete. No
exhaustive novelty claim follows from those searches.

This result permits arbitrary independently chosen diagonal unit scales and
keeps the weighted reversal and surrounding ordinary wrapper fixed. It gives
no optimum over changed wrappers, nondiagonal maps, nonunit weights, auxiliary
banks or input-dependent scales. The checker bounds its finite arithmetic
domain to M<=16 and n<=6; the proof has no such restriction. Its Python managed
allocation is a documented runtime deviation from fixed-allocation discipline.
Every loop is bounded by those finite domains and the per-list limit of 4,096
scale assignments. There is no recursion or dynamic code generation.

Physical scale preparation, access, restoration, storage, native implementation,
compiler, stock, precision/tape and analytic recovery obligations remain
unpriced. The support theorem is not a complete multiplication theorem.
No Lean, Docker, predecessor scientific replay or selected operator replay
was run. Independent human and formal proof-kernel review are unclaimed.

Credit Jerry Chen for #2950's wrapper contract and precision-blind example;
Wentao Li for the dual-scale setting and restricted support classifications;
Nick Petalas for the earlier #2808 wrapper; David Arias for the retained
ordinary caller; Jose Manuel and the credited source lineage for its physical
composition. Their files, credit lines and source notices are unchanged.

## Open next questions

Can a concrete weighted callee realize one of these minimum-support repairs
at a favorable complete cost? Start with a literal source and charge each
scale, inverse, frame change, access and restoration. The blocker is a physical
implementation and its invoice, not algebraic existence. Coordinate prices
that depend on the scalar or location also need a different optimization
objective; support optimality alone cannot choose the cheapest physical repair.
