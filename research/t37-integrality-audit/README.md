# Integer penalties in the T37 signed-dual relaxation

**Adversarial mathematical audit; no new kappa.** The fixed-U8 all-replica
bound in Jonathan Capalbo's PR942 is consistent with integer replica counts.
This package strengthens its qualitative equality condition with a **sharp
positive numerator penalty** whenever `37` does not divide the replica count,
and provides certified lower bounds for all 37 residue classes.

The exact base is `407d52ff15b2217b6e22bce44728b4c3907b6515`. At that base,
the selected conditional kappa is `0.001661960547713947`, from PR942 at
`1960cfa919a0945d0ca4cb14ea96237000037903`. That selection is unchanged.

## Result

Use exactly the fixed family and endpoint from
[the inherited all-T proof](../complex-t37-owners/ALL-T-PROOF.md):

```
z = 0.001664727258740678855773
phi(r) = r*(73/r)^z
c(r) = 48*phi(r) - r*phi(48)
lambda = c(1)/925
delta(r) = c(r) - lambda*v(r)
```

For every nonnegative **integer** residual profile satisfying that proof's
rank and signed-credit constraints at a positive integer `T` with `37 ∤ T`,

```
Delta = sum_(0<r<48) c(r)*n_r - 150*T*lambda
      >= delta(2)
       = c(2) - (26/37)*c(1)
       > 0.291373150447.
```

This constant is sharp **in the arithmetic relaxation**: `T=29` with
`{1:4, 2:1, 48:8689}` attains exactly `delta(2)`. Adding any number of
`(T,n1,n48)=(37,6,11086)` blocks preserves its excess. This does not
construct a physical owner assignment for these profiles.

For the full normalized complex moment, including the unchanged repeated
local profile, the exact penalty is

```
M_T(z) - M_formal_T37(z) = Delta / (3,139,584*T).
```

The penalty tends to zero as `T` grows. It establishes **no fixed improvement
in the root or kappa grid**, and does not exclude other supplier families.

The [proof](PROOF.md) derives the stronger `1200`-unit credit-slack lattice
and reduces every positive replica count to a 37-state residue graph. The
receipt checks every directed edge inequality of an exact rational
potential. Its 37 explicit profiles give upper witnesses within `10^-23`
of their corresponding certified numerator lower bounds. These are rigorous
sandwiches; rounding the graph weights is not presented as an exact symbolic
optimization of the transcendental costs.

## Reproduce

Python 3.11+ and the standard library suffice. From the repository root:

```sh
python -I -O -B research/t37-integrality-audit/verify.py
```

Expected final line:

```
PASS_T37_INTEGRALITY_AUDIT: 1163 bins; 37 residue certificates; 1591 edge inequalities; 8 rejection controls; no new kappa
```

The checker verifies [source hashes](SOURCES.json), recomputes all intervals,
checks all certificate fields against [EXPECTED.json](EXPECTED.json), and
writes no files. To generate a fresh receipt, pass `--write NEW_FILE`;
existing files are refused. Checks remain active under optimized Python.

A separately structured checker is also supplied:

```sh
python -I -O -B research/t37-integrality-audit/independent_check.py
```

It uses a different bin enumeration and shortest-path computation, checks
the full moment normalization directly, and imports no primary checker.
The primary checker reuses the repository's pinned base-two rational
engine; the second reuses its pinned Mercator engine. Neither claims to
provide a new proof of those arithmetic engines or formal verification of
the multiplication theorem.

## Controls and completed coverage

The primary replay completes all 1,163 legal bin count vectors, all 43 graph
edge types at all 37 states (1,591 inequalities), and all 37 relaxation
witnesses. There is no replica cutoff: the proof lifts each residue witness
by the exact T37 block. Negative controls exhibit:

- Fractional equality at `T=1` if count integrality is dropped.
- A mass-correct `T=8` profile that fails the credit inequality.
- A credit-correct `T=1` profile that fails rank balance.
- A mass/credit-correct `T=1` profile that would give false equality if
  the strictly positive rank-30 penalty were erased.
- An inflated potential at seeded residue `65 % 37 = 28`, a missing slack
  edge, an omitted negative-credit rank, and an overstated edge bound.

The seed-65 example is `T=65`, with `{1:10,20:1,48:19475}`, obtained from
the residue-28 witness by adding one T37 block. Its excess is `delta(20)`.
Seed 65 selected this obligation from the three
candidates in [CLAIM.md](CLAIM.md); it is not a randomized evidence sample.
The stopping rule was complete residue coverage and the stated controls.

## Scope, pins and credit

This audits the finite arithmetic relaxation at one specified endpoint.
It retains the U8 widths, capacity inventory, whole-helper convention and
signed prices. Bin-type inventory realization, chronology, source access,
frame changes, restoration, hosting, precision/tape admission, all-size
compiler, common-label/mutable-source realization, bit interfaces and
analytic transfer remain outside this contribution. No supplier program,
complete recurrence, or finite invoice is proposed or changed.

Credit belongs to Chafik Boukhalfa (@chafreaky), whose PR795 supplies the
signed prices and PR890 the fixed-family equations and finite `T<=22`
relaxation; Jonathan Capalbo (@jon314159), whose PR942 supplies the all-T
support inequality and selected T37 construction; and Joel Pulikkan
(@GamingPuzzled), whose concurrent [PR962](https://github.com/CrocSwap/integer-mult-bounds/pull/962)
independently constructs T37 and identifies the normalized optimum. The
U8 supplier lineage includes Jeremy Kothe and Hao Yan; unchanged bit and
arithmetic dependencies retain their predecessor notices, including eumemic
and the maintainer arithmetic lineage. This audit claims priority for none
of those results. Its addition is the slack lattice and quantitative
integer-residue certificates.

Prepared for **woklerx** with substantial **OpenAI Codex** assistance,
including a separately implemented agent check. This is not independent
human peer review. New work is Apache-2.0 under the repository license.
Source implementations, `upstream/`, selected certificates and the review
ledger are untouched. The source pins identify what was audited even if
the accepted frontier subsequently changes.
