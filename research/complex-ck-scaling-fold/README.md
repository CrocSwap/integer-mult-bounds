# One CK cleanup scale relocation saves 62 primitives per orientation

Status: finite complex-supplier circuit improvement and scoped exhaustive search.
No new kappa is claimed.

In the selected #626 CK cleanup, move the doubling of register 97 from
zero-based operation 4832 to operation 4869. Double the coefficients of the
37 intervening additions, which all read register 97. This saves 62
real-component primitives in each orientation under the retained binary-Horner
lowering. The complete interval map, including arbitrary incoming values, is
unchanged. Both complete-program prefix envelopes remain unchanged.

| Complete CK scalar program | Original | Replacement | Saving |
| --- | ---: | ---: | ---: |
| Forward real-component primitives | 224,938 | 224,876 | 62 |
| Inverse-transpose real-component primitives | 224,986 | 224,924 | 62 |
| Scalar macros, either orientation | 21,936 | 21,936 | 0 |
| Events, either orientation | 27,256 | 27,256 | 0 |

The saving is small. It establishes a checked improvement to a specific
cleanup circuit and an exact limit for all single-scale relocations of that
fixed word. It is not a practical runtime benchmark or an exponent improvement.

## Reproduce

From the repository root, using Python 3.9+ and only the standard library:

```sh
python3 -B research/complex-ck-scaling-fold/verify.py
```

Expected:

```text
PASS_CK_SINGLE_SCALE_RELOCATION candidates=1022007 saving=62/62 columns=38/38 controls=6
```

The independently implemented check is:

```sh
python3 -B research/complex-ck-scaling-fold/independent.py
```

It reports 1,022,007 positions, minimum complex-component delta -31,
644 minimizing placements, 38 columns in each orientation and eight rejected
controls. Both scripts are offline and read-only. `verify.py --emit-certificate`
prints the complete deterministic certificate to stdout; the default command
compares the recomputed result with `CERTIFICATE.json`.

## Exact circuit argument

Let S multiply register r by nonzero q. While delaying S to the right, replace
each crossed addition `t += a*s` by `t += a*q*s` if s=r, or by
`t += (a/q)*s` if t=r. Other additions and all diagonal scales commute with S.
For motion to the left, use the reciprocal adjustments. The invariant is
`original_state = D * replacement_state`, with D equal to q on register r
and one elsewhere. Executing S at the chosen boundary makes D the identity.
This proves equality for every input, including dirty helper coordinates.

Here q=2, r=97, and all 37 crossed additions use r only as a source.
Thirty-four adjusted coefficients cost one fewer complex primitive. Three
original integral coefficients cost one more. The net change is
`-34 + 3 = -31`, doubled to -62 for real and imaginary components. The
doubling itself is still paid once. There is no omitted restoration operation.

The same-order gatewise inverse transpose respects equality of the complete
product. Its additions swap source and target and negate the coefficient;
its scale is 1/2. The programs are not reversed. The two checkers explicitly
compare the 38-by-38 rational boundary maps in both orientations. All other
678 register columns are unaffected because the changed interval never reads
or writes those registers. The surrounding selected program is byte-for-byte
preserved as parsed events outside the cleanup replacement.

## Complete local accounting and interface

Each addition keeps the existing cleared-private-work binary Horner recipe.
The bill includes the initial clear, every source read, doubling, halving,
signed target accumulation and final clear. Relocation does not introduce
scratch, copies, recursive calls or frame changes. Private work is still
cleared after each macro. All 38 involved registers have final frame 1, the
full frame; settlement occurs before any post residual wrapper.

The selected 492 helpers, eight private centres, 3,698 paid children, 238 pre
and 238 post residual wrappers, 426,400 local adapters and compiler charge
25,934,336 are retained. The paid histogram remains
`{1:2596, 2:552, 3:304, 4:160, 5:70, 6:8, 8:8}`. No changes to a bank, owner,
source-access interface, tail operation or early-ended helper are used.

`recount` traverses both complete event streams and expands Horner billing by
digits. This is checked against the separate closed-form cost used by the
search. It also propagates positive rational envelopes through scalar registers
and private coefficient work. Forward remains `920709848294`, charged at
40 bits; inverse transpose remains `146068000389976309073/32`, charged at
62 bits. Both fit the inherited 192-bit local allowance. The inverse-transpose
intermediate value on register 97 can be larger before settlement, so these
full recounts are necessary even though the boundary maps agree.

This package reconstructs the revised local programs and binds their exact
hashes. It does not install them into the selected emitter or regenerate the
global invoice, owner certificate, assembly inequalities or selected frontier.
Such integration remains a separate obligation. Inherited all-size compilation,
common-label and mutable-basis realization, pooled whole-call hosting,
normalized residuals, precision/tape/exact recovery and analytic transfer
assumptions remain. Finite exact replay is not a formal proof of the full
multiplication theorem.

## Search domain, stopping rule and negative evidence

OS seed 34 assigned the complex-supplier track and selected CK from CK/JP8
by parity. The first hypothesis moved every cleanup scale to the end; its
complex-component bill increased from 42,309 to 45,275. Moving all scales to
the beginning also lost, giving 42,497. The single evidence-driven pivot was
to relocate one scale while leaving every other operation in relative order.

The completed domain contains all 123 original scales and all 8,309 insertion
positions after removing the selected scale, including its original position.
The scan stops after all 1,022,007 placements. It has no sampling, timeout,
floating arithmetic or external solver. For each placement the search prices
every changed coefficient; the scale's cost is unchanged. The certificate
contains every scale's best placement and a digest of the complete ordered
score stream. Ties choose the shortest displacement, then the lower source
and destination indices. This selects 4832 to 4869.

The independent implementation instead uses the valuation identity
`cost(a) = 2 + bit_length(abs(odd)) + popcount(abs(odd)) + abs(e)` for
`a = odd * 2**e`. It finds exactly 644 optimal placements: 4832 to 4869 and
8061 to any position from 5391 through 6033 inclusive. Its matrix check uses
integer linear forms with denominator 16 and checks divisibility at every
step. It imports neither the first checker nor the native emitter.

The -31 bound applies only to a single original scale relocated in this fixed
word, with forced conjugation coefficients and the original Horner price.
It does not bound multiple relocations, new scales, different scalar
factorizations, different lowerings or supplier constructions. Per-scale
improvements are not asserted additive. Omitted settlement, an unadjusted
coefficient, wrong settlement factors and sign errors are rejected by the
exact boundary controls.

## Pins, overlap and credit

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The accepted conditional value at that base is
`51110230636731/31250000000000000`, from selected #626, not an open-PR title.
The source chain is:

- #626, Chafik Boukhalfa: `660de893d27bb7abd1d5b01b1640207528a5c851`.
- #622, Jeremy Kothe: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
- Retained #543 bit supplier, eumemic: `2065fe4f72a914d907f1046603f5a36f17018535`.

`CERTIFICATE.json` pins the consumed native word, event stream, emitter,
supplier specification, selected record and maintainer review. Gzip pins hash
the entire decompressed payload, so container recompression does not invalidate
the mathematical source binding. Other source pins hash file bytes.

The review ledger, current status and selected construction review were read
before selection. No pinned coordination issue existed; `CLAIM.md` records the
scope. The initial open queue contained 542 PRs through #723. A later refresh
contained 551 through #732. The pre-submission scan covered 566 through #747.
No cleanup diagonal-scale relocation was found.
#414's body match concerns relocated target prefixes in an older entrance
construction, not this scale relocation.

Related pending work is credited as context, with no code imported:
#696 `5a3f983715027c4fd83f50bc9001d4b18463bed1` lowers individual macros;
#722 `a0766ab0fab379e1997fadc3ca157578d57986c1` shares JP8 coefficient work;
#723 `d3bc41b87fc7d23f50d064a0f06f1a89e3ab02a7` uses signed digits in JP8;
#719 `a3d9c0aa0a16b68b1f4dd064671ad018013e6dd4` obstructs rank-one fusion
of repeated CK addition pairs. #698 studies fixed-boundary CK B frames.
The final refresh also found #734
`ba76ba3321d000c8996b0b254bcf0d7260e1bbb6`, which bounds signed-Horner
prefixes, and #739 `abb9825202dba6f9bc95c7df8d12d86088fdff1a`, which rescales
shared JP8 private coefficient work. Neither relocates a live CK register scale.
The present result changes the scalar coefficients and scale order of a
full-frame cleanup interval. Savings are relative to the selected base and
are not asserted additive to those pending changes without a composed recount.

The retained construction and accounting descend from icekylinx's direct
delivery and emitter work, Jeremy Kothe's CK/K-triangle lineage,
DreamingOfClouds' cold-helper and native checks, and the contributors credited
by the selected review. Their notices and code are unchanged.

Prepared for @thakrarsagar with substantial OpenAI Codex assistance, including
one separately implemented AI verification worker. This is implementation
independence, not independent human review. New files are Apache-2.0.
