# Excluded-prime pattern for general odd-kernel native DATA shears

**Research construction / recursive interface; no new kappa.** Completes open
question 2 of the pending
[triadic-query-pair](https://github.com/VictorLiwentao/integer-mult-bounds/tree/cursor/triadic-query-pair-60b9)
package (`77041f2d`), itself the kernel-3 specialization of
[PR840](https://github.com/CrocSwap/integer-mult-bounds/pull/840)
(`research/dyadic-query-pair`).

For every positive odd kernel `q`, the same three-query fusion at `a=±q·2^j`
attains the typed invoice below on every **odd modulus coprime to `q`**. Even
moduli and odd moduli sharing a prime with `q` are excluded. Typed costs do
**not** improve over the dyadic (`q=1`) case.

```text
x <- h^-a x
x ^= y
x <- h^(2a) x
x ^= y
x <- h^-a x
```

| Complete cost item | Separate pair | Fused odd-kernel pair |
|---|---:|---:|
| Ordinary recursive children | 4 | 3 |
| Ordered affine events | 24 | 18 |
| Aligned XOR scans | 4 | 2 |
| Extra full private rows | 0 | 0 |

Certificate kernels: `{1,3,5,7,9,15}` (dyadic recovery, triadic cross-check, and
primary new kernels `{5,7,9,15}`). Pattern: admitted ⇔ odd and
`gcd(modulus,q)=1`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/odd-kernel-query-pair/verify.py
python3.12 -I -O -B research/odd-kernel-query-pair/verify.py
python3.12 -I -B research/odd-kernel-query-pair/independent.py
python3.12 -I -B research/odd-kernel-query-pair/test_package.py
python3.12 -B scripts/research_package.py --package research/odd-kernel-query-pair
```

Expected:

```text
PASS_ODD_KERNEL_QUERY_PAIR kernels=[1, 3, 5, 7, 9, 15] primary_new=[5, 7, 9, 15] children=4->3 affine=24->18 xor=4->2 no_typed_gain_over_dyadic ... no_new_kappa
PASS_INDEPENDENT_ODD_KERNEL_QUERY_PAIR kernels=[1, 3, 5, 7, 9, 15] ... no_new_kappa
PASS_ODD_KERNEL_QUERY_PAIR_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/odd-kernel-query-pair outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` also passes.

## Scope and overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessor:
PR840 / `research/dyadic-query-pair`. Complementary pending: triadic kernel-3
package (OQ2 answered here; kernel-3 rows are cross-checks, not a competing
re-proof). Does not reopen leave-alone tooling through
[#2487](https://github.com/CrocSwap/integer-mult-bounds/pull/2487), pending
`mutable-source-789q-invoice`, or [#2643](https://github.com/CrocSwap/integer-mult-bounds/pull/2643)
(`seven-query-xor-floor`).

## Open next questions

1. Can an admitted BIT supplier host some small odd-kernel shear on moduli
   coprime to `q` with a favorable fully charged bill versus the dyadic path?
   First write one exact source-return boundary and charge routing, precision
   and dispatch.
2. Do coefficient-table bit-sizes for larger `q` ever pay for themselves under
   a concrete physical tariff despite identical typed child/XOR counts?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit PR840/PR521/PR677 and the pending triadic kernel-3 package.
No independent human review is claimed. No new kappa.

## Integration source binding

Historical `provenance` entries are authenticated against `SOURCES.json`'s
recorded base commit, including their Git blob and SHA256. Mathematical
`input` entries still require the current file bytes and HEAD blob to match.
The original source manifest and historical task remain unchanged. Added
positive-first package controls verify acceptance after a current provenance
edit and rejection of actual input drift, historical pin corruption and a
changed certificate. These checks do not promote the local construction to a
selected supplier or a new multiplication bound.

The lowering proof also distinguishes invertible diagonal units from arbitrary
control numerators: only the latter denominators need to invert. This clarifies
the existing admitted-modulus domain without changing it.
