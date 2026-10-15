# Same-slot helper470 retirement raises the complete frozen bit bill

**Status: scoped negative result. No construction or new exponent is claimed.**

This note completes one missing cost calculation around the finite helper470
exception in PR #1256. It asks whether shrinking its existing width-eight slot
to width seven, then returning the freed rank to that slot's idle remainder,
improves the complete paid bit profile. The answer is no for every feasible
old remainder in the frozen width-64 interface. For the three idle classes in
the pinned selected profile, exact interval replay shows that the complete
moment bill increases, including the inherited residue surcharge.

The question is distinct from the two-slot displacement priced in PR #1256.
That relaxation spends eight coordinates in a second slot and can lower the
raw moment at remainders 2, 4, and 6. It is also distinct from PR #1302's
native replay and full-frame closure audit, and from PR #1043's earlier
source-boundary deletion with a hosted invoice. This result only prices the
same-slot profile change.

## Frozen inputs and complete profile

The exact base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The four live
inputs and their Git blob and SHA256 pins are in [SOURCES.json](SOURCES.json).
The verifier checks those SHA256 values, the compressed word receipt and its
uncompressed content receipt. The selected nine-stage bit endpoint is
`a = 1733427039589844234749/10^24`; it comes from the pinned `EXPECTED.json`.

The pinned local paid histogram is
`p = {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`. The frozen hosting
remainder, parsed from the pinned `fastc.py`, is
`R = {2:13920, 4:14208, 6:14208, 7:21312, 42:288}`. Thus the complete
nine-stage profile is `H = 288 p + R`, with 904896 calls, rank mass 1808352,
and deficit 10272 from `64*28416`. The moment engine prices

```text
M(H,a) = sum_r H[r] * r * (64/r)^a / (64*28416)
       + 32*64*sum_r(H[r])/(10^16*28416) * 64^a.
```

The second term is the inherited residue envelope in the pinned source. The
calculation takes its existing coefficient as given and charges its change
when the call count changes.

## Same-slot delta and proof

Shrinking the width-eight helper to seven changes its paid local profile by
`e1 + e5 - e7`. Returning one unit of unused width to an old idle remainder
`r > 0` changes that term by `e_(r+1) - e_r`. Hence

```text
Delta_r = e1 + e5 - e7 + e_(r+1) - e_r,   1 <= r <= 56.
Delta_0 = 2 e1 + e5 - e7.
```

For every `0 < a < 1`, define `g_a(t)=t*(64/t)^a=64^a*t^(1-a)` for `t>0`
and `g_a(0)=0`. Dividing the raw moment change by `64^a` gives

```text
Q_r = 1 + 5^(1-a) - 7^(1-a) + (r+1)^(1-a) - r^(1-a)
    = (1-a) * [integral_0^1 t^(-a) dt - integral_5^7 t^(-a) dt
               + integral_r^(r+1) t^(-a) dt].
```

The factor `1-a` is essential: the derivative of `t^(1-a)` is
`(1-a)*t^(-a)`. The integrals converge even at `r=0` because `a<1`.
On `0 <= r <= 56`, the last integral is at least `57^(-a)` and the middle
integral is at most `2*5^(-a)`. Multiplying the integral bound by the
positive factor gives

```text
Q_r >= (1-a)*[1/(1-a) + 57^(-a) - 2*5^(-a)]
    = 1 + (1-a)*(57^(-a) - 2*5^(-a))
    >= 1 - (1-a)*(57/25)^a > 0.
```

For the penultimate inequality, AM-GM gives
`2*5^(-a) <= 57^(-a) + (57/25)^a`. For the final strict inequality,
`-ln(1-a)>a` and `ln(57/25)<1` (because `57/25 < 8/3 < e`),
so `(1-a)*(57/25)^a < 1`. Thus the raw moment strictly
increases throughout the stated domain. For `r>0`, the complete profile adds
one call; for `r=0`, it adds two. The inherited surcharge consequently also
increases. The complete bill is strictly worse for every `0<a<1` and every
feasible old remainder `r` in the fixed width-64 slot.

## Exact replay and controls

`verify.py` independently computes outward rational intervals using exact
`Fraction` arithmetic: 24-term atanh log bounds, 32-term Taylor exponential
bounds with explicit tails, then signed interval propagation. It checks all
57 old remainders and separately rebuilds and prices the complete mutated
profiles at the pinned exponent for the actual classes 2, 4, and 6. The direct
delta formula and subtraction of the two complete profile prices enclose the
same result.

For remainders 2, 4, and 6, the complete moment increases by the following
outward intervals; divide each integer endpoint by `10^30`:

| old remainder | lower endpoint | upper endpoint |
|---:|---:|---:|
| 2 | `3509181979935340631634` | `3509181979935340636370` |
| 4 | `2942545622277557042992` | `2942545622277557047728` |
| 6 | `2590121108088020625486` | `2590121108088020630221` |

The negative control omits the returned idle rank: its raw delta
`1 + 5^(1-a) - 7^(1-a)` is negative, so that incomplete shortcut appears
favorable. Exact call and rank-mass checks catch the omission. As a distinct
positive control, the verifier replays PR #1256's two-slot relaxation
`e1+e5-2e7+e_(r+8)-e_r`; its raw moment delta remains negative at all three
actual remainder classes. This confirms that the same-slot result does not
erase the separately priced relocation mechanism.

Reproduce from the repository root with Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/bit-inplace-retirement-seed11
```

Expected: `PASS_REGISTERED_RESEARCH_PACKAGE research/bit-inplace-retirement-seed11 outcome=negative-result`.
The result certificate is [RESULT.json](RESULT.json). The registered check is
a finite exact replay of this profile claim, not a proof of supplier
admission, a new bit endpoint, or an asymptotic theorem.

## Scope and remaining obligations

The conclusion applies to the explicitly stated same-slot histogram change,
the frozen `64,28416` profile, the pinned exponent, and the inherited moment
formula. It does not rule out a different owner/window relocation, topology,
helper interface, source boundary, or a change that removes other charges.
Physical owner placement, H4 cleanup admission, native recursive replay,
precision/tape obligations, and outer assembly remain outside this profile
audit. PR #1256's finite circuit remains a finite construction; this note does
not extend its interface contract.

## Open next questions

The next useful task is to price one concrete H4-admissible owner/window
itinerary for helper470. It matters because a different placement or interface
could change the complete profile even though the same-slot return is worse.
The first step is to derive its full hosted histogram before implementing a
compiler. Physical owner/window admission and the changed H4 cleanup contract
remain open in PR #1256.

## Credit

Ali Romman's PR #1043 is credited for the earlier source-boundary helper470
deletion and hosted invoice. The finite restoration exception, its two-slot
relaxation, and the exact head `d6d5a994fcdcd8d04ec439ff988daa8f37b17ece`
are from PR #1256. PR #1302 (head
`0cc5db33b0999a7d3333383a855667f6f8cbda88`) supplies the native replay and
full-frame closure audit; this note does not repeat those checks. The tuned
bit word and its pipeline lineage are credited to PR #555 and its cited
predecessors in the pinned source README. PR #1048 (head
`07730cd8302c378607259a9ad0efb73e0b57a2f2`) proposed a general fixed-exponent
profile-ordering claim, which the selected review rejects with an exact
counterexample. This audit does not use that claim: it directly compares the
same frozen moment at one pinned exponent using rational intervals, including
the inherited call surcharge. The selected review is pinned as provenance in
SOURCES.json. Prepared by Cinna Davis
(@1337isnot1337) with substantial OpenAI Codex assistance in source review,
derivation, exact interval code, replay, and writing. New work is Apache-2.0.
