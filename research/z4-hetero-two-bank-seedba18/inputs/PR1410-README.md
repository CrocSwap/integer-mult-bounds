# A persistent order-four boundary across two root echoes

**Scoped recursive-interface construction; no new `kappa`, supplier admission, or change to the selected result.** For the pinned PR #1391 child family, two identical five-child root echoes on the same source can be replaced by one ten-child dirty echo that carries its order-four phase across the midpoint. The complete word has 1,904 scalar primitives versus 2,016 for two separate calls, saving 112 primitives and 232 data reads. Its peak prefix row-L1 is 42 instead of 30, so this result does not establish a precision improvement.

## Assignment and scope

The OS assignment seed was **57**, on the recursive-interfaces track. The pinned base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Candidate tasks recorded before selection were (1) share the midpoint restoration between two identical PR #1391 root echoes, (2) extend the paired frame alphabet to order five, and (3) test a six-child extension. Seed rule `57 mod 3 = 0` selected the first. The short claim is recorded in [discussion #1163](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911847).

This is exact for the stated order-four macro alphabet and the fixed two-call same-source family. It composes the predecessor's five-child interface; it does not change the physical child supplier, address routing, precision model, selected certificate, or theorem exponent. The motivating interface card asks whether two consecutive calls can eliminate a restoration reconstructed by the next call. Here the joint word removes one separate call's copy/restoration wrapper and avoids paying two independent boundary schedules. It does not prove an improvement for heterogeneous calls or arbitrary ADD/NEG interleavings.

## Recurrence and complete cost

For phase `t` in `Z/4Z`, let `A(t)` be the cost of the three-octet workspace frame and `B(t)` the cost of the output frame. The source-pinned phase vectors are

```text
B = [(0,0), (18,2), (12,4), (18,2)]
A = 3 B
```

where each pair is `(ADD, NEG)`. The predecessor recurrence is independently re-evaluated for five and ten children:

```text
F0(t) = A(t) + B(t)
F(j+1)(s) = min_t { F(j)(t) + A(s-t-1 mod 4) + B(s-t mod 4) }
g(k) = Fk(0)
```

The five-child control has path `[0,1,2,3,0,0]`, boundary vector `(126,14)`, total 140; all `4^5 = 1,024` paths are checked. For ten children the optimum is `[0,1,2,3,0,1,2,3,0,1,0]`, with midpoint phase 1, boundary vector `(216,32)`, total 248; all `4^10 = 1,048,576` paths are checked.

The complete dirty root echo has map

```text
(D, X, W) -> (D + 2 sum_i R_i X, X, W)
```

for arbitrary input vectors `D`, `X`, and `W`. Its full invoice is

| Schedule | ADD | NEG | Primitives | Reads | Writes | Prefix row-L1 peak |
|---|---:|---:|---:|---:|---:|---:|
| Two separate five-child calls | 1,840 | 176 | 2,016 | 3,856 | 2,016 | 30 |
| Joint ten-child call | 1,720 | 184 | 1,904 | 3,624 | 1,904 | 42 |
| Eager ten-child control | 2,368 | 240 | 2,608 | — | — | — |

The joint schedule uses 120 fewer ADDs and 8 more NEGs than the two-call schedule. The total decreases by 112. Prefix row-L1 grows by 12; coefficient width, fixed-precision safety, and tape costs are outside this experiment. In particular the result is a gate-count construction, not a resource-admitted supplier or a revised recursive bound.

## Evidence and reproduction

`inputs/PR1391-CERTIFICATE.json`, `inputs/PR1391-verify.py`, and `inputs/PR1391-README.md` preserve the predecessor material from PR #1391 at head `6ce8017e4c27c8b220b6c3a27a53bb18f138212a`; hashes and Git blob IDs are checked before importing its word emitter. The inherited source pins are checked against the exact base. The new verifier independently implements the recurrence, complete vector invoice, map expectation, and full path census. The emitted predecessor circuit is reused only as the pinned child-word emitter.

Run from the repository root:

```sh
python3 -I -O -B research/z4-persistent-pair-seed57/verify.py
```

Expected output begins `PASS_Z4_PERSISTENT_PAIR` and reports `g5 140 g10 248 paths 1048576`, followed by `two_calls 2016 joint 1904 saving 112`. The same verifier also checks 56 basis columns for both separate and joint maps and rejects three controls: omitting the second call, using a wrong output phase, and failing terminal restoration. `test_package.py` repeats focused recurrence and result-receipt assertions. All arithmetic is exact integer arithmetic; the state/path search domain and stopping rule are the finite four-phase paths for exactly 5 and 10 children, exhaustively enumerated. Local replay and package-pin validation passed on CPython 3.14.7, and `make selected-record-check` passed with the exact base kappa unchanged. The registered wrapper declares Python 3.12, which is unavailable locally; that replay, hosted CI, and independent human review remain pending. Exact command receipts are in [VALIDATION.json](VALIDATION.json).

## Predecessors and attribution

This result extends the fixed order-four paired-frame construction in [PR #1391](https://github.com/CrocSwap/integer-mult-bounds/pull/1391), which in turn credits Ross Richardson's order-three cyclic-output frame in [PR #1287](https://github.com/CrocSwap/integer-mult-bounds/pull/1287) and Sagar Thakrar's paid output-sign frames in [PR #1227](https://github.com/CrocSwap/integer-mult-bounds/pull/1227). The imported emitter and predecessor certificate are byte-pinned. The ten-child recurrence, exhaustive census, composed dirty map and complete two-call comparison are new in this package.

Prepared by **Cinna Davis** with substantial **OpenAI Codex assistance** in research, algebra, code, verification and prose. No independent human review or formal proof assistant is claimed. New package material is Apache-2.0; the copied predecessor README/code/certificate retain their upstream attribution and license context.

## Open next questions

- Does a named selected supplier expose this exact paired order-four intertwiner? This is necessary before transferring the gate saving into a selected recursive profile. First step: inspect one retained supplier's actual child matrix for the paired-cycle invariant. Blocked by the absence of a precision-admitted physical supplier with this interface.
- Can the 12-unit increase in prefix row-L1 be absorbed under the selected fixed-precision profile? First step: propagate the joint word's exact prefix coefficient envelope through the named host schedule. Blocked by the missing supplier and address/tape admission.
