# QQ16 L2 recovery with exactly 24 retained arrays

**Scoped information lemma; no supplier or new kappa.** Given the fixed live
post-B1 observations `X2_U, Y2_U, Y2_A`, exactly **24** rational-linear retained
complete arrays are necessary and sufficient to recover all 224 arbitrary
pair-0 input arrays. Retain `x1_A, x1_T, y1_T` after F0. The eight `y1_A` arrays
in PR2470's 32-array L2 lead are reconstructible from its already granted future
logger output. This removes eight retained arrays in that information contract;
it does not establish a physical storage, recursive-work or native-cost saving.

A separate specialist derived the inverse and kernel and wrote an independent
noncommuting-matrix check; see [REVIEW.md](REVIEW.md).

## Exact contract and predecessor delta

Let `(x1,y1)=F0(x,y)` and `(x2,y2)=B_1_2(x1,y1)`, with **no intervening event**.
Use the pinned disjoint sets

```
A = [0,7,20,27,36,46,57,111]
T = [21,37,47,76,81,87,92,110]
U = {0,...,111} minus (A union T), |U|=96.
```

All arrays lie in the same space `W=Q^n`, for any finite `n>=1`. Owner, payload,
tensor and spectator coordinates belong to the complete array. Every initial
X/Y array is arbitrary. Each retained record is a fixed rational-linear map to
one copy of W and may mix coordinates or ports. No nonlinear encoding, enlarged
array, extra read or adaptive nonlinear observation is granted. The lower bound
even permits a nonlinear decoder of these linear records. Other bank pairs are
arbitrary but neither read nor decoded; they do not participate in these events.

| Observation | Cut | Complete arrays |
|---|---|---:|
| `r=x1_A`, `t=x1_T`, `h=y1_T` | retained after F0 | 24 |
| `C=x2_U`, `V=y2_U`, `Z=y2_A` | live immediately after B1 | 200 |
| Total independent records | two cuts | 224 |

PR2470's L2 lead grants the same 200 live arrays and retains 32 F0 arrays.
We remove its `y1_A` block. PR2443 instead grants 88 ordinary F0 reads and
104 B1 arrays; its contract expressly excludes `y2_U`. Our 96 `y2_U` arrays
change that contract, so its 88-read threshold and any native-cost comparison
do not transfer. Without Z, only 192 live arrays remain and the same dimension
argument would require at least 32 retained arrays.

Exact consulted file hashes and heads are in [PREDECESSORS.json](PREDECESSORS.json):

- [PR2470](https://github.com/CrocSwap/integer-mult-bounds/pull/2470),
  `1b2eee3bf1ec67e68c0b0fa7f47c7b2a66febe56`: Sagar Thakrar's retention census,
  L2 reconstruction and 32-array sufficient record; these results retain credit.
- [PR2443](https://github.com/CrocSwap/integer-mult-bounds/pull/2443),
  `545c05e17243c962b112b91e7f84b4c1a41de7b8`: starship-s's ordered cut decoder
  and arbitrary-input F0 inverse.
- [PR2456](https://github.com/CrocSwap/integer-mult-bounds/pull/2456),
  `665ba8d7bffab92a434413096e9d5c0df7db40bd`: ywz65's operator audit and
  chart-fault warning. Its affine-operator implementation is not imported.
- Ali Romman's [PR1969 conserved contract](../joint-query/evidence/CONSERVED-QQ16.md)
  supplies the inherited F/B maps, retained unchanged on the pinned base.

## Ordered sufficiency proof

Let `B_(s,U)=R_U D_(s,U)`, `ell_(s,V)=R_V D_(s,V)` for V=A,T,
`P_(s,V)=D_(s,V)^(-1) R_V^(-1)`, and `K_(s,U)=D_(s,U)^(-1)R_U^T/4`.
The selected Grams are `R_A R_A^T=R_T R_T^T=4I`. Each D is an invertible
port-diagonal operator; `D_0=I`. Products act from right to left. Positive-stage
charts need not commute. D denotes the logical owner route, not the physical
alignment A with its payload translation; the bridge is inherited from the
pinned [cover-action note](../joint-query/evidence/QQ16-COVER-ACTION-ADDENDUM.md).

The relevant backward rows are

```
a = ell_(1,T) x1_T
C = x1_U - y1_U
V = y1_U + K_(1,U) a
Z = y1_A + P_(2,A)(B_(2,U) y1_U + ell_(2,T) y1_T).
```

Recover the entire post-F0 state in order:

```
a    = ell_(1,T) t
y1_U = V - K_(1,U) a
x1_U = C + y1_U
y1_A = Z - P_(2,A)(B_(2,U) y1_U + ell_(2,T) h)
x1_A = r; x1_T = t; y1_T = h.
```

The logger correction has no y1_A input, so there is no circular dependence.
The mixed product `P_(2,A) B_(2,U) K_(1,U) ell_(1,T)` retains this order.
No 88-coordinate F0 read or unread-minor inverse is needed for this changed map.
Apply the credited F0 inverse:

```
f   = ell_(0,T) x1_T
c   = ell_(0,A) x1_A
x_U = x1_U + K_(0,U) f
x_T = P_(0,T) c
x_A = P_(0,A)(f - B_(0,U) x_U - c)
y_U = y1_U - x1_U
y_p = x1_p + y1_p - x_p, p in A union T.
```

Substitution proves both inverse orders for F0 and for the observation map.
This is an all-finite-dimension written operator proof under the stated local
contract, distinct from executable finite verification or a formal-kernel proof.

## Sharp lower bound

A record of 200 live arrays and q retained arrays is a linear map
`W^224 -> W^(200+q)`. Recovery of every input forces this map to be injective,
even if the decoder is nonlinear. Thus `(200+q)n>=224n`, so `q>=24`.
The construction attains equality. This permits arbitrary fixed rational-linear
compression, not just selection of coordinates.

The live observation H has an explicit kernel. Choose arbitrary `r,t,h in W^8`
and set

```
x1_A=r, x1_T=t, y1_T=h
x1_U=y1_U=-K_(1,U)ell_(1,T)t
y1_A=-P_(2,A)(B_(2,U)y1_U + ell_(2,T)h).
```

These are exactly all states with C=V=Z=0, so `ker H` is isomorphic to `W^24`
and `rank H=200n`. F0 is invertible, transferring this kernel dimension to the
original inputs. No conclusion for infinite array spaces, nonlinear encodings
or a different live-read set is intended.

## Reproduction and coverage

From a full checkout, with standard-library Python:

```sh
python3.12 -I -B scripts/research_package.py --package research/qq16-l2-minimal-retention
python3 -I -B research/qq16-l2-minimal-retention/verify.py
python3 -I -B research/qq16-l2-minimal-retention/independent_check.py
```

The primary verifier consumes pinned R/K and checks selected Grams, the first
two chronological events, and both inverse orders of 224 registered owner-route
pairs, including their native translation inverse equations. This binds packet
registrations; it does not freshly derive phase geometry, reconstruct R from the
scalar prefix, execute native words, or audit their full cost/precision invoice.

Every input array is independent, and a second pass uses 224 independently
specified observation arrays. Six complete identities are checked in the rational
free-group ring on 224 chart/port symbols, allowing only adjacent inverse
cancellation. Zero formal residual specializes to zero for every invertible
choice of the maps. This stronger symbolic model applies to the pinned logical
maps, but the executable is not a proof assistant.

[RESULT.json](RESULT.json) is the complete deterministic receipt. It records
32 semantic fault residuals: 24 individual retained-coordinate omissions plus
eight driver, sign, logger, chart, missing-read or wrong-cut mutations. They are
free-operator controls; a nonzero formal residual need not survive every concrete
specialization. The chart substitution becomes invisible when every D is set to
identity. No source-specific native counterexample is claimed. Reordered terms
and equivalent rational splitting are accepted. Missing or changed receipts fail;
explicit generation (`--write-result`) refuses to overwrite an existing receipt.

The independent checker uses the same R but separately constructed noncommuting
2x2 rational maps. It covers 448 independent input coordinates and 448 independent
observation coordinates, both inverse orders and five faults. Those finite
fixtures supplement the separate written proof, not an exhaustive chart census.
Behavioral tests exercise source/receipt integrity and ineffective-control
rejection. The registered Python 3.12 replay passes all four declared commands;
REVIEW.md separately records the specialist's direct replays. Hosted CI is a
separate gate.

## Open next questions and limits

1. Can these 24 retained arrays and 200 live arrays be accessed and retired
   legally at d1? Trace post-F0/B1 endpoint frames, especially the extra Y2_U
   read, then price current-driver and future-logger reconstruction together
   with output storage and literal cleanup. Native access and restoration are
   the blockers, not information sufficiency.
2. Can the d1 record serve the full controller? Follow the next bridge and F2
   before proposing final-cut recovery. The remaining 17 events and their costs
   have not been checked here.

Concurrent work: ywz65's [12:12 UTC native L2 claim](https://github.com/CrocSwap/integer-mult-bounds/pull/2470#issuecomment-6191762591)
targets the native reconstruction of x1_U with restored sources and owned outputs.
It explicitly excludes this 24-array information minimum and full decoder.
That claim is an adjacent lead, not verified native evidence for this package.

This decoder is an information map, not a reversible implementation restoring
separate record workspace from arbitrary dirt. Physical retention, native reads,
helper cleanup, ownership, rounding, precision, tape costs, global hosting and the
complete invoice remain open. A smaller record can cost more to reconstruct.
No selected cold replay, hosted CI pass, full multiplication theorem or improved
kappa is implied.

## Provenance and credit

Base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4;
[SOURCES.json](SOURCES.json) pins inputs and historical guidance. The independent
verification card is explicitly changed from ledger reconstruction to this
retention implication; see [TASK.json](TASK.json).
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2424#discussioncomment-18948536).

Credit Sagar Thakrar/PR2470, starship-s/PR2443, ywz65/PR2456, Ali Romman/PR1969,
Gareth Davidson/PR2432, commdata2338/PR2174 and the retained QQ16/supplier lineage,
including Rohan Arun, Jeremy Kothe and DreamingOfClouds. Existing sources and
notices are unchanged. New work is Apache-2.0, prepared by Ross Richardson with
substantial OpenAI Codex assistance for derivation, implementation and writing;
a separate Codex recursive-interface specialist performed the independent proof
and matrix check. No independent human or formal-kernel review is claimed.
