# Frame-incidence zero exclusion, with a P107 fixture

This package gives a **conditional structural theorem**: finite root/frame
incidence conditions `(D), (G), (W)` force `a_ik b_ik = 4`, hence exclude support
zeros, in every characteristic-zero solution of the rank-eight E-graph
conditions. The written proof uses full-frame projector sums and a complete
four-line class plus one opposite-class witness. It uses no SAT/DRUP certificate
and does not assume the unknown factor entries are nonzero.

The theorem and definitions are in [proof.md](proof.md). Condition `(D)` is eight
incidence/kernel rank identities, `(G)` is connectivity of 28 two-point
frame-intersection graphs, and `(W)` covers each pivot pair by a complete live
class with an opposite-class live witness. The checker certifies these finite
premises; the universal algebraic implication remains a written proof.

The default **P107 fixture**, outside the frame-contained deletion family, is:

```text
FRAME0 = (0, 1, 6, 11, 20, 29, 106, 119)
F      = (2, 5, 8, 9, 30, 41, 108, 117)
X      = (32, 45, 73, 78, 88)
L      = P112 minus X
```

Stable IDs come from lexicographically sorting the 120 canonical doubled roots:
56 vectors `2e_i +/- 2e_j` with `i<j`, and 64 vectors `(1,s1,...,s7)` with
`sj in {-1,1}` and an even number of minus signs. Set `G_ij=(v_i dot v_j)/4`.
`P112` excludes `FRAME0`; `G[32,73]=-1` certifies that `X` is not frame-contained.

There are 877 live frames and 12 witnessed 4+1 blocks covering all pivot pairs.
Only seven blocks are fully live; those seven alone miss three pairs, so the
weaker 4+1 condition is used. **All 14 blocks are nonempty in this default
fixture**, which supplies the separate extra premise of the proof's gauge
corollary `K=D(2G_L)D^-1`.

This does **not** establish all five-line deletions or an orbit classification.
The alternate fixture `X=(3,4,7,10,12)` passes `(D),(G),(W)` but has an empty
block; **no gauge-corollary claim is made for that alternate**. The control
`X=(3,13,14,22,23)` passes `(D),(G)` and fails `(W)` at pivot pair `(2,5)`.
That is failure of a sufficient criterion at one pivot, not an actual nongauge
P107 matrix. The actual nongauge positive controls are restricted to 12 and 13
lines; neither is a P107 matrix.
No supplier, new cost floor, recursive moment, `kappa`, or frontier change is
claimed. [TASK.json](TASK.json) records the changed masked-decoder assignment.

## Reproduce and evidence

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/frame-incidence-zero-exclusion --check-only
python3.12 -B scripts/research_package.py --package research/frame-incidence-zero-exclusion
```

The registered command uses `-I -O -B`, a 120-second bound and no external inputs
or dependencies. Direct normal/optimized reproduction:

```sh
python3.12 -I -B research/frame-incidence-zero-exclusion/verify.py
python3.12 -I -O -B research/frame-incidence-zero-exclusion/verify.py
```

[verify.py](verify.py) regenerates 120 roots and all 2,025 frames, checks eight
exact characteristic-zero rank certificates, 28 connected graphs and twelve
explicit 4+1 witnesses, then compares [certificate.json](certificate.json).
Modular nonzero minors provide rank lower bounds; verified exact integer kernel
identities provide matching upper bounds. These are exact rank certificates,
not finite-field guesses about characteristic-zero solutions.

The default run also checks 11,449 entries of an exact rational gauge example,
four rejection controls, restricted 12- and 13-line nongauge examples and four
local exceptional diagonal branches. The 13-line control checks 13 diagonal and
108 ordered orthogonal-zero equations, rank eight and 15 missing support
coordinates per factor. Its shared diagonal formula predicts `-1/2` where the
actual value is `1`, illustrating why the global `(D),(G)` hypotheses are needed.
Required guards use explicit exceptions,
including the extra nonempty-block premise for the default gauge corollary.
Alternate CLI calls check only their selected finite premises, not the default
controls or that extra corollary premise:

```sh
python3.12 -I -O -B research/frame-incidence-zero-exclusion/verify.py --deleted 3,4,7,10,12
# Expected failure: W: uncovered pivot pairs [(2, 5)]
python3.12 -I -O -B research/frame-incidence-zero-exclusion/verify.py --deleted 3,13,14,22,23
```

The initial CPython 3.12.14 replay on macOS 26.5.1 arm64 passed the default runs in
0.583 and 0.622 seconds. Eleven recorded outcomes cover both modes, the alternate
fixture, coverage failure, deleted-pivot rejection, two certificate regenerations
and a deliberately tampered incidence rank. Regenerated certificates byte-match
the supplied one; normal/optimized outputs match in each paired case. The
optimized tamper run rejects `certificate content mismatch`.
[REPLAY.json](REPLAY.json) records the commands, outcomes and original hashes.
These local receipts are distinct from the Pro research-session runtime report.

The boundary-control update adds fourteen local expected outcomes under the same
runtime: seven successes and seven intended rejections. Default normal/optimized
runs passed in 0.545 and 0.631 seconds; both regenerated certificates byte-match
the replacement. The new saved-prediction tamper is rejected. Changing the extra
line's assigned pivot from label 2 to label 5 is rejected at the shared-diagonal
guard under `-O`, including with `--write-certificate`, without changing the
certificate. The alternate fixture and earlier rejection guards retain their
reported behavior. Its receipt is appended to [REPLAY.json](REPLAY.json), keeping
the initial evidence above.

All 411 verifier lines were inspected before execution: standard library only,
no network, subprocesses, installation or predecessor imports. Default execution
writes nothing. `--write-certificate` overwrites the adjacent certificate, so
regeneration and tamper tests were performed only in separate scratch copies.
The replacement verifier and certificate are byte-identical to the supplied
GPT-6 Pro boundary update. Applying its diff to PR1560 head
`5bebfd0066b98fa2353987decc47ff259b3c816a` reproduces those bytes exactly; removing
only the new control field restores the old certificate. The original theorem
and its shared-formula clarification remain unchanged. No
proof-assistant certification or independent human mathematical review is claimed.

A separate GPT-6 Pro review found no proof-level flaw in the transcribed
theorem or gauge corollary. It checked the nonsymmetric transpose conventions,
field extension, local quadratic branches and gauge normalization. Its small
exact checker also passed locally in normal and optimized Python 3.12.14, with
identical reports. That review did not receive the package verifier or compute
the incidence-rank lower bounds and graph connectivity; those finite premises
are supplied by the package replay above. The 4+1 step depends on the shared
projector formulas obtained from `(D)` and `(G)`, not on the equations of five
lines considered in isolation.

## Provenance and credit

Prepared by **Andrey Mas** with substantial **GPT-6 Pro assistance through
ChatGPT** for mathematics and checker authorship. Codex coordinated source
access, audited execution, separately replayed the program and packaged it.

Credit **Brett Halligan / @burntout76 / Ninefold** for
[PR1212](https://github.com/CrocSwap/integer-mult-bounds/pull/1212),
**Josie Elliston** for [PR1399](https://github.com/CrocSwap/integer-mult-bounds/pull/1399),
[PR1419](https://github.com/CrocSwap/integer-mult-bounds/pull/1419) and
[PR1474](https://github.com/CrocSwap/integer-mult-bounds/pull/1474),
**@DreamingOfClouds** for the PR717 E-graph model and **@themilkman216** for the
PR968 floor lineage. Predecessor rigidity, propagation, extension and DRUP
coverage remain credited prior work.

[SOURCES.json](SOURCES.json) pins main catalogue/selected-record provenance at
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`, separately from exact pending-PR proof
pins. All four proof files were authenticated against fetched Git objects during
packaging; the three supplied source hashes matched. These informational
external pins are not validated by the generic main-provenance hook and are not
runtime inputs. No predecessor package is copied. Source authentication is not
proof review or predecessor replay.

Coordination: [claim1502](https://github.com/CrocSwap/integer-mult-bounds/discussions/1502)
and [structural I2 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18912716).
Josie Elliston's complementary
[I3/I4 pivot investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1502#discussioncomment-18913583)
is separate from this structural I2 result; its orbit coverage is not claimed here.
New work is Apache-2.0 under the repository [LICENSE](../../LICENSE).

## Open next questions

Does the explicit coverage-failure deletion `(3,13,14,22,23)` admit a different
live pivot satisfying `(D),(G),(W)`? Testing its live frames is a bounded next
step toward understanding this criterion's coverage; record the nonempty-block
premise separately. Only the displayed pivot was checked here. Even failure at
every pivot would not produce a nongauge matrix or classify all five-sets.
See the structured question in [TASK.json](TASK.json).
