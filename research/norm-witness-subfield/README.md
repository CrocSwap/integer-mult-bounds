# Minimal subfields for determinant norm witnesses

For `K=F_q`, `L=F_(q^d)` and `e | d`, the norm restricted to `F_(q^e)` has
image `(K^*)^(d/e)`. The least intermediate-field degree that supplies every
nonzero norm target is therefore exactly

```text
e_* = product over primes ell dividing q-1 of ell^v_ell(d).
```

Every sufficient degree is a multiple of `e_*`. A primitive norm target
requires at least that degree. From a supplied primitive generator of L,
[witness.py](witness.py) constructs each witness in this least field using
at most `q-1` target comparisons after its initial powers. It does not enumerate
the full residue field. [PROOF.md](PROOF.md) gives the all-finite-field proof,
exact image/fiber sizes and the determinant application.

Claim type: scoped algebraic proof and construction with finite exact
corroboration. No new kappa or complete multiplication theorem is claimed.

## New determinant application

apoursh's PR5668 identifies exhaustive norm-preimage search as an outstanding
arithmetic cost in its nonsplit transport interface. PR5663 supplies the
coefficient-unit determinant identity `det(m_z)=Norm(z)^N`, where N is a
power of the characteristic. Since `gcd(N,q-1)=1`, the same `e_*` is the
least coefficient-field degree that supports every determinant request.
These predecessor identities are cited premises, not audit deliverables.

The new concrete example uses `F_3[t]/(t^6+t^5+2)`. A norm-two witness is
`t^91`, canonically encoded as 599, and lies in F_9. Both nonzero base
scalars have norm one. Thus degree two suffices and degree one fails.
The verifier displays the witness's 6 by 6 multiplication matrix and checks
its determinant two. It also directly checks the 18 by 18 scalar-unit map
on `L[x]/x^3`, again with determinant two. The full field has 728 nonzero
elements; the sufficient subfield has eight. These are field sizes, not
measured scan counts or a runtime speedup.

## Evidence and boundary

The deterministic replay enumerates 12,900 cyclic power images for 2,560
order/degree pairs. The twenty supplied prime-power orders are printed in
its report; d runs from one through 128. Separately, eighteen literal field
presentations give 41 base-field domains, 74 intermediate fields, 7,764
nonzero element/norm evaluations and 2,494 constructed target witnesses.
The complete multiplicative generator cycles certify those field fixtures.
Conjugate products check norms separately from the constructor's power
formula. Seventeen invalid inputs reject, and four discriminating formula
fixtures retain the full prime powers, use q rather than the characteristic,
and distinguish proper subfields from the full field.

The report is generated from enumeration and includes hashes of package
files. No hand-written receipt is supplied. The same complete finite checks
run normally and with optimization. The universal result rests on the
written proof, rather than extrapolation from these finite domains.

The classical norm and cyclic-group facts retain their classical status;
this is a new scoped application to the repository's witness boundary, with
no global literature-priority claim. Primitive-generator discovery,
efficient embedding construction, discrete logarithms at large q, physical
map costs, native/rounded realization and supplier admission remain open.
In particular, the retained full arithmetic tables are not eliminated.
The five selected framework assumptions remain. Independent human and
formal proof-kernel review are unclaimed.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -X dev -B research/norm-witness-subfield/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -X dev -B research/norm-witness-subfield/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/norm-witness-subfield
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/norm-witness-subfield --check-source-history
```

Any clean CPython 3.12 installation can replace the shown interpreter path.
Expected verifier status is `PASS_NORM_WITNESS_SUBFIELD`. The registered
launcher runs both modes, each with a 180-second timeout. No external input
is needed by the verifier. Exact source and predecessor provenance is pinned
in [SOURCES.json](SOURCES.json), and the changed card is declared in
[TASK.json](TASK.json). Selected cold replay, Lean, Docker and an actual
native caller are unrun.

## Scope and coordination

Base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision eight, selected PR6030. The cheap selected-binding baseline passed.
The formal-interface card is explicitly changed to a written algebraic
side result, rather than a proof-assistant or supplier-admission task.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361587)
names the norm-witness seam in apoursh PR5668. This question differs from
PR6004's presentation determinant and PR6303's row-elimination implementation.

Live open and account PRs, handoffs and active Discussions, local reservations,
main README/proof/code terms and merged searches were checked. The cached
card report covers 369 open PRs and 6,288 Discussion records with complete
pagination, but only 119 of 8,917 tracked local notes. The 8,798 omitted
notes, arbitrary historical diffs and unpublished work remain coverage
limits. Main searches supplement the sparse note corpus; no search is a
novelty certificate. Expansion stops at this first proved criterion.

## Code bounds

There is no recursion or dynamic code execution. Functions have at most 60
lines. Gcd stripping has at most 33 iterations in the executable domain.
Polynomial quotients have degree at most eight and at most 4,096 elements;
power exponents have at most 64 bits. Witness lookup has at most 4,095
iterations. All failures propagate as explicit exceptions, including in
optimized Python. The caller certifies its supplied primitive generator
once before witness construction; finding that generator is outside the
constructor's contract.

Power-of-ten rule 3 has a managed-Python allocation deviation: integer and
collection allocation occurs during these bounded calculations. The bounds
above cap live data, including at most 4,095 generator-cycle entries and
degree-eight polynomial temporaries. There is no persistent cache or child
process. A future large-field backend would require a new resource contract.
Rules 8/9 have a test-only callback deviation: seventeen fixed rejection
cases use synchronous lambdas so the verifier can require exceptions. These
callbacks have no recursive or dynamically selected target. Python has no
compiler warning phase; warning-strict development-mode normal/optimized
replay and AST/function-size inspection supply local diagnostics. Ruff,
Mypy and Pyright are unavailable on PATH. No shared build configuration is
changed for this standalone package.

## Open next questions

- Supply a primitive element at an actual determinant consumer without a
  full-field traversal. First name its residue presentation and target set,
  then charge discovery or certification separately. No large-degree native
  consumer is specified here.
- Replace the retained full residue tables under a complete transport
  contract. First specify polynomial-basis arithmetic, coefficient-map
  storage and the consumer's embedding requirements. The least-field
  theorem alone does not pay those costs.

## Credit

This contribution was produced by Nick Petalas. Credit apoursh PR5663/5668
for the determinant witnesses, transport interface and explicit arithmetic
seam; Ali Romman for recognition and coefficient-field arithmetic; Nick
Petalas PR5252 for the etale norm interface; David Ganz and the retained
tensor-atlas lineage. Classical field and norm facts are credited in
[PROOF.md](PROOF.md). New work is Apache-2.0. Frozen predecessor files and
their credit lines are unchanged.
