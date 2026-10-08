# Near-balanced bit blocks with semantic assembly

The conditional witness is **κ = 13001411/10^12 = 1.3001411e-5** in
`T(n) = O(n (log n)^(1−κ))`. The bit saving is `52007/4000000000`.
This is approximately 6.0393% above PR28's `1.2260937e-5` witness.
The result retains the inherited analytic and fixed-tape hypotheses; exact
finite checks do not formally verify the complete multiplication theorem.

## Construction and dependencies

The selected bit dimensions are **(33,31,34)**. The same rational basis
family supports paired A1 blocks `33,1,1,31,1,34648`, an A5 width-29 block,
and every retained ordinary corner. The proof derives the two A1 blocks
by ordered Schur elimination, gives exact incidence-tree witnesses for A5,
and proves simultaneous nonvanishing in one irreducible rational family.
Concrete rational projector controls supplement the general argument.

PR24's base-four producer algorithm is unchanged. All three selected scalar
networks, coefficients, positive labels, matchings and rank histograms are
reconstructed. At h=34 the final positive matching has 3706 edges, 68 more
than the initial envelope matching; each final edge passes containment and
event-order checks. Cardinality equality between these matchings is not a
requirement of the inherited carrier argument.

PR21's complex circuit and saving `18e-6`, and PR23's semantic guard `C1=1`,
bulk exposure estimates and scalar charge remain unchanged. With beta=1/4,
the complex leaf saving is `13.5e-6`, above the new bit saving. The new bit
halving depth is 389 and wire exponent 43; complex values are 544 and 41.
The product row stock has coefficient 39031 and degree 80000, with suffix
exponent 320000. The assembly uses headroom `1e-8` and recomputes all 47
strict inequalities and seven margins. The bit gap exceeds `1e-13`; the
final absorption gap exceeds `5e-13`.

## Reproduction

```sh
make near-balanced-producer
make near-balanced-certificate
make verify
```

Python 3.11+, a C++17 compiler, Git and Make are required. The producer
rebuilds complete records in temporary storage and compares them exactly
with `certificates/near-balanced-axes.json`. The certificate generator
checks every profile and rank identity, exact logarithmic/power bounds,
the full assembly, common-basis controls and six rejecting controls.
`patches/near-balanced-bit.patch` adds the proof extension to the pinned
PR23 manuscript. It is applied independently of the previous PR27 patch.
No PDF is generated or required by these commands.

The branch extends PR27 commit `c297233e788a23e9833ad1ee07fc8517accd0f42`.
Its last commit isolates the new construction. PR23 is pinned at
`661ebabc1076c9f525d7ce4967c876b203fa9827`; PR24 at
`ed90fd940279c336ebc45968631bdebfb087b505`; the A5 argument is credited to
PR25's mathematical commit `61f81dc9c864d921adbc2ddeeeec3e672e688335`.
Historical certificates and sources remain unchanged. The exact certificate
records dependency hashes, new source hashes and rational witnesses.

## Attribution

Dominik Scholz, with substantial OpenAI GPT-6 Astra/Codex assistance,
contributes the near-balanced common basis, two A1 blocks and integration.
Credit icekylinx for PR18/24's prescribed bases, producers, endpoint gauges
and batching/tape interfaces; Rohan Arun for PR25's A5 Schur cancellation;
Zhihao Chen (jacklightChen) for PR21's translated frames and complex circuit
and PR23's semantic/bulk composition; and RaD/hipotures for the attributed
semantic precision, routing, phase-cell inverse and bulk arguments.
PR28 independently extends rectangular geometry and supplied the comparison
benchmark. Douglas Colkitt, OpenAI, eumemic and all preceding contributors
retain their notices and licenses. No global optimality or priority claim
is made.
