# Exact polynomial pairs across two stage-0 gaps

**Claim type: scoped written proof with exact finite corroboration.**
For the two literal gaps in unpaidmoon's [PR #7103][7103], replacing constant
insertion matrices by matrices over `K[x]` permits previously excluded
off-diagonal couplings through coordinate 1. Over every field `K`, all pairs
of entry degree at most `d >= 0` form an affine space of dimension
**`64d + 50`**. In particular, the degree-one dimension is **114**. The proof
gives an explicit bijection, hence exactly `q^(64d+50)` pairs over `F_q`.
The checker enumerates small entrywise factors of that count; it does not
enumerate the entire degree-one space.

This answers Open next question 2 of #7103. Its constant-entry classification
is a cited predecessor, not the deliverable. No new kappa, paid-rank gain,
native caller, supplier admission or complete multiplication theorem is claimed.

## Literal word and target

Use zero-based matrix indices `0,...,7` and ordinary written matrix-product
order, exactly as in #7103. Work in `K[x,y,z][e]/(e^2)`, with `e` central.
For stage `s=0,1,2`, write `x_s=x,y,z`, respectively. Its three diagonal gates,
in order, are

```text
I + x_s E00,  I + x_s E11,
I + x_s (E_(2+2s,2+2s) + E_(3+2s,3+2s)).
```

Concatenate the stages to obtain `G0,...,G8`, and let `P=G0...G8`.
Insert `I+eR` just after `G0` and `I+eS` just after `G1`. The question is

```text
G0 (I+eR) G1 (I+eS) G2 ... G8 = (1+e) P.             (1)
```

Here `R,S` have entries in `K[x]`. Their pure term always remains `P`.
Equation (1) requires the coefficient of `e` to equal **`P`**, rather than
the identity. Matrix equality means the endpoint holds on every initial
input vector; it does not establish a physical workspace contract.

## Classification and proof

Put `t=1+x`, `B=G1=diag(1,t,1,1,1,1,1,1)` and `H=G2...G8`.
Expanding the left side of (1), using centrality and `e^2=0`, gives

```text
P + e G0 (R B + B S) H.
```

Every diagonal entry of `G0` and `H` is a nonzero polynomial. Since
`K[x,y,z]` is an integral domain, entrywise cancellation is valid even
though these matrices are not invertible over the polynomial ring.
Thus (1) is equivalent to

```text
R B + B S = B.                                      (2)
```

Write `b_1=t` and `b_i=1` for `i != 1`. Equation (2) at `(i,j)` is
`b_j R_ij + b_i S_ij = b_i delta_ij`. Solving each independent entry gives
the complete list:

| Position | All solutions |
|---|---|
| `i=j` | `R_ii=a_i`, `S_ii=1-a_i` |
| `i!=j`, both different from 1 | `R_ij=a_ij`, `S_ij=-a_ij` |
| `i=1`, `j!=1` | `R_1j=-t p_j`, `S_1j=p_j` |
| `j=1`, `i!=1` | `R_i1=p_i`, `S_i1=-t p_i` |

All parameters are arbitrary polynomials. Necessity follows directly from
the entry equation; substitution proves sufficiency. Each parameter can be
recovered from the displayed pair, so the parametrization is injective as
well as surjective. In characteristic two the displayed minus signs become
plus signs.

Now impose entry degree at most `d`. Each of the eight diagonal parameters
and the `7*6=42` off-diagonal parameters missing coordinate 1 has degree at
most `d`. Each of the fourteen crossing parameters has degree at most `d-1`:
for nonzero `p`, the monic polynomial `t` satisfies `deg(tp)=deg(p)+1`.
When `d=0`, those fourteen parameters must be zero. The solution space is
therefore explicitly affine-isomorphic to

```text
(K[x]_(<=d))^50  x  (K[x]_(<=d-1))^14,
```

where `K[x]_(<=-1)={0}`. Its dimension is
`50(d+1)+14d=64d+50`. Over a field with `q` elements the bijection gives
the stated exact count. This is a parameter count, not a claim that the
checker visited each full pair.

The simplest new crossing solution, valid even over the integers, is

```text
R = I - (1+x) E10,       S = E10.
```

Indeed, `E10 B=E10` and `B E10=t E10`, so `RB+BS=B`.
It has degree one. Degree zero cannot realize any nonzero crossing entry,
by the degree restriction just proved. This settles the minimum degree for
opening such a coupling. Reversing the two occurrences of `t` does not work;
the written product order matters.

## Evidence and reproduction

The proof above supplies the quantifiers over every field and every `d`.
The standalone [verifier](verify.py) uses only the Python 3.12 standard library.
It derives both entry scales from the literal nine gates, then:

- computes coefficient-system ranks for `d=1,2,3,4` over `F2,F3,F5,F7`;
  the resulting affine dimensions are `114,178,242,306`, respectively;
- exhausts **56,960 entry pairs** in the four domains `(q,d)=(2,1),(2,2),
  (3,1),(3,2)`, compares the solved criterion with the literal scales, and
  multiplies the entrywise counts using their Cartesian independence;
- multiplies the full eleven-factor operator for **56 integer crossing
  witnesses**, covering both crossing directions, all seven other coordinates
  and parameters `1,x,x^2,x^3`, plus the affine origin `(I,0)`;
- rejects four false witnesses: reversed crossing orientation, a missing
  `x` term, an omitted second insertion, and `(I,I)`.

It prints `PASS_POLYNOMIAL_TWO_GAP_INSERTIONS` and a generated JSON receipt
binding its results to SHA256 hashes of all five package files. The receipt
is emitted to stdout, never maintained by hand.

From the repository root, the exact local interpreter is
`~/git/integer-mult-bounds/.venv/bin/python3.12` (CPython 3.12.15):

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/polynomial-two-gap-insertions/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/polynomial-two-gap-insertions/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/polynomial-two-gap-insertions
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/polynomial-two-gap-insertions --check-source-history
```

Both registered checks have 30-second limits. Explicit exceptions keep the
checks active under `-O`. [TASK.json](TASK.json) records the changed card
scope and open question. [SOURCES.json](SOURCES.json) pins the historical
catalogue and selected record, and separately lists the immutable external
citation. No external file or predecessor verifier is loaded at runtime;
the word and convention used here are fully specified above.

The verifier has no recursive calls or unbounded searches. Width is fixed
at eight, degree at four, field samples at seven, the largest enumeration
at 729 polynomial pairs per entry, and the longest word at eleven factors.
Python requires dynamic allocation; bounded finite collections replace the
fixed-allocation rule. Warning-strict normal and optimized checks provide
runtime diagnostics. No additional static type checker is required by this
package. These checks corroborate a written proof, not a formal-kernel proof.

## Limitations

The allowed insertion entries change from constants to `K[x]`. Their
implementation, interaction with the native stage operator, physical
restoration, precision, hosting and complete signed invoice are unproved.
The displayed witness has no established cost advantage over `(I,0)`.
Other gap pairs, non-idempotent stage factors and the larger paired-star
callers are outside scope. No predecessor scientific replay, Lean, Docker,
selected-frontier replay or complete multiplication implementation was run.
The selected result is unchanged.

## Open next questions

Can a polynomial crossing pair reduce a complete legal invoice after every
`x`-dependent entry is implemented and restoration is charged? Start with
`R=I-(1+x)E10, S=E10` and compare its physical realization with `(I,0)`.
The blocker is a legal, fully priced implementation of those entries. This
is necessary before the new algebraic freedom can advance a supplier.
The structured question is also in [TASK.json](TASK.json).

## Credit

This result was produced by Nick Petalas. New work is Apache-2.0.

Credit **unpaidmoon** for #7103, exact head
`f3af1384aeda8c75be58f09cb07da3941ba7aba3`, which poses the polynomial-entry
question and fixes the gap convention; #7027, head
`1ba2ac5adfe58fbe9dba34d50d4e5d30633ce3d0`, supplies the diagonal word;
#7039, head `e4ddcd2fde8c46b7e528e8806ab72d9bf7690978`, distinguishes the
one-gap coefficient targets. Credit **Ali Romman** for the paired-star
contract in #5747 and its retained #5673, #5631 and #5617 lineage. Their
source attributions remain in their original packages. The new step here
is the polynomial classification, its exact degree filtration and its
explicit crossing witnesses.

[7103]: https://github.com/CrocSwap/integer-mult-bounds/pull/7103
