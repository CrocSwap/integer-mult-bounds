# Equivalence of the pooled ceiling with the 1,090-call fill

The #4091 certificate in `research/staged-fourth-mixture-ceiling` is pinned to
PR #4088 head `76088d49e3ed4142a958659aa996b0ca4da5e88e`. Its unique pooled
optimum uses 1,080 fourth-entry calls. The later literal fill in
`research/staged544-mixed-fourth-entry` uses 1,090. This note checks the three
quantities the ceiling needs before that number can be read against the later
fill: the local words, the bin capacities, and the stock coefficient.

## Words

The four gzip exports

```text
THREE-base.json.gz
THREE-extra.json.gz
FOUR-base.json.gz
FOUR-extra.json.gz
```

are byte-identical in the two packages. Their gzip SHA-256 values are the
ceiling's `source_sha256` pins, and the SHA-256 values of the decompressed
JSON are the later package's `INPUTS.json` pins. Both THREE orientations have
local profile

```text
L3 = 2487 H1 + 713 H2 + 224 H3 + 102 H4 + 20 H5 + 8 H8
```

and width inventory `{5:28, 6:18, 7:56, 8:93, 9:213}`. Both FOUR orientations
have

```text
L4 = L3 + 2 H1 + 3 H3 - 3 H4
```

and width inventory `{5:28, 6:18, 7:57, 8:92, 9:213}`. Helper 601 is recorded
at entrance `[45]` in THREE and `[127, 45]` in FOUR. The local rank mass falls
by exactly one from L3 to L4.

## Capacity

`owner/TEMPLATE.json.gz` and `owner/ORDER.json` are byte-identical. The
template has 2,016 child rows, 18 on each of 112 ports, with ranks

```text
{8:672, 16:448, 32:448, 48:448}.
```

Multiplying by the 360 replicas gives the ceiling's bin counts

```text
{8:241920, 16:161280, 32:161280, 48:161280},
```

725,760 bins and total capacity 17,418,240.

## Stock

Both proofs use the comparison stock `(896*360)*73 = 23,546,880` and the paid
rank-mass identity `65088*360 = 23,431,680`. Rebuilding the recorded profiles
from the words and the recorded idle histograms gives that mass for both:

```text
2160 L3 + 1080 L4 + (22788 H3 + 1620 H5 + 138492 H48)
2150 L3 + 1090 L4 + (22783 H3 + 1625 H5 + 138492 H48).
```

The first identity is the ceiling's recorded complete profile. The second is
the later fill's recorded profile. The ten extra fourth calls lower the local
rank mass by ten, and the later idle rank mass is ten higher. The total does
not move.

## What the selector change does to the root

The ceiling's literal-minus-ideal histogram still contains one rank-16 term
and two rank-32 terms. The 1,090-call idle support is only ranks 3, 5 and 48.
The two recorded roots, as reduced comparisons of the pinned rational
endpoints, satisfy

```text
1080 literal upper < 1090 lower < 1090 upper < pooled ceiling lower.
```

The separations are

```text
1090 lower - 1080 literal upper = 810594906779329 / 10^24,
pooled ceiling lower - 1090 upper = 1140318244487201 / 10^24.
```

The shared words, capacities and stock coefficient make the pooled ceiling the
correct optimistic cap for this two-word invoice, including a 1,090-call
mixture. The 1,090 root does not exceed it. The headroom `1.951e-9` measured
from the 1,080 literal fill is a different gap: the later fill has already
moved part of the way from that literal root toward the ceiling.

No pattern of the 841-bin program is replayed here, and no claim is made that
the 1,090 idle histogram is a feasible point of that program beyond the
recorded capacity and rank-mass identities. The ordinary/outer four-provider
rebind is not run.
