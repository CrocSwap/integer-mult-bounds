# Joint Horner preparation in X4 checkpoint nonzero frames

**Finite complex-supplier circuit construction; no new kappa.** Fusing two
adjacent same-target additions with different sources shares their coefficient
preparation. An exact disjoint-pair selection saves **13,072 real-component
primitives** in the complete PR799 X4 backward scalar program, selected at the
starting base.

| Quantity | Accepted PR696 lowering | Joint preparation |
| --- | ---: | ---: |
| Backward real primitives | 143,674 | 130,602 |
| Forward real primitives, retained | 143,658 | 143,658 |
| Maximum over orientations | 143,674 | 143,658 |
| Backward non-work source reads | 39,446 | 39,446 |
| Backward total arithmetic operand reads | 146,392 | 136,492 |
| Scalar prefix row-l1 maximum | 5,338,828 | 5,338,828 |
| Scalar fractional depth | 19 | 19 |

The unchanged forward orientation becomes binding in the conservative local
maximum. Keeping the full inherited adapter allowance, that local arithmetic
recount improves by only **16**, from 9,875,380,343,098 to 9,875,380,343,082.
The separate 13,072 saving is a complete *backward* circuit count. Neither is
a measured runtime benefit or a new exponent. During this sprint, main advanced
to the reviewed **PR890, kappa 0.001661957774647029**. This remains a contribution
to the historical #799 checkpoint (kappa 0.001661634653669567); transport to the
new U8 supplier is not claimed.
The forward row is a complete primitive recount under PR696; only the backward
orientation receives a new full scalar replay in this package.

## Reproduce

From the repository root, Python 3.11+ and the standard library suffice:

```sh
python3 -I -B research/x4-joint-horner-seed29/verify.py
```

Expected final line:

```text
PASS_X4_JOINT_HORNER candidates=6112 pairs=1586 saved=13072 columns=737 no_new_kappa
```

The command reads pinned committed inputs without network access, evaluates all
6,112 local matrices, recomputes the complete finite selection, replays baseline
and candidate scalar primitives, checks adverse controls, and compares every
receipt field with [EXPECTED.json](EXPECTED.json). It writes nothing normally.
`--write PATH` creates a new development receipt and refuses an existing path.

Additional checks:

```sh
python3 -I -O -B research/x4-joint-horner-seed29/independent.py
python3 -I -O -B research/x4-joint-horner-seed29/test_package.py
```

The first imports neither the compiler, Fraction, nor predecessor code. Integer
four-column matrices, an independently emitted complete primitive-stream hash,
and a forward longest-path calculation corroborate the main implementation's
Fraction replay and suffix dynamic program. Both implementations were written
by the same AI agent; no independent human review is implied.

## Construction and completed coverage

For a common denominator `a=A/2^K`, `b=B/2^K`, build the signed sum
`A*S1+B*S2` in the existing work register using shared binary doublings, halve
K times, accumulate once into the target, and clear. The initial copy handles
arbitrary dirty work. Every copy, read, doubling, halving, signed addition and
clear is charged. No helper, source mutation/restoration, physical frame change
or recursive child is introduced. [PROOF.md](PROOF.md) gives the identity,
exact cost and substitution argument.

The domain is every adjacent scalar ADD pair in the frozen backward event list
with equal **nonzero** frame, identical target and two distinct nonaliasing
sources: **6,112** pairs. Of these, **2,764** save more than deleting a single
work clear. Exact path dynamic programming selects **1,586** disjoint pairs
with total saving 6,536 per real component. Enumeration ends at the last event;
there is no timeout, sampling or uncompleted region. The optimum is certified
only for this restricted binary-Horner disjoint-pair class. No unrestricted
circuit optimum or coefficient synthesis novelty is claimed.

The main full projection checks all **737 arbitrary input columns**: 728
logical, eight center and one coefficient-work input. It verifies each group
boundary, the final shear, helper restoration and private clearing. The
independent local check covers 97,792 exact matrix entries and reproduces the
complete candidate stream hash. The nonnegative full-program envelope remains
`48299247699832632898063/16`, within the retained 192-bit magnitude allowance.
This does not imply general per-macro prefix domination or a full compiler
precision certificate.

The seed-selected pair's primitive deletion, wrong-sign, source-alias,
non-dyadic, dirty-work, event/frame-boundary and endpoint-neutral cost controls
are rejected. Four separate integer adverse circuits are rejected. Tests also
compare the DP with exhaustive small matchings and check minimal relocation,
source corruption, overlapping recipes and a suboptimal matching.

## Source pins and overlap

Exact base: **91a2094f2e022930069e8cfdc810a3ea1b81cd09**. The OS-random seed
**29** assigns the complex track and, by parity, backward orientation; it also
fixes tie handling and a mutation-control example. [CLAIM.json](CLAIM.json)
records the three considered tasks and timing. No pinned coordination issue
existed; the claim is local. [SOURCES.json](SOURCES.json) pins every consumed
input, including decompressed member payloads of the immutable integrated
replay archive. The event hashes are checked against the pinned X4 SPEC.
The #799 selection bytes are accepted at their original path or the official
`certificates/checkpoints/frontier799.json` path, with the same exact hash.
The newer active selection is not repinned or represented as an X4 witness.

Source heads: PR799 `80e6463157cfc80b85af09e7e2f14748fe2dac60`, PR741
`e516b1463606840a15f80aac1995d64ce0092e89`, PR696
`5a3f983715027c4fd83f50bc9001d4b18463bed1`.

This scope was chosen after inspecting the review ledger, accepted source and
review, open PRs, and prior negative results. The starting construction's actual
word/profile is used, not a number inferred from an open PR title. Related work:

- [#734](https://github.com/CrocSwap/integer-mult-bounds/pull/734),
  [#837](https://github.com/CrocSwap/integer-mult-bounds/pull/837) and
  [#882](https://github.com/CrocSwap/integer-mult-bounds/pull/882) optimize
  individual coefficient macros. This crosses two different-source macros.
- [#793](https://github.com/CrocSwap/integer-mult-bounds/pull/793),
  [#901](https://github.com/CrocSwap/integer-mult-bounds/pull/901) and
  [#932](https://github.com/CrocSwap/integer-mult-bounds/pull/932) change
  frame-zero compensation ordering or bases. That region is excluded here.
- [#719](https://github.com/CrocSwap/integer-mult-bounds/pull/719) excludes
  single rank-one replacements for historical CK repeated-source pairs with
  fixed middle gates. Here sources differ, gates are adjacent, and the output
  is a paid primitive circuit, so its obstruction is not reopened.
- [#839](https://github.com/CrocSwap/integer-mult-bounds/pull/839) removes known
  zero clears; every retained pair here saves strictly more than that one-clear
  comparison. [#919](https://github.com/CrocSwap/integer-mult-bounds/pull/919)
  normalizes CK signs; this does not relocate live-register signs or scales.
- [#922](https://github.com/CrocSwap/integer-mult-bounds/pull/922),
  [#924](https://github.com/CrocSwap/integer-mult-bounds/pull/924) and
  [#931](https://github.com/CrocSwap/integer-mult-bounds/pull/931) investigate
  historical factory macro topologies. Those words are not consumed here.

No pending implementation is imported and savings from different submissions
are not assumed additive. [OVERLAP.json](OVERLAP.json) retains inspected heads;
[VALIDATION.md](VALIDATION.md) records final refresh and executed checks.

## Scope and credit

Only this research directory is added. The selected frontier, production
generators and `upstream/` remain unchanged. Physical Clifford/frame/phase
operations are preserved as opaque events, not executed by these scalar
interpreters. Typed primitive integration, fresh physical admission and receipt
bindings, global owner/hosting/invoice/assembly remain separate work. The
inherited all-size/compiler, common-label/mutable-source realization,
precision/tape/recovery, bit-supplier and analytic assumptions remain.

Prepared by **Ross Richardson (@RossRichardson)** with substantial **OpenAI
Codex assistance** in selection, implementation, mathematics, tests and writing.
No delegated agent or independent human review is claimed. Apache-2.0 under
the repository [LICENSE](../../LICENSE).

Credit **Jeremy Kothe** for PR799 and the supplier lineage; **Chafik Boukhalfa**
for PR741; **icekylinx** for the scalar/factory and Horner architecture;
**Sagar Thakrar** for PR696; **DreamingOfClouds, Rohan Arun, eumemic, Dugongue**
and the contributors retained in the source notices and
[maintainer review](../../docs/research/community-frontier799-review.md).
Related coefficient-work contributions above are credited without a priority
claim for joint Horner arithmetic.
