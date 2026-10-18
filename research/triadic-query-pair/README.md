# Fuse a completed native BIT shear pair at odd kernel 3

**Research construction / recursive interface; no new kappa.** Complements
[PR840](https://github.com/CrocSwap/integer-mult-bounds/pull/840)
(`research/dyadic-query-pair`), which fuses two completed DATA shears for
dyadic powers `a=±2^j` with an all-odd-radix lowering and explicitly leaves
non-dyadic powers to introduce prime exclusions. This package fixes the odd
kernel to **3**, takes `a=±3·2^j`, and prices the same three-query fusion with
every excluded modulus named.

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

Each query lowers to six ordered affine events and one ordinary ADDRESS
interchange child. Diagonal units involve the factor 3, so the lowering
specializes to every **odd modulus not divisible by 3**. Multiples of 3 and
even rings are rejected by the verifier. These are explicit interface counts,
not measured runtime or a selected-supplier optimization.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/triadic-query-pair/verify.py
python3.12 -I -O -B research/triadic-query-pair/verify.py
python3.12 -I -B research/triadic-query-pair/independent.py
python3.12 -I -B research/triadic-query-pair/test_package.py
python3.12 -B scripts/research_package.py --package research/triadic-query-pair
```

Expected:

```text
PASS_TRIADIC_QUERY_PAIR children 4->3; affine 24->18; XOR 4->2; kernel=3 ... no_new_kappa
PASS_INDEPENDENT_TRIADIC_QUERY_PAIR children=4->3 xor=4->2 kernel=3 ...
PASS_TRIADIC_QUERY_PAIR_PACKAGE_TESTS ...
PASS_REGISTERED_RESEARCH_PACKAGE research/triadic-query-pair outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` also passes.

## Scope and overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessor:
PR840 / `research/dyadic-query-pair` (Wentao Li), which retains PR521/PR677
credit. This package does not reopen leave-alone tooling through
[#2487](https://github.com/CrocSwap/integer-mult-bounds/pull/2487), the pending
`mutable-source-789q-invoice` work, or ledger Deferred objects.

Closest prior: PR840 proves the dyadic all-odd-radix case and the three-query
minimum for any integer power alphabet; it does not supply a priced non-dyadic
lowering. `research/dyadic-query-runs` batches several dyadic pairs and does not
admit kernel 3. No competing open PR on this freestanding package was found in
the refreshed overlap scan.

## Open next questions

1. Does a structured encoder make the odd-kernel shear usable inside an
   admitted BIT supplier on moduli coprime to 3? First write one exact
   source-return boundary and charge routing, precision and dispatch.
2. What is the excluded-prime pattern for a general odd kernel `q`, and does
   any small `q` improve a concrete paid profile after those exclusions?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit PR840/PR521/PR677 and the retained OpenAI tape framework.
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
