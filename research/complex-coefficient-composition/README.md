# Composed coefficient circuits for the selected complex supplier

**Finite circuit composition / research note; no new κ.** This composes
[PR696](https://github.com/CrocSwap/integer-mult-bounds/pull/696)'s copy/unit
lowering, the signed-digit method independently corroborated by
[PR723](https://github.com/CrocSwap/integer-mult-bounds/pull/723), and
[PR722](https://github.com/CrocSwap/integer-mult-bounds/pull/722)'s cleanup work
sharing. The sharing rule also applies to 946 CK cleanup blocks, in addition
to PR722's 999 JP8 blocks. Complete primitive execution checks the composition.

| Provider | Orientation | Selected bill | Copy + signed, unshared | Composed bill | Total saving |
| --- | --- | ---: | ---: | ---: | ---: |
| CK | Forward | 224,938 | 169,416 | 156,426 | 68,512 |
| CK | Backward | 224,986 | 169,432 | 169,432 | 55,554 |
| JP8 | Forward | 257,232 | 197,104 | 181,610 | 75,622 |
| JP8 | Backward | 257,280 | 197,120 | 197,120 | 60,160 |

Counts include both real components, all source reads, coefficient preparation,
target accumulation and work clearing. They are scalar primitive bills, not
runtime measurements or recursive-exponent improvements. Neither backward
program has an eligible shared cleanup block.

The improvements are **not additive**. On JP8 forward, adding 56,852 (PR696),
3,276 (PR723), and 19,688 (PR722) predicts 79,816 saved primitives. Composition
saves 75,622: the sum overstates the gain by **4,194**. The corresponding CK
overstatement is **3,946**. Sharing removes some of the preparations on which
individual-macro optimizations saved work.

## Reproduce

From the repository root, Python 3.11+ and its standard library suffice:

```sh
python3 -B -I research/complex-coefficient-composition/verify.py
python3 -B -I research/complex-coefficient-composition/test_verify.py
```

Expected final verifier line:

```text
PASS_COMPLEX_COEFFICIENT_COMPOSITION programs=4 logical_columns=716 coefficients=686 savings=68512,55554,75622,60160 controls=21
```

The verifier runs offline and is read-only by default. Fresh results must equal
[EXPECTED.json](EXPECTED.json). `--write /new/path.json` writes a certificate
to a new destination and refuses to overwrite one. Checks remain active under
`-O`. Ten tests include independent columns, separate grouping/cost arithmetic,
event-boundary controls, source corruption and gzip recompression. Observed
runs and limitations are in [VALIDATION.md](VALIDATION.md).

## Construction and local proof

For `t += q*s`, write `q = sign*a/2^k` in lowest terms, with positive integer
`a`. The exact PR696 implementation is in [vendor/pr696_lower.py](vendor/pr696_lower.py).
For `|q|=1`, it accumulates directly and clears work. Otherwise it copies the
source to work, forms `a*s` by binary Horner, halves `k` times, accumulates
with the requested sign, and clears work. Copying overwrites arbitrary old work.

The signed alternative uses the classical non-adjacent binary representation.
For current positive `n`, choose `d=0` if even, otherwise `d=2-(n mod 4)`,
and replace `n` by `(n-d)/2`. Every `n>1` strictly decreases; `n=1` reaches
zero. Telescoping `n=2*n_next+d` proves `a=sum(d_i*2^i)` with digits `-1,0,1`
and leading digit 1. Copy the source, then double work and add/subtract the
source for each remaining digit. Induction on prefixes proves the prepared
value. The classical recoding and its JP8 savings are credited to concurrent
work; this contribution checks composition and additional CK sharing.

An expansion with length `ell` and `w` nonzero digits costs
`C(q)=ell+w+k+1` real primitives: copy, `ell-1` doublings, `w-1` signed source
reads, `k` halvings, one target accumulation and one clear. Choose the shorter
of binary and signed Horner, retaining binary on ties and the two-operation
unit case. Of the 686 distinct signed coefficients, 296 get a shorter word:
59 macro occurrences per CK orientation and 250 per JP8 orientation.

Partition **only full-frame cleanup** into maximal contiguous blocks of
non-unit additions with the same source and absolute coefficient. Every
intervening non-scalar event, different frame, source or magnitude ends the
block. Every addition has source distinct from target, so no target write
changes the common source. All target updates, including signs and order,
are retained. Shared registers have the full final frame, checked against
the canonical word.

For `m` additions, prepare `abs(q)*s` once, perform the `m` signed target
accumulations, then clear work. This preserves the original sequential map
on arbitrary inputs, including repeated targets. It uses one existing work
stream, no new helper or recursive child, and leaves work zero. The complex
circuit applies the real circuit separately to real and imaginary components.

**The private-work interface changes:** work is cleared at shared-block exit,
rather than after each internal macro, as in PR722. Work is never carried
across a child, adapter, phase change or frame change. Private work is erased,
not restored; logical dirty helpers are restored by the complete program.
The original event list defines the input partition, not a claim that scratch
is zero at internal macro boundaries.

The block costs `C(q)+m-1` per component. Sharing saves `(m-1)*(C(q)-1)`
relative to individually lowered additions. If one preparation optimization
saves `D=C_old-C_new`, adding its separate gain to the original sharing gain
double-counts `(m-1)*D`. Sum twice this over all blocks to obtain the exact
4,194 and 3,946 overstatements above.

The certificate records every block's event index, length, source, coefficient
and costs. The exhaustive census has 999 JP8 blocks covering 3,022 additions
and 946 CK blocks covering 2,911 additions. No search over reorderings,
source-changing blocks, new frames or optimal circuits is claimed.

## Exact billing and prefix evidence

| Program | Selected + sharing only | Copy + sharing | Copy + signed + sharing |
| --- | ---: | ---: | ---: |
| CK forward | 208,002 | 156,612 | 156,426 |
| CK backward | 224,986 | 169,634 | 169,432 |
| JP8 forward | 237,544 | 184,738 | 181,610 |
| JP8 backward | 257,280 | 200,396 | 197,120 |

The JP8 sharing-only count reproduces PR722's reported bill. Each column is
recounted from the same inputs. The final column is executed primitive by
primitive; intermediate columns are arithmetic comparators, not separately
replayed production emitters.

Signed preparation can exceed its final numerator. Endpoint equality alone
cannot justify reusing the old precision receipt. The checker propagates a
**cancellation-free positive triangle majorant through every primitive**,
treating subtraction as addition of magnitudes. It separately recovers the
selected invoice's exact old envelope and primitive counts. New rational
envelopes increase slightly but retain the same bit bounds:

| Program | Existing prefix bits | Composed prefix bits | Retained allowance |
| --- | ---: | ---: | ---: |
| CK forward / backward | 40 / 62 | 40 / 62 | 192 |
| JP8 forward / backward | 64 / 101 | 64 / 101 | 192 |

Exact rationals are in the certificate. This checks finite exact-arithmetic
sizing below `2^192`, not an all-size rounding theorem.

For every block, the rational sparse-row interpreter compares actual
primitives to the direct sequential macro map. It then checks both complete
orientations on **716 logical columns plus nine arbitrary private-input
columns**: eight centers and coefficient work. All 492 dirty helper columns
are restored; private work ends zero. Linearity makes exact basis equality
cover arbitrary finite scalar inputs. This is not a formalization of the
multiplication theorem.

An independent flat scalar-column interpreter checks all 686 coefficient
maps and all 1,945 shared blocks. A separate scan reconstructs grouping and
nonadditive bills. Twenty-one built-in controls reject wrong signs, missing
initialization/reads/halvings/clears, aliases, invalid coefficients, inflated
cost, endpoint-neutral prefix growth, and sharing across incompatible frames,
sources, magnitudes or children.

## Binding, provenance and scope

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The initially downloaded
archive's complete local Git tree matches upstream tree
`a7c79baff74f9a53d920d7b5c62f290b1df75dc1`. Before publication, the actual
upstream commit was fetched and this contribution was rebased onto it after
checking that the two base trees were identical.
[SOURCE-PINS.json](SOURCE-PINS.json) records exact files and complete gzip
payloads. The selected source manifest binds the SPEC, which binds the
canonical words and event streams. Paid children are recounted against SPEC.
Frame labels and non-scalar events retain their input positions relative to
the original logical updates.

Predecessor pins:

- Selected PR626: `660de893d27bb7abd1d5b01b1640207528a5c851`, on reviewed PR622
  `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6` and the retained PR543 supplier.
- PR696: `5a3f983715027c4fd83f50bc9001d4b18463bed1`; verbatim lowering checked
  against Git blob `a2c2889e5be41a0fc30d4dfa5dfcebb03d6d47f8`.
- PR722: `a0766ab0fab379e1997fadc3ca157578d57986c1`; grouping/preparation source
  inspected, grouping rule adapted here and extended to CK.
- PR723: `d3bc41b87fc7d23f50d064a0f06f1a89e3ab02a7`; matching JP8 signed-digit
  result credited. Its code is not an execution dependency.
- PR734: `ba76ba3321d000c8996b0b254bcf0d7260e1bbb6`; stricter per-macro
  numerator cap is distinct and is not imported or composed here.

The final overlap refresh reached PR779. Related PR739 changes coefficient
magnitudes within a run, PR751 batches a common target backward, and PR755
extends reuse across other JP8 phases (inspected head
`a1dd9f819102c40e0b5e4a75215cf69ee864f480`). These are credited related
extensions. This package adds the explicitly priced signed/copy/sharing
composition, CK coverage and nonadditivity certificate for the stated cleanup
class. It does not claim their broader coverage or add their savings.

[PR769](https://github.com/CrocSwap/integer-mult-bounds/pull/769), by
@24kHandsome1201 (inspected head
`e891b2b19e3185ec91bcf001e255af87f42389ce`), also contributes CK coverage,
using varying-magnitude dyadic ladders in forward cleanup and backward
preconditioning under the original binary-Horner initialization. Its CK
coverage and equal-magnitude comparator are credited. The present package
checks the combined copy/signed/equal-magnitude bill in cleanup; it makes no
priority claim for CK reuse and does not combine PR769's counts.

OS seed **24** selected the complex track and candidate zero of three
(`24 mod 3`). [CLAIM.json](CLAIM.json) records the candidates and one pivot
after concurrent signed-digit results appeared. No pinned sprint issue
existed, so the claim is local. The stopping rule was full coverage of all
four programs and maximal eligible blocks, not a timeout or sampled search.

Production emitter integration, global invoice/admission, fresh phase/wrapper
lowering and supplier regeneration remain separate. Geometric and physical
facts are inherited from pinned inputs, not claimed freshly replayed. Selected
κ stays `51110230636731/31250000000000000`. All-size/compiler, common-label/
mutable-source realization, whole-call hosting, precision, fixed tape/exact
recovery, analytic transfer and bit assumptions remain. No optimality,
practical speedup or new multiplication bound is claimed.

## Attribution

Prepared for **Gareth Davidson (@bitplane)** with substantial **OpenAI Codex
assistance** in research, code, verification and writing. No independent human
review, delegated-agent review or proof-assistant formalization is claimed.
New material is Apache-2.0 under the repository [LICENSE](../../LICENSE).

Credit to Sagar Thakrar/OpenAI Codex (PR696/723), @ellipsi2/OpenAI Codex (PR722),
Chris Pagolu/OpenAI Codex (PR734), eumemic (PR411 dyadic microcircuits and
PR543), icekylinx (PR425/433/531 vocabulary, emitter and factory), Jeremy
Kothe/AtomScout and their Claude Code lineage (PR622/JP8), DreamingOfClouds
(cold-helper/native checks), Chafik Boukhalfa (PR626), Dugongue and all other
predecessors retained in the [supplier notice](../complex-k492-owner-repair/NOTICE.md).
The vendored PR696 source retains its original attribution verbatim.
