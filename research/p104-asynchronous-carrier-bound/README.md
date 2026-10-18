# A uniform bound for asynchronous P104 delivery

**Status: scoped negative result. No new supplier or kappa.**

This package extends PR1071's delivery obstruction to all 7168 mixed
frame-pair decoders from PR968. It permits different target orders,
extra frame directions, and paid downward moves. The carrier interface
is stated in [PROOF.md](PROOF.md). Each carrier path holds one decoder
term. Free resets and arbitrary linear combinations are outside it.

All members have the same target-support family on a cube. Its inclusion
poset has width **32**. Removing any one term leaves width **26**. Exact
antichains and matching chain covers are in [CERTIFICATE.json](CERTIFICATE.json).
A separate checker repeats the full decoder census by a different method.

Let `P` count continuous delivery paths, including the eight seeds. Let
`L` be the excess recursive rank from delivery and target frame moves.
Then:

| Delivery case | Necessary condition |
|---|---|
| No survivor is erased | `L >= 2 max(0,32-P)` |
| One term's survivor is erased | `L >= 1+2 max(0,27-P)` |
| At least two terms' survivors are erased | `L >= 2` |

Thus at most 26 paths always require at least two excess ranks. With
no erased survivor, at most 31 paths require at least two. These are
path counts, not peak memory counts. Chain covers do not prove that a
full schedule exists at the stated thresholds.

The PR942/T37 and refreshed PR1042/T16 price checks are exact. On the
corresponding favorable P104 knob profiles,
two extra ranks per call fail the selected `b`, even when each extra rank
has the lower price of one. All other delivery work is free in this
screen. This comparison requires the rest of the PR968 profile to be
retained, or bounded below by it. A new word that changes other charges
needs a new invoice. The geometric bound does not establish that cost
premise for an arbitrary new supplier.

## Reproduce

Use Python 3.10 or later and the standard library, from the repository
root:

```sh
python3 -I -B research/p104-asynchronous-carrier-bound/verify.py
python3 -I -B research/p104-asynchronous-carrier-bound/independent.py
```

Expected final lines:

```text
PASS_P104_ASYNCHRONOUS_BOUND decoders=7168 cube_families=1 widths=32,26 controls=7 two_rank_budget=FAIL_T37_T16
PASS_P104_INDEPENDENT partition_census=7168 graph_isomorphisms=16 antichains=9 chain_covers=9
```

`two_rank_budget=FAIL_T37_T16` is the checked negative result, not a verifier
failure. Both commands exit with status zero. `verify.py --write`
regenerates this package's certificate only. `--repo` selects the pinned
source checkout for a relocated package.

The domain is all 1260 frames disjoint from the coordinate frame and all
mixed dual root bases on each union. There is no random seed. The search
ends only after complete enumeration. The reflection orbit extends the
result to all 2025 choices of the first frame. This is a finite certificate
and a written scheduling argument, not a formal multiplication proof.

The exact base is `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`.
[Source pins](SOURCES.json), [credit](NOTICE.md), and
[validation and failed attempts](VALIDATION.md) give the remaining details.
