# Prime-power kernel valuations and Newton polygons

Independent verification and a scoped research note; **no new kappa**.
Concurrent [#796][796] submitted the same mathematical formula before this
package's final overlap refresh. The distinct contribution here is exact
integral uniformizer division, corroboration of its pinned receipt, and every
primitive embedding at radix 81, beyond its cutoff of 68. No priority is claimed.

For Ali Romman's PR621 kernel

    f(z) = sum_{j=0}^{r-1} a_j z^j,
    a_j = product_{s=j+1}^{r-1} (1-u^s),   r=p^a,

normalize the nonarchimedean valuation by `v(1-u)=1`. The exact result is

    v(a_j) = sum_{s=j+1}^{r-1} p^{v_p(s)}.

The lower Newton polygon has vertices
`(r-p^b, b*phi(p^b))` for `b=a,...,1`, followed by `(r-1,0)`.
Exactly `phi(p^b)` roots, counted with algebraic multiplicity, have valuation
`1+(b-1)(p-1)/p`. In the normalization `v_p(p)=1`, divide these values by
`phi(r)`. For example, radix 8 has four roots of valuation 2, two of valuation
3/2 and one of valuation 1 in the first normalization.

[PROOF.md](PROOF.md) supplies the uniform written argument. The finite replay
does not prove the uniform statement. The kernel and the earlier conclusion
that its algebraic roots are not units belong to [PR621][621]; the additional
result here is their exact ramified valuation distribution.

## Reproduce

From the repository root, using Python 3.11+ and no external dependencies:

```sh
python -B -I -O research/prime-power-newton-valuation/verify.py --check research/prime-power-newton-valuation/EXPECTED.json
```

Expected output:

```text
PASS 214 primitive embeddings; 10268 exact coefficients; 8 negative controls
```

The focused tests are:

```sh
python -B -I research/prime-power-newton-valuation/test_verify.py
```

Expected: nine tests pass. If Python is managed by uv, prefix either command
with `uv run --no-project`. To regenerate only this receipt, replace `--check`
with `--output` and a new output path. Verification reads, but does not rewrite,
the predecessor package or selected frontier.

## What is independently checked

The new engine imports no predecessor field arithmetic, determinant, inverse,
SymPy or scan code. It builds each tail product in `Z[u]/(u^r-1)` using integer
cyclic differences, reduces by the explicit cyclotomic polynomial, and
substitutes `u=1-pi` using binomial coefficients. It checks the shifted
cyclotomic polynomial is Eisenstein and obtains every coefficient valuation
in two ways:

- The minimum of `phi(r)*v_p(c_i)+i` in the uniformizer basis.
- The number of exact integral divisions by `pi` before the residue is nonzero.

Both are compared with the separate factor-valuation sum. An integer
cross-product convex-hull algorithm is then compared with the proposed
rational segment formula. No numerical root finding or floating arithmetic
is used. Each reconstructed coefficient tuple is bound by a canonical JSON
SHA-256 digest, separately for every primitive power, in `EXPECTED.json`.

The completed fixed domain is orders **3, 5, 7**, plus every repeated prime
power through **81**: **4, 8, 9, 16, 25, 27, 32, 49, 64, 81**. Every primitive
power at every listed order is checked. The OS-random assignment seed is 80;
`seed+1` sets the repeated-prime-power cutoff. The stopping rule was completion
of this domain, not finding a favorable example.

The eight rejection controls include nonprimitive powers, non-prime-power
inputs, an omitted tail factor, a polynomial with a unit root, and a
radix-4 coefficient doubled from `2+2u` to `4+4u`. The last mutation preserves
all modulo-`(1-u)` residues, the monic endpoint and the full-product endpoint,
but changes the exact coefficient valuation from 3 to 5. This demonstrates
the additional coverage of this check; it is not a defect in PR621. Tests also
execute a changed-receipt rejection under optimized Python and a source-pin
failure against an altered predecessor file.

## Pins, overlap and limitations

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR621 source head: `520774462b19b29af41554b74def31f9d01e997e`.
PR796 comparison head: `22902155c7875139e43e4fdf15723142d6709bdd`.
[SOURCE.json](SOURCE.json) retains the kernel source pin and checked
predecessor-file hashes. [CLAIM.md](CLAIM.md) records selection and scope.
[VALIDATION.md](VALIDATION.md) records the completed checks and handoff.

Concurrent [#668][668] checks resultants through radix 27 using CRT;
[#666][666] extends selected composite families using Bezout lifting;
[#692][692] checks weighted-stride resolvents; [#628][628] supplies rounded
scans and dirty restoration. Those are credited related work, not dependencies
or results imported here. The valuations, all-embedding repeated-prime-power
coverage and integer-divisibility engine are different obligations from those
packages. #796 overlaps the mathematical formula and the weighted-minimum
method. Its twelve shared radices, 160 primitive embeddings and 5,894
coefficient valuations agree exactly with this receipt; all shared hulls and
root multiplicities also agree. Radix 81 adds 54 embeddings and 4,374
coefficients. The integral-division extraction is not present in #796's pinned
`cyclotomic.py`; it independently corroborates both implementations' weighted
minimum extraction. [CORROBORATION.json](CORROBORATION.json) records the pins
and comparison scope.

Positive p-adic valuations do not say that complex roots lie inside the unit
disk. This note does not strengthen the archimedean conditioning constant,
implement a paid inverse, or settle coefficient preparation, rounded execution,
restoration, tape routing, recursive hosting or the inherited all-size/compiler/
analytic multiplication obligations. It is not proof-assistant formalization
or independent human peer review. The selected conditional kappa and
`upstream/` are unchanged.

[NOTICE.md](NOTICE.md) records attribution, Apache-2.0 licensing and substantial
AI assistance.

[621]: https://github.com/CrocSwap/integer-mult-bounds/pull/621
[628]: https://github.com/CrocSwap/integer-mult-bounds/pull/628
[666]: https://github.com/CrocSwap/integer-mult-bounds/pull/666
[668]: https://github.com/CrocSwap/integer-mult-bounds/pull/668
[692]: https://github.com/CrocSwap/integer-mult-bounds/pull/692
[796]: https://github.com/CrocSwap/integer-mult-bounds/pull/796
