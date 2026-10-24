# The #4091 pooled ceiling still bounds the 1,090-call fill

**Audit of a fixed two-word invoice. No new κ.** The selected record remains
`60403/20000000 = 0.00302015`.

The pooled ceiling in
[research/staged-fourth-mixture-ceiling](../staged-fourth-mixture-ceiling/README.md)
is pinned to PR #4088 head `76088d49e3ed4142a958659aa996b0ca4da5e88e` and its
unique optimum uses 1,080 fourth-entry calls. The later literal fill in
[research/staged544-mixed-fourth-entry](../staged544-mixed-fourth-entry/README.md)
uses 1,090 of the same 3,240 calls. This package checks the three quantities
that ceiling needs before it can be read against the later fill: the local
words, the bin capacities, and the stock coefficient.

## Result

The four gzip word exports are byte-identical. Their gzip SHA-256 values are
the ceiling `source_sha256` pins. The SHA-256 values of the decompressed JSON
are the later package's `INPUTS.json` pins. Both THREE orientations have

```text
L3 = 2487 H1 + 713 H2 + 224 H3 + 102 H4 + 20 H5 + 8 H8
```

and widths `{5:28, 6:18, 7:56, 8:93, 9:213}`. Both FOUR orientations have
`L4 = L3 + 2 H1 + 3 H3 - 3 H4` and widths `{5:28, 6:18, 7:57, 8:92, 9:213}`.
Helper 601 is recorded at entrance `[45]` in THREE and `[127, 45]` in FOUR.
Local rank mass falls by exactly one.

`owner/TEMPLATE.json.gz` and `owner/ORDER.json` are byte-identical. The
template has 2,016 child rows, 18 on each of 112 ports, with ranks
`{8:672, 16:448, 32:448, 48:448}`. Times 360 replicas this is the ceiling bin
count `{8:241920, 16:161280, 32:161280, 48:161280}`: 725,760 bins and total
capacity 17,418,240.

Both proofs use the comparison stock `(896*360)*73 = 23,546,880` and the paid
mass `65088*360 = 23,431,680`. Rebuilding the recorded profiles from the words
and the recorded idle histograms gives that mass for both:

```text
2160 L3 + 1080 L4 + (22788 H3 + 1620 H5 + 138492 H48)
2150 L3 + 1090 L4 + (22783 H3 + 1625 H5 + 138492 H48)
```

The ten extra fourth calls lower the local rank mass by ten, and the later
idle rank mass is ten higher. The total stays put.

The recorded roots satisfy

```text
1080 literal upper < 1090 lower < 1090 upper < pooled ceiling lower.
```

The separations are exact:

```text
1090 lower − 1080 literal upper = 810594906779329 / 10^24
pooled ceiling lower − 1090 upper = 1140318244487201 / 10^24
```

The shared words, capacities and stock coefficient make the pooled ceiling the
optimistic cap for this two-word invoice at 1,090 calls as well. The later
root stays under it. The headroom `1.951e-9` measured from the 1,080 literal
fill is a different gap: the later fill has already moved part of the way from
that literal root toward the ceiling. The ceiling's literal-minus-ideal
histogram still contains one rank-16 term and two rank-32 terms. The 1,090-call
idle support is ranks 3, 5 and 48.

The argument is in [PROOF.md](PROOF.md). The checker reads the pinned bytes
and rebuilds both mixtures. It does not import either predecessor verifier.

## Scope

Task card `independent-moment`, priority revision 7, base
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`. Scope status is **refined**: the
card's first step asks for this equivalence before the #4091 ceiling is applied
to the later fill.

This comparison stops at the three identities and the two root separations.
It does not replay the 841-pattern linear program, so it does not show that
the 1,090 idle histogram is a feasible point of that program beyond the
recorded capacity and rank-mass identities. The ordinary/outer four-provider
rebind is left to
[research/staged544-mixed-idle-rebind](../staged544-mixed-idle-rebind/README.md).

## Reproduce

From the repository root, Python 3.12 standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/staged-fourth-ceiling-equivalence --check-only
python3.12 -B scripts/research_package.py --package research/staged-fourth-ceiling-equivalence
```

The direct checker is `python3.12 -B research/staged-fourth-ceiling-equivalence/verify.py`.
It prints `PASS_STAGED_FOURTH_CEILING_EQUIVALENCE`. Live inputs are the sixteen
predecessor files listed in [VERIFY.json](VERIFY.json). Pins are in
[SOURCES.json](SOURCES.json).

## Open next questions

1. Does the 1,090-call idle `{3:22783, 5:1625, 48:138492}` correspond to a
   feasible pattern vector of the 841-pattern program? Express the idle delta
   from the certified eight-pattern witness as a combination of tight patterns.
   Pattern enumeration is not replayed here.
2. Can the pinned ordinary rebind take four provider ids, recompute this idle,
   and still pass the outer release? That is open question 1 of
   `research/staged544-mixed-idle-rebind`. Equivalence does not run it.

Structured fields are in [TASK.json](TASK.json).

## Credit

Credit Cinna Davis and PR #4088 for the later fill, and Ross Richardson and
PR #4091 for the pooled ceiling. Prepared by unpaidmoon with substantial Cursor
Grok assistance. New work is Apache-2.0.
